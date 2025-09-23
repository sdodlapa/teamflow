"""
Webhook service for external integrations and event delivery.
Provides webhook management, OAuth2 flow, and reliable delivery with retries.
"""
import hmac
import hashlib
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlencode
import uuid

import httpx
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.webhooks import (
    WebhookEndpoint, WebhookDelivery, WebhookEvent, ExternalIntegration,
    APIRateLimit, WebhookEventType, WebhookStatus, DeliveryStatus
)
from app.schemas.webhooks import (
    WebhookEventCreate, WebhookDeliveryCreate, OAuth2TokenResponse
)

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing webhook endpoints and deliveries."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def create_webhook_endpoint(
        self,
        db: AsyncSession,
        endpoint_data: Dict[str, Any],
        organization_id: int,
        user_id: int
    ) -> WebhookEndpoint:
        """Create a new webhook endpoint."""
        
        endpoint = WebhookEndpoint(
            **endpoint_data,
            organization_id=organization_id,
            created_by=user_id
        )
        
        # Generate secret if not provided
        if not endpoint.secret:
            endpoint.secret = self._generate_webhook_secret()
        
        db.add(endpoint)
        await db.commit()
        await db.refresh(endpoint)
        
        logger.info(f"Created webhook endpoint {endpoint.id} for organization {organization_id}")
        return endpoint
    
    async def update_webhook_endpoint(
        self,
        db: AsyncSession,
        endpoint_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[WebhookEndpoint]:
        """Update an existing webhook endpoint."""
        
        query = select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id)
        result = await db.execute(query)
        endpoint = result.scalar()
        
        if not endpoint:
            return None
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(endpoint, field) and value is not None:
                setattr(endpoint, field, value)
        
        endpoint.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(endpoint)
        
        return endpoint
    
    async def delete_webhook_endpoint(
        self,
        db: AsyncSession,
        endpoint_id: int
    ) -> bool:
        """Delete a webhook endpoint."""
        
        query = select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id)
        result = await db.execute(query)
        endpoint = result.scalar()
        
        if not endpoint:
            return False
        
        await db.delete(endpoint)
        await db.commit()
        
        logger.info(f"Deleted webhook endpoint {endpoint_id}")
        return True
    
    async def get_webhook_endpoints(
        self,
        db: AsyncSession,
        organization_id: int,
        event_type: Optional[WebhookEventType] = None,
        is_active: Optional[bool] = None
    ) -> List[WebhookEndpoint]:
        """Get webhook endpoints for an organization."""
        
        query = select(WebhookEndpoint).where(
            WebhookEndpoint.organization_id == organization_id
        )
        
        if event_type:
            query = query.where(
                WebhookEndpoint.event_types.contains([event_type.value])
            )
        
        if is_active is not None:
            query = query.where(WebhookEndpoint.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_webhook_event(
        self,
        db: AsyncSession,
        event_data: WebhookEventCreate,
        organization_id: int
    ) -> WebhookEvent:
        """Create a webhook event for processing."""
        
        event = WebhookEvent(
            event_type=event_data.event_type,
            event_source=event_data.event_source,
            source_id=event_data.source_id,
            payload=event_data.payload,
            context=event_data.context,
            organization_id=organization_id,
            user_id=event_data.user_id,
            scheduled_for=event_data.scheduled_for or datetime.utcnow()
        )
        
        db.add(event)
        await db.commit()
        await db.refresh(event)
        
        # Queue for immediate processing
        asyncio.create_task(self.process_webhook_event(db, event.id))
        
        return event
    
    async def process_webhook_event(
        self,
        db: AsyncSession,
        event_id: int
    ) -> List[WebhookDelivery]:
        """Process a webhook event and create deliveries."""
        
        # Get the event
        query = select(WebhookEvent).where(WebhookEvent.id == event_id)
        result = await db.execute(query)
        event = result.scalar()
        
        if not event or event.is_processed:
            return []
        
        # Get matching webhook endpoints
        endpoints = await self.get_webhook_endpoints(
            db,
            event.organization_id,
            event.event_type,
            is_active=True
        )
        
        deliveries = []
        
        for endpoint in endpoints:
            # Check if endpoint should receive this event
            if not self._should_deliver_event(endpoint, event):
                continue
            
            # Create delivery
            delivery = await self._create_webhook_delivery(
                db, endpoint, event
            )
            
            if delivery:
                deliveries.append(delivery)
                # Schedule delivery
                asyncio.create_task(self._deliver_webhook(db, delivery.id))
        
        # Mark event as processed
        event.is_processed = True
        event.processed_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Processed webhook event {event_id}, created {len(deliveries)} deliveries")
        return deliveries
    
    async def _create_webhook_delivery(
        self,
        db: AsyncSession,
        endpoint: WebhookEndpoint,
        event: WebhookEvent
    ) -> Optional[WebhookDelivery]:
        """Create a webhook delivery record."""
        
        # Prepare payload
        payload = {
            "event_type": event.event_type,
            "event_id": str(event.uuid),
            "timestamp": event.created_at.isoformat(),
            "data": event.payload,
            "context": event.context
        }
        
        # Prepare headers
        headers = endpoint.headers.copy()
        headers.update({
            "Content-Type": "application/json",
            "X-Webhook-Event": event.event_type,
            "X-Webhook-ID": str(event.uuid),
            "X-Webhook-Timestamp": str(int(event.created_at.timestamp()))
        })
        
        # Generate signature
        signature = self._generate_webhook_signature(
            json.dumps(payload, sort_keys=True),
            endpoint.secret
        )
        headers["X-Webhook-Signature"] = signature
        
        # Add authentication headers
        if endpoint.auth_type and endpoint.auth_config:
            auth_headers = self._get_auth_headers(endpoint.auth_type, endpoint.auth_config)
            headers.update(auth_headers)
        
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_type=event.event_type,
            event_id=str(event.uuid),
            payload=payload,
            headers=headers,
            url=str(endpoint.url),
            signature=signature,
            max_attempts=endpoint.max_retries + 1,
            organization_id=event.organization_id
        )
        
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        
        return delivery
    
    async def _deliver_webhook(self, db: AsyncSession, delivery_id: int) -> bool:
        """Deliver a webhook to its endpoint."""
        
        # Get delivery
        query = select(WebhookDelivery).options(
            selectinload(WebhookDelivery.endpoint)
        ).where(WebhookDelivery.id == delivery_id)
        result = await db.execute(query)
        delivery = result.scalar()
        
        if not delivery or delivery.status == DeliveryStatus.DELIVERED:
            return False
        
        # Check rate limits
        if not await self._check_rate_limit(db, delivery.endpoint):
            # Schedule retry
            delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
            await db.commit()
            return False
        
        # Update delivery status
        delivery.status = DeliveryStatus.PENDING
        delivery.started_at = datetime.utcnow()
        
        try:
            # Make HTTP request
            start_time = datetime.utcnow()
            
            response = await self.http_client.post(
                delivery.url,
                json=delivery.payload,
                headers=delivery.headers,
                timeout=delivery.endpoint.timeout_seconds
            )
            
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update delivery with response
            delivery.response_status_code = response.status_code
            delivery.response_headers = dict(response.headers)
            delivery.response_body = response.text[:10000]  # Limit response size
            delivery.response_time_ms = response_time_ms
            delivery.completed_at = end_time
            
            # Check if successful
            if 200 <= response.status_code < 300:
                delivery.status = DeliveryStatus.DELIVERED
                
                # Update endpoint statistics
                endpoint = delivery.endpoint
                endpoint.total_deliveries += 1
                endpoint.successful_deliveries += 1
                endpoint.last_delivery_at = end_time
                endpoint.last_success_at = end_time
                
                await db.commit()
                logger.info(f"Successfully delivered webhook {delivery_id}")
                return True
            else:
                # HTTP error
                delivery.status = DeliveryStatus.FAILED
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                
        except httpx.TimeoutException:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Request timeout"
            delivery.error_code = "TIMEOUT"
            
        except httpx.RequestError as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)[:500]
            delivery.error_code = "REQUEST_ERROR"
            
        except Exception as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)[:500]
            delivery.error_code = "UNKNOWN_ERROR"
            logger.exception(f"Unexpected error delivering webhook {delivery_id}")
        
        # Update endpoint statistics for failure
        endpoint = delivery.endpoint
        endpoint.total_deliveries += 1
        endpoint.failed_deliveries += 1
        endpoint.last_delivery_at = datetime.utcnow()
        endpoint.last_failure_at = datetime.utcnow()
        
        # Schedule retry if possible
        if delivery.attempt_number < delivery.max_attempts:
            delay_seconds = endpoint.retry_delay_seconds * (2 ** (delivery.attempt_number - 1))  # Exponential backoff
            delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            delivery.status = DeliveryStatus.RETRYING
            delivery.attempt_number += 1
            
            # Schedule retry
            asyncio.create_task(
                self._schedule_retry(db, delivery_id, delay_seconds)
            )
        
        await db.commit()
        return False
    
    async def _schedule_retry(self, db: AsyncSession, delivery_id: int, delay_seconds: int):
        """Schedule a webhook delivery retry."""
        await asyncio.sleep(delay_seconds)
        await self._deliver_webhook(db, delivery_id)
    
    async def retry_failed_deliveries(self, db: AsyncSession) -> int:
        """Retry failed webhook deliveries that are ready for retry."""
        
        query = select(WebhookDelivery).where(
            and_(
                WebhookDelivery.status.in_([DeliveryStatus.FAILED, DeliveryStatus.RETRYING]),
                WebhookDelivery.attempt_number < WebhookDelivery.max_attempts,
                WebhookDelivery.next_retry_at <= datetime.utcnow()
            )
        ).limit(100)  # Process in batches
        
        result = await db.execute(query)
        deliveries = result.scalars().all()
        
        retry_tasks = []
        for delivery in deliveries:
            task = asyncio.create_task(self._deliver_webhook(db, delivery.id))
            retry_tasks.append(task)
        
        if retry_tasks:
            await asyncio.gather(*retry_tasks, return_exceptions=True)
        
        return len(deliveries)
    
    def _should_deliver_event(self, endpoint: WebhookEndpoint, event: WebhookEvent) -> bool:
        """Check if an endpoint should receive an event."""
        
        # Check if endpoint is active
        if not endpoint.is_active or endpoint.status != WebhookStatus.ACTIVE:
            return False
        
        # Check event type subscription
        if endpoint.event_types and event.event_type not in endpoint.event_types:
            return False
        
        # Apply filters
        if endpoint.filters:
            return self._apply_event_filters(endpoint.filters, event)
        
        return True
    
    def _apply_event_filters(self, filters: Dict[str, Any], event: WebhookEvent) -> bool:
        """Apply filters to determine if event should be delivered."""
        
        for filter_key, filter_value in filters.items():
            if filter_key == "source_type":
                if event.event_source != filter_value:
                    return False
            elif filter_key == "user_id":
                if event.user_id != filter_value:
                    return False
            elif filter_key in event.payload:
                if event.payload[filter_key] != filter_value:
                    return False
        
        return True
    
    async def _check_rate_limit(self, db: AsyncSession, endpoint: WebhookEndpoint) -> bool:
        """Check if webhook endpoint is within rate limits."""
        
        # Check per-minute limit
        minute_limit = await self._get_rate_limit_status(
            db, "webhook", str(endpoint.id), "minute", endpoint.rate_limit_per_minute
        )
        
        if minute_limit.is_exceeded:
            return False
        
        # Check per-hour limit
        hour_limit = await self._get_rate_limit_status(
            db, "webhook", str(endpoint.id), "hour", endpoint.rate_limit_per_hour
        )
        
        return not hour_limit.is_exceeded
    
    async def _get_rate_limit_status(
        self,
        db: AsyncSession,
        subject_type: str,
        subject_id: str,
        limit_type: str,
        max_requests: int
    ) -> APIRateLimit:
        """Get or create rate limit status."""
        
        window_sizes = {"minute": 60, "hour": 3600, "day": 86400}
        window_size = window_sizes[limit_type]
        
        # Get existing rate limit
        query = select(APIRateLimit).where(
            and_(
                APIRateLimit.subject_type == subject_type,
                APIRateLimit.subject_id == subject_id,
                APIRateLimit.limit_type == limit_type
            )
        )
        result = await db.execute(query)
        rate_limit = result.scalar()
        
        now = datetime.utcnow()
        
        if not rate_limit:
            # Create new rate limit
            rate_limit = APIRateLimit(
                subject_type=subject_type,
                subject_id=subject_id,
                limit_type=limit_type,
                max_requests=max_requests,
                window_size_seconds=window_size,
                organization_id=1  # TODO: Get from context
            )
            db.add(rate_limit)
        
        # Check if we need to reset the window
        if now >= (rate_limit.window_start + timedelta(seconds=window_size)):
            rate_limit.current_count = 0
            rate_limit.window_start = now
        
        # Increment counter
        rate_limit.current_count += 1
        rate_limit.last_request_at = now
        
        await db.commit()
        return rate_limit
    
    def _generate_webhook_secret(self) -> str:
        """Generate a webhook secret for signature verification."""
        return str(uuid.uuid4())
    
    def _generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def _get_auth_headers(self, auth_type: str, auth_config: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers for webhook delivery."""
        headers = {}
        
        if auth_type == "bearer":
            if "token" in auth_config:
                headers["Authorization"] = f"Bearer {auth_config['token']}"
        
        elif auth_type == "api_key":
            if "header_name" in auth_config and "api_key" in auth_config:
                headers[auth_config["header_name"]] = auth_config["api_key"]
        
        elif auth_type == "basic":
            if "username" in auth_config and "password" in auth_config:
                import base64
                credentials = f"{auth_config['username']}:{auth_config['password']}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        
        return headers


class OAuth2Service:
    """Service for managing OAuth2 integrations."""
    
    # OAuth2 provider configurations
    PROVIDERS = {
        "slack": {
            "auth_url": "https://slack.com/oauth/v2/authorize",
            "token_url": "https://slack.com/api/oauth.v2.access",
            "scopes": ["chat:write", "channels:read", "users:read"]
        },
        "github": {
            "auth_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "scopes": ["repo", "user", "notifications"]
        },
        "google": {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scopes": ["openid", "email", "profile"]
        }
    }
    
    def __init__(self):
        self.http_client = httpx.AsyncClient()
    
    async def get_authorization_url(
        self,
        provider: str,
        client_id: str,
        redirect_uri: str,
        scopes: List[str],
        state: Optional[str] = None
    ) -> str:
        """Generate OAuth2 authorization URL."""
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes or provider_config["scopes"]),
            "response_type": "code",
            "access_type": "offline"  # For refresh tokens
        }
        
        if state:
            params["state"] = state
        
        auth_url = provider_config["auth_url"]
        return f"{auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> OAuth2TokenResponse:
        """Exchange authorization code for access token."""
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
        response = await self.http_client.post(
            provider_config["token_url"],
            data=data,
            headers={"Accept": "application/json"}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return OAuth2TokenResponse(**token_data)
    
    async def refresh_access_token(
        self,
        provider: str,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> OAuth2TokenResponse:
        """Refresh access token using refresh token."""
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = self.PROVIDERS[provider]
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        response = await self.http_client.post(
            provider_config["token_url"],
            data=data,
            headers={"Accept": "application/json"}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return OAuth2TokenResponse(**token_data)
    
    async def update_integration_tokens(
        self,
        db: AsyncSession,
        integration_id: int,
        token_response: OAuth2TokenResponse
    ) -> ExternalIntegration:
        """Update integration with new tokens."""
        
        query = select(ExternalIntegration).where(ExternalIntegration.id == integration_id)
        result = await db.execute(query)
        integration = result.scalar()
        
        if not integration:
            raise ValueError(f"Integration not found: {integration_id}")
        
        # Update tokens (in production, these should be encrypted)
        integration.access_token = token_response.access_token
        integration.refresh_token = token_response.refresh_token
        
        # Calculate expiration
        if token_response.expires_in:
            integration.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_response.expires_in
            )
        
        integration.is_connected = True
        integration.connected_at = datetime.utcnow()
        integration.last_error = None
        
        await db.commit()
        await db.refresh(integration)
        
        return integration


# Global service instances
webhook_service = WebhookService()
oauth2_service = OAuth2Service()
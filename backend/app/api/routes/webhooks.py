"""
Webhook and integration API routes.
Provides endpoints for webhook management, OAuth2 flow, and external integrations.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.webhooks import (
    WebhookEndpoint, WebhookDelivery, WebhookEvent, ExternalIntegration,
    APIRateLimit, WebhookEventType, WebhookStatus, DeliveryStatus
)
from app.schemas.webhooks import (
    WebhookEndpointCreate, WebhookEndpointUpdate, WebhookEndpointResponse,
    WebhookDeliveryResponse, WebhookEventCreate, WebhookEventResponse,
    ExternalIntegrationCreate, ExternalIntegrationUpdate, ExternalIntegrationResponse,
    OAuth2AuthorizeRequest, OAuth2CallbackRequest, WebhookTestRequest, WebhookTestResponse,
    WebhookAnalyticsFilter, WebhookAnalyticsResponse, RateLimitStatus,
    IntegrationProviderList, IntegrationProvider
)
from app.services.webhook_service import webhook_service, oauth2_service

router = APIRouter(prefix="/webhooks", tags=["webhooks-integrations"])


# ============================================================================
# Webhook Endpoint Management
# ============================================================================

@router.post("/endpoints", response_model=WebhookEndpointResponse)
async def create_webhook_endpoint(
    webhook: WebhookEndpointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook endpoint."""
    
    # TODO: Check organization permissions
    organization_id = 1  # TODO: Get from user context
    
    endpoint = await webhook_service.create_webhook_endpoint(
        db=db,
        endpoint_data=webhook.dict(),
        organization_id=organization_id,
        user_id=current_user.id
    )
    
    return endpoint


@router.get("/endpoints", response_model=List[WebhookEndpointResponse])
async def list_webhook_endpoints(
    event_type: Optional[WebhookEventType] = Query(None, description="Filter by event type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    status: Optional[WebhookStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List webhook endpoints."""
    
    organization_id = 1  # TODO: Get from user context
    
    query = select(WebhookEndpoint).where(
        WebhookEndpoint.organization_id == organization_id
    )
    
    if event_type:
        query = query.where(WebhookEndpoint.event_types.contains([event_type.value]))
    if is_active is not None:
        query = query.where(WebhookEndpoint.is_active == is_active)
    if status:
        query = query.where(WebhookEndpoint.status == status)
    
    query = query.order_by(desc(WebhookEndpoint.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/endpoints/{endpoint_id}", response_model=WebhookEndpointResponse)
async def get_webhook_endpoint(
    endpoint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific webhook endpoint."""
    
    query = select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id)
    result = await db.execute(query)
    endpoint = result.scalar()
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    # TODO: Check access permissions
    
    return endpoint


@router.put("/endpoints/{endpoint_id}", response_model=WebhookEndpointResponse)
async def update_webhook_endpoint(
    endpoint_id: int,
    webhook_update: WebhookEndpointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a webhook endpoint."""
    
    # TODO: Check edit permissions
    
    endpoint = await webhook_service.update_webhook_endpoint(
        db=db,
        endpoint_id=endpoint_id,
        update_data=webhook_update.dict(exclude_unset=True)
    )
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    return endpoint


@router.delete("/endpoints/{endpoint_id}")
async def delete_webhook_endpoint(
    endpoint_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a webhook endpoint."""
    
    # TODO: Check delete permissions
    
    success = await webhook_service.delete_webhook_endpoint(db, endpoint_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    return {"message": "Webhook endpoint deleted successfully"}


@router.post("/endpoints/{endpoint_id}/test", response_model=WebhookTestResponse)
async def test_webhook_endpoint(
    endpoint_id: int,
    test_request: WebhookTestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test a webhook endpoint with a sample payload."""
    
    # Get endpoint
    query = select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id)
    result = await db.execute(query)
    endpoint = result.scalar()
    
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    # Create test event
    test_payload = test_request.test_payload.copy()
    test_payload.update({
        "test": True,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint_id": endpoint_id
    })
    
    event = WebhookEvent(
        event_type=test_request.event_type,
        event_source="test",
        source_id=0,
        payload=test_payload,
        context={"test": True, "user_id": current_user.id},
        organization_id=endpoint.organization_id,
        user_id=current_user.id
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Create and execute delivery
    delivery = await webhook_service._create_webhook_delivery(db, endpoint, event)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test delivery"
        )
    
    # Execute delivery in background
    background_tasks.add_task(webhook_service._deliver_webhook, db, delivery.id)
    
    return WebhookTestResponse(
        success=True,
        delivery_id=delivery.id
    )


# ============================================================================
# Webhook Deliveries
# ============================================================================

@router.get("/deliveries", response_model=List[WebhookDeliveryResponse])
async def list_webhook_deliveries(
    endpoint_id: Optional[int] = Query(None, description="Filter by endpoint"),
    event_type: Optional[WebhookEventType] = Query(None, description="Filter by event type"),
    status: Optional[DeliveryStatus] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List webhook deliveries."""
    
    organization_id = 1  # TODO: Get from user context
    
    query = select(WebhookDelivery).options(
        selectinload(WebhookDelivery.endpoint)
    ).where(WebhookDelivery.organization_id == organization_id)
    
    # Apply filters
    if endpoint_id:
        query = query.where(WebhookDelivery.endpoint_id == endpoint_id)
    if event_type:
        query = query.where(WebhookDelivery.event_type == event_type)
    if status:
        query = query.where(WebhookDelivery.status == status)
    if start_date:
        query = query.where(WebhookDelivery.scheduled_at >= start_date)
    if end_date:
        query = query.where(WebhookDelivery.scheduled_at <= end_date)
    
    query = query.order_by(desc(WebhookDelivery.scheduled_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/deliveries/{delivery_id}", response_model=WebhookDeliveryResponse)
async def get_webhook_delivery(
    delivery_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific webhook delivery."""
    
    query = select(WebhookDelivery).options(
        selectinload(WebhookDelivery.endpoint)
    ).where(WebhookDelivery.id == delivery_id)
    
    result = await db.execute(query)
    delivery = result.scalar()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery not found"
        )
    
    # TODO: Check access permissions
    
    return delivery


@router.post("/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    delivery_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually retry a failed webhook delivery."""
    
    query = select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
    result = await db.execute(query)
    delivery = result.scalar()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery not found"
        )
    
    if not delivery.can_retry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery cannot be retried"
        )
    
    # TODO: Check permissions
    
    # Reset delivery for retry
    delivery.status = DeliveryStatus.PENDING
    delivery.attempt_number += 1
    delivery.next_retry_at = None
    delivery.error_message = None
    delivery.error_code = None
    
    await db.commit()
    
    # Execute retry in background
    background_tasks.add_task(webhook_service._deliver_webhook, db, delivery_id)
    
    return {"message": "Webhook delivery retry scheduled"}


# ============================================================================
# Webhook Events
# ============================================================================

@router.post("/events", response_model=WebhookEventResponse)
async def create_webhook_event(
    event: WebhookEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a webhook event for processing."""
    
    organization_id = 1  # TODO: Get from user context
    
    webhook_event = await webhook_service.create_webhook_event(
        db=db,
        event_data=event,
        organization_id=organization_id
    )
    
    return webhook_event


@router.get("/events", response_model=List[WebhookEventResponse])
async def list_webhook_events(
    event_type: Optional[WebhookEventType] = Query(None, description="Filter by event type"),
    event_source: Optional[str] = Query(None, description="Filter by event source"),
    is_processed: Optional[bool] = Query(None, description="Filter by processed status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List webhook events."""
    
    organization_id = 1  # TODO: Get from user context
    
    query = select(WebhookEvent).where(
        WebhookEvent.organization_id == organization_id
    )
    
    if event_type:
        query = query.where(WebhookEvent.event_type == event_type)
    if event_source:
        query = query.where(WebhookEvent.event_source == event_source)
    if is_processed is not None:
        query = query.where(WebhookEvent.is_processed == is_processed)
    
    query = query.order_by(desc(WebhookEvent.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# External Integrations
# ============================================================================

@router.get("/providers", response_model=IntegrationProviderList)
async def list_integration_providers():
    """List available integration providers."""
    
    providers = []
    for provider_id, config in oauth2_service.PROVIDERS.items():
        provider = IntegrationProvider(
            id=provider_id,
            name=provider_id.title(),
            description=f"{provider_id.title()} integration",
            provider_type="oauth2",
            supported_scopes=config["scopes"],
            auth_url=config["auth_url"],
            token_url=config["token_url"]
        )
        providers.append(provider)
    
    return IntegrationProviderList(providers=providers)


@router.post("/integrations", response_model=ExternalIntegrationResponse)
async def create_external_integration(
    integration: ExternalIntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new external integration."""
    
    organization_id = 1  # TODO: Get from user context
    
    ext_integration = ExternalIntegration(
        name=integration.name,
        provider=integration.provider,
        provider_type=integration.provider_type,
        config=integration.config,
        credentials=integration.credentials,
        scopes=integration.scopes,
        client_id=integration.client_id,
        client_secret=integration.client_secret,  # TODO: Encrypt
        is_active=integration.is_active,
        sync_frequency_minutes=integration.sync_frequency_minutes,
        organization_id=organization_id,
        created_by=current_user.id
    )
    
    db.add(ext_integration)
    await db.commit()
    await db.refresh(ext_integration)
    
    return ext_integration


@router.get("/integrations", response_model=List[ExternalIntegrationResponse])
async def list_external_integrations(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_connected: Optional[bool] = Query(None, description="Filter by connection status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List external integrations."""
    
    organization_id = 1  # TODO: Get from user context
    
    query = select(ExternalIntegration).where(
        ExternalIntegration.organization_id == organization_id
    )
    
    if provider:
        query = query.where(ExternalIntegration.provider == provider)
    if is_active is not None:
        query = query.where(ExternalIntegration.is_active == is_active)
    if is_connected is not None:
        query = query.where(ExternalIntegration.is_connected == is_connected)
    
    query = query.order_by(desc(ExternalIntegration.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/integrations/{integration_id}", response_model=ExternalIntegrationResponse)
async def get_external_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific external integration."""
    
    query = select(ExternalIntegration).where(ExternalIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External integration not found"
        )
    
    # TODO: Check access permissions
    
    return integration


@router.put("/integrations/{integration_id}", response_model=ExternalIntegrationResponse)
async def update_external_integration(
    integration_id: int,
    integration_update: ExternalIntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an external integration."""
    
    query = select(ExternalIntegration).where(ExternalIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External integration not found"
        )
    
    # TODO: Check edit permissions
    
    # Update fields
    update_data = integration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(integration, field):
            setattr(integration, field, value)
    
    integration.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(integration)
    
    return integration


@router.delete("/integrations/{integration_id}")
async def delete_external_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an external integration."""
    
    query = select(ExternalIntegration).where(ExternalIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="External integration not found"
        )
    
    # TODO: Check delete permissions
    
    await db.delete(integration)
    await db.commit()
    
    return {"message": "External integration deleted successfully"}


# ============================================================================
# OAuth2 Flow
# ============================================================================

@router.post("/oauth2/authorize")
async def oauth2_authorize(
    auth_request: OAuth2AuthorizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start OAuth2 authorization flow."""
    
    # TODO: Get client credentials from integration
    client_id = "your_client_id"  # TODO: Get from integration config
    redirect_uri = "http://localhost:8000/webhooks/oauth2/callback"  # TODO: Configure
    
    auth_url = await oauth2_service.get_authorization_url(
        provider=auth_request.provider,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=auth_request.scopes,
        state=auth_request.state
    )
    
    return {"authorization_url": auth_url}


@router.get("/oauth2/callback")
async def oauth2_callback(
    code: str,
    state: Optional[str] = None,
    integration_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth2 callback."""
    
    if not integration_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration ID required"
        )
    
    # Get integration
    query = select(ExternalIntegration).where(ExternalIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    try:
        # Exchange code for token
        redirect_uri = "http://localhost:8000/webhooks/oauth2/callback"  # TODO: Configure
        
        token_response = await oauth2_service.exchange_code_for_token(
            provider=integration.provider,
            code=code,
            client_id=integration.client_id,
            client_secret=integration.client_secret,
            redirect_uri=redirect_uri
        )
        
        # Update integration with tokens
        await oauth2_service.update_integration_tokens(
            db=db,
            integration_id=integration_id,
            token_response=token_response
        )
        
        return RedirectResponse(
            url=f"/integrations/{integration_id}?connected=true",
            status_code=status.HTTP_302_FOUND
        )
        
    except Exception as e:
        # Update integration with error
        integration.last_error = str(e)
        await db.commit()
        
        return RedirectResponse(
            url=f"/integrations/{integration_id}?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


# ============================================================================
# Rate Limiting
# ============================================================================

@router.get("/rate-limits/{subject_type}/{subject_id}", response_model=RateLimitStatus)
async def get_rate_limit_status(
    subject_type: str,
    subject_id: str,
    limit_type: str = Query(..., pattern=r"^(minute|hour|day)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get rate limit status for a subject."""
    
    query = select(APIRateLimit).where(
        and_(
            APIRateLimit.subject_type == subject_type,
            APIRateLimit.subject_id == subject_id,
            APIRateLimit.limit_type == limit_type
        )
    )
    result = await db.execute(query)
    rate_limit = result.scalar()
    
    if not rate_limit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate limit not found"
        )
    
    return RateLimitStatus(
        limit_type=rate_limit.limit_type,
        max_requests=rate_limit.max_requests,
        current_count=rate_limit.current_count,
        remaining_requests=rate_limit.remaining_requests,
        window_start=rate_limit.window_start,
        window_size_seconds=rate_limit.window_size_seconds,
        is_exceeded=rate_limit.is_exceeded,
        reset_at=rate_limit.window_start + timedelta(seconds=rate_limit.window_size_seconds)
    )


# ============================================================================
# Analytics
# ============================================================================

@router.post("/analytics", response_model=WebhookAnalyticsResponse)
async def get_webhook_analytics(
    filters: WebhookAnalyticsFilter,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get webhook delivery analytics."""
    
    organization_id = 1  # TODO: Get from user context
    
    # Build base query
    query = select(WebhookDelivery).options(
        selectinload(WebhookDelivery.endpoint)
    ).where(WebhookDelivery.organization_id == organization_id)
    
    conditions = []
    
    # Apply filters
    if filters.start_date:
        conditions.append(WebhookDelivery.scheduled_at >= filters.start_date)
    if filters.end_date:
        conditions.append(WebhookDelivery.scheduled_at <= filters.end_date)
    if filters.endpoint_ids:
        conditions.append(WebhookDelivery.endpoint_id.in_(filters.endpoint_ids))
    if filters.event_types:
        conditions.append(WebhookDelivery.event_type.in_(filters.event_types))
    if filters.status_filter:
        conditions.append(WebhookDelivery.status.in_(filters.status_filter))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Execute query
    result = await db.execute(query)
    deliveries = result.scalars().all()
    
    # Calculate analytics
    total_deliveries = len(deliveries)
    successful_deliveries = len([d for d in deliveries if d.is_successful])
    failed_deliveries = total_deliveries - successful_deliveries
    success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    
    # Calculate response times
    response_times = [d.response_time_ms for d in deliveries if d.response_time_ms is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    
    # Calculate median
    sorted_times = sorted(response_times)
    median_response_time = sorted_times[len(sorted_times) // 2] if sorted_times else 0
    
    # TODO: Implement additional analytics (daily trends, event type breakdown, etc.)
    
    return WebhookAnalyticsResponse(
        overall_stats={
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "success_rate": round(success_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "median_response_time_ms": median_response_time,
            "max_response_time_ms": max_response_time
        },
        deliveries_by_day=[],  # TODO: Implement
        deliveries_by_event_type=[],  # TODO: Implement
        top_failing_endpoints=[],  # TODO: Implement
        response_time_trends=[]  # TODO: Implement
    )


# ============================================================================
# System Management
# ============================================================================

@router.post("/system/retry-failed")
async def retry_failed_webhooks(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry all failed webhook deliveries."""
    
    # TODO: Check admin permissions
    
    background_tasks.add_task(webhook_service.retry_failed_deliveries, db)
    
    return {"message": "Failed webhook retry process started"}


@router.post("/system/cleanup")
async def cleanup_old_deliveries(
    days: int = Query(30, ge=1, le=365, description="Days to keep delivery records"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up old webhook delivery records."""
    
    # TODO: Check admin permissions
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old completed deliveries
    delete_query = select(WebhookDelivery).where(
        and_(
            WebhookDelivery.completed_at < cutoff_date,
            WebhookDelivery.status.in_([DeliveryStatus.DELIVERED, DeliveryStatus.FAILED])
        )
    )
    
    result = await db.execute(delete_query)
    old_deliveries = result.scalars().all()
    
    for delivery in old_deliveries:
        await db.delete(delivery)
    
    await db.commit()
    
    return {
        "message": f"Cleaned up {len(old_deliveries)} old delivery records",
        "deleted_count": len(old_deliveries)
    }
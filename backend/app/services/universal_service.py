"""Universal service patterns for template system."""

from typing import Any, Dict, List, Optional, Type, Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.models.base import BaseModel
from app.core.template_config import DomainConfig, get_domain_config


T = TypeVar('T', bound=BaseModel)


class UniversalEntityService(Generic[T]):
    """Universal service for CRUD operations on any entity type."""
    
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def create(self, data: Dict[str, Any], domain_config: Optional[DomainConfig] = None) -> T:
        """Create a new entity with template metadata."""
        entity_data = data.copy()
        
        # Add template metadata if domain config provided
        if domain_config:
            entity_data.update({
                'is_template_generated': True,
                'template_version': domain_config.version,
                'domain_config': {
                    'domain_name': domain_config.name,
                    'domain_type': domain_config.domain_type.value,
                    'entity_type': self.model.__name__
                }
            })
        
        entity = self.model(**entity_data)
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        result = await self.db.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalar_one_or_none()
    
    async def get_by_uuid(self, entity_uuid: str) -> Optional[T]:
        """Get entity by UUID."""
        result = await self.db.execute(select(self.model).where(self.model.uuid == entity_uuid))
        return result.scalar_one_or_none()
    
    async def list_entities(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[T]:
        """List entities with pagination and filtering."""
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        else:
            query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return None
        
        for field, value in data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        
        await self.db.commit()
        await self.db.refresh(entity)
        return entity
    
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        
        await self.db.delete(entity)
        await self.db.commit()
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        query = select(func.count(self.model.id))
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, field).in_(value))
                    else:
                        query = query.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(query)
        return result.scalar()


class UniversalAnalyticsService:
    """Universal analytics service for any entity type."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_entity_analytics(
        self, 
        model: Type[BaseModel], 
        days: int = 30,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get analytics for any entity type."""
        # Base query
        query = select(model)
        
        # Add organization filter if applicable
        if organization_id and hasattr(model, 'organization_id'):
            query = query.where(model.organization_id == organization_id)
        
        # Time-based analytics
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_query = query.where(model.created_at >= cutoff_date)
        
        # Execute queries
        total_result = await self.db.execute(select(func.count(model.id)))
        total_count = total_result.scalar()
        
        recent_result = await self.db.execute(select(func.count(model.id)).where(model.created_at >= cutoff_date))
        recent_count = recent_result.scalar()
        
        # Status analytics (if status field exists)
        status_analytics = {}
        if hasattr(model, 'status'):
            status_result = await self.db.execute(
                select(model.status, func.count(model.id))
                .group_by(model.status)
            )
            status_analytics = {
                status: count for status, count in status_result.fetchall()
            }
        
        return {
            'entity_type': model.__name__,
            'total_count': total_count,
            'recent_count': recent_count,
            'days_analyzed': days,
            'growth_rate': (recent_count / max(total_count - recent_count, 1)) * 100,
            'status_breakdown': status_analytics,
            'created_per_day': recent_count / max(days, 1)
        }
    
    async def get_usage_patterns(
        self, 
        model: Type[BaseModel],
        time_range: str = "week"
    ) -> Dict[str, Any]:
        """Get usage patterns for entity type."""
        if time_range == "week":
            days = 7
        elif time_range == "month":
            days = 30
        elif time_range == "year":
            days = 365
        else:
            days = 7
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily creation patterns
        daily_result = await self.db.execute(
            select(
                func.date(model.created_at).label('date'),
                func.count(model.id).label('count')
            )
            .where(model.created_at >= cutoff_date)
            .group_by(func.date(model.created_at))
            .order_by(func.date(model.created_at))
        )
        
        daily_patterns = {
            str(date): count for date, count in daily_result.fetchall()
        }
        
        return {
            'entity_type': model.__name__,
            'time_range': time_range,
            'daily_patterns': daily_patterns,
            'peak_day': max(daily_patterns.items(), key=lambda x: x[1]) if daily_patterns else None,
            'average_per_day': sum(daily_patterns.values()) / max(len(daily_patterns), 1)
        }
    
    async def get_performance_metrics(
        self, 
        model: Type[BaseModel],
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for entity type."""
        base_query = select(model)
        
        if organization_id and hasattr(model, 'organization_id'):
            base_query = base_query.where(model.organization_id == organization_id)
        
        # Total records
        total_result = await self.db.execute(select(func.count(model.id)))
        total_count = total_result.scalar()
        
        # Recent activity (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_result = await self.db.execute(
            select(func.count(model.id)).where(model.created_at >= last_24h)
        )
        recent_activity = recent_result.scalar()
        
        # Template-generated vs manual
        template_stats = {}
        if hasattr(model, 'is_template_generated'):
            template_result = await self.db.execute(
                select(
                    model.is_template_generated,
                    func.count(model.id)
                ).group_by(model.is_template_generated)
            )
            template_stats = {
                'template_generated' if is_template else 'manual': count 
                for is_template, count in template_result.fetchall()
            }
        
        return {
            'entity_type': model.__name__,
            'total_records': total_count,
            'activity_last_24h': recent_activity,
            'template_breakdown': template_stats,
            'performance_score': min((recent_activity / max(total_count * 0.1, 1)) * 100, 100),
            'health_status': 'healthy' if recent_activity > 0 else 'inactive'
        }


class DomainService:
    """Service for managing domain-specific operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def get_entity_service(self, model: Type[T]) -> UniversalEntityService[T]:
        """Get entity service for specific model."""
        return UniversalEntityService(model, self.db)
    
    async def get_domain_analytics(self, domain_name: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a domain."""
        config = get_domain_config(domain_name)
        if not config:
            return {'error': f'Domain {domain_name} not found'}
        
        analytics_service = UniversalAnalyticsService(self.db)
        
        # This would need to be implemented based on actual models
        # For now, return placeholder structure
        return {
            'domain': domain_name,
            'entities': [],  # Would be populated with actual entity analytics
            'overview': {
                'total_records': 0,
                'active_users': 0,
                'recent_activity': 0
            }
        }
    
    async def validate_domain_data(
        self, 
        domain_name: str, 
        entity_name: str, 
        data: Dict[str, Any]
    ) -> List[str]:
        """Validate data against domain configuration."""
        config = get_domain_config(domain_name)
        if not config:
            return [f'Domain {domain_name} not found']
        
        # Find entity configuration
        entity_config = None
        for entity in config.entities:
            if entity.name.lower() == entity_name.lower():
                entity_config = entity
                break
        
        if not entity_config:
            return [f'Entity {entity_name} not found in domain {domain_name}']
        
        errors = []
        
        # Validate required fields
        for field in entity_config.fields:
            if not field.nullable and field.name not in data:
                errors.append(f'Required field {field.name} is missing')
            
            if field.name in data:
                value = data[field.name]
                
                # Type validation
                if field.type == 'string' and not isinstance(value, str):
                    errors.append(f'Field {field.name} must be a string')
                elif field.type == 'integer' and not isinstance(value, int):
                    errors.append(f'Field {field.name} must be an integer')
                
                # Length validation
                if field.max_length and isinstance(value, str) and len(value) > field.max_length:
                    errors.append(f'Field {field.name} exceeds maximum length of {field.max_length}')
                
                # Choice validation
                if field.choices and value not in field.choices:
                    errors.append(f'Field {field.name} must be one of {field.choices}')
        
        return errors
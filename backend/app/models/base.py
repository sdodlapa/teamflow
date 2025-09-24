"""Base model class with common fields and utilities for template system."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, DateTime, String, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator, JSON

from app.core.database import Base


class JSONField(TypeDecorator):
    """Universal JSON field that works with both SQLite and PostgreSQL."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())


class BaseModel(Base):
    """Enhanced base model class with template system support."""

    __abstract__ = True

    # Universal primary key and UUID
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)

    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Template system fields
    is_template_generated = Column(Boolean, default=False, nullable=False)
    template_version = Column(String(50), nullable=True)
    domain_config = Column(JSONField, nullable=True)

    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        """Convert model instance to dictionary with template support."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    def get_template_metadata(self) -> Dict[str, Any]:
        """Get template metadata for this entity."""
        return {
            'is_template_generated': self.is_template_generated,
            'template_version': self.template_version,
            'domain_config': self.domain_config,
            'entity_type': self.__class__.__name__,
            'table_name': self.__tablename__
        }

    @classmethod
    def get_universal_fields(cls) -> list:
        """Get list of universal fields common to all entities."""
        return ['id', 'uuid', 'created_at', 'updated_at', 'is_template_generated', 'template_version', 'domain_config']

    @classmethod
    def get_domain_specific_fields(cls) -> list:
        """Get list of domain-specific fields for this entity."""
        all_fields = [column.name for column in cls.__table__.columns]
        universal_fields = cls.get_universal_fields()
        return [field for field in all_fields if field not in universal_fields]

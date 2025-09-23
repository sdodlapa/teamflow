"""Import all models to ensure they are registered with SQLAlchemy."""

from app.models.base import BaseModel

# Import all model classes here as they are created
# from app.models.user import User
# from app.models.organization import Organization
# from app.models.project import Project
# from app.models.task import Task

# Make Base available for Alembic
from app.core.database import Base

__all__ = ["Base", "BaseModel"]
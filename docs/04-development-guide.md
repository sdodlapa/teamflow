# TeamFlow - Development Guide

## Quick Start

### Prerequisites
- **Python 3.11+** (recommended 3.12)
- **pip** for package management
- **Git** for version control
- **SQLite** (included with Python) or **PostgreSQL** for production

### Setup Instructions

#### 1. Clone Repository
```bash
git clone <repository-url>
cd teamflow
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Environment Variables:**
```env
# Database
DATABASE_URL=sqlite:///./teamflow.db
# or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/teamflow

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Development
DEBUG=True
ENVIRONMENT=development
```

#### 4. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Verify setup
python -c "from app.core.database import engine; print('Database connection successful')"
```

#### 5. Start Development Server
```bash
# Start FastAPI server with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 6. Verify Installation
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

## Development Workflow

### 1. Code Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core application configuration
│   │   ├── config.py           # Environment and app settings
│   │   ├── database.py         # Database connection and session
│   │   ├── dependencies.py     # FastAPI dependency injection
│   │   └── security.py         # Authentication and authorization
│   ├── models/                 # SQLAlchemy database models
│   │   ├── base.py             # Base model class
│   │   ├── user.py             # User model and enums
│   │   ├── organization.py     # Organization and membership models
│   │   ├── project.py          # Project and membership models
│   │   └── task.py             # Task, comment, and dependency models
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── user.py             # User request/response schemas
│   │   ├── organization.py     # Organization schemas
│   │   ├── project.py          # Project schemas
│   │   └── task.py             # Task schemas with advanced features
│   └── api/                    # API routes and endpoints
│       ├── __init__.py
│       └── routes/
│           ├── auth.py         # Authentication endpoints
│           ├── users.py        # User management
│           ├── organizations.py # Organization management
│           ├── projects.py     # Project management
│           └── tasks.py        # Task management (12 endpoints)
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic configuration
│   └── alembic.ini             # Alembic settings
├── tests/                      # Test suite
│   ├── integration/            # Integration tests
│   └── conftest.py             # Test configuration and fixtures
├── requirements.txt            # Python dependencies
└── .env.example                # Example environment configuration
```

### 2. Adding New Features

#### Creating a New Model
```python
# app/models/new_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign key relationship
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="new_models")
```

#### Creating Pydantic Schemas
```python
# app/schemas/new_model.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewModelBase(BaseModel):
    name: str
    description: Optional[str] = None

class NewModelCreate(NewModelBase):
    pass

class NewModelUpdate(NewModelBase):
    name: Optional[str] = None

class NewModelResponse(NewModelBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### Creating API Routes
```python
# app/api/routes/new_model.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.new_model import NewModelCreate, NewModelResponse
from app.models.user import User

router = APIRouter(prefix="/new-models", tags=["new-models"])

@router.post("/", response_model=NewModelResponse)
async def create_new_model(
    new_model: NewModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation here
    pass
```

### 3. Database Migrations

#### Creating a New Migration
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add new_model table"

# Review the generated migration file
# Edit if necessary: alembic/versions/xxxx_add_new_model_table.py

# Apply migration
alembic upgrade head
```

#### Migration Best Practices
- Always review auto-generated migrations
- Test migrations on development data
- Create backup before production migrations
- Use descriptive migration messages

### 4. Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/integration/test_tasks.py

# Run with verbose output
pytest -v

# Run specific test function
pytest tests/integration/test_tasks.py::test_create_task
```

#### Writing Tests
```python
# tests/integration/test_new_model.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_new_model(
    client: AsyncClient,
    authenticated_user_headers
):
    response = await client.post(
        "/api/v1/new-models/",
        json={"name": "Test Model", "description": "Test description"},
        headers=authenticated_user_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"
```

### 5. Code Quality

#### Formatting and Linting
```bash
# Install development tools
pip install black flake8 mypy

# Format code
black app tests

# Check linting
flake8 app tests

# Type checking
mypy app
```

#### Pre-commit Setup
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Common Development Tasks

### 1. Adding Authentication to New Endpoints
```python
from app.core.dependencies import get_current_user
from app.models.user import User

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"user_id": current_user.id}
```

### 2. Adding Organization/Project Access Control
```python
from app.core.dependencies import get_project_member

@router.get("/projects/{project_id}/protected")
async def project_protected_endpoint(
    project_id: int,
    current_user: User = Depends(get_project_member)
):
    # User is guaranteed to be a project member
    return {"project_id": project_id}
```

### 3. Database Queries with Relationships
```python
from sqlalchemy.orm import selectinload
from sqlalchemy import select

# Efficient relationship loading
async def get_task_with_relationships(db: AsyncSession, task_id: int):
    query = select(Task).options(
        selectinload(Task.assignee),
        selectinload(Task.project),
        selectinload(Task.comments),
        selectinload(Task.dependencies)
    ).where(Task.id == task_id)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()
```

### 4. Error Handling
```python
from fastapi import HTTPException, status

# Standard error responses
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )

# Custom error with details
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={
        "message": "Invalid task status transition",
        "current_status": task.status,
        "attempted_status": new_status
    }
)
```

---

## Production Considerations

### 1. Environment Variables
```env
# Production settings
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@localhost/teamflow_prod
SECRET_KEY=very-secure-production-key
```

### 2. Database Connection Pooling
```python
# app/core/database.py - Production settings
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)
```

### 3. Security Headers
```python
# app/main.py - Security middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### 4. Logging Configuration
```python
# app/core/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database exists
ls teamflow.db  # For SQLite

# Reset database
rm teamflow.db
alembic upgrade head
```

#### 2. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 3. Test Failures
```bash
# Run single test with detailed output
pytest tests/integration/test_auth.py::test_login -v -s

# Check test database
rm test_teamflow.db  # Clean test database
```

#### 4. Migration Issues
```bash
# Check migration history
alembic history

# Reset to specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current
```

---

## Performance Tips

### 1. Database Optimization
- Use `selectinload()` for relationship loading
- Add database indexes for frequently queried fields
- Use pagination for large result sets
- Consider connection pooling for production

### 2. API Performance
- Use async/await consistently
- Implement response caching for static data
- Use background tasks for heavy operations
- Monitor query performance with logging

### 3. Development Efficiency
- Use auto-reload for development server
- Set up IDE with Python type checking
- Use database GUI tools for inspection
- Implement comprehensive logging

This development guide provides everything needed to effectively work with the TeamFlow codebase, from initial setup through advanced development patterns and production considerations.
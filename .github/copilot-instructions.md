# TeamFlow AI Coding Instructions

## Project Overview
TeamFlow is an enterprise task management platform with a **FastAPI backend** (production-ready) and **React frontend** (in development). The system uses a multi-tenant architecture with comprehensive authentication, authorization, and audit logging.

## Architecture & Key Patterns

### Backend Structure (FastAPI + SQLAlchemy)
- **Entry Point**: `backend/app/main.py` - Contains app factory pattern with middleware configuration
- **API Organization**: `backend/app/api/__init__.py` - All routes imported and prefixed (e.g., `/api/v1/auth`, `/api/v1/tasks`)
- **Models**: `backend/app/models/` - SQLAlchemy models inherit from `BaseModel` in `base.py` (provides UUID, timestamps)
- **Multi-tenant**: All core entities (`Organization` → `Project` → `Task`) follow hierarchical ownership model
- **Security**: JWT auth with role-based access (`user`, `admin`) + organization/project membership roles

### Database Patterns
- **Base Model**: All models extend `BaseModel` with UUID primary keys and automatic timestamps
- **Async SQLAlchemy**: Uses `AsyncSession` throughout with `create_async_engine`
- **Migrations**: Alembic in `backend/alembic/` - use `make db-revision` for new migrations
- **Test Isolation**: In-memory SQLite for tests with automatic table creation/teardown per test

### Authentication Flow
```python
# JWT tokens: 15-min access + 7-day refresh
# Headers: "Authorization: Bearer <access_token>"
# Protected routes use: depends(get_current_user)
```

## Development Workflows

### Backend Development
```bash
cd backend
make dev                    # Start FastAPI with auto-reload
make test                   # Run full test suite (64 tests)
make test-fast              # Skip slow tests
make format                 # Black + isort formatting
make lint                   # Flake8 + mypy checking
make db-revision            # Create new migration
```

### Testing Patterns
- **Fixtures**: `backend/tests/conftest.py` provides `db_session`, `client`, `test_user`, `auth_headers`
- **Test Structure**: Mark tests with `@pytest.mark.{unit|integration|api|auth}`
- **Database Tests**: Use `db_session` fixture for isolated test database
- **API Tests**: Use `authenticated_client` fixture for protected endpoints

### Frontend Development (React + TypeScript)
```bash
cd frontend
npm run dev                 # Vite dev server on :3000
npm run test               # Jest unit tests
npm run lint               # ESLint + TypeScript checking
```

## Critical Conventions

### API Response Patterns
- **Success**: Return Pydantic schemas directly (auto-serialized to JSON)
- **Errors**: Use `HTTPException(status_code=404, detail="User not found")`
- **Pagination**: Default 20 items, max 100, use `skip` and `limit` parameters
- **Validation**: Pydantic schemas in `backend/app/schemas/` for request/response validation

### Database Conventions
- **UUID Primary Keys**: All entities use `UUID(as_uuid=True)` from `BaseModel`
- **Relationships**: Use `relationship()` with proper `back_populates`
- **Soft Deletes**: Use `is_active` boolean flag rather than hard deletes
- **Audit Trail**: Automatic `created_at`/`updated_at` from `BaseModel`

### Security Implementation
- **Password Hashing**: Always use `get_password_hash()` and `verify_password()`
- **Route Protection**: Apply `depends(get_current_user)` to protected endpoints
- **Multi-tenant Security**: Check organization/project membership in route handlers
- **Role Hierarchy**: `admin` > `user`, plus org-specific roles (`owner`, `admin`, `member`)

### File Organization
- **Services**: Business logic in `backend/app/services/` (e.g., `analytics.py`, `workflow_engine.py`)
- **Middleware**: Custom middleware in `backend/app/middleware/` (performance, security)
- **Shared Types**: Common TypeScript types in `shared/` directory
- **Configuration**: Environment-based config in `backend/app/core/config.py`

## Integration Points

### Database Connection
```python
# Async database sessions
from app.core.database import get_db
# Use: db: AsyncSession = Depends(get_db)
```

### Authentication Integration
```python
# Current user dependency
from app.core.security import get_current_user
# Use: current_user: User = Depends(get_current_user)
```

### Docker Development
```bash
docker-compose up -d        # Full stack: backend, frontend, postgres, redis
# Services: postgres:5432, redis:6379, backend:8000, frontend:3000
```

## Performance & Monitoring
- **Caching**: Redis integration configured but not yet implemented
- **Performance Monitoring**: `performance_service.py` provides metrics collection
- **Database Optimization**: Connection pooling configured in `config.py`
- **File Management**: Upload handling in `app/services/file_management.py`

## Key Files to Reference
- **Backend API Router**: `backend/app/api/__init__.py` - See all available endpoints
- **Database Models**: `backend/app/models/` - Understand data relationships
- **Test Examples**: `backend/tests/conftest.py` - Testing patterns and fixtures
- **Configuration**: `backend/app/core/config.py` - Environment settings and feature flags
- **Main App**: `backend/app/main.py` - Application setup and middleware configuration
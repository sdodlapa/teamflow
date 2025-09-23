# 🚀 TeamFlow Platform Quick Reference

## Platform Overview
**TeamFlow** is a complete enterprise task management platform with FastAPI backend and React TypeScript frontend.

## Quick Start Commands

### Development Environment
```bash
# Start full development stack
docker-compose up -d

# Backend development
cd backend
make dev          # Start FastAPI with auto-reload
make test         # Run all tests
make format       # Format code with Black + isort
make lint         # Run linting and type checking

# Frontend development  
cd frontend
npm run dev       # Start Vite dev server
npm run test      # Run Jest tests
npm run lint      # Run ESLint + TypeScript
```

### API Endpoints Quick Reference

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - User logout

#### Organizations
- `GET /api/v1/organizations` - List user organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations/{id}` - Get organization details
- `POST /api/v1/organizations/{id}/members` - Add organization member

#### Projects
- `GET /api/v1/projects` - List user projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project

#### Tasks
- `GET /api/v1/tasks` - List tasks with filtering
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `POST /api/v1/tasks/{id}/comments` - Add task comment

#### Files
- `POST /api/v1/files/upload` - Upload file
- `GET /api/v1/files/{id}` - Download file
- `GET /api/v1/files/{id}/thumbnail` - Get file thumbnail

#### Admin Dashboard
- `GET /api/v1/admin/dashboard` - Admin dashboard data
- `GET /api/v1/admin/analytics/overview` - Analytics overview
- `GET /api/v1/admin/system/health` - System health check

#### Webhooks
- `GET /api/v1/webhooks` - List webhooks
- `POST /api/v1/webhooks` - Create webhook
- `POST /api/v1/webhooks/{id}/test` - Test webhook

#### Configuration
- `GET /api/v1/config/system` - System configuration
- `PUT /api/v1/config/performance` - Update performance settings
- `GET /api/v1/config/feature-flags` - Feature flags

## Database Schema Quick Reference

### Core Tables
```sql
users (id, email, username, password_hash, is_active, created_at)
organizations (id, name, description, owner_id, created_at)
projects (id, name, description, organization_id, created_at)
tasks (id, title, description, project_id, assignee_id, status, priority, due_date)
```

### Advanced Tables
```sql
task_comments (id, task_id, user_id, content, created_at)
task_dependencies (id, task_id, depends_on_task_id)
time_logs (id, task_id, user_id, hours, description, date)
files (id, filename, content_type, file_path, uploader_id)
webhooks (id, organization_id, url, events, is_active)
audit_logs (id, user_id, action, resource_type, resource_id, details)
```

## Environment Variables

### Backend Configuration
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/teamflow

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Storage
UPLOAD_DIRECTORY=./uploads
MAX_FILE_SIZE=104857600  # 100MB

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend Configuration
```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL
VITE_WS_URL=ws://localhost:8000
```

## Testing Quick Reference

### Backend Tests
```bash
# Run all tests
make test

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only  
pytest -m api          # API tests only
pytest -m auth         # Authentication tests only

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## Performance Tips

### Database Optimization
- Use database indexes on frequently queried columns
- Enable connection pooling (configured in `config.py`)
- Use async queries for better concurrency
- Monitor slow queries with performance logging

### Caching Strategy
- Redis caching enabled for frequently accessed data
- Cache TTL configured per data type
- Automatic cache invalidation on data updates
- Fallback to in-memory cache if Redis unavailable

### API Performance
- Response compression enabled for large payloads
- Pagination on list endpoints (default 20, max 100)
- Field selection to reduce response size
- Rate limiting to prevent abuse

## Security Configuration

### Authentication
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- Password hashing with bcrypt
- Role-based access control (RBAC)

### Data Protection
- Request validation with Pydantic
- SQL injection prevention with SQLAlchemy
- XSS protection with content type validation
- CORS configuration for cross-origin requests

### Audit & Compliance
- Comprehensive audit logging
- GDPR compliance with data export/deletion
- User activity tracking
- Security event monitoring

## Deployment Quick Reference

### Docker Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Database migration
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python -c "
from app.core.database import get_db
from app.services.user_service import create_admin_user
import asyncio
asyncio.run(create_admin_user())
"
```

### Health Checks
- `/api/v1/health` - Basic health check
- `/api/v1/admin/system/health` - Detailed system health
- Database connection monitoring
- Redis connection monitoring
- File storage availability

## Monitoring & Debugging

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Error tracking with stack traces
- Performance metrics logging

### Metrics
- Response time monitoring
- Database query performance
- Cache hit ratios
- User activity metrics

### Debugging
- FastAPI automatic API documentation at `/docs`
- SQLAlchemy query logging in development
- WebSocket connection monitoring
- File upload progress tracking

## Common Issues & Solutions

### Database Connection Issues
```bash
# Check database connection
docker-compose exec backend python -c "
from app.core.database import test_connection
import asyncio
asyncio.run(test_connection())
"
```

### File Upload Issues
- Check upload directory permissions
- Verify `MAX_FILE_SIZE` configuration
- Ensure sufficient disk space
- Check file type restrictions

### WebSocket Issues
- Verify WebSocket URL configuration
- Check CORS settings for WebSocket
- Monitor connection stability
- Validate authentication for WebSocket

### Performance Issues
- Check database query performance
- Monitor cache hit ratios
- Verify compression settings
- Check concurrent connection limits

---

## 📞 Support & Documentation

### Full Documentation
- **API Documentation**: Available at `/docs` when running backend
- **Development Guide**: `docs/04-development-guide.md`
- **Deployment Guide**: `docs/06-deployment-guide.md`
- **Architecture Guide**: `docs/02-technical-architecture.md`

### Key Configuration Files
- **Backend Config**: `backend/app/core/config.py`
- **Database Models**: `backend/app/models/`
- **API Routes**: `backend/app/api/`
- **Frontend Config**: `frontend/vite.config.ts`

### Quick Help
```bash
# Backend help
cd backend && make help

# View all available make commands
make

# Check system status
make health-check
```

---

**TeamFlow** - Complete Enterprise Task Management Platform  
**Version**: 1.0.0 - Production Ready  
**Last Updated**: Phase 3 Day 7 Complete
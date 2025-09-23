# TeamFlow - Technical Architecture

## System Architecture Overview

### Current Implementation Status
✅ **Backend**: Production-ready FastAPI with comprehensive features  
🔄 **Frontend**: Planned for Phase 3 (React + TypeScript)  
📅 **Infrastructure**: Planned for Phase 5 (Docker + CI/CD)

### High-Level Architecture (Implemented)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │  FastAPI Backend │    │   SQLite/       │
│  (PLANNED)      │◄──►│   ✅ COMPLETE    │◄──►│   PostgreSQL    │
│                 │    │                 │    │  ✅ IMPLEMENTED │
│  • Modern UI    │    │  • 30+ REST APIs│    │                 │
│  • Real-time    │    │  • JWT Auth     │    │  • Users        │
│  • Responsive   │    │  • Multi-tenant │    │  • Organizations│
└─────────────────┘    │  • Validation   │    │  • Projects     │
                       └─────────────────┘    │  • Tasks        │
                                │             │  • Comments     │
                       ┌─────────────────┐    │  • Dependencies │
                       │     Redis       │    └─────────────────┘
                       │   (PLANNED)     │
                       │                 │
                       │  • Caching      │
                       │  • Sessions     │
                       │  • Real-time    │
                       └─────────────────┘
```

### Current Implementation Details

#### ✅ Backend (FastAPI + Python) - **PRODUCTION-READY**
- **Framework**: FastAPI with async/await support
- **ORM**: SQLAlchemy 2.0 with async patterns
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Comprehensive Pydantic schemas
- **Database**: SQLite for development, PostgreSQL-ready
- **Testing**: 64 comprehensive tests with 100% pass rate
- **Migration**: Alembic for database schema versioning
- **Documentation**: Auto-generated OpenAPI docs

#### 🔄 Frontend (React + TypeScript) - **PLANNED PHASE 3**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development
- **Styling**: Tailwind CSS utility-first approach
- **State Management**: Zustand + React Query
- **Testing**: Jest + React Testing Library + Playwright

#### ✅ Database Design - **IMPLEMENTED**
- **Primary Database**: SQLite (development) → PostgreSQL (production)
- **Schema**: Multi-tenant with proper relationships
- **Performance**: Optimized queries with proper indexing
- **Migration**: Alembic-based versioning system

#### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for development
- **CI/CD**: GitHub Actions
- **Production**: AWS (ECS/EKS, RDS, ElastiCache)

## Database Schema

### Core Entities

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Organizations Table
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    priority VARCHAR(20) DEFAULT 'medium',
    start_date DATE,
    end_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',
    priority VARCHAR(20) DEFAULT 'medium',
    assignee_id UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    due_date TIMESTAMP,
    estimated_hours INTEGER,
    actual_hours INTEGER,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationship Tables

#### Organization Members
```sql
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
);
```

#### Project Members
```sql
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);
```

#### Task Comments
```sql
CREATE TABLE task_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Audit Log
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Design

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Reset password with token

### User Management
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `POST /users/me/change-password` - Change password
- `GET /users/{user_id}` - Get user by ID (if permitted)

### Organizations
- `GET /organizations` - List user's organizations
- `POST /organizations` - Create new organization
- `GET /organizations/{org_id}` - Get organization details
- `PUT /organizations/{org_id}` - Update organization
- `DELETE /organizations/{org_id}` - Delete organization
- `GET /organizations/{org_id}/members` - List organization members
- `POST /organizations/{org_id}/members` - Add member to organization
- `PUT /organizations/{org_id}/members/{user_id}` - Update member role
- `DELETE /organizations/{org_id}/members/{user_id}` - Remove member

### Projects
- `GET /organizations/{org_id}/projects` - List organization projects
- `POST /organizations/{org_id}/projects` - Create new project
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project
- `GET /projects/{project_id}/members` - List project members
- `POST /projects/{project_id}/members` - Add member to project

### Tasks
- `GET /projects/{project_id}/tasks` - List project tasks
- `POST /projects/{project_id}/tasks` - Create new task
- `GET /tasks/{task_id}` - Get task details
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `GET /tasks/{task_id}/comments` - List task comments
- `POST /tasks/{task_id}/comments` - Add comment to task

### Search & Filtering
- `GET /search/tasks` - Search tasks across projects
- `GET /search/projects` - Search projects
- `GET /search/users` - Search users (within organization)

## Security Architecture

### Authentication Flow
1. User registers/logs in with email/password
2. Server validates credentials and returns JWT access token (15 min) + refresh token (7 days)
3. Client stores tokens securely (httpOnly cookies for refresh, memory for access)
4. Access token included in Authorization header for API requests
5. Refresh token used to get new access token when expired

### Authorization Levels
- **System Admin**: Full system access
- **Organization Owner**: Full access to organization and all projects
- **Organization Admin**: Manage organization, create projects, manage members
- **Organization Member**: Access assigned projects
- **Project Admin**: Manage specific project and its tasks
- **Project Member**: View project, manage assigned tasks

### Security Measures
- Password hashing with bcrypt (cost factor 12)
- JWT tokens with short expiration
- Rate limiting on authentication endpoints
- Input validation and sanitization
- SQL injection prevention via parameterized queries
- XSS prevention via content security policy
- CORS configuration for production
- Audit logging for sensitive operations

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns (user_id, project_id, created_at)
- Pagination for large datasets
- Database connection pooling
- Query optimization and monitoring

### Caching Strategy
- Redis for session storage
- Cache frequently accessed data (user permissions, project metadata)
- Cache invalidation on data updates

### Real-time Features
- WebSocket connections for live updates
- Redis pub/sub for message broadcasting
- Optimistic UI updates

---
**Next Document**: [03-implementation-roadmap.md](./03-implementation-roadmap.md)
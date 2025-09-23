# TeamFlow - Development Setup Guide

## Prerequisites

### Required Software
- **Node.js**: Version 18+ (LTS recommended)
- **Python**: Version 3.11+ 
- **Docker**: Latest stable version
- **Docker Compose**: Version 2.0+
- **Git**: Latest version
- **Code Editor**: VS Code recommended with extensions

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode-remote.remote-containers",
    "ms-vscode.docker",
    "ms-vscode.thunder-client"
  ]
}
```

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for development
- **OS**: macOS, Linux, or Windows with WSL2

---

## Initial Setup

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/yourusername/teamflow.git
cd teamflow

# Create environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Environment Configuration

#### Backend Environment (backend/.env)
```bash
# Database
DATABASE_URL=postgresql://teamflow:teamflow_dev@localhost:5432/teamflow_dev
TEST_DATABASE_URL=postgresql://teamflow:teamflow_test@localhost:5432/teamflow_test

# Redis
REDIS_URL=redis://localhost:6379

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration (for development)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@teamflow.dev

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Frontend Environment (frontend/.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_SENTRY=false

# Development
VITE_ENVIRONMENT=development
```

#### Root Environment (.env)
```bash
# Docker Compose Configuration
POSTGRES_DB=teamflow_dev
POSTGRES_USER=teamflow
POSTGRES_PASSWORD=teamflow_dev
POSTGRES_TEST_DB=teamflow_test

REDIS_PASSWORD=redis_dev_password

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379
MAILHOG_PORT=8025
```

---

## Development Environment Setup

### Option 1: Docker Development (Recommended)

#### Start All Services
```bash
# Start all services in development mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Individual Service Management
```bash
# Start only database and Redis
docker-compose up -d postgres redis

# Start backend only
docker-compose up backend

# Start frontend only
docker-compose up frontend

# Rebuild services after code changes
docker-compose up --build
```

#### Database Management
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new table"

# Seed database with sample data
docker-compose exec backend python scripts/seed_data.py

# Reset database (DANGER: Deletes all data)
docker-compose exec backend python scripts/reset_db.py
```

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run database migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Alternative: Start with custom port
npm run dev -- --port 3001
```

#### Database Setup (Local PostgreSQL)
```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create development database
createdb teamflow_dev
createdb teamflow_test

# Create user
psql -c "CREATE USER teamflow WITH PASSWORD 'teamflow_dev';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE teamflow_dev TO teamflow;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE teamflow_test TO teamflow;"
```

---

## Development Workflow

### Daily Development Process

#### 1. Start Development Environment
```bash
# Option A: Docker (Recommended)
docker-compose up -d

# Option B: Local services
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Database (if running locally)
brew services start postgresql redis
```

#### 2. Verify Services
```bash
# Check all services are running
curl http://localhost:8000/health
curl http://localhost:3000

# Check database connection
docker-compose exec backend python -c "from app.core.database import engine; print('DB Connected:', engine.connect())"
```

#### 3. Code Quality Checks
```bash
# Backend code quality
cd backend
black .                    # Format code
isort .                    # Sort imports
flake8                     # Lint code
mypy app                   # Type checking
pytest                     # Run tests

# Frontend code quality
cd frontend
npm run lint               # ESLint
npm run format             # Prettier
npm run type-check         # TypeScript check
npm run test               # Jest tests
```

### Git Workflow

#### Branch Naming Convention
```bash
# Feature branches
feature/user-authentication
feature/task-management
feature/real-time-updates

# Bug fixes
bugfix/login-validation
bugfix/task-deletion

# Hotfixes
hotfix/security-patch
hotfix/critical-bug
```

#### Commit Process
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test
# ... development work ...

# 3. Run pre-commit checks
pre-commit run --all-files

# 4. Commit with conventional format
git add .
git commit -m "feat: add user authentication system

- Implement JWT token generation
- Add login/logout endpoints
- Create user registration flow
- Add password reset functionality

Closes #123"

# 5. Push and create PR
git push origin feature/new-feature
```

#### Commit Message Format
```
<type>(<scope>): <description>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore
**Scopes**: auth, tasks, projects, ui, api, db

---

## Testing

### Backend Testing

#### Run Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_user_login

# Run tests in watch mode
pytest-watch
```

#### Test Structure
```
backend/tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py             # Authentication tests
├── test_users.py            # User management tests
├── test_projects.py         # Project tests
├── test_tasks.py            # Task tests
├── integration/             # Integration tests
│   ├── test_api_auth.py
│   └── test_api_tasks.py
└── factories/               # Test data factories
    ├── user_factory.py
    └── project_factory.py
```

#### Writing Tests
```python
# Example test file: tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.factories.user_factory import UserFactory

client = TestClient(app)

def test_user_registration():
    user_data = {
        "email": "test@example.com",
        "password": "securepassword",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]

def test_user_login():
    # Create user using factory
    user = UserFactory()
    
    login_data = {
        "email": user.email,
        "password": "password"  # Default factory password
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Frontend Testing

#### Run Tests
```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run specific test file
npm test -- UserAuth.test.tsx
```

#### Test Structure
```
frontend/src/__tests__/
├── components/              # Component tests
│   ├── UserAuth.test.tsx
│   ├── TaskList.test.tsx
│   └── ProjectDashboard.test.tsx
├── hooks/                   # Custom hook tests
│   ├── useAuth.test.ts
│   └── useTasks.test.ts
├── utils/                   # Utility function tests
│   ├── dateUtils.test.ts
│   └── validation.test.ts
├── pages/                   # Page component tests
│   ├── LoginPage.test.tsx
│   └── Dashboard.test.tsx
└── e2e/                     # End-to-end tests
    ├── auth.spec.ts
    ├── tasks.spec.ts
    └── projects.spec.ts
```

#### Writing Tests
```typescript
// Example: components/UserAuth.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from '../components/LoginForm';
import { AuthProvider } from '../contexts/AuthContext';

const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

describe('LoginForm', () => {
  test('should submit valid login credentials', async () => {
    const user = userEvent.setup();
    renderWithAuth(<LoginForm />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
    });
  });

  test('should show validation errors for invalid input', async () => {
    const user = userEvent.setup();
    renderWithAuth(<LoginForm />);

    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
});
```

---

## Debugging

### Backend Debugging

#### VS Code Debug Configuration (.vscode/launch.json)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      },
      "args": ["--reload"]
    },
    {
      "name": "Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${workspaceFolder}/backend/tests"],
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

#### Logging Configuration
```python
# app/core/logging.py
import logging
import sys
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

# Usage in code
import logging
logger = logging.getLogger(__name__)

def some_function():
    logger.info("Processing started")
    try:
        # ... code ...
        logger.debug("Debug information")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
```

### Frontend Debugging

#### Browser DevTools Setup
```typescript
// utils/debug.ts
export const debugMode = import.meta.env.VITE_ENVIRONMENT === 'development';

export const debugLog = (message: string, data?: any) => {
  if (debugMode) {
    console.log(`[DEBUG] ${message}`, data);
  }
};

// React DevTools integration
if (debugMode && typeof window !== 'undefined') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || {};
}
```

#### Error Boundary
```typescript
// components/ErrorBoundary.tsx
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error reporting service in production
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          {import.meta.env.VITE_ENVIRONMENT === 'development' && (
            <details>
              <summary>Error details</summary>
              <pre>{this.state.error?.stack}</pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## Common Issues and Solutions

### Database Issues

#### Connection Problems
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Connect to database directly
docker-compose exec postgres psql -U teamflow -d teamflow_dev

# Reset database completely
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

#### Migration Issues
```bash
# Check migration status
docker-compose exec backend alembic current

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Downgrade migration
docker-compose exec backend alembic downgrade -1

# Reset migrations (DANGER)
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Frontend Issues

#### Port Conflicts
```bash
# Check what's using port 3000
lsof -ti:3000

# Kill process using port
kill -9 $(lsof -ti:3000)

# Start frontend on different port
npm run dev -- --port 3001
```

#### Node Modules Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Docker Issues

#### Container Won't Start
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs service-name

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### Disk Space Issues
```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove all containers and images
docker-compose down --rmi all -v
```

---

## Performance Optimization

### Development Performance

#### Backend Optimization
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

# Enable query logging in development
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

#### Frontend Optimization
```typescript
// Lazy loading components
const TaskList = lazy(() => import('./components/TaskList'));
const ProjectDashboard = lazy(() => import('./components/ProjectDashboard'));

// Use React.memo for expensive components
export const TaskItem = React.memo(({ task }: { task: Task }) => {
  return <div>{task.title}</div>;
});

// Optimize re-renders with useCallback
const handleTaskUpdate = useCallback((taskId: string, updates: Partial<Task>) => {
  updateTask(taskId, updates);
}, [updateTask]);
```

### Database Performance
```sql
-- Add indexes for common queries
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- Compound indexes for complex queries
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_assignee_status ON tasks(assignee_id, status);
```

---

## Security Considerations

### Development Security

#### Environment Variables
```bash
# Never commit .env files
echo ".env" >> .gitignore
echo "backend/.env" >> .gitignore
echo "frontend/.env" >> .gitignore

# Use different secrets for each environment
# Generate secure secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### API Security
```python
# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    pass

# Input validation
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()
```

#### Frontend Security
```typescript
// Sanitize user input
import DOMPurify from 'dompurify';

const SafeHTML = ({ html }: { html: string }) => {
  const sanitizedHTML = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />;
};

// Secure token storage
const tokenStorage = {
  getToken: () => localStorage.getItem('access_token'),
  setToken: (token: string) => localStorage.setItem('access_token', token),
  removeToken: () => localStorage.removeItem('access_token'),
  isTokenExpired: (token: string) => {
    try {
      const { exp } = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= exp * 1000;
    } catch {
      return true;
    }
  }
};
```

---
**Next Document**: [05-testing-strategy.md](./05-testing-strategy.md)
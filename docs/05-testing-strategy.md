# TeamFlow - Testing Strategy

## Testing Philosophy

TeamFlow follows a comprehensive testing strategy that ensures code quality, reliability, and maintainability. Our testing approach is built on the testing pyramid principle with extensive automation at every level.

### Testing Pyramid
```
                     /\
                    /  \
                   / E2E \    (5-10%)
                  /______\
                 /        \
                / Integration \ (20-30%)
               /_____________\
              /               \
             /      Unit       \ (60-70%)
            /_________________\
```

### Testing Principles
1. **Fast Feedback**: Unit tests run in milliseconds, integration tests in seconds
2. **Test-Driven Development**: Write tests before implementation when possible
3. **Behavior-Driven**: Focus on testing behavior, not implementation details
4. **Maintainable**: Tests should be easy to read, write, and maintain
5. **Isolated**: Each test should be independent and deterministic
6. **Comprehensive**: Cover happy paths, edge cases, and error scenarios

---

## Unit Testing

### Backend Unit Testing (Python/FastAPI)

#### Test Structure and Organization
```
backend/tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Pure unit tests
│   ├── test_models.py       # Model validation and methods
│   ├── test_schemas.py      # Pydantic schema validation
│   ├── test_utils.py        # Utility functions
│   ├── test_auth.py         # Authentication logic
│   └── test_business_logic.py
├── factories/               # Test data factories
│   ├── __init__.py
│   ├── user_factory.py
│   ├── project_factory.py
│   └── task_factory.py
└── fixtures/                # Test fixtures and data
    ├── sample_data.json
    └── test_files/
```

#### Test Configuration (conftest.py)
```python
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client, user_factory):
    """Provide authentication headers for authenticated requests."""
    user = user_factory()
    login_data = {"email": user.email, "password": "password"}
    response = client.post("/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### Test Factories (factories/user_factory.py)
```python
import factory
from faker import Faker
from app.models.user import User
from app.core.security import get_password_hash

fake = Faker()

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: fake.uuid4())
    email = factory.LazyFunction(lambda: fake.unique.email())
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    password_hash = factory.LazyFunction(lambda: get_password_hash("password"))
    is_active = True
    is_verified = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create to use the test database session."""
        session = cls._meta.sqlalchemy_session
        obj = model_class(*args, **kwargs)
        session.add(obj)
        session.commit()
        return obj
```

#### Model Testing Example
```python
# tests/unit/test_models.py
import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.task import Task
from tests.factories.user_factory import UserFactory
from tests.factories.task_factory import TaskFactory

class TestUserModel:
    def test_user_creation(self, db_session):
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True

    def test_user_email_uniqueness(self, db_session):
        user1 = UserFactory(email="test@example.com")
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            user2 = UserFactory(email="test@example.com")

    def test_user_password_validation(self):
        user = User(email="test@example.com", password_hash="short")
        with pytest.raises(ValueError, match="Password too short"):
            user.validate_password_strength()

class TestTaskModel:
    def test_task_creation(self, db_session):
        user = UserFactory()
        task = TaskFactory(created_by=user, assignee=user)
        
        assert task.title is not None
        assert task.status == "todo"
        assert task.created_by == user
        assert task.assignee == user

    def test_task_due_date_validation(self):
        past_date = datetime.utcnow() - timedelta(days=1)
        task = Task(title="Test Task", due_date=past_date)
        
        with pytest.raises(ValueError, match="Due date cannot be in the past"):
            task.validate_due_date()

    def test_task_status_transitions(self):
        task = TaskFactory(status="todo")
        
        # Valid transitions
        task.status = "in_progress"
        assert task.can_transition_to("done") is True
        
        # Invalid transitions
        task.status = "done"
        assert task.can_transition_to("todo") is False
```

#### Business Logic Testing
```python
# tests/unit/test_task_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate
from tests.factories.task_factory import TaskFactory
from tests.factories.user_factory import UserFactory

class TestTaskService:
    @pytest.fixture
    def task_service(self, db_session):
        return TaskService(db_session)

    @pytest.fixture
    def mock_notification_service(self):
        with patch('app.services.notification_service.NotificationService') as mock:
            yield mock

    def test_create_task_success(self, task_service, mock_notification_service):
        user = UserFactory()
        task_data = TaskCreate(
            title="New Task",
            description="Task description",
            assignee_id=user.id
        )
        
        task = task_service.create_task(task_data, created_by=user)
        
        assert task.title == "New Task"
        assert task.assignee_id == user.id
        assert task.created_by == user
        mock_notification_service.send_task_assigned.assert_called_once()

    def test_update_task_with_validation(self, task_service):
        task = TaskFactory()
        update_data = TaskUpdate(
            title="Updated Task",
            status="in_progress"
        )
        
        updated_task = task_service.update_task(task.id, update_data)
        
        assert updated_task.title == "Updated Task"
        assert updated_task.status == "in_progress"

    def test_delete_task_permission_check(self, task_service):
        task = TaskFactory()
        unauthorized_user = UserFactory()
        
        with pytest.raises(PermissionError):
            task_service.delete_task(task.id, user=unauthorized_user)

    def test_assign_task_notification(self, task_service, mock_notification_service):
        task = TaskFactory()
        new_assignee = UserFactory()
        
        task_service.assign_task(task.id, new_assignee.id)
        
        mock_notification_service.send_task_assigned.assert_called_with(
            task, new_assignee
        )
```

### Frontend Unit Testing (React/TypeScript)

#### Test Structure
```
frontend/src/__tests__/
├── components/              # Component unit tests
│   ├── auth/
│   │   ├── LoginForm.test.tsx
│   │   └── RegisterForm.test.tsx
│   ├── tasks/
│   │   ├── TaskList.test.tsx
│   │   ├── TaskItem.test.tsx
│   │   └── TaskForm.test.tsx
│   └── common/
│       ├── Button.test.tsx
│       └── Modal.test.tsx
├── hooks/                   # Custom hook tests
│   ├── useAuth.test.ts
│   ├── useTasks.test.ts
│   └── useLocalStorage.test.ts
├── utils/                   # Utility function tests
│   ├── dateUtils.test.ts
│   ├── validation.test.ts
│   └── formatting.test.ts
├── services/                # Service layer tests
│   ├── api.test.ts
│   ├── authService.test.ts
│   └── taskService.test.ts
└── __mocks__/               # Mock implementations
    ├── api.ts
    └── localStorage.ts
```

#### Test Setup (setupTests.ts)
```typescript
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { server } from './mocks/server';

// Configure testing library
configure({ testIdAttribute: 'data-testid' });

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Start MSW server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

#### Component Testing Example
```typescript
// components/tasks/TaskForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskForm } from '../TaskForm';
import { TaskProvider } from '../../contexts/TaskContext';
import { Task } from '../../types/task';

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'Test Description',
  status: 'todo',
  priority: 'medium',
  assigneeId: null,
  projectId: 'project-1',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

const renderTaskForm = (props = {}) => {
  return render(
    <TaskProvider>
      <TaskForm {...props} />
    </TaskProvider>
  );
};

describe('TaskForm', () => {
  test('renders create form correctly', () => {
    renderTaskForm({ mode: 'create' });
    
    expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
  });

  test('renders edit form with existing data', () => {
    renderTaskForm({ mode: 'edit', task: mockTask });
    
    expect(screen.getByDisplayValue('Test Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test Description')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /update task/i })).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    const user = userEvent.setup();
    renderTaskForm({ mode: 'create' });
    
    await user.click(screen.getByRole('button', { name: /create task/i }));
    
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    renderTaskForm({ mode: 'create', onSubmit });
    
    await user.type(screen.getByLabelText(/task title/i), 'New Task');
    await user.type(screen.getByLabelText(/description/i), 'Task description');
    await user.selectOptions(screen.getByLabelText(/priority/i), 'high');
    await user.click(screen.getByRole('button', { name: /create task/i }));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        title: 'New Task',
        description: 'Task description',
        priority: 'high',
      });
    });
  });

  test('shows loading state during submission', async () => {
    const user = userEvent.setup();
    renderTaskForm({ mode: 'create', isLoading: true });
    
    const submitButton = screen.getByRole('button', { name: /create task/i });
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/creating/i)).toBeInTheDocument();
  });
});
```

#### Hook Testing Example
```typescript
// hooks/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../useAuth';
import { AuthProvider } from '../../contexts/AuthContext';
import * as authService from '../../services/authService';

// Mock the auth service
jest.mock('../../services/authService');
const mockAuthService = authService as jest.Mocked<typeof authService>;

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('should login successfully', async () => {
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };
    const mockTokens = { accessToken: 'token123', refreshToken: 'refresh123' };
    
    mockAuthService.login.mockResolvedValue({ user: mockUser, ...mockTokens });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(localStorage.getItem('accessToken')).toBe('token123');
  });

  test('should handle login failure', async () => {
    const errorMessage = 'Invalid credentials';
    mockAuthService.login.mockRejectedValue(new Error(errorMessage));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      try {
        await result.current.login('test@example.com', 'wrongpassword');
      } catch (error) {
        expect(error.message).toBe(errorMessage);
      }
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  test('should logout and clear tokens', async () => {
    localStorage.setItem('accessToken', 'token123');
    localStorage.setItem('refreshToken', 'refresh123');
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });
});
```

---

## Integration Testing

### Backend Integration Testing

#### API Integration Tests
```python
# tests/integration/test_auth_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.factories.user_factory import UserFactory

client = TestClient(app)

class TestAuthAPI:
    def test_user_registration_flow(self, db_session):
        # Register new user
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "New",
            "last_name": "User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        user = response.json()
        assert user["email"] == user_data["email"]
        assert "password" not in user
        
        # Login with new user
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_protected_endpoint_access(self, db_session, auth_headers):
        # Access protected endpoint with valid token
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        user = response.json()
        assert "email" in user
        assert "password_hash" not in user

    def test_token_refresh_flow(self, db_session):
        user = UserFactory()
        
        # Login to get tokens
        login_data = {"email": user.email, "password": "password"}
        response = client.post("/auth/login", json=login_data)
        tokens = response.json()
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]
```

#### Database Integration Tests
```python
# tests/integration/test_task_operations.py
import pytest
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate
from tests.factories.user_factory import UserFactory
from tests.factories.project_factory import ProjectFactory

class TestTaskOperations:
    @pytest.fixture
    def task_service(self, db_session):
        return TaskService(db_session)

    def test_task_lifecycle(self, task_service, db_session):
        # Setup
        user = UserFactory()
        project = ProjectFactory(created_by=user)
        
        # Create task
        task_data = TaskCreate(
            title="Integration Test Task",
            description="Testing task lifecycle",
            project_id=project.id,
            assignee_id=user.id,
            priority="high"
        )
        task = task_service.create_task(task_data, created_by=user)
        
        # Verify creation
        assert task.title == task_data.title
        assert task.project_id == project.id
        assert task.assignee_id == user.id
        assert task.status == "todo"
        
        # Update task status
        updated_task = task_service.update_task_status(task.id, "in_progress")
        assert updated_task.status == "in_progress"
        
        # Add comment
        comment = task_service.add_comment(
            task.id, 
            "This is a test comment", 
            user.id
        )
        assert comment.content == "This is a test comment"
        assert comment.task_id == task.id
        
        # Complete task
        completed_task = task_service.update_task_status(task.id, "done")
        assert completed_task.status == "done"
        assert completed_task.completed_at is not None
        
        # Verify task in database
        db_session.refresh(task)
        assert task.status == "done"
        assert len(task.comments) == 1
```

### Frontend Integration Testing

#### API Integration with MSW
```typescript
// __mocks__/handlers.ts
import { rest } from 'msw';
import { API_BASE_URL } from '../src/config/api';

export const handlers = [
  // Auth endpoints
  rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
    const { email, password } = req.body as any;
    
    if (email === 'test@example.com' && password === 'password') {
      return res(
        ctx.status(200),
        ctx.json({
          access_token: 'mock-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '1',
            email: 'test@example.com',
            first_name: 'Test',
            last_name: 'User',
          },
        })
      );
    }
    
    return res(
      ctx.status(401),
      ctx.json({ detail: 'Invalid credentials' })
    );
  }),

  // Task endpoints
  rest.get(`${API_BASE_URL}/projects/:projectId/tasks`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [
          {
            id: '1',
            title: 'Test Task 1',
            description: 'First test task',
            status: 'todo',
            priority: 'medium',
            project_id: req.params.projectId,
          },
          {
            id: '2',
            title: 'Test Task 2',
            description: 'Second test task',
            status: 'in_progress',
            priority: 'high',
            project_id: req.params.projectId,
          },
        ],
        total: 2,
        page: 1,
        size: 10,
      })
    );
  }),

  rest.post(`${API_BASE_URL}/projects/:projectId/tasks`, (req, res, ctx) => {
    const taskData = req.body as any;
    return res(
      ctx.status(201),
      ctx.json({
        id: '3',
        ...taskData,
        project_id: req.params.projectId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
    );
  }),
];
```

#### Component Integration Tests
```typescript
// components/TaskDashboard.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskDashboard } from '../TaskDashboard';
import { AppProviders } from '../../providers/AppProviders';
import { BrowserRouter } from 'react-router-dom';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AppProviders>
        {component}
      </AppProviders>
    </BrowserRouter>
  );
};

describe('TaskDashboard Integration', () => {
  test('loads and displays tasks from API', async () => {
    renderWithProviders(<TaskDashboard projectId="project-1" />);
    
    // Show loading state
    expect(screen.getByText(/loading tasks/i)).toBeInTheDocument();
    
    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      expect(screen.getByText('Test Task 2')).toBeInTheDocument();
    });
    
    // Verify task details
    expect(screen.getByText('First test task')).toBeInTheDocument();
    expect(screen.getByText('Second test task')).toBeInTheDocument();
  });

  test('creates new task via form submission', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TaskDashboard projectId="project-1" />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument();
    });
    
    // Open create task form
    await user.click(screen.getByRole('button', { name: /create task/i }));
    
    // Fill out form
    await user.type(screen.getByLabelText(/task title/i), 'New Integration Test Task');
    await user.type(screen.getByLabelText(/description/i), 'Created via integration test');
    await user.selectOptions(screen.getByLabelText(/priority/i), 'high');
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /create task/i }));
    
    // Verify new task appears in list
    await waitFor(() => {
      expect(screen.getByText('New Integration Test Task')).toBeInTheDocument();
    });
  });

  test('filters tasks by status', async () => {
    const user = userEvent.setup();
    renderWithProviders(<TaskDashboard projectId="project-1" />);
    
    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      expect(screen.getByText('Test Task 2')).toBeInTheDocument();
    });
    
    // Filter by 'in_progress' status
    await user.selectOptions(screen.getByLabelText(/filter by status/i), 'in_progress');
    
    // Only in_progress task should be visible
    await waitFor(() => {
      expect(screen.queryByText('Test Task 1')).not.toBeInTheDocument(); // todo status
      expect(screen.getByText('Test Task 2')).toBeInTheDocument(); // in_progress status
    });
  });
});
```

---

## End-to-End Testing

### E2E Test Structure
```
frontend/e2e/
├── support/                 # Helper functions and utilities
│   ├── commands.ts          # Custom Playwright commands
│   ├── fixtures.ts          # Test data fixtures
│   └── page-objects/        # Page object models
│       ├── LoginPage.ts
│       ├── DashboardPage.ts
│       └── TaskPage.ts
├── tests/                   # E2E test files
│   ├── auth.spec.ts         # Authentication flows
│   ├── task-management.spec.ts
│   ├── project-management.spec.ts
│   └── collaboration.spec.ts
└── playwright.config.ts     # Playwright configuration
```

### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/e2e-results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Page Object Models
```typescript
// support/page-objects/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;
  readonly registerLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.loginButton = page.getByRole('button', { name: 'Login' });
    this.errorMessage = page.getByTestId('error-message');
    this.registerLink = page.getByRole('link', { name: 'Register' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async waitForErrorMessage() {
    await this.errorMessage.waitFor();
    return this.errorMessage.textContent();
  }
}
```

### E2E Test Examples
```typescript
// tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../support/page-objects/LoginPage';
import { DashboardPage } from '../support/page-objects/DashboardPage';

test.describe('Authentication', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test('should login with valid credentials', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password');
    
    await dashboardPage.waitForLoad();
    expect(await dashboardPage.getWelcomeMessage()).toContain('Welcome, Test User');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login('test@example.com', 'wrongpassword');
    
    const errorMessage = await loginPage.waitForErrorMessage();
    expect(errorMessage).toContain('Invalid credentials');
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page).toHaveURL('/login');
    expect(await page.getByText('Please log in to continue')).toBeVisible();
  });

  test('should maintain session after page refresh', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password');
    await dashboardPage.waitForLoad();
    
    await page.reload();
    await dashboardPage.waitForLoad();
    
    expect(await dashboardPage.getWelcomeMessage()).toContain('Welcome, Test User');
  });
});
```

```typescript
// tests/task-management.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../support/page-objects/LoginPage';
import { TaskPage } from '../support/page-objects/TaskPage';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password');
  });

  test('should create a new task', async ({ page }) => {
    const taskPage = new TaskPage(page);
    await taskPage.goto('project-1');
    
    await taskPage.clickCreateTask();
    await taskPage.fillTaskForm({
      title: 'E2E Test Task',
      description: 'Created via end-to-end test',
      priority: 'high',
    });
    await taskPage.submitTaskForm();
    
    await expect(taskPage.getTaskByTitle('E2E Test Task')).toBeVisible();
  });

  test('should update task status via drag and drop', async ({ page }) => {
    const taskPage = new TaskPage(page);
    await taskPage.goto('project-1');
    
    const task = taskPage.getTaskByTitle('Test Task');
    const inProgressColumn = taskPage.getColumn('In Progress');
    
    await task.dragTo(inProgressColumn);
    
    // Verify task moved to correct column
    await expect(taskPage.getTaskInColumn('Test Task', 'In Progress')).toBeVisible();
  });

  test('should filter tasks by assignee', async ({ page }) => {
    const taskPage = new TaskPage(page);
    await taskPage.goto('project-1');
    
    await taskPage.selectAssigneeFilter('John Doe');
    
    // Only tasks assigned to John Doe should be visible
    const visibleTasks = await taskPage.getVisibleTasks();
    expect(visibleTasks.length).toBeGreaterThan(0);
    
    for (const task of visibleTasks) {
      expect(await task.getAttribute('data-assignee')).toBe('John Doe');
    }
  });

  test('should search tasks by title', async ({ page }) => {
    const taskPage = new TaskPage(page);
    await taskPage.goto('project-1');
    
    await taskPage.searchTasks('integration');
    
    const searchResults = await taskPage.getSearchResults();
    expect(searchResults.length).toBeGreaterThan(0);
    
    for (const result of searchResults) {
      const title = await result.textContent();
      expect(title?.toLowerCase()).toContain('integration');
    }
  });
});
```

---

## Performance Testing

### Load Testing with Artillery

#### Artillery Configuration
```yaml
# artillery.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 5
      name: "Warm up"
    - duration: 300
      arrivalRate: 10
      name: "Steady load"
    - duration: 120
      arrivalRate: 50
      name: "Spike test"
  payload:
    path: "test-data.csv"
    fields:
      - "email"
      - "password"

scenarios:
  - name: "User authentication and task management"
    weight: 70
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            json: "$.access_token"
            as: "token"
      - get:
          url: "/users/me"
          headers:
            Authorization: "Bearer {{ token }}"
      - get:
          url: "/projects"
          headers:
            Authorization: "Bearer {{ token }}"
          capture:
            json: "$[0].id"
            as: "projectId"
      - get:
          url: "/projects/{{ projectId }}/tasks"
          headers:
            Authorization: "Bearer {{ token }}"
      - post:
          url: "/projects/{{ projectId }}/tasks"
          headers:
            Authorization: "Bearer {{ token }}"
          json:
            title: "Load test task {{ $randomString() }}"
            description: "Created during load test"
            priority: "medium"

  - name: "Read-only operations"
    weight: 30
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            json: "$.access_token"
            as: "token"
      - loop:
          count: 10
          over:
            - get:
                url: "/projects"
                headers:
                  Authorization: "Bearer {{ token }}"
            - get:
                url: "/search/tasks?q=test"
                headers:
                  Authorization: "Bearer {{ token }}"
```

### Frontend Performance Testing

#### Lighthouse CI Configuration
```json
// .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000',
        'http://localhost:3000/login',
        'http://localhost:3000/dashboard',
        'http://localhost:3000/projects/1/tasks'
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox'
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.8 }],
        'categories:seo': ['warn', { minScore: 0.8 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['warn', { maxNumericValue: 4000 }],
        'cumulative-layout-shift': ['warn', { maxNumericValue: 0.1 }]
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};
```

---

## Test Data Management

### Test Database Setup
```python
# scripts/setup_test_data.py
import asyncio
from app.core.database import engine, SessionLocal
from app.models import Base
from tests.factories import (
    UserFactory, 
    OrganizationFactory, 
    ProjectFactory, 
    TaskFactory
)

async def create_test_data():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        # Create test organizations
        org1 = OrganizationFactory(name="Test Organization 1")
        org2 = OrganizationFactory(name="Test Organization 2")
        
        # Create test users
        admin_user = UserFactory(
            email="admin@test.com",
            first_name="Admin",
            last_name="User"
        )
        
        regular_user = UserFactory(
            email="user@test.com",
            first_name="Regular",
            last_name="User"
        )
        
        # Create test projects
        project1 = ProjectFactory(
            organization=org1,
            name="Frontend Redesign",
            created_by=admin_user
        )
        
        project2 = ProjectFactory(
            organization=org1,
            name="API Development",
            created_by=admin_user
        )
        
        # Create test tasks
        for i in range(50):
            TaskFactory(
                project=project1 if i % 2 == 0 else project2,
                created_by=admin_user,
                assignee=regular_user if i % 3 == 0 else admin_user,
                title=f"Test Task {i + 1}",
                status=["todo", "in_progress", "done"][i % 3]
            )
        
        session.commit()
        print("Test data created successfully!")
        
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(create_test_data())
```

### Test Data Cleanup
```python
# conftest.py - Database cleanup
@pytest.fixture(scope="function", autouse=True)
def cleanup_database(db_session):
    """Clean up database after each test."""
    yield
    
    # Delete in reverse order of foreign key dependencies
    db_session.execute("DELETE FROM task_comments")
    db_session.execute("DELETE FROM tasks")
    db_session.execute("DELETE FROM project_members")
    db_session.execute("DELETE FROM projects")
    db_session.execute("DELETE FROM organization_members")
    db_session.execute("DELETE FROM organizations")
    db_session.execute("DELETE FROM users")
    db_session.commit()
```

---

## Continuous Integration Testing

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: teamflow_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        cd backend
        black --check .
        isort --check-only .
        flake8
        mypy app
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/teamflow_test
        REDIS_URL: redis://localhost:6379
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run linting
      run: |
        cd frontend
        npm run lint
        npm run type-check
    
    - name: Run unit tests
      run: |
        cd frontend
        npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info

  e2e-tests:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
        npx playwright install
    
    - name: Start application
      run: |
        docker-compose -f docker-compose.test.yml up -d
        # Wait for services to be ready
        sleep 30
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e
    
    - name: Upload E2E test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: e2e-test-results
        path: frontend/test-results/

  performance-tests:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start application
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
    
    - name: Run load tests
      run: |
        npm install -g artillery
        artillery run artillery.yml --output report.json
        artillery report report.json --output report.html
    
    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-test-results
        path: |
          report.json
          report.html
```

This comprehensive testing strategy ensures that TeamFlow maintains high code quality, reliability, and performance throughout its development lifecycle. The combination of unit, integration, and end-to-end tests provides confidence in the system's behavior at all levels.

---
**Next Document**: [06-deployment-guide.md](./06-deployment-guide.md)
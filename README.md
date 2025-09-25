# TeamFlow - Enterprise Task Management Platform

**Modern, full-stack enterprise task management platform built with FastAPI and React**

TeamFlow provides comprehensive project and task management capabilities with real-time collaboration, advanced analytics, and enterprise-grade security.

## 🌟 Features

- **Multi-tenant Architecture**: Organizations, projects, and tasks hierarchy
- **Advanced Task Management**: Priority levels, assignments, time tracking, dependencies
- **Real-time Collaboration**: Live updates and notifications via WebSockets  
- **File Management**: Document uploads, version control, and thumbnail generation
- **Advanced Search**: Full-text search with faceted filtering
- **Business Intelligence**: Analytics dashboard, performance metrics, and insights
- **Workflow Automation**: Rule-based task automation and notifications
- **Security & Compliance**: JWT authentication, RBAC, audit logging, data protection
- **Optimized Authentication**: High-performance direct database access for critical auth flows

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (recommended)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd teamflow
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MailHog (Email testing): http://localhost:8025
   - pgAdmin (Database admin): http://localhost:5050

### Backend Setup (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost/teamflow"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start the server
python -m uvicorn app.main:app --reload
```

### Frontend Setup (without Docker)

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

teamflow/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── core/         # Core configuration and utilities
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── api/          # API endpoints
│   │   └── services/     # Business logic
│   ├── tests/            # Backend tests
│   └── alembic/          # Database migrations
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # Utility functions
│   │   └── types/        # TypeScript type definitions
│   └── __tests__/        # Frontend tests
├── shared/               # Shared types and utilities
├── docs/                 # Project documentation
├── scripts/              # Development and deployment scripts
└── .github/workflows/    # CI/CD workflows

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **PostgreSQL** - Advanced open source relational database
- **Redis** - In-memory data structure store for caching
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **React 18** - A JavaScript library for building user interfaces
- **TypeScript** - Typed superset of JavaScript
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and state management
- **React Router** - Declarative routing for React

### DevOps
- **Docker** - Containerization platform
- **GitHub Actions** - CI/CD workflows
- **PostgreSQL** - Production database
- **Redis** - Caching and session management

## 📚 Documentation

- **[API Documentation](docs/05-api-documentation.md)**: Complete REST API reference
- **[Development Guide](docs/04-development-guide.md)**: Setup and contribution guidelines
- **[Deployment Guide](docs/06-deployment-guide.md)**: Production deployment instructions
- **[Architecture Overview](docs/ARCHITECTURE.md)**: Technical architecture and design patterns

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🧪 Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

### Code Quality

```bash
# Backend formatting and linting
cd backend
black .
isort .
flake8

# Frontend formatting and linting
cd frontend
npm run lint
npm run format
```

### Database Management

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run migrations
docker-compose exec backend alembic upgrade head

# Reset database (development only)
docker-compose down -v
docker-compose up -d postgres
```

## 🔍 Performance Optimization

TeamFlow includes several performance optimizations, notably:

### Optimized Authentication

The platform includes two authentication methods:

1. **Standard Authentication**: Using FastAPI and SQLAlchemy ORM
2. **Optimized Authentication**: Direct SQLite access that bypasses ORM overhead

To use the optimized authentication endpoints:

```
POST /api/v1/optimized-auth/register  # Register a new user
POST /api/v1/optimized-auth/login     # Get authentication tokens
POST /api/v1/optimized-auth/refresh   # Refresh access token
GET  /api/v1/optimized-auth/me        # Get current user info
```

To compare authentication performance:

```bash
cd backend
python auth_optimizer.py --compare
```

To run authentication diagnostics:

```bash
python auth_optimizer.py --diagnose
```

### Performance Monitoring

Access database performance metrics:

```
GET /api/v1/monitoring/db-performance            # Get performance metrics
GET /api/v1/monitoring/db-performance/auth-comparison  # Compare auth methods
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions and support, please refer to the [documentation](./docs/) or open an issue.

---

**TeamFlow** - Building the future of enterprise task management, one commit at a time. 🚀
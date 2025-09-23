# TeamFlow - Enterprise Task Management Platform

TeamFlow is an enterprise-grade task management and collaboration platform designed to demonstrate advanced full-stack development skills, focusing on readable, testable, maintainable, and scalable code architecture.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

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

## 📁 Project Structure

```
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
```

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

## 📖 Documentation

- **[📋 Project Overview](./docs/01-project-overview.md)** - Vision, goals, and technology stack
- **[🏗️ Technical Architecture](./docs/02-technical-architecture.md)** - System design and API specifications
- **[🚀 Implementation Roadmap](./docs/03-implementation-roadmap.md)** - 12-week development plan
- **[⚙️ Development Setup](./docs/04-development-setup.md)** - Detailed setup instructions
- **[🧪 Testing Strategy](./docs/05-testing-strategy.md)** - Testing approach and examples
- **[🌐 Deployment Guide](./docs/06-deployment-guide.md)** - Production deployment strategies

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

## 🎯 Development Phases

This project is being developed in 6 phases over 12 weeks:

1. **Phase 1**: Project Setup & Foundation (Weeks 1-2) ✅
2. **Phase 2**: Authentication & User Management (Weeks 3-4) 🚧
3. **Phase 3**: Organization & Project Management (Weeks 5-6)
4. **Phase 4**: Task Management Core (Weeks 7-8)
5. **Phase 5**: Advanced Features & Real-time (Weeks 9-10)
6. **Phase 6**: Production Deployment & Optimization (Weeks 11-12)

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
# TeamFlow Backend Development Makefile
.PHONY: help install test test-unit test-integration test-coverage lint format clean dev setup

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
help: ## Show this help message
	@echo "$(BLUE)TeamFlow Backend Development Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Environment setup
setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	@echo "$(YELLOW)Using project-level virtual environment at ../venv$(RESET)"
	cd .. && pip install -e ".[dev]"
	@echo "$(GREEN)Environment setup complete!$(RESET)"

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	cd .. && pip install -e ".[dev]"
	@echo "$(GREEN)Dependencies installed!$(RESET)"

# Testing commands
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(RESET)"
	pytest

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	pytest tests/integration/ -v

test-auth: ## Run authentication tests only
	@echo "$(BLUE)Running authentication tests...$(RESET)"
	pytest -m auth -v

test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(RESET)"
	pytest -m api -v

test-coverage: ## Run tests with detailed coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	pytest --cov=app --cov-report=term-missing --cov-report=html

test-fast: ## Run tests excluding slow ones
	@echo "$(BLUE)Running fast tests...$(RESET)"
	pytest -m "not slow" -x -v

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	ptw -- -x -v

# Code quality
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(RESET)"
	flake8 app/ tests/
	mypy app/
	@echo "$(GREEN)Linting complete!$(RESET)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	black app/ tests/
	isort app/ tests/
	@echo "$(GREEN)Code formatted!$(RESET)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	black --check app/ tests/
	isort --check-only app/ tests/

type-check: ## Run type checking
	@echo "$(BLUE)Running type checks...$(RESET)"
	mypy app/

# Development server
dev: ## Run development server with timeout protection
	@echo "$(BLUE)Starting development server with timeout protection...$(RESET)"
	../scripts/start-server.sh

dev-simple: ## Run simple development server (legacy)
	@echo "$(BLUE)Starting simple development server...$(RESET)"
	cd .. && teamflow-server

dev-debug: ## Run development server with debug logging
	@echo "$(BLUE)Starting development server with debug logging...$(RESET)"
	cd .. && DEBUG=1 teamflow-server

kill-server: ## Emergency server shutdown
	@echo "$(RED)Emergency server shutdown...$(RESET)"
	../scripts/kill-server.sh

# Database operations
db-upgrade: ## Apply database migrations
	@echo "$(BLUE)Applying database migrations...$(RESET)"
	alembic upgrade head

db-downgrade: ## Rollback database migrations
	@echo "$(BLUE)Rolling back database migrations...$(RESET)"
	alembic downgrade -1

db-revision: ## Create new database migration
	@echo "$(BLUE)Creating new database migration...$(RESET)"
	@read -p "Migration message: " message; \
	alembic revision --autogenerate -m "$$message"

db-setup: ## Set up database tables with new architecture
	@echo "$(BLUE)Setting up database tables...$(RESET)"
	python setup_database.py
	@echo "$(GREEN)Database setup complete!$(RESET)"

db-reset: ## Reset database and create tables (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all database data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)Resetting database...$(RESET)"; \
		python setup_database.py --reset; \
		echo "$(GREEN)Database reset complete!$(RESET)"; \
	else \
		echo "$(YELLOW)Database reset cancelled.$(RESET)"; \
	fi

db-sample: ## Reset database and create tables with sample data
	@echo "$(BLUE)Setting up database with sample data...$(RESET)"
	python setup_database.py --reset --sample-data
	@echo "$(GREEN)Database setup with sample data complete!$(RESET)"

# Cleanup
clean: ## Clean temporary files and cache
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "$(GREEN)Cleanup complete!$(RESET)"

clean-db: ## Clean database files
	@echo "$(BLUE)Cleaning database files...$(RESET)"
	rm -f teamflow.db
	rm -f teamflow.db-journal
	@echo "$(GREEN)Database files cleaned!$(RESET)"

# Security and dependencies
security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	pip-audit
	bandit -r app/

update-deps: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	@echo "$(YELLOW)Dependencies are managed in ../pyproject.toml$(RESET)"
	cd .. && pip install -e ".[dev]" --upgrade

# Docker operations (if using Docker)
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t teamflow-backend .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -p 8000:8000 teamflow-backend

# Documentation
docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(RESET)"
	@echo "$(YELLOW)Visit http://localhost:8000/docs when server is running$(RESET)"

# Utility commands
shell: ## Open Python shell with app context
	@echo "$(BLUE)Opening Python shell...$(RESET)"
	python -c "from app.main import app; import IPython; IPython.embed()"

routes: ## List all API routes
	@echo "$(BLUE)API Routes:$(RESET)"
	python -c "from app.main import app; from fastapi.routing import APIRoute; [print(f'{route.methods} {route.path}') for route in app.routes if isinstance(route, APIRoute)]"

# CI/CD helpers
ci-test: ## Run tests in CI mode
	@echo "$(BLUE)Running CI tests...$(RESET)"
	pytest --tb=short --disable-warnings

ci-quality: ## Run all quality checks for CI
	@echo "$(BLUE)Running CI quality checks...$(RESET)"
	black --check app/ tests/
	isort --check-only app/ tests/
	flake8 app/ tests/
	mypy app/
	pytest --tb=short --disable-warnings

# Production helpers
prod-requirements: ## Generate production requirements.txt
	@echo "$(BLUE)Generating production requirements...$(RESET)"
	@echo "$(YELLOW)Production dependencies are defined in ../pyproject.toml$(RESET)"
	cd .. && pip freeze > backend/requirements-generated.txt

health-check: ## Check if server is healthy
	@echo "$(BLUE)Checking server health...$(RESET)"
	curl -f http://localhost:8000/health || echo "$(RED)Server is not responding$(RESET)"

# Quick development workflows
quick-test: format lint test-fast ## Quick development test cycle
	@echo "$(GREEN)Quick test cycle complete!$(RESET)"

full-check: format lint test coverage security-check ## Full quality check
	@echo "$(GREEN)Full quality check complete!$(RESET)"

reset-dev: clean clean-db db-upgrade ## Reset development environment
	@echo "$(GREEN)Development environment reset!$(RESET)"

# CI/CD specific commands
.PHONY: ci-docker-test ci-local-pipeline
ci-docker-test: ## Test Docker build and health check
	@echo "$(BLUE)Testing Docker build and health check...$(RESET)"
	docker build -t teamflow-backend .
	docker run --rm -d -p 8000:8000 --name test-container teamflow-backend
	sleep 10
	curl -f http://localhost:8000/health || (docker stop test-container && exit 1)
	docker stop test-container
	@echo "$(GREEN)Docker test passed!$(RESET)"

ci-local-pipeline: deps format lint test coverage security-check ci-docker-test ## Run full local CI pipeline
	@echo "$(GREEN)🎉 Local CI pipeline completed successfully!$(RESET)"
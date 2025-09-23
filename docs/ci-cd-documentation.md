# CI/CD Pipeline Documentation

## Overview

TeamFlow uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline ensures code quality, runs tests, and automates deployments.

## Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### Test Job
- **Environment:** Ubuntu latest with PostgreSQL 15
- **Steps:**
  1. Checkout code
  2. Set up Python 3.12
  3. Cache dependencies
  4. Install dependencies
  5. Run linting (flake8, black)
  6. Run type checking (mypy)
  7. Run tests with coverage
  8. Upload coverage to Codecov

#### Build Job
- **Environment:** Ubuntu latest
- **Dependencies:** Requires test job to pass
- **Steps:**
  1. Checkout code
  2. Set up Docker Buildx
  3. Build backend Docker image
  4. Test Docker image health endpoint

#### Security Job
- **Environment:** Ubuntu latest
- **Steps:**
  1. Run security scans (bandit, safety)
  2. Upload security reports as artifacts

### 2. Deploy Pipeline (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to tags starting with `v` (e.g., `v1.0.0`)
- Manual workflow dispatch

**Jobs:**
- Build and push Docker images to GitHub Container Registry
- Deploy to staging environment
- Deploy to production environment (requires manual approval)

### 3. Dependency Updates (`.github/workflows/dependencies.yml`)

**Triggers:**
- Scheduled: Every Monday at 10 AM UTC
- Manual workflow dispatch

**Jobs:**
- Update Python dependencies
- Run security audit
- Create pull request with updates

## Local Development

### Running CI Checks Locally

```bash
# Run full local CI pipeline
make ci-local-pipeline

# Run individual checks
make lint          # Code linting
make test          # Run tests
make coverage      # Generate coverage report
make security-check # Security scan
make ci-docker-test # Test Docker build
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Environment Configuration

### CI Environment Variables

The CI pipeline uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection for tests
- `SECRET_KEY`: JWT secret for testing
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Secrets Required

For deployment workflows, configure these secrets in GitHub:

- `GITHUB_TOKEN`: Automatically provided by GitHub
- Additional secrets for production deployment (TBD)

## Code Quality Standards

### Test Requirements
- Minimum 60% code coverage
- All tests must pass
- Integration tests for API endpoints
- Unit tests for business logic

### Code Style
- **Formatter:** Black with 88-character line length
- **Import Sorting:** isort
- **Linting:** flake8 with standard configuration
- **Type Checking:** mypy (non-blocking for now)

### Security
- **Static Analysis:** bandit for Python security issues
- **Dependency Scanning:** safety for known vulnerabilities
- Regular dependency updates via automated PRs

## Deployment Strategy

### Environments

1. **Development:** Local development with SQLite
2. **Staging:** Automated deployment from `develop` branch
3. **Production:** Manual deployment from version tags

### Docker Images

Images are built and stored in GitHub Container Registry:
- `ghcr.io/[username]/teamflow:latest`
- `ghcr.io/[username]/teamflow:v1.0.0` (tagged releases)

### Health Checks

All deployments include health check validation:
- HTTP endpoint: `/health`
- Database connectivity verification
- Dependencies status check

## Monitoring and Alerts

### Coverage Reporting
- Codecov integration for coverage tracking
- Coverage reports in CI artifacts
- HTML coverage reports for local development

### Security Monitoring
- Weekly dependency vulnerability scans
- Security report artifacts in CI
- Automated dependency update PRs

## Best Practices

### Branch Protection
- Require status checks to pass
- Require up-to-date branches
- Require review from code owners
- Restrict force pushes

### Pull Request Workflow
1. Create feature branch from `develop`
2. Make changes with tests
3. Run local CI checks: `make ci-local-pipeline`
4. Submit pull request
5. Wait for CI to pass and review
6. Merge to `develop` for staging deployment

### Release Process
1. Create release branch from `develop`
2. Update version numbers
3. Create pull request to `main`
4. After merge, create git tag: `git tag v1.0.0`
5. Push tag to trigger production deployment

## Troubleshooting

### Common Issues

**Tests failing in CI but passing locally:**
- Check environment variables in CI
- Verify database schema in test environment
- Check for timing issues in async tests

**Docker build failures:**
- Verify Dockerfile syntax
- Check dependency installation
- Ensure all required files are included

**Coverage below threshold:**
- Add tests for uncovered code
- Check test discovery patterns
- Verify coverage configuration

### Debug Commands

```bash
# Test Docker build locally
make ci-docker-test

# Check what tests are discovered
pytest --collect-only

# Run tests with verbose output
pytest -v

# Check coverage report
make coverage
open htmlcov/index.html
```

## Future Enhancements

- [ ] Add frontend CI/CD pipeline
- [ ] Implement blue-green deployment
- [ ] Add performance testing
- [ ] Set up monitoring and alerting
- [ ] Add automatic rollback on failure
- [ ] Implement infrastructure as code
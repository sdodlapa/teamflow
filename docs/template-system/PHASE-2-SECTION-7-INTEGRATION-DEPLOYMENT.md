# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 7: Integration & Deployment

---

## 🚀 INTEGRATION & DEPLOYMENT FRAMEWORK

### **Docker Configuration Generator**

The deployment system automatically generates production-ready Docker configurations, CI/CD pipelines, and infrastructure as code for template-generated applications.

#### **Docker Generator** (`backend/app/core/docker_generator.py`)
```python
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.domain_config import DomainConfig

class DockerGenerator:
    """Generate Docker configurations from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.dockerfile_template = self.env.get_template('Dockerfile.j2')
        self.compose_template = self.env.get_template('docker-compose.yml.j2')
        self.nginx_template = self.env.get_template('nginx.conf.j2')
    
    def generate_backend_dockerfile(self, domain_config: DomainConfig) -> str:
        """Generate optimized Dockerfile for FastAPI backend"""
        
        python_version = domain_config.deployment.get('python_version', '3.11')
        requirements = self._extract_backend_requirements(domain_config)
        
        # Determine if async database is used
        uses_async_db = any(
            entity.features.get('async_operations', True) 
            for entity in domain_config.entities.values()
        )
        
        return self.dockerfile_template.render(
            service_type='backend',
            python_version=python_version,
            requirements=requirements,
            uses_async_db=uses_async_db,
            domain_name=domain_config.domain.name.lower().replace(' ', '-'),
            port=domain_config.deployment.get('backend_port', 8000),
            workers=domain_config.deployment.get('workers', 4),
            environment=domain_config.deployment.get('environment', 'production')
        )
    
    def generate_frontend_dockerfile(self, domain_config: DomainConfig) -> str:
        """Generate optimized Dockerfile for React frontend"""
        
        node_version = domain_config.deployment.get('node_version', '18-alpine')
        build_args = domain_config.deployment.get('build_args', {})
        
        return self.dockerfile_template.render(
            service_type='frontend',
            node_version=node_version,
            build_args=build_args,
            domain_name=domain_config.domain.name.lower().replace(' ', '-'),
            port=domain_config.deployment.get('frontend_port', 3000),
            api_url=domain_config.deployment.get('api_url', 'http://localhost:8000')
        )
    
    def generate_docker_compose(self, domain_config: DomainConfig) -> str:
        """Generate docker-compose.yml for full stack deployment"""
        
        services = self._extract_required_services(domain_config)
        networks = self._generate_network_config(domain_config)
        volumes = self._generate_volume_config(domain_config)
        
        return self.compose_template.render(
            domain_name=domain_config.domain.name.lower().replace(' ', '-'),
            services=services,
            networks=networks,
            volumes=volumes,
            environment=domain_config.deployment.get('environment', 'production'),
            database_type=domain_config.database.get('type', 'postgresql'),
            redis_enabled=domain_config.features.get('caching', False),
            monitoring_enabled=domain_config.deployment.get('monitoring', True)
        )
    
    def generate_nginx_config(self, domain_config: DomainConfig) -> str:
        """Generate Nginx configuration for reverse proxy"""
        
        domain_name = domain_config.deployment.get('domain', 'localhost')
        ssl_enabled = domain_config.deployment.get('ssl', False)
        
        upstream_servers = self._generate_upstream_config(domain_config)
        
        return self.nginx_template.render(
            domain_name=domain_name,
            ssl_enabled=ssl_enabled,
            upstream_servers=upstream_servers,
            backend_port=domain_config.deployment.get('backend_port', 8000),
            frontend_port=domain_config.deployment.get('frontend_port', 3000),
            max_body_size=domain_config.deployment.get('max_upload_size', '50M'),
            rate_limiting=domain_config.deployment.get('rate_limiting', True)
        )
    
    def _extract_backend_requirements(self, domain_config: DomainConfig) -> List[str]:
        """Extract Python requirements based on domain features"""
        base_requirements = [
            'fastapi>=0.100.0',
            'uvicorn[standard]>=0.22.0',
            'sqlalchemy[asyncio]>=2.0.0',
            'pydantic>=2.0.0',
            'alembic>=1.11.0',
            'python-jose[cryptography]>=3.3.0',
            'passlib[bcrypt]>=1.7.4',
            'python-multipart>=0.0.6'
        ]
        
        # Add database-specific requirements
        db_type = domain_config.database.get('type', 'postgresql')
        if db_type == 'postgresql':
            base_requirements.extend([
                'asyncpg>=0.28.0',
                'psycopg2-binary>=2.9.0'
            ])
        elif db_type == 'mysql':
            base_requirements.extend([
                'aiomysql>=0.2.0',
                'PyMySQL>=1.1.0'
            ])
        
        # Add feature-specific requirements
        if domain_config.features.get('caching'):
            base_requirements.append('redis>=4.5.0')
        
        if domain_config.features.get('file_upload'):
            base_requirements.extend([
                'aiofiles>=23.0.0',
                'python-magic>=0.4.27'
            ])
        
        if domain_config.features.get('email'):
            base_requirements.append('fastapi-mail>=1.4.0')
        
        if domain_config.features.get('monitoring'):
            base_requirements.extend([
                'prometheus-client>=0.17.0',
                'structlog>=23.0.0'
            ])
        
        return base_requirements
    
    def _extract_required_services(self, domain_config: DomainConfig) -> List[Dict]:
        """Extract required Docker services"""
        services = []
        
        # Backend service
        services.append({
            'name': 'backend',
            'type': 'api',
            'port': domain_config.deployment.get('backend_port', 8000),
            'health_check': '/health',
            'dependencies': ['database']
        })
        
        # Frontend service
        services.append({
            'name': 'frontend',
            'type': 'web',
            'port': domain_config.deployment.get('frontend_port', 3000),
            'dependencies': ['backend']
        })
        
        # Database service
        db_type = domain_config.database.get('type', 'postgresql')
        services.append({
            'name': 'database',
            'type': db_type,
            'port': 5432 if db_type == 'postgresql' else 3306,
            'volume': f"{domain_config.domain.name.lower()}_db_data"
        })
        
        # Redis service (if caching enabled)
        if domain_config.features.get('caching'):
            services.append({
                'name': 'redis',
                'type': 'redis',
                'port': 6379,
                'volume': f"{domain_config.domain.name.lower()}_redis_data"
            })
        
        # Nginx service (if reverse proxy enabled)
        if domain_config.deployment.get('reverse_proxy'):
            services.append({
                'name': 'nginx',
                'type': 'nginx',
                'port': 80,
                'ssl_port': 443 if domain_config.deployment.get('ssl') else None,
                'dependencies': ['backend', 'frontend']
            })
        
        return services
```

#### **Dockerfile Template** (`templates/deployment/Dockerfile.j2`)
```dockerfile
{% if service_type == 'backend' %}
# FastAPI Backend Dockerfile for {{ domain_name }}
FROM python:{{ python_version }}-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{{ port }}/health || exit 1

# Expose port
EXPOSE {{ port }}

# Production command
{% if environment == 'production' %}
CMD ["gunicorn", "app.main:app", "-w", "{{ workers }}", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:{{ port }}"]
{% else %}
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{{ port }}", "--reload"]
{% endif %}

{% elif service_type == 'frontend' %}
# React Frontend Dockerfile for {{ domain_name }}
FROM node:{{ node_version }} as build

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build arguments
{% for key, value in build_args.items() %}
ARG {{ key }}={{ value }}
{% endfor %}

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Expose port
EXPOSE {{ port }}

CMD ["nginx", "-g", "daemon off;"]
{% endif %}
```

#### **Docker Compose Template** (`templates/deployment/docker-compose.yml.j2`)
```yaml
# Docker Compose for {{ domain_name }} Application
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: {{ domain_name }}-backend
    restart: unless-stopped
    ports:
      - "{{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}:{{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}"
    environment:
      - DATABASE_URL={% if database_type == 'postgresql' %}postgresql://postgres:password@database:5432/{{ domain_name }}{% else %}mysql://root:password@database:3306/{{ domain_name }}{% endif %}
      {% if redis_enabled %}
      - REDIS_URL=redis://redis:6379/0
      {% endif %}
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-in-production}
      - ENVIRONMENT={{ environment }}
    depends_on:
      - database
      {% if redis_enabled %}
      - redis
      {% endif %}
    volumes:
      - ./backend/uploads:/app/uploads
    networks:
      - {{ domain_name }}-network
    {% if monitoring_enabled %}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{{ domain_name }}-backend.rule=Host(`api.{{ domain_name }}.local`)"
      - "traefik.http.services.{{ domain_name }}-backend.loadbalancer.server.port={{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}"
    {% endif %}

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_URL=http://localhost:{{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}
    container_name: {{ domain_name }}-frontend
    restart: unless-stopped
    ports:
      - "{{ services | selectattr('name', 'equalto', 'frontend') | map(attribute='port') | first }}:{{ services | selectattr('name', 'equalto', 'frontend') | map(attribute='port') | first }}"
    depends_on:
      - backend
    networks:
      - {{ domain_name }}-network
    {% if monitoring_enabled %}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{{ domain_name }}-frontend.rule=Host(`{{ domain_name }}.local`)"
      - "traefik.http.services.{{ domain_name }}-frontend.loadbalancer.server.port={{ services | selectattr('name', 'equalto', 'frontend') | map(attribute='port') | first }}"
    {% endif %}

  database:
    {% if database_type == 'postgresql' %}
    image: postgres:15-alpine
    container_name: {{ domain_name }}-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB={{ domain_name }}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - {{ domain_name }}_db_data:/var/lib/postgresql/data
    {% else %}
    image: mysql:8.0
    container_name: {{ domain_name }}-mysql
    restart: unless-stopped
    environment:
      - MYSQL_DATABASE={{ domain_name }}
      - MYSQL_ROOT_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - {{ domain_name }}_db_data:/var/lib/mysql
    {% endif %}
    networks:
      - {{ domain_name }}-network

  {% if redis_enabled %}
  redis:
    image: redis:7-alpine
    container_name: {{ domain_name }}-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - {{ domain_name }}_redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - {{ domain_name }}-network
  {% endif %}

  {% if 'nginx' in services | map(attribute='name') %}
  nginx:
    image: nginx:alpine
    container_name: {{ domain_name }}-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      {% if services | selectattr('name', 'equalto', 'nginx') | selectattr('ssl_port') | list %}
      - "443:443"
      {% endif %}
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      {% if services | selectattr('name', 'equalto', 'nginx') | selectattr('ssl_port') | list %}
      - ./nginx/ssl:/etc/nginx/ssl:ro
      {% endif %}
    depends_on:
      - backend
      - frontend
    networks:
      - {{ domain_name }}-network
  {% endif %}

  {% if monitoring_enabled %}
  prometheus:
    image: prom/prometheus:latest
    container_name: {{ domain_name }}-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - {{ domain_name }}_prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - {{ domain_name }}-network

  grafana:
    image: grafana/grafana:latest
    container_name: {{ domain_name }}-grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - {{ domain_name }}_grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - {{ domain_name }}-network
  {% endif %}

volumes:
  {{ domain_name }}_db_data:
  {% if redis_enabled %}
  {{ domain_name }}_redis_data:
  {% endif %}
  {% if monitoring_enabled %}
  {{ domain_name }}_prometheus_data:
  {{ domain_name }}_grafana_data:
  {% endif %}

networks:
  {{ domain_name }}-network:
    driver: bridge
```

### **CI/CD Pipeline Generator**

#### **GitHub Actions Generator** (`backend/app/core/cicd_generator.py`)
```python
class CICDGenerator:
    """Generate CI/CD pipeline configurations"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.github_actions_template = self.env.get_template('github-actions.yml.j2')
        self.gitlab_ci_template = self.env.get_template('gitlab-ci.yml.j2')
    
    def generate_github_actions(self, domain_config: DomainConfig) -> str:
        """Generate GitHub Actions workflow"""
        
        # Extract test configuration
        test_config = self._extract_test_config(domain_config)
        
        # Extract deployment configuration
        deployment_config = self._extract_deployment_config(domain_config)
        
        # Extract security scanning configuration
        security_config = self._extract_security_config(domain_config)
        
        return self.github_actions_template.render(
            domain_name=domain_config.domain.name.lower().replace(' ', '-'),
            python_version=domain_config.deployment.get('python_version', '3.11'),
            node_version=domain_config.deployment.get('node_version', '18'),
            test_config=test_config,
            deployment_config=deployment_config,
            security_config=security_config,
            database_type=domain_config.database.get('type', 'postgresql'),
            has_frontend=True,  # Always true for full-stack templates
            docker_registry=domain_config.deployment.get('docker_registry', 'ghcr.io'),
            environments=domain_config.deployment.get('environments', ['staging', 'production'])
        )
```

#### **GitHub Actions Template** (`templates/deployment/github-actions.yml.j2`)
```yaml
# CI/CD Pipeline for {{ domain_name }}
name: {{ domain_name | title }} CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: {{ docker_registry }}
  IMAGE_NAME: {{ domain_name }}

jobs:
  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    
    services:
      {% if database_type == 'postgresql' %}
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_{{ domain_name }}
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      {% else %}
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_{{ domain_name }}
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
        ports:
          - 3306:3306
      {% endif %}
      
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
    - uses: actions/checkout@v4
    
    - name: Set up Python {{ python_version }}
      uses: actions/setup-python@v4
      with:
        python-version: {{ python_version }}
    
    - name: Cache Python dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run linting
      working-directory: ./backend
      run: |
        flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check app/
        isort --check-only app/
    
    - name: Run type checking
      working-directory: ./backend
      run: mypy app/
    
    - name: Run tests
      working-directory: ./backend
      env:
        {% if database_type == 'postgresql' %}
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_{{ domain_name }}
        {% else %}
        DATABASE_URL: mysql://root:root@localhost:3306/test_{{ domain_name }}
        {% endif %}
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
        TESTING: true
      run: |
        pytest --cov=app --cov-report=xml --cov-report=html -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

  {% if has_frontend %}
  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js {{ node_version }}
      uses: actions/setup-node@v4
      with:
        node-version: {{ node_version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run linting
      working-directory: ./frontend
      run: npm run lint
    
    - name: Run type checking
      working-directory: ./frontend
      run: npm run type-check
    
    - name: Run tests
      working-directory: ./frontend
      run: npm run test:ci
    
    - name: Build application
      working-directory: ./frontend
      run: npm run build
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend
        name: frontend-coverage
  {% endif %}

  {% if security_config.enabled %}
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Run Bandit security linter
      working-directory: ./backend
      run: |
        pip install bandit
        bandit -r app/ -f json -o bandit-report.json
    
    - name: Run npm audit
      working-directory: ./frontend
      run: npm audit --audit-level moderate
  {% endif %}

  build-and-push:
    name: Build and Push Docker Images
    runs-on: ubuntu-latest
    needs: [test-backend{% if has_frontend %}, test-frontend{% endif %}]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata (tags, labels) for backend
      id: meta-backend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ github.repository }}/backend
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix=sha-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ${{ steps.meta-backend.outputs.tags }}
        labels: ${{ steps.meta-backend.outputs.labels }}
    
    {% if has_frontend %}
    - name: Extract metadata (tags, labels) for frontend
      id: meta-frontend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ github.repository }}/frontend
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix=sha-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ steps.meta-frontend.outputs.tags }}
        labels: ${{ steps.meta-frontend.outputs.labels }}
    {% endif %}

  {% for env in environments %}
  deploy-{{ env }}:
    name: Deploy to {{ env | title }}
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: {{ env }}
    {% if env == 'production' %}
    if: github.ref == 'refs/heads/main'
    {% endif %}
    
    steps:
    - name: Deploy to {{ env | title }}
      run: |
        echo "Deploying to {{ env }} environment"
        # Add your deployment commands here
        # Examples:
        # - kubectl apply -f k8s/{{ env }}/
        # - docker-compose -f docker-compose.{{ env }}.yml up -d
        # - terraform apply -var-file={{ env }}.tfvars
  {% endfor %}
```

### **Kubernetes Configuration Generator**

#### **Kubernetes Template** (`templates/deployment/kubernetes.yml.j2`)
```yaml
# Kubernetes deployment for {{ domain_name }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ domain_name }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ domain_name }}-backend
  namespace: {{ domain_name }}
  labels:
    app: {{ domain_name }}-backend
spec:
  replicas: {{ deployment_config.backend_replicas | default(3) }}
  selector:
    matchLabels:
      app: {{ domain_name }}-backend
  template:
    metadata:
      labels:
        app: {{ domain_name }}-backend
    spec:
      containers:
      - name: backend
        image: {{ docker_registry }}/{{ domain_name }}/backend:latest
        ports:
        - containerPort: {{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ domain_name }}-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: {{ domain_name }}-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: {{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: {{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {{ domain_name }}-backend-service
  namespace: {{ domain_name }}
spec:
  selector:
    app: {{ domain_name }}-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: {{ services | selectattr('name', 'equalto', 'backend') | map(attribute='port') | first }}
  type: ClusterIP
---
{% if has_frontend %}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ domain_name }}-frontend
  namespace: {{ domain_name }}
  labels:
    app: {{ domain_name }}-frontend
spec:
  replicas: {{ deployment_config.frontend_replicas | default(2) }}
  selector:
    matchLabels:
      app: {{ domain_name }}-frontend
  template:
    metadata:
      labels:
        app: {{ domain_name }}-frontend
    spec:
      containers:
      - name: frontend
        image: {{ docker_registry }}/{{ domain_name }}/frontend:latest
        ports:
        - containerPort: {{ services | selectattr('name', 'equalto', 'frontend') | map(attribute='port') | first }}
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: {{ domain_name }}-frontend-service
  namespace: {{ domain_name }}
spec:
  selector:
    app: {{ domain_name }}-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: {{ services | selectattr('name', 'equalto', 'frontend') | map(attribute='port') | first }}
  type: ClusterIP
---
{% endif %}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ domain_name }}-ingress
  namespace: {{ domain_name }}
  annotations:
    kubernetes.io/ingress.class: nginx
    {% if deployment_config.ssl %}
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    {% endif %}
spec:
  {% if deployment_config.ssl %}
  tls:
  - hosts:
    - {{ deployment_config.domain }}
    - api.{{ deployment_config.domain }}
    secretName: {{ domain_name }}-tls
  {% endif %}
  rules:
  - host: {{ deployment_config.domain | default('localhost') }}
    http:
      paths:
      {% if has_frontend %}
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ domain_name }}-frontend-service
            port:
              number: 80
      {% endif %}
  - host: api.{{ deployment_config.domain | default('localhost') }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ domain_name }}-backend-service
            port:
              number: 80
```

---

*Continue to Section 8: Migration & Adaptation Manual...*
# TeamFlow - Deployment Guide

## Deployment Overview

This guide covers deployment strategies from local development through production deployment. The current implementation focuses on backend deployment with containerization planned for Phase 5.

## Current Status
- ✅ **Development Setup**: Complete local development environment
- ✅ **Backend Ready**: Production-ready FastAPI application
- 📅 **Containerization**: Planned for Phase 5
- 📅 **CI/CD Pipeline**: Planned for Phase 5
- 📅 **Production Deployment**: Planned for Phase 5

---

## Local Development Deployment

### Prerequisites
- Python 3.11+
- Git
- SQLite (included) or PostgreSQL

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd teamflow/backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Configuration
```env
# .env file for development
DATABASE_URL=sqlite:///./teamflow.db
SECRET_KEY=development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=True
ENVIRONMENT=development
```

### Infrastructure as Code
All infrastructure is managed using Terraform for consistency, versioning, and reproducibility across environments.

---

## Local Development Deployment

### Docker Compose Setup

#### Development Configuration (docker-compose.yml)
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: teamflow-postgres-dev
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-teamflow_dev}
      POSTGRES_USER: ${POSTGRES_USER:-teamflow}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-teamflow_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-teamflow}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: teamflow-redis-dev
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis_dev_password}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: teamflow-backend-dev
    environment:
      - DATABASE_URL=postgresql://teamflow:teamflow_dev@postgres:5432/teamflow_dev
      - REDIS_URL=redis://:redis_dev_password@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Application
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: teamflow-frontend-dev
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000/ws
      - VITE_ENVIRONMENT=development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev -- --host 0.0.0.0

  # Email Testing (MailHog)
  mailhog:
    image: mailhog/mailhog:v1.0.1
    container_name: teamflow-mailhog-dev
    ports:
      - "8025:8025"  # Web UI
      - "1025:1025"  # SMTP

  # Database Administration (pgAdmin)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: teamflow-pgadmin-dev
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@teamflow.dev
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
  backend_uploads:
  pgadmin_data:

networks:
  default:
    name: teamflow-network
```

#### Development Dockerfiles

**Backend Dockerfile (backend/Dockerfile.dev)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Frontend Dockerfile (frontend/Dockerfile.dev)**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

---

## Staging Deployment (AWS ECS)

### Infrastructure Setup with Terraform

#### Main Terraform Configuration (infra/staging/main.tf)
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "teamflow-terraform-state"
    key    = "staging/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = "staging"
      Project     = "teamflow"
      ManagedBy   = "terraform"
    }
  }
}

# VPC and Networking
module "networking" {
  source = "../modules/networking"
  
  environment = "staging"
  cidr_block  = "10.1.0.0/16"
  
  availability_zones = ["us-west-2a", "us-west-2b"]
  
  public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnet_cidrs = ["10.1.11.0/24", "10.1.12.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true  # Cost optimization for staging
}

# RDS Database
module "database" {
  source = "../modules/database"
  
  environment = "staging"
  
  instance_class = "db.t3.micro"
  engine_version = "15.4"
  
  database_name = "teamflow_staging"
  username      = "teamflow"
  
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.security.database_security_group_id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true  # For staging only
}

# ElastiCache Redis
module "cache" {
  source = "../modules/cache"
  
  environment = "staging"
  
  node_type = "cache.t3.micro"
  
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.security.cache_security_group_id]
}

# ECS Cluster
module "ecs" {
  source = "../modules/ecs"
  
  environment = "staging"
  
  vpc_id     = module.networking.vpc_id
  subnet_ids = module.networking.private_subnet_ids
  
  database_url = module.database.connection_string
  redis_url    = module.cache.connection_string
  
  backend_image  = "teamflow/backend:staging"
  frontend_image = "teamflow/frontend:staging"
  
  backend_cpu    = 256
  backend_memory = 512
  
  frontend_cpu    = 256
  frontend_memory = 512
  
  desired_count = 1
  
  load_balancer_subnets = module.networking.public_subnet_ids
  load_balancer_security_group_ids = [module.security.alb_security_group_id]
}

# Security Groups
module "security" {
  source = "../modules/security"
  
  environment = "staging"
  vpc_id      = module.networking.vpc_id
}

# Route 53 DNS
module "dns" {
  source = "../modules/dns"
  
  environment = "staging"
  domain_name = "staging.teamflow.app"
  
  load_balancer_dns_name = module.ecs.load_balancer_dns_name
  load_balancer_zone_id  = module.ecs.load_balancer_zone_id
}
```

#### ECS Module (infra/modules/ecs/main.tf)
```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-teamflow"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "${var.environment}-teamflow-cluster"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-teamflow-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.load_balancer_security_group_ids
  subnets            = var.load_balancer_subnets
  
  enable_deletion_protection = var.environment == "production"
  
  tags = {
    Name = "${var.environment}-teamflow-alb"
  }
}

# Target Groups
resource "aws_lb_target_group" "backend" {
  name     = "${var.environment}-backend-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  target_type = "ip"
  
  tags = {
    Name = "${var.environment}-backend-target-group"
  }
}

resource "aws_lb_target_group" "frontend" {
  name     = "${var.environment}-frontend-tg"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  target_type = "ip"
  
  tags = {
    Name = "${var.environment}-frontend-target-group"
  }
}

# Load Balancer Listeners
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.main.arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.main.arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
  
  condition {
    path_pattern {
      values = ["/api/*", "/docs", "/redoc"]
    }
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "backend"
      image = var.backend_image
      
      essential = true
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "DATABASE_URL"
          value = var.database_url
        },
        {
          name  = "REDIS_URL"
          value = var.redis_url
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      ]
      
      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = aws_ssm_parameter.secret_key.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = {
    Name = "${var.environment}-backend-task"
  }
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.frontend_cpu
  memory                   = var.frontend_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = var.frontend_image
      
      essential = true
      
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "VITE_API_URL"
          value = "https://${var.environment}.teamflow.app/api"
        },
        {
          name  = "VITE_ENVIRONMENT"
          value = var.environment
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  
  tags = {
    Name = "${var.environment}-frontend-task"
  }
}

# ECS Services
resource "aws_ecs_service" "backend" {
  name            = "${var.environment}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.main]
  
  tags = {
    Name = "${var.environment}-backend-service"
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "${var.environment}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }
  
  depends_on = [aws_lb_listener.main]
  
  tags = {
    Name = "${var.environment}-frontend-service"
  }
}
```

---

## Production Deployment (AWS EKS)

### Kubernetes Manifests

#### Namespace and ConfigMap
```yaml
# k8s/namespaces/teamflow.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: teamflow
  labels:
    name: teamflow
    environment: production

---
# k8s/configmaps/app-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: teamflow
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://teamflow.app"
  DATABASE_MAX_CONNECTIONS: "20"
  REDIS_MAX_CONNECTIONS: "10"
```

#### Secrets Management
```yaml
# k8s/secrets/app-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: teamflow
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  SMTP_PASSWORD: <base64-encoded-smtp-password>
```

#### Backend Deployment
```yaml
# k8s/deployments/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: teamflow
  labels:
    app: backend
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
      version: v1
  template:
    metadata:
      labels:
        app: backend
        version: v1
    spec:
      containers:
      - name: backend
        image: teamflow/backend:v1.0.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: ENVIRONMENT
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: SECRET_KEY
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: REDIS_URL
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
      serviceAccountName: teamflow-backend
      securityContext:
        fsGroup: 1000

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: teamflow
  labels:
    app: backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: backend
```

#### Frontend Deployment
```yaml
# k8s/deployments/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: teamflow
  labels:
    app: frontend
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
      version: v1
  template:
    metadata:
      labels:
        app: frontend
        version: v1
    spec:
      containers:
      - name: frontend
        image: teamflow/frontend:v1.0.0
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: VITE_API_URL
          value: "https://api.teamflow.app"
        - name: VITE_ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
      serviceAccountName: teamflow-frontend
      securityContext:
        fsGroup: 1000

---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: teamflow
  labels:
    app: frontend
spec:
  type: ClusterIP
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app: frontend
```

#### Ingress Configuration
```yaml
# k8s/ingress/teamflow-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: teamflow-ingress
  namespace: teamflow
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/backend-protocol: HTTP
spec:
  rules:
  - host: teamflow.app
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
  - host: api.teamflow.app
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

#### Horizontal Pod Autoscaler
```yaml
# k8s/hpa/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: teamflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 60

---
# k8s/hpa/frontend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: teamflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 3
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Production Dockerfiles

### Backend Production Dockerfile
```dockerfile
# backend/Dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r teamflow && useradd -r -g teamflow teamflow

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/teamflow/.local

# Copy application code
COPY . .

# Create uploads directory and set permissions
RUN mkdir -p uploads \
    && chown -R teamflow:teamflow /app

# Switch to non-root user
USER teamflow

# Add local Python packages to PATH
ENV PATH=/home/teamflow/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Frontend Production Dockerfile
```dockerfile
# frontend/Dockerfile
# Multi-stage build for production
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Create non-root user
RUN addgroup -g 1001 -S teamflow && \
    adduser -S teamflow -u 1001

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx cache directory and set permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    && chown -R teamflow:teamflow /var/cache/nginx \
    && chown -R teamflow:teamflow /usr/share/nginx/html \
    && touch /var/run/nginx.pid \
    && chown teamflow:teamflow /var/run/nginx.pid

# Switch to non-root user
USER teamflow

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
# frontend/nginx.conf
user teamflow;
worker_processes auto;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    server {
        listen 3000;
        server_name _;
        
        root /usr/share/nginx/html;
        index index.html;

        # Enable browser caching for static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Security: Don't allow access to sensitive files
        location ~ /\. {
            deny all;
        }

        location ~ /(package\.json|package-lock\.json|yarn\.lock)$ {
            deny all;
        }
    }
}
```

---

## CI/CD Pipeline for Deployment

### GitHub Actions Deployment Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

env:
  AWS_REGION: us-west-2
  ECR_REPOSITORY_BACKEND: teamflow/backend
  ECR_REPOSITORY_FRONTEND: teamflow/frontend

jobs:
  # Determine deployment environment and version
  setup:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.determine-env.outputs.environment }}
      version: ${{ steps.determine-version.outputs.version }}
      deploy: ${{ steps.determine-deploy.outputs.deploy }}
    steps:
    - name: Determine environment
      id: determine-env
      run: |
        if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
          echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
        elif [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
          echo "environment=staging" >> $GITHUB_OUTPUT
        elif [[ "${{ github.ref }}" == refs/tags/v* ]]; then
          echo "environment=production" >> $GITHUB_OUTPUT
        else
          echo "environment=none" >> $GITHUB_OUTPUT
        fi

    - name: Determine version
      id: determine-version
      run: |
        if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
          echo "version=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
        else
          echo "version=${GITHUB_SHA:0:7}" >> $GITHUB_OUTPUT
        fi

    - name: Determine if should deploy
      id: determine-deploy
      run: |
        if [[ "${{ steps.determine-env.outputs.environment }}" != "none" ]]; then
          echo "deploy=true" >> $GITHUB_OUTPUT
        else
          echo "deploy=false" >> $GITHUB_OUTPUT
        fi

  # Build and push Docker images
  build:
    needs: setup
    if: needs.setup.outputs.deploy == 'true'
    runs-on: ubuntu-latest
    environment: ${{ needs.setup.outputs.environment }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build and push backend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ needs.setup.outputs.version }}
      run: |
        cd backend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG
        
        # Also tag as latest for the environment
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:${{ needs.setup.outputs.environment }}
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:${{ needs.setup.outputs.environment }}

    - name: Build and push frontend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ needs.setup.outputs.version }}
        VITE_API_URL: ${{ vars.VITE_API_URL }}
        VITE_ENVIRONMENT: ${{ needs.setup.outputs.environment }}
      run: |
        cd frontend
        docker build \
          --build-arg VITE_API_URL=$VITE_API_URL \
          --build-arg VITE_ENVIRONMENT=$VITE_ENVIRONMENT \
          -t $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG
        
        # Also tag as latest for the environment
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:${{ needs.setup.outputs.environment }}
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:${{ needs.setup.outputs.environment }}

  # Deploy to staging (ECS)
  deploy-staging:
    needs: [setup, build]
    if: needs.setup.outputs.environment == 'staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Deploy to ECS
      run: |
        # Update ECS service to use new image
        aws ecs update-service \
          --cluster staging-teamflow \
          --service staging-backend \
          --force-new-deployment

        aws ecs update-service \
          --cluster staging-teamflow \
          --service staging-frontend \
          --force-new-deployment

    - name: Wait for deployment to complete
      run: |
        aws ecs wait services-stable \
          --cluster staging-teamflow \
          --services staging-backend staging-frontend

    - name: Run database migrations
      run: |
        # Get backend task definition
        TASK_DEF=$(aws ecs describe-task-definition --task-definition staging-backend --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Run migration task
        aws ecs run-task \
          --cluster staging-teamflow \
          --task-definition $TASK_DEF \
          --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=DISABLED}" \
          --overrides '{"containerOverrides":[{"name":"backend","command":["python","-m","alembic","upgrade","head"]}]}'

  # Deploy to production (EKS)
  deploy-production:
    needs: [setup, build]
    if: needs.setup.outputs.environment == 'production'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region ${{ env.AWS_REGION }} --name production-teamflow

    - name: Update deployment images
      env:
        ECR_REGISTRY: ${{ secrets.ECR_REGISTRY }}
        IMAGE_TAG: ${{ needs.setup.outputs.version }}
      run: |
        kubectl set image deployment/backend -n teamflow \
          backend=$ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG

        kubectl set image deployment/frontend -n teamflow \
          frontend=$ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG

    - name: Wait for rollout to complete
      run: |
        kubectl rollout status deployment/backend -n teamflow --timeout=600s
        kubectl rollout status deployment/frontend -n teamflow --timeout=600s

    - name: Run database migrations
      run: |
        kubectl create job migration-${{ needs.setup.outputs.version }} \
          --from=deployment/backend \
          -n teamflow \
          -- python -m alembic upgrade head

        kubectl wait --for=condition=complete job/migration-${{ needs.setup.outputs.version }} -n teamflow --timeout=300s

    - name: Run smoke tests
      run: |
        # Wait for services to be ready
        kubectl wait --for=condition=available deployment/backend -n teamflow --timeout=300s
        kubectl wait --for=condition=available deployment/frontend -n teamflow --timeout=300s
        
        # Run basic health checks
        kubectl exec deployment/backend -n teamflow -- curl -f http://localhost:8000/health
        kubectl exec deployment/frontend -n teamflow -- curl -f http://localhost:3000/health

  # Notify deployment status
  notify:
    needs: [setup, build, deploy-staging, deploy-production]
    if: always() && needs.setup.outputs.deploy == 'true'
    runs-on: ubuntu-latest
    
    steps:
    - name: Notify Slack on success
      if: ${{ success() }}
      uses: 8398a7/action-slack@v3
      with:
        status: success
        channel: '#deployments'
        message: |
          ✅ TeamFlow successfully deployed to ${{ needs.setup.outputs.environment }}
          Version: ${{ needs.setup.outputs.version }}
          Commit: ${{ github.sha }}
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    - name: Notify Slack on failure
      if: ${{ failure() }}
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        channel: '#deployments'
        message: |
          ❌ TeamFlow deployment to ${{ needs.setup.outputs.environment }} failed
          Version: ${{ needs.setup.outputs.version }}
          Commit: ${{ github.sha }}
          Please check the GitHub Actions logs.
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Monitoring and Observability

### CloudWatch Configuration
```yaml
# monitoring/cloudwatch-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudwatch-config
  namespace: amazon-cloudwatch
data:
  cwagentconfig.json: |
    {
      "agent": {
        "region": "us-west-2",
        "debug": false
      },
      "logs": {
        "metrics_collected": {
          "kubernetes": {
            "metrics_collection_interval": 60,
            "cluster_name": "production-teamflow",
            "namespace_name": "teamflow"
          }
        },
        "log_groups": [
          {
            "log_group_name": "/aws/containerinsights/production-teamflow/application",
            "log_stream_name": "{namespace_name}-{pod_name}-{container_name}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "timezone": "UTC"
          }
        ]
      },
      "metrics": {
        "namespace": "TeamFlow/Application",
        "metrics_collected": {
          "cpu": {
            "measurement": [
              "cpu_usage_idle",
              "cpu_usage_iowait",
              "cpu_usage_user",
              "cpu_usage_system"
            ],
            "metrics_collection_interval": 60
          },
          "memory": {
            "measurement": [
              "mem_used_percent"
            ],
            "metrics_collection_interval": 60
          },
          "disk": {
            "measurement": [
              "used_percent"
            ],
            "metrics_collection_interval": 60,
            "resources": [
              "*"
            ]
          }
        }
      }
    }
```

### Application Performance Monitoring (APM)
```python
# backend/app/core/monitoring.py
import time
import logging
from functools import wraps
from typing import Callable, Any
import boto3
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')

# CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name='us-west-2')

logger = logging.getLogger(__name__)

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = 'success'
            return result
        except Exception as e:
            status = 'error'
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            REQUEST_LATENCY.observe(duration)
            
            # Send custom metrics to CloudWatch
            cloudwatch.put_metric_data(
                Namespace='TeamFlow/Application',
                MetricData=[
                    {
                        'MetricName': f'{func.__name__}_duration',
                        'Value': duration,
                        'Unit': 'Seconds',
                        'Dimensions': [
                            {
                                'Name': 'Status',
                                'Value': status
                            }
                        ]
                    }
                ]
            )
    
    return wrapper

def setup_monitoring():
    """Initialize monitoring and metrics collection."""
    # Start Prometheus metrics server
    start_http_server(9090)
    
    # Setup structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(name)s"}',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger.info("Monitoring and metrics collection initialized")

class HealthCheck:
    """Application health check utilities."""
    
    @staticmethod
    async def check_database() -> bool:
        """Check database connectivity."""
        try:
            from app.core.database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    async def check_redis() -> bool:
        """Check Redis connectivity."""
        try:
            from app.core.cache import redis_client
            await redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    @staticmethod
    async def check_external_services() -> dict:
        """Check external service dependencies."""
        checks = {
            'database': await HealthCheck.check_database(),
            'redis': await HealthCheck.check_redis(),
        }
        
        # Add more service checks as needed
        # checks['email_service'] = await HealthCheck.check_email_service()
        
        return checks
```

This comprehensive deployment guide provides everything needed to deploy TeamFlow from local development to production-grade AWS infrastructure. The combination of containerization, infrastructure as code, and automated CI/CD ensures reliable, scalable deployments with proper monitoring and observability.

---
**Final Document**: Complete implementation ready for phase-by-phase development!
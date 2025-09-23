# TeamFlow - API Documentation

## API Overview

TeamFlow provides a comprehensive REST API built with FastAPI, featuring automatic OpenAPI documentation, JWT authentication, and multi-tenant architecture.

**Base URL**: `http://localhost:8000/api/v1`  
**Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)  
**OpenAPI Spec**: `http://localhost:8000/openapi.json`

## Authentication

### JWT Token-Based Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### **POST /auth/register**
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### **POST /auth/login**
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## User Management

### **GET /users/me**
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "status": "ACTIVE",
  "created_at": "2025-09-23T10:00:00Z",
  "updated_at": "2025-09-23T10:00:00Z"
}
```

### **PUT /users/me**
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

---

## Organization Management

### **POST /organizations/**
Create a new organization.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Acme Corp",
  "description": "Technology company focused on innovation"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Acme Corp",
  "description": "Technology company focused on innovation",
  "created_by": 1,
  "status": "ACTIVE",
  "created_at": "2025-09-23T10:00:00Z",
  "member_count": 1
}
```

### **GET /organizations/**
List user's organizations.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

**Response (200):**
```json
{
  "organizations": [
    {
      "id": 1,
      "name": "Acme Corp",
      "description": "Technology company",
      "status": "ACTIVE",
      "role": "ADMIN",
      "member_count": 5,
      "created_at": "2025-09-23T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### **GET /organizations/{org_id}**
Get specific organization details.

### **PUT /organizations/{org_id}**
Update organization (Admin only).

### **POST /organizations/{org_id}/members**
Add member to organization.

**Request Body:**
```json
{
  "user_email": "member@example.com",
  "role": "MEMBER"
}
```

### **GET /organizations/{org_id}/members**
List organization members.

---

## Project Management

### **POST /projects/**
Create a new project within an organization.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "organization_id": 1
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Complete redesign of company website",
  "organization_id": 1,
  "created_by": 1,
  "status": "ACTIVE",
  "created_at": "2025-09-23T10:00:00Z",
  "member_count": 1
}
```

### **GET /projects/**
List user's projects across all organizations.

**Query Parameters:**
- `organization_id` (int): Filter by organization
- `status` (str): Filter by status (ACTIVE, COMPLETED, ARCHIVED)
- `skip` (int): Pagination offset
- `limit` (int): Results per page

### **GET /projects/{project_id}**
Get specific project details with members.

### **PUT /projects/{project_id}**
Update project details.

### **POST /projects/{project_id}/members**
Add member to project.

### **GET /projects/{project_id}/members**
List project members.

---

## Task Management

### **POST /tasks/**
Create a new task within a project.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Design homepage mockups",
  "description": "Create wireframes and mockups for new homepage",
  "project_id": 1,
  "assignee_id": 2,
  "priority": "HIGH",
  "status": "TODO",
  "estimated_hours": 8,
  "due_date": "2025-09-30T17:00:00Z",
  "tags": ["design", "frontend", "urgent"]
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Design homepage mockups",
  "description": "Create wireframes and mockups for new homepage",
  "project_id": 1,
  "assignee_id": 2,
  "created_by": 1,
  "priority": "HIGH",
  "status": "TODO",
  "estimated_hours": 8,
  "actual_hours": null,
  "due_date": "2025-09-30T17:00:00Z",
  "tags": ["design", "frontend", "urgent"],
  "is_active": true,
  "created_at": "2025-09-23T10:00:00Z",
  "updated_at": "2025-09-23T10:00:00Z"
}
```

### **GET /tasks/**
List tasks with filtering and pagination.

**Query Parameters:**
- `project_id` (int): Filter by project
- `assignee_id` (int): Filter by assigned user
- `status` (str): Filter by status (TODO, IN_PROGRESS, IN_REVIEW, DONE, CANCELLED)
- `priority` (str): Filter by priority (LOW, MEDIUM, HIGH, URGENT)
- `search` (str): Search in title and description
- `tags` (str): Filter by tags (comma-separated)
- `due_before` (datetime): Tasks due before date
- `due_after` (datetime): Tasks due after date
- `skip` (int): Pagination offset
- `limit` (int): Results per page

**Response (200):**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Design homepage mockups",
      "status": "TODO",
      "priority": "HIGH",
      "assignee_name": "John Doe",
      "project_name": "Website Redesign",
      "due_date": "2025-09-30T17:00:00Z",
      "created_at": "2025-09-23T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

### **GET /tasks/{task_id}**
Get specific task with full details and relationships.

**Response (200):**
```json
{
  "id": 1,
  "title": "Design homepage mockups",
  "description": "Create wireframes and mockups for new homepage",
  "project": {
    "id": 1,
    "name": "Website Redesign"
  },
  "assignee": {
    "id": 2,
    "full_name": "John Doe",
    "email": "john@example.com"
  },
  "creator": {
    "id": 1,
    "full_name": "Admin User"
  },
  "priority": "HIGH",
  "status": "TODO",
  "estimated_hours": 8,
  "actual_hours": null,
  "due_date": "2025-09-30T17:00:00Z",
  "tags": ["design", "frontend", "urgent"],
  "comments_count": 0,
  "dependencies_count": 0,
  "created_at": "2025-09-23T10:00:00Z",
  "updated_at": "2025-09-23T10:00:00Z"
}
```

### **PUT /tasks/{task_id}**
Update task details.

### **PATCH /tasks/{task_id}/status**
Quick status update.

**Request Body:**
```json
{
  "status": "IN_PROGRESS",
  "actual_hours": 3
}
```

### **DELETE /tasks/{task_id}**
Soft delete task (marks as inactive).

---

## Task Comments

### **POST /tasks/{task_id}/comments**
Add comment to task.

**Request Body:**
```json
{
  "content": "Added initial wireframe sketches to the shared folder."
}
```

**Response (201):**
```json
{
  "id": 1,
  "content": "Added initial wireframe sketches to the shared folder.",
  "task_id": 1,
  "user": {
    "id": 1,
    "full_name": "John Doe"
  },
  "created_at": "2025-09-23T14:30:00Z"
}
```

### **GET /tasks/{task_id}/comments**
List task comments.

**Response (200):**
```json
{
  "comments": [
    {
      "id": 1,
      "content": "Added initial wireframe sketches to the shared folder.",
      "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com"
      },
      "created_at": "2025-09-23T14:30:00Z",
      "updated_at": "2025-09-23T14:30:00Z"
    }
  ],
  "total": 1
}
```

---

## Task Dependencies

### **POST /tasks/{task_id}/dependencies**
Add task dependency.

**Request Body:**
```json
{
  "depends_on_id": 2
}
```

### **GET /tasks/{task_id}/dependencies**
List task dependencies.

### **DELETE /tasks/{task_id}/dependencies/{dependency_id}**
Remove task dependency.

---

## Bulk Operations

### **POST /tasks/bulk**
Create multiple tasks from template or list.

**Request Body:**
```json
{
  "project_id": 1,
  "tasks": [
    {
      "title": "Task 1",
      "description": "First task description"
    },
    {
      "title": "Task 2", 
      "description": "Second task description"
    }
  ]
}
```

### **PATCH /tasks/bulk**
Update multiple tasks.

**Request Body:**
```json
{
  "task_ids": [1, 2, 3],
  "updates": {
    "status": "IN_PROGRESS",
    "assignee_id": 2
  }
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-09-23T10:00:00Z"
}
```

### Common HTTP Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error)
- **401**: Unauthorized (invalid/missing token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **422**: Unprocessable Entity (validation error)
- **500**: Internal Server Error

### Common Error Codes
- `INVALID_CREDENTIALS`: Login failed
- `TOKEN_EXPIRED`: JWT token expired
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `VALIDATION_ERROR`: Request data validation failed
- `DUPLICATE_RESOURCE`: Resource already exists

---

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute per IP
- **General API**: 100 requests per minute per user
- **Bulk operations**: 10 requests per minute per user

## Data Models

### User Statuses
- `ACTIVE`: Normal active user
- `INACTIVE`: Temporarily disabled
- `SUSPENDED`: Account suspended

### Task Statuses
- `TODO`: Not started
- `IN_PROGRESS`: Currently being worked on
- `IN_REVIEW`: Awaiting review/approval
- `DONE`: Completed successfully
- `CANCELLED`: Cancelled or abandoned

### Task Priorities
- `LOW`: Nice to have
- `MEDIUM`: Standard priority
- `HIGH`: Important, should be prioritized
- `URGENT`: Critical, immediate attention required

### Organization/Project Roles
- `ADMIN`: Full administrative access
- `MEMBER`: Standard member access

This API documentation provides comprehensive coverage of all implemented endpoints with request/response examples and detailed parameter information.
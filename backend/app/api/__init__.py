"""API router initialization."""

from fastapi import APIRouter

# Import routes with file management commented out temporarily
from app.api.routes import auth, organizations, projects, tasks, users, advanced_features, websocket, search, workflow, webhooks, security, performance, performance_optimization, admin, config, enhanced_comments, comment_attachments, comment_websockets, comment_search, task_analytics, workflow_automation, enhanced_tasks, templates, db_performance
# Redundant auth routes archived: fast_auth, optimized_auth
# from app.api.routes import files  # Disabled for deployment
from app.api import template, health

# Create main API router
api_router = APIRouter()

# Health check endpoints (not prefixed to be accessible at root)
api_router.include_router(health.router, tags=["health"])

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    advanced_features.router, prefix="/advanced", tags=["advanced-features"]
)
api_router.include_router(
    websocket.router, prefix="/realtime", tags=["realtime-collaboration"]
)
# api_router.include_router(files.router, prefix="/files", tags=["file-management"])  # Disabled for deployment
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(workflow.router, tags=["workflow-automation"])
api_router.include_router(webhooks.router, tags=["webhooks-integrations"])
api_router.include_router(security.router, prefix="/security", tags=["security-compliance"])
api_router.include_router(performance.router, tags=["performance-optimization"])
api_router.include_router(performance_optimization.router, prefix="/optimization", tags=["advanced-optimization"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin-dashboard"])
api_router.include_router(config.router, prefix="/config", tags=["system-configuration"])

# Enhanced comment system routes (Day 2)
api_router.include_router(enhanced_comments.router, prefix="/tasks", tags=["enhanced-comments"])
# TODO LATER: Re-enable after file management system dependencies resolved (libmagic)
# api_router.include_router(comment_attachments.router, prefix="/comments", tags=["comment-attachments"])
api_router.include_router(comment_websockets.router, prefix="/realtime", tags=["comment-websockets"])
api_router.include_router(comment_search.router, prefix="/search", tags=["comment-search"])

# Day 3: Advanced Task Management & Workflow Automation
api_router.include_router(task_analytics.router, prefix="/api/v1", tags=["task-analytics"])
api_router.include_router(workflow_automation.router, prefix="/api/v1", tags=["workflow-automation"])
api_router.include_router(enhanced_tasks.router, prefix="/api/v1", tags=["enhanced-task-management"])

# Template system routes
api_router.include_router(template.router, prefix="/template", tags=["template-system"])

# Database persistence templates API (Day 13)
api_router.include_router(templates.router, prefix="/templates", tags=["template-persistence"])

# Template Builder routes (new)
try:
    from app.api import template_builder
    api_router.include_router(template_builder.router, prefix="/templates/builder", tags=["template-builder"])
except ImportError:
    # Template builder not available yet
    pass

# Removed redundant auth routes that were causing confusion:
# - fast_auth: Direct SQLite implementation (redundant with main auth)  
# - optimized_auth: Alternative auth system (redundant with main auth)

# Database performance monitoring (commented out - was causing hanging)
api_router.include_router(db_performance.router, prefix="/monitoring", tags=["db-performance-monitoring"])

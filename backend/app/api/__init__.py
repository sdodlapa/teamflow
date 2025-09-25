"""API router initialization."""

from fastapi import APIRouter

from app.api.routes import auth, organizations, projects, tasks, users, advanced_features, websocket, files, search, workflow, webhooks, security, performance, performance_optimization, admin, config, enhanced_comments, comment_attachments, comment_websockets, comment_search, task_analytics, workflow_automation, enhanced_tasks, templates
from app.api import template

# Create main API router
api_router = APIRouter()

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
api_router.include_router(files.router, prefix="/files", tags=["file-management"])
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
api_router.include_router(comment_attachments.router, prefix="/comments", tags=["comment-attachments"])
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

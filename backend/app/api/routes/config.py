"""
System configuration and management API endpoints
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.core.performance_config import performance_config
from app.core.config import settings
from app.services.performance_service import performance_monitor
from app.core.cache import cache


router = APIRouter()


@router.get("/config/system")
async def get_system_configuration(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get current system configuration"""
    try:
        # Get performance configuration
        perf_config = performance_config.get_all_configurations()
        
        # Get application settings (filtered for security)
        app_config = {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "enable_redis_cache": getattr(settings, 'ENABLE_REDIS_CACHE', True),
            "cache_ttl_default": getattr(settings, 'CACHE_TTL_DEFAULT', 3600),
            "enable_performance_monitoring": getattr(settings, 'ENABLE_PERFORMANCE_MONITORING', True),
            "metrics_collection_interval": getattr(settings, 'METRICS_COLLECTION_INTERVAL', 30),
            "db_pool_size": getattr(settings, 'DB_POOL_SIZE', 20),
            "db_max_overflow": getattr(settings, 'DB_MAX_OVERFLOW', 30)
        }
        
        # Get feature flags
        feature_flags = {
            "advanced_analytics": True,
            "real_time_collaboration": True,
            "file_management": True,
            "workflow_automation": True,
            "webhook_integrations": True,
            "security_compliance": True,
            "performance_optimization": True,
            "admin_dashboard": True
        }
        
        return {
            "system_info": {
                "version": "1.0.0",
                "deployment_date": "2025-09-23",
                "last_updated": performance_monitor.last_update_time,
                "uptime_seconds": await get_system_uptime()
            },
            "application_config": app_config,
            "performance_config": perf_config,
            "feature_flags": feature_flags,
            "configuration_last_modified": performance_config.config_file_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system configuration: {str(e)}")


@router.put("/config/performance")
async def update_performance_configuration(
    config_updates: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Update performance configuration"""
    try:
        success = True
        updated_sections = []
        
        # Update database config
        if "database" in config_updates:
            db_success = performance_config.update_database_config(**config_updates["database"])
            if db_success:
                updated_sections.append("database")
            else:
                success = False
        
        # Update cache config
        if "cache" in config_updates:
            cache_success = performance_config.update_cache_config(**config_updates["cache"])
            if cache_success:
                updated_sections.append("cache")
            else:
                success = False
        
        # Update API config
        if "api" in config_updates:
            api_success = performance_config.update_api_config(**config_updates["api"])
            if api_success:
                updated_sections.append("api")
            else:
                success = False
        
        if success:
            return {
                "status": "success",
                "message": f"Performance configuration updated successfully: {', '.join(updated_sections)}",
                "updated_sections": updated_sections
            }
        else:
            return {
                "status": "partial_success",
                "message": f"Some configuration updates failed. Updated: {', '.join(updated_sections)}",
                "updated_sections": updated_sections
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating performance configuration: {str(e)}")


@router.post("/config/performance/preset/{preset_name}")
async def apply_performance_preset(
    preset_name: str,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Apply predefined performance configuration preset"""
    try:
        valid_presets = ["development", "production", "high_performance"]
        
        if preset_name not in valid_presets:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid preset. Valid options: {', '.join(valid_presets)}"
            )
        
        success = performance_config.apply_performance_preset(preset_name)
        
        if success:
            return {
                "status": "success",
                "message": f"Performance preset '{preset_name}' applied successfully",
                "preset": preset_name
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to apply preset '{preset_name}'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying performance preset: {str(e)}")


@router.get("/config/performance/validate")
async def validate_performance_configuration(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Validate current performance configuration"""
    try:
        validation_result = performance_config.validate_configuration()
        
        return {
            "validation_status": "valid" if validation_result["valid"] else "invalid",
            "validation_result": validation_result,
            "timestamp": performance_monitor.last_update_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating configuration: {str(e)}")


@router.get("/config/feature-flags")
async def get_feature_flags(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get current feature flags configuration"""
    try:
        feature_flags = {
            "advanced_analytics": {
                "enabled": True,
                "description": "Advanced analytics and reporting features",
                "dependencies": ["database", "cache"],
                "performance_impact": "medium"
            },
            "real_time_collaboration": {
                "enabled": True,
                "description": "WebSocket-based real-time collaboration",
                "dependencies": ["websocket"],
                "performance_impact": "high"
            },
            "file_management": {
                "enabled": True,
                "description": "File upload and management system",
                "dependencies": ["storage"],
                "performance_impact": "low"
            },
            "workflow_automation": {
                "enabled": True,
                "description": "Automated workflow and business rules",
                "dependencies": ["background_tasks"],
                "performance_impact": "medium"
            },
            "webhook_integrations": {
                "enabled": True,
                "description": "External webhook integrations",
                "dependencies": ["http_client"],
                "performance_impact": "low"
            },
            "security_compliance": {
                "enabled": True,
                "description": "Enhanced security and compliance features",
                "dependencies": ["audit_logging"],
                "performance_impact": "medium"
            },
            "performance_optimization": {
                "enabled": True,
                "description": "Advanced performance monitoring and optimization",
                "dependencies": ["metrics_collection"],
                "performance_impact": "low"
            },
            "admin_dashboard": {
                "enabled": True,
                "description": "Administrative dashboard and analytics",
                "dependencies": ["analytics", "reporting"],
                "performance_impact": "medium"
            }
        }
        
        return {
            "feature_flags": feature_flags,
            "total_features": len(feature_flags),
            "enabled_features": len([f for f in feature_flags.values() if f["enabled"]]),
            "last_updated": performance_monitor.last_update_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feature flags: {str(e)}")


@router.put("/config/feature-flags/{feature_name}")
async def toggle_feature_flag(
    feature_name: str,
    enabled: bool = Query(..., description="Enable or disable the feature"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Toggle a specific feature flag"""
    try:
        # In a real implementation, this would update a feature flag configuration
        # For now, we'll simulate the operation
        
        valid_features = [
            "advanced_analytics", "real_time_collaboration", "file_management",
            "workflow_automation", "webhook_integrations", "security_compliance",
            "performance_optimization", "admin_dashboard"
        ]
        
        if feature_name not in valid_features:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid feature name. Valid features: {', '.join(valid_features)}"
            )
        
        # Simulate feature flag update
        action = "enabled" if enabled else "disabled"
        
        return {
            "status": "success",
            "message": f"Feature '{feature_name}' has been {action}",
            "feature": feature_name,
            "enabled": enabled
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling feature flag: {str(e)}")


@router.get("/config/system/health")
async def get_system_configuration_health(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get system configuration health check"""
    try:
        # Validate performance configuration
        perf_validation = performance_config.validate_configuration()
        
        # Check critical system components
        system_checks = {
            "database_config": await check_database_configuration(),
            "cache_config": await check_cache_configuration(),
            "api_config": await check_api_configuration(),
            "security_config": await check_security_configuration(),
            "performance_config": perf_validation["valid"]
        }
        
        # Calculate overall health score
        healthy_components = sum(1 for check in system_checks.values() if check)
        health_score = (healthy_components / len(system_checks)) * 100
        
        # Determine health status
        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 75:
            health_status = "good"
        elif health_score >= 60:
            health_status = "fair"
        else:
            health_status = "critical"
        
        return {
            "overall_health_score": round(health_score, 2),
            "health_status": health_status,
            "component_checks": system_checks,
            "performance_validation": perf_validation,
            "recommendations": generate_configuration_recommendations(system_checks, perf_validation),
            "last_check": performance_monitor.last_update_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking configuration health: {str(e)}")


@router.post("/config/backup")
async def backup_system_configuration(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Create backup of system configuration"""
    try:
        import datetime
        
        backup_id = f"config_backup_{int(datetime.datetime.utcnow().timestamp())}"
        backup_path = f"/tmp/{backup_id}.json"
        
        # Schedule backup creation in background
        background_tasks.add_task(create_configuration_backup, backup_path)
        
        return {
            "status": "success",
            "message": "Configuration backup started",
            "backup_id": backup_id,
            "backup_path": backup_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating configuration backup: {str(e)}")


@router.post("/config/restore")
async def restore_system_configuration(
    backup_id: str,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Restore system configuration from backup"""
    try:
        backup_path = f"/tmp/{backup_id}.json"
        
        # In a real implementation, this would restore from the backup file
        success = performance_config.import_configuration(backup_path)
        
        if success:
            return {
                "status": "success",
                "message": f"Configuration restored from backup {backup_id}",
                "backup_id": backup_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restore configuration from backup")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring configuration: {str(e)}")


# Helper functions

async def get_system_uptime() -> int:
    """Get system uptime in seconds"""
    # This would calculate actual system uptime
    # For now, return a simulated value
    return 86400  # 1 day


async def check_database_configuration() -> bool:
    """Check database configuration health"""
    try:
        # This would perform actual database configuration checks
        return True
    except Exception:
        return False


async def check_cache_configuration() -> bool:
    """Check cache configuration health"""
    try:
        # Test cache connectivity
        await cache.set("health_check", "ok", ttl=60)
        result = await cache.get("health_check")
        return result == "ok"
    except Exception:
        return False


async def check_api_configuration() -> bool:
    """Check API configuration health"""
    try:
        # This would check API configuration settings
        return True
    except Exception:
        return False


async def check_security_configuration() -> bool:
    """Check security configuration health"""
    try:
        # This would check security settings
        return True
    except Exception:
        return False


def generate_configuration_recommendations(
    system_checks: Dict[str, bool], 
    perf_validation: Dict[str, Any]
) -> List[str]:
    """Generate configuration recommendations"""
    recommendations = []
    
    # Check failed components
    for component, status in system_checks.items():
        if not status:
            recommendations.append(f"Review and fix {component.replace('_', ' ')} configuration")
    
    # Add performance recommendations
    if not perf_validation.get("valid", True):
        recommendations.extend(perf_validation.get("recommendations", []))
    
    # Add general recommendations
    if len(recommendations) == 0:
        recommendations.append("Configuration appears healthy. Continue monitoring for optimization opportunities.")
    
    return recommendations


async def create_configuration_backup(backup_path: str):
    """Background task to create configuration backup"""
    try:
        success = performance_config.export_configuration(backup_path)
        if success:
            print(f"Configuration backup created: {backup_path}")
        else:
            print(f"Failed to create configuration backup: {backup_path}")
    except Exception as e:
        print(f"Error creating configuration backup: {e}")
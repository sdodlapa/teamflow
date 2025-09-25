"""
API endpoints for monitoring database performance.
"""

from fastapi import APIRouter, Depends, Response

from app.services.db_performance import db_performance_monitor
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/db-performance")
async def get_db_performance_metrics(current_user = Depends(get_current_user)):
    """
    Get database performance metrics.
    Requires authenticated user.
    """
    stats = db_performance_monitor.get_stats_summary()
    return stats


@router.post("/db-performance/reset", status_code=204)
async def reset_db_performance_metrics(current_user = Depends(get_current_user)):
    """
    Reset database performance metrics.
    Requires authenticated user.
    """
    db_performance_monitor.reset_stats()
    return Response(status_code=204)


@router.get("/db-performance/auth-comparison")
async def get_auth_performance_comparison(current_user = Depends(get_current_user)):
    """
    Compare performance between standard and optimized auth endpoints.
    Requires authenticated user.
    """
    # Extract endpoint stats specifically for auth endpoints
    endpoint_stats = db_performance_monitor.query_stats.get("endpoint_stats", {})
    
    # Filter for auth-related endpoints
    auth_stats = {
        endpoint: stats for endpoint, stats in endpoint_stats.items()
        if "auth" in endpoint.lower()
    }
    
    # Organize by auth type (optimized_auth routes archived)
    comparison = {
        "main_auth": {},
        "archived_auth": {},  # Previously optimized_auth, now archived
        "recommendation": "Using main auth system - redundant auth systems archived"
    }
    
    # Populate comparison data
    for endpoint, stats in auth_stats.items():
        if "optimized" in endpoint.lower() or "fast" in endpoint.lower():
            comparison["archived_auth"][endpoint] = stats
        else:
            comparison["main_auth"][endpoint] = stats
    
    # Generate recommendation based on main auth performance
    main_avg = 0
    main_count = 0
    archived_avg = 0
    archived_count = 0
    
    for stats in comparison["main_auth"].values():
        if stats["count"] > 0:
            main_avg += stats["avg_time"]
            main_count += 1
    
    for stats in comparison["archived_auth"].values():
        opt_avg += stats.get("avg_ms", 0)
        opt_count += 1
    
    if std_count > 0:
        std_avg /= std_count
    
    if opt_count > 0:
        opt_avg /= opt_count
    
    if std_count > 0 and opt_count > 0:
        if opt_avg < std_avg * 0.8:  # 20% improvement threshold
            comparison["recommendation"] = (
                f"The optimized auth is {(std_avg - opt_avg) / std_avg * 100:.1f}% "
                f"faster than standard auth. Recommend using optimized auth endpoints."
            )
        else:
            comparison["recommendation"] = (
                "No significant performance difference detected between auth methods."
            )
    elif std_count > 0:
        comparison["recommendation"] = (
            "No data available for optimized auth. Try the optimized auth endpoints."
        )
    elif opt_count > 0:
        comparison["recommendation"] = (
            "No data available for standard auth. Only optimized auth is being used."
        )
    else:
        comparison["recommendation"] = "Insufficient data to make a recommendation."
    
    return comparison
"""
Database performance monitoring module with specific optimizations for auth queries.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_performance")

# Define threshold constants
SLOW_QUERY_THRESHOLD_MS = 500
CRITICAL_QUERY_THRESHOLD_MS = 2000


class DatabasePerformanceMonitor:
    """
    Monitor and track database performance metrics.
    """
    
    def __init__(self):
        self.query_stats = {
            "total_queries": 0,
            "slow_queries": 0,
            "critical_queries": 0,
            "query_times": [],
            "slow_query_details": [],
            "hourly_stats": {},
            "endpoint_stats": {},
        }
        self.last_reset = datetime.utcnow()
    
    def record_query_time(
        self, 
        query_type: str, 
        duration_ms: float, 
        query_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a query execution time."""
        # Update overall stats
        self.query_stats["total_queries"] += 1
        self.query_stats["query_times"].append(duration_ms)
        
        # Keep query times list manageable
        if len(self.query_stats["query_times"]) > 1000:
            self.query_stats["query_times"] = self.query_stats["query_times"][-1000:]
        
        # Track slow queries
        if duration_ms > SLOW_QUERY_THRESHOLD_MS:
            self.query_stats["slow_queries"] += 1
            
            # Record details for slow queries
            query_info = {
                "type": query_type,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
                "details": query_details or {}
            }
            
            self.query_stats["slow_query_details"].append(query_info)
            
            # Keep slow query details list manageable
            if len(self.query_stats["slow_query_details"]) > 100:
                self.query_stats["slow_query_details"] = self.query_stats["slow_query_details"][-100:]
            
            # Log slow query
            logger.warning(
                f"Slow Query Alert: {query_type} took {duration_ms:.2f}ms. "
                f"Details: {query_details}"
            )
            
            # Check if critically slow
            if duration_ms > CRITICAL_QUERY_THRESHOLD_MS:
                self.query_stats["critical_queries"] += 1
                logger.error(
                    f"CRITICAL Query Performance: {query_type} took {duration_ms:.2f}ms. "
                    f"Consider using optimized auth endpoints. Details: {query_details}"
                )
        
        # Update hourly stats
        current_hour = datetime.utcnow().strftime("%Y-%m-%d %H:00:00")
        if current_hour not in self.query_stats["hourly_stats"]:
            self.query_stats["hourly_stats"][current_hour] = {
                "total": 0,
                "slow": 0,
                "avg_ms": 0,
                "max_ms": 0
            }
        
        hourly_data = self.query_stats["hourly_stats"][current_hour]
        hourly_data["total"] += 1
        if duration_ms > SLOW_QUERY_THRESHOLD_MS:
            hourly_data["slow"] += 1
        
        # Update average (rolling)
        hourly_data["avg_ms"] = (
            (hourly_data["avg_ms"] * (hourly_data["total"] - 1) + duration_ms) / 
            hourly_data["total"]
        )
        
        # Update max
        if duration_ms > hourly_data["max_ms"]:
            hourly_data["max_ms"] = duration_ms
        
        # Update endpoint stats if provided
        if query_details and "endpoint" in query_details:
            endpoint = query_details["endpoint"]
            if endpoint not in self.query_stats["endpoint_stats"]:
                self.query_stats["endpoint_stats"][endpoint] = {
                    "total": 0,
                    "slow": 0,
                    "avg_ms": 0,
                    "max_ms": 0
                }
            
            endpoint_data = self.query_stats["endpoint_stats"][endpoint]
            endpoint_data["total"] += 1
            if duration_ms > SLOW_QUERY_THRESHOLD_MS:
                endpoint_data["slow"] += 1
            
            # Update average (rolling)
            endpoint_data["avg_ms"] = (
                (endpoint_data["avg_ms"] * (endpoint_data["total"] - 1) + duration_ms) / 
                endpoint_data["total"]
            )
            
            # Update max
            if duration_ms > endpoint_data["max_ms"]:
                endpoint_data["max_ms"] = duration_ms
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get a summary of database performance stats."""
        # Calculate percentiles if we have data
        percentiles = {}
        if self.query_stats["query_times"]:
            times = sorted(self.query_stats["query_times"])
            percentiles = {
                "p50": times[int(len(times) * 0.5)],
                "p90": times[int(len(times) * 0.9)],
                "p95": times[int(len(times) * 0.95)],
                "p99": times[int(len(times) * 0.99)] if len(times) >= 100 else None
            }
        
        # Calculate average
        avg_time = (
            sum(self.query_stats["query_times"]) / len(self.query_stats["query_times"])
            if self.query_stats["query_times"] else 0
        )
        
        # Return summary
        return {
            "total_queries": self.query_stats["total_queries"],
            "slow_queries": self.query_stats["slow_queries"],
            "critical_queries": self.query_stats["critical_queries"],
            "avg_query_time_ms": avg_time,
            "percentiles": percentiles,
            "last_reset": self.last_reset.isoformat(),
            "recent_slow_queries": self.query_stats["slow_query_details"][-5:],
            "top_slow_endpoints": self._get_top_slow_endpoints(5)
        }
    
    def _get_top_slow_endpoints(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the top slow endpoints."""
        endpoints = list(self.query_stats["endpoint_stats"].items())
        
        # Sort by percentage of slow queries (if total > 0)
        endpoints = [
            {
                "endpoint": endpoint,
                "total": stats["total"],
                "slow": stats["slow"],
                "slow_percentage": (stats["slow"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                "avg_ms": stats["avg_ms"],
                "max_ms": stats["max_ms"]
            }
            for endpoint, stats in endpoints
            if stats["total"] > 0
        ]
        
        # Sort by slow percentage
        endpoints.sort(key=lambda x: x["slow_percentage"], reverse=True)
        
        return endpoints[:limit]
    
    def reset_stats(self) -> None:
        """Reset performance stats."""
        self.query_stats = {
            "total_queries": 0,
            "slow_queries": 0,
            "critical_queries": 0,
            "query_times": [],
            "slow_query_details": [],
            "hourly_stats": {},
            "endpoint_stats": {},
        }
        self.last_reset = datetime.utcnow()


# Global instance
db_performance_monitor = DatabasePerformanceMonitor()


class QueryTimer:
    """
    Context manager to time database queries.
    """
    
    def __init__(self, query_type: str, details: Optional[Dict[str, Any]] = None):
        self.query_type = query_type
        self.details = details or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            db_performance_monitor.record_query_time(
                self.query_type, duration_ms, self.details
            )


def time_query(query_type: str, details: Optional[Dict[str, Any]] = None) -> QueryTimer:
    """Create a query timer context manager."""
    return QueryTimer(query_type, details)
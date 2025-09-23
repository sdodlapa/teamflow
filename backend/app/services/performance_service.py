"""
Performance monitoring and metrics collection service
"""
import time
import psutil
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager

from sqlalchemy import text
from app.core.database import get_db
from app.core.cache import cache, CacheStrategies


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str]
    duration: Optional[float] = None


class MetricsCollector:
    """Collect and store performance metrics"""
    
    def __init__(self):
        self.metrics = deque(maxlen=10000)  # Keep last 10k metrics
        self.request_times = defaultdict(deque)
        self.db_query_times = deque(maxlen=1000)
        self.cache_hit_miss = {"hits": 0, "misses": 0}
        self.active_requests = 0
        self.total_requests = 0
        self.error_count = 0
        self._lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None, duration: float = None):
        """Record a performance metric"""
        with self._lock:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                tags=tags or {},
                duration=duration
            )
            self.metrics.append(metric)
    
    def record_request_time(self, endpoint: str, duration: float):
        """Record API request timing"""
        with self._lock:
            self.request_times[endpoint].append({
                "timestamp": datetime.now(),
                "duration": duration
            })
            if len(self.request_times[endpoint]) > 100:
                self.request_times[endpoint].popleft()
            
            self.total_requests += 1
            self.record_metric("request_duration", duration, {"endpoint": endpoint}, duration)
    
    def record_db_query_time(self, query: str, duration: float):
        """Record database query timing"""
        with self._lock:
            self.db_query_times.append({
                "timestamp": datetime.now(),
                "query": query[:100],  # Truncate long queries
                "duration": duration
            })
            self.record_metric("db_query_duration", duration, {"query_type": "sql"}, duration)
    
    def record_cache_operation(self, operation: str, hit: bool):
        """Record cache hit/miss statistics"""
        with self._lock:
            if hit:
                self.cache_hit_miss["hits"] += 1
            else:
                self.cache_hit_miss["misses"] += 1
            
            self.record_metric("cache_operation", 1, {
                "operation": operation,
                "result": "hit" if hit else "miss"
            })
    
    def increment_active_requests(self):
        """Increment active request counter"""
        with self._lock:
            self.active_requests += 1
    
    def decrement_active_requests(self):
        """Decrement active request counter"""
        with self._lock:
            self.active_requests = max(0, self.active_requests - 1)
    
    def record_error(self, error_type: str):
        """Record application error"""
        with self._lock:
            self.error_count += 1
            self.record_metric("error_count", 1, {"error_type": error_type})
    
    def get_metrics_summary(self, timeframe_minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for specified timeframe"""
        cutoff_time = datetime.now() - timedelta(minutes=timeframe_minutes)
        
        with self._lock:
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            
            # Calculate average response times by endpoint
            endpoint_stats = defaultdict(list)
            for endpoint, times in self.request_times.items():
                recent_times = [t["duration"] for t in times if t["timestamp"] >= cutoff_time]
                if recent_times:
                    endpoint_stats[endpoint] = {
                        "avg_duration": sum(recent_times) / len(recent_times),
                        "min_duration": min(recent_times),
                        "max_duration": max(recent_times),
                        "request_count": len(recent_times),
                        "p95_duration": sorted(recent_times)[int(len(recent_times) * 0.95)] if recent_times else 0
                    }
            
            # Calculate database query stats
            recent_db_queries = [q for q in self.db_query_times if q["timestamp"] >= cutoff_time]
            db_stats = {}
            if recent_db_queries:
                durations = [q["duration"] for q in recent_db_queries]
                db_stats = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "query_count": len(recent_db_queries),
                    "p95_duration": sorted(durations)[int(len(durations) * 0.95)] if durations else 0
                }
            
            # Cache statistics
            total_cache_ops = self.cache_hit_miss["hits"] + self.cache_hit_miss["misses"]
            cache_hit_ratio = (self.cache_hit_miss["hits"] / total_cache_ops * 100) if total_cache_ops > 0 else 0
            
            return {
                "timeframe_minutes": timeframe_minutes,
                "total_metrics": len(recent_metrics),
                "active_requests": self.active_requests,
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "endpoint_stats": dict(endpoint_stats),
                "database_stats": db_stats,
                "cache_stats": {
                    "hit_ratio": round(cache_hit_ratio, 2),
                    "total_hits": self.cache_hit_miss["hits"],
                    "total_misses": self.cache_hit_miss["misses"]
                }
            }


# Global metrics collector
metrics_collector = MetricsCollector()


class PerformanceMonitor:
    """Performance monitoring service"""
    
    def __init__(self):
        self.system_metrics = {}
        self.monitoring_active = False
        self._monitoring_task = None
    
    async def start_monitoring(self):
        """Start background performance monitoring"""
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._collect_system_metrics())
    
    async def stop_monitoring(self):
        """Stop background performance monitoring"""
        self.monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        while self.monitoring_active:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Network I/O
                network = psutil.net_io_counters()
                
                # Process metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()
                
                # Database connection pool metrics
                db_metrics = await self._get_database_metrics()
                
                # Update system metrics
                self.system_metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu": {
                        "percent": cpu_percent,
                        "count": psutil.cpu_count()
                    },
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": (disk.used / disk.total) * 100
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    },
                    "process": {
                        "memory_rss": process_memory.rss,
                        "memory_vms": process_memory.vms,
                        "cpu_percent": process_cpu,
                        "num_threads": process.num_threads()
                    },
                    "database": db_metrics
                }
                
                # Record metrics
                metrics_collector.record_metric("cpu_percent", cpu_percent)
                metrics_collector.record_metric("memory_percent", memory.percent)
                metrics_collector.record_metric("disk_percent", (disk.used / disk.total) * 100)
                metrics_collector.record_metric("process_memory_mb", process_memory.rss / 1024 / 1024)
                
                # Cache system metrics for dashboard
                cache.set("system_metrics", self.system_metrics, ttl=60, namespace="performance")
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(30)
    
    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            async for db in get_db():
                # Query database statistics
                result = await db.execute(text("""
                    SELECT 
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                        (SELECT count(*) FROM pg_stat_activity) as total_connections,
                        (SELECT sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)) 
                         FROM pg_stat_database WHERE datname = current_database()) as cache_hit_ratio
                """))
                row = result.fetchone()
                
                if row:
                    return {
                        "active_connections": row[0] or 0,
                        "total_connections": row[1] or 0,
                        "cache_hit_ratio": round(float(row[2] or 0), 2)
                    }
                break
        except Exception as e:
            print(f"Error getting database metrics: {e}")
        
        return {
            "active_connections": 0,
            "total_connections": 0,
            "cache_hit_ratio": 0
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return self.system_metrics
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        # Get metrics from collector
        app_metrics = metrics_collector.get_metrics_summary()
        
        # Get system metrics
        system_metrics = self.get_system_metrics()
        
        # Get cache statistics
        cache_stats = cache.get_stats()
        
        # Calculate health scores
        health_scores = self._calculate_health_scores(app_metrics, system_metrics)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "application_metrics": app_metrics,
            "system_metrics": system_metrics,
            "cache_statistics": cache_stats,
            "health_scores": health_scores,
            "recommendations": self._generate_recommendations(app_metrics, system_metrics)
        }
    
    def _calculate_health_scores(self, app_metrics: Dict, system_metrics: Dict) -> Dict[str, int]:
        """Calculate health scores (0-100) for different components"""
        scores = {}
        
        # API Health Score
        endpoint_stats = app_metrics.get("endpoint_stats", {})
        if endpoint_stats:
            avg_response_times = [stats["avg_duration"] for stats in endpoint_stats.values()]
            avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
            
            # Score based on response time (< 200ms = 100, > 1000ms = 0)
            api_score = max(0, min(100, 100 - (avg_response_time - 200) / 8))
            scores["api_performance"] = int(api_score)
        else:
            scores["api_performance"] = 100
        
        # Database Health Score
        db_stats = app_metrics.get("database_stats", {})
        if db_stats:
            avg_db_time = db_stats.get("avg_duration", 0)
            # Score based on query time (< 50ms = 100, > 500ms = 0)
            db_score = max(0, min(100, 100 - (avg_db_time - 50) / 4.5))
            scores["database_performance"] = int(db_score)
        else:
            scores["database_performance"] = 100
        
        # Cache Health Score
        cache_stats = app_metrics.get("cache_stats", {})
        hit_ratio = cache_stats.get("hit_ratio", 0)
        scores["cache_performance"] = min(100, int(hit_ratio))
        
        # System Health Score
        if system_metrics:
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            
            # Average of CPU and memory scores
            cpu_score = max(0, 100 - cpu_percent)
            memory_score = max(0, 100 - memory_percent)
            scores["system_performance"] = int((cpu_score + memory_score) / 2)
        else:
            scores["system_performance"] = 100
        
        # Overall Health Score
        scores["overall"] = int(sum(scores.values()) / len(scores))
        
        return scores
    
    def _generate_recommendations(self, app_metrics: Dict, system_metrics: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # API performance recommendations
        endpoint_stats = app_metrics.get("endpoint_stats", {})
        for endpoint, stats in endpoint_stats.items():
            if stats["avg_duration"] > 500:
                recommendations.append(f"Consider optimizing {endpoint} - avg response time: {stats['avg_duration']:.2f}ms")
        
        # Database performance recommendations
        db_stats = app_metrics.get("database_stats", {})
        if db_stats.get("avg_duration", 0) > 100:
            recommendations.append("Database queries are slow - consider adding indexes or query optimization")
        
        # Cache recommendations
        cache_stats = app_metrics.get("cache_stats", {})
        if cache_stats.get("hit_ratio", 0) < 80:
            recommendations.append("Cache hit ratio is low - review caching strategy")
        
        # System recommendations
        if system_metrics:
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            
            if cpu_percent > 80:
                recommendations.append("High CPU usage detected - consider scaling or optimization")
            if memory_percent > 85:
                recommendations.append("High memory usage detected - review memory usage patterns")
        
        return recommendations


# Global performance monitor
performance_monitor = PerformanceMonitor()


@asynccontextmanager
async def performance_tracker(operation_name: str, tags: Dict[str, str] = None):
    """Context manager for tracking operation performance"""
    start_time = time.time()
    metrics_collector.increment_active_requests()
    
    try:
        yield
    except Exception as e:
        metrics_collector.record_error(type(e).__name__)
        raise
    finally:
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        metrics_collector.record_metric(operation_name, duration, tags, duration)
        metrics_collector.decrement_active_requests()


def performance_measure(operation_name: str = None, tags: Dict[str, str] = None):
    """Decorator for measuring function performance"""
    def decorator(func):
        @asynccontextmanager
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            async with performance_tracker(op_name, tags):
                result = await func(*args, **kwargs)
                return result
        
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            metrics_collector.increment_active_requests()
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                metrics_collector.record_error(type(e).__name__)
                raise
            finally:
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                metrics_collector.record_metric(op_name, duration, tags, duration)
                metrics_collector.decrement_active_requests()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator
"""
Database performance optimization utilities
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.services.performance_service import metrics_collector


class DatabaseOptimizer:
    """Database performance optimization utilities"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
        self.connection_pool_stats = {}
    
    async def analyze_slow_queries(self, min_duration_ms: float = 100) -> List[Dict[str, Any]]:
        """Analyze and return slow queries"""
        try:
            from app.core.config import settings
            
            async for db in get_db():
                db_url = str(settings.DATABASE_URL)
                
                if "sqlite" in db_url.lower():
                    # SQLite doesn't have pg_stat_statements
                    # Return empty list or use QueryPerformanceTracker data
                    return []
                
                elif "postgresql" in db_url.lower():
                    # Get slow queries from PostgreSQL
                    result = await db.execute(text("""
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time,
                            rows,
                            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                        FROM pg_stat_statements 
                        WHERE mean_time > :min_duration
                        ORDER BY mean_time DESC 
                        LIMIT 20
                    """), {"min_duration": min_duration_ms})
                    
                    slow_queries = []
                    for row in result:
                        slow_queries.append({
                            "query": row[0][:200] + "..." if len(row[0]) > 200 else row[0],
                            "calls": row[1],
                            "total_time_ms": round(row[2], 2),
                            "mean_time_ms": round(row[3], 2),
                            "avg_rows": row[4],
                            "cache_hit_percent": round(row[5] or 0, 2)
                        })
                    
                    return slow_queries
                
                return []
                break
        except Exception as e:
            print(f"Error analyzing slow queries: {e}")
            return []
    
    async def get_index_recommendations(self) -> List[Dict[str, Any]]:
        """Get index recommendations based on query patterns"""
        try:
            from app.core.config import settings
            
            async for db in get_db():
                db_url = str(settings.DATABASE_URL)
                
                if "sqlite" in db_url.lower():
                    # SQLite doesn't have pg_stat_user_tables
                    # Return generic recommendations
                    return [
                        {
                            "schema": "main",
                            "table": "users",
                            "recommendation": "Consider adding index on frequently queried columns",
                            "reason": "SQLite - manual index analysis recommended"
                        }
                    ]
                
                elif "postgresql" in db_url.lower():
                    # Find missing indexes based on seq scans
                    result = await db.execute(text("""
                        SELECT 
                            schemaname,
                            tablename,
                            seq_scan,
                            seq_tup_read,
                            idx_scan,
                            idx_tup_fetch,
                            n_tup_ins + n_tup_upd + n_tup_del as write_activity
                        FROM pg_stat_user_tables 
                        WHERE seq_scan > 100
                        AND (idx_scan IS NULL OR seq_scan > idx_scan)
                        ORDER BY seq_tup_read DESC
                        LIMIT 10
                    """))
                    
                    recommendations = []
                    for row in result:
                        recommendations.append({
                            "schema": row[0],
                            "table": row[1],
                            "sequential_scans": row[2],
                            "seq_tuples_read": row[3],
                            "index_scans": row[4] or 0,
                            "index_tuples_fetched": row[5] or 0,
                            "write_activity": row[6],
                            "recommendation": f"Consider adding indexes to {row[0]}.{row[1]} - high sequential scan activity"
                        })
                    
                    return recommendations
                
                return []
                break
        except Exception as e:
            print(f"Error getting index recommendations: {e}")
            return []
    
    async def get_table_statistics(self) -> List[Dict[str, Any]]:
        """Get table usage statistics"""
        try:
            from app.core.config import settings
            
            async for db in get_db():
                db_url = str(settings.DATABASE_URL)
                
                if "sqlite" in db_url.lower():
                    # SQLite doesn't have detailed table statistics
                    return [
                        {
                            "schema": "main",
                            "table": "Generic SQLite table stats",
                            "inserts": 0,
                            "updates": 0,
                            "deletes": 0,
                            "live_tuples": 0,
                            "dead_tuples": 0,
                            "recommendation": "SQLite - use ANALYZE command for basic statistics"
                        }
                    ]
                
                elif "postgresql" in db_url.lower():
                    result = await db.execute(text("""
                        SELECT 
                            schemaname,
                            tablename,
                            n_tup_ins as inserts,
                            n_tup_upd as updates,
                            n_tup_del as deletes,
                            n_live_tup as live_tuples,
                            n_dead_tup as dead_tuples,
                            last_vacuum,
                            last_autovacuum,
                            last_analyze,
                            last_autoanalyze
                        FROM pg_stat_user_tables 
                        ORDER BY (n_tup_ins + n_tup_upd + n_tup_del) DESC
                        LIMIT 20
                    """))
                    
                    table_stats = []
                    for row in result:
                        table_stats.append({
                            "schema": row[0],
                            "table": row[1],
                            "inserts": row[2],
                            "updates": row[3],
                            "deletes": row[4],
                            "live_tuples": row[5],
                            "dead_tuples": row[6],
                            "last_vacuum": row[7].isoformat() if row[7] else None,
                            "last_autovacuum": row[8].isoformat() if row[8] else None,
                            "last_analyze": row[9].isoformat() if row[9] else None,
                            "last_autoanalyze": row[10].isoformat() if row[10] else None,
                            "dead_tuple_ratio": round((row[6] / max(row[5], 1)) * 100, 2) if row[6] else 0
                        })
                    
                    return table_stats
                
                return []
                break
        except Exception as e:
            print(f"Error getting table statistics: {e}")
            return []
    
    async def optimize_connection_pool(self) -> Dict[str, Any]:
        """Get connection pool optimization recommendations (database-agnostic)"""
        try:
            async for db in get_db():
                db_url = str(db.bind.url)
                
                if "sqlite" in db_url.lower():
                    # SQLite doesn't have connection pooling stats like PostgreSQL
                    # Return basic stats
                    stats = {
                        "total_connections": 1,  # SQLite typically uses single connection
                        "active_connections": 1,
                        "idle_connections": 0,
                        "idle_in_transaction": 0,
                        "longest_connection_age": 0,
                        "longest_idle_time": 0
                    }
                elif "postgresql" in db_url.lower():
                    # PostgreSQL-specific connection stats
                    result = await db.execute(text("""
                        SELECT 
                            count(*) as total_connections,
                            count(*) FILTER (WHERE state = 'active') as active_connections,
                            count(*) FILTER (WHERE state = 'idle') as idle_connections,
                            count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                            max(extract(epoch from now() - backend_start)) as longest_connection_age,
                            max(extract(epoch from now() - state_change)) as longest_idle_time
                        FROM pg_stat_activity 
                        WHERE backend_type = 'client backend'
                    """))
                    
                    row = result.fetchone()
                    if row:
                        stats = {
                            "total_connections": row[0],
                            "active_connections": row[1],
                        "idle_connections": row[2],
                        "idle_in_transaction": row[3],
                        "longest_connection_age_seconds": round(row[4] or 0, 2),
                        "longest_idle_time_seconds": round(row[5] or 0, 2)
                    }
                    
                    # Generate recommendations
                    recommendations = []
                    
                    if stats["idle_in_transaction"] > 5:
                        recommendations.append("High number of 'idle in transaction' connections - review transaction handling")
                    
                    if stats["longest_idle_time_seconds"] > 300:  # 5 minutes
                        recommendations.append("Long idle connections detected - consider reducing connection timeout")
                    
                    if stats["total_connections"] > 50:
                        recommendations.append("High number of total connections - consider connection pooling optimization")
                    
                    stats["recommendations"] = recommendations
                    return stats
                break
        except Exception as e:
            print(f"Error optimizing connection pool: {e}")
            return {}
    
    async def get_database_size_stats(self) -> Dict[str, Any]:
        """Get database size and growth statistics"""
        try:
            from app.core.config import settings
            
            async for db in get_db():
                db_url = str(settings.DATABASE_URL)
                
                if "sqlite" in db_url.lower():
                    # SQLite - use file system stats
                    import os
                    db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
                    
                    stats = {
                        "database_size": "SQLite file",
                        "database_size_bytes": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
                        "table_sizes": [],
                        "recommendations": ["SQLite database - consider table size monitoring"]
                    }
                    return stats
                
                elif "postgresql" in db_url.lower():
                    # PostgreSQL database size
                    size_result = await db.execute(text("""
                        SELECT 
                            pg_size_pretty(pg_database_size(current_database())) as database_size,
                            pg_database_size(current_database()) as database_size_bytes
                    """))
                    size_row = size_result.fetchone()
                    
                    # Table sizes
                    table_result = await db.execute(text("""
                        SELECT 
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                        LIMIT 10
                    """))
                    
                    table_sizes = []
                    for row in table_result:
                        table_sizes.append({
                            "schema": row[0],
                            "table": row[1],
                            "size": row[2],
                            "size_bytes": row[3]
                        })
                    
                    return {
                        "database_size": size_row[0] if size_row else "Unknown",
                        "database_size_bytes": size_row[1] if size_row else 0,
                        "largest_tables": table_sizes
                    }
                
                # Default fallback
                return {
                    "database_size": "Unknown",
                    "database_size_bytes": 0,
                    "largest_tables": []
                }
                break
        except Exception as e:
            print(f"Error getting database size stats: {e}")
            return {}


class QueryPerformanceTracker:
    """Track and analyze query performance"""
    
    def __init__(self):
        self.query_times = {}
        self.slow_query_threshold = 100  # milliseconds
    
    def track_query(self, query: str, duration_ms: float):
        """Track query execution time"""
        # Normalize query for tracking
        normalized_query = self._normalize_query(query)
        
        if normalized_query not in self.query_times:
            self.query_times[normalized_query] = {
                "count": 0,
                "total_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "slow_executions": 0
            }
        
        stats = self.query_times[normalized_query]
        stats["count"] += 1
        stats["total_time"] += duration_ms
        stats["min_time"] = min(stats["min_time"], duration_ms)
        stats["max_time"] = max(stats["max_time"], duration_ms)
        
        if duration_ms > self.slow_query_threshold:
            stats["slow_executions"] += 1
        
        # Record in metrics collector
        metrics_collector.record_db_query_time(query, duration_ms)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for tracking (remove dynamic values)"""
        import re
        
        # Remove string literals
        query = re.sub(r"'[^']*'", "'?'", query)
        
        # Remove numeric literals
        query = re.sub(r'\b\d+\b', '?', query)
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Truncate very long queries
        if len(query) > 200:
            query = query[:200] + "..."
        
        return query
    
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get queries that frequently run slowly"""
        slow_queries = []
        
        for query, stats in self.query_times.items():
            avg_time = stats["total_time"] / stats["count"]
            slow_ratio = stats["slow_executions"] / stats["count"]
            
            if avg_time > self.slow_query_threshold or slow_ratio > 0.1:
                slow_queries.append({
                    "query": query,
                    "avg_time_ms": round(avg_time, 2),
                    "execution_count": stats["count"],
                    "slow_execution_ratio": round(slow_ratio * 100, 2),
                    "min_time_ms": round(stats["min_time"], 2),
                    "max_time_ms": round(stats["max_time"], 2)
                })
        
        return sorted(slow_queries, key=lambda x: x["avg_time_ms"], reverse=True)
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get overall query statistics"""
        if not self.query_times:
            return {}
        
        total_queries = sum(stats["count"] for stats in self.query_times.values())
        total_time = sum(stats["total_time"] for stats in self.query_times.values())
        slow_queries = sum(stats["slow_executions"] for stats in self.query_times.values())
        
        return {
            "total_queries": total_queries,
            "unique_queries": len(self.query_times),
            "avg_query_time_ms": round(total_time / total_queries, 2) if total_queries > 0 else 0,
            "slow_query_count": slow_queries,
            "slow_query_ratio": round(slow_queries / total_queries * 100, 2) if total_queries > 0 else 0
        }


# Global query tracker
query_tracker = QueryPerformanceTracker()


# SQLAlchemy event listeners for performance tracking
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time"""
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query end time and record performance"""
    if hasattr(context, '_query_start_time'):
        duration = (time.time() - context._query_start_time) * 1000  # Convert to milliseconds
        query_tracker.track_query(statement, duration)


# Database optimization utilities
class DatabaseMaintenanceService:
    """Service for database maintenance and optimization"""
    
    async def analyze_all_tables(self) -> Dict[str, Any]:
        """Run ANALYZE on all tables to update statistics"""
        try:
            async for db in get_db():
                start_time = time.time()
                await db.execute(text("ANALYZE;"))
                duration = (time.time() - start_time) * 1000
                
                return {
                    "status": "success",
                    "duration_ms": round(duration, 2),
                    "message": "Database statistics updated successfully"
                }
                break
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to update database statistics"
            }
    
    async def vacuum_analyze_tables(self) -> Dict[str, Any]:
        """Run VACUUM ANALYZE on tables that need it"""
        try:
            from app.core.config import settings
            
            async for db in get_db():
                db_url = str(settings.DATABASE_URL)
                
                if "sqlite" in db_url.lower():
                    # SQLite uses VACUUM differently
                    try:
                        await db.execute(text("VACUUM;"))
                        await db.execute(text("ANALYZE;"))
                        return {
                            "status": "success",
                            "tables_processed": ["SQLite database"],
                            "message": "SQLite VACUUM and ANALYZE completed"
                        }
                    except Exception as e:
                        return {
                            "status": "error",
                            "error": str(e),
                            "message": "Failed to run SQLite VACUUM/ANALYZE"
                        }
                
                elif "postgresql" in db_url.lower():
                    # Find tables with high dead tuple ratio
                    result = await db.execute(text("""
                        SELECT schemaname, tablename, n_dead_tup, n_live_tup
                        FROM pg_stat_user_tables 
                        WHERE n_dead_tup > 1000 
                        AND (n_dead_tup::float / GREATEST(n_live_tup, 1)) > 0.1
                        ORDER BY (n_dead_tup::float / GREATEST(n_live_tup, 1)) DESC
                    """))
                    
                    tables_vacuumed = []
                    for row in result:
                        table_name = f"{row[0]}.{row[1]}"
                        try:
                            await db.execute(text(f"VACUUM ANALYZE {table_name};"))
                            tables_vacuumed.append(table_name)
                        except Exception as e:
                            print(f"Error vacuuming {table_name}: {e}")
                    
                    return {
                        "status": "success",
                        "tables_vacuumed": tables_vacuumed,
                        "message": f"Vacuumed {len(tables_vacuumed)} tables"
                    }
                
                return {
                    "status": "success",
                    "tables_vacuumed": [],
                    "message": "No database-specific vacuum method available"
                }
                break
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to vacuum tables"
            }


# Global database optimizer
db_optimizer = DatabaseOptimizer()
db_maintenance = DatabaseMaintenanceService()
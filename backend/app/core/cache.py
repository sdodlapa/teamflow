"""
Redis caching system for high-performance data access
"""
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import redis
from redis.exceptions import ConnectionError, TimeoutError
import asyncio
import hashlib
from functools import wraps

from app.core.config import settings


class CacheManager:
    """High-performance Redis cache manager with multi-level strategies"""
    
    def __init__(self):
        self.redis_client = None
        self.local_cache = {}
        self.local_cache_ttl = {}
        self.max_local_cache_size = 1000
        self._connect()
    
    def _connect(self):
        """Connect to Redis with fallback handling"""
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connection established")
        except (ConnectionError, TimeoutError) as e:
            print(f"⚠️ Redis connection failed, using local cache only: {e}")
            self.redis_client = None
    
    def _generate_key(self, key: str, namespace: str = "teamflow") -> str:
        """Generate namespaced cache key"""
        return f"{namespace}:{key}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for caching"""
        try:
            # Try JSON first for simple types
            return json.dumps(data, default=str).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize cached data"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def _clean_local_cache(self):
        """Clean expired local cache entries"""
        current_time = datetime.now()
        expired_keys = [
            key for key, ttl in self.local_cache_ttl.items()
            if ttl < current_time
        ]
        for key in expired_keys:
            self.local_cache.pop(key, None)
            self.local_cache_ttl.pop(key, None)
        
        # Limit cache size
        if len(self.local_cache) > self.max_local_cache_size:
            # Remove oldest entries
            sorted_keys = sorted(
                self.local_cache_ttl.items(),
                key=lambda x: x[1]
            )
            keys_to_remove = sorted_keys[:len(self.local_cache) - self.max_local_cache_size]
            for key, _ in keys_to_remove:
                self.local_cache.pop(key, None)
                self.local_cache_ttl.pop(key, None)
    
    def get(self, key: str, namespace: str = "teamflow") -> Optional[Any]:
        """Get value from cache (local first, then Redis)"""
        cache_key = self._generate_key(key, namespace)
        
        # Check local cache first
        self._clean_local_cache()
        if cache_key in self.local_cache:
            if datetime.now() < self.local_cache_ttl.get(cache_key, datetime.min):
                return self.local_cache[cache_key]
            else:
                self.local_cache.pop(cache_key, None)
                self.local_cache_ttl.pop(cache_key, None)
        
        # Check Redis cache
        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    value = self._deserialize_data(data)
                    # Store in local cache for faster access
                    self.local_cache[cache_key] = value
                    self.local_cache_ttl[cache_key] = datetime.now() + timedelta(minutes=5)
                    return value
            except Exception as e:
                print(f"Redis get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600, namespace: str = "teamflow") -> bool:
        """Set value in cache"""
        cache_key = self._generate_key(key, namespace)
        
        # Store in local cache
        self.local_cache[cache_key] = value
        self.local_cache_ttl[cache_key] = datetime.now() + timedelta(seconds=min(ttl, 300))
        
        # Store in Redis
        if self.redis_client:
            try:
                serialized_data = self._serialize_data(value)
                return self.redis_client.setex(cache_key, ttl, serialized_data)
            except Exception as e:
                print(f"Redis set error: {e}")
                return False
        
        return True
    
    def delete(self, key: str, namespace: str = "teamflow") -> bool:
        """Delete value from cache"""
        cache_key = self._generate_key(key, namespace)
        
        # Remove from local cache
        self.local_cache.pop(cache_key, None)
        self.local_cache_ttl.pop(cache_key, None)
        
        # Remove from Redis
        if self.redis_client:
            try:
                return bool(self.redis_client.delete(cache_key))
            except Exception as e:
                print(f"Redis delete error: {e}")
                return False
        
        return True
    
    def invalidate_pattern(self, pattern: str, namespace: str = "teamflow") -> int:
        """Invalidate all keys matching pattern"""
        cache_pattern = self._generate_key(pattern, namespace)
        deleted_count = 0
        
        # Clear matching local cache entries
        local_keys_to_delete = [
            key for key in self.local_cache.keys()
            if key.startswith(cache_pattern.replace('*', ''))
        ]
        for key in local_keys_to_delete:
            self.local_cache.pop(key, None)
            self.local_cache_ttl.pop(key, None)
            deleted_count += 1
        
        # Clear matching Redis entries
        if self.redis_client:
            try:
                keys = self.redis_client.keys(cache_pattern)
                if keys:
                    deleted_count += self.redis_client.delete(*keys)
            except Exception as e:
                print(f"Redis pattern delete error: {e}")
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "local_cache_size": len(self.local_cache),
            "local_cache_max_size": self.max_local_cache_size,
            "redis_connected": self.redis_client is not None
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_memory_used": info.get('used_memory_human', 'Unknown'),
                    "redis_connected_clients": info.get('connected_clients', 0),
                    "redis_total_commands": info.get('total_commands_processed', 0),
                    "redis_keyspace_hits": info.get('keyspace_hits', 0),
                    "redis_keyspace_misses": info.get('keyspace_misses', 0)
                })
                
                # Calculate hit ratio
                hits = stats.get('redis_keyspace_hits', 0)
                misses = stats.get('redis_keyspace_misses', 0)
                if hits + misses > 0:
                    stats['redis_hit_ratio'] = round(hits / (hits + misses) * 100, 2)
                else:
                    stats['redis_hit_ratio'] = 0
                    
            except Exception as e:
                print(f"Redis stats error: {e}")
        
        return stats


# Global cache instance
cache = CacheManager()


def cached(ttl: int = 3600, namespace: str = "teamflow", key_func=None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Generate key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key, namespace)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl, namespace)
            return result
        
        # Add cache control methods
        wrapper.cache_invalidate = lambda *args, **kwargs: cache.delete(
            key_func(*args, **kwargs) if key_func else 
            hashlib.md5(":".join([func.__name__] + [str(arg) for arg in args] + 
                               [f"{k}={v}" for k, v in sorted(kwargs.items())]).encode()).hexdigest(),
            namespace
        )
        
        return wrapper
    return decorator


class CacheStrategies:
    """Common caching strategies for different data types"""
    
    @staticmethod
    def user_cache_key(user_id: int) -> str:
        """Generate cache key for user data"""
        return f"user:{user_id}"
    
    @staticmethod
    def organization_cache_key(org_id: int) -> str:
        """Generate cache key for organization data"""
        return f"organization:{org_id}"
    
    @staticmethod
    def task_cache_key(task_id: int) -> str:
        """Generate cache key for task data"""
        return f"task:{task_id}"
    
    @staticmethod
    def user_tasks_cache_key(user_id: int) -> str:
        """Generate cache key for user's tasks"""
        return f"user_tasks:{user_id}"
    
    @staticmethod
    def organization_tasks_cache_key(org_id: int) -> str:
        """Generate cache key for organization's tasks"""
        return f"org_tasks:{org_id}"
    
    @staticmethod
    def analytics_cache_key(metric: str, timeframe: str, entity_id: int) -> str:
        """Generate cache key for analytics data"""
        return f"analytics:{metric}:{timeframe}:{entity_id}"
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all user-related cache"""
        patterns = [
            f"user:{user_id}",
            f"user_tasks:{user_id}",
            f"user_*:{user_id}",
        ]
        for pattern in patterns:
            cache.invalidate_pattern(pattern)
    
    @staticmethod
    def invalidate_organization_cache(org_id: int):
        """Invalidate all organization-related cache"""
        patterns = [
            f"organization:{org_id}",
            f"org_tasks:{org_id}",
            f"org_*:{org_id}",
        ]
        for pattern in patterns:
            cache.invalidate_pattern(pattern)
    
    @staticmethod
    def invalidate_task_cache(task_id: int, user_id: int = None, org_id: int = None):
        """Invalidate all task-related cache"""
        patterns = [f"task:{task_id}"]
        
        if user_id:
            patterns.append(f"user_tasks:{user_id}")
        if org_id:
            patterns.append(f"org_tasks:{org_id}")
            
        for pattern in patterns:
            cache.invalidate_pattern(pattern)


# Cache warming functions
class CacheWarmer:
    """Pre-load frequently accessed data into cache"""
    
    @staticmethod
    async def warm_user_data(user_id: int):
        """Pre-load user data into cache"""
        from app.services.user_service import UserService
        user_service = UserService()
        
        # Warm user profile
        user = await user_service.get_user_by_id(user_id)
        if user:
            cache.set(CacheStrategies.user_cache_key(user_id), user, ttl=1800)
    
    @staticmethod
    async def warm_organization_data(org_id: int):
        """Pre-load organization data into cache"""
        from app.services.organization_service import OrganizationService
        org_service = OrganizationService()
        
        # Warm organization profile
        org = await org_service.get_organization(org_id)
        if org:
            cache.set(CacheStrategies.organization_cache_key(org_id), org, ttl=3600)
    
    @staticmethod
    async def warm_dashboard_data(user_id: int):
        """Pre-load dashboard data for user"""
        try:
            # This would warm frequently accessed dashboard data
            # Implementation depends on specific dashboard requirements
            pass
        except Exception as e:
            print(f"Cache warming error: {e}")
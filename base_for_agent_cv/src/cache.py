"""
CZ Career Architect - Caching Layer
Redis-based caching for GPT responses and validation results
"""

import hashlib
import json
from typing import Optional, Any, Callable
from functools import wraps

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import CacheError
from src.metrics import record_cache_hit, record_cache_miss

logger = get_logger(__name__)


class CacheManager:
    """Manage caching operations with Redis."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.settings = get_settings()
        self._redis_client = None
        
        if self.settings.cache_enabled:
            try:
                import redis
                self._redis_client = redis.from_url(
                    self.settings.cache_redis_url,
                    decode_responses=True
                )
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis cache: {e}")
                self.settings.cache_enabled = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if caching is enabled and available."""
        return self.settings.cache_enabled and self._redis_client is not None
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        Generate cache key from data.
        
        Args:
            prefix: Key prefix
            data: Data to hash
            
        Returns:
            Cache key string
        """
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_value = hashlib.sha256(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_value[:16]}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_enabled:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value:
                record_cache_hit()
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            else:
                record_cache_miss()
                logger.debug(f"Cache miss: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: from settings)
            
        Returns:
            True if successful
        """
        if not self.is_enabled:
            return False
        
        try:
            if ttl is None:
                ttl = self.settings.cache_ttl
            
            value_str = json.dumps(value)
            self._redis_client.setex(key, ttl, value_str)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if not self.is_enabled:
            return False
        
        try:
            self._redis_client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "cv:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_enabled:
            return 0
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                deleted = self._redis_client.delete(*keys)
                logger.info(f"Cache cleared: {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance (singleton)."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Cache TTL in seconds
        
    Usage:
        @cached('cv_generation')
        def generate_cv(user_input):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            if not cache.is_enabled:
                return func(*args, **kwargs)
            
            # Generate cache key from function arguments
            cache_data = {
                'args': args,
                'kwargs': kwargs
            }
            cache_key = cache._generate_key(prefix, cache_data)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Returning cached result for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


__all__ = [
    'CacheManager',
    'get_cache_manager',
    'cached',
]

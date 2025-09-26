"""Cache management utilities for TravelSmart."""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib
from loguru import logger


class CacheManager:
    """In-memory cache manager with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() < entry["expires_at"]:
                    logger.debug(f"Cache hit for key: {key}")
                    return entry["data"]
                else:
                    # Expired entry
                    del self._cache[key]
                    logger.debug(f"Cache expired for key: {key}")
            
            logger.debug(f"Cache miss for key: {key}")
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL."""
        async with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = {
                "data": value,
                "expires_at": expires_at,
                "created_at": datetime.now()
            }
            logger.debug(f"Cached key: {key} with TTL: {ttl_seconds}s")
    
    async def delete(self, key: str):
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache key: {key}")
    
    async def clear(self):
        """Clear all cache."""
        async with self._lock:
            self._cache.clear()
            logger.debug("Cleared all cache")
    
    async def cleanup_expired(self):
        """Remove expired entries."""
        async with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now >= entry["expires_at"]
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def cache_key_for_weather(self, location: str, start_date: str, end_date: str) -> str:
        """Generate cache key for weather data."""
        key_data = f"weather:{location}:{start_date}:{end_date}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cache_key_for_insights(self, destination: str, travel_type: str) -> str:
        """Generate cache key for travel insights."""
        key_data = f"insights:{destination}:{travel_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cache_key_for_flights(self, origin: str, destination: str, date: str) -> str:
        """Generate cache key for flight search."""
        key_data = f"flights:{origin}:{destination}:{date}"
        return hashlib.md5(key_data.encode()).hexdigest()


def cached_result(ttl_seconds: int = 3600):
    """Decorator for caching async function results."""
    def decorator(func: Callable):
        cache = {}
        
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {"func": func.__name__, "args": args, "kwargs": kwargs}
            key_string = json.dumps(key_data, sort_keys=True, default=str)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()
            
            # Check cache
            if cache_key in cache:
                entry = cache[cache_key]
                if datetime.now() < entry["expires_at"]:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return entry["data"]
                else:
                    del cache[cache_key]
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = {
                "data": result,
                "expires_at": datetime.now() + timedelta(seconds=ttl_seconds)
            }
            
            logger.debug(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator


# Global cache instance
cache_manager = CacheManager()

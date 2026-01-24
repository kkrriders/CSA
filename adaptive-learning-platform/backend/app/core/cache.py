"""
Redis caching configuration and utilities.
"""
import json
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()


class CacheManager:
    """Manage Redis cache connections and operations."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.CACHE_ENABLED

    async def connect(self):
        """Connect to Redis."""
        if not self.enabled:
            return

        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            print(f"✓ Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}")
            print("Continuing without caching...")
            self.enabled = False

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache delete pattern error: {e}")

        return 0

    async def clear_all(self) -> bool:
        """Clear all cache (use with caution)."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def cached(ttl: int = None, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Usage:
        @cached(ttl=300, key_prefix="analytics")
        async def get_analytics(user_id: str):
            # Expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            key = cache_key(*key_parts)

            # Try to get from cache
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(key, result, ttl)

            return result

        return wrapper
    return decorator


async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user."""
    patterns = [
        f"analytics:*:{user_id}:*",
        f"mastery:*:{user_id}:*",
        f"session:*:{user_id}:*",
        f"readiness:*:{user_id}:*",
    ]

    for pattern in patterns:
        await cache_manager.delete_pattern(pattern)


async def invalidate_document_cache(document_id: str):
    """Invalidate all cache entries for a document."""
    patterns = [
        f"analytics:*:*:{document_id}:*",
        f"readiness:*:{document_id}:*",
        f"questions:*:{document_id}:*",
    ]

    for pattern in patterns:
        await cache_manager.delete_pattern(pattern)


async def invalidate_session_cache(session_id: str):
    """Invalidate all cache entries for a session."""
    await cache_manager.delete_pattern(f"session:*:{session_id}:*")

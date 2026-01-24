"""
Rate limiting middleware using SlowAPI and Redis.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import get_settings

settings = get_settings()

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.REDIS_URL if settings.CACHE_ENABLED else "memory://",
)


# Rate limit decorators for different endpoints
LLM_RATE_LIMIT = "10/minute"  # LLM endpoints (expensive)
ANALYTICS_RATE_LIMIT = "60/minute"  # Analytics endpoints
AUTH_RATE_LIMIT = "20/minute"  # Authentication endpoints
DEFAULT_RATE_LIMIT = "100/minute"  # Default for other endpoints

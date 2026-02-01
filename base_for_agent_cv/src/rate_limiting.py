"""
CZ Career Architect - Rate Limiting
Rate limiting for API endpoints using slowapi
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import RateLimitError

logger = get_logger(__name__)


def create_limiter() -> Limiter:
    """
    Create and configure rate limiter.
    
    Returns:
        Limiter: Configured limiter instance
    """
    settings = get_settings()
    
    if settings.rate_limit_enabled:
        logger.info("Rate limiting enabled")
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{settings.rate_limit_per_minute}/minute"]
        )
    else:
        logger.info("Rate limiting disabled")
        limiter = Limiter(
            key_func=get_remote_address,
            enabled=False
        )
    
    return limiter


def handle_rate_limit_exceeded(request, exc: RateLimitExceeded):
    """
    Handle rate limit exceeded exception.
    
    Args:
        request: Request object
        exc: RateLimitExceeded exception
        
    Returns:
        dict: Error response
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    
    error = RateLimitError(
        limit=get_settings().rate_limit_per_minute,
        window="minute"
    )
    
    return {
        "error": error.to_dict(),
        "retry_after": getattr(exc, 'retry_after', 60)
    }


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    'chat': "10/minute",          # Chat endpoint: 10 requests per minute
    'upload': "5/minute",          # File upload: 5 requests per minute
    'generate': "5/minute",        # Document generation: 5 requests per minute
    'validate': "20/minute",       # Validation: 20 requests per minute
    'health': "60/minute",         # Health check: 60 requests per minute
}


def get_rate_limit(endpoint: str) -> str:
    """
    Get rate limit for specific endpoint.
    
    Args:
        endpoint: Endpoint name
        
    Returns:
        Rate limit string (e.g., "10/minute")
    """
    return RATE_LIMITS.get(endpoint, "10/minute")


__all__ = [
    'create_limiter',
    'handle_rate_limit_exceeded',
    'get_rate_limit',
    'RATE_LIMITS',
]

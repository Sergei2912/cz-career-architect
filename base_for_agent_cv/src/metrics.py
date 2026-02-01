"""
CZ Career Architect - Metrics and Monitoring
Prometheus metrics for monitoring application performance
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
from typing import Callable

from src.logging_config import get_logger

logger = get_logger(__name__)


# Metrics definitions
cv_generated_total = Counter(
    'cv_generated_total',
    'Total number of CVs generated'
)

cover_letter_generated_total = Counter(
    'cover_letter_generated_total',
    'Total number of cover letters generated'
)

validation_errors_total = Counter(
    'validation_errors_total',
    'Total number of validation errors',
    ['error_type']  # GDPR, CSN, ATS
)

api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

model_request_duration_seconds = Histogram(
    'model_request_duration_seconds',
    'GPT model request duration in seconds',
    ['model']
)

file_upload_size_bytes = Histogram(
    'file_upload_size_bytes',
    'File upload size in bytes'
)

active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)


def track_api_request(method: str, endpoint: str):
    """
    Decorator to track API request metrics.
    
    Usage:
        @track_api_request('POST', '/chat')
        def chat_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                logger.error(f"API request failed: {e}")
                raise
            finally:
                duration = time.time() - start_time
                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                api_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator


def track_model_request(model: str):
    """
    Decorator to track GPT model request metrics.
    
    Usage:
        @track_model_request('gpt-5.2')
        def generate_cv():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                model_request_duration_seconds.labels(model=model).observe(duration)
        
        return wrapper
    return decorator


def record_cv_generated():
    """Record that a CV was generated."""
    cv_generated_total.inc()
    logger.debug("CV generation metric recorded")


def record_cover_letter_generated():
    """Record that a cover letter was generated."""
    cover_letter_generated_total.inc()
    logger.debug("Cover letter generation metric recorded")


def record_validation_error(error_type: str):
    """
    Record a validation error.
    
    Args:
        error_type: Type of validation error (GDPR, CSN, ATS)
    """
    validation_errors_total.labels(error_type=error_type).inc()
    logger.debug(f"Validation error metric recorded: {error_type}")


def record_file_upload(size_bytes: int):
    """
    Record file upload size.
    
    Args:
        size_bytes: File size in bytes
    """
    file_upload_size_bytes.observe(size_bytes)
    logger.debug(f"File upload metric recorded: {size_bytes} bytes")


def record_cache_hit():
    """Record a cache hit."""
    cache_hits_total.inc()


def record_cache_miss():
    """Record a cache miss."""
    cache_misses_total.inc()


def get_metrics() -> tuple[bytes, str]:
    """
    Get current metrics in Prometheus format.
    
    Returns:
        tuple: (metrics_bytes, content_type)
    """
    return generate_latest(), CONTENT_TYPE_LATEST


__all__ = [
    'cv_generated_total',
    'cover_letter_generated_total',
    'validation_errors_total',
    'api_requests_total',
    'api_request_duration_seconds',
    'model_request_duration_seconds',
    'file_upload_size_bytes',
    'active_sessions',
    'cache_hits_total',
    'cache_misses_total',
    'track_api_request',
    'track_model_request',
    'record_cv_generated',
    'record_cover_letter_generated',
    'record_validation_error',
    'record_file_upload',
    'record_cache_hit',
    'record_cache_miss',
    'get_metrics',
]

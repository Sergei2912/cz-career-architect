"""
CZ Career Architect - Custom Exceptions
Unified exception hierarchy for better error handling
"""

from typing import List, Optional, Any


class CZCareerArchitectException(Exception):
    """Base exception for all CZ Career Architect errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary format for API responses."""
        result = {
            'error': self.__class__.__name__,
            'message': self.message
        }
        if self.details:
            result['details'] = self.details
        return result


class ConfigurationError(CZCareerArchitectException):
    """Configuration-related errors (missing env vars, invalid settings)."""
    pass


class APIKeyError(ConfigurationError):
    """OpenAI API key missing or invalid."""
    
    def __init__(self, message: str = "OpenAI API key is missing or invalid"):
        super().__init__(message)


class GDPRValidationError(CZCareerArchitectException):
    """GDPR validation failed."""
    
    def __init__(self, findings: List[dict]):
        self.findings = findings
        message = f"GDPR validation failed: {len(findings)} issue(s) found"
        super().__init__(message, details={'findings': findings})


class CSNTypographyError(CZCareerArchitectException):
    """Czech typography (ČSN) validation failed."""
    
    def __init__(self, findings: List[dict]):
        self.findings = findings
        message = f"ČSN typography validation failed: {len(findings)} issue(s) found"
        super().__init__(message, details={'findings': findings})


class ATSValidationError(CZCareerArchitectException):
    """ATS compatibility validation failed."""
    
    def __init__(self, findings: List[dict]):
        self.findings = findings
        message = f"ATS validation failed: {len(findings)} issue(s) found"
        super().__init__(message, details={'findings': findings})


class DocumentGenerationError(CZCareerArchitectException):
    """Document generation failed."""
    
    def __init__(self, message: str = "Failed to generate document", model_error: Optional[str] = None):
        details = {'model_error': model_error} if model_error else None
        super().__init__(message, details)


class FileProcessingError(CZCareerArchitectException):
    """File processing errors (upload, parsing, format issues)."""
    pass


class FileSizeError(FileProcessingError):
    """File size exceeds maximum allowed."""
    
    def __init__(self, size: int, max_size: int):
        message = f"File size ({size} bytes) exceeds maximum allowed ({max_size} bytes)"
        super().__init__(message, details={'size': size, 'max_size': max_size})


class FileFormatError(FileProcessingError):
    """Unsupported file format."""
    
    def __init__(self, extension: str, allowed: List[str]):
        message = f"File format '{extension}' not supported. Allowed: {', '.join(allowed)}"
        super().__init__(message, details={'extension': extension, 'allowed': allowed})


class RateLimitError(CZCareerArchitectException):
    """Rate limit exceeded."""
    
    def __init__(self, limit: int, window: str = "minute"):
        message = f"Rate limit exceeded: {limit} requests per {window}"
        super().__init__(message, details={'limit': limit, 'window': window})


class ModelResponseError(CZCareerArchitectException):
    """GPT model response error."""
    
    def __init__(self, message: str = "Invalid response from AI model", model: Optional[str] = None):
        details = {'model': model} if model else None
        super().__init__(message, details)


class ValidationError(CZCareerArchitectException):
    """Input validation error."""
    
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation error for '{field}': {message}", details={'field': field})


class CacheError(CZCareerArchitectException):
    """Cache operation failed."""
    pass


class DatabaseError(CZCareerArchitectException):
    """Database operation failed."""
    pass


# Exception mapping for HTTP status codes
EXCEPTION_STATUS_CODES = {
    ConfigurationError: 500,
    APIKeyError: 500,
    GDPRValidationError: 400,
    CSNTypographyError: 400,
    ATSValidationError: 400,
    DocumentGenerationError: 500,
    FileProcessingError: 400,
    FileSizeError: 413,
    FileFormatError: 415,
    RateLimitError: 429,
    ModelResponseError: 502,
    ValidationError: 422,
    CacheError: 500,
    DatabaseError: 500,
    CZCareerArchitectException: 500,
}


def get_status_code(exception: Exception) -> int:
    """Get HTTP status code for exception."""
    return EXCEPTION_STATUS_CODES.get(type(exception), 500)

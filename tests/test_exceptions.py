"""
Tests for custom exceptions module
"""

import pytest

from base_for_agent_cv.src.exceptions import (
    CZCareerArchitectException,
    ConfigurationError,
    APIKeyError,
    GDPRValidationError,
    CSNTypographyError,
    ATSValidationError,
    DocumentGenerationError,
    FileProcessingError,
    FileSizeError,
    FileFormatError,
    RateLimitError,
    ModelResponseError,
    ValidationError,
    CacheError,
    DatabaseError,
    get_status_code,
)


class TestBaseException:
    """Test base exception class."""
    
    def test_exception_message(self):
        """Test exception message."""
        exc = CZCareerArchitectException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
    
    def test_exception_with_details(self):
        """Test exception with details."""
        exc = CZCareerArchitectException("Test error", details={'key': 'value'})
        assert exc.details == {'key': 'value'}
    
    def test_exception_to_dict(self):
        """Test exception to_dict method."""
        exc = CZCareerArchitectException("Test error", details={'key': 'value'})
        result = exc.to_dict()
        
        assert result['error'] == 'CZCareerArchitectException'
        assert result['message'] == 'Test error'
        assert result['details'] == {'key': 'value'}


class TestSpecificExceptions:
    """Test specific exception classes."""
    
    def test_api_key_error(self):
        """Test APIKeyError."""
        exc = APIKeyError()
        assert "API key" in str(exc)
        assert isinstance(exc, ConfigurationError)
    
    def test_gdpr_validation_error(self):
        """Test GDPRValidationError."""
        findings = [{'code': 'GDPR_001', 'message': 'Birth date found'}]
        exc = GDPRValidationError(findings)
        
        assert exc.findings == findings
        assert "1 issue" in str(exc)
        assert exc.details['findings'] == findings
    
    def test_csn_typography_error(self):
        """Test CSNTypographyError."""
        findings = [{'code': 'CSN_001', 'message': 'Spacing error'}]
        exc = CSNTypographyError(findings)
        
        assert exc.findings == findings
        assert "1 issue" in str(exc)
    
    def test_ats_validation_error(self):
        """Test ATSValidationError."""
        findings = [{'code': 'ATS_001', 'message': 'Table detected'}]
        exc = ATSValidationError(findings)
        
        assert exc.findings == findings
        assert "1 issue" in str(exc)
    
    def test_document_generation_error(self):
        """Test DocumentGenerationError."""
        exc = DocumentGenerationError(model_error="Model timeout")
        
        assert "generate document" in str(exc)
        assert exc.details['model_error'] == "Model timeout"
    
    def test_file_size_error(self):
        """Test FileSizeError."""
        exc = FileSizeError(size=20000000, max_size=10000000)
        
        assert "20000000" in str(exc)
        assert "10000000" in str(exc)
        assert exc.details['size'] == 20000000
        assert exc.details['max_size'] == 10000000
    
    def test_file_format_error(self):
        """Test FileFormatError."""
        exc = FileFormatError(extension='.exe', allowed=['.pdf', '.docx'])
        
        assert ".exe" in str(exc)
        assert exc.details['extension'] == '.exe'
        assert exc.details['allowed'] == ['.pdf', '.docx']
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        exc = RateLimitError(limit=10, window="minute")
        
        assert "10" in str(exc)
        assert "minute" in str(exc)
    
    def test_model_response_error(self):
        """Test ModelResponseError."""
        exc = ModelResponseError(model="gpt-4")
        
        assert "AI model" in str(exc)
        assert exc.details['model'] == "gpt-4"
    
    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError(field="email", message="Invalid format")
        
        assert "email" in str(exc)
        assert "Invalid format" in str(exc)


class TestStatusCodes:
    """Test HTTP status code mapping."""
    
    def test_get_status_code_for_known_exceptions(self):
        """Test status codes for known exceptions."""
        assert get_status_code(ConfigurationError("test")) == 500
        assert get_status_code(APIKeyError()) == 500
        assert get_status_code(GDPRValidationError([])) == 400
        assert get_status_code(FileSizeError(1000, 500)) == 413
        assert get_status_code(FileFormatError('.exe', [])) == 415
        assert get_status_code(RateLimitError(10)) == 429
        assert get_status_code(ValidationError("field", "msg")) == 422
    
    def test_get_status_code_for_unknown_exception(self):
        """Test status code for unknown exception."""
        assert get_status_code(Exception("test")) == 500
    
    def test_get_status_code_for_base_exception(self):
        """Test status code for base exception."""
        assert get_status_code(CZCareerArchitectException("test")) == 500

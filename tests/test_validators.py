"""
Tests for input validation models
"""

import pytest
from pydantic import ValidationError

from base_for_agent_cv.src.validators import (
    UserProfile,
    WorkExperience,
    Education,
    MedicalCredentials,
    CVGenerationRequest,
    ChatRequest,
    ValidationRequest,
    FileUploadMetadata,
)


class TestUserProfile:
    """Test UserProfile validation."""
    
    def test_valid_profile(self):
        """Test valid user profile."""
        profile = UserProfile(
            name="John Doe",
            email="john.doe@example.com",
            phone="+420 777 123 456",
            city="Praha"
        )
        
        assert profile.name == "John Doe"
        assert profile.city == "Praha"
        assert profile.country == "Česká republika"
    
    def test_invalid_name_with_gdpr_keyword(self):
        """Test that name with GDPR keywords is rejected."""
        with pytest.raises(ValidationError):
            UserProfile(
                name="John Doe born 1990",
                email="john@example.com",
                phone="+420 777 123 456",
                city="Praha"
            )
    
    def test_invalid_phone_format(self):
        """Test invalid phone format."""
        with pytest.raises(ValidationError):
            UserProfile(
                name="John Doe",
                email="john@example.com",
                phone="123456789",  # Invalid format
                city="Praha"
            )
    
    def test_invalid_email(self):
        """Test invalid email."""
        with pytest.raises(ValidationError):
            UserProfile(
                name="John Doe",
                email="not-an-email",
                phone="+420 777 123 456",
                city="Praha"
            )


class TestWorkExperience:
    """Test WorkExperience validation."""
    
    def test_valid_experience(self):
        """Test valid work experience."""
        exp = WorkExperience(
            position="Software Engineer",
            company="Tech Corp",
            start_date="2020-01",
            end_date="2023-12"
        )
        
        assert exp.position == "Software Engineer"
        assert exp.start_date == "2020-01"
    
    def test_invalid_date_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            WorkExperience(
                position="Software Engineer",
                company="Tech Corp",
                start_date="2020/01/15",  # Wrong format
                end_date="2023-12"
            )
    
    def test_current_position(self):
        """Test current position with no end date."""
        exp = WorkExperience(
            position="Software Engineer",
            company="Tech Corp",
            start_date="2020-01",
            end_date=None
        )
        
        assert exp.end_date is None


class TestEducation:
    """Test Education validation."""
    
    def test_valid_education(self):
        """Test valid education."""
        edu = Education(
            degree="Bachelor of Science",
            institution="Charles University",
            year=2020,
            field="Computer Science"
        )
        
        assert edu.degree == "Bachelor of Science"
        assert edu.year == 2020
    
    def test_invalid_year(self):
        """Test invalid year."""
        with pytest.raises(ValidationError):
            Education(
                degree="Bachelor",
                institution="University",
                year=1900  # Too old
            )


class TestMedicalCredentials:
    """Test MedicalCredentials validation."""
    
    def test_valid_credentials(self):
        """Test valid medical credentials."""
        cred = MedicalCredentials(
            nostrifikace_status="completed",
            approbace_status="full"
        )
        
        assert cred.nostrifikace_status == "completed"
        assert cred.approbace_status == "full"
    
    def test_russian_status(self):
        """Test Russian language status."""
        cred = MedicalCredentials(
            nostrifikace_status="завершена",
            approbace_status="полная"
        )
        
        assert cred.nostrifikace_status == "завершена"
    
    def test_invalid_status(self):
        """Test invalid status."""
        with pytest.raises(ValidationError):
            MedicalCredentials(
                nostrifikace_status="invalid_status",
                approbace_status="full"
            )


class TestChatRequest:
    """Test ChatRequest validation."""
    
    def test_valid_request(self):
        """Test valid chat request."""
        req = ChatRequest(
            message="Hello, create a CV for me",
            session_id="session123"
        )
        
        assert req.message == "Hello, create a CV for me"
        assert req.session_id == "session123"
    
    def test_message_with_script(self):
        """Test message with script tags is rejected."""
        with pytest.raises(ValidationError):
            ChatRequest(
                message="<script>alert('xss')</script>"
            )
    
    def test_message_with_sql_injection(self):
        """Test message with SQL injection is rejected."""
        with pytest.raises(ValidationError):
            ChatRequest(
                message="test'; DROP TABLE users; --"
            )
    
    def test_empty_message(self):
        """Test empty message is rejected."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")


class TestValidationRequest:
    """Test ValidationRequest validation."""
    
    def test_valid_request(self):
        """Test valid validation request."""
        req = ValidationRequest(
            text="Sample text to validate",
            validation_types=["gdpr", "csn"]
        )
        
        assert req.text == "Sample text to validate"
        assert set(req.validation_types) == {"gdpr", "csn"}
    
    def test_default_validation_types(self):
        """Test default validation types."""
        req = ValidationRequest(text="Sample text")
        
        assert set(req.validation_types) == {"gdpr", "csn", "ats"}
    
    def test_invalid_validation_type(self):
        """Test invalid validation type."""
        with pytest.raises(ValidationError):
            ValidationRequest(
                text="Sample text",
                validation_types=["invalid_type"]
            )


class TestFileUploadMetadata:
    """Test FileUploadMetadata validation."""
    
    def test_valid_metadata(self):
        """Test valid file metadata."""
        meta = FileUploadMetadata(
            filename="document.pdf",
            content_type="application/pdf",
            size=1024000
        )
        
        assert meta.filename == "document.pdf"
        assert meta.size == 1024000
    
    def test_path_traversal_rejected(self):
        """Test path traversal in filename is rejected."""
        with pytest.raises(ValidationError):
            FileUploadMetadata(
                filename="../../../etc/passwd",
                content_type="text/plain",
                size=1024
            )
    
    def test_invalid_extension(self):
        """Test invalid file extension is rejected."""
        with pytest.raises(ValidationError):
            FileUploadMetadata(
                filename="malware.exe",
                content_type="application/x-executable",
                size=1024
            )
    
    def test_zero_size(self):
        """Test zero size is rejected."""
        with pytest.raises(ValidationError):
            FileUploadMetadata(
                filename="document.pdf",
                content_type="application/pdf",
                size=0
            )

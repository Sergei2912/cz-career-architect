"""
CZ Career Architect - Input Validation Models
Enhanced Pydantic models for input validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
import re

from src.logging_config import get_logger

logger = get_logger(__name__)


class UserProfile(BaseModel):
    """User profile input validation."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    city: str = Field(..., min_length=2, max_length=50, description="City")
    country: str = Field(default="Česká republika", description="Country")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name doesn't contain GDPR-sensitive keywords."""
        gdpr_keywords = [
            'born', 'age', 'married', 'children', 'single',
            'divorced', 'widow', 'husband', 'wife'
        ]
        v_lower = v.lower()
        for keyword in gdpr_keywords:
            if keyword in v_lower:
                logger.warning(f"Name contains GDPR-sensitive keyword: {keyword}")
                raise ValueError(f"Name should not contain: {keyword}")
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate Czech phone number format."""
        # Czech phone: +420 XXX XXX XXX or variations
        pattern = r'^\+420\s?\d{3}\s?\d{3}\s?\d{3}$'
        if not re.match(pattern, v):
            raise ValueError("Phone must be in Czech format: +420 XXX XXX XXX")
        return v


class WorkExperience(BaseModel):
    """Work experience validation."""
    
    position: str = Field(..., min_length=2, max_length=100, description="Job position")
    company: str = Field(..., min_length=2, max_length=100, description="Company name")
    start_date: str = Field(..., description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM) or None if current")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate date format YYYY-MM."""
        if v is None:
            return v
        pattern = r'^\d{4}-\d{2}$'
        if not re.match(pattern, v):
            raise ValueError("Date must be in format: YYYY-MM (e.g., 2023-01)")
        return v


class Education(BaseModel):
    """Education validation."""
    
    degree: str = Field(..., min_length=2, max_length=100, description="Degree or qualification")
    institution: str = Field(..., min_length=2, max_length=150, description="Educational institution")
    year: int = Field(..., ge=1950, le=2030, description="Graduation year")
    field: Optional[str] = Field(None, max_length=100, description="Field of study")


class MedicalCredentials(BaseModel):
    """Medical credentials validation."""
    
    nostrifikace_status: str = Field(..., description="Nostrifikace status")
    approbace_status: str = Field(..., description="Approbace status")
    chamber_registration: Optional[str] = Field(None, description="Medical chamber registration")
    
    @validator('nostrifikace_status')
    def validate_nostrifikace(cls, v):
        """Validate nostrifikace status."""
        valid_statuses = [
            'completed', 'in_progress', 'not_started',
            'завершена', 'в процессе', 'не начата'
        ]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid nostrifikace status. Must be one of: {valid_statuses}")
        return v
    
    @validator('approbace_status')
    def validate_approbace(cls, v):
        """Validate approbace status."""
        valid_statuses = [
            'full', 'temporary', 'in_progress', 'not_started',
            'полная', 'временная', 'в процессе', 'не начата'
        ]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid approbace status. Must be one of: {valid_statuses}")
        return v


class CVGenerationRequest(BaseModel):
    """CV generation request validation."""
    
    profile: UserProfile
    work_experience: List[WorkExperience] = Field(..., min_items=1, description="Work experience list")
    education: List[Education] = Field(..., min_items=1, description="Education list")
    medical_credentials: Optional[MedicalCredentials] = Field(None, description="Medical credentials")
    skills: Optional[List[str]] = Field(None, description="Skills list")
    languages: Optional[List[str]] = Field(None, description="Languages list")
    target_position: Optional[str] = Field(None, description="Target position")
    target_company: Optional[str] = Field(None, description="Target company")


class ChatRequest(BaseModel):
    """Chat request validation."""
    
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message doesn't contain injection attempts."""
        # Basic SQL/XSS injection prevention
        dangerous_patterns = [
            r'<script', r'javascript:', r'onerror=',
            r'DROP\s+TABLE', r'DELETE\s+FROM'
        ]
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, v_lower, re.IGNORECASE):
                logger.warning(f"Message contains dangerous pattern: {pattern}")
                raise ValueError("Message contains prohibited content")
        return v


class ValidationRequest(BaseModel):
    """Validation request."""
    
    text: str = Field(..., min_length=1, max_length=50000, description="Text to validate")
    validation_types: List[str] = Field(
        default=['gdpr', 'csn', 'ats'],
        description="Types of validation to perform"
    )
    
    @validator('validation_types')
    def validate_types(cls, v):
        """Validate validation types."""
        valid_types = {'gdpr', 'csn', 'ats'}
        for vtype in v:
            if vtype.lower() not in valid_types:
                raise ValueError(f"Invalid validation type: {vtype}. Must be one of: {valid_types}")
        return [vt.lower() for vt in v]


class FileUploadMetadata(BaseModel):
    """File upload metadata validation."""
    
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., gt=0, description="File size in bytes")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename."""
        # Check for path traversal attempts
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("Invalid filename: path traversal detected")
        
        # Check extension
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}
        extension = v[v.rfind('.'):].lower() if '.' in v else ''
        if extension not in allowed_extensions:
            raise ValueError(f"File extension {extension} not allowed. Allowed: {allowed_extensions}")
        
        return v


__all__ = [
    'UserProfile',
    'WorkExperience',
    'Education',
    'MedicalCredentials',
    'CVGenerationRequest',
    'ChatRequest',
    'ValidationRequest',
    'FileUploadMetadata',
]

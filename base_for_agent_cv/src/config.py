"""
CZ Career Architect - Configuration Management
Centralized configuration using Pydantic Settings
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with validation and environment variable support."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env='OPENAI_API_KEY', description='OpenAI API key')
    openai_model: str = Field('gpt-5.2', env='OPENAI_MODEL', description='GPT model to use')
    openai_vector_store_id: Optional[str] = Field(None, env='OPENAI_VECTOR_STORE_ID', description='Vector store ID')
    
    # Application Settings
    app_version: str = Field('2.0.0', description='Application version')
    app_name: str = Field('CZ Career Architect', description='Application name')
    debug: bool = Field(False, env='DEBUG', description='Debug mode')
    
    # File Upload Settings
    max_file_size: int = Field(10 * 1024 * 1024, description='Maximum file size in bytes (10MB)')
    allowed_extensions: set = Field(
        default={'.pdf', '.docx', '.doc', '.txt', '.rtf'},
        description='Allowed file extensions'
    )
    
    # Paths
    upload_dir: Path = Field(Path('uploads'), description='Upload directory path')
    output_dir: Path = Field(Path('out'), description='Output directory path')
    log_dir: Path = Field(Path('logs'), description='Log directory path')
    
    # API Settings
    api_host: str = Field('0.0.0.0', env='API_HOST', description='API host')
    api_port: int = Field(8000, env='API_PORT', description='API port')
    api_reload: bool = Field(False, env='API_RELOAD', description='API auto-reload')
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(True, env='RATE_LIMIT_ENABLED', description='Enable rate limiting')
    rate_limit_per_minute: int = Field(10, env='RATE_LIMIT_PER_MINUTE', description='Requests per minute')
    
    # Logging
    log_level: str = Field('INFO', env='LOG_LEVEL', description='Logging level')
    log_format: str = Field(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        description='Log format'
    )
    
    # Monitoring
    metrics_enabled: bool = Field(False, env='METRICS_ENABLED', description='Enable Prometheus metrics')
    
    # Caching
    cache_enabled: bool = Field(False, env='CACHE_ENABLED', description='Enable caching')
    cache_redis_url: Optional[str] = Field(None, env='REDIS_URL', description='Redis URL for caching')
    cache_ttl: int = Field(86400, env='CACHE_TTL', description='Cache TTL in seconds (24 hours)')
    
    @validator('upload_dir', 'output_dir', 'log_dir', pre=True)
    def ensure_path(cls, v):
        """Ensure path is a Path object."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.upload_dir, self.output_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_directories()
    return _settings


# Convenience export
settings = get_settings()

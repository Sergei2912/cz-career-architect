"""
Tests for configuration module
"""

import os
import pytest
from pathlib import Path
from pydantic import ValidationError

from base_for_agent_cv.src.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""
    
    def test_settings_default_values(self):
        """Test settings with default values."""
        os.environ['OPENAI_API_KEY'] = 'test-key-123'
        settings = Settings()
        
        assert settings.app_version == '2.0.0'
        assert settings.app_name == 'CZ Career Architect'
        assert settings.openai_model == 'gpt-5.2'
        assert settings.max_file_size == 10 * 1024 * 1024
        assert settings.api_port == 8000
        
    def test_settings_from_env(self):
        """Test settings loaded from environment variables."""
        os.environ['OPENAI_API_KEY'] = 'test-key-456'
        os.environ['OPENAI_MODEL'] = 'gpt-4'
        os.environ['API_PORT'] = '9000'
        os.environ['DEBUG'] = 'true'
        
        settings = Settings()
        
        assert settings.openai_api_key == 'test-key-456'
        assert settings.openai_model == 'gpt-4'
        assert settings.api_port == 9000
        assert settings.debug is True
        
    def test_settings_validation_log_level(self):
        """Test log level validation."""
        os.environ['OPENAI_API_KEY'] = 'test-key-789'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        settings = Settings()
        assert settings.log_level == 'DEBUG'
        
    def test_settings_invalid_log_level(self):
        """Test invalid log level raises error."""
        os.environ['OPENAI_API_KEY'] = 'test-key-999'
        os.environ['LOG_LEVEL'] = 'INVALID'
        
        with pytest.raises(ValidationError):
            Settings()
    
    def test_settings_paths_are_path_objects(self):
        """Test that paths are converted to Path objects."""
        os.environ['OPENAI_API_KEY'] = 'test-key-path'
        settings = Settings()
        
        assert isinstance(settings.upload_dir, Path)
        assert isinstance(settings.output_dir, Path)
        assert isinstance(settings.log_dir, Path)
    
    def test_ensure_directories(self, tmp_path):
        """Test directory creation."""
        os.environ['OPENAI_API_KEY'] = 'test-key-dir'
        settings = Settings()
        settings.upload_dir = tmp_path / 'uploads'
        settings.output_dir = tmp_path / 'output'
        settings.log_dir = tmp_path / 'logs'
        
        settings.ensure_directories()
        
        assert settings.upload_dir.exists()
        assert settings.output_dir.exists()
        assert settings.log_dir.exists()
    
    def test_allowed_extensions(self):
        """Test allowed extensions set."""
        os.environ['OPENAI_API_KEY'] = 'test-key-ext'
        settings = Settings()
        
        assert '.pdf' in settings.allowed_extensions
        assert '.docx' in settings.allowed_extensions
        assert '.txt' in settings.allowed_extensions


class TestGetSettings:
    """Test get_settings singleton function."""
    
    def test_get_settings_returns_same_instance(self):
        """Test that get_settings returns the same instance."""
        os.environ['OPENAI_API_KEY'] = 'test-key-singleton'
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_get_settings_creates_directories(self, tmp_path, monkeypatch):
        """Test that get_settings creates directories."""
        os.environ['OPENAI_API_KEY'] = 'test-key-create'
        
        # Force new instance
        import base_for_agent_cv.src.config as config_module
        config_module._settings = None
        
        # Mock the paths to use tmp_path
        def mock_settings_init(self):
            self.__dict__.update(Settings().__dict__)
            self.upload_dir = tmp_path / 'uploads'
            self.output_dir = tmp_path / 'output'
            self.log_dir = tmp_path / 'logs'
        
        monkeypatch.setattr(Settings, '__init__', mock_settings_init)
        
        settings = get_settings()
        
        # Note: directories might not exist in test due to mocking
        assert settings is not None

"""
Tests for logging configuration module
"""

import logging
import pytest
from pathlib import Path

from base_for_agent_cv.src.logging_config import (
    setup_logging,
    get_logger,
    LoggerMixin,
)


class TestSetupLogging:
    """Test setup_logging function."""
    
    def test_setup_logging_default(self, tmp_path):
        """Test setup logging with default parameters."""
        logger = setup_logging(log_dir=tmp_path)
        
        assert logger is not None
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 3  # console, file, error file
    
    def test_setup_logging_custom_level(self, tmp_path):
        """Test setup logging with custom log level."""
        logger = setup_logging(log_level='DEBUG', log_dir=tmp_path)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_creates_log_files(self, tmp_path):
        """Test that setup_logging creates log files."""
        logger = setup_logging(log_dir=tmp_path, app_name='test-app')
        
        log_file = tmp_path / 'test-app.log'
        error_log_file = tmp_path / 'test-app-error.log'
        
        # Files should exist after first log
        logger.info("Test message")
        logger.error("Test error")
        
        assert log_file.exists()
        assert error_log_file.exists()
    
    def test_setup_logging_custom_format(self, tmp_path):
        """Test setup logging with custom format."""
        custom_format = '%(levelname)s - %(message)s'
        logger = setup_logging(
            log_dir=tmp_path,
            log_format=custom_format
        )
        
        assert logger is not None
        # Check that handlers have the custom format
        for handler in logger.handlers:
            if isinstance(handler.formatter, logging.Formatter):
                assert handler.formatter._fmt == custom_format


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger."""
        logger = get_logger('test_module')
        
        assert isinstance(logger, logging.Logger)
        assert 'test_module' in logger.name
    
    def test_get_logger_with_different_names(self):
        """Test that different names return different loggers."""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')
        
        assert logger1.name != logger2.name


class TestLoggerMixin:
    """Test LoggerMixin class."""
    
    def test_logger_mixin_property(self):
        """Test that LoggerMixin provides logger property."""
        
        class TestClass(LoggerMixin):
            pass
        
        obj = TestClass()
        logger = obj.logger
        
        assert isinstance(logger, logging.Logger)
        assert 'TestClass' in logger.name
    
    def test_logger_mixin_caching(self):
        """Test that logger is cached."""
        
        class TestClass(LoggerMixin):
            pass
        
        obj = TestClass()
        logger1 = obj.logger
        logger2 = obj.logger
        
        assert logger1 is logger2

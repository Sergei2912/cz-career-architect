"""
CZ Career Architect - Logging Configuration
Structured logging system with file and console output
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_level: str = 'INFO',
    log_dir: Optional[Path] = None,
    log_format: Optional[str] = None,
    app_name: str = 'cz-career-architect'
) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_format: Custom log format string
        app_name: Application name for logger
        
    Returns:
        Configured logger instance
    """
    # Set default log directory
    if log_dir is None:
        log_dir = Path('logs')
    
    # Ensure log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set default format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    log_file = log_dir / f'{app_name}.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    error_log_file = log_dir / f'{app_name}-error.log'
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logging initialized: level={log_level}, log_dir={log_dir}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'cz-career-architect.{name}')


# Module-level logger for this file
logger = get_logger(__name__)


class LoggerMixin:
    """Mixin class to add logging capability to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for the class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger

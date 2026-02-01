"""
CZ Career Architect - Utility Functions
Helper functions for file handling and environment setup
"""

import os
from pathlib import Path
from typing import Optional

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import ConfigurationError, FileProcessingError

logger = get_logger(__name__)


def load_env_file(env_path: Optional[Path] = None):
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file (defaults to .env in root)
    """
    logger.info("Loading environment variables")
    
    if env_path is None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        env_path = root_dir / ".env"
    
    if not isinstance(env_path, Path):
        env_path = Path(env_path)
    
    if env_path.exists():
        logger.info(f"Loading .env from: {env_path}")
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key] = val
        logger.info("Environment variables loaded successfully")
    else:
        logger.warning(f".env file not found at: {env_path}")


def ensure_output_dir(output_dir: Optional[Path] = None) -> Path:
    """
    Ensure output directory exists.
    
    Args:
        output_dir: Path to output directory (defaults to settings.output_dir)
        
    Returns:
        Path: Output directory path
        
    Raises:
        FileProcessingError: If directory cannot be created
    """
    try:
        if output_dir is None:
            settings = get_settings()
            output_dir = settings.output_dir
        
        if not isinstance(output_dir, Path):
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True, parents=True)
        logger.debug(f"Output directory ensured: {output_dir}")
        return output_dir
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        raise FileProcessingError(f"Cannot create output directory: {e}")


def save_output(content: str, output_path: Path, encoding: str = "utf-8"):
    """
    Save content to file.
    
    Args:
        content: Content to save
        output_path: Path to output file
        encoding: File encoding
        
    Raises:
        FileProcessingError: If file cannot be saved
    """
    try:
        if not isinstance(output_path, Path):
            output_path = Path(output_path)
        
        # Ensure parent directory exists
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        output_path.write_text(content, encoding=encoding)
        logger.info(f"Content saved to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save content to {output_path}: {e}")
        raise FileProcessingError(f"Cannot save file: {e}")


def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
    """
    Validate file size against maximum allowed.
    
    Args:
        file_size: File size in bytes
        max_size: Maximum size in bytes (defaults to settings.max_file_size)
        
    Returns:
        bool: True if size is valid
        
    Raises:
        FileSizeError: If file is too large
    """
    if max_size is None:
        settings = get_settings()
        max_size = settings.max_file_size
    
    if file_size > max_size:
        from src.exceptions import FileSizeError
        logger.warning(f"File size {file_size} exceeds maximum {max_size}")
        raise FileSizeError(file_size, max_size)
    
    logger.debug(f"File size {file_size} is valid (max: {max_size})")
    return True


def validate_file_extension(filename: str, allowed: Optional[set] = None) -> bool:
    """
    Validate file extension against allowed extensions.
    
    Args:
        filename: File name to validate
        allowed: Set of allowed extensions (defaults to settings.allowed_extensions)
        
    Returns:
        bool: True if extension is valid
        
    Raises:
        FileFormatError: If extension is not allowed
    """
    if allowed is None:
        settings = get_settings()
        allowed = settings.allowed_extensions
    
    extension = Path(filename).suffix.lower()
    
    if extension not in allowed:
        from src.exceptions import FileFormatError
        logger.warning(f"File extension {extension} not allowed: {allowed}")
        raise FileFormatError(extension, list(allowed))
    
    logger.debug(f"File extension {extension} is valid")
    return True


__all__ = [
    "load_env_file",
    "ensure_output_dir",
    "save_output",
    "validate_file_size",
    "validate_file_extension",
]

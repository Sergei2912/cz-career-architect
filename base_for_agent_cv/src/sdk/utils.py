"""
CZ Career Architect - Utility Functions
Helper functions for file handling and environment setup
"""

import os
from pathlib import Path


def load_env_file(env_path=None):
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file (defaults to .env in root)
    """
    if env_path is None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        env_path = root_dir / ".env"
    
    if not isinstance(env_path, Path):
        env_path = Path(env_path)
    
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key] = val


def ensure_output_dir(output_dir):
    """
    Ensure output directory exists.
    
    Args:
        output_dir: Path to output directory
        
    Returns:
        Path: Output directory path
    """
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    return output_dir


def save_output(content, output_path, encoding="utf-8"):
    """
    Save content to file.
    
    Args:
        content: Content to save
        output_path: Path to output file
        encoding: File encoding
    """
    if not isinstance(output_path, Path):
        output_path = Path(output_path)
    
    output_path.write_text(content, encoding=encoding)


__all__ = [
    "load_env_file",
    "ensure_output_dir",
    "save_output",
]

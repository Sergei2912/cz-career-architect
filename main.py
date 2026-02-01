#!/usr/bin/env python3
"""
CZ Career Architect - Main entry point wrapper
Allows running from repository root
"""

import sys
from pathlib import Path

# Add base_for_agent_cv to path
base_dir = Path(__file__).resolve().parent / "base_for_agent_cv"
sys.path.insert(0, str(base_dir))

# Run main module
from src.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

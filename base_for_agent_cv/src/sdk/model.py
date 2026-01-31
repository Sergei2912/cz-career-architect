"""
CZ Career Architect - Model Interactions
Handles GPT model interactions and agent creation
"""

import os
import sys
from pathlib import Path

# Add packages to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

from agents import Agent, ModelSettings, Runner


def create_agent(name, instructions, model=None):
    """
    Create an agent instance.
    
    Args:
        name: Name of the agent
        instructions: System instructions for the agent
        model: Model to use (defaults to OPENAI_MODEL env var)
        
    Returns:
        Agent: Configured agent instance
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    return Agent(
        name=name,
        instructions=instructions,
        model=model,
        model_settings=ModelSettings(),
    )


def get_runner():
    """
    Get the Runner class for executing agents.
    
    Returns:
        Runner: Runner class
    """
    return Runner


def get_model_name():
    """
    Get the configured model name.
    
    Returns:
        str: Model name from environment
    """
    return os.getenv("OPENAI_MODEL", "gpt-4")


__all__ = [
    "create_agent",
    "get_runner",
    "get_model_name",
    "Agent",
    "ModelSettings",
    "Runner",
]

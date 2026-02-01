"""
CZ Career Architect - Model Interactions
Handles GPT model interactions and agent creation
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add packages to path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "packages"))

from agents import Agent, ModelSettings, Runner

from src.logging_config import get_logger
from src.config import get_settings
from src.exceptions import APIKeyError, ModelResponseError, ConfigurationError

logger = get_logger(__name__)


def create_agent(name: str, instructions: str, model: Optional[str] = None) -> Agent:
    """
    Create an agent instance.
    
    Args:
        name: Name of the agent
        instructions: System instructions for the agent
        model: Model to use (defaults to settings.openai_model)
        
    Returns:
        Agent: Configured agent instance
        
    Raises:
        APIKeyError: If OpenAI API key is not configured
        ConfigurationError: If configuration is invalid
    """
    logger.info(f"Creating agent: {name}")
    
    try:
        settings = get_settings()
        
        # Validate API key
        api_key = settings.openai_api_key
        if not api_key or api_key == "":
            logger.error("OpenAI API key not configured")
            raise APIKeyError("OpenAI API key is not configured. Please set OPENAI_API_KEY in .env")
        
        # Use provided model or default from settings
        if model is None:
            model = settings.openai_model
            logger.debug(f"Using default model: {model}")
        else:
            logger.debug(f"Using specified model: {model}")
        
        # Create agent
        agent = Agent(
            name=name,
            instructions=instructions,
            model=model,
            model_settings=ModelSettings(),
        )
        
        logger.info(f"Agent created successfully: {name} with model {model}")
        return agent
        
    except APIKeyError:
        raise
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise ConfigurationError(f"Failed to create agent: {e}")


def get_runner() -> type:
    """
    Get the Runner class for executing agents.
    
    Returns:
        Runner: Runner class
    """
    logger.debug("Getting Runner class")
    return Runner


def get_model_name() -> str:
    """
    Get the configured model name.
    
    Returns:
        str: Model name from settings
    """
    try:
        settings = get_settings()
        model_name = settings.openai_model
        logger.debug(f"Model name: {model_name}")
        return model_name
    except Exception as e:
        logger.error(f"Failed to get model name: {e}")
        return "gpt-4"  # Fallback default


def validate_model_response(response: any) -> bool:
    """
    Validate model response.
    
    Args:
        response: Response from the model
        
    Returns:
        bool: True if response is valid
        
    Raises:
        ModelResponseError: If response is invalid
    """
    if response is None:
        logger.error("Model response is None")
        raise ModelResponseError("Model returned empty response")
    
    if not hasattr(response, 'final_output'):
        logger.error("Model response missing final_output attribute")
        raise ModelResponseError("Invalid model response structure")
    
    logger.debug("Model response validated successfully")
    return True


__all__ = [
    "create_agent",
    "get_runner",
    "get_model_name",
    "validate_model_response",
    "Agent",
    "ModelSettings",
    "Runner",
]

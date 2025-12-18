"""Base agent configuration for AI Chatbot feature."""

from openai import OpenAI
from typing import Optional, List, Dict, Any


class BaseAgentConfig:
    """Base configuration for agents in the system."""

    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        instructions: Optional[str] = None
    ):
        """
        Initialize base agent configuration.

        Args:
            client: OpenAI client instance
            model: Model to use for the agent
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            instructions: System instructions for the agent
        """
        self.client = client
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.instructions = instructions or "You are a helpful assistant."

    def get_config(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary."""
        config = {
            "model": self.model,
            "temperature": self.temperature,
        }

        if self.max_tokens:
            config["max_tokens"] = self.max_tokens

        return config
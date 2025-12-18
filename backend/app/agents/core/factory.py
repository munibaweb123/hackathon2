"""Model factory for OpenAI Agents SDK integration."""

import os
from openai import OpenAI, AzureOpenAI
from typing import Union

from ...core.config import settings


def create_model():
    """Return a model object compatible with the Agents SDK.

    - Uses LLM_PROVIDER to decide provider.
    - Uses provider-specific env vars for keys and defaults.
    - Returns a model usable in Agent(model=...).
    """
    llm_provider = settings.LLM_PROVIDER

    if llm_provider.lower() == "openai":
        # Use OpenAI with standard API
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("OPENAI_API_KEY environment variable is required")

        default_model = settings.OPENAI_DEFAULT_MODEL

        client = OpenAI(api_key=api_key)

        # Return the client which can be used with the Agent SDK
        return client

    elif llm_provider.lower() == "gemini":
        # Use OpenAI-compatible client with Google's Gemini endpoint
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        default_model = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        # Return the client which can be used with the Agent SDK
        return client

    elif llm_provider.lower() == "gemini":
        # Use OpenAI-compatible client with Google's Gemini endpoint
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        default_model = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash")

        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        # Return the client which can be used with the Agent SDK
        return client

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {llm_provider}. Use 'openai' or 'gemini'")
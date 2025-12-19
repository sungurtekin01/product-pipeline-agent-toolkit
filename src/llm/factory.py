"""LLM client factory for provider-agnostic client creation"""

import os
from typing import Dict, Any, Optional

from .base import BaseLLMClient
from .gemini_client import GeminiClient
from .claude_client import ClaudeClient
from .openai_client import OpenAIClient


class LLMFactory:
    """Factory for creating LLM clients with configuration support

    This factory enables creating LLM clients based on configuration,
    supporting multiple providers and per-agent customization.

    Example usage:
        # Create from explicit parameters
        client = LLMFactory.create('gemini', 'gemini-2.5-pro', 'GEMINI_API_KEY')

        # Create from config with agent-specific settings
        config = {
            'llm': {
                'strategist': {
                    'provider': 'claude',
                    'model': 'claude-opus-4-5',
                    'api_key_env': 'ANTHROPIC_API_KEY'
                }
            }
        }
        client = LLMFactory.from_config(config, 'strategist')
    """

    # Registry of available providers
    PROVIDERS = {
        'gemini': GeminiClient,
        'claude': ClaudeClient,
        'openai': OpenAIClient
    }

    @classmethod
    def create(cls, provider: str, model: str, api_key_env: str) -> BaseLLMClient:
        """Create LLM client from explicit parameters

        Args:
            provider: Provider name ('gemini', 'claude', 'openai')
            model: Model identifier (e.g., 'gemini-2.5-pro')
            api_key_env: Environment variable name containing API key

        Returns:
            Configured LLM client instance

        Raises:
            ValueError: If provider is unknown or API key not found
        """
        # Validate provider
        if provider not in cls.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available providers: {', '.join(cls.PROVIDERS.keys())}"
            )

        # Load API key from environment
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable: {api_key_env}. "
                f"Please ensure it is set in your .env file."
            )

        # Create and return client
        client_class = cls.PROVIDERS[provider]
        return client_class(model=model, api_key=api_key)

    @classmethod
    def from_config(
        cls,
        config: Dict[str, Any],
        agent_name: str,
        cli_override: Optional[Dict[str, str]] = None
    ) -> BaseLLMClient:
        """Create client from product.config.json with CLI overrides

        Configuration priority (highest to lowest):
        1. CLI arguments (--provider, --model)
        2. Agent-specific config in product.config.json
        3. Default values

        Args:
            config: Product configuration dictionary (from product.config.json)
            agent_name: Name of agent (e.g., 'strategist', 'designer', 'po')
            cli_override: Optional dict with 'provider' and/or 'model' from CLI

        Returns:
            Configured LLM client instance

        Raises:
            ValueError: If configuration is invalid or API key not found

        Example config structure:
            {
                "llm": {
                    "strategist": {
                        "provider": "claude",
                        "model": "claude-opus-4-5",
                        "api_key_env": "ANTHROPIC_API_KEY"
                    },
                    "designer": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "api_key_env": "OPENAI_API_KEY"
                    }
                }
            }
        """
        # Get agent-specific config
        agent_config = config.get('llm', {}).get(agent_name, {})

        # Apply priority: CLI > agent config > defaults
        cli = cli_override or {}

        provider = cli.get('provider') or agent_config.get('provider', 'gemini')
        model = cli.get('model') or agent_config.get('model', cls._get_default_model(provider))

        # Determine API key environment variable
        # Use agent-specific key if configured, otherwise use provider default
        api_key_env = agent_config.get('api_key_env')
        if not api_key_env:
            api_key_env = cls._get_default_api_key_env(provider)

        # Create and return client
        return cls.create(provider, model, api_key_env)

    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get default model for a provider

        Args:
            provider: Provider name

        Returns:
            Default model identifier for the provider
        """
        defaults = {
            'gemini': 'gemini-2.5-pro',
            'claude': 'claude-sonnet-4-5',
            'openai': 'gpt-4'
        }
        return defaults.get(provider, 'gemini-2.5-pro')

    @staticmethod
    def _get_default_api_key_env(provider: str) -> str:
        """Get default API key environment variable for a provider

        Args:
            provider: Provider name

        Returns:
            Default environment variable name for the provider's API key
        """
        defaults = {
            'gemini': 'GEMINI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY'
        }
        return defaults.get(provider, 'GEMINI_API_KEY')

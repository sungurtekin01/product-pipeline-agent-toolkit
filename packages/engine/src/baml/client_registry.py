"""
BAML Client Registry

Maps API parameters to BAML client names for runtime provider override.

Design Principles:
- NO hardcoded persona-to-provider mappings
- API keys from .env file (GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY)
- Default: All personas use Gemini
- Future: UI → API → ClientRegistry → BAML client override

Example Usage:
    # Current state (defaults)
    registry = BAMLClientRegistry()
    client_registry = registry.get_client_registry()
    # Returns: None (use BAML defaults)

    # Future state (from API parameters)
    api_params = {"strategist_provider": "claude", "designer_provider": "openai"}
    registry = BAMLClientRegistry(api_params)
    client_registry = registry.get_client_registry()
    # Returns: baml_py.ClientRegistry object with overrides

    # Use with BAML
    brd = await b.GenerateBRD(vision="...", persona="...", baml_options={"client_registry": client_registry})
"""

import os
from typing import Dict, Optional, Any
from baml_py import ClientRegistry


class BAMLClientRegistry:
    """
    Maps API parameters to BAML client names for runtime provider selection.

    This class enables flexible provider selection without hardcoding persona-to-provider
    mappings. Any persona can use any provider at runtime.
    """

    # Provider name to BAML provider string mapping
    PROVIDER_MAP = {
        "gemini": "google-ai",
        "claude": "anthropic",
        "openai": "openai",
    }

    # Provider to default model mapping
    PROVIDER_MODELS = {
        "gemini": "gemini-2.0-flash-exp",
        "claude": "claude-sonnet-4-20250514",
        "openai": "gpt-4o",
    }

    # Provider to environment variable mapping
    PROVIDER_ENV_VARS = {
        "gemini": "GEMINI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
    }

    # Persona function client names (used by BAML functions)
    PERSONA_CLIENTS = {
        "strategist": "StrategistClient",
        "designer": "DesignerClient",
        "po": "POClient",
    }

    def __init__(self, api_params: Optional[Dict[str, Any]] = None):
        """
        Initialize ClientRegistry with optional API parameters.

        Args:
            api_params: Optional dict with provider selection from API/UI
                        Format: {"strategist_provider": "claude", "designer_provider": "gemini", ...}
                        If None, uses BAML default clients (all Gemini)
        """
        self.api_params = api_params or {}

    def get_client_registry(self) -> Optional[ClientRegistry]:
        """
        Generate BAML ClientRegistry object from API parameters.

        Returns:
            ClientRegistry object with provider overrides, or None to use BAML defaults.

        Example:
            # API params: {"strategist_provider": "claude"}
            # Returns: ClientRegistry with StrategistClient configured to use Claude

            # BAML function GenerateBRD uses StrategistClient
            # With override, BAML uses Claude instead of default Gemini
        """
        # If no overrides specified, return None to use BAML defaults
        if not self.api_params:
            return None

        # Create ClientRegistry object
        client_registry = ClientRegistry()

        for persona, function_client in self.PERSONA_CLIENTS.items():
            # Check if API specified provider for this persona
            provider_key = f"{persona}_provider"

            if provider_key in self.api_params:
                provider_name = self.api_params[provider_key]

                # Validate provider name
                if provider_name not in self.PROVIDER_MAP:
                    raise ValueError(
                        f"Invalid provider '{provider_name}' for {persona}. "
                        f"Valid options: {list(self.PROVIDER_MAP.keys())}"
                    )

                # Get provider details
                provider_string = self.PROVIDER_MAP[provider_name]
                model = self.PROVIDER_MODELS[provider_name]
                api_key_env = self.PROVIDER_ENV_VARS[provider_name]
                api_key = os.getenv(api_key_env)

                if not api_key:
                    raise ValueError(
                        f"Missing API key for {provider_name}. "
                        f"Please set {api_key_env} environment variable."
                    )

                # Add client override to registry
                client_registry.add_llm_client(
                    name=function_client,
                    provider=provider_string,
                    options={
                        "model": model,
                        "api_key": api_key,
                    }
                )

        return client_registry

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available LLM providers.

        Returns:
            List of provider names: ["gemini", "claude", "openai"]
        """
        return list(cls.PROVIDER_MAP.keys())

    @classmethod
    def get_persona_clients(cls) -> Dict[str, str]:
        """
        Get mapping of personas to their function client names.

        Returns:
            Dict of persona -> function client name
        """
        return cls.PERSONA_CLIENTS.copy()

    def __repr__(self) -> str:
        if self.api_params:
            return f"<BAMLClientRegistry overrides={self.api_params}>"
        return "<BAMLClientRegistry defaults>"

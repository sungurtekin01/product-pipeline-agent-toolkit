"""
Unit tests for BAML ClientRegistry

Tests client override mapping logic for flexible provider selection.
"""

import os
import pytest
from unittest.mock import patch
from baml_py import ClientRegistry
from packages.engine.src.baml.client_registry import BAMLClientRegistry


class TestBAMLClientRegistry:
    """Test suite for BAMLClientRegistry"""

    def test_init_without_params(self):
        """Test initialization without API parameters uses defaults"""
        registry = BAMLClientRegistry()
        assert registry.api_params == {}
        assert registry.get_client_registry() is None

    def test_init_with_params(self):
        """Test initialization with API parameters"""
        params = {"strategist_provider": "claude"}
        registry = BAMLClientRegistry(params)
        assert registry.api_params == params

    def test_get_client_registry_returns_none_when_empty(self):
        """Test get_client_registry returns None with no API params"""
        registry = BAMLClientRegistry()
        client_registry = registry.get_client_registry()
        assert client_registry is None

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_client_registry_single_persona(self):
        """Test mapping single persona to provider returns ClientRegistry"""
        params = {"strategist_provider": "claude"}
        registry = BAMLClientRegistry(params)
        client_registry = registry.get_client_registry()

        assert client_registry is not None
        assert isinstance(client_registry, ClientRegistry)

    @patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-claude-key",
        "OPENAI_API_KEY": "test-openai-key",
        "GEMINI_API_KEY": "test-gemini-key",
    })
    def test_get_client_registry_multiple_personas(self):
        """Test mapping multiple personas to different providers"""
        params = {
            "strategist_provider": "claude",
            "designer_provider": "openai",
            "po_provider": "gemini",
        }
        registry = BAMLClientRegistry(params)
        client_registry = registry.get_client_registry()

        assert client_registry is not None
        assert isinstance(client_registry, ClientRegistry)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_client_registry_partial_params(self):
        """Test that only specified personas are overridden"""
        params = {"strategist_provider": "claude"}
        registry = BAMLClientRegistry(params)
        client_registry = registry.get_client_registry()

        # Should return a valid ClientRegistry object
        assert client_registry is not None
        assert isinstance(client_registry, ClientRegistry)

    def test_invalid_provider_name(self):
        """Test that invalid provider name raises ValueError"""
        params = {"strategist_provider": "invalid_provider"}
        registry = BAMLClientRegistry(params)

        with pytest.raises(ValueError) as exc_info:
            registry.get_client_registry()

        assert "Invalid provider 'invalid_provider'" in str(exc_info.value)
        assert "gemini" in str(exc_info.value)
        assert "claude" in str(exc_info.value)
        assert "openai" in str(exc_info.value)

    def test_missing_api_key(self):
        """Test that missing API key raises ValueError"""
        params = {"strategist_provider": "claude"}
        registry = BAMLClientRegistry(params)

        # Clear environment to ensure key is missing
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                registry.get_client_registry()

            assert "Missing API key for claude" in str(exc_info.value)
            assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_get_available_providers(self):
        """Test getting list of available providers"""
        providers = BAMLClientRegistry.get_available_providers()

        assert isinstance(providers, list)
        assert "gemini" in providers
        assert "claude" in providers
        assert "openai" in providers
        assert len(providers) == 3

    def test_get_persona_clients(self):
        """Test getting persona to client mapping"""
        clients = BAMLClientRegistry.get_persona_clients()

        assert isinstance(clients, dict)
        assert clients["strategist"] == "StrategistClient"
        assert clients["designer"] == "DesignerClient"
        assert clients["po"] == "POClient"
        assert len(clients) == 3

    def test_repr_with_defaults(self):
        """Test string representation with defaults"""
        registry = BAMLClientRegistry()
        repr_str = repr(registry)

        assert "BAMLClientRegistry" in repr_str
        assert "defaults" in repr_str

    def test_repr_with_overrides(self):
        """Test string representation with overrides"""
        params = {"strategist_provider": "claude"}
        registry = BAMLClientRegistry(params)
        repr_str = repr(registry)

        assert "BAMLClientRegistry" in repr_str
        assert "overrides" in repr_str
        assert "strategist_provider" in repr_str
        assert "claude" in repr_str

    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-gemini",
        "ANTHROPIC_API_KEY": "test-claude",
        "OPENAI_API_KEY": "test-openai",
    })
    def test_all_providers_for_strategist(self):
        """Test that strategist can use all providers"""
        for provider in ["gemini", "claude", "openai"]:
            params = {"strategist_provider": provider}
            registry = BAMLClientRegistry(params)
            client_registry = registry.get_client_registry()

            assert client_registry is not None
            assert isinstance(client_registry, ClientRegistry)

    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-gemini",
        "ANTHROPIC_API_KEY": "test-claude",
        "OPENAI_API_KEY": "test-openai",
    })
    def test_all_providers_for_designer(self):
        """Test that designer can use all providers"""
        for provider in ["gemini", "claude", "openai"]:
            params = {"designer_provider": provider}
            registry = BAMLClientRegistry(params)
            client_registry = registry.get_client_registry()

            assert client_registry is not None
            assert isinstance(client_registry, ClientRegistry)

    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-gemini",
        "ANTHROPIC_API_KEY": "test-claude",
        "OPENAI_API_KEY": "test-openai",
    })
    def test_all_providers_for_po(self):
        """Test that PO can use all providers"""
        for provider in ["gemini", "claude", "openai"]:
            params = {"po_provider": provider}
            registry = BAMLClientRegistry(params)
            client_registry = registry.get_client_registry()

            assert client_registry is not None
            assert isinstance(client_registry, ClientRegistry)

    def test_case_sensitivity(self):
        """Test that provider names are case-sensitive"""
        params = {"strategist_provider": "Claude"}  # Capital C
        registry = BAMLClientRegistry(params)

        with pytest.raises(ValueError):
            registry.get_client_registry()

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_extra_params_ignored(self):
        """Test that extra/unknown params are ignored"""
        params = {
            "strategist_provider": "claude",
            "unknown_param": "value",
            "another_param": 123,
        }
        registry = BAMLClientRegistry(params)
        client_registry = registry.get_client_registry()

        # Should return valid ClientRegistry with only strategist override
        assert client_registry is not None
        assert isinstance(client_registry, ClientRegistry)

    def test_immutability_of_persona_clients(self):
        """Test that get_persona_clients returns a copy"""
        clients1 = BAMLClientRegistry.get_persona_clients()
        clients2 = BAMLClientRegistry.get_persona_clients()

        # Modify one
        clients1["test"] = "TestClient"

        # Original should be unchanged
        assert "test" not in clients2
        assert "test" not in BAMLClientRegistry.PERSONA_CLIENTS

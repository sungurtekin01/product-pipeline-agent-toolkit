"""Unit tests for LLM clients and factory"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.llm.base import BaseLLMClient
from src.llm.gemini_client import GeminiClient
from src.llm.claude_client import ClaudeClient
from src.llm.openai_client import OpenAIClient
from src.llm.factory import LLMFactory


class TestGeminiClient:
    """Test GeminiClient implementation"""

    @patch('src.llm.gemini_client.genai')
    def test_generate(self, mock_genai):
        """Test Gemini client generation"""
        # Setup mock for new google-genai SDK
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Create client and generate
        client = GeminiClient(model='gemini-2.5-pro', api_key='test_key')
        result = client.generate("Test prompt")

        # Assertions
        assert result == "Generated response"
        mock_client.models.generate_content.assert_called_once()

    def test_clean_response(self):
        """Test response cleaning for code fences"""
        client = GeminiClient(model='gemini-2.5-pro', api_key='test_key')

        # Test JSON code fence removal
        response = "```json\n{\"key\": \"value\"}\n```"
        cleaned = client.clean_response(response)
        assert cleaned == '{"key": "value"}'

        # Test plain code fence removal
        response = "```\n{\"key\": \"value\"}\n```"
        cleaned = client.clean_response(response)
        assert cleaned == '{"key": "value"}'

        # Test no code fence
        response = '{"key": "value"}'
        cleaned = client.clean_response(response)
        assert cleaned == '{"key": "value"}'


class TestClaudeClient:
    """Test ClaudeClient implementation"""

    @patch('src.llm.claude_client.Anthropic')
    def test_generate(self, mock_anthropic):
        """Test Claude client generation"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create client and generate
        client = ClaudeClient(model='claude-opus-4-5', api_key='test_key')
        result = client.generate("Test prompt")

        # Assertions
        assert result == "Generated response"
        mock_client.messages.create.assert_called_once()

    @patch('src.llm.claude_client.Anthropic')
    def test_generate_with_system_prompt(self, mock_anthropic):
        """Test Claude client with system prompt"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create client and generate with system prompt
        client = ClaudeClient(model='claude-opus-4-5', api_key='test_key')
        result = client.generate("Test prompt", system_prompt="You are a helpful assistant")

        # Assertions
        assert result == "Generated response"
        call_kwargs = mock_client.messages.create.call_args[1]
        assert 'system' in call_kwargs
        assert call_kwargs['system'] == "You are a helpful assistant"


class TestOpenAIClient:
    """Test OpenAIClient implementation"""

    @patch('src.llm.openai_client.OpenAI')
    def test_generate(self, mock_openai):
        """Test OpenAI client generation"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create client and generate
        client = OpenAIClient(model='gpt-4', api_key='test_key')
        result = client.generate("Test prompt")

        # Assertions
        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.llm.openai_client.OpenAI')
    def test_generate_with_system_prompt(self, mock_openai):
        """Test OpenAI client with system prompt"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create client and generate with system prompt
        client = OpenAIClient(model='gpt-4', api_key='test_key')
        result = client.generate("Test prompt", system_prompt="You are a helpful assistant")

        # Assertions
        assert result == "Generated response"
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are a helpful assistant"


class TestLLMFactory:
    """Test LLMFactory for client creation"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_gemini_key'})
    @patch('src.llm.gemini_client.genai')
    def test_create_gemini(self, mock_genai):
        """Test factory creates Gemini client"""
        client = LLMFactory.create('gemini', 'gemini-2.5-pro', 'GEMINI_API_KEY')
        assert isinstance(client, GeminiClient)
        assert client.model == 'gemini-2.5-pro'

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_claude_key'})
    @patch('src.llm.claude_client.Anthropic')
    def test_create_claude(self, mock_anthropic):
        """Test factory creates Claude client"""
        client = LLMFactory.create('claude', 'claude-opus-4-5', 'ANTHROPIC_API_KEY')
        assert isinstance(client, ClaudeClient)
        assert client.model == 'claude-opus-4-5'

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('src.llm.openai_client.OpenAI')
    def test_create_openai(self, mock_openai):
        """Test factory creates OpenAI client"""
        client = LLMFactory.create('openai', 'gpt-4', 'OPENAI_API_KEY')
        assert isinstance(client, OpenAIClient)
        assert client.model == 'gpt-4'

    def test_create_invalid_provider(self):
        """Test factory raises error for invalid provider"""
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMFactory.create('invalid', 'model', 'API_KEY')

    def test_create_missing_api_key(self):
        """Test factory raises error for missing API key"""
        with pytest.raises(ValueError, match="API key not found"):
            LLMFactory.create('gemini', 'gemini-2.5-pro', 'NONEXISTENT_KEY')

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.llm.claude_client.Anthropic')
    def test_from_config(self, mock_anthropic):
        """Test factory creates client from config"""
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
        assert isinstance(client, ClaudeClient)
        assert client.model == 'claude-opus-4-5'

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.llm.claude_client.Anthropic')
    def test_from_config_with_cli_override(self, mock_anthropic):
        """Test CLI overrides take precedence"""
        config = {
            'llm': {
                'strategist': {
                    'provider': 'gemini',  # This should be overridden
                    'model': 'gemini-2.5-pro',
                    'api_key_env': 'ANTHROPIC_API_KEY'
                }
            }
        }

        # CLI override
        cli_override = {'provider': 'claude', 'model': 'claude-sonnet-4-5'}

        client = LLMFactory.from_config(config, 'strategist', cli_override)
        assert isinstance(client, ClaudeClient)
        assert client.model == 'claude-sonnet-4-5'

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'})
    @patch('src.llm.gemini_client.genai')
    def test_from_config_with_defaults(self, mock_genai):
        """Test factory uses defaults when config missing"""
        config = {}  # Empty config

        client = LLMFactory.from_config(config, 'unknown_agent')
        assert isinstance(client, GeminiClient)  # Default provider
        assert client.model == 'gemini-2.5-pro'  # Default model


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

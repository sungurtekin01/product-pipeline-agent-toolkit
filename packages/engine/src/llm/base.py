"""Base LLM client interface for provider-agnostic LLM interactions"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM providers

    This class defines the interface that all LLM provider implementations
    must follow, enabling seamless switching between different providers
    (Gemini, Claude, OpenAI, etc.)
    """

    def __init__(self, model: str, api_key: str):
        """Initialize LLM client

        Args:
            model: Model identifier (e.g., 'gemini-2.5-pro', 'claude-opus-4-5')
            api_key: API key for the provider
        """
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM

        Args:
            prompt: The user prompt/message to send to the LLM
            system_prompt: Optional system prompt to set context/persona

        Returns:
            Generated text response from the LLM

        Raises:
            Exception: If API call fails or response is invalid
        """
        pass

    @abstractmethod
    def clean_response(self, response: str) -> str:
        """Clean code fences and formatting from response

        Different LLM providers may wrap JSON responses in code fences
        (e.g., ```json ... ```). This method removes such formatting to
        extract the raw content.

        Args:
            response: Raw response text from LLM

        Returns:
            Cleaned response text without code fences or extra formatting
        """
        pass

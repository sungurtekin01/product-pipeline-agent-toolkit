"""Claude (Anthropic) LLM client implementation"""

import re
from typing import Optional

from anthropic import Anthropic

from .base import BaseLLMClient


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude LLM client implementation

    Wraps the anthropic SDK to provide a consistent interface
    for Claude models (claude-opus-4-5, claude-sonnet-4-5, etc.)
    """

    def __init__(self, model: str, api_key: str):
        """Initialize Claude client

        Args:
            model: Claude model identifier (e.g., 'claude-opus-4-5')
            api_key: Anthropic API key
        """
        super().__init__(model, api_key)
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from Claude

        Args:
            prompt: The user prompt/message to send to Claude
            system_prompt: Optional system prompt to set context/persona

        Returns:
            Generated text response from Claude

        Raises:
            Exception: If API call fails
        """
        # Build messages array
        messages = [{"role": "user", "content": prompt}]

        # Call Claude API with optional system prompt
        if system_prompt:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=messages
            )

        # Extract text from response
        return response.content[0].text

    def clean_response(self, response: str) -> str:
        """Clean code fences from Claude response

        Claude may wrap JSON responses in code fences like:
        ```json
        {...}
        ```

        This method removes those fences to extract raw content.

        Args:
            response: Raw response text from Claude

        Returns:
            Cleaned response without code fences
        """
        # Strip leading/trailing whitespace
        cleaned = response.strip()

        # Remove opening code fence (```json or ```)
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)

        # Remove closing code fence (```)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        return cleaned.strip()

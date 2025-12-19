"""OpenAI GPT LLM client implementation"""

import re
from typing import Optional

from openai import OpenAI

from .base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT LLM client implementation

    Wraps the openai SDK to provide a consistent interface
    for GPT models (gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.)
    """

    def __init__(self, model: str, api_key: str):
        """Initialize OpenAI client

        Args:
            model: OpenAI model identifier (e.g., 'gpt-4', 'gpt-4-turbo')
            api_key: OpenAI API key
        """
        super().__init__(model, api_key)
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from OpenAI GPT

        Args:
            prompt: The user prompt/message to send to GPT
            system_prompt: Optional system prompt to set context/persona

        Returns:
            Generated text response from GPT

        Raises:
            Exception: If API call fails
        """
        # Build messages array
        messages = []

        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )

        # Extract text from response
        return response.choices[0].message.content

    def clean_response(self, response: str) -> str:
        """Clean code fences from OpenAI response

        OpenAI may wrap JSON responses in code fences like:
        ```json
        {...}
        ```

        This method removes those fences to extract raw content.

        Args:
            response: Raw response text from OpenAI

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

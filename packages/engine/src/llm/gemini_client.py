"""Gemini LLM client implementation"""

import re
from typing import Optional

import google.generativeai as genai

from .base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client implementation

    Wraps the google.generativeai SDK to provide a consistent interface
    for Gemini models (gemini-2.5-pro, gemini-2.5-flash, etc.)
    """

    def __init__(self, model: str, api_key: str):
        """Initialize Gemini client

        Args:
            model: Gemini model identifier (e.g., 'gemini-2.5-pro')
            api_key: Google API key for Gemini
        """
        super().__init__(model, api_key)
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from Gemini

        Args:
            prompt: The user prompt/message to send to Gemini
            system_prompt: Optional system prompt (prepended to prompt)

        Returns:
            Generated text response from Gemini

        Raises:
            Exception: If API call fails
        """
        # Combine system prompt and user prompt if system prompt provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Call Gemini API
        response = self.client.generate_content(full_prompt, stream=False)

        return response.text

    def clean_response(self, response: str) -> str:
        """Clean code fences from Gemini response

        Gemini often wraps JSON responses in code fences like:
        ```json
        {...}
        ```

        This method removes those fences to extract raw content.

        Args:
            response: Raw response text from Gemini

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

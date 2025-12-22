"""Gemini LLM client implementation"""

import re
from typing import Optional

import google.genai as genai
from google.genai import types

from .base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM client implementation

    Wraps the google.genai SDK to provide a consistent interface
    for Gemini models (gemini-2.5-pro, gemini-2.5-flash, etc.)
    """

    def __init__(self, model: str, api_key: str):
        """Initialize Gemini client

        Args:
            model: Gemini model identifier (e.g., 'gemini-2.5-pro')
            api_key: Google API key for Gemini
        """
        super().__init__(model, api_key)
        self.client = genai.Client(api_key=self.api_key)

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
        import time

        # Prepare contents
        contents = [types.Content(parts=[types.Part(text=prompt)])]

        # Add system instruction if provided
        config = None
        if system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt
            )

        # Call Gemini API with retry on rate limit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                        print(f"Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                raise

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

"""
OpenAI provider implementation with streaming support
"""
from typing import List, Dict, Generator
import time

from .base_provider import BaseAIProvider
from utils.retry_handler import with_retry, RateLimitHandler


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API provider with streaming capabilities and retry logic
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True
        self.rate_limiter = RateLimitHandler(calls_per_minute=60)

    @with_retry(max_retries=3, base_delay=1.0)
    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using OpenAI API with retry logic"""
        self.rate_limiter.wait_if_needed()
        
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            # Prepare messages with system prompt
            api_messages = self._prepare_messages_with_system(messages)

            response = client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=self.temperature,
            )

            return response.choices[0].message.content

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"OpenAI API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using OpenAI API"""
        self.rate_limiter.wait_if_needed()
        
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            # Prepare messages with system prompt
            api_messages = self._prepare_messages_with_system(messages)

            stream = client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=self.temperature,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"OpenAI API streaming error: {exc}") from exc

    def _prepare_messages_with_system(self, messages: List[Dict]) -> List[Dict]:
        """Add system prompt to messages"""
        api_messages = []

        if self.system_prompt:
            api_messages.append({
                'role': 'system',
                'content': self.system_prompt,
            })

        api_messages.extend(messages)
        return api_messages
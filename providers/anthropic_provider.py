"""
Anthropic Claude provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider
from utils.retry_handler import with_retry, RateLimitHandler


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude API provider with streaming capabilities and retry logic
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True
        self.rate_limiter = RateLimitHandler(calls_per_minute=50)  # Anthropic has stricter limits

    @with_retry(max_retries=3, base_delay=1.0)
    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Anthropic API with retry logic"""
        self.rate_limiter.wait_if_needed()
        
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=self.temperature,
                system=self.system_prompt if self.system_prompt else None,
                messages=messages,
            )

            return response.content[0].text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Anthropic API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Anthropic API"""
        self.rate_limiter.wait_if_needed()
        
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=self.api_key)

            with client.messages.stream(
                model=self.model,
                max_tokens=4096,
                temperature=self.temperature,
                system=self.system_prompt if self.system_prompt else None,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Anthropic API streaming error: {exc}") from exc
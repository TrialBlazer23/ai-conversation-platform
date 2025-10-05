"""
Anthropic Claude provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude API provider with streaming capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True

    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Anthropic API"""
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

            # Extract content with defensive checks
            if response.content and len(response.content) > 0:
                content = response.content[0].text
                if content is not None:
                    return content
            
            raise Exception("No content in Anthropic response")

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Anthropic API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Anthropic API"""
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
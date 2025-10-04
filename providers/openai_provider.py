"""
OpenAI provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API provider with streaming capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True

    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using OpenAI API"""
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

            # Extract content with defensive checks
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content is not None:
                    return content
            
            raise Exception("No content in OpenAI response")

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"OpenAI API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using OpenAI API"""
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
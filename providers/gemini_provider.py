"""
Google Gemini provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API provider with streaming capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True

    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Google Gemini API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini(messages)

            # Configure generation
            generation_config = {
                'temperature': self.temperature,
            }

            response = model.generate_content(
                gemini_messages,
                generation_config=generation_config,
            )

            return response.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Gemini API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Google Gemini API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini(messages)

            # Configure generation
            generation_config = {
                'temperature': self.temperature,
            }

            response = model.generate_content(
                gemini_messages,
                generation_config=generation_config,
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Gemini API streaming error: {exc}") from exc

    def _convert_messages_to_gemini(self, messages: List[Dict]) -> List[Dict]:
        """
        Convert standard message format to Gemini format
        Gemini uses 'user' and 'model' roles instead of 'user' and 'assistant'
        """
        gemini_messages = []

        # Add system prompt if exists
        if self.system_prompt:
            gemini_messages.append({
                'role': 'user',
                'parts': [self.system_prompt],
            })
            gemini_messages.append({
                'role': 'model',
                'parts': ['Understood. I will follow these instructions.'],
            })

        # Convert messages
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            # Map roles: assistant -> model
            if role == 'assistant':
                role = 'model'
            elif role == 'system':
                # System messages converted to user messages in Gemini
                role = 'user'

            gemini_messages.append({
                'role': role,
                'parts': [content],
            })

        return gemini_messages

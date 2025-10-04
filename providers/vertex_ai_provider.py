"""
Google Vertex AI provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider


class VertexAIProvider(BaseAIProvider):
    """
    Google Vertex AI provider with streaming capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True

    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Google Vertex AI API"""
        try:
            from vertexai.preview.generative_models import GenerativeModel
            import vertexai

            # Extract project ID from api_key (format: "project_id" or JSON credentials)
            project_id = self._extract_project_id(self.api_key)

            # Initialize Vertex AI
            vertexai.init(project=project_id)

            model = GenerativeModel(self.model)

            # Convert messages to Vertex AI format
            vertex_messages = self._convert_messages_to_vertex(messages)

            # Configure generation
            generation_config = {
                'temperature': self.temperature,
            }

            response = model.generate_content(
                vertex_messages,
                generation_config=generation_config,
            )

            return response.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Vertex AI API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Google Vertex AI API"""
        try:
            from vertexai.preview.generative_models import GenerativeModel
            import vertexai

            # Extract project ID from api_key
            project_id = self._extract_project_id(self.api_key)

            # Initialize Vertex AI
            vertexai.init(project=project_id)

            model = GenerativeModel(self.model)

            # Convert messages to Vertex AI format
            vertex_messages = self._convert_messages_to_vertex(messages)

            # Configure generation
            generation_config = {
                'temperature': self.temperature,
            }

            response = model.generate_content(
                vertex_messages,
                generation_config=generation_config,
                stream=True,
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Vertex AI API streaming error: {exc}") from exc

    def _extract_project_id(self, api_key: str) -> str:
        """
        Extract project ID from API key
        Can be a simple project ID string or JSON credentials
        """
        import json

        try:
            # Try to parse as JSON credentials
            credentials = json.loads(api_key)
            return credentials.get('project_id', '')
        except (json.JSONDecodeError, TypeError):
            # Assume it's a simple project ID string
            return api_key

    def _convert_messages_to_vertex(self, messages: List[Dict]) -> List[Dict]:
        """
        Convert standard message format to Vertex AI format
        Vertex AI uses 'user' and 'model' roles
        """
        vertex_messages = []

        # Add system prompt if exists
        if self.system_prompt:
            vertex_messages.append({
                'role': 'user',
                'parts': [{'text': self.system_prompt}],
            })
            vertex_messages.append({
                'role': 'model',
                'parts': [{'text': 'Understood. I will follow these instructions.'}],
            })

        # Convert messages
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            # Map roles: assistant -> model
            if role == 'assistant':
                role = 'model'
            elif role == 'system':
                # System messages converted to user messages
                role = 'user'

            vertex_messages.append({
                'role': role,
                'parts': [{'text': content}],
            })

        return vertex_messages

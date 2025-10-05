"""
Ollama provider implementation for local models
Supports streaming and provides cost-free inference
"""
from typing import List, Dict, Generator
import json

import requests

from .base_provider import BaseAIProvider
from config import Config


class OllamaProvider(BaseAIProvider):
    """
    Ollama API provider for local model inference
    Zero-cost, privacy-focused alternative to cloud providers
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "llama2",
        temperature: float = 0.7,
        system_prompt: str = '',
    ):
        # Ollama doesn't need API key, but we maintain interface consistency
        super().__init__(api_key or "local", model, temperature, system_prompt)
        self.base_url = Config.OLLAMA_BASE_URL
        self.supports_streaming = True
        self.timeout = Config.OLLAMA_TIMEOUT

    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Ollama API"""
        try:
            url = f"{self.base_url}/api/chat"

            payload = {
                "model": self.model,
                "messages": self._prepare_messages_with_system(messages),
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                },
            }

            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            return result.get('message', {}).get('content', '')

        except requests.exceptions.ConnectionError as exc:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running (ollama serve)",
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Ollama API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Ollama API"""
        try:
            url = f"{self.base_url}/api/chat"

            payload = {
                "model": self.model,
                "messages": self._prepare_messages_with_system(messages),
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                },
            }

            response = requests.post(url, json=payload, timeout=self.timeout, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'message' in chunk and 'content' in chunk['message']:
                        yield chunk['message']['content']

        except requests.exceptions.ConnectionError as exc:
            raise Exception(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running (ollama serve)",
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Ollama API streaming error: {exc}") from exc

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

    @staticmethod
    def list_available_models():
        """
        List all models available in local Ollama instance

        Returns:
            List of model names
        """
        try:
            url = f"{Config.OLLAMA_BASE_URL}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except Exception:  # noqa: BLE001
            return []
"""
Base provider abstraction with streaming support
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Generator


class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers
    Enhanced with streaming capabilities
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        system_prompt: str = '',
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.supports_streaming = False

    @abstractmethod
    def generate_response(self, messages: List[Dict]) -> str:
        """
        Generate a response from the AI model

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Generated response text
        """

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        Generate a streaming response from the AI model
        Override this method in subclasses that support streaming

        Args:
            messages: List of message dictionaries

        Yields:
            Chunks of response text
        """
        # Default implementation: yield entire response at once
        response = self.generate_response(messages)
        yield response

    def _prepare_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Prepare messages for API call
        Can be overridden by subclasses for provider-specific formatting
        """
        return messages

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count (override for accurate counting)

        Args:
            text: Text to count

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
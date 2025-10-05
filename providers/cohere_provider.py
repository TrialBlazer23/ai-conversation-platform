"""
Cohere provider implementation with streaming support
"""
from typing import List, Dict, Generator

from .base_provider import BaseAIProvider
from utils.retry_handler import with_retry, RateLimitHandler


class CohereProvider(BaseAIProvider):
    """
    Cohere API provider with streaming capabilities and retry logic
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True
        self.rate_limiter = RateLimitHandler(calls_per_minute=50)

    @with_retry(max_retries=3, base_delay=1.0)
    def generate_response(self, messages: List[Dict]) -> str:
        """Generate response using Cohere API with retry logic"""
        self.rate_limiter.wait_if_needed()
        
        try:
            import cohere

            client = cohere.Client(api_key=self.api_key)

            # Convert messages to Cohere format
            chat_history, message = self._convert_messages(messages)

            response = client.chat(
                message=message,
                model=self.model,
                temperature=self.temperature,
                chat_history=chat_history,
                preamble=self.system_prompt if self.system_prompt else None,
            )

            return response.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Cohere API error: {exc}") from exc

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Generate streaming response using Cohere API"""
        self.rate_limiter.wait_if_needed()
        
        try:
            import cohere

            client = cohere.Client(api_key=self.api_key)

            # Convert messages to Cohere format
            chat_history, message = self._convert_messages(messages)

            stream = client.chat_stream(
                message=message,
                model=self.model,
                temperature=self.temperature,
                chat_history=chat_history,
                preamble=self.system_prompt if self.system_prompt else None,
            )

            for event in stream:
                if event.event_type == "text-generation":
                    yield event.text

        except Exception as exc:  # noqa: BLE001
            raise Exception(f"Cohere API streaming error: {exc}") from exc

    def _convert_messages(self, messages: List[Dict]) -> tuple:
        """
        Convert standard message format to Cohere chat format
        
        Returns:
            Tuple of (chat_history, current_message)
        """
        if not messages:
            return [], ""
        
        chat_history = []
        
        # Process all but the last message as history
        for msg in messages[:-1]:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                # System messages are handled via preamble
                continue
            elif role == 'assistant':
                chat_history.append({
                    "role": "CHATBOT",
                    "message": content
                })
            else:  # user
                chat_history.append({
                    "role": "USER",
                    "message": content
                })
        
        # Last message is the current prompt
        current_message = messages[-1].get('content', '')
        
        return chat_history, current_message

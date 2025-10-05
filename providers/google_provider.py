"""
Google Gemini provider with streaming support
"""
from typing import List, Dict, Generator
from providers.base_provider import BaseAIProvider
import google.generativeai as genai


class GoogleProvider(BaseAIProvider):
    """
    Google Gemini AI provider with streaming support
    """

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, system_prompt: str = ''):
        super().__init__(api_key, model, temperature, system_prompt)
        self.supports_streaming = True
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        generation_config = {
            'temperature': temperature,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
        
        # Store system prompt to prepend to messages
        self.system_instruction = system_prompt
        
        self.client = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )

    def _prepare_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Convert messages to Gemini format
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Formatted messages for Gemini
        """
        gemini_messages = []
        
        # Add system prompt as first user message if present
        if self.system_instruction:
            gemini_messages.append({
                'role': 'user',
                'parts': [f"System instructions: {self.system_instruction}"]
            })
            gemini_messages.append({
                'role': 'model',
                'parts': ["Understood. I will follow these instructions."]
            })
        
        for msg in messages:
            role = msg['role']
            # Convert role format
            if role == 'assistant':
                role = 'model'
            elif role == 'system':
                # Already handled system messages above
                continue
            
            gemini_messages.append({
                'role': role,
                'parts': [msg['content']]
            })
        
        return gemini_messages

    def generate_response(self, messages: List[Dict]) -> str:
        """
        Generate non-streaming response
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Generated response text
        """
        gemini_messages = self._prepare_messages(messages)
        
        # Start a chat session
        chat = self.client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        
        # Send the last message and get response
        response = chat.send_message(gemini_messages[-1]['parts'][0] if gemini_messages else "Hello")
        
        return response.text

    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        Generate streaming response
        
        Args:
            messages: List of message dictionaries
            
        Yields:
            Chunks of response text
        """
        gemini_messages = self._prepare_messages(messages)
        
        # Start a chat session
        chat = self.client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        
        # Send the last message with streaming
        response = chat.send_message(
            gemini_messages[-1]['parts'][0] if gemini_messages else "Hello",
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text

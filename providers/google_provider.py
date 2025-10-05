"""
Google Gemini AI Provider
Supports Gemini API with the new @google/genai SDK format
"""
from typing import List, Dict, Generator, Optional
import os
import json
import requests
from .base_provider import BaseAIProvider

# Using direct REST API calls following the new @google/genai format


class GoogleProvider(BaseAIProvider):
    """
    Google AI Provider using the new Gemini API REST format
    
    Supports latest Gemini models:
    - gemini-2.5-pro - Latest flagship model
    - gemini-2.0-flash-exp - Latest experimental
    - gemini-1.5-pro - Production flagship
    - gemini-1.5-flash - Fast & efficient
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'gemini-2.5-pro',
        temperature: float = 0.7,
        system_prompt: str = '',
        max_tokens: int = 8192
    ):
        """
        Initialize Google provider
        
        Args:
            api_key: Google API key
            model: Model name
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
        """
        super().__init__(api_key, model, temperature, system_prompt)
        self.max_tokens = max_tokens
        self.supports_streaming = True
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        if not api_key:
            raise ValueError("Google API key is required")
    
    def _format_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Convert OpenAI-style messages to Google format
        
        Google uses 'user' and 'model' roles instead of 'assistant'
        """
        formatted = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            # Convert 'assistant' to 'model' for Google
            if role == 'assistant':
                role = 'model'
            elif role == 'system':
                # Handle system messages by prepending to first user message
                continue
            
            formatted.append({
                'role': role,
                'parts': [{'text': content}]
            })
        
        return formatted
    
    def _create_request_payload(self, messages: List[Dict]) -> Dict:
        """Create request payload for Gemini API"""
        formatted_messages = self._format_messages(messages)
        
        # Handle system prompt
        system_instruction = None
        if self.system_prompt:
            system_instruction = {
                'parts': [{'text': self.system_prompt}]
            }
        
        # Build the payload
        payload = {
            'contents': formatted_messages,
            'generationConfig': {
                'temperature': self.temperature,
                'maxOutputTokens': self.max_tokens,
            }
        }
        
        if system_instruction:
            payload['systemInstruction'] = system_instruction
            
        return payload
    
    def generate_response(self, messages: List[Dict]) -> str:
        """
        Generate a non-streaming response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            payload = self._create_request_payload(messages)
            
            # Make API request
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            return part['text']
            
            return "No response generated"
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")
    
    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """
        Generate a streaming response
        
        Args:
            messages: List of message dictionaries
        
        Yields:
            Chunks of generated text
        """
        try:
            payload = self._create_request_payload(messages)
            
            # Make streaming API request
            url = f"{self.base_url}/models/{self.model}:streamGenerateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            response = requests.post(url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            
            # Process streaming response
            # Gemini returns newline-delimited JSON, NOT SSE format
            for line in response.iter_lines():
                if line:
                    try:
                        # Decode and parse JSON directly (no 'data: ' prefix)
                        chunk_data = json.loads(line.decode('utf-8'))
                        
                        # Extract text from chunk
                        if 'candidates' in chunk_data and len(chunk_data['candidates']) > 0:
                            candidate = chunk_data['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                for part in candidate['content']['parts']:
                                    if 'text' in part:
                                        yield part['text']
                    except json.JSONDecodeError:
                        # Skip lines that aren't valid JSON
                        continue
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Google API streaming request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Google API streaming error: {str(e)}")
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """Return list of available Google models"""
        return [
            {
                'id': 'gemini-2.5-pro',
                'name': 'Gemini 2.5 Pro',
                'description': 'Latest flagship model with 2M token context',
                'context_window': 2000000
            },
            {
                'id': 'gemini-2.0-flash-exp',
                'name': 'Gemini 2.0 Flash Experimental',
                'description': 'Latest experimental model',
                'context_window': 1000000
            },
            {
                'id': 'gemini-1.5-pro',
                'name': 'Gemini 1.5 Pro',
                'description': 'Production flagship, 2M token context',
                'context_window': 2000000
            },
            {
                'id': 'gemini-1.5-flash',
                'name': 'Gemini 1.5 Flash',
                'description': 'Fast and efficient, 1M token context',
                'context_window': 1000000
            },
        ]

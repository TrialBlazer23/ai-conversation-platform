"""
Google Gemini AI Provider
Supports Gemini API with the new @google/genai SDK format
"""
from typing import List, Dict, Generator, Optional
import os
import json
import requests
from .base_provider import BaseAIProvider
from utils.retry_handler import with_retry, RateLimitHandler

# Using direct REST API calls following the new @google/genai format


class GoogleProvider(BaseAIProvider):
    """
    Google AI Provider using the new Gemini API REST format with retry logic
    
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
        self.rate_limiter = RateLimitHandler(calls_per_minute=60)
        
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
    
    @with_retry(max_retries=3, base_delay=1.0)
    def generate_response(self, messages: List[Dict]) -> str:
        """
        Generate a non-streaming response with retry logic
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        self.rate_limiter.wait_if_needed()
        
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
            
            # Debug logging
            print(f"DEBUG GOOGLE: Full API response: {json.dumps(result, indent=2)}")
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"DEBUG GOOGLE: Candidate: {candidate}")
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        if 'text' in part:
                            extracted_text = part['text']
                            print(f"DEBUG GOOGLE: Extracted text: {extracted_text}")
                            return extracted_text
            
            print("DEBUG GOOGLE: No response generated - returning default message")
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
        self.rate_limiter.wait_if_needed()
        
        try:
            payload = self._create_request_payload(messages)
            
            # Make streaming API request
            url = f"{self.base_url}/models/{self.model}:streamGenerateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            print(f"DEBUG GOOGLE STREAM: Making request to {url}")
            
            response = requests.post(url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            
            # Google's streaming response is a JSON array of objects
            # Each line contains a complete JSON object
            buffer = ""
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    # Add to buffer
                    buffer += chunk
                    
                    # Try to extract and parse JSON objects from the buffer
                    # Remove leading characters like '[', ',', whitespace
                    buffer = buffer.lstrip('[\n\r\t, ')
                    
                    # Try to find a complete JSON object
                    if buffer.startswith('{'):
                        # Find matching closing brace
                        brace_count = 0
                        end_pos = -1
                        
                        for i, char in enumerate(buffer):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                        
                        if end_pos > 0:
                            # We have a complete JSON object
                            json_str = buffer[:end_pos]
                            try:
                                chunk_data = json.loads(json_str)
                                
                                print(f"DEBUG GOOGLE STREAM: Parsed chunk: {json.dumps(chunk_data, indent=2)[:200]}")
                                
                                if 'candidates' in chunk_data and len(chunk_data['candidates']) > 0:
                                    candidate = chunk_data['candidates'][0]
                                    if 'content' in candidate and 'parts' in candidate['content']:
                                        for part in candidate['content']['parts']:
                                            if 'text' in part:
                                                text = part['text']
                                                print(f"DEBUG GOOGLE STREAM: Yielding text: {text[:100]}")
                                                yield text
                                
                                # Remove processed object from buffer
                                buffer = buffer[end_pos:]
                                
                            except json.JSONDecodeError as e:
                                print(f"DEBUG GOOGLE STREAM: JSON decode error: {e}")
                                # Keep buffer as is and wait for more data
                                pass
        
        except requests.exceptions.RequestException as e:
            print(f"DEBUG GOOGLE STREAM: Request error: {str(e)}")
            raise Exception(f"Google API streaming request error: {str(e)}")
        except Exception as e:
            print(f"DEBUG GOOGLE STREAM: General error: {str(e)}")
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

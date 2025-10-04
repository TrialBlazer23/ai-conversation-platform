"""
Google Gemini AI Provider
Supports both Gemini API and Vertex AI with streaming
"""
from typing import List, Dict, Generator, Optional
import os
from .base_provider import BaseAIProvider

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig as VertexGenerationConfig
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False


class GoogleProvider(BaseAIProvider):
    """
    Google AI Provider supporting both Gemini API and Vertex AI
    
    Supports:
    - Gemini Pro (gemini-pro)
    - Gemini Pro Vision (gemini-pro-vision)
    - Gemini Ultra (gemini-ultra) - via Vertex AI
    - Gemini 1.5 Pro (gemini-1.5-pro)
    - Gemini 1.5 Flash (gemini-1.5-flash)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'gemini-pro',
        temperature: float = 0.7,
        system_prompt: str = '',
        max_tokens: int = 8192,
        use_vertex: bool = False,
        project_id: Optional[str] = None,
        location: str = 'us-central1'
    ):
        """
        Initialize Google provider
        
        Args:
            api_key: Google API key (for Gemini API)
            model: Model name
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            use_vertex: Use Vertex AI instead of Gemini API
            project_id: GCP project ID (for Vertex AI)
            location: GCP region (for Vertex AI)
        """
        super().__init__(api_key, model, temperature, system_prompt)
        self.max_tokens = max_tokens
        self.use_vertex = use_vertex
        self.project_id = project_id
        self.location = location
        self.supports_streaming = True
        
        # Initialize appropriate SDK
        if self.use_vertex:
            if not VERTEXAI_AVAILABLE:
                raise ImportError(
                    "Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform"
                )
            vertexai.init(project=project_id, location=location)
            self.client = GenerativeModel(model)
        else:
            if not GENAI_AVAILABLE:
                raise ImportError(
                    "Google Generative AI SDK not installed. Install with: pip install google-generativeai"
                )
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
    
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
                # Google doesn't have system role, prepend to first user message
                # We'll handle this in the generation config
                continue
            
            formatted.append({
                'role': role,
                'parts': [content]
            })
        
        return formatted
    
    def _create_generation_config(self) -> Dict:
        """Create generation configuration"""
        config = {
            'temperature': self.temperature,
            'max_output_tokens': self.max_tokens,
        }
        
        if self.use_vertex:
            return VertexGenerationConfig(**config)
        else:
            return GenerationConfig(**config)
    
    def generate_response(self, messages: List[Dict]) -> str:
        """
        Generate a non-streaming response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        
        Returns:
            Generated response text
        """
        try:
            formatted_messages = self._format_messages(messages)
            generation_config = self._create_generation_config()
            
            # Build the conversation history
            chat = self.client.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            # Add system prompt if provided
            if self.system_prompt:
                # Prepend system prompt to the user message
                last_message = formatted_messages[-1]['parts'][0]
                formatted_messages[-1]['parts'][0] = f"{self.system_prompt}\n\n{last_message}"
            
            # Generate response
            response = chat.send_message(
                formatted_messages[-1]['parts'][0],
                generation_config=generation_config
            )
            
            return response.text
        
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
            formatted_messages = self._format_messages(messages)
            generation_config = self._create_generation_config()
            
            # Build the conversation history
            chat = self.client.start_chat(history=formatted_messages[:-1] if len(formatted_messages) > 1 else [])
            
            # Add system prompt if provided
            if self.system_prompt:
                last_message = formatted_messages[-1]['parts'][0]
                formatted_messages[-1]['parts'][0] = f"{self.system_prompt}\n\n{last_message}"
            
            # Stream response
            response = chat.send_message(
                formatted_messages[-1]['parts'][0],
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        except Exception as e:
            raise Exception(f"Google API streaming error: {str(e)}")
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """Return list of available Google models"""
        return [
            {
                'id': 'gemini-1.5-pro',
                'name': 'Gemini 1.5 Pro',
                'description': 'Most capable model, 1M token context',
                'context_window': 1000000
            },
            {
                'id': 'gemini-1.5-flash',
                'name': 'Gemini 1.5 Flash',
                'description': 'Fast and efficient, 1M token context',
                'context_window': 1000000
            },
            {
                'id': 'gemini-pro',
                'name': 'Gemini Pro',
                'description': 'Balanced performance and speed',
                'context_window': 32000
            },
            {
                'id': 'gemini-pro-vision',
                'name': 'Gemini Pro Vision',
                'description': 'Multimodal model with vision capabilities',
                'context_window': 16000
            },
        ]

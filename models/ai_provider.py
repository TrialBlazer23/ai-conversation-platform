"""
AI Provider factory with enhanced provider support
"""
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.ollama_provider import OllamaProvider
from providers.gemini_provider import GeminiProvider
from providers.vertex_ai_provider import VertexAIProvider


class AIProviderFactory:
    """
    Factory for creating AI provider instances
    Enhanced with local model support
    """

    @staticmethod
    def create_provider(
        provider_type: str,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        system_prompt: str = '',
    ):
        """
        Create an AI provider instance

        Args:
            provider_type: Type of provider ('openai', 'anthropic', 'ollama', 'gemini', 'vertex_ai')
            api_key: API key for the provider
            model: Model identifier
            temperature: Sampling temperature
            system_prompt: System instructions for the model

        Returns:
            Provider instance
        """
        provider_type = provider_type.lower()

        if provider_type == 'openai':
            return OpenAIProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
            )
        if provider_type == 'anthropic':
            return AnthropicProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
            )
        if provider_type == 'ollama':
            return OllamaProvider(
                api_key=api_key,  # Not used, but maintains interface
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
            )
        if provider_type == 'gemini':
            return GeminiProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
            )
        if provider_type == 'vertex_ai':
            return VertexAIProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
            )
        raise ValueError(f"Unknown provider type: {provider_type}")

    @staticmethod
    def get_available_providers():
        """
        Get list of available providers with their models

        Returns:
            List of provider configurations
        """
        providers = [
            {
                'id': 'openai',
                'name': 'OpenAI',
                'requires_api_key': True,
                'supports_streaming': True,
                'models': [
                    'gpt-4',
                    'gpt-4-turbo',
                    'gpt-4-turbo-preview',
                    'gpt-3.5-turbo',
                    'gpt-3.5-turbo-16k',
                ],
            },
            {
                'id': 'anthropic',
                'name': 'Anthropic',
                'requires_api_key': True,
                'supports_streaming': True,
                'models': [
                    'claude-3-opus-20240229',
                    'claude-3-sonnet-20240229',
                    'claude-3-haiku-20240307',
                    'claude-2.1',
                    'claude-2.0',
                ],
            },
            {
                'id': 'gemini',
                'name': 'Google Gemini',
                'requires_api_key': True,
                'supports_streaming': True,
                'models': [
                    'gemini-pro',
                    'gemini-pro-vision',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash',
                ],
            },
            {
                'id': 'vertex_ai',
                'name': 'Google Vertex AI',
                'requires_api_key': True,
                'supports_streaming': True,
                'models': [
                    'gemini-pro',
                    'gemini-pro-vision',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash',
                ],
            },
            {
                'id': 'ollama',
                'name': 'Ollama (Local)',
                'requires_api_key': False,
                'supports_streaming': True,
                'models': OllamaProvider.list_available_models()
                or [
                    'llama2',
                    'mistral',
                    'codellama',
                    'neural-chat',
                    'phi',
                ],
            },
        ]

        return providers
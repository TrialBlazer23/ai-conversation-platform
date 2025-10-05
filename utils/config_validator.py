"""
Configuration validator for API keys and model settings
"""
from typing import Dict, List, Tuple
import requests
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.google_provider import GoogleProvider


class ConfigValidator:
    """Validate API keys and configurations before use"""
    
    @staticmethod
    def validate_openai_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate OpenAI API key
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key or not api_key.startswith('sk-'):
            return False, "Invalid OpenAI API key format. Should start with 'sk-'"
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Quick validation - list models
            client.models.list()
            return True, "OpenAI API key is valid"
        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg or 'Unauthorized' in error_msg:
                return False, "Invalid OpenAI API key. Please check your key."
            elif '429' in error_msg:
                return False, "Rate limit reached. API key might be valid but service is busy."
            else:
                return False, f"OpenAI validation error: {error_msg}"
    
    @staticmethod
    def validate_anthropic_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate Anthropic API key
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key or not api_key.startswith('sk-ant-'):
            return False, "Invalid Anthropic API key format. Should start with 'sk-ant-'"
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Quick validation - make minimal API call
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True, "Anthropic API key is valid"
        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg or 'authentication' in error_msg.lower():
                return False, "Invalid Anthropic API key. Please check your key."
            elif '429' in error_msg:
                return False, "Rate limit reached. API key might be valid but service is busy."
            else:
                return False, f"Anthropic validation error: {error_msg}"
    
    @staticmethod
    def validate_google_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate Google API key
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key:
            return False, "Google API key is required"
        
        try:
            # Test with a simple API call
            url = "https://generativelanguage.googleapis.com/v1beta/models"
            headers = {'x-goog-api-key': api_key}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, "Google API key is valid"
            elif response.status_code == 401 or response.status_code == 403:
                return False, "Invalid Google API key. Please check your key."
            else:
                return False, f"Google validation error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Google validation error: {str(e)}"
    
    @staticmethod
    def validate_model_config(model_config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a model configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not model_config.get('provider'):
            errors.append("Provider is required")
        
        if not model_config.get('model'):
            errors.append("Model name is required")
        
        # Validate temperature
        temp = model_config.get('temperature', 0.7)
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            errors.append("Temperature must be between 0 and 2")
        
        # Validate provider-specific requirements
        provider = model_config.get('provider', '').lower()
        valid_providers = ['openai', 'anthropic', 'google', 'ollama']
        
        if provider not in valid_providers:
            errors.append(f"Invalid provider. Must be one of: {', '.join(valid_providers)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_all_configs(api_keys: Dict, models: List[Dict]) -> Dict:
        """
        Validate entire configuration
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'api_keys': {},
            'models': [],
            'errors': []
        }
        
        # Validate API keys
        if api_keys.get('openai'):
            valid, msg = ConfigValidator.validate_openai_key(api_keys['openai'])
            results['api_keys']['openai'] = {'valid': valid, 'message': msg}
            if not valid:
                results['valid'] = False
        
        if api_keys.get('anthropic'):
            valid, msg = ConfigValidator.validate_anthropic_key(api_keys['anthropic'])
            results['api_keys']['anthropic'] = {'valid': valid, 'message': msg}
            if not valid:
                results['valid'] = False
        
        if api_keys.get('google'):
            valid, msg = ConfigValidator.validate_google_key(api_keys['google'])
            results['api_keys']['google'] = {'valid': valid, 'message': msg}
            if not valid:
                results['valid'] = False
        
        # Validate model configs
        for i, model_config in enumerate(models):
            valid, errors = ConfigValidator.validate_model_config(model_config)
            results['models'].append({
                'index': i,
                'valid': valid,
                'errors': errors
            })
            if not valid:
                results['valid'] = False
                results['errors'].extend([f"Model {i + 1}: {e}" for e in errors])
        
        # Check if at least one model is configured
        if len(models) == 0:
            results['valid'] = False
            results['errors'].append("At least one model must be configured")
        
        # Check if necessary API keys are provided for models
        required_keys = set()
        for model in models:
            provider = model.get('provider', '').lower()
            if provider in ['openai', 'anthropic', 'google']:
                required_keys.add(provider)
        
        for provider in required_keys:
            if not api_keys.get(provider):
                results['valid'] = False
                results['errors'].append(f"API key required for {provider}")
        
        return results
    
    @staticmethod
    def check_ollama_connection() -> Tuple[bool, str]:
        """
        Check if Ollama is running and accessible
        
        Returns:
            Tuple of (is_available, message)
        """
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return True, f"Ollama is running with {len(models)} model(s)"
            else:
                return False, "Ollama is running but returned an error"
        except requests.exceptions.ConnectionError:
            return False, "Ollama is not running. Start it with 'ollama serve'"
        except requests.exceptions.Timeout:
            return False, "Ollama connection timed out"
        except Exception as e:
            return False, f"Ollama check failed: {str(e)}"

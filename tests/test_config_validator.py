"""
Tests for configuration validator utility
"""
import pytest
from unittest.mock import Mock, patch
from utils.config_validator import ConfigValidator


class TestConfigValidator:
    """Test ConfigValidator class"""

    @patch('openai.OpenAI')
    def test_validate_openai_key_success(self, mock_openai_class):
        """Test successful OpenAI key validation"""
        mock_client = Mock()
        mock_client.models.list.return_value = []
        mock_openai_class.return_value = mock_client

        is_valid, message = ConfigValidator.validate_openai_key("sk-test-key")

        assert is_valid is True
        assert "is valid" in message
        mock_openai_class.assert_called_once_with(api_key="sk-test-key")

    @patch('openai.OpenAI', side_effect=Exception("Invalid API key"))
    def test_validate_openai_key_failure(self, mock_openai_class):
        """Test failed OpenAI key validation"""
        is_valid, message = ConfigValidator.validate_openai_key("invalid-key")

        assert is_valid is False
        assert "Invalid OpenAI API key format" in message

    @patch('anthropic.Anthropic')
    def test_validate_anthropic_key_success(self, mock_anthropic_class):
        """Test successful Anthropic key validation"""
        mock_client = Mock()
        mock_client.messages.create.return_value = Mock()
        mock_anthropic_class.return_value = mock_client

        is_valid, message = ConfigValidator.validate_anthropic_key("sk-ant-test-key")

        assert is_valid is True
        assert "is valid" in message

    @patch('anthropic.Anthropic', side_effect=Exception("Invalid API key"))
    def test_validate_anthropic_key_failure(self, mock_anthropic_class):
        """Test failed Anthropic key validation"""
        is_valid, message = ConfigValidator.validate_anthropic_key("invalid-key")

        assert is_valid is False
        assert "Invalid Anthropic API key format" in message

    @patch('utils.config_validator.requests.get')
    def test_validate_google_key_success(self, mock_get):
        """Test successful Google key validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        is_valid, message = ConfigValidator.validate_google_key("test-key")

        assert is_valid is True
        assert "is valid" in message

    @patch('utils.config_validator.requests.get')
    def test_validate_google_key_failure(self, mock_get):
        """Test failed Google key validation"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        is_valid, message = ConfigValidator.validate_google_key("invalid-key")

        assert is_valid is False
        assert "Invalid Google API key" in message

    @patch('utils.config_validator.requests.get')
    def test_check_ollama_connection_success(self, mock_get):
        """Test successful Ollama connection check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'models': []}
        mock_get.return_value = mock_response

        is_valid, message = ConfigValidator.check_ollama_connection()

        assert is_valid is True
        assert "Ollama is running" in message

    @patch('utils.config_validator.requests.get', side_effect=Exception("Connection refused"))
    def test_check_ollama_connection_failure(self, mock_get):
        """Test failed Ollama connection check"""
        is_valid, message = ConfigValidator.check_ollama_connection()

        assert is_valid is False
        assert "Ollama check failed" in message

    @patch('utils.config_validator.ConfigValidator.validate_openai_key', return_value=(True, "valid"))
    @patch('utils.config_validator.ConfigValidator.validate_anthropic_key', return_value=(True, "valid"))
    @patch('utils.config_validator.ConfigValidator.validate_google_key', return_value=(True, "valid"))
    def test_validate_all_configs_success(self, mock_google, mock_anthropic, mock_openai):
        """Test validation of all configurations"""
        api_keys = {
            'openai': 'test-key',
            'anthropic': 'test-key',
            'google': 'test-key',
        }
        models = [
            {'provider': 'openai', 'model': 'gpt-4'},
            {'provider': 'anthropic', 'model': 'claude-3'},
            {'provider': 'google', 'model': 'gemini-pro'},
        ]
        
        result = ConfigValidator.validate_all_configs(api_keys, models)

        assert result['valid'] is True
        assert result['api_keys']['openai']['valid'] is True
        assert result['api_keys']['anthropic']['valid'] is True
        assert result['api_keys']['google']['valid'] is True
        assert all(m['valid'] for m in result['models'])

    @patch('utils.config_validator.ConfigValidator.validate_openai_key', return_value=(False, "Invalid key"))
    def test_validate_all_configs_partial_failure(self, mock_openai):
        """Test validation with some failures"""
        api_keys = {'openai': 'invalid-key'}
        models = [{'provider': 'openai', 'model': 'gpt-4'}]
        
        result = ConfigValidator.validate_all_configs(api_keys, models)
        
        assert result['valid'] is False
        assert result['api_keys']['openai']['valid'] is False

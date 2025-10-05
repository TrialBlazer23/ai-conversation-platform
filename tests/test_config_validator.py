"""
Tests for configuration validator utility
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.config_validator import ConfigValidator


class TestConfigValidator:
    """Test ConfigValidator class"""
    
    @patch('utils.config_validator.openai.OpenAI')
    def test_validate_openai_key_success(self, mock_openai):
        """Test successful OpenAI key validation"""
        mock_client = Mock()
        mock_client.models.list.return_value = Mock()
        mock_openai.return_value = mock_client
        
        result = ConfigValidator.validate_openai_key("test-key")
        
        assert result['valid'] is True
        assert 'error' not in result
        mock_openai.assert_called_once_with(api_key="test-key")
    
    @patch('utils.config_validator.openai.OpenAI')
    def test_validate_openai_key_failure(self, mock_openai):
        """Test failed OpenAI key validation"""
        mock_openai.side_effect = Exception("Invalid API key")
        
        result = ConfigValidator.validate_openai_key("invalid-key")
        
        assert result['valid'] is False
        assert 'error' in result
        assert 'Invalid API key' in result['error']
    
    @patch('utils.config_validator.anthropic.Anthropic')
    def test_validate_anthropic_key_success(self, mock_anthropic):
        """Test successful Anthropic key validation"""
        mock_client = Mock()
        mock_client.messages.create.return_value = Mock()
        mock_anthropic.return_value = mock_client
        
        result = ConfigValidator.validate_anthropic_key("test-key")
        
        assert result['valid'] is True
        assert 'error' not in result
    
    @patch('utils.config_validator.anthropic.Anthropic')
    def test_validate_anthropic_key_failure(self, mock_anthropic):
        """Test failed Anthropic key validation"""
        mock_anthropic.side_effect = Exception("Invalid API key")
        
        result = ConfigValidator.validate_anthropic_key("invalid-key")
        
        assert result['valid'] is False
        assert 'error' in result
    
    @patch('utils.config_validator.requests.post')
    def test_validate_google_key_success(self, mock_post):
        """Test successful Google key validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'candidates': []}
        mock_post.return_value = mock_response
        
        result = ConfigValidator.validate_google_key("test-key")
        
        assert result['valid'] is True
        assert 'error' not in result
    
    @patch('utils.config_validator.requests.post')
    def test_validate_google_key_failure(self, mock_post):
        """Test failed Google key validation"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        result = ConfigValidator.validate_google_key("invalid-key")
        
        assert result['valid'] is False
        assert 'error' in result
    
    @patch('utils.config_validator.requests.get')
    def test_check_ollama_connection_success(self, mock_get):
        """Test successful Ollama connection check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = ConfigValidator.check_ollama_connection("http://localhost:11434")
        
        assert result['valid'] is True
        assert 'error' not in result
    
    @patch('utils.config_validator.requests.get')
    def test_check_ollama_connection_failure(self, mock_get):
        """Test failed Ollama connection check"""
        mock_get.side_effect = Exception("Connection refused")
        
        result = ConfigValidator.check_ollama_connection("http://localhost:11434")
        
        assert result['valid'] is False
        assert 'error' in result
    
    @patch('utils.config_validator.ConfigValidator.validate_openai_key')
    @patch('utils.config_validator.ConfigValidator.validate_anthropic_key')
    @patch('utils.config_validator.ConfigValidator.validate_google_key')
    @patch('utils.config_validator.ConfigValidator.check_ollama_connection')
    def test_validate_all_configs_success(self, mock_ollama, mock_google, mock_anthropic, mock_openai):
        """Test validation of all configurations"""
        mock_openai.return_value = {'valid': True}
        mock_anthropic.return_value = {'valid': True}
        mock_google.return_value = {'valid': True}
        mock_ollama.return_value = {'valid': True}
        
        config = {
            'openai_api_key': 'test-key',
            'anthropic_api_key': 'test-key',
            'google_api_key': 'test-key',
            'ollama_base_url': 'http://localhost:11434'
        }
        
        result = ConfigValidator.validate_all_configs(config)
        
        assert result['openai']['valid'] is True
        assert result['anthropic']['valid'] is True
        assert result['google']['valid'] is True
        assert result['ollama']['valid'] is True
    
    @patch('utils.config_validator.ConfigValidator.validate_openai_key')
    def test_validate_all_configs_partial_failure(self, mock_openai):
        """Test validation with some failures"""
        mock_openai.return_value = {'valid': False, 'error': 'Invalid key'}
        
        config = {
            'openai_api_key': 'invalid-key'
        }
        
        result = ConfigValidator.validate_all_configs(config)
        
        assert result['openai']['valid'] is False
        assert 'error' in result['openai']

"""
Tests for Flask API endpoints
"""
import pytest
import json
from unittest.mock import Mock, patch


class TestConfigEndpoints:
    """Test configuration-related endpoints"""
    
    def test_get_config_empty(self, client):
        """Test getting empty configuration"""
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == {}
    
    def test_save_config(self, client):
        """Test saving configuration"""
        config = {
            'api_keys': {'openai': 'test-key'},
            'models': [{
                'provider': 'openai',
                'model': 'gpt-4',
                'name': 'Assistant'
            }]
        }
        
        response = client.post('/api/config',
                               data=json.dumps(config),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Verify it was saved
        response = client.get('/api/config')
        data = json.loads(response.data)
        assert data['api_keys']['openai'] == 'test-key'
    
    @patch('utils.config_validator.ConfigValidator.validate_all_configs')
    def test_validate_config_endpoint(self, mock_validate, client):
        """Test configuration validation endpoint"""
        mock_validate.return_value = {
            'valid': False,
            'api_keys': {
                'openai': {'valid': True, 'message': 'valid'},
                'anthropic': {'valid': False, 'message': 'Invalid key'}
            },
            'models': []
        }
        
        config = {
            'api_keys': {
                'openai': 'test-key',
                'anthropic': 'invalid-key'
            },
            'models': []
        }
        
        response = client.post('/api/config/validate',
                               data=json.dumps(config),
                               content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['api_keys']['openai']['valid'] is True
        assert data['api_keys']['anthropic']['valid'] is False


class TestConversationEndpoints:
    """Test conversation-related endpoints"""
    
    def test_list_conversations_empty(self, client):
        """Test listing conversations when none exist"""
        response = client.get('/api/conversations')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert isinstance(data['conversations'], list)
        assert len(data['conversations']) == 0
    
    def test_create_conversation(self, client):
        """Test creating a new conversation"""
        conv_data = {
            'initial_prompt': 'Test prompt',
            'models': [{
                'provider': 'openai',
                'model': 'gpt-4',
                'name': 'Assistant'
            }]
        }
        
        response = client.post('/api/conversation/start',
                               data=json.dumps(conv_data),
                               content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'conversation_id' in data
    
    @patch('openai.OpenAI')
    def test_send_message(self, mock_openai_class, client):
        """Test sending a message"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create conversation
        conv_data = {
            'initial_prompt': 'Test prompt',
            'models': [{
                'provider': 'openai',
                'model': 'gpt-4',
                'name': 'Assistant'
            }]
        }
        response = client.post('/api/conversation/start',
                               data=json.dumps(conv_data),
                               content_type='application/json')
        conversation_id = json.loads(response.data)['conversation_id']
        
        # Send message (non-streaming for test)
        message_data = {
            'edited_message': 'Hello',
        }
        
        response = client.post(f'/api/conversation/{conversation_id}/next',
                               data=json.dumps(message_data),
                               content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message']['content'] == 'Test response'


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test that health check returns OK"""
        response = client.get('/')
        assert response.status_code == 200
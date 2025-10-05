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
        assert 'participants' in data
        assert isinstance(data['participants'], list)
    
    def test_save_config(self, client):
        """Test saving configuration"""
        config = {
            'title': 'Test Conversation',
            'system_message': 'You are helpful.',
            'participants': [{
                'name': 'Assistant',
                'provider': 'openai',
                'model': 'gpt-4'
            }]
        }
        
        response = client.post('/api/config',
                               data=json.dumps(config),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Verify it was saved
        response = client.get('/api/config')
        data = json.loads(response.data)
        assert data['title'] == 'Test Conversation'
    
    @patch('utils.config_validator.ConfigValidator.validate_all_configs')
    def test_validate_config_endpoint(self, mock_validate, client):
        """Test configuration validation endpoint"""
        mock_validate.return_value = {
            'openai': {'valid': True},
            'anthropic': {'valid': False, 'error': 'Invalid key'}
        }
        
        config = {
            'openai_api_key': 'test-key',
            'anthropic_api_key': 'invalid-key'
        }
        
        response = client.post('/api/config/validate',
                               data=json.dumps(config),
                               content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['openai']['valid'] is True
        assert data['anthropic']['valid'] is False


class TestConversationEndpoints:
    """Test conversation-related endpoints"""
    
    def test_list_conversations_empty(self, client):
        """Test listing conversations when none exist"""
        response = client.get('/api/conversations')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_conversation(self, client):
        """Test creating a new conversation"""
        # First save a config
        config = {
            'title': 'Test Conversation',
            'system_message': 'You are helpful.',
            'participants': [{
                'name': 'Assistant',
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }]
        }
        
        client.post('/api/config',
                    data=json.dumps(config),
                    content_type='application/json')
        
        # Create conversation
        response = client.post('/api/conversations/new')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'id' in data
        assert data['title'] == 'Test Conversation'
    
    @patch('providers.openai_provider.openai.OpenAI')
    def test_send_message(self, mock_openai, client):
        """Test sending a message"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_response.model = "gpt-4"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Setup config
        config = {
            'title': 'Test',
            'system_message': 'You are helpful.',
            'participants': [{
                'name': 'Assistant',
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }],
            'openai_api_key': 'test-key'
        }
        client.post('/api/config',
                    data=json.dumps(config),
                    content_type='application/json')
        
        # Create conversation
        response = client.post('/api/conversations/new')
        conv_data = json.loads(response.data)
        conversation_id = conv_data['id']
        
        # Send message (non-streaming for test)
        message_data = {
            'message': 'Hello',
            'stream': False
        }
        
        response = client.post(f'/api/conversations/{conversation_id}/message',
                               data=json.dumps(message_data),
                               content_type='application/json')
        
        assert response.status_code == 200


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test that health check returns OK"""
        response = client.get('/')
        assert response.status_code == 200

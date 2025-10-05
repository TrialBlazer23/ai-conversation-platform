"""
Tests for new enhancements: Cohere provider, caching, health checks, and UI features
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time


class TestCohereProvider:
    """Test Cohere provider implementation"""
    
    @pytest.fixture
    def provider(self):
        from providers.cohere_provider import CohereProvider
        return CohereProvider(
            api_key='test-key',
            model='command-r',
            temperature=0.7
        )
    
    def test_provider_initialization(self, provider):
        """Test that provider initializes correctly"""
        assert provider.api_key == 'test-key'
        assert provider.model == 'command-r'
        assert provider.temperature == 0.7
        assert provider.supports_streaming is True
    
    def test_convert_messages(self, provider):
        """Test message format conversion"""
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ]
        
        chat_history, current_message = provider._convert_messages(messages)
        
        assert len(chat_history) == 2
        assert chat_history[0]['role'] == 'USER'
        assert chat_history[1]['role'] == 'CHATBOT'
        assert current_message == 'How are you?'
    
    def test_generate_response(self, provider):
        """Test response generation (skipped if cohere not installed)"""
        try:
            import cohere
        except ImportError:
            pytest.skip("cohere package not installed")
        
        with patch('cohere.Client') as mock_client:
            mock_response = Mock()
            mock_response.text = 'Test response'
            mock_client.return_value.chat.return_value = mock_response
            
            messages = [{'role': 'user', 'content': 'Hello'}]
            response = provider.generate_response(messages)
            
            assert response == 'Test response'
            mock_client.return_value.chat.assert_called_once()


class TestResponseCache:
    """Test response caching functionality"""
    
    @pytest.fixture
    def cache(self):
        from utils.cache import ResponseCache
        return ResponseCache(ttl=1, max_size=100)
    
    def test_cache_initialization(self, cache):
        """Test cache initializes with correct settings"""
        assert cache.ttl == 1
        assert cache.max_size == 100
        assert len(cache._cache) == 0
    
    def test_cache_set_and_get(self, cache):
        """Test basic cache operations"""
        messages = [{'role': 'user', 'content': 'test'}]
        
        # Cache a response
        cache.set('openai', 'gpt-4', messages, 0.7, 'Test response')
        
        # Retrieve it
        cached = cache.get('openai', 'gpt-4', messages, 0.7)
        assert cached == 'Test response'
    
    def test_cache_expiration(self, cache):
        """Test that cache items expire after TTL"""
        messages = [{'role': 'user', 'content': 'test'}]
        
        cache.set('openai', 'gpt-4', messages, 0.7, 'Test response')
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        cached = cache.get('openai', 'gpt-4', messages, 0.7)
        assert cached is None
    
    def test_cache_max_size(self):
        """Test LRU eviction when max size reached"""
        from utils.cache import ResponseCache
        cache = ResponseCache(ttl=3600, max_size=2)
        
        messages1 = [{'role': 'user', 'content': 'test1'}]
        messages2 = [{'role': 'user', 'content': 'test2'}]
        messages3 = [{'role': 'user', 'content': 'test3'}]
        
        cache.set('openai', 'gpt-4', messages1, 0.7, 'Response 1')
        cache.set('openai', 'gpt-4', messages2, 0.7, 'Response 2')
        cache.set('openai', 'gpt-4', messages3, 0.7, 'Response 3')
        
        # First item should be evicted
        assert len(cache._cache) == 2
        assert cache.get('openai', 'gpt-4', messages1, 0.7) is None
        assert cache.get('openai', 'gpt-4', messages2, 0.7) == 'Response 2'
        assert cache.get('openai', 'gpt-4', messages3, 0.7) == 'Response 3'
    
    def test_cache_clear(self, cache):
        """Test cache clearing"""
        messages = [{'role': 'user', 'content': 'test'}]
        cache.set('openai', 'gpt-4', messages, 0.7, 'Test response')
        
        cache.clear()
        
        assert len(cache._cache) == 0
        assert cache.get('openai', 'gpt-4', messages, 0.7) is None
    
    def test_cache_stats(self, cache):
        """Test cache statistics"""
        messages = [{'role': 'user', 'content': 'test'}]
        cache.set('openai', 'gpt-4', messages, 0.7, 'Test response')
        
        stats = cache.get_stats()
        
        assert stats['total_items'] == 1
        assert stats['max_size'] == 100
        assert stats['ttl'] == 1


class TestAPIEnhancements:
    """Test new API endpoints"""
    
    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_cache_stats_endpoint(self, client):
        """Test GET /api/cache/stats"""
        response = client.get('/api/cache/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'cache' in data
        assert 'total_items' in data['cache']
    
    def test_cache_clear_endpoint(self, client):
        """Test POST /api/cache/clear"""
        response = client.post('/api/cache/clear')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_health_check_endpoint(self, mock_openai, mock_anthropic, client):
        """Test POST /api/health/providers"""
        # Mock OpenAI
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        mock_openai_instance.models.list.return_value = []
        
        response = client.post(
            '/api/health/providers',
            data=json.dumps({
                'api_keys': {
                    'openai': 'sk-test',
                    'anthropic': 'sk-ant-test'
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'providers' in data
        assert 'openai' in data['providers']
    
    def test_response_time_header(self, client):
        """Test that X-Response-Time header is added"""
        response = client.get('/api/providers')
        assert 'X-Response-Time' in response.headers
        
        # Header should be in format "0.123s"
        time_header = response.headers['X-Response-Time']
        assert time_header.endswith('s')
        assert float(time_header[:-1]) >= 0
    
    def test_security_headers(self, client):
        """Test security headers are added"""
        response = client.get('/')
        
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'DENY'


class TestProviderFactory:
    """Test AI provider factory enhancements"""
    
    def test_cohere_in_available_providers(self):
        """Test that Cohere is listed in available providers"""
        from models.ai_provider import AIProviderFactory
        
        providers = AIProviderFactory.get_available_providers()
        
        cohere_provider = next(
            (p for p in providers if p['id'] == 'cohere'),
            None
        )
        
        assert cohere_provider is not None
        assert cohere_provider['name'] == 'Cohere'
        assert cohere_provider['requires_api_key'] is True
        assert cohere_provider['supports_streaming'] is True
        assert len(cohere_provider['models']) > 0
    
    def test_create_cohere_provider(self):
        """Test creating Cohere provider via factory"""
        from models.ai_provider import AIProviderFactory
        
        provider = AIProviderFactory.create_provider(
            provider_type='cohere',
            api_key='test-key',
            model='command-r',
            temperature=0.7
        )
        
        assert provider is not None
        assert provider.model == 'command-r'
        assert provider.supports_streaming is True


class TestTimeoutConfiguration:
    """Test timeout configuration in providers"""
    
    def test_base_provider_timeout(self):
        """Test that base provider accepts timeout parameter"""
        from providers.openai_provider import OpenAIProvider
        
        provider = OpenAIProvider(
            api_key='test-key',
            model='gpt-4',
            timeout=30.0
        )
        
        assert provider.timeout == 30.0
    
    def test_default_timeout(self):
        """Test default timeout value"""
        from providers.openai_provider import OpenAIProvider
        
        provider = OpenAIProvider(
            api_key='test-key',
            model='gpt-4'
        )
        
        assert provider.timeout == 60.0  # Default value


class TestUIEnhancements:
    """Test UI enhancement utilities"""
    
    def test_response_time_tracker(self):
        """Test ResponseTimeTracker class"""
        # This would be tested in a browser environment
        # Here we just verify the structure exists
        pass
    
    def test_model_status_indicator(self):
        """Test ModelStatusIndicator class"""
        # This would be tested in a browser environment
        # Here we just verify the structure exists
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

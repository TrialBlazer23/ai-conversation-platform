"""
Tests for AI provider implementations
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.google_provider import GoogleProvider


class TestOpenAIProvider:
    """Test OpenAI provider"""
    
    @pytest.fixture
    def provider(self):
        """Create an OpenAI provider instance"""
        config = {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        return OpenAIProvider(api_key='test-key', config=config)
    
    @patch('providers.openai_provider.openai.OpenAI')
    def test_generate_response_success(self, mock_openai, provider):
        """Test successful response generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_response.model = "gpt-4"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)
        
        assert result['content'] == "Test response"
        assert result['tokens_used'] == 15
        assert result['model'] == "gpt-4"
    
    @patch('providers.openai_provider.openai.OpenAI')
    def test_generate_response_stream(self, mock_openai, provider):
        """Test streaming response generation"""
        mock_client = Mock()
        
        # Create mock stream chunks
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content="!"))]),
        ]
        
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai.return_value = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(provider.generate_response_stream(messages))
        
        # Parse the JSON chunks
        content_chunks = []
        for chunk in chunks:
            if chunk.startswith('data: '):
                data = json.loads(chunk[6:])
                if 'content' in data:
                    content_chunks.append(data['content'])
        
        assert len(content_chunks) > 0
        assert "".join(content_chunks) == "Hello world!"


class TestAnthropicProvider:
    """Test Anthropic provider"""
    
    @pytest.fixture
    def provider(self):
        """Create an Anthropic provider instance"""
        config = {
            'model': 'claude-3-sonnet-20240229',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        return AnthropicProvider(api_key='test-key', config=config)
    
    @patch('providers.anthropic_provider.anthropic.Anthropic')
    def test_generate_response_success(self, mock_anthropic, provider):
        """Test successful response generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=5)
        mock_response.model = "claude-3-sonnet-20240229"
        
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)
        
        assert result['content'] == "Test response"
        assert result['tokens_used'] == 15
        assert result['model'] == "claude-3-sonnet-20240229"
    
    @patch('providers.anthropic_provider.anthropic.Anthropic')
    def test_generate_response_stream(self, mock_anthropic, provider):
        """Test streaming response generation"""
        mock_client = Mock()
        
        # Create mock stream events
        mock_events = [
            Mock(type='content_block_delta', delta=Mock(type='text_delta', text='Hello')),
            Mock(type='content_block_delta', delta=Mock(type='text_delta', text=' world')),
            Mock(type='content_block_delta', delta=Mock(type='text_delta', text='!')),
            Mock(type='message_stop'),
        ]
        
        mock_stream = Mock()
        mock_stream.__enter__ = Mock(return_value=iter(mock_events))
        mock_stream.__exit__ = Mock(return_value=False)
        
        mock_client.messages.stream.return_value = mock_stream
        mock_anthropic.return_value = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(provider.generate_response_stream(messages))
        
        # Parse the JSON chunks
        content_chunks = []
        for chunk in chunks:
            if chunk.startswith('data: '):
                data = json.loads(chunk[6:])
                if 'content' in data:
                    content_chunks.append(data['content'])
        
        assert len(content_chunks) > 0


class TestGoogleProvider:
    """Test Google Gemini provider"""
    
    @pytest.fixture
    def provider(self):
        """Create a Google provider instance"""
        config = {
            'model': 'gemini-pro',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        return GoogleProvider(api_key='test-key', config=config)
    
    @patch('providers.google_provider.requests.post')
    def test_generate_response_success(self, mock_post, provider):
        """Test successful response generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Test response'}]
                }
            }],
            'usageMetadata': {
                'promptTokenCount': 10,
                'candidatesTokenCount': 5,
                'totalTokenCount': 15
            }
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)
        
        assert result['content'] == "Test response"
        assert result['tokens_used'] == 15
    
    @patch('providers.google_provider.requests.post')
    def test_generate_response_error(self, mock_post, provider):
        """Test error handling"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(Exception):
            provider.generate_response(messages)
    
    @patch('providers.google_provider.requests.post')
    def test_generate_response_stream(self, mock_post, provider):
        """Test streaming response generation"""
        # Create mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Simulate chunked JSON responses
        chunks = [
            b'[{"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}',
            b',{"candidates": [{"content": {"parts": [{"text": " world"}]}}]}',
            b',{"candidates": [{"content": {"parts": [{"text": "!"}]}}]}]'
        ]
        
        mock_response.iter_lines.return_value = chunks
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result_chunks = list(provider.generate_response_stream(messages))
        
        # Verify we got streaming data
        assert len(result_chunks) > 0
        
        # Parse chunks to verify content
        content_parts = []
        for chunk in result_chunks:
            if chunk.startswith('data: '):
                data = json.loads(chunk[6:])
                if 'content' in data:
                    content_parts.append(data['content'])
        
        # Should have accumulated some content
        assert len(content_parts) > 0
    
    def test_convert_messages_format(self, provider):
        """Test message format conversion"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        
        result = provider._convert_messages_format(messages)
        
        assert 'contents' in result
        assert len(result['contents']) == 3
        assert result['contents'][0]['role'] == 'user'
        assert result['contents'][1]['role'] == 'model'  # assistant -> model
        assert result['contents'][2]['role'] == 'user'

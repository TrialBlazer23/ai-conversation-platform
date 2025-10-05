"""
Tests for AI provider implementations
"""
import pytest
import json
import requests
from unittest.mock import Mock, patch, MagicMock
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.google_provider import GoogleProvider


class TestOpenAIProvider:
    """Test OpenAI provider"""
    
    @pytest.fixture
    def provider(self):
        """Create an OpenAI provider instance"""
        return OpenAIProvider(
            api_key='test-key',
            model='gpt-4',
            temperature=0.7
        )
    
    @patch('openai.OpenAI')
    def test_generate_response_success(self, mock_openai_class, provider):
        """Test successful response generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)

        assert result == "Test response"

    @patch('openai.OpenAI')
    def test_generate_response_stream(self, mock_openai_class, provider):
        """Test streaming response generation"""
        mock_client = Mock()

        # Create mock stream chunks
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content="!"))]),
            Mock(choices=[Mock(delta=Mock(content=None))]),
        ]

        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai_class.return_value = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(provider.generate_response_stream(messages))

        assert chunks == ["Hello", " world", "!"]


class TestAnthropicProvider:
    """Test Anthropic provider"""
    
    @pytest.fixture
    def provider(self):
        """Create an Anthropic provider instance"""
        return AnthropicProvider(
            api_key='test-key',
            model='claude-3-sonnet-20240229',
            temperature=0.7
        )
    
    @patch('anthropic.Anthropic')
    def test_generate_response_success(self, mock_anthropic_class, provider):
        """Test successful response generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]

        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)

        assert result == "Test response"

    @patch('anthropic.Anthropic')
    def test_generate_response_stream(self, mock_anthropic_class, provider):
        """Test streaming response generation"""
        mock_client = MagicMock()

        # The object that is iterated over
        mock_text_stream = ["Hello", " world", "!"]

        # The stream object returned by the context manager's __enter__
        mock_stream = MagicMock()
        mock_stream.text_stream = iter(mock_text_stream)

        # The context manager object
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_stream
        
        mock_client.messages.stream.return_value = mock_context_manager
        mock_anthropic_class.return_value = mock_client

        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(provider.generate_response_stream(messages))

        assert chunks == ["Hello", " world", "!"]


class TestGoogleProvider:
    """Test Google Gemini provider"""
    
    @pytest.fixture
    def provider(self):
        """Create a Google provider instance"""
        return GoogleProvider(
            api_key='test-key',
            model='gemini-pro',
            temperature=0.7
        )
    
    @patch('providers.google_provider.requests.post')
    def test_generate_response_success(self, mock_post, provider):
        """Test successful response generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Test response'}]}}]
        }
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)

        assert result == "Test response"

    @patch('providers.google_provider.requests.post')
    def test_generate_response_error(self, mock_post, provider):
        """Test error handling"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad request")
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(Exception, match="Google API request error"):
            provider.generate_response(messages)

    @patch('providers.google_provider.requests.post')
    def test_generate_response_stream(self, mock_post, provider):
        """Test streaming response generation"""
        mock_response = Mock()
        mock_response.status_code = 200

        # Simulate chunked JSON responses as strings
        chunks = [
            '{"candidates": [{"content": {"parts": [{"text": "Hello "}]}}]}',
            '{"candidates": [{"content": {"parts": [{"text": "world"}]}}]}',
            '{"candidates": [{"content": {"parts": [{"text": "!"}]}}]}',
        ]
        mock_response.iter_lines.return_value = iter(chunks)
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result_chunks = list(provider.generate_response_stream(messages))

        assert result_chunks == ["Hello ", "world", "!"]

    def test_format_messages(self, provider):
        """Test message format conversion"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How are you?"}
        ]

        result = provider._format_messages(messages)

        expected = [
            {'role': 'user', 'parts': [{'text': 'Hello'}]},
            {'role': 'model', 'parts': [{'text': 'Hi there'}]},
            {'role': 'user', 'parts': [{'text': 'How are you?'}]},
        ]
        assert result == expected

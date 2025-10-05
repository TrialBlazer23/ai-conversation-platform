"""
Pytest configuration and shared fixtures
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database.session import db


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application"""
    return app.test_cli_runner()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing"""
    return {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Test response from OpenAI'
            }
        }],
        'usage': {
            'prompt_tokens': 10,
            'completion_tokens': 5,
            'total_tokens': 15
        },
        'model': 'gpt-4'
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response for testing"""
    return {
        'content': [{
            'type': 'text',
            'text': 'Test response from Claude'
        }],
        'usage': {
            'input_tokens': 10,
            'output_tokens': 5
        },
        'model': 'claude-3-sonnet-20240229'
    }


@pytest.fixture
def mock_google_response():
    """Mock Google Gemini API response for testing"""
    return {
        'candidates': [{
            'content': {
                'parts': [{
                    'text': 'Test response from Gemini'
                }]
            }
        }],
        'usageMetadata': {
            'promptTokenCount': 10,
            'candidatesTokenCount': 5,
            'totalTokenCount': 15
        }
    }


@pytest.fixture
def sample_conversation_config():
    """Sample conversation configuration for testing"""
    return {
        'title': 'Test Conversation',
        'system_message': 'You are a helpful assistant.',
        'participants': [
            {
                'name': 'Assistant 1',
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        ]
    }

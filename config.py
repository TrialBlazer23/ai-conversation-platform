"""
Application configuration
Enhanced with database and advanced features
"""
import os
from pathlib import Path


class Config:
    """Base configuration class - Single Source of Fact"""
    
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Paths
    BASE_DIR = Path(__file__).parent
    STORAGE_PATH = os.environ.get('STORAGE_PATH', BASE_DIR / 'data')
    TEMPLATES_PATH = BASE_DIR / 'templates_config'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "conversations.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Streaming
    STREAM_ENABLED = True
    SSE_RETRY_TIMEOUT = 3000  # milliseconds
    
    # Token Management
    TOKEN_WARNING_THRESHOLD = 0.8  # Warn at 80% capacity
    TOKEN_LIMIT_BUFFER = 500  # Reserve tokens for response
    
    # Model Limits (tokens)
    MODEL_LIMITS = {
        # OpenAI models
        'gpt-4o': 128000,
        'gpt-4o-mini': 128000,
        'gpt-4-turbo': 128000,
        'o1-preview': 128000,
        'o1-mini': 128000,
        'gpt-4': 8192,
        'gpt-3.5-turbo': 16385,
        # Anthropic models
        'claude-3-5-sonnet-20241022': 200000,
        'claude-3-5-haiku-20241022': 200000,
        'claude-3-opus-20240229': 200000,
        'claude-3-sonnet-20240229': 200000,
        'claude-3-haiku-20240307': 200000,
        # Google Gemini models
        'gemini-2.0-flash-exp': 1000000,
        'gemini-1.5-pro': 2000000,
        'gemini-1.5-flash': 1000000,
        # Default fallback
        'default': 4096
    }
    
    # Cost per 1K tokens (USD)
    MODEL_COSTS = {
        # OpenAI models
        'gpt-4o': {'input': 0.0025, 'output': 0.01},
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'o1-preview': {'input': 0.015, 'output': 0.06},
        'o1-mini': {'input': 0.003, 'output': 0.012},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        # Anthropic models
        'claude-3-5-sonnet-20241022': {'input': 0.003, 'output': 0.015},
        'claude-3-5-haiku-20241022': {'input': 0.0008, 'output': 0.004},
        'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        # Google Gemini models
        'gemini-2.0-flash-exp': {'input': 0.0, 'output': 0.0},  # Free during preview
        'gemini-1.5-pro': {'input': 0.00125, 'output': 0.005},
        'gemini-1.5-flash': {'input': 0.000075, 'output': 0.0003},
        # Default for local/unknown models
        'default': {'input': 0.0, 'output': 0.0}
    }
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_TIMEOUT = 120  # seconds
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with config"""
        # Create directories if they don't exist
        cls.STORAGE_PATH.mkdir(exist_ok=True)
        cls.TEMPLATES_PATH.mkdir(exist_ok=True)
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
        'gpt-4': 8192,
        'gpt-4-turbo': 128000,
        'gpt-4-turbo-preview': 128000,
        'gpt-3.5-turbo': 16385,
        'gpt-3.5-turbo-16k': 16385,
        'claude-3-opus-20240229': 200000,
        'claude-3-sonnet-20240229': 200000,
        'claude-3-haiku-20240307': 200000,
        'claude-2.1': 200000,
        'claude-2.0': 100000,
        'gemini-1.5-pro': 1000000,
        'gemini-1.5-flash': 1000000,
        'gemini-pro': 32000,
        'gemini-pro-vision': 16000,
        'default': 4096  # Fallback for unknown models
    }
    
    # Cost per 1K tokens (USD)
    MODEL_COSTS = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        'gemini-1.5-pro': {'input': 0.00125, 'output': 0.00375},
        'gemini-1.5-flash': {'input': 0.000125, 'output': 0.000375},
        'gemini-pro': {'input': 0.00025, 'output': 0.00075},
        'gemini-pro-vision': {'input': 0.00025, 'output': 0.00075},
        'default': {'input': 0.0, 'output': 0.0}  # Free for local models
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
#!/usr/bin/env python3
"""
Setup script for AI Conversation Platform
Helps with initial setup and verification
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_python_version():
    """Verify Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        return False
    
    print("✅ Python version OK")
    return True


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    dirs = [
        'data',
        'templates_config',
        'database',
        'models',
        'providers',
        'utils',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}/")
    
    print("\n✅ All directories created")


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("\n✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Failed to install dependencies")
        return False


def check_ollama():
    """Check if Ollama is available"""
    print_header("Checking Ollama (Optional)")
    
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            
            # List available models
            models_result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            if models_result.returncode == 0:
                print("\nAvailable models:")
                print(models_result.stdout)
            return True
    except FileNotFoundError:
        print("⚠️  Ollama not found (optional for local models)")
        print("   Install from: https://ollama.ai/download")
        return False


def create_env_template():
    """Create .env.example template"""
    print_header("Creating Environment Template")
    
    env_template = """# AI Conversation Platform - Environment Configuration

# Database
DATABASE_URL=sqlite:///conversations.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Security
SECRET_KEY=change-this-to-a-random-secret-key

# Debug Mode
DEBUG=True

# Optional: API Keys (can also be set in UI)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env.example")
    print("   Copy to .env and customize if needed")


def run_initial_check():
    """Run initial application check"""
    print_header("Testing Application")
    
    try:
        # Import main app to check for errors
        import config
        from database import init_db
        from flask import Flask
        
        app = Flask(__name__)
        app.config.from_object(config.Config)
        init_db(app)
        
        print("✅ Application loads successfully")
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Error loading application: {e}")
        return False


def print_next_steps():
    """Print next steps for user"""
    print_header("Setup Complete! 🎉")
    
    print("""
Next Steps:
-----------

1. Configure API Keys:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

2. (Optional) Install Ollama for local models:
   - Download: https://ollama.ai/download
   - Pull a model: ollama pull llama2

3. Start the application:
   python app.py

4. Open browser:
   http://localhost:5000

5. Start conversing!
   - Try a template or configure your own models
   - Enable streaming for real-time responses
   - Use Auto Mode for autonomous conversations

Documentation: See README.md for detailed usage guide

Happy conversing! 🤖💬
    """)


def main():
    """Main setup process"""
    print_header("AI Conversation Platform - Setup")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Please install dependencies manually:")
        print("   pip install -r requirements.txt")
    
    # Check Ollama
    check_ollama()
    
    # Create env template
    create_env_template()
    
    # Test application
    run_initial_check()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
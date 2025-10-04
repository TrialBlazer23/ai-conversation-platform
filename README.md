# 🤖 AI Conversation Platform

A powerful local web application for orchestrating multi-model AI conversations with full control, streaming responses, and advanced features.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### Core Capabilities
- 🤖 **Multi-Model Support**: Configure 2+ AI models to converse with each other
- 🔄 **Dual Modes**: 
  - **Autonomous Mode**: Models respond automatically in sequence
  - **Manual Mode**: Interrupt and edit messages before sending
- ⚡ **Real-Time Streaming**: See AI responses token-by-token as they're generated
- 💾 **Database Persistence**: SQLite-based conversation history and management

### Intelligence & Control
- 🏠 **Local Model Support**: Run models locally via Ollama (zero cost, full privacy)
- 🎯 **Token Management**: Real-time token counting with visual progress bars
- 📊 **Cost Tracking**: Monitor API costs per message and conversation
- 📝 **Markdown & Code Highlighting**: Beautiful rendering with syntax highlighting
- 📋 **Conversation Templates**: Quick-start presets for common scenarios

### Provider Support
- ✅ **OpenAI** (GPT-4, GPT-4-turbo, GPT-3.5-turbo)
- ✅ **Anthropic** (Claude 3 Opus, Sonnet, Haiku, Claude 2)
- ✅ **Ollama** (Llama 2, Mistral, CodeLlama, Neural Chat, Phi, and more)

### Developer-Friendly
- 🏗️ **Clean Architecture**: Follows SDR (Single Responsibility), SCC (Separation of Concerns), SSF (Single Source of Fact)
- 🔧 **Modular Design**: Easy to extend with new providers
- 📚 **Well-Documented**: Comprehensive code comments and documentation
- 🎨 **Modern UI**: Responsive design with sleek dark theme

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **pip** package manager
- **(Optional)** Ollama for local models

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TrialBlazer23/ai-conversation-platform.git
   cd ai-conversation-platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

### Optional: Install Ollama for Local Models

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
ollama pull mistral
```

**Windows:**
Download from [ollama.ai](https://ollama.ai)

---

## 📖 Usage Guide

### 1. Quick Start with Templates

The fastest way to get started is using pre-configured templates:

1. On the Configuration panel, browse **Quick Start Templates**
2. Click on a template (e.g., "Debate Mode", "Brainstorm", "Code Review")
3. The initial prompt and model configurations will auto-populate
4. Add your API keys
5. Click **Start Conversation**

### 2. Manual Configuration

#### Configure API Keys

Enter your API keys for the providers you want to use:
- **OpenAI**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: Get from [console.anthropic.com](https://console.anthropic.com)
- **Ollama**: No API key needed - runs locally!

#### Add Models

1. Click **"Add Model"** to configure each AI participant
2. Select the provider (OpenAI, Anthropic, or Ollama)
3. Choose the specific model
4. Set a display name (optional, for easier identification)
5. Adjust temperature (0 = deterministic, 2 = creative)
6. Add custom system prompts to shape model behavior

**Example Configuration:**
```
Model 1: GPT-4 (Creative Explorer)
- Temperature: 0.9
- System Prompt: "You are a creative brainstorming partner..."

Model 2: Claude 3 Opus (Critical Analyst)
- Temperature: 0.5
- System Prompt: "You are a critical analyst who evaluates ideas..."
```

#### Start Conversation

1. Enter your **Initial Prompt** - this starts the conversation
2. Click **Save Configuration**
3. Click **Start Conversation**

### 3. Running Conversations

#### Manual Mode (Default)
- Click **"Next Turn"** to generate one response at a time
- Review and optionally edit the response
- Full control over conversation flow

#### Autonomous Mode
- Click **"Auto Mode"** to let models converse automatically
- Models take turns responding in sequence
- Click **"Stop Auto"** to pause and regain control

#### Streaming Toggle
- **Streaming ON**: See responses token-by-token as they're generated (exciting!)
- **Streaming OFF**: Wait for complete response (faster for slower connections)

### 4. Advanced Features

#### Token Management
- Real-time token counter shows context window usage
- Visual progress bar warns when approaching limits
- Prevents truncation errors

#### Cost Tracking
- Per-message cost calculation
- Running total for conversation
- Header shows aggregate statistics

#### Export Conversations
- Click **"Export"** to download conversation as JSON
- Includes all messages, metadata, tokens, and costs
- Import later for analysis or archival

---

## 🏗️ Architecture

### Project Structure

```
ai-conversation-platform/
├── app.py                          # Main Flask application with SSE streaming
├── config.py                       # Configuration management (SSF)
├── requirements.txt                # Python dependencies
├── database/
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models (Conversation, Message, ModelConfig)
│   └── session.py                  # Database session management
├── models/
│   ├── __init__.py
│   ├── conversation.py             # Business logic for conversations (SCC)
│   └── ai_provider.py              # Provider factory pattern
├── providers/
│   ├── __init__.py
│   ├── base_provider.py            # Abstract base class (DIP)
│   ├── openai_provider.py          # OpenAI implementation with streaming
│   ├── anthropic_provider.py       # Anthropic implementation with streaming
│   └── ollama_provider.py          # Ollama local model implementation
├── utils/
│   ├── __init__.py
│   ├── token_counter.py            # Token counting with tiktoken (SDR)
│   └── helpers.py                  # Utility functions
├── templates_config/
│   ├── debate.json                 # Debate mode template
│   ├── brainstorm.json             # Brainstorming template
│   ├── code_review.json            # Code review template
│   └── tutor.json                  # Tutoring template
├── static/
│   ├── css/
│   │   └── style.css               # Enhanced UI styles
│   └── js/
│       └── app.js                  # Frontend application with streaming
└── templates/
    └── index.html                  # Main HTML template
```

### Design Principles

#### Single Responsibility (SDR)
Each module has one clear purpose:
- `token_counter.py`: Only handles token operations
- `conversation.py`: Only manages conversation state
- `base_provider.py`: Only defines provider interface

#### Separation of Concerns (SCC)
Clear boundaries between layers:
- **Presentation**: HTML/CSS/JavaScript (UI)
- **Business Logic**: Conversation management, orchestration
- **Data Access**: Database models, provider integrations
- **Infrastructure**: Configuration, utilities

#### Single Source of Fact (SSF)
Centralized configuration and state:
- `config.py`: All application settings
- Database: Single source of conversation truth
- Provider factory: Centralized provider creation

#### Additional Patterns
- **Factory Pattern**: AIProviderFactory for provider creation
- **Template Method**: BaseAIProvider defines interface
- **Dependency Inversion**: Providers implement abstract interface
- **Strategy Pattern**: Ready for orchestration modes (future)

---

## 🔌 Extending the Platform

### Adding a New AI Provider

1. **Create provider class** in `providers/`:

```python
from providers.base_provider import BaseAIProvider
from typing import List, Dict, Generator

class NewProvider(BaseAIProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supports_streaming = True  # If provider supports streaming
    
    def generate_response(self, messages: List[Dict]) -> str:
        """Implement non-streaming response"""
        # Your API call here
        pass
    
    def generate_response_stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Implement streaming response"""
        # Your streaming API call here
        pass
```

2. **Update factory** in `models/ai_provider.py`:

```python
elif provider_type == 'newprovider':
    return NewProvider(api_key=api_key, model=model, ...)
```

3. **Add to providers list** in `get_available_providers()`:

```python
{
    'id': 'newprovider',
    'name': 'New Provider',
    'requires_api_key': True,
    'supports_streaming': True,
    'models': ['model-1', 'model-2']
}
```

### Creating Custom Templates

Create a JSON file in `templates_config/`:

```json
{
  "name": "Your Template Name",
  "description": "Description of what this template does",
  "initial_prompt": "The starting prompt with [PLACEHOLDERS] for user to fill",
  "models": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "name": "Model Display Name",
      "temperature": 0.7,
      "system_prompt": "Instructions for this model's behavior"
    }
  ]
}
```

---

## 🎯 Use Cases

### Debate & Analysis
Configure two models with opposing viewpoints to debate topics:
```
Model 1: Pro position (temperature: 0.6)
Model 2: Con position (temperature: 0.6)
Initial: "Should AI development be regulated?"
```

### Creative Brainstorming
Multiple models with high creativity collaborate:
```
Model 1: Creative explorer (temperature: 0.9)
Model 2: Practical analyst (temperature: 0.5)
Model 3: Synthesizer (temperature: 0.7)
Initial: "New product ideas for eco-friendly tech"
```

### Code Review
Different models focus on different aspects:
```
Model 1: Security reviewer (temperature: 0.3)
Model 2: Performance reviewer (temperature: 0.3)
Initial: [Paste your code]
```

### Educational Tutoring
Socratic method teaching:
```
Model 1: Primary tutor (temperature: 0.7)
Model 2: Examples provider (temperature: 0.6)
Initial: "Teach me about quantum computing"
```

### Research Synthesis
Models analyze from different perspectives:
```
Model 1: Scientific analyst
Model 2: Philosophical perspective
Model 3: Practical applications
Initial: "Implications of AGI development"
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///conversations.db

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Token Management
TOKEN_WARNING_THRESHOLD=0.8
TOKEN_LIMIT_BUFFER=500
```

### Model Limits

Default token limits are configured in `config.py`:
- GPT-4: 8,192 tokens
- GPT-4-turbo: 128,000 tokens
- Claude 3: 200,000 tokens
- Custom models: 4,096 default

### Cost Configuration

API costs per 1K tokens (configurable in `config.py`):
- Local models (Ollama): $0 (free!)
- Commercial models: See provider pricing

---

## 🛡️ Security & Privacy

### API Key Storage
- Keys stored in session (memory only by default)
- Not persisted to disk
- Session expires after 1 hour

### Data Privacy
- All data stored locally in SQLite database
- No telemetry or external data transmission
- Use Ollama for complete privacy (local inference)

### Production Recommendations
1. Use environment variables for API keys
2. Enable HTTPS if exposing beyond localhost
3. Implement user authentication for multi-user setups
4. Regular database backups
5. Review and sanitize conversation data before sharing

---

## 🐛 Troubleshooting

### Common Issues

**Import Errors / Missing Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Ollama Connection Failed**
```bash
# Make sure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**API Authentication Errors**
- Verify API keys are correct
- Check API key has proper permissions
- Ensure account has sufficient credits

**Database Errors**
```bash
# Delete and recreate database
rm conversations.db
python app.py  # Will recreate automatically
```

**Streaming Not Working**
- Check browser console for errors
- Some corporate firewalls block SSE
- Try disabling browser extensions
- Toggle streaming mode off if issues persist

### Debug Mode

Enable detailed logging:
```python
# In config.py
DEBUG = True
SQLALCHEMY_ECHO = True
```

---

## 🗺️ Roadmap

### Phase 2 Features (Coming Soon)
- 🌳 **Conversation Branching**: Fork conversations and explore alternate paths
- 🎭 **Advanced Orchestration**: Debate mode, consensus mode, chain-of-thought
- 🧠 **Vector Memory (RAG)**: Long-term memory with document grounding
- 🌐 **Additional Providers**: Google Gemini, Cohere, Mistral AI
- 📊 **Analytics Dashboard**: Conversation insights and visualization

### Phase 3 Features (Future)
- 🔌 **Plugin System**: Community extensibility
- 🔬 **Prompt Engineering Tools**: A/B testing and optimization
- 🤝 **Multi-user Support**: Collaborative conversations
- 📱 **Mobile App**: Native iOS/Android applications
- ☁️ **Cloud Sync**: Optional cloud backup (encrypted)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code guidelines**:
   - Use Python conventions (PEP 8)
   - Follow SDR, SCC, SSF principles
   - Add docstrings and comments
   - Write tests for new features
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Code Style

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ES6+, clear variable names
- **Architecture**: Maintain separation of concerns
- **Documentation**: Update README for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Anthropic** for Claude models
- **Ollama** for local model infrastructure
- **Flask** for the web framework
- **SQLAlchemy** for ORM
- **Prism.js** for syntax highlighting
- **Marked.js** for markdown rendering

---

## 📧 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/TrialBlazer23/ai-conversation-platform/issues)
- **Discussions**: [Join the community](https://github.com/TrialBlazer23/ai-conversation-platform/discussions)
- **Author**: [@TrialBlazer23](https://github.com/TrialBlazer23)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

**Built with ❤️ for the AI community**

*Multi-model orchestration for humans*
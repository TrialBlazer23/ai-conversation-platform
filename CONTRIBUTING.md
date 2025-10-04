# Contributing to AI Conversation Platform

First off, thank you for considering contributing to AI Conversation Platform! 🎉

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, browser)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- **Use a clear title**
- **Provide detailed description** of the feature
- **Explain why it would be useful**
- **Consider architecture** - how does it fit with SDR/SCC/SSF?

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Follow the code style guidelines below
3. Add tests if applicable
4. Update documentation
5. Ensure the test suite passes
6. Submit your pull request!

## Code Style Guidelines

### Python

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Write **docstrings** for all public functions/classes
- Follow **SDR** (Single Responsibility), **SCC** (Separation of Concerns), **SSF** (Single Source of Fact)

Example:
```python
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate API cost for a model invocation.
    
    Args:
        model: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Total cost in USD
    """
    # Implementation
```

### JavaScript

- Use **ES6+** features
- Clear, descriptive variable names
- Comment complex logic
- Consistent formatting

### Architecture Principles

- **Single Responsibility**: Each class/module does one thing
- **Separation of Concerns**: UI, business logic, and data access are separate
- **Single Source of Fact**: Avoid duplicating configuration/state

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-conversation-platform.git
cd ai-conversation-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py
```

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=.
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update architecture diagrams if structure changes

## Questions?

Feel free to open an issue for discussion or reach out via GitHub Discussions!

Thank you for contributing! 🚀
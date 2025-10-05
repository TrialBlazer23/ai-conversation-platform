# 🚀 Quick Start Guide - New Features

This guide helps you get started with the newly added features in the AI Conversation Platform.

## 🎯 What's New

### 1. Cohere AI Provider
You can now use Cohere's Command models in your conversations!

**Setup:**
1. Get your API key from https://cohere.com/
2. In the UI, click "Add Model"
3. Select **Cohere** as the provider
4. Choose from available models:
   - `command-r-plus` - Most capable
   - `command-r` - Balanced
   - `command` - Standard
   - `command-light` - Fastest

### 2. Keyboard Shortcuts ⌨️
Work faster with these shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Generate next response |
| `Ctrl/Cmd + N` | New conversation |
| `Ctrl/Cmd + S` | Save configuration |
| `Ctrl/Cmd + E` | Export conversation |
| `Ctrl/Cmd + /` | Show shortcuts help |
| `Escape` | Stop auto mode |

**Try it:** Press `Ctrl+/` (or `Cmd+/` on Mac) to see the shortcuts help dialog!

### 3. Response Caching 💾
Reduce API costs and get faster responses for repeated queries.

**Features:**
- Automatic caching of AI responses
- 1-hour default cache lifetime
- Up to 1000 cached responses
- Smart cache key based on model, messages, and temperature

**API Endpoints:**
```bash
# View cache statistics
curl http://localhost:5000/api/cache/stats

# Clear the cache
curl -X POST http://localhost:5000/api/cache/clear
```

### 4. Provider Health Checks ✅
Validate your API keys before starting conversations!

**Usage:**
```javascript
// From the browser console or your code
const health = await UIEnhancements.checkProviderHealth({
  openai: 'sk-...',
  anthropic: 'sk-ant-...',
  google: 'AIza...',
  cohere: '...'
});

// Display health status
UIEnhancements.displayProviderHealth(health);
```

**API Endpoint:**
```bash
curl -X POST http://localhost:5000/api/health/providers \
  -H "Content-Type: application/json" \
  -d '{
    "api_keys": {
      "openai": "sk-...",
      "anthropic": "sk-ant-..."
    }
  }'
```

### 5. Export Conversations 📤
Export your conversations in multiple formats!

**Available Formats:**
- **JSON** - Raw data export
- **Markdown** - Formatted for documentation
- **Text** - Plain text format

**UI Export:**
- Press `Ctrl+E` or `Cmd+E`
- Choose your format
- File downloads automatically!

**API Export:**
```bash
# Export as JSON
curl http://localhost:5000/api/conversation/<id>/export

# Export as Markdown
curl http://localhost:5000/api/conversation/<id>/export/markdown

# Export as Text
curl http://localhost:5000/api/conversation/<id>/export/text
```

### 6. Response Time Tracking ⏱️
See how fast each AI model responds!

**Features:**
- Automatic response time measurement
- Displayed in message metadata
- Server-side tracking via `X-Response-Time` header

**Example:**
```javascript
const tracker = new UIEnhancements.ResponseTimeTracker();
tracker.start();
// ... make API call ...
const elapsed = tracker.stop();
console.log(`Response took ${elapsed}s`);
```

### 7. Model Status Indicators 🟢
Visual indicators show what each model is doing:

- ⚪ **Idle** - Ready to respond
- 🟡 **Thinking** - Processing your request
- 🟢 **Streaming** - Sending response
- 🔴 **Error** - Something went wrong

### 8. Enhanced Security 🔒
New security features protect your application:

- Request validation middleware
- Response time tracking
- Security headers (X-Content-Type-Options, X-Frame-Options)
- API timeout configuration (default: 60 seconds)

## 🎨 UI Improvements

### Copy Button Enhancement
- Click the 📋 icon to copy any message
- Visual feedback with ✅ when copied
- Success notification

### Typing Indicators
Models now show animated "..." when generating responses!

### Dark Mode Support
All new features fully support dark mode.

## 🔧 Configuration

### Timeout Settings
Configure API timeouts in your provider initialization:

```python
from providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-...",
    model="gpt-4",
    timeout=30.0  # 30 seconds
)
```

### Cache Settings
Customize cache behavior:

```python
from utils.cache import ResponseCache

cache = ResponseCache(
    ttl=1800,      # 30 minutes
    max_size=500   # 500 items max
)
```

## 📊 Monitoring

### Check System Health
```bash
# Get cache stats
curl http://localhost:5000/api/cache/stats

# Response:
{
  "status": "success",
  "cache": {
    "total_items": 45,
    "active_items": 42,
    "max_size": 1000,
    "ttl": 3600
  }
}
```

### Check Provider Health
```bash
curl -X POST http://localhost:5000/api/health/providers \
  -H "Content-Type: application/json" \
  -d '{"api_keys": {"openai": "sk-..."}}'

# Response:
{
  "status": "success",
  "providers": {
    "openai": {
      "status": "healthy",
      "message": "API key is valid"
    }
  }
}
```

### Monitor Response Times
Check the `X-Response-Time` header in API responses:
```bash
curl -I http://localhost:5000/api/providers

# Look for:
# X-Response-Time: 0.042s
```

## 🎓 Best Practices

### 1. Use Keyboard Shortcuts
- Learn the shortcuts with `Ctrl+/`
- Use `Ctrl+Enter` for faster conversations
- Export regularly with `Ctrl+E`

### 2. Monitor Cache Performance
- Check cache stats periodically
- Clear cache when changing configurations
- Adjust TTL based on your use case

### 3. Validate API Keys
- Run health checks before important conversations
- Use the health display to see provider status
- Handle errors gracefully

### 4. Export Important Conversations
- Export as Markdown for documentation
- Export as JSON for data analysis
- Export as Text for simple backups

### 5. Optimize Response Times
- Use caching for repeated queries
- Choose faster models when appropriate
- Monitor response times to track performance

## 🐛 Troubleshooting

### Issue: Keyboard shortcuts not working
**Solution:** Refresh the page. Shortcuts are initialized on load.

### Issue: Cache not improving performance
**Solution:** Check cache stats. If hit rate is low, increase TTL.

### Issue: Export fails
**Solution:** Ensure conversation exists and has messages.

### Issue: Health check shows error
**Solution:** Verify API key is correct and has no typos.

### Issue: Slow response times
**Solution:** Check your internet connection and provider status.

## 📚 Additional Resources

- **Full Documentation:** See `ENHANCEMENTS.md`
- **API Reference:** Check the Flask routes in `app.py`
- **UI Components:** Review `static/js/ui-enhancements.js`
- **Styling:** See `static/css/style.css`

## 🎉 Getting Started

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open in browser:**
   ```
   http://localhost:5000
   ```

3. **Try a keyboard shortcut:**
   - Press `Ctrl+/` to see all shortcuts

4. **Add a Cohere model:**
   - Click "Add Model"
   - Select "Cohere"
   - Enter your API key
   - Choose a model

5. **Start a conversation:**
   - Enter a prompt
   - Press `Ctrl+Enter` to generate response

6. **Export your conversation:**
   - Press `Ctrl+E`
   - Choose format (JSON, Markdown, or Text)

## 💡 Tips & Tricks

### Speed Up Development
- Use keyboard shortcuts for common actions
- Enable caching for faster repeated queries
- Monitor response times to identify slow models

### Improve Reliability
- Validate API keys before starting
- Export important conversations regularly
- Clear cache when switching configurations

### Enhance Experience
- Learn the keyboard shortcuts
- Use model status indicators to track progress
- Copy messages easily with the copy button

## 🔮 Coming Soon

- Batch conversation operations
- Advanced streaming error recovery
- Custom keyboard shortcut configuration
- Real-time collaboration features
- More AI provider integrations

---

**Need Help?** Check the full documentation in `ENHANCEMENTS.md` or open an issue on GitHub!

**Enjoying the new features?** ⭐ Star the repository!

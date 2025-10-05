# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-05

### Added
- **Keyboard Shortcuts System** ⌨️
  - `Ctrl/Cmd + Enter`: Start conversation or next turn
  - `Ctrl/Cmd + N`: New conversation
  - `Ctrl/Cmd + S`: Save configuration
  - `Ctrl/Cmd + E`: Export conversation
  - `Escape`: Stop auto mode
  - `Shift + ?`: Show keyboard shortcuts help modal
  
- **Auto-Save Configuration** 💾
  - Automatically saves API keys after 2 seconds of inactivity
  - Debounced to prevent excessive save operations
  - Silent saves don't interrupt user workflow
  - Auto-save before starting conversations

- **Enhanced Input Validation** ✅
  - Validates initial prompt presence and minimum length (10 characters)
  - Checks for at least one configured model
  - Verifies API keys are provided for selected providers
  - Provides helpful error messages with emojis

- **Improved Status Messages** 💬
  - Auto-dismiss for success messages (3 seconds)
  - Extended display for errors (5 seconds)
  - Loading spinner animation
  - Rich emoji-based feedback (✅, ❌, ⚠️, 💡, 🚀)

- **Better Error Handling** 🛡️
  - Detailed error messages with recovery suggestions
  - Automatic retry prompts for failed operations
  - Console logging for debugging
  - Graceful fallbacks

- **Cost Estimation** 💰
  - Shows estimated token count before starting conversations
  - Based on initial prompt length
  - Helps users plan API usage

- **Accessibility Improvements** ♿
  - ARIA labels on all form inputs
  - Keyboard navigation support
  - Tooltips with helpful information (ℹ️)
  - Better screen reader support
  - Improved focus states with visible outlines

- **Welcome & Onboarding** 👋
  - First-time user tip about keyboard shortcuts
  - Stored in localStorage to show only once
  - Non-intrusive onboarding experience

- **Confirmation Dialogs** ⚠️
  - Confirms before starting new conversation when one exists
  - Retry prompts after streaming failures
  - Prevents accidental data loss

- **Enhanced Visual Feedback** 🎨
  - Loading spinner animations
  - Smooth transitions for status messages
  - Better button hover states with ripple effect
  - Improved scrollbar styling
  - Pulse animations for status indicators

### Changed
- **saveConfig() function** now supports silent saves and returns boolean success status
- **startConversation() function** now builds model list from UI and auto-saves configuration
- **showStatus() function** now supports custom durations and auto-dismisses messages
- **newConversation() function** now asks for confirmation if conversation exists

### Fixed
- Focus is now properly set to Initial Prompt field when validation fails
- Status messages no longer persist indefinitely
- Better error recovery for streaming failures

### Security
- Added autocomplete="off" to API key fields
- Improved input sanitization

### Documentation
- Added comprehensive IMPROVEMENTS.md with full feature documentation
- Created CHANGELOG.md for version tracking
- Enhanced inline code comments
- Added tooltips for better user guidance

### Developer Experience
- Improved code organization with better separation of concerns
- Added debouncing for auto-save to reduce server load
- Better error logging for debugging
- More maintainable event handling

---

## [1.0.0] - 2024-10-04

### Added
- Initial release with multi-model conversation support
- OpenAI, Anthropic, Google, and Ollama provider support
- Streaming and non-streaming response modes
- Token counting and cost tracking
- Conversation templates
- Database persistence with SQLite
- Markdown rendering with syntax highlighting
- Auto mode for continuous conversations
- Manual mode with message editing
- Export conversations as JSON

### Providers
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini 2.5 Pro, Gemini 1.5 Pro/Flash)
- Ollama (Local models)

### Architecture
- Flask backend with SQLAlchemy ORM
- Clean architecture with SDR, SCC, SSF principles
- Provider factory pattern
- Template method pattern for providers
- RESTful API design

---

## Future Releases

See [UPGRADE_PLAN.md](UPGRADE_PLAN.md) for planned features and improvements.

### Planned for 1.2.0
- [ ] Conversation search and filtering
- [ ] Model comparison view
- [ ] Dark mode toggle
- [ ] Conversation templates management UI
- [ ] Export/import configuration feature
- [ ] Conversation branching

### Planned for 2.0.0
- [ ] Real-time collaboration features
- [ ] Advanced context management
- [ ] Analytics dashboard
- [ ] Additional AI providers
- [ ] Plugin system
- [ ] API documentation (OpenAPI/Swagger)

---

**Note:** This project follows semantic versioning. Breaking changes will only be introduced in major version releases.

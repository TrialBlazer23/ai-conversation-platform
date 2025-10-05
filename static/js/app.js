/**
 * AI Conversation Platform - Enhanced Frontend Application
 * Supports streaming, token management, templates, and local models
 */

class ConversationApp {
    constructor() {
        this.conversationId = null;
        this.autoMode = false;
        this.streamingEnabled = true;
        this.currentConfig = {
            api_keys: {},
            models: []
        };
        this.providers = [];
        this.templates = [];
        this.tokenUsage = null;
        this.autoSaveEnabled = true;
        this.autoSaveTimeout = null;

        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        await this.loadProviders();
        await this.loadTemplates();
        await this.checkOllamaStatus();
        this.loadConfig();
        this.addModelConfig(); // Add first model by default
        this.showWelcomeMessage();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter or Cmd+Enter: Start conversation or next turn
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                if (this.conversationId) {
                    this.nextTurn();
                } else {
                    this.startConversation();
                }
            }
            
            // Ctrl+N or Cmd+N: New conversation
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.newConversation();
            }
            
            // Ctrl+S or Cmd+S: Save configuration
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.saveConfig();
            }
            
            // Ctrl+E or Cmd+E: Export conversation
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                if (this.conversationId) {
                    this.exportConversation();
                }
            }

            // Escape: Cancel auto mode or close modals
            if (e.key === 'Escape') {
                if (this.autoMode) {
                    this.toggleAutoMode();
                }
            }

            // Show keyboard shortcuts with ?
            if (e.shiftKey && e.key === '?') {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
        });
    }

    showWelcomeMessage() {
        const welcomeKey = 'ai-conversation-welcome-shown';
        if (!localStorage.getItem(welcomeKey)) {
            setTimeout(() => {
                this.showStatus('💡 Tip: Press Shift+? to see keyboard shortcuts', 'info', 5000);
                localStorage.setItem(welcomeKey, 'true');
            }, 1000);
        }
    }

    showKeyboardShortcuts() {
        const shortcuts = [
            { keys: 'Ctrl/Cmd + Enter', action: 'Start conversation or next turn' },
            { keys: 'Ctrl/Cmd + N', action: 'New conversation' },
            { keys: 'Ctrl/Cmd + S', action: 'Save configuration' },
            { keys: 'Ctrl/Cmd + E', action: 'Export conversation' },
            { keys: 'Escape', action: 'Stop auto mode' },
            { keys: 'Shift + ?', action: 'Show this help' }
        ];

        const helpHtml = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        background: var(--bg-dark); border: 2px solid var(--border-color); 
                        border-radius: 8px; padding: 20px; z-index: 10000; max-width: 500px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                <h3 style="margin-top: 0; color: var(--primary-color);">⌨️ Keyboard Shortcuts</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    ${shortcuts.map(s => `
                        <tr style="border-bottom: 1px solid var(--border-color);">
                            <td style="padding: 8px; font-family: monospace; color: var(--accent-color);">${s.keys}</td>
                            <td style="padding: 8px; color: var(--text-color);">${s.action}</td>
                        </tr>
                    `).join('')}
                </table>
                <button onclick="this.parentElement.remove()" 
                        style="margin-top: 15px; padding: 8px 16px; background: var(--primary-color); 
                               border: none; border-radius: 4px; color: white; cursor: pointer;">
                    Close
                </button>
            </div>
            <div onclick="this.nextElementSibling.remove(); this.remove();" 
                 style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: rgba(0,0,0,0.5); z-index: 9999;"></div>
        `;

        const helpDiv = document.createElement('div');
        helpDiv.innerHTML = helpHtml;
        document.body.appendChild(helpDiv);
    }

    setupEventListeners() {
        // Configuration
        document.getElementById('add-model-btn').addEventListener('click', () => this.addModelConfig());
        document.getElementById('save-config-btn').addEventListener('click', () => this.saveConfig());
        document.getElementById('start-conversation-btn').addEventListener('click', () => this.startConversation());
        document.getElementById('refresh-ollama-btn').addEventListener('click', () => this.checkOllamaStatus());

        // Conversation controls
        document.getElementById('streaming-toggle').addEventListener('click', () => this.toggleStreaming());
        document.getElementById('auto-mode-btn').addEventListener('click', () => this.toggleAutoMode());
        document.getElementById('next-turn-btn').addEventListener('click', () => this.nextTurn());
        document.getElementById('export-btn').addEventListener('click', () => this.exportConversation());
        document.getElementById('new-conversation-btn').addEventListener('click', () => this.newConversation());

        // Edit controls
        document.getElementById('send-edited-btn').addEventListener('click', () => this.sendEdited());
        document.getElementById('send-original-btn').addEventListener('click', () => this.sendOriginal());
        document.getElementById('cancel-edit-btn').addEventListener('click', () => this.cancelEdit());

        // Initial prompt character counter
        document.getElementById('initial-prompt').addEventListener('input', (e) => this.updatePromptStats(e.target.value));

        // Auto-save on configuration changes
        ['openai-key', 'anthropic-key', 'google-key'].forEach(id => {
            const elem = document.getElementById(id);
            if (elem) {
                elem.addEventListener('input', () => this.scheduleAutoSave());
            }
        });
    }

    scheduleAutoSave() {
        if (!this.autoSaveEnabled) return;
        
        // Clear existing timeout
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        
        // Schedule auto-save after 2 seconds of inactivity
        this.autoSaveTimeout = setTimeout(() => {
            this.saveConfig(true); // true = silent save
        }, 2000);
    }

    async loadProviders() {
        try {
            const response = await fetch('/api/providers');
            this.providers = await response.json();
        } catch (error) {
            console.error('Error loading providers:', error);
            this.showStatus('Error loading providers', 'error');
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            this.templates = await response.json();
            this.renderTemplates();
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    renderTemplates() {
        const container = document.getElementById('templates-container');

        if (this.templates.length === 0) {
            container.innerHTML = '<div class="template-card">No templates available</div>';
            return;
        }

        container.innerHTML = this.templates.map(template => `
            <div class="template-card" onclick="app.selectTemplate('${template.id}')">
                <div class="template-name">${template.name}</div>
                <div class="template-description">${template.description}</div>
                <div class="template-models">${template.models.length} models configured</div>
            </div>
        `).join('');
    }

    selectTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        // Clear existing models
        document.getElementById('models-container').innerHTML = '';

        // Set initial prompt
        document.getElementById('initial-prompt').value = template.initial_prompt;
        this.updatePromptStats(template.initial_prompt);

        // Add template models
        template.models.forEach(modelConfig => {
            this.addModelConfig(modelConfig);
        });

        // Visual feedback
        document.querySelectorAll('.template-card').forEach(card => {
            card.classList.remove('selected');
        });
        event.target.closest('.template-card').classList.add('selected');

        this.showStatus(`Template "${template.name}" loaded`, 'success');
    }

    async checkOllamaStatus() {
        const statusEl = document.getElementById('ollama-status');
        statusEl.textContent = 'Checking...';
        statusEl.className = 'status-indicator';

        try {
            const response = await fetch('/api/providers');
            const providers = await response.json();
            const ollama = providers.find(p => p.id === 'ollama');

            if (ollama && ollama.models && ollama.models.length > 0) {
                statusEl.textContent = `Connected (${ollama.models.length} models)`;
                statusEl.classList.add('connected');
            } else {
                statusEl.textContent = 'Not running';
                statusEl.classList.add('disconnected');
            }
        } catch (error) {
            statusEl.textContent = 'Error checking status';
            statusEl.classList.add('disconnected');
        }
    }

    addModelConfig(config = null) {
        const container = document.getElementById('models-container');
        const modelIndex = container.children.length;

        const modelDiv = document.createElement('div');
        modelDiv.className = 'model-config';
        modelDiv.innerHTML = `
            <div class="model-header">
                <h4><span class="model-number">${modelIndex + 1}</span>Model Configuration</h4>
                <button class="btn btn-sm btn-danger" onclick="app.removeModelConfig(this)">
                    <span class="btn-icon">🗑️</span> Remove
                </button>
            </div>
            <div class="form-group">
                <label>Provider:</label>
                <select class="model-provider" onchange="app.updateModelOptions(this)">
                    ${this.providers.map(p => `
                        <option value="${p.id}" ${config && config.provider === p.id ? 'selected' : ''}>
                            ${p.name}
                        </option>
                    `).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Model:</label>
                <select class="model-name">
                    <option value="">Select a model...</option>
                </select>
            </div>
            <div class="form-group">
                <label>Display Name:</label>
                <input type="text" class="model-display-name" placeholder="Optional custom name" 
                       value="${config ? config.name : ''}">
            </div>
            <div class="form-group">
                <label>Temperature (0-2):</label>
                <input type="number" class="model-temperature" min="0" max="2" step="0.1" 
                       value="${config ? config.temperature : 0.7}">
            </div>
            <div class="form-group">
                <label>System Prompt / Instructions:</label>
                <textarea class="model-system-prompt" rows="3" 
                          placeholder="Custom instructions for this model...">${config ? config.system_prompt : ''}</textarea>
            </div>
        `;

        container.appendChild(modelDiv);

        // Initialize model dropdown
        const providerSelect = modelDiv.querySelector('.model-provider');
        this.updateModelOptions(providerSelect, config ? config.model : null);
    }

    updateModelOptions(providerSelect, selectedModel = null) {
        const modelDiv = providerSelect.closest('.model-config');
        const modelSelect = modelDiv.querySelector('.model-name');
        const providerId = providerSelect.value;

        const provider = this.providers.find(p => p.id === providerId);
        if (!provider) return;

        modelSelect.innerHTML = provider.models.map(model => `
            <option value="${model}" ${selectedModel === model ? 'selected' : ''}>${model}</option>
        `).join('');
    }

    removeModelConfig(button) {
        const modelConfig = button.closest('.model-config');
        modelConfig.remove();
        this.renumberModels();
    }

    renumberModels() {
        const models = document.querySelectorAll('.model-config');
        models.forEach((model, index) => {
            model.querySelector('.model-number').textContent = index + 1;
        });
    }

    updatePromptStats(text) {
        const statsEl = document.getElementById('prompt-stats');
        const charCount = text.length;
        const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;

        statsEl.textContent = `${charCount} characters, ${wordCount} words`;
        statsEl.style.color = 'var(--text-muted)';
        statsEl.style.fontSize = '0.85em';
        statsEl.style.marginTop = '5px';
    }

    async saveConfig(silent = false) {
        const apiKeys = {
            openai: document.getElementById('openai-key').value,
            anthropic: document.getElementById('anthropic-key').value,
            google: document.getElementById('google-key').value
        };

        const models = [];
        document.querySelectorAll('.model-config').forEach(modelDiv => {
            const provider = modelDiv.querySelector('.model-provider').value;
            const model = modelDiv.querySelector('.model-name').value;
            const displayName = modelDiv.querySelector('.model-display-name').value;
            const temperature = parseFloat(modelDiv.querySelector('.model-temperature').value);
            const systemPrompt = modelDiv.querySelector('.model-system-prompt').value;

            if (model) {
                models.push({
                    provider,
                    model,
                    name: displayName || model,
                    temperature,
                    system_prompt: systemPrompt
                });
            }
        });

        // Validation
        if (models.length === 0) {
            if (!silent) {
                this.showStatus('⚠️ Please add at least one model', 'error');
            }
            return false;
        }

        // Check if API keys are provided for selected providers
        const usedProviders = [...new Set(models.map(m => m.provider))];
        const missingKeys = usedProviders.filter(p => p !== 'ollama' && !apiKeys[p]);
        
        if (missingKeys.length > 0 && !silent) {
            this.showStatus(`⚠️ Missing API keys for: ${missingKeys.join(', ')}`, 'error');
            return false;
        }

        this.currentConfig = { api_keys: apiKeys, models };

        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentConfig)
            });

            const result = await response.json();
            
            if (!silent) {
                this.showStatus('✅ Configuration saved successfully!', 'success');
            }
            return true;
        } catch (error) {
            if (!silent) {
                this.showStatus('❌ Error saving configuration. Please try again.', 'error');
            }
            console.error('Save config error:', error);
            return false;
        }
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();

            if (config.api_keys) {
                document.getElementById('openai-key').value = config.api_keys.openai || '';
                document.getElementById('anthropic-key').value = config.api_keys.anthropic || '';
                document.getElementById('google-key').value = config.api_keys.google || '';
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }
    }

    async startConversation() {
        const initialPrompt = document.getElementById('initial-prompt').value.trim();

        if (!initialPrompt) {
            this.showStatus('⚠️ Please enter an initial prompt to start the conversation', 'error');
            document.getElementById('initial-prompt').focus();
            return;
        }

        // Validate prompt length
        if (initialPrompt.length < 10) {
            this.showStatus('⚠️ Initial prompt is too short. Please provide more detail.', 'error');
            return;
        }

        // Build models list from UI
        const models = [];
        document.querySelectorAll('.model-config').forEach(modelDiv => {
            const provider = modelDiv.querySelector('.model-provider').value;
            const model = modelDiv.querySelector('.model-name').value;
            const displayName = modelDiv.querySelector('.model-display-name').value;
            const temperature = parseFloat(modelDiv.querySelector('.model-temperature').value);
            const systemPrompt = modelDiv.querySelector('.model-system-prompt').value;

            if (model) {
                models.push({
                    provider,
                    model,
                    name: displayName || model,
                    temperature,
                    system_prompt: systemPrompt
                });
            }
        });

        if (models.length === 0) {
            this.showStatus('⚠️ Please configure at least one model before starting', 'error');
            return;
        }

        // Show estimated cost
        const estimatedTokens = Math.ceil(initialPrompt.length / 4); // rough estimate
        this.showStatus(`🚀 Starting conversation... (estimated ~${estimatedTokens} tokens)`, 'loading');

        // Auto-save configuration before starting
        const saved = await this.saveConfig(true);
        if (!saved) {
            this.showStatus('⚠️ Please fix configuration errors before starting', 'error');
            return;
        }

        try {
            const response = await fetch('/api/conversation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    initial_prompt: initialPrompt,
                    models: models
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.conversationId = data.conversation_id;
                this.currentConfig.models = models; // Update current config
                this.showConversationPanel();
                this.displayMessage({
                    role: 'user',
                    content: initialPrompt,
                    model: 'You',
                    timestamp: new Date().toISOString()
                });
                this.updateNextModel(models[0].name);
                this.showStatus('✅ Conversation started! Ready for first response.', 'success');
                this.updateConversationMeta();
            } else {
                this.showStatus(`❌ Error: ${data.message || 'Failed to start conversation'}`, 'error');
            }
        } catch (error) {
            console.error('Start conversation error:', error);
            this.showStatus('❌ Error starting conversation. Please check your configuration and try again.', 'error');
        }
    }

    async nextTurn(editedMessage = null) {
        if (!this.conversationId) {
            this.showStatus('No active conversation', 'error');
            return;
        }

        if (this.streamingEnabled) {
            await this.nextTurnStreaming(editedMessage);
        } else {
            await this.nextTurnNonStreaming(editedMessage);
        }
    }

    async nextTurnNonStreaming(editedMessage = null) {
        this.showStatus('Generating response...', 'loading');
        this.setButtonsDisabled(true);

        try {
            const response = await fetch(`/api/conversation/${this.conversationId}/next`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ edited_message: editedMessage })
            });

            const data = await response.json();
            
            // Debug: Log the full response
            console.log('API Response:', data);
            console.log('Message object:', data.message);

            if (data.status === 'success') {
                this.displayMessage(data.message);
                this.updateNextModel(data.next_model);
                this.updateTokenUsage(data.token_usage);
                this.showStatus('Response generated', 'success');
                this.updateGlobalStats(data.message);

                if (this.autoMode) {
                    setTimeout(() => this.nextTurn(), 2000);
                }
            } else {
                this.showStatus(`Error: ${data.message}`, 'error');
            }
        } catch (error) {
            this.showStatus('Error generating response', 'error');
            console.error(error);
        } finally {
            this.setButtonsDisabled(false);
        }
    }

    async nextTurnStreaming(editedMessage = null) {
        this.showStatus('Streaming response...', 'loading');
        this.setButtonsDisabled(true);

        const messagesContainer = document.getElementById('messages-container');
        const streamingMessage = document.createElement('div');
        streamingMessage.className = 'message assistant streaming';

        let currentModel = '';
        let fullContent = '';
        let timestamp = '';

        try {
            const response = await fetch(`/api/conversation/${this.conversationId}/next/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ edited_message: editedMessage })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    if (buffer.length > 0) {
                        // Process any remaining data in the buffer
                        processChunk(buffer);
                    }
                    break;
                }

                buffer += decoder.decode(value, { stream: true });
                
                let boundary = buffer.lastIndexOf('\n\n');
                if (boundary !== -1) {
                    const completedMessages = buffer.substring(0, boundary);
                    buffer = buffer.substring(boundary + 2);
                    processChunk(completedMessages);
                }
            }

            function processChunk(chunk) {
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            handleStreamData(data);
                        } catch (e) {
                            console.error('Error parsing stream data:', e, 'line:', line);
                        }
                    }
                }
            }

            function handleStreamData(data) {
                // Debug logging
                console.log('Stream data:', data);

                if (data.error) {
                    app.showStatus(`Error: ${data.error}`, 'error');
                    streamingMessage.remove();
                    return;
                }

                if (data.type === 'metadata') {
                    currentModel = data.model;
                    timestamp = data.timestamp;

                    streamingMessage.innerHTML = `
                        <div class="message-header">
                            <span class="message-model">${app.escapeHtml(currentModel)}</span>
                            <span class="message-timestamp">${new Date(timestamp).toLocaleString()}</span>
                        </div>
                        <div class="message-content"></div>
                    `;
                    messagesContainer.appendChild(streamingMessage);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                } else if (data.type === 'content') {
                    fullContent += data.chunk;
                    const contentDiv = streamingMessage.querySelector('.message-content');
                    if (contentDiv) {
                        contentDiv.innerHTML = app.renderMarkdown(fullContent);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                } else if (data.type === 'done') {
                    streamingMessage.classList.remove('streaming');

                    // Add metadata footer
                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'message-meta';
                    metaDiv.innerHTML = `
                        <span class="message-meta-item">🎯 ${data.tokens_used} tokens</span>
                        <span class="message-meta-item">💰 $${data.cost.toFixed(6)}</span>
                    `;
                    streamingMessage.appendChild(metaDiv);

                    app.updateNextModel(data.next_model);
                    app.updateTokenUsage(data.token_usage);
                    app.showStatus('Response complete', 'success');
                    app.updateGlobalStats({ tokens_used: data.tokens_used, cost: data.cost });

                    if (app.autoMode) {
                        setTimeout(() => app.nextTurn(), 2000);
                    }
                }
            }
        } catch (error) {
            this.showStatus('❌ Error streaming response. Check console for details.', 'error');
            console.error('Streaming error:', error);
            streamingMessage.remove();
            
            // Provide recovery suggestion
            setTimeout(() => {
                const retry = confirm('Streaming failed. Would you like to try again with streaming disabled?');
                if (retry && this.streamingEnabled) {
                    this.toggleStreaming();
                    this.nextTurn(editedMessage);
                }
            }, 1000);
        } finally {
            this.setButtonsDisabled(false);
        }
    }

    toggleStreaming() {
        this.streamingEnabled = !this.streamingEnabled;
        const statusEl = document.getElementById('streaming-status');
        const btn = document.getElementById('streaming-toggle');

        statusEl.textContent = this.streamingEnabled ? 'ON' : 'OFF';
        btn.classList.toggle('btn-success', this.streamingEnabled);
        btn.classList.toggle('btn-secondary', !this.streamingEnabled);

        this.showStatus(`Streaming ${this.streamingEnabled ? 'enabled' : 'disabled'}`, 'info');
    }

    toggleAutoMode() {
        this.autoMode = !this.autoMode;
        const btn = document.getElementById('auto-mode-btn');

        if (this.autoMode) {
            btn.innerHTML = '<span class="btn-icon">⏸️</span> Stop Auto';
            btn.classList.add('btn-danger');
            btn.classList.remove('btn-primary');
            this.nextTurn();
        } else {
            btn.innerHTML = '<span class="btn-icon">▶️</span> Auto Mode';
            btn.classList.add('btn-primary');
            btn.classList.remove('btn-danger');
        }
    }

    displayMessage(message) {
        const messagesContainer = document.getElementById('messages-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;

        const timestamp = new Date(message.timestamp).toLocaleString();
        
        // Debug: Log the message object to console
        console.log('Displaying message:', message);
        console.log('Message content:', message.content);
        
        // Ensure content exists and is not undefined
        const messageContent = message.content || '';
        const content = this.renderMarkdown(messageContent);

        let metaHtml = '';
        if (message.tokens_used || message.cost) {
            metaHtml = `
                <div class="message-meta">
                    ${message.tokens_used ? `<span class="message-meta-item">🎯 ${message.tokens_used} tokens</span>` : ''}
                    ${message.cost ? `<span class="message-meta-item">💰 $${message.cost.toFixed(6)}</span>` : ''}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-model">${this.escapeHtml(message.model || message.role)}</span>
                <span class="message-timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${content}</div>
            ${metaHtml}
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Highlight code blocks
        messageDiv.querySelectorAll('pre code').forEach(block => {
            Prism.highlightElement(block);
        });
    }

    renderMarkdown(text) {
        // Handle empty or undefined text
        if (!text) {
            console.warn('renderMarkdown received empty text:', text);
            return '';
        }
        
        try {
            // Configure marked options
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && Prism.languages[lang]) {
                        return Prism.highlight(code, Prism.languages[lang], lang);
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });

            const rendered = marked.parse(text);
            console.log('Rendered markdown:', rendered.substring(0, 100) + '...');
            return rendered;
        } catch (error) {
            console.error('Error rendering markdown:', error);
            // Fallback to plain text with HTML escaping
            return this.escapeHtml(text);
        }
    }

    updateTokenUsage(tokenUsage) {
        if (!tokenUsage) return;

        this.tokenUsage = tokenUsage;

        const statsEl = document.getElementById('token-stats');
        const fillEl = document.getElementById('token-progress-fill');
        const warningEl = document.getElementById('token-warning');

        statsEl.textContent = `${tokenUsage.used.toLocaleString()} / ${tokenUsage.max.toLocaleString()} tokens`;
        fillEl.style.width = `${tokenUsage.percentage}%`;

        if (tokenUsage.warning) {
            fillEl.classList.add('warning');
            warningEl.style.display = 'block';
        } else {
            fillEl.classList.remove('warning');
            warningEl.style.display = 'none';
        }
    }

    updateGlobalStats(message) {
        const statsEl = document.getElementById('global-stats');
        statsEl.style.display = 'flex';

        const messagesCount = document.querySelectorAll('.message').length;
        const totalTokens = parseInt(document.getElementById('total-tokens').textContent) + (message.tokens_used || 0);
        const totalCost = parseFloat(document.getElementById('total-cost').textContent) + (message.cost || 0);

        document.getElementById('total-messages').textContent = messagesCount;
        document.getElementById('total-tokens').textContent = totalTokens.toLocaleString();
        document.getElementById('total-cost').textContent = totalCost.toFixed(4);
    }

    updateConversationMeta() {
        const metaEl = document.getElementById('conversation-meta');
        metaEl.textContent = `${this.currentConfig.models.length} models • Started ${new Date().toLocaleString()}`;
    }

    updateNextModel(modelName) {
        document.getElementById('next-model-text').textContent = `Next: ${modelName}`;
    }

    async exportConversation() {
        if (!this.conversationId) return;

        try {
            const response = await fetch(`/api/conversation/${this.conversationId}/export`);
            const data = await response.json();

            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversation_${this.conversationId}_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);

            this.showStatus('Conversation exported successfully', 'success');
        } catch (error) {
            this.showStatus('Error exporting conversation', 'error');
        }
    }

    newConversation() {
        // Confirm if there's an active conversation
        if (this.conversationId) {
            const confirmed = confirm('Start a new conversation? Current conversation will remain saved but you\'ll need to export it if you want to keep it.');
            if (!confirmed) return;
        }

        if (this.autoMode) {
            this.toggleAutoMode();
        }

        this.conversationId = null;
        this.tokenUsage = null;
        document.getElementById('messages-container').innerHTML = '';
        document.getElementById('global-stats').style.display = 'none';
        document.getElementById('total-messages').textContent = '0';
        document.getElementById('total-tokens').textContent = '0';
        document.getElementById('total-cost').textContent = '0.00';
        document.getElementById('config-panel').style.display = 'block';
        document.getElementById('conversation-panel').style.display = 'none';
        this.showStatus('✨ Ready for new conversation', 'success');
    }

    showConversationPanel() {
        document.getElementById('config-panel').style.display = 'none';
        document.getElementById('conversation-panel').style.display = 'flex';
    }

    sendEdited() {
        const editedMessage = document.getElementById('edit-message').value;
        this.hideEditPanel();
        this.nextTurn(editedMessage);
    }

    sendOriginal() {
        this.hideEditPanel();
        this.nextTurn();
    }

    cancelEdit() {
        this.hideEditPanel();
    }

    hideEditPanel() {
        document.getElementById('edit-panel').style.display = 'none';
        document.getElementById('edit-message').value = '';
    }

    showStatus(message, type = 'info', duration = 0) {
        const statusText = document.getElementById('status-text');
        const statusBar = document.getElementById('status-bar');

        statusText.innerHTML = message;

        // Remove existing status classes
        statusBar.className = 'status-bar';

        // Add type-specific styling
        switch(type) {
            case 'success':
                statusText.style.color = 'var(--success-color)';
                if (duration === 0) duration = 3000; // Auto-dismiss success after 3s
                break;
            case 'error':
                statusText.style.color = 'var(--danger-color)';
                if (duration === 0) duration = 5000; // Keep errors longer
                break;
            case 'warning':
                statusText.style.color = 'var(--warning-color)';
                if (duration === 0) duration = 4000;
                break;
            case 'loading':
                statusText.style.color = 'var(--primary-color)';
                statusText.innerHTML = message + ' <span class="loading-spinner">⏳</span>';
                break;
            default:
                statusText.style.color = 'var(--text-secondary)';
                if (duration === 0) duration = 3000;
        }

        // Auto-dismiss if duration is set
        if (duration > 0 && type !== 'loading') {
            setTimeout(() => {
                if (statusText.innerHTML === message) {
                    statusText.innerHTML = 'Ready';
                    statusText.style.color = 'var(--text-secondary)';
                }
            }, duration);
        }
    }

    setButtonsDisabled(disabled) {
        document.getElementById('next-turn-btn').disabled = disabled;
        document.getElementById('auto-mode-btn').disabled = disabled;
        document.getElementById('export-btn').disabled = disabled;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ConversationApp();
});
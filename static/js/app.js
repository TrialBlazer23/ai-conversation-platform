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

            this.searchResults = [];
        this.historyOffset = 0;
        this.historyLimit = 20;
        this.showingFavorites = false;

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadProviders();
        await this.loadTemplates();
        await this.checkOllamaStatus();
        this.loadConfig();
        this.addModelConfig(); // Add first model by default
        this.detectColorScheme(); // Auto-detect dark mode preference
        await this.loadConversationHistory(); // Load history sidebar

        // Setup search event listeners
        const searchBtn = document.getElementById('conversation-search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchConversations());
        }
        const searchInput = document.getElementById('conversation-search-input');
        if (searchInput) {
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.searchConversations();
            });
        }
    }

    async searchConversations() {
        // Get filter values
        const q = document.getElementById('conversation-search-input').value.trim();
        const model = document.getElementById('conversation-search-model').value;
        const status = document.getElementById('conversation-search-status').value;
        const favoritesOnly = document.getElementById('conversation-search-favorites')?.checked || false;
        const startDate = document.getElementById('conversation-search-start-date').value;
        const endDate = document.getElementById('conversation-search-end-date').value;

        // Build query string
        const params = new URLSearchParams();
        if (q) params.append('q', q);
        if (model) params.append('model', model);
        if (status) params.append('status', status);
        if (favoritesOnly) params.append('favorites_only', 'true');
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        this.showStatus('Searching conversations...', 'loading');
        try {
            const response = await fetch(`/api/conversations/search?${params.toString()}`);
            this.searchResults = await response.json();
            this.renderSearchResults();
            this.showStatus(`Found ${this.searchResults.length} conversations`, 'success');
        } catch (error) {
            this.showStatus('Error searching conversations', 'error');
            console.error('Search error:', error);
        }
    }

    renderSearchResults() {
        // Display search results in the conversation panel with enhanced features
        const container = document.getElementById('messages-container');
        if (!container) return;
        if (this.searchResults.length === 0) {
            container.innerHTML = '<div class="no-results">No conversations found.</div>';
            return;
        }
        container.innerHTML = this.searchResults.map(conv => `
            <div class="conversation-result" data-conversation-id="${conv.id}">
                <div class="result-header">
                    <div class="result-title-section">
                        <button class="favorite-btn ${conv.is_favorite ? 'favorited' : ''}" 
                                onclick="app.toggleFavorite('${conv.id}')" 
                                title="${conv.is_favorite ? 'Remove from favorites' : 'Add to favorites'}">
                            ★
                        </button>
                        <span class="result-title editable-title" 
                              onclick="app.editTitle('${conv.id}', this)"
                              title="Click to edit title">
                            ${this.escapeHtml(conv.display_title || conv.initial_prompt.slice(0, 60))}${(!conv.display_title && conv.initial_prompt.length > 60) ? '...' : ''}
                        </span>
                    </div>
                    <span class="result-date">${new Date(conv.created_at).toLocaleString()}</span>
                </div>
                <div class="result-meta">
                    <span class="result-status">Status: ${conv.status}</span>
                    <span class="result-tokens">Tokens: ${conv.total_tokens}</span>
                    <span class="result-cost">Cost: $${conv.total_cost.toFixed(4)}</span>
                </div>
                <div class="result-actions">
                    <button class="btn btn-sm btn-primary" onclick="app.loadConversationById('${conv.id}')">Open</button>
                    <button class="btn btn-sm btn-secondary" onclick="app.exportConversation('${conv.id}')">Export</button>
                    <button class="btn btn-sm btn-outline" onclick="app.duplicateConversation('${conv.id}')">Duplicate</button>
                    <button class="btn btn-sm btn-danger" onclick="app.deleteConversation('${conv.id}')" title="Delete conversation">🗑️ Delete</button>
                </div>
            </div>
        `).join('');
    }

    async loadConversationById(conversationId) {
        // TODO: Implement loading a conversation by ID and displaying its messages
        this.showStatus(`Loading conversation ${conversationId}...`, 'loading');
        // ...existing code to load and display conversation...
    }
    async searchConversations() {
        // Get filter values
        const q = document.getElementById('conversation-search-input').value.trim();
        const model = document.getElementById('conversation-search-model').value;
        const status = document.getElementById('conversation-search-status').value;
        const startDate = document.getElementById('conversation-search-start-date').value;
        const endDate = document.getElementById('conversation-search-end-date').value;

        // Build query string
        const params = new URLSearchParams();
        if (q) params.append('q', q);
        if (model) params.append('model', model);
        if (status) params.append('status', status);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        this.showStatus('Searching conversations...', 'loading');
        try {
            const response = await fetch(`/api/conversations/search?${params.toString()}`);
            this.searchResults = await response.json();
            this.renderSearchResults();
            this.showStatus(`Found ${this.searchResults.length} conversations`, 'success');
        } catch (error) {
            this.showStatus('Error searching conversations', 'error');
            console.error('Search error:', error);
        }
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

        // History sidebar controls
        document.getElementById('toggle-history-btn').addEventListener('click', () => this.toggleHistorySidebar());
        document.getElementById('show-all-btn').addEventListener('click', () => this.showAllHistory());
        document.getElementById('show-favorites-btn').addEventListener('click', () => this.showFavoritesHistory());

        // Initial prompt character counter
        document.getElementById('initial-prompt').addEventListener('input', (e) => this.updatePromptStats(e.target.value));
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

    async saveConfig() {
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

        this.currentConfig = { api_keys: apiKeys, models };

        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentConfig)
            });

            const result = await response.json();
            this.showStatus('Configuration saved successfully!', 'success');
            return true; // Indicate success
        } catch (error) {
            this.showStatus('Error saving configuration', 'error');
            console.error('Save config error:', error);
            return false; // Indicate failure
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
            this.showStatus('Please enter an initial prompt', 'error');
            return;
        }

        // Auto-save config before starting (build config from UI)
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
            this.showStatus('Please configure at least one model', 'error');
            return;
        }

        // Auto-save config
        this.showStatus('Saving configuration...', 'loading');
        const saved = await this.saveConfig();
        
        if (!saved) {
            this.showStatus('Failed to save configuration', 'error');
            return;
        }

        try {
            this.showStatus('Starting conversation...', 'loading');
            
            const response = await fetch('/api/conversation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    initial_prompt: initialPrompt,
                    models: this.currentConfig.models
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.conversationId = data.conversation_id;
                this.showConversationPanel();
                this.displayMessage({
                    role: 'user',
                    content: initialPrompt,
                    model: 'You',
                    timestamp: new Date().toISOString()
                });
                this.updateNextModel(this.currentConfig.models[0].name);
                this.showStatus('Conversation started - ready for first response', 'success');
                this.updateConversationMeta();
            } else {
                this.showStatus(`Error: ${data.message || 'Failed to start conversation'}`, 'error');
            }
        } catch (error) {
            this.showStatus('Error starting conversation', 'error');
            console.error('Start conversation error:', error);
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
            this.showStatus('Error streaming response', 'error');
            console.error(error);
            streamingMessage.remove();
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
        const timeAgo = window.UIEnhancements ? 
            window.UIEnhancements.formatTimeAgo(message.timestamp) : 
            timestamp;
        
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
                <span class="message-timestamp" data-iso="${message.timestamp}" title="${timestamp}">${timeAgo}</span>
            </div>
            <div class="message-content">${content}</div>
            ${metaHtml}
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add copy button if available
        if (window.UIEnhancements) {
            window.UIEnhancements.addCopyButton(messageDiv, messageContent);
        }

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

        // Show export format options
        const format = await this.showExportFormatDialog();
        if (!format) return; // User cancelled

        try {
            let response, blob, filename, mimeType;
            
            if (format === 'json') {
                response = await fetch(`/api/conversation/${this.conversationId}/export`);
                const data = await response.json();
                blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                filename = `conversation_${this.conversationId.slice(0, 8)}.json`;
                mimeType = 'application/json';
            } else if (format === 'markdown') {
                response = await fetch(`/api/conversation/${this.conversationId}/export/markdown`);
                if (!response.ok) throw new Error('Export failed');
                
                const markdownContent = await response.text();
                blob = new Blob([markdownContent], { type: 'text/markdown' });
                filename = `conversation_${this.conversationId.slice(0, 8)}.md`;
                mimeType = 'text/markdown';
            }

            // Download the file
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.showStatus(`Conversation exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            this.showStatus('Error exporting conversation', 'error');
            console.error('Export error:', error);
        }
    }

    showExportFormatDialog() {
        return new Promise((resolve) => {
            // Create modal dialog for format selection
            const modal = document.createElement('div');
            modal.className = 'export-modal-overlay';
            modal.innerHTML = `
                <div class="export-modal">
                    <h3>📥 Export Conversation</h3>
                    <p>Choose the export format:</p>
                    <div class="export-format-options">
                        <button class="export-format-btn" data-format="markdown">
                            <span class="format-icon">📝</span>
                            <span class="format-name">Markdown</span>
                            <span class="format-desc">Human-readable, formatted text</span>
                        </button>
                        <button class="export-format-btn" data-format="json">
                            <span class="format-icon">📋</span>
                            <span class="format-name">JSON</span>
                            <span class="format-desc">Complete data with metadata</span>
                        </button>
                    </div>
                    <div class="export-modal-actions">
                        <button class="btn btn-secondary export-cancel">Cancel</button>
                    </div>
                </div>
            `;

            // Add event listeners
            modal.addEventListener('click', (e) => {
                if (e.target.classList.contains('export-modal-overlay') || 
                    e.target.classList.contains('export-cancel')) {
                    document.body.removeChild(modal);
                    resolve(null);
                }
                
                if (e.target.closest('.export-format-btn')) {
                    const format = e.target.closest('.export-format-btn').dataset.format;
                    document.body.removeChild(modal);
                    resolve(format);
                }
            });

            // Handle Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    document.body.removeChild(modal);
                    document.removeEventListener('keydown', escapeHandler);
                    resolve(null);
                }
            };
            document.addEventListener('keydown', escapeHandler);

            document.body.appendChild(modal);
        });
    }

    newConversation() {
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
        this.showStatus('Ready for new conversation', 'success');
    }

        // Edit title inline
    editTitle(conversationId, titleElement) {
        const currentTitle = titleElement.textContent.trim();
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentTitle;
        input.className = 'title-editor';
        input.style.cssText = 'width: 100%; font-size: inherit; border: 1px solid #ccc; padding: 2px 5px;';
        
        // Replace the span with input
        titleElement.style.display = 'none';
        titleElement.parentNode.insertBefore(input, titleElement.nextSibling);
        input.focus();
        input.select();
        
        const saveTitle = async () => {
            const newTitle = input.value.trim();
            if (newTitle && newTitle !== currentTitle) {
                const success = await this.updateConversationTitle(conversationId, newTitle);
                if (success) {
                    titleElement.textContent = newTitle;
                    // Update the search results data
                    const conv = this.searchResults.find(c => c.id === conversationId);
                    if (conv) conv.display_title = newTitle;
                }
            }
            
            // Restore the span and remove input
            titleElement.style.display = '';
            input.remove();
        };
        
        const cancelEdit = () => {
            titleElement.style.display = '';
            input.remove();
        };
        
        input.addEventListener('blur', saveTitle);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveTitle();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEdit();
            }
        });
    }

    // Quick wins features
    async toggleFavorite(conversationId) {
        if (!conversationId) return;
        
        try {
            const response = await fetch(`/api/conversation/${conversationId}/favorite`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showStatus(data.message, 'success');
                // Update UI if needed
                const favoriteBtn = document.querySelector(`[data-conversation-id="${conversationId}"] .favorite-btn`);
                if (favoriteBtn) {
                    favoriteBtn.textContent = data.is_favorite ? '⭐' : '☆';
                    favoriteBtn.title = data.is_favorite ? 'Remove from favorites' : 'Add to favorites';
                }
            } else {
                this.showStatus(data.message, 'error');
            }
        } catch (error) {
            this.showStatus('Error toggling favorite', 'error');
            console.error('Favorite error:', error);
        }
    }

    async updateConversationTitle(conversationId, newTitle) {
        if (!conversationId) return;
        
        try {
            const response = await fetch(`/api/conversation/${conversationId}/title`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle })
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showStatus(data.message, 'success');
                return data.display_title;
            } else {
                this.showStatus(data.message, 'error');
                return null;
            }
        } catch (error) {
            this.showStatus('Error updating title', 'error');
            console.error('Title update error:', error);
            return null;
        }
    }

    async duplicateConversation(conversationId) {
        if (!conversationId) return;
        
        try {
            const response = await fetch(`/api/conversation/${conversationId}/duplicate`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showStatus(data.message, 'success');
                // Reload history to show new conversation
                await this.loadConversationHistory();
                return data.new_conversation_id;
            } else {
                this.showStatus(data.message, 'error');
                return null;
            }
        } catch (error) {
            this.showStatus('Error duplicating conversation', 'error');
            console.error('Duplication error:', error);
            return null;
        }
    }

    // Conversation History Sidebar Methods
    async loadConversationHistory(append = false) {
        try {
            const params = new URLSearchParams();
            params.append('limit', this.historyLimit);
            params.append('offset', append ? this.historyOffset : 0);
            if (this.showingFavorites) {
                params.append('favorites_only', 'true');
            }

            const response = await fetch(`/api/conversations/history?${params.toString()}`);
            const data = await response.json();

            if (!append) {
                this.historyOffset = 0;
            }

            this.renderConversationHistory(data.conversations, append);
            this.historyOffset += data.conversations.length;

            // Add "Load More" button if there are more conversations
            if (data.has_more) {
                this.addLoadMoreButton();
            }
        } catch (error) {
            console.error('Error loading history:', error);
            document.getElementById('history-list').innerHTML = '<div class="error-history">Failed to load history</div>';
        }
    }

    renderConversationHistory(conversations, append = false) {
        const container = document.getElementById('history-list');

        if (!append) {
            container.innerHTML = '';
        } else {
            // Remove "Load More" button if it exists
            const loadMore = container.querySelector('.load-more-history');
            if (loadMore) loadMore.remove();
        }

        if (conversations.length === 0 && !append) {
            container.innerHTML = '<div class="empty-history">No conversations yet</div>';
            return;
        }

        const historyHTML = conversations.map(conv => `
            <div class="history-item ${conv.id === this.conversationId ? 'active' : ''}" 
                 data-conversation-id="${conv.id}">
                <div class="history-item-header">
                    <button class="history-favorite-btn ${conv.is_favorite ? 'favorited' : ''}" 
                            onclick="app.toggleFavorite('${conv.id}'); event.stopPropagation();"
                            title="${conv.is_favorite ? 'Remove from favorites' : 'Add to favorites'}">
                        ★
                    </button>
                    <span class="history-title" onclick="app.loadConversationById('${conv.id}')">
                        ${this.escapeHtml(conv.display_title || conv.initial_prompt.slice(0, 40))}${(!conv.display_title && conv.initial_prompt.length > 40) ? '...' : ''}
                    </span>
                </div>
                <div class="history-item-meta">
                    <span class="history-date">${this.formatRelativeTime(conv.updated_at)}</span>
                    <span class="history-cost">$${conv.total_cost.toFixed(4)}</span>
                </div>
            </div>
        `).join('');

        container.insertAdjacentHTML('beforeend', historyHTML);
    }

    addLoadMoreButton() {
        const container = document.getElementById('history-list');
        const loadMoreBtn = document.createElement('button');
        loadMoreBtn.className = 'load-more-history btn btn-sm btn-secondary';
        loadMoreBtn.textContent = 'Load More';
        loadMoreBtn.onclick = () => this.loadConversationHistory(true);
        container.appendChild(loadMoreBtn);
    }

    toggleHistorySidebar() {
        const sidebar = document.getElementById('history-sidebar');
        const btn = document.getElementById('toggle-history-btn');
        sidebar.classList.toggle('collapsed');
        btn.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
    }

    async showAllHistory() {
        this.showingFavorites = false;
        document.getElementById('show-all-btn').className = 'btn btn-sm btn-secondary';
        document.getElementById('show-favorites-btn').className = 'btn btn-sm btn-outline';
        await this.loadConversationHistory();
    }

    async showFavoritesHistory() {
        this.showingFavorites = true;
        document.getElementById('show-all-btn').className = 'btn btn-sm btn-outline';
        document.getElementById('show-favorites-btn').className = 'btn btn-sm btn-secondary';
        await this.loadConversationHistory();
    }

    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }


    async deleteConversation(conversationId) {
        if (!conversationId) return;
        
        // Confirmation dialog
        const confirmed = confirm('Are you sure you want to delete this conversation? This action cannot be undone.');
        if (!confirmed) return false;
        
        try {
            const response = await fetch(`/api/conversation/${conversationId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showStatus(data.message, 'success');
                
                // Remove from search results if displayed
                this.searchResults = this.searchResults.filter(conv => conv.id !== conversationId);
                this.renderSearchResults();
                
                return true;
            } else {
                this.showStatus(data.message, 'error');
                return false;
            }
        } catch (error) {
            this.showStatus('Error deleting conversation', 'error');
            console.error('Delete error:', error);
            return false;
        }
    }

    // Auto-detect system dark mode preference
    detectColorScheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const currentTheme = document.documentElement.getAttribute('data-theme');
        
        // Only set if no theme is currently set
        if (!currentTheme) {
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
            localStorage.setItem('theme', prefersDark ? 'dark' : 'light');
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const storedTheme = localStorage.getItem('theme');
            // Only auto-change if user hasn't manually set a preference
            if (!storedTheme) {
                document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
            }
        });
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

    showStatus(message, type = 'info') {
        const statusText = document.getElementById('status-text');
        const statusBar = document.getElementById('status-bar');

        statusText.innerHTML = message;

        // Remove existing status classes
        statusBar.className = 'status-bar';

        // Add type-specific styling
        switch(type) {
            case 'success':
                statusText.style.color = 'var(--success-color)';
                break;
            case 'error':
                statusText.style.color = 'var(--danger-color)';
                break;
            case 'warning':
                statusText.style.color = 'var(--warning-color)';
                break;
            case 'loading':
                statusText.style.color = 'var(--primary-color)';
                statusText.innerHTML = message + ' <span class="loading-spinner"></span>';
                break;
            default:
                statusText.style.color = 'var(--text-secondary)';
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
    
    // Initialize UI enhancements if available
    if (window.UIEnhancements) {
        window.UIEnhancements.setupKeyboardShortcuts(app);
        window.UIEnhancements.startTimestampUpdater();
        window.UIEnhancements.setupApiKeyValidation();
        window.UIEnhancements.addTooltips();
        console.log('✨ UI enhancements loaded');
    }
    
    // Show welcome notification
    if (window.notifications) {
        notifications.show('Welcome to AI Conversation Platform! Use Ctrl+Enter to send, Ctrl+N for new conversation.', 'info', 5000);
    }
});
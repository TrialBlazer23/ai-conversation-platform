/**
 * UI Enhancements - Keyboard shortcuts, copy buttons, and time formatting
 */

// Add to ConversationApp class or standalone utilities

/**
 * Format timestamp to human-readable "time ago" format
 */
function formatTimeAgo(timestamp) {
    const now = new Date();
    const past = new Date(timestamp);
    const secondsAgo = Math.floor((now - past) / 1000);
    
    if (secondsAgo < 10) return 'just now';
    if (secondsAgo < 60) return `${secondsAgo}s ago`;
    
    const minutesAgo = Math.floor(secondsAgo / 60);
    if (minutesAgo < 60) return `${minutesAgo}m ago`;
    
    const hoursAgo = Math.floor(minutesAgo / 60);
    if (hoursAgo < 24) return `${hoursAgo}h ago`;
    
    const daysAgo = Math.floor(hoursAgo / 24);
    if (daysAgo < 7) return `${daysAgo}d ago`;
    
    // For older messages, show actual date
    return past.toLocaleDateString();
}

/**
 * Add copy button to a message element
 */
function addCopyButton(messageDiv, content) {
    const messageHeader = messageDiv.querySelector('.message-header');
    if (!messageHeader) return;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.innerHTML = '📋';
    copyBtn.title = 'Copy message';
    copyBtn.setAttribute('aria-label', 'Copy message to clipboard');
    
    copyBtn.onclick = async (e) => {
        e.stopPropagation();
        try {
            await navigator.clipboard.writeText(content);
            copyBtn.innerHTML = '✅';
            copyBtn.classList.add('copied');
            notifications.show('Message copied to clipboard!', 'success', 2000);
            
            setTimeout(() => {
                copyBtn.innerHTML = '📋';
                copyBtn.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
            notifications.show('Failed to copy message', 'error');
        }
    };
    
    messageHeader.appendChild(copyBtn);
}

/**
 * Setup global keyboard shortcuts
 */
function setupKeyboardShortcuts(app) {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter: Send next turn
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (app.conversationId && !document.getElementById('next-turn-btn').disabled) {
                app.nextTurn();
                notifications.show('Generating next response...', 'loading', 2000);
            }
        }
        
        // Ctrl/Cmd + N: New conversation
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            if (confirm('Start a new conversation? Current conversation will be saved.')) {
                app.newConversation();
                notifications.show('Ready for new conversation', 'info');
            }
        }
        
        // Ctrl/Cmd + S: Save configuration
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            app.saveConfig();
        }
        
        // Ctrl/Cmd + E: Export conversation
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            if (app.conversationId) {
                app.exportConversation();
            }
        }
        
        // Ctrl/Cmd + ?: Show keyboard shortcuts help
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcutsHelp();
        }
    });
}

/**
 * Show keyboard shortcuts help dialog
 */
function showKeyboardShortcutsHelp() {
    const helpHtml = `
        <div class="shortcuts-help">
            <h3>⌨️ Keyboard Shortcuts</h3>
            <div class="shortcut-list">
                <div class="shortcut-item">
                    <kbd>Ctrl/Cmd</kbd> + <kbd>Enter</kbd>
                    <span>Generate next response</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl/Cmd</kbd> + <kbd>N</kbd>
                    <span>New conversation</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl/Cmd</kbd> + <kbd>S</kbd>
                    <span>Save configuration</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl/Cmd</kbd> + <kbd>E</kbd>
                    <span>Export conversation</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl/Cmd</kbd> + <kbd>/</kbd>
                    <span>Show this help</span>
                </div>
            </div>
            <button onclick="this.closest('.shortcuts-help').remove()" class="btn btn-primary">Got it!</button>
        </div>
    `;
    
    const overlay = document.createElement('div');
    overlay.className = 'shortcuts-overlay';
    overlay.innerHTML = helpHtml;
    overlay.onclick = (e) => {
        if (e.target === overlay) overlay.remove();
    };
    
    document.body.appendChild(overlay);
}
        
        // Escape: Cancel auto mode if running
        if (e.key === 'Escape' && app.autoMode) {
            e.preventDefault();
            app.toggleAutoMode();
            notifications.show('Auto mode stopped', 'info');
        }
    });
    
    console.log('⌨️  Keyboard shortcuts enabled:');
    console.log('  • Ctrl/Cmd + Enter: Generate next response');
    console.log('  • Ctrl/Cmd + N: New conversation');
    console.log('  • Ctrl/Cmd + S: Save configuration');
    console.log('  • Ctrl/Cmd + E: Export conversation');
    console.log('  • Escape: Stop auto mode');
}

/**
 * Update timestamps periodically
 */
function startTimestampUpdater() {
    setInterval(() => {
        document.querySelectorAll('.message-timestamp[data-iso]').forEach(el => {
            const isoTime = el.getAttribute('data-iso');
            el.textContent = formatTimeAgo(isoTime);
            el.title = new Date(isoTime).toLocaleString();
        });
    }, 30000); // Update every 30 seconds
}

/**
 * Add loading animation to buttons
 */
function setButtonLoading(buttonId, isLoading, loadingText = 'Loading...') {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    if (isLoading) {
        button.setAttribute('data-original-text', button.innerHTML);
        button.innerHTML = `<span class="loading-spinner"></span> ${loadingText}`;
        button.disabled = true;
        button.classList.add('loading');
    } else {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
        button.disabled = false;
        button.classList.remove('loading');
    }
}

/**
 * Show API key strength indicator
 */
function validateApiKeyFormat(provider, key) {
    const patterns = {
        openai: /^sk-[A-Za-z0-9]{48,}$/,
        anthropic: /^sk-ant-[A-Za-z0-9-]{95,}$/,
        google: /^[A-Za-z0-9_-]{39}$/
    };
    
    return patterns[provider]?.test(key) || false;
}

/**
 * Add visual feedback for API key inputs
 */
function setupApiKeyValidation() {
    const apiKeyInputs = [
        { id: 'openai-key', provider: 'openai' },
        { id: 'anthropic-key', provider: 'anthropic' },
        { id: 'google-key', provider: 'google' }
    ];
    
    apiKeyInputs.forEach(({ id, provider }) => {
        const input = document.getElementById(id);
        if (!input) return;
        
        input.addEventListener('input', (e) => {
            const value = e.target.value.trim();
            const indicator = input.parentElement.querySelector('.key-indicator') || 
                           createKeyIndicator(input.parentElement);
            
            if (!value) {
                indicator.textContent = '';
                indicator.className = 'key-indicator';
                return;
            }
            
            const isValid = validateApiKeyFormat(provider, value);
            indicator.textContent = isValid ? '✓ Format valid' : '⚠ Check format';
            indicator.className = `key-indicator ${isValid ? 'valid' : 'warning'}`;
        });
    });
}

function createKeyIndicator(parent) {
    const indicator = document.createElement('span');
    indicator.className = 'key-indicator';
    parent.appendChild(indicator);
    return indicator;
}

/**
 * Add tooltips to UI elements
 */
function addTooltips() {
    const tooltips = {
        'streaming-toggle': 'Toggle real-time streaming responses',
        'auto-mode-btn': 'Automatically generate responses in sequence',
        'next-turn-btn': 'Generate next AI response',
        'export-btn': 'Export conversation as JSON',
        'new-conversation-btn': 'Start a new conversation',
        'save-config-btn': 'Save API keys and model configuration',
        'start-conversation-btn': 'Start the conversation with configured models'
    };
    
    Object.entries(tooltips).forEach(([id, tooltip]) => {
        const element = document.getElementById(id);
        if (element && !element.title) {
            element.title = tooltip;
        }
    });
}

/**
 * Response time tracker
 */
class ResponseTimeTracker {
    constructor() {
        this.startTime = null;
        this.endTime = null;
    }
    
    start() {
        this.startTime = performance.now();
        this.endTime = null;
    }
    
    stop() {
        if (!this.startTime) return null;
        this.endTime = performance.now();
        return this.getElapsedTime();
    }
    
    getElapsedTime() {
        if (!this.startTime) return null;
        const end = this.endTime || performance.now();
        return ((end - this.startTime) / 1000).toFixed(2); // seconds
    }
    
    reset() {
        this.startTime = null;
        this.endTime = null;
    }
}

/**
 * Display response time in UI
 */
function displayResponseTime(elementId, timeInSeconds) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const timeHtml = `
        <span class="response-time">
            ⏱️ ${timeInSeconds}s
        </span>
    `;
    element.innerHTML = timeHtml;
}

/**
 * Model status indicator
 */
class ModelStatusIndicator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.statuses = new Map();
    }
    
    setStatus(modelName, status) {
        // status can be: 'idle', 'thinking', 'streaming', 'error'
        this.statuses.set(modelName, status);
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        const statusIcons = {
            'idle': '⚪',
            'thinking': '🟡',
            'streaming': '🟢',
            'error': '🔴'
        };
        
        const statusLabels = {
            'idle': 'Idle',
            'thinking': 'Thinking...',
            'streaming': 'Responding...',
            'error': 'Error'
        };
        
        let html = '<div class="model-statuses">';
        this.statuses.forEach((status, modelName) => {
            const icon = statusIcons[status] || '⚪';
            const label = statusLabels[status] || 'Unknown';
            html += `
                <div class="model-status model-status-${status}">
                    <span class="status-icon">${icon}</span>
                    <span class="model-name">${modelName}</span>
                    <span class="status-label">${label}</span>
                </div>
            `;
        });
        html += '</div>';
        
        this.container.innerHTML = html;
    }
    
    clear() {
        this.statuses.clear();
        this.render();
    }
}

/**
 * Create typing indicator for a model
 */
function showTypingIndicator(modelName, container) {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = `typing-${modelName}`;
    indicator.innerHTML = `
        <div class="typing-indicator-content">
            <span class="model-name">${modelName}</span>
            <span class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </span>
        </div>
    `;
    
    const messagesContainer = container || document.getElementById('messages-container');
    if (messagesContainer) {
        messagesContainer.appendChild(indicator);
    }
    
    return indicator;
}

/**
 * Remove typing indicator for a model
 */
function hideTypingIndicator(modelName) {
    const indicator = document.getElementById(`typing-${modelName}`);
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Export conversation handler
 */
async function exportConversation(conversationId, format = 'markdown') {
    try {
        const response = await fetch(`/api/conversation/${conversationId}/export/${format}`);
        
        if (format === 'json') {
            const data = await response.json();
            downloadJSON(data, `conversation_${conversationId}.json`);
        } else {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversation_${conversationId}.${format === 'markdown' ? 'md' : 'txt'}`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        notifications.show(`Conversation exported as ${format}`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        notifications.show('Failed to export conversation', 'error');
    }
}

/**
 * Download JSON data as file
 */
function downloadJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Check provider health
 */
async function checkProviderHealth(apiKeys) {
    try {
        const response = await fetch('/api/health/providers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_keys: apiKeys })
        });
        
        const result = await response.json();
        return result.providers;
    } catch (error) {
        console.error('Health check error:', error);
        return {};
    }
}

/**
 * Display provider health status
 */
function displayProviderHealth(healthResults) {
    const container = document.getElementById('provider-health-status');
    if (!container) return;
    
    let html = '<div class="provider-health">';
    Object.entries(healthResults).forEach(([provider, result]) => {
        const statusClass = result.status === 'healthy' ? 'healthy' : 
                          result.status === 'error' ? 'error' : 'warning';
        const icon = result.status === 'healthy' ? '✅' : 
                    result.status === 'error' ? '❌' : '⚠️';
        
        html += `
            <div class="provider-health-item ${statusClass}">
                <span class="health-icon">${icon}</span>
                <span class="provider-name">${provider}</span>
                <span class="health-message">${result.message}</span>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Export functions for use in app.js
window.UIEnhancements = {
    formatTimeAgo,
    addCopyButton,
    setupKeyboardShortcuts,
    showKeyboardShortcutsHelp,
    startTimestampUpdater,
    setButtonLoading,
    setupApiKeyValidation,
    addTooltips,
    ResponseTimeTracker,
    displayResponseTime,
    ModelStatusIndicator,
    showTypingIndicator,
    hideTypingIndicator,
    exportConversation,
    checkProviderHealth,
    displayProviderHealth
};

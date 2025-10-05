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

// Export functions for use in app.js
window.UIEnhancements = {
    formatTimeAgo,
    addCopyButton,
    setupKeyboardShortcuts,
    startTimestampUpdater,
    setButtonLoading,
    setupApiKeyValidation,
    addTooltips
};

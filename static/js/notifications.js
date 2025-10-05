/* Enhanced error handling and notifications */

class NotificationManager {
    constructor() {
        this.container = this.createContainer();
        document.body.appendChild(this.container);
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            loading: '⏳'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${icons[type]}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        notification.style.cssText = `
            background: ${this.getBackgroundColor(type)};
            color: white;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
            display: flex;
            align-items: center;
            gap: 10px;
        `;

        this.container.appendChild(notification);

        if (duration > 0) {
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }

        return notification;
    }

    getBackgroundColor(type) {
        const colors = {
            success: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            error: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            warning: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            info: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            loading: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
        };
        return colors[type] || colors.info;
    }

    showApiError(error, provider) {
        const errorMessages = {
            401: `Invalid API key for ${provider}. Please check your configuration.`,
            403: `Access forbidden for ${provider}. Verify your API key permissions.`,
            429: `Rate limit exceeded for ${provider}. Please wait a moment and try again.`,
            500: `${provider} server error. The service may be experiencing issues.`,
            503: `${provider} is temporarily unavailable. Please try again later.`,
        };

        const message = errorMessages[error.status] || 
            `An error occurred with ${provider}: ${error.message}`;

        this.show(message, 'error', 10000);
    }

    showRetryProgress(attempt, maxAttempts) {
        return this.show(
            `Connection failed. Retrying (${attempt}/${maxAttempts})...`,
            'warning',
            0  // Don't auto-dismiss
        );
    }

    showStreamingStatus(modelName, status) {
        const messages = {
            'starting': `${modelName} is preparing to respond...`,
            'streaming': `${modelName} is responding...`,
            'complete': `${modelName} finished responding`,
            'error': `${modelName} encountered an error`
        };

        const types = {
            'starting': 'loading',
            'streaming': 'info',
            'complete': 'success',
            'error': 'error'
        };

        this.show(messages[status], types[status], status === 'complete' ? 3000 : 0);
    }
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
        opacity: 0.8;
        transition: opacity 0.2s;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
    }

    .notification-icon {
        font-size: 20px;
        flex-shrink: 0;
    }

    .notification-message {
        flex: 1;
        line-height: 1.4;
    }
`;
document.head.appendChild(style);

// Initialize globally
window.notifications = new NotificationManager();

// Example usage in ConversationApp:
/*
async nextTurnStreaming(editedMessage = null) {
    const streamNotification = notifications.showStreamingStatus(currentModel, 'starting');
    
    try {
        // ... streaming code ...
        
        if (data.type === 'metadata') {
            streamNotification.remove();
            notifications.showStreamingStatus(data.model, 'streaming');
        }
        
        if (data.type === 'done') {
            notifications.showStreamingStatus(currentModel, 'complete');
        }
        
    } catch (error) {
        streamNotification.remove();
        notifications.showApiError(error, currentProvider);
        notifications.showStreamingStatus(currentModel, 'error');
    }
}
*/

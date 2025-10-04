"""
Token counting and management utilities
Follows Single Responsibility - only handles token operations
"""
from typing import List, Dict, Optional
import tiktoken
from config import Config


class TokenCounter:
    """
    Token counting and context management
    Uses tiktoken for accurate token counting
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize token counter for specific model
        
        Args:
            model: Model name to determine encoding
        """
        self.model = model
        self.encoding = self._get_encoding(model)
        self.max_tokens = Config.MODEL_LIMITS.get(model, Config.MODEL_LIMITS['default'])
    
    def _get_encoding(self, model: str):
        """Get appropriate encoding for model"""
        try:
            # Try to get model-specific encoding
            return tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base (used by gpt-4, gpt-3.5-turbo)
            return tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict]) -> int:
        """
        Count tokens in a list of messages
        Accounts for message formatting overhead
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Total number of tokens
        """
        num_tokens = 0
        
        for message in messages:
            # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4  # Message formatting overhead
            
            for key, value in message.items():
                num_tokens += self.count_tokens(str(value))
                if key == "name":  # If there's a name, the role is omitted
                    num_tokens += -1  # Role is always required and always 1 token
        
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        
        return num_tokens
    
    def get_context_usage(self, messages: List[Dict]) -> Dict:
        """
        Get detailed context window usage information
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary with usage statistics
        """
        used_tokens = self.count_messages_tokens(messages)
        available_tokens = self.max_tokens - used_tokens - Config.TOKEN_LIMIT_BUFFER
        percentage = (used_tokens / self.max_tokens) * 100
        
        return {
            'used': used_tokens,
            'max': self.max_tokens,
            'available': max(0, available_tokens),
            'percentage': round(percentage, 2),
            'warning': percentage >= (Config.TOKEN_WARNING_THRESHOLD * 100),
            'exceeded': used_tokens >= self.max_tokens
        }
    
    def trim_messages(self, messages: List[Dict], target_tokens: Optional[int] = None) -> List[Dict]:
        """
        Trim messages to fit within token limit
        Keeps system message and most recent messages
        
        Args:
            messages: List of message dictionaries
            target_tokens: Target token count (defaults to max - buffer)
            
        Returns:
            Trimmed list of messages
        """
        if target_tokens is None:
            target_tokens = self.max_tokens - Config.TOKEN_LIMIT_BUFFER
        
        # Always keep system message if present
        system_messages = [m for m in messages if m.get('role') == 'system']
        other_messages = [m for m in messages if m.get('role') != 'system']
        
        # Start with system messages
        trimmed = system_messages.copy()
        current_tokens = self.count_messages_tokens(trimmed)
        
        # Add messages from most recent backwards until we hit limit
        for message in reversed(other_messages):
            message_tokens = self.count_messages_tokens([message])
            if current_tokens + message_tokens <= target_tokens:
                trimmed.insert(len(system_messages), message)
                current_tokens += message_tokens
            else:
                break
        
        return trimmed
    
    def should_summarize(self, messages: List[Dict]) -> bool:
        """
        Check if conversation should be summarized
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            True if summarization recommended
        """
        usage = self.get_context_usage(messages)
        return usage['warning']
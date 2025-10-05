"""
Response caching for AI providers
"""
import hashlib
import json
import time
from typing import Optional, Any
from functools import wraps


class ResponseCache:
    """
    Simple in-memory cache for AI responses with TTL
    """
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (default 1 hour)
            max_size: Maximum number of cached items
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache = {}
        self._timestamps = {}
        
    def _generate_key(self, provider: str, model: str, messages: list, temperature: float) -> str:
        """Generate cache key from request parameters"""
        key_data = {
            'provider': provider,
            'model': model,
            'messages': messages,
            'temperature': round(temperature, 2)  # Round to avoid float precision issues
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, provider: str, model: str, messages: list, temperature: float) -> Optional[str]:
        """
        Get cached response if available and not expired
        
        Returns:
            Cached response or None
        """
        key = self._generate_key(provider, model, messages, temperature)
        
        if key not in self._cache:
            return None
        
        # Check if expired
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, provider: str, model: str, messages: list, temperature: float, response: str):
        """
        Cache a response
        """
        # Implement simple LRU by removing oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._timestamps.keys(), key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        key = self._generate_key(provider, model, messages, temperature)
        self._cache[key] = response
        self._timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cached items"""
        self._cache.clear()
        self._timestamps.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        current_time = time.time()
        active_items = sum(
            1 for timestamp in self._timestamps.values()
            if current_time - timestamp <= self.ttl
        )
        
        return {
            'total_items': len(self._cache),
            'active_items': active_items,
            'max_size': self.max_size,
            'ttl': self.ttl
        }


# Global cache instance
_global_cache = ResponseCache()


def get_cache() -> ResponseCache:
    """Get the global cache instance"""
    return _global_cache


def with_cache(enabled: bool = True):
    """
    Decorator to add caching to provider methods
    
    Usage:
        @with_cache(enabled=True)
        def generate_response(self, messages):
            # Your implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, messages, *args, **kwargs):
            if not enabled:
                return func(self, messages, *args, **kwargs)
            
            cache = get_cache()
            provider_name = self.__class__.__name__
            
            # Try to get from cache
            cached_response = cache.get(
                provider_name,
                self.model,
                messages,
                self.temperature
            )
            
            if cached_response is not None:
                return cached_response
            
            # Generate new response
            response = func(self, messages, *args, **kwargs)
            
            # Cache the response
            cache.set(
                provider_name,
                self.model,
                messages,
                self.temperature,
                response
            )
            
            return response
        
        return wrapper
    return decorator

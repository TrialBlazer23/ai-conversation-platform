"""
Tests for retry handler utility
"""
import pytest
import time
from unittest.mock import Mock, patch
from utils.retry_handler import RetryHandler, with_retry, RateLimitHandler


class TestRetryHandler:
    """Test RetryHandler class"""
    
    def test_retry_success_on_first_attempt(self):
        """Test successful execution on first attempt"""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        mock_func = Mock(return_value="success")
        result = handler.retry_with_backoff(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test successful execution after some failures"""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        mock_func = Mock(side_effect=[Exception("Error 1"), Exception("Error 2"), "success"])
        result = handler.retry_with_backoff(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted(self):
        """Test that retries are exhausted after max attempts"""
        handler = RetryHandler(max_retries=2, base_delay=0.1)
        
        mock_func = Mock(side_effect=Exception("Persistent error"))
        
        with pytest.raises(Exception, match="Persistent error"):
            handler.retry_with_backoff(mock_func)
        
        assert mock_func.call_count == 2
    
    def test_exponential_backoff_timing(self):
        """Test that backoff delays increase exponentially"""
        handler = RetryHandler(max_retries=3, base_delay=0.1)
        
        call_times = []
        
        def failing_func():
            call_times.append(time.time())
            raise Exception("Error")
        
        try:
            handler.retry_with_backoff(failing_func)
        except Exception:
            pass
        
        # Check that delays increase (with some tolerance for timing variations)
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            assert delay2 > delay1, "Second delay should be longer than first"
    
    def test_with_retry_decorator(self):
        """Test the with_retry decorator"""
        call_count = 0
        
        @with_retry(max_retries=3, base_delay=0.1)
        def decorated_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Not yet")
            return "success"
        
        result = decorated_func()
        assert result == "success"
        assert call_count == 3


class TestRateLimitHandler:
    """Test RateLimitHandler class"""
    
    def test_no_wait_on_first_call(self):
        """Test that first call doesn't wait"""
        handler = RateLimitHandler(requests_per_second=10)
        
        start_time = time.time()
        handler.wait_if_needed()
        elapsed = time.time() - start_time
        
        assert elapsed < 0.01, "First call should not wait"
    
    def test_rate_limiting_enforced(self):
        """Test that rate limiting is enforced"""
        handler = RateLimitHandler(requests_per_second=5)  # 5 requests per second = 0.2s between requests
        
        # First call - no wait
        handler.wait_if_needed()
        
        # Second call should wait if called immediately
        start_time = time.time()
        handler.wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should wait approximately 0.2 seconds (with some tolerance)
        assert 0.15 < elapsed < 0.25, f"Expected ~0.2s wait, got {elapsed}s"
    
    def test_multiple_rapid_calls(self):
        """Test multiple rapid calls are rate limited"""
        handler = RateLimitHandler(requests_per_second=10)
        
        start_time = time.time()
        for _ in range(3):
            handler.wait_if_needed()
        elapsed = time.time() - start_time
        
        # With 10 req/sec, 3 calls should take ~0.2 seconds
        assert elapsed >= 0.15, "Multiple calls should be rate limited"
    
    def test_no_wait_after_sufficient_delay(self):
        """Test that no waiting occurs if enough time has passed"""
        handler = RateLimitHandler(requests_per_second=5)
        
        handler.wait_if_needed()
        time.sleep(0.25)  # Wait longer than required interval
        
        start_time = time.time()
        handler.wait_if_needed()
        elapsed = time.time() - start_time
        
        assert elapsed < 0.01, "Should not wait if enough time has passed"

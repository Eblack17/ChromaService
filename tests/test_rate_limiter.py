import pytest
import time
from app.core.rate_limiter import TokenBucket, RateLimiter
from app.core.exceptions import RateLimitError

def test_token_bucket():
    """Test token bucket functionality."""
    # Initialize bucket with 10 tokens, refill rate of 1 token per second
    bucket = TokenBucket(10, 1.0)
    
    # Should be able to consume initial tokens
    assert bucket.consume(5) == True
    assert abs(bucket.tokens - 5) < 0.1  # Allow small floating-point difference
    
    # Should not be able to consume more than available
    assert bucket.consume(6) == False
    assert abs(bucket.tokens - 5) < 0.1
    
    # Wait for refill
    time.sleep(2)
    bucket._refill()
    
    # Should have refilled tokens (approximately 2 tokens over 2 seconds)
    assert bucket.tokens > 5
    assert bucket.tokens < 8  # Allow for some timing variation

def test_rate_limiter():
    """Test rate limiter functionality."""
    limiter = RateLimiter()
    client_id = "test_client"
    
    # Should allow requests within limits
    for _ in range(5):
        assert limiter.check_rate_limit(client_id, "free") == True
    
    # Check remaining quota
    quota = limiter.get_remaining_quota(client_id, "free")
    assert abs(quota["requests_per_minute_remaining"] - 15) <= 1  # Allow small difference
    assert abs(quota["requests_per_hour_remaining"] - 95) <= 1
    
    # Should raise error when exceeding minute limit
    with pytest.raises(RateLimitError) as exc_info:
        for _ in range(20):  # Try to make 20 more requests
            limiter.check_rate_limit(client_id, "free")
    assert "Too many requests per minute" in str(exc_info.value)

def test_rate_limiter_tiers():
    """Test rate limiter tiers."""
    limiter = RateLimiter()
    client_id = "test_client"
    
    # Test free tier
    assert limiter.check_rate_limit(client_id, "free") == True
    quota = limiter.get_remaining_quota(client_id, "free")
    assert abs(quota["requests_per_minute_remaining"] - 19) <= 1
    
    # Test pro tier
    assert limiter.check_rate_limit(client_id, "pro") == True
    quota = limiter.get_remaining_quota(client_id, "pro")
    assert abs(quota["requests_per_minute_remaining"] - 59) <= 1
    
    # Test enterprise tier
    assert limiter.check_rate_limit(client_id, "enterprise") == True
    quota = limiter.get_remaining_quota(client_id, "enterprise")
    assert abs(quota["requests_per_minute_remaining"] - 119) <= 1

def test_rate_limiter_refill():
    """Test rate limiter token refill."""
    limiter = RateLimiter()
    client_id = "test_client"
    
    # Use some tokens
    for _ in range(5):
        limiter.check_rate_limit(client_id, "free")
    
    initial_quota = limiter.get_remaining_quota(client_id, "free")
    
    # Wait for refill
    time.sleep(2)
    
    # Check refilled tokens
    final_quota = limiter.get_remaining_quota(client_id, "free")
    assert final_quota["requests_per_minute_remaining"] >= initial_quota["requests_per_minute_remaining"] 
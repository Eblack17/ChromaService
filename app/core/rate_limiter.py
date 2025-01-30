from typing import Dict, Optional
import time
from datetime import datetime
import logging
from .exceptions import RateLimitError

logger = logging.getLogger(__name__)

class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, tokens: int, fill_rate: float):
        """Initialize the token bucket.
        
        Args:
            tokens (int): Maximum number of tokens in the bucket
            fill_rate (float): Rate at which tokens are added (tokens per second)
        """
        self.capacity = tokens
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.last_update = time.time()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        delta = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + delta * self.fill_rate)
        self.last_update = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens from the bucket.
        
        Args:
            tokens (int): Number of tokens to consume
            
        Returns:
            bool: True if tokens were consumed, False otherwise
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self):
        """Initialize the rate limiter with default limits."""
        # Default limits for different tiers
        self.limits = {
            "free": {
                "requests_per_minute": 20,
                "requests_per_hour": 100,
                "tokens_per_request": 1
            },
            "pro": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "tokens_per_request": 1
            },
            "enterprise": {
                "requests_per_minute": 120,
                "requests_per_hour": 5000,
                "tokens_per_request": 1
            }
        }
        
        # Initialize buckets for each client
        self.minute_buckets: Dict[str, Dict[str, TokenBucket]] = {}
        self.hour_buckets: Dict[str, Dict[str, TokenBucket]] = {}
    
    def _get_or_create_buckets(self, client_id: str, tier: str = "free"):
        """Get or create rate limit buckets for a client.
        
        Args:
            client_id (str): The client identifier
            tier (str): The client's service tier
        """
        # Initialize minute bucket if not exists
        if client_id not in self.minute_buckets:
            self.minute_buckets[client_id] = {}
        if tier not in self.minute_buckets[client_id]:
            self.minute_buckets[client_id][tier] = TokenBucket(
                self.limits[tier]["requests_per_minute"],
                self.limits[tier]["requests_per_minute"] / 60.0
            )
        
        # Initialize hour bucket if not exists
        if client_id not in self.hour_buckets:
            self.hour_buckets[client_id] = {}
        if tier not in self.hour_buckets[client_id]:
            self.hour_buckets[client_id][tier] = TokenBucket(
                self.limits[tier]["requests_per_hour"],
                self.limits[tier]["requests_per_hour"] / 3600.0
            )
    
    def check_rate_limit(self, client_id: str, tier: str = "free") -> bool:
        """Check if a request is within rate limits.
        
        Args:
            client_id (str): The client identifier
            tier (str): The client's service tier
            
        Returns:
            bool: True if request is allowed, False otherwise
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        try:
            self._get_or_create_buckets(client_id, tier)
            
            # Check minute limit
            minute_bucket = self.minute_buckets[client_id][tier]
            if not minute_bucket.consume(self.limits[tier]["tokens_per_request"]):
                raise RateLimitError(
                    "Rate limit exceeded: Too many requests per minute",
                    {
                        "limit": self.limits[tier]["requests_per_minute"],
                        "period": "minute",
                        "tier": tier
                    }
                )
            
            # Check hour limit
            hour_bucket = self.hour_buckets[client_id][tier]
            if not hour_bucket.consume(self.limits[tier]["tokens_per_request"]):
                raise RateLimitError(
                    "Rate limit exceeded: Too many requests per hour",
                    {
                        "limit": self.limits[tier]["requests_per_hour"],
                        "period": "hour",
                        "tier": tier
                    }
                )
            
            return True
            
        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow request on error to prevent blocking service
    
    def get_remaining_quota(self, client_id: str, tier: str = "free") -> Dict[str, int]:
        """Get remaining quota for a client.
        
        Args:
            client_id (str): The client identifier
            tier (str): The client's service tier
            
        Returns:
            Dict[str, int]: Remaining quota for different time periods
        """
        self._get_or_create_buckets(client_id, tier)
        
        # Refill buckets to get current token counts
        self.minute_buckets[client_id][tier]._refill()
        self.hour_buckets[client_id][tier]._refill()
        
        return {
            "requests_per_minute_remaining": int(self.minute_buckets[client_id][tier].tokens),
            "requests_per_hour_remaining": int(self.hour_buckets[client_id][tier].tokens)
        }

# Global rate limiter instance
rate_limiter = RateLimiter() 
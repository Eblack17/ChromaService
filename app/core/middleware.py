from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from .rate_limiter import rate_limiter
from .exceptions import RateLimitError, handle_agent_error

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for applying rate limits to API requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting.
        
        Args:
            request (Request): The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            Response: The response from the next handler
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        try:
            # Get client identifier (IP address or API key)
            client_id = self._get_client_id(request)
            
            # Get client tier (from API key or default to free)
            tier = self._get_client_tier(request)
            
            # Check rate limit
            rate_limiter.check_rate_limit(client_id, tier)
            
            # Get remaining quota
            quota = rate_limiter.get_remaining_quota(client_id, tier)
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit-Minute"] = str(rate_limiter.limits[tier]["requests_per_minute"])
            response.headers["X-RateLimit-Remaining-Minute"] = str(quota["requests_per_minute_remaining"])
            response.headers["X-RateLimit-Limit-Hour"] = str(rate_limiter.limits[tier]["requests_per_hour"])
            response.headers["X-RateLimit-Remaining-Hour"] = str(quota["requests_per_hour_remaining"])
            
            return response
            
        except RateLimitError as e:
            error_details = handle_agent_error(e)
            return JSONResponse(
                status_code=error_details["status_code"],
                content={
                    "error": error_details["error_type"],
                    "message": error_details["message"],
                    "details": error_details["details"]
                }
            )
        except Exception as e:
            logger.error(f"Error in rate limit middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request.
        
        Args:
            request (Request): The incoming request
            
        Returns:
            str: The client identifier
        """
        # Try to get API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host
    
    def _get_client_tier(self, request: Request) -> str:
        """Get client tier from request.
        
        Args:
            request (Request): The incoming request
            
        Returns:
            str: The client tier
        """
        # TODO: Implement API key validation and tier lookup
        # For now, return free tier for all requests
        return "free" 
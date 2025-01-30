from typing import Optional, Any, Dict

class BaseCustomException(Exception):
    """Base exception class for all custom exceptions."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class AgentError(BaseCustomException):
    """Base class for agent-related errors."""
    pass

class ModelError(AgentError):
    """Base class for model-related errors."""
    pass

class GeminiError(ModelError):
    """Base class for Gemini-specific errors."""
    pass

class GeminiSafetyError(GeminiError):
    """Raised when content is blocked by Gemini's safety filters."""
    pass

class GeminiQuotaError(GeminiError):
    """Raised when Gemini API quota is exceeded."""
    pass

class GeminiInvalidRequestError(GeminiError):
    """Raised when the request to Gemini API is invalid."""
    pass

class GeminiUnavailableError(GeminiError):
    """Raised when the Gemini API service is unavailable."""
    pass

class ContentGenerationError(ModelError):
    """Raised when content generation fails."""
    pass

class ContentBlockedError(ModelError):
    """Raised when content is blocked by safety filters."""
    pass

class RateLimitError(ModelError):
    """Raised when API rate limits are exceeded."""
    pass

class AuthenticationError(BaseCustomException):
    """Raised when there are authentication issues."""
    pass

class ValidationError(BaseCustomException):
    """Raised when input validation fails."""
    pass

class ConfigurationError(BaseCustomException):
    """Raised when there are configuration issues."""
    pass

class DatabaseError(BaseCustomException):
    """Raised when database operations fail."""
    pass

class NetworkError(BaseCustomException):
    """Raised when network operations fail."""
    pass

def handle_agent_error(error: Exception) -> Dict[str, Any]:
    """Convert various exceptions to standardized error responses.
    
    Args:
        error: The exception to handle
        
    Returns:
        Dict containing error details in a standardized format
    """
    if isinstance(error, GeminiSafetyError):
        return {
            "error_type": "GEMINI_SAFETY_ERROR",
            "message": "The request was blocked by Gemini's safety filters. Please rephrase your message.",
            "details": error.details,
            "status_code": 400
        }
    elif isinstance(error, GeminiQuotaError):
        return {
            "error_type": "GEMINI_QUOTA_ERROR",
            "message": "API quota exceeded. Please try again later.",
            "details": error.details,
            "status_code": 429
        }
    elif isinstance(error, GeminiInvalidRequestError):
        return {
            "error_type": "GEMINI_INVALID_REQUEST",
            "message": "Invalid request to Gemini API.",
            "details": error.details,
            "status_code": 400
        }
    elif isinstance(error, GeminiUnavailableError):
        return {
            "error_type": "GEMINI_UNAVAILABLE",
            "message": "Gemini API service is currently unavailable. Please try again later.",
            "details": error.details,
            "status_code": 503
        }
    elif isinstance(error, ContentBlockedError):
        return {
            "error_type": "CONTENT_BLOCKED",
            "message": str(error),
            "details": error.details,
            "status_code": 400
        }
    elif isinstance(error, ContentGenerationError):
        return {
            "error_type": "GENERATION_FAILED",
            "message": str(error),
            "details": error.details,
            "status_code": 500
        }
    elif isinstance(error, RateLimitError):
        return {
            "error_type": "RATE_LIMIT_EXCEEDED",
            "message": str(error),
            "details": error.details,
            "status_code": 429
        }
    elif isinstance(error, AuthenticationError):
        return {
            "error_type": "AUTHENTICATION_FAILED",
            "message": str(error),
            "details": error.details,
            "status_code": 401
        }
    elif isinstance(error, ValidationError):
        return {
            "error_type": "VALIDATION_FAILED",
            "message": str(error),
            "details": error.details,
            "status_code": 400
        }
    elif isinstance(error, ConfigurationError):
        return {
            "error_type": "CONFIGURATION_ERROR",
            "message": str(error),
            "details": error.details,
            "status_code": 500
        }
    else:
        return {
            "error_type": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {"original_error": str(error)},
            "status_code": 500
        } 
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, validator, AnyHttpUrl
from typing import List, Dict, Any, Optional, Union
from functools import lru_cache
import os
from dotenv import load_dotenv
import secrets
import logging
from pathlib import Path

# Load environment-specific .env file
app_env = os.getenv("APP_ENV", "development")
env_file = Path(__file__).parent / "environments" / f"{app_env}.env"
load_dotenv(env_file if env_file.exists() else ".env")

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings with enhanced validation and documentation."""
    
    # App configuration
    APP_NAME: str = Field(
        "ChromaPages AI Customer Service",
        description="Name of the application"
    )
    APP_VERSION: str = Field(
        "1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version of the application"
    )
    APP_ENV: str = Field(
        "development",
        pattern="^(development|staging|production)$",
        description="Application environment"
    )
    DEBUG: bool = Field(
        True,
        description="Debug mode flag"
    )
    
    # API configuration
    API_PREFIX: str = Field(
        "/api",
        description="API route prefix"
    )
    CORS_ORIGINS: Union[str, List[str]] = Field(
        ["*"],
        description="Allowed CORS origins. Use ['*'] for development, specific origins for production"
    )
    
    # Authentication configuration
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
        description="Secret key for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30,
        ge=1,
        le=1440,
        description="Access token expiration time in minutes"
    )
    ALGORITHM: str = Field(
        "HS256",
        pattern="^(HS256|HS384|HS512)$",
        description="JWT encoding algorithm"
    )
    API_KEY_HEADER: str = Field(
        "X-API-Key",
        description="Header name for API key authentication"
    )
    
    # API key tiers and scopes
    API_KEY_TIERS: Dict[str, Dict[str, Any]] = Field(
        {
            "free": {
                "scope": "agents:read",
                "rate_limits": {
                    "requests_per_minute": 20,
                    "requests_per_hour": 100
                }
            },
            "pro": {
                "scope": "agents:*",
                "rate_limits": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000
                }
            },
            "enterprise": {
                "scope": "agents:*",
                "rate_limits": {
                    "requests_per_minute": 120,
                    "requests_per_hour": 5000
                }
            }
        },
        description="API key tiers configuration"
    )
    
    # Rate limiting configuration
    RATE_LIMIT_ENABLED: bool = Field(
        True,
        description="Enable/disable rate limiting"
    )
    RATE_LIMIT_TIERS: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Rate limiting configuration per tier"
    )
    
    # Gemini API configuration
    GOOGLE_API_KEY: str = Field(
        "",
        description="Google API key for Gemini model access"
    )
    GEMINI_MODEL: str = Field(
        "gemini-pro",
        description="Gemini model name"
    )
    GEMINI_TEMPERATURE: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for model generation"
    )
    GEMINI_TOP_P: float = Field(
        0.8,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter"
    )
    GEMINI_TOP_K: int = Field(
        40,
        ge=1,
        description="Top-k sampling parameter"
    )
    GEMINI_MAX_OUTPUT_TOKENS: int = Field(
        1024,
        ge=1,
        description="Maximum output tokens for model generation"
    )
    
    # Safety settings
    SAFETY_SETTINGS: List[Dict[str, str]] = Field(
        [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ],
        description="Safety settings for content filtering"
    )
    
    # Database configuration
    DB_HOST: str = Field(
        "localhost",
        description="Database host"
    )
    DB_PORT: int = Field(
        5432,
        ge=1,
        le=65535,
        description="Database port"
    )
    DB_NAME: str = Field(
        "customer_service_db",
        description="Database name"
    )
    DB_USER: str = Field(
        "postgres",
        description="Database user"
    )
    DB_PASSWORD: str = Field(
        "",
        description="Database password"
    )
    
    # Logging configuration
    LOG_LEVEL: str = Field(
        "INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        "standard",
        pattern="^(standard|json)$",
        description="Logging format"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Get the database URL.
        
        Returns:
            str: Database connection URL
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate and process CORS origins.
        
        Args:
            v: CORS origins as string or list
            
        Returns:
            List[str]: Processed CORS origins
        """
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("RATE_LIMIT_TIERS", always=True)
    def set_rate_limit_tiers(cls, v: Dict[str, Dict[str, Any]], values: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Set rate limit tiers from API key tiers.
        
        Args:
            v: Rate limit tiers
            values: Settings values
            
        Returns:
            Dict[str, Dict[str, Any]]: Rate limit tiers configuration
        """
        if not v and "API_KEY_TIERS" in values:
            return {
                tier: tier_config["rate_limits"]
                for tier, tier_config in values["API_KEY_TIERS"].items()
            }
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in environment variables
        validate_assignment=True  # Validate values on assignment
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings
        
    Note:
        Uses LRU cache to prevent multiple reads of environment variables
    """
    try:
        settings = Settings()
        logger.info(f"Loaded settings for environment: {settings.APP_ENV}")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {str(e)}")
        raise 
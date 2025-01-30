from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import logging
from .config import get_settings
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)
settings = get_settings()

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str

class TokenData(BaseModel):
    """Token data model."""
    api_key: str
    tier: str
    scope: str
    exp: datetime

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise AuthenticationError("Failed to create access token")

def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        api_key: str = payload.get("api_key")
        tier: str = payload.get("tier")
        scope: str = payload.get("scope")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"), UTC)
        
        if api_key is None or tier is None:
            raise AuthenticationError("Invalid token contents")
            
        return TokenData(
            api_key=api_key,
            tier=tier,
            scope=scope,
            exp=exp
        )
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise AuthenticationError("Invalid or expired token")
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise AuthenticationError("Token verification failed")

def verify_api_key(api_key: str) -> Dict[str, Any]:
    """Verify an API key and return associated data.
    
    Args:
        api_key: The API key to verify
        
    Returns:
        Dict containing API key data (tier, scope, etc.)
        
    Raises:
        AuthenticationError: If API key is invalid
    """
    # TODO: Implement proper API key verification against database
    # For now, use a simple mapping for testing
    api_keys = {
        "test_free_key": {"tier": "free", "scope": "agents:read"},
        "test_pro_key": {"tier": "pro", "scope": "agents:*"},
        "test_enterprise_key": {"tier": "enterprise", "scope": "agents:*"}
    }
    
    if api_key not in api_keys:
        raise AuthenticationError("Invalid API key")
        
    return api_keys[api_key]

async def get_current_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Dependency for getting current token data.
    
    Args:
        token: JWT token from request
        
    Returns:
        TokenData: Current token data
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        return verify_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

def create_api_key_token(api_key: str) -> Token:
    """Create a JWT token for an API key.
    
    Args:
        api_key: The API key to create a token for
        
    Returns:
        Token: The created token
        
    Raises:
        AuthenticationError: If API key is invalid
    """
    # Verify API key and get associated data
    api_key_data = verify_api_key(api_key)
    
    # Create token with expiration
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "api_key": api_key,
        "tier": api_key_data["tier"],
        "scope": api_key_data["scope"]
    }
    
    access_token = create_access_token(token_data, expires_delta)
    
    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=api_key_data["scope"]
    ) 
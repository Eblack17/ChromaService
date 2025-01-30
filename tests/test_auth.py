import pytest
from datetime import datetime, timedelta
from app.core.auth import (
    create_access_token,
    verify_token,
    verify_api_key,
    create_api_key_token,
    Token,
    TokenData
)
from app.core.exceptions import AuthenticationError

def test_create_access_token():
    """Test access token creation."""
    # Test with valid data
    data = {
        "api_key": "test_key",
        "tier": "free",
        "scope": "agents:read"
    }
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test with expiration
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_token():
    """Test token verification."""
    # Create a token
    data = {
        "api_key": "test_key",
        "tier": "free",
        "scope": "agents:read"
    }
    token = create_access_token(data)
    
    # Verify valid token
    token_data = verify_token(token)
    assert isinstance(token_data, TokenData)
    assert token_data.api_key == "test_key"
    assert token_data.tier == "free"
    assert token_data.scope == "agents:read"
    
    # Test invalid token
    with pytest.raises(AuthenticationError):
        verify_token("invalid_token")
    
    # Test expired token
    expired_data = data.copy()
    expired_token = create_access_token(expired_data, timedelta(minutes=-1))
    with pytest.raises(AuthenticationError):
        verify_token(expired_token)

def test_verify_api_key():
    """Test API key verification."""
    # Test valid API keys
    free_data = verify_api_key("test_free_key")
    assert free_data["tier"] == "free"
    assert free_data["scope"] == "agents:read"
    
    pro_data = verify_api_key("test_pro_key")
    assert pro_data["tier"] == "pro"
    assert pro_data["scope"] == "agents:*"
    
    enterprise_data = verify_api_key("test_enterprise_key")
    assert enterprise_data["tier"] == "enterprise"
    assert enterprise_data["scope"] == "agents:*"
    
    # Test invalid API key
    with pytest.raises(AuthenticationError):
        verify_api_key("invalid_key")

def test_create_api_key_token():
    """Test API key token creation."""
    # Test with valid API keys
    free_token = create_api_key_token("test_free_key")
    assert isinstance(free_token, Token)
    assert free_token.token_type == "bearer"
    assert free_token.scope == "agents:read"
    assert free_token.expires_in > 0
    
    pro_token = create_api_key_token("test_pro_key")
    assert isinstance(pro_token, Token)
    assert pro_token.scope == "agents:*"
    
    # Test with invalid API key
    with pytest.raises(AuthenticationError):
        create_api_key_token("invalid_key")

def test_token_expiration():
    """Test token expiration handling."""
    # Create token with short expiration
    data = {
        "api_key": "test_key",
        "tier": "free",
        "scope": "agents:read"
    }
    token = create_access_token(data, timedelta(seconds=1))
    
    # Verify token immediately
    token_data = verify_token(token)
    assert isinstance(token_data, TokenData)
    
    # Wait for token to expire
    import time
    time.sleep(2)
    
    # Verify expired token
    with pytest.raises(AuthenticationError):
        verify_token(token)

def test_token_data_validation():
    """Test token data validation."""
    # Test with missing required fields
    with pytest.raises(AuthenticationError):
        data = {"api_key": "test_key"}  # Missing tier
        token = create_access_token(data)
        verify_token(token)
    
    with pytest.raises(AuthenticationError):
        data = {"tier": "free"}  # Missing api_key
        token = create_access_token(data)
        verify_token(token) 
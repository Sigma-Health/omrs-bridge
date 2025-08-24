from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_valid_api_keys
import secrets
import hashlib
import time


# Security scheme for API key authentication
security = HTTPBearer(auto_error=False)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API key from Authorization header
    Expected format: Bearer <api_key>
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    valid_keys = get_valid_api_keys()
    
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No API keys configured"
        )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


def generate_api_key() -> str:
    """
    Generate a secure API key
    Format: omrs_<32_random_chars>
    """
    random_bytes = secrets.token_bytes(16)
    random_hex = random_bytes.hex()
    return f"omrs_{random_hex}"


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for secure storage (if needed)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


# Dependency for protected endpoints
def get_current_api_key(api_key: str = Depends(verify_api_key)):
    return api_key 
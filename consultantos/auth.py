"""
Authentication and authorization for ConsultantOS (v0.3.0)
"""
import hashlib
import secrets
import logging
import threading
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from consultantos.config import settings
from consultantos.database import get_db_service, APIKeyRecord

logger = logging.getLogger(__name__)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

# Fallback in-memory store (for development when DB unavailable)
_api_keys_fallback: Dict[str, Dict] = {}
_api_keys_fallback_lock = threading.Lock()


def generate_api_key() -> str:
    """Generate a new API key"""
    return secrets.token_urlsafe(32)


def create_api_key(user_id: str, description: Optional[str] = None) -> str:
    """
    Create a new API key for a user
    
    Args:
        user_id: User identifier
        description: Optional description for the key
    
    Returns:
        Generated API key
    """
    api_key = generate_api_key()
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    key_record = APIKeyRecord(
        key_hash=key_hash,
        user_id=user_id,
        description=description
    )
    
    # Try database first, fallback to in-memory
    try:
        db_service = get_db_service()
        if db_service.create_api_key(key_record):
            logger.info(f"Created API key in database for user {user_id}")
            return api_key
    except Exception as e:
        logger.warning(f"Database unavailable, using fallback: {e}")
    
    # Fallback to in-memory
    _api_keys_fallback[key_hash] = {
        "user_id": user_id,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0,
        "active": True
    }
    logger.info(f"Created API key (fallback) for user {user_id}")
    return api_key


def validate_api_key(api_key: str) -> Optional[Dict]:
    """
    Validate an API key
    
    Args:
        api_key: API key to validate
    
    Returns:
        User info dict if valid, None otherwise
    """
    if not api_key:
        return None
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Try database first
    try:
        db_service = get_db_service()
        key_record = db_service.get_api_key(key_hash)
        
        if key_record:
            if not key_record.active:
                return None
            
            # Update usage stats
            db_service.update_api_key(key_hash, {
                "last_used": datetime.now().isoformat(),
                "usage_count": key_record.usage_count + 1
            })
            
            return {
                "user_id": key_record.user_id,
                "key_info": key_record.to_dict()
            }
    except Exception as e:
        logger.warning(f"Database unavailable, using fallback: {e}")
    
    # Fallback to in-memory (thread-safe)
    with _api_keys_fallback_lock:
        if key_hash in _api_keys_fallback:
            key_info = _api_keys_fallback[key_hash]
            
            if not key_info.get("active", True):
                return None
            
            # Atomic update
            key_info["last_used"] = datetime.now().isoformat()
            key_info["usage_count"] = key_info.get("usage_count", 0) + 1
            
            return {
                "user_id": key_info["user_id"],
                "key_info": key_info
            }
    
    return None


def revoke_api_key(api_key: str, user_id: Optional[str] = None) -> bool:
    """
    Revoke an API key
    
    Args:
        api_key: API key to revoke
        user_id: Optional user ID for verification
    
    Returns:
        True if revoked, False if not found
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Try database first
    try:
        db_service = get_db_service()
        key_record = db_service.get_api_key(key_hash)
        
        # Verify user_id if provided
        if user_id and key_record and key_record.user_id != user_id:
            logger.warning(f"User {user_id} attempted to revoke key belonging to {key_record.user_id}")
            return False
        
        if db_service.update_api_key(key_hash, {"active": False}):
            logger.info(f"Revoked API key in database: {key_hash[:8]}...")
            return True
    except Exception as e:
        logger.warning(f"Database unavailable, using fallback: {e}")
    
    # Fallback to in-memory (thread-safe)
    with _api_keys_fallback_lock:
        # Re-check after acquiring lock to avoid TOCTOU
        if key_hash not in _api_keys_fallback:
            return False
        
        key_info = _api_keys_fallback[key_hash]
        
        # Verify user_id if provided
        if user_id and key_info.get("user_id") != user_id:
            logger.warning(f"User {user_id} attempted to revoke key belonging to {key_info.get('user_id')}")
            return False
        
        _api_keys_fallback[key_hash]["active"] = False
        logger.info(f"Revoked API key (fallback): {key_hash[:8]}...")
        return True


def revoke_api_key_by_hash(key_hash: str, user_id: str) -> bool:
    """
    Revoke an API key by hash prefix (for listing/revocation UI)
    
    Args:
        key_hash: Hash prefix to match
        user_id: User ID for verification
    
    Returns:
        True if revoked, False if not found
    """
    # Try database first
    try:
        db_service = get_db_service()
        key_records = db_service.list_api_keys(user_id)
        
        for key_record in key_records:
            if key_record.key_hash.startswith(key_hash):
                if db_service.update_api_key(key_record.key_hash, {"active": False}):
                    logger.info(f"Revoked API key by hash prefix: {key_hash[:8]}...")
                    return True
    except Exception as e:
        logger.warning(f"Database unavailable, using fallback: {e}")
    
    # Fallback to in-memory (thread-safe)
    with _api_keys_fallback_lock:
        # Take snapshot of items while holding lock, then iterate
        entries = list(_api_keys_fallback.items())
        for stored_hash, key_info in entries:
            if stored_hash.startswith(key_hash) and key_info.get("user_id") == user_id:
                # Modify while still holding the lock
                _api_keys_fallback[stored_hash]["active"] = False
                logger.info(f"Revoked API key by hash (fallback): {key_hash[:8]}...")
                return True
    
    return False


def rotate_api_key(user_id: str, old_api_key: Optional[str] = None, description: Optional[str] = None) -> str:
    """
    Rotate an API key (revoke old, create new)
    
    Args:
        user_id: User identifier
        old_api_key: Optional old API key to revoke
        description: Description for new key
    
    Returns:
        New API key
    """
    # Revoke old key if provided
    if old_api_key:
        revoke_api_key(old_api_key, user_id)
        logger.info(f"Rotated API key for user {user_id}")
    else:
        logger.info(f"Creating new API key for user {user_id} (no old key to revoke)")
    
    # Create new key
    return create_api_key(user_id, description or "Rotated key")


def check_api_key_expiry(key_hash: str, max_age_days: int = 365) -> bool:
    """
    Check if API key should be expired based on age
    
    Args:
        key_hash: Key hash to check
        max_age_days: Maximum age in days
    
    Returns:
        True if key should be expired, False otherwise
    """
    try:
        db_service = get_db_service()
        key_record = db_service.get_api_key(key_hash)
        
        if key_record and key_record.created_at:
            created = datetime.fromisoformat(key_record.created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(created.tzinfo) - created).days
            
            if age_days > max_age_days:
                logger.warning(f"API key {key_hash[:8]}... is {age_days} days old, should be rotated")
                return True
    except Exception as e:
        logger.debug(f"Could not check key expiry: {e}")
    
    return False


async def get_api_key(
    header_key: Optional[str] = Security(api_key_header),
    query_key: Optional[str] = Security(api_key_query)
) -> Optional[str]:
    """
    Extract API key from header or query parameter (optional)
    
    Args:
        header_key: API key from header
        query_key: API key from query parameter
    
    Returns:
        API key string or None if not provided
    """
    return header_key or query_key


async def verify_api_key(api_key: Optional[str] = Security(get_api_key)) -> Dict:
    """
    Verify API key and return user info

    Args:
        api_key: API key to verify (required)

    Returns:
        User info dict

    Raises:
        HTTPException if key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide via X-API-Key header or api_key query parameter."
        )

    user_info = validate_api_key(api_key)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    return user_info


async def get_current_user(api_key: Optional[str] = Security(get_api_key)) -> str:
    """
    Get current authenticated user ID from API key

    This is a dependency function for FastAPI endpoints that require authentication.

    Args:
        api_key: API key from header or query parameter

    Returns:
        User ID string

    Raises:
        HTTPException if authentication fails

    Example:
        @router.get("/my-endpoint")
        async def my_endpoint(user_id: str = Depends(get_current_user)):
            # user_id is the authenticated user's ID
            pass
    """
    user_info = await verify_api_key(api_key)
    return user_info["user_id"]


async def get_current_user_id(api_key: Optional[str] = Security(get_api_key)) -> str:
    """
    Get current authenticated user ID from API key (alias for get_current_user)

    This is an alias for get_current_user for backward compatibility.

    Args:
        api_key: API key from header or query parameter

    Returns:
        User ID string

    Raises:
        HTTPException if authentication fails
    """
    return await get_current_user(api_key)


async def get_optional_user_id(api_key: Optional[str] = Security(get_api_key)) -> Optional[str]:
    """
    Get current user ID from API key (optional authentication)

    Returns None if no API key provided or if API key is invalid,
    rather than raising an HTTPException.

    This is useful for endpoints that support both authenticated and
    unauthenticated access.

    Args:
        api_key: API key from header or query parameter (optional)

    Returns:
        User ID string if authenticated, None otherwise

    Example:
        @router.get("/my-endpoint")
        async def my_endpoint(user_id: Optional[str] = Depends(get_optional_user_id)):
            if user_id:
                # Authenticated access
                pass
            else:
                # Unauthenticated access
                pass
    """
    if not api_key:
        return None

    user_info = validate_api_key(api_key)
    if not user_info:
        return None

    return user_info["user_id"]


def get_user_api_keys(user_id: str) -> list:
    """Get all API keys for a user (without exposing actual keys)"""
    user_keys = []
    
    # Try database first
    try:
        db_service = get_db_service()
        key_records = db_service.list_api_keys(user_id)
        for key_record in key_records:
            user_keys.append({
                "key_hash": key_record.key_hash[:8] + "...",
                "description": key_record.description,
                "created_at": key_record.created_at,
                "last_used": key_record.last_used,
                "usage_count": key_record.usage_count,
                "active": key_record.active
            })
        return user_keys
    except Exception as e:
        logger.warning(f"Database unavailable, using fallback: {e}")
    
    # Fallback to in-memory
    for key_hash, key_info in _api_keys_fallback.items():
        if key_info["user_id"] == user_id:
            user_keys.append({
                "key_hash": key_hash[:8] + "...",
                "description": key_info.get("description"),
                "created_at": key_info.get("created_at"),
                "last_used": key_info.get("last_used"),
                "usage_count": key_info.get("usage_count", 0),
                "active": key_info.get("active", True)
            })
    return user_keys


# For development/demo: Create a default API key
if settings.environment == "development":
    DEFAULT_API_KEY = create_api_key("demo_user", "Default demo API key")
    logger.info(f"Created default API key for development: {DEFAULT_API_KEY[:16]}...")


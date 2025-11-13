"""
Enhanced User Management for ConsultantOS (v0.4.0)
Includes registration, login, email verification, password management
"""
import hashlib
import secrets
import logging
import re
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext
from consultantos.database import get_db_service, UserAccount
from consultantos.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Email verification tokens (in production, use Redis or database)
_verification_tokens: Dict[str, Dict] = {}
_password_reset_tokens: Dict[str, Dict] = {}


def validate_password(password: str) -> None:
    """
    Validate password meets security requirements

    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character

    Args:
        password: Password to validate

    Raises:
        HTTPException: If password doesn't meet requirements
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("Password must contain at least one special character")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet security requirements", "errors": errors}
        )


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_user(email: str, password: str, name: Optional[str] = None) -> Dict:
    """
    Create a new user account

    Args:
        email: User email
        password: Plain text password
        name: Optional user name

    Returns:
        User account dict with user_id
    """
    # Validate password strength
    validate_password(password)

    # Check if user already exists
    db_service = get_db_service()
    existing_user = db_service.get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Generate user ID
    user_id = f"user_{secrets.token_urlsafe(16)}"

    # Hash password
    password_hash = hash_password(password)
    
    # Create user account
    user_account = UserAccount(
        user_id=user_id,
        email=email,
        name=name,
        subscription_tier="free"
    )
    
    # Store in database (with password hash in a separate collection for security)
    try:
        success = db_service.create_user(user_account, password_hash)
        if not success:
            logger.error(f"Database service returned False when creating user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account in database"
            )
        
        # Verify password hash was stored correctly
        stored_hash = db_service.get_user_password_hash(user_id)
        if not stored_hash:
            logger.error(f"Password hash not found after creating user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password hash was not stored correctly"
            )
        
        # Verify the stored hash matches what we created
        if stored_hash != password_hash:
            logger.error(
                f"Password hash mismatch for user {user_id} - stored hash differs from created hash",
                extra={"user_id": user_id}
            )
            # Attempt rollback by deleting the user
            try:
                rollback_success = db_service.delete_user(user_id)
                if rollback_success:
                    logger.info(f"Successfully rolled back user creation for user {user_id}")
                else:
                    logger.error(
                        f"Failed to rollback user creation for user {user_id} - user may exist with incorrect password hash",
                        extra={"user_id": user_id}
                    )
            except Exception as rollback_error:
                logger.error(
                    f"Exception during rollback for user {user_id}: {rollback_error}",
                    exc_info=True,
                    extra={"user_id": user_id, "rollback_error": str(rollback_error)}
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password hash verification failed - user creation rolled back"
            )
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        _verification_tokens[verification_token] = {
            "user_id": user_id,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        logger.info(f"Created user account: {user_id} ({email})")
        
        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "verification_token": verification_token,
            "email_verified": False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with email and password
    
    Args:
        email: User email
        password: Plain text password
    
    Returns:
        User info dict if authenticated, None otherwise
        
    Raises:
        Exception: If database operations fail critically
    """
    try:
        db_service = get_db_service()
    except Exception as e:
        logger.error(f"Failed to get database service: {e}", exc_info=True)
        raise
    
    try:
        user_account = db_service.get_user_by_email(email)
    except Exception as e:
        logger.error(f"Database error while fetching user by email: {e}", exc_info=True)
        raise
    
    if not user_account:
        logger.debug(f"User not found: email={email}")
        return None
    
    try:
        # Get password hash
        password_hash = db_service.get_user_password_hash(user_account.user_id)
    except Exception as e:
        logger.error(f"Database error while fetching password hash: {e}", exc_info=True)
        raise
    
    if not password_hash:
        logger.warning(f"No password hash found for user: id={user_account.user_id}")
        return None
    
    # Verify password
    try:
        if not verify_password(password, password_hash):
            logger.debug(f"Password verification failed for user: id={user_account.user_id}")
            return None
    except Exception as e:
        logger.error(f"Password verification error: {e}", exc_info=True)
        raise
    
    # Update last login
    try:
        db_service.update_user(user_account.user_id, {
            "last_login": datetime.now().isoformat()
        })
    except Exception as e:
        logger.warning(f"Failed to update last login for user: id={user_account.user_id}, error={str(e)}")
        # Don't fail authentication if last login update fails
    
    logger.info(f"User authenticated successfully: id={user_account.user_id}")
    return {
        "user_id": user_account.user_id,
        "email": user_account.email,
        "name": user_account.name,
        "subscription_tier": user_account.subscription_tier
    }


def verify_email_token(token: str) -> bool:
    """
    Verify email verification token
    
    Args:
        token: Verification token
    
    Returns:
        True if verified, False otherwise
    """
    if token not in _verification_tokens:
        return False
    
    token_info = _verification_tokens[token]
    
    # Check expiration
    expires_at = datetime.fromisoformat(token_info["expires_at"])
    if datetime.now() > expires_at:
        del _verification_tokens[token]
        return False
    
    # Mark email as verified in database
    user_id = token_info["user_id"]
    db_service = get_db_service()
    db_service.update_user(user_id, {
        "email_verified": True
    })
    
    # Remove token
    del _verification_tokens[token]
    
    logger.info(f"Email verified for user: {user_id}")
    return True


def request_password_reset(email: str) -> Optional[str]:
    """
    Request password reset token
    
    Args:
        email: User email
    
    Returns:
        Reset token if user exists, None otherwise
    """
    db_service = get_db_service()
    user_account = db_service.get_user_by_email(email)
    
    if not user_account:
        # Don't reveal if user exists (security best practice)
        return None
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    _password_reset_tokens[reset_token] = {
        "user_id": user_account.user_id,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    logger.info(f"Password reset requested for: {email}")
    return reset_token


def reset_password(token: str, new_password: str) -> bool:
    """
    Reset password using token
    
    Args:
        token: Password reset token
        new_password: New plain text password
    
    Returns:
        True if reset successful, False otherwise
    """
    if token not in _password_reset_tokens:
        return False
    
    token_info = _password_reset_tokens[token]
    
    # Check expiration
    expires_at = datetime.fromisoformat(token_info["expires_at"])
    if datetime.now() > expires_at:
        del _password_reset_tokens[token]
        return False

    # Validate new password
    validate_password(new_password)

    # Update password
    user_id = token_info["user_id"]
    password_hash = hash_password(new_password)
    
    db_service = get_db_service()
    db_service.update_user_password(user_id, password_hash)
    
    # Remove token
    del _password_reset_tokens[token]
    
    logger.info(f"Password reset for user: {user_id}")
    return True


def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    """
    Change password for authenticated user
    
    Args:
        user_id: User ID
        old_password: Current password
        new_password: New password
    
    Returns:
        True if changed, False if old password incorrect
    """
    db_service = get_db_service()
    password_hash = db_service.get_user_password_hash(user_id)
    
    if not password_hash or not verify_password(old_password, password_hash):
        return False
    
    new_password_hash = hash_password(new_password)
    db_service.update_user_password(user_id, new_password_hash)
    
    logger.info(f"Password changed for user: {user_id}")
    return True


def get_user_profile(user_id: str) -> Optional[Dict]:
    """Get user profile"""
    db_service = get_db_service()
    user_account = db_service.get_user(user_id)
    
    if not user_account:
        return None
    
    return {
        "user_id": user_account.user_id,
        "email": user_account.email,
        "name": user_account.name,
        "subscription_tier": user_account.subscription_tier,
        "created_at": user_account.created_at,
        "last_login": user_account.last_login
    }


def update_user_profile(user_id: str, updates: Dict) -> bool:
    """Update user profile"""
    db_service = get_db_service()
    return db_service.update_user(user_id, updates)


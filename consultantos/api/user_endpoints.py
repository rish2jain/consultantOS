"""
User management API endpoints (v0.4.0)
"""
from datetime import datetime
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, status, Security
from pydantic import BaseModel, EmailStr
from consultantos.user_management import (
    create_user,
    authenticate_user,
    verify_email_token,
    request_password_reset,
    reset_password,
    change_password,
    get_user_profile,
    update_user_profile
)
from consultantos.auth import verify_api_key

router = APIRouter(prefix="/users", tags=["users"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user account"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        user_info = create_user(
            email=request.email,
            password=request.password,
            name=request.name
        )
        # Send verification email (or log for dev)
        verification_token = user_info.get("verification_token")
        if verification_token:
            try:
                from consultantos.services.email_service import get_email_service
                email_service = get_email_service()
                email_service.send_email(
                    to=request.email,
                    subject="Verify your ConsultantOS account",
                    body=f"Please verify your email using this token: {verification_token}"
                )
            except Exception as email_error:
                # Log email error but don't fail registration
                logger.warning(f"Failed to send verification email: {email_error}")
        
        return {
            "message": "User registered successfully. Please check your email for verification.",
            "user_id": user_info["user_id"],
            "email": user_info["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {request.email}: {e}", exc_info=True)
        # Provide more detailed error message
        error_detail = str(e)
        if "database" in error_detail.lower() or "connection" in error_detail.lower():
            error_detail = "Database connection error. Please try again later."
        elif "email" in error_detail.lower() and "exists" in error_detail.lower():
            # This should be caught by create_user, but handle it anyway
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {error_detail}"
        )


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate user and return API key"""
    user_info = authenticate_user(request.email, request.password)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate API key for the user (or return existing)
    from consultantos.auth import create_api_key
    api_key = create_api_key(user_info["user_id"], "Login API key")
    
    return {
        "access_token": api_key,  # In production, use JWT tokens
        "token_type": "bearer",
        "user": user_info
    }


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """Verify email address with token"""
    if verify_email_token(request.token):
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )


@router.post("/password-reset/request")
async def request_reset(request: PasswordResetRequest):
    """Request password reset token"""
    token = request_password_reset(request.email)
    
    # Send email with token (or log for dev)
    if token:
        from consultantos.services.email_service import get_email_service
        email_service = get_email_service()
        email_service.send_email(
            to=request.email,
            subject="Password Reset - ConsultantOS",
            body=f"Use this token to reset your password: {token}"
        )
    
    # Always return generic message (don't reveal if user exists)
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/password-reset/confirm")
async def confirm_reset(request: PasswordResetConfirm):
    """Reset password using token"""
    if reset_password(request.token, request.new_password):
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.post("/change-password")
async def change_user_password(
    request: ChangePasswordRequest,
    user_info: Dict = Security(verify_api_key)
):
    """Change password for authenticated user"""
    user_id = user_info.get("user_id")
    
    if change_password(user_id, request.old_password, request.new_password):
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )


@router.get("/profile")
async def get_profile(user_info: Dict = Security(verify_api_key)):
    """Get user profile"""
    user_id = user_info.get("user_id")
    profile = get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    user_info: Dict = Security(verify_api_key)
):
    """Update user profile"""
    user_id = user_info.get("user_id")
    
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    
    if update_user_profile(user_id, updates):
        return {"message": "Profile updated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


"""
Report sharing API endpoints (v0.4.0)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Security
from consultantos.models.sharing import (
    ShareAccess,
    CreateShareRequest,
    ShareListResponse,
    ShareType
)
from consultantos.auth import verify_api_key
from consultantos.services.email_service import get_email_service
from consultantos.database import get_db_service
import secrets
import logging
from datetime import datetime, timedelta, timezone
import threading

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sharing", tags=["sharing"])

# In-memory share store (in production, use database)
_shares: dict[str, ShareAccess] = {}
# Locks for thread-safe operations
_share_locks: dict[str, threading.Lock] = {}
_share_locks_lock = threading.Lock()  # Lock for the locks dict itself

def _get_share_lock(share_id: str) -> threading.Lock:
    """Get or create a lock for a specific share"""
    with _share_locks_lock:
        if share_id not in _share_locks:
            _share_locks[share_id] = threading.Lock()
        return _share_locks[share_id]


@router.post("", response_model=ShareAccess, status_code=status.HTTP_201_CREATED)
async def create_share(
    request: CreateShareRequest,
    user_info: dict = Security(verify_api_key)
):
    """Share a report"""
    share_id = f"share_{secrets.token_urlsafe(16)}"
    share_token = secrets.token_urlsafe(32) if request.share_type == ShareType.LINK else None
    
    share = ShareAccess(
        share_id=share_id,
        report_id=request.report_id,
        shared_by=user_info["user_id"],
        permission=request.permission,
        expires_at=request.expires_at,
        share_type=request.share_type,
        shared_with=request.shared_with,
        share_token=share_token,
        public_url=f"/shared/{share_token}" if share_token else None
    )
    
    _shares[share_id] = share
    
    # Send email notification if share_type is "email"
    if request.share_type == ShareType.EMAIL and request.shared_with:
        email_service = get_email_service()
        # Get user email from database
        db_service = get_db_service()
        user_account = db_service.get_user_by_email(request.shared_with)
        if user_account:
            share_url = f"{share.public_url}" if share.public_url else f"/shared/{share.share_token}"
            email_service.send_share_notification(
                to=request.shared_with,
                report_id=request.report_id,
                shared_by=user_info.get("name", "A user"),
                share_url=share_url,
                message=request.message
            )
    
    return share


@router.get("/report/{report_id}", response_model=ShareListResponse)
async def list_shares(
    report_id: str,
    user_info: dict = Security(verify_api_key)
):
    """List all shares for a report"""
    user_shares = [
        s for s in _shares.values()
        if s.report_id == report_id and s.shared_by == user_info["user_id"]
    ]
    
    return ShareListResponse(
        report_id=report_id,
        shares=user_shares,
        total=len(user_shares)
    )


@router.get("/token/{token}", response_model=ShareAccess)
async def get_share_by_token(token: str):
    """Get share details by token (public endpoint)"""
    share = next((s for s in _shares.values() if s.share_token == token), None)
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # Check expiration (timezone-aware comparison)
    if share.expires_at:
        expires = datetime.fromisoformat(share.expires_at)
        # Ensure expires is timezone-aware
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        else:
            expires = expires.astimezone(timezone.utc)
        
        # Compare with timezone-aware current time
        now = datetime.now(timezone.utc)
        if now > expires:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share link has expired"
            )
    
    # Update access stats (thread-safe)
    share_lock = _get_share_lock(share.share_id)
    with share_lock:
        share.last_accessed = datetime.now(timezone.utc).isoformat()
        share.access_count += 1
        _shares[share.share_id] = share
    
    # Log access analytics
    from consultantos.api.analytics_endpoints import log_share_access
    log_share_access(share.share_id, None, share.last_accessed)
    logger.info(f"Share accessed: {share.share_id}, count: {share.access_count}")
    
    return share


@router.delete("/{share_id}")
async def revoke_share(
    share_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Revoke a share"""
    if share_id not in _shares:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    share = _shares[share_id]
    
    if share.shared_by != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own shares"
        )
    
    share.active = False
    _shares[share_id] = share
    
    return {"message": "Share revoked successfully"}


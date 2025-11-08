"""
Report sharing models for ConsultantOS (v0.4.0)
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum


class SharePermission(str, Enum):
    """Share permissions"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"


class ShareType(str, Enum):
    """Share type"""
    LINK = "link"
    EMAIL = "email"
    USER = "user"


class ShareAccess(BaseModel):
    """Share access model"""
    share_id: str
    report_id: str
    shared_by: str = Field(..., description="User ID who shared")
    
    # Access control
    permission: SharePermission = SharePermission.VIEW
    expires_at: Optional[str] = None
    
    # Sharing method
    share_type: ShareType = Field(..., description="link, email, user")
    shared_with: Optional[str] = None  # User ID or email
    
    @model_validator(mode='after')
    def validate_shared_with(self):
        """Validate that shared_with is required when share_type is EMAIL"""
        if self.share_type == ShareType.EMAIL and not self.shared_with:
            raise ValueError("shared_with is required when share_type is 'email'")
        return self
    
    # Link sharing
    share_token: Optional[str] = None  # For public links
    public_url: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_accessed: Optional[str] = None
    access_count: int = 0
    active: bool = True


class CreateShareRequest(BaseModel):
    """Request to share a report"""
    report_id: str
    permission: SharePermission = SharePermission.VIEW
    expires_at: Optional[str] = None  # ISO datetime
    share_type: ShareType = Field(..., description="link, email, or user")
    shared_with: Optional[str] = None  # Required if share_type is email
    message: Optional[str] = None  # Optional message for email shares
    
    @model_validator(mode='after')
    def validate_shared_with(self):
        """Validate that shared_with is required when share_type is EMAIL"""
        if self.share_type == ShareType.EMAIL and not self.shared_with:
            raise ValueError("shared_with is required when share_type is 'email'")
        return self


class ShareListResponse(BaseModel):
    """List of shares for a report"""
    report_id: str
    shares: List[ShareAccess]
    total: int


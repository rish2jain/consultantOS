"""
Comment models for report sharing (v0.5.0)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CommentStatus(str, Enum):
    """Comment status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    DELETED = "deleted"


class Comment(BaseModel):
    """Comment model"""
    comment_id: str
    report_id: str
    share_id: Optional[str] = None  # If comment is on a shared report
    parent_comment_id: Optional[str] = None  # For threaded comments
    
    # Content
    content: str = Field(..., min_length=1, max_length=5000)
    author_id: str = Field(..., description="User ID")
    author_name: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    status: CommentStatus = CommentStatus.ACTIVE
    
    # Location/context
    section: Optional[str] = None  # e.g., "porter", "swot", "executive_summary"
    page_number: Optional[int] = None
    
    # Reactions
    reactions: dict[str, int] = Field(default_factory=dict)  # emoji -> count


class CreateCommentRequest(BaseModel):
    """Request to create a comment"""
    report_id: str
    content: str
    share_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    section: Optional[str] = None
    page_number: Optional[int] = None


class UpdateCommentRequest(BaseModel):
    """Request to update a comment"""
    content: str


class CommentThread(BaseModel):
    """Comment thread (parent + replies)"""
    comment: Comment
    replies: List[Comment] = Field(default_factory=list)
    total_replies: int = 0


class CommentListResponse(BaseModel):
    """List of comments for a report"""
    report_id: str
    comments: List[CommentThread]
    total: int


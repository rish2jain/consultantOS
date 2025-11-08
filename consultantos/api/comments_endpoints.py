"""
Comment API endpoints for report sharing (v0.5.0)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Security
from consultantos.models.comments import (
    Comment,
    CreateCommentRequest,
    UpdateCommentRequest,
    CommentThread,
    CommentListResponse,
    CommentStatus
)
from consultantos.auth import verify_api_key
from consultantos.services.email_service import get_email_service
from consultantos.database import get_db_service
import secrets
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["comments"])

# In-memory comment store (in production, use database)
_comments: dict[str, Comment] = {}
_report_comments: dict[str, List[str]] = {}  # report_id -> list of comment_ids


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    request: CreateCommentRequest,
    user_info: dict = Security(verify_api_key)
):
    """Create a new comment"""
    comment_id = f"comment_{secrets.token_urlsafe(16)}"
    
    comment = Comment(
        comment_id=comment_id,
        report_id=request.report_id,
        share_id=request.share_id,
        parent_comment_id=request.parent_comment_id,
        content=request.content,
        author_id=user_info["user_id"],
        author_name=user_info.get("name"),
        section=request.section,
        page_number=request.page_number
    )
    
    _comments[comment_id] = comment
    
    # Update report comments index
    if request.report_id not in _report_comments:
        _report_comments[request.report_id] = []
    _report_comments[request.report_id].append(comment_id)
    
    # Send email notification to report owner
    try:
        db_service = get_db_service()
        report_metadata = db_service.get_report_metadata(request.report_id)
        if report_metadata and report_metadata.user_id:
            user_account = db_service.get_user(report_metadata.user_id)
            if user_account and user_account.email:
                email_service = get_email_service()
                comment_url = f"/reports/{request.report_id}#comment-{comment_id}"
                email_service.send_comment_notification(
                    to=user_account.email,
                    report_id=request.report_id,
                    commenter=user_info.get("name", "A user"),
                    comment=request.content[:100],  # First 100 chars
                    comment_url=comment_url
                )
    except Exception as e:
        logger.warning(f"Failed to send comment notification: {e}")
    
    return comment


@router.get("/report/{report_id}", response_model=CommentListResponse)
async def list_comments(
    report_id: str,
    section: Optional[str] = None
):
    """List comments for a report"""
    comment_ids = _report_comments.get(report_id, [])
    all_comments = [_comments[cid] for cid in comment_ids if cid in _comments]
    
    # Filter by section if provided
    if section:
        all_comments = [c for c in all_comments if c.section == section]
    
    # Filter active comments
    active_comments = [c for c in all_comments if c.status == CommentStatus.ACTIVE]
    
    # Build threads (parent comments with replies)
    parent_comments = [c for c in active_comments if c.parent_comment_id is None]
    threads = []
    
    for parent in parent_comments:
        replies = [c for c in active_comments if c.parent_comment_id == parent.comment_id]
        threads.append(CommentThread(
            comment=parent,
            replies=replies,
            total_replies=len(replies)
        ))
    
    return CommentListResponse(
        report_id=report_id,
        comments=threads,
        total=len(active_comments)
    )


@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: str,
    request: UpdateCommentRequest,
    user_info: dict = Security(verify_api_key)
):
    """Update a comment (only author)"""
    if comment_id not in _comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    comment = _comments[comment_id]
    
    if comment.author_id != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )
    
    comment.content = request.content
    comment.updated_at = datetime.now().isoformat()
    _comments[comment_id] = comment
    
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Delete a comment (soft delete)"""
    if comment_id not in _comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    comment = _comments[comment_id]
    
    if comment.author_id != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    comment.status = CommentStatus.DELETED
    _comments[comment_id] = comment
    
    return {"message": "Comment deleted successfully"}


@router.post("/{comment_id}/react")
async def add_reaction(
    comment_id: str,
    emoji: str,
    user_info: dict = Security(verify_api_key)
):
    """Add reaction to a comment"""
    if comment_id not in _comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    comment = _comments[comment_id]
    
    # Increment reaction count
    if emoji not in comment.reactions:
        comment.reactions[emoji] = 0
    comment.reactions[emoji] += 1
    
    _comments[comment_id] = comment
    
    return {"message": "Reaction added", "reactions": comment.reactions}


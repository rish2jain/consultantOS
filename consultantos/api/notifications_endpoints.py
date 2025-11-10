"""
Notifications API endpoints (v0.3.0)
Fully implemented with Firestore storage
"""
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Security, Query
from pydantic import BaseModel
from consultantos.auth import verify_api_key, get_api_key
from consultantos.database import get_db_service
from consultantos.log_utils import get_logger
from google.cloud import firestore

logger = get_logger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


# Request/Response Models
class Notification(BaseModel):
    id: str
    type: str
    title: str
    description: str
    read: bool
    created_at: str
    link: Optional[str] = None


class NotificationListResponse(BaseModel):
    notifications: List[Notification]
    count: int


class NotificationSettings(BaseModel):
    in_app_enabled: bool = True
    email_enabled: bool = False
    email_frequency: str = "daily"  # instant, daily, weekly


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    user_id: Optional[str] = Query(None, alias="user_id"),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """
    List notifications for a user
    
    **Authentication:** Optional. If authenticated, filters by user_id automatically.
    
    **Query Parameters:**
    - `user_id`: User ID to fetch notifications for (optional if authenticated)
    - `limit`: Maximum number of notifications to return (1-100, default: 50)
    - `unread_only`: If true, only return unread notifications
    """
    # Get user_id from API key if provided
    authenticated_user_id = None
    if api_key:
        try:
            from consultantos.auth import validate_api_key
            user_info = validate_api_key(api_key)
            if user_info:
                authenticated_user_id = user_info.get("user_id")
        except Exception:
            pass
    
    # Use authenticated user_id if no explicit user_id provided
    if authenticated_user_id and not user_id:
        user_id = authenticated_user_id
    
    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id is required. Provide via query parameter or API key authentication."
        )
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            # In-memory database fallback
            return {"notifications": [], "count": 0}
        
        # Query notifications subcollection
        notifications_ref = db.db.collection(f"users/{user_id}/notifications")
        query = notifications_ref.order_by("created_at", direction=firestore.Query.DESCENDING)
        
        if unread_only:
            query = query.where("read", "==", False)
        
        query = query.limit(limit)
        docs = query.stream()
        
        notifications = []
        for doc in docs:
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            created_at = data.get("created_at")
            if hasattr(created_at, 'isoformat'):
                created_at_str = created_at.isoformat()
            elif isinstance(created_at, datetime):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at)
            
            notifications.append(Notification(
                id=doc.id,
                type=data.get("type", "alert"),
                title=data.get("title", "Notification"),
                description=data.get("summary", data.get("description", "")),
                read=data.get("read", False),
                created_at=created_at_str,
                link=data.get("link")
            ))
        
        return {
            "notifications": notifications,
            "count": len(notifications)
        }
    except Exception as e:
        logger.error(
            "Failed to list notifications",
            extra={"user_id": user_id, "error": str(e)}
        )
        # Return empty list on error rather than failing
        return {"notifications": [], "count": 0}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user_info: Dict = Security(verify_api_key)
):
    """
    Mark a notification as read
    
    **Authentication:** Required
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Update notification in subcollection
        notification_ref = db.db.collection(f"users/{user_id}/notifications").document(notification_id)
        doc = notification_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Verify ownership
        data = doc.to_dict()
        if data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update read status
        notification_ref.update({
            "read": True,
            "read_at": datetime.utcnow()
        })
        
        return {
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to mark notification as read",
            extra={"notification_id": notification_id, "user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update notification")


@router.post("/read-all")
async def mark_all_notifications_read(
    user_info: Dict = Security(verify_api_key)
):
    """
    Mark all notifications as read for the authenticated user
    
    **Authentication:** Required
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get all unread notifications
        notifications_ref = db.db.collection(f"users/{user_id}/notifications")
        query = notifications_ref.where("read", "==", False)
        docs = query.stream()
        
        # Batch update
        batch = db.db.batch()
        count = 0
        for doc in docs:
            notification_ref = notifications_ref.document(doc.id)
            batch.update(notification_ref, {
                "read": True,
                "read_at": datetime.utcnow()
            })
            count += 1
        
        if count > 0:
            batch.commit()
        
        return {
            "message": f"Marked {count} notification(s) as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to mark all notifications as read",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update notifications")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_info: Dict = Security(verify_api_key)
):
    """
    Delete a notification
    
    **Authentication:** Required
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get notification to verify ownership
        notification_ref = db.db.collection(f"users/{user_id}/notifications").document(notification_id)
        doc = notification_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Verify ownership
        data = doc.to_dict()
        if data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete notification
        notification_ref.delete()
        
        return {
            "message": "Notification deleted",
            "notification_id": notification_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete notification",
            extra={"notification_id": notification_id, "user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to delete notification")


@router.post("/clear-all")
async def clear_all_notifications(
    user_info: Dict = Security(verify_api_key)
):
    """
    Clear all notifications for the authenticated user
    
    **Authentication:** Required
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Get all notifications
        notifications_ref = db.db.collection(f"users/{user_id}/notifications")
        docs = notifications_ref.stream()
        
        # Batch delete
        batch = db.db.batch()
        count = 0
        for doc in docs:
            notification_ref = notifications_ref.document(doc.id)
            batch.delete(notification_ref)
            count += 1
        
        if count > 0:
            batch.commit()
        
        return {
            "message": f"Cleared {count} notification(s)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to clear all notifications",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to clear notifications")


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    user_info: Dict = Security(verify_api_key)
):
    """
    Get notification settings for the authenticated user
    
    **Authentication:** Required
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            # Return defaults if database not available
            return NotificationSettings()
        
        # Get user document
        user_ref = db.db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # Return defaults for new user
            return NotificationSettings()
        
        user_data = user_doc.to_dict()
        settings_data = user_data.get("notification_settings", {})
        
        return NotificationSettings(
            in_app_enabled=settings_data.get("in_app_enabled", True),
            email_enabled=settings_data.get("email_enabled", False),
            email_frequency=settings_data.get("email_frequency", "daily")
        )
    except Exception as e:
        logger.error(
            "Failed to get notification settings",
            extra={"user_id": user_id, "error": str(e)}
        )
        # Return defaults on error
        return NotificationSettings()


@router.put("/settings")
async def update_notification_settings(
    settings: NotificationSettings,
    user_info: Dict = Security(verify_api_key)
):
    """
    Update notification settings for the authenticated user
    
    **Authentication:** Required
    
    **Request Body:**
    ```json
    {
        "in_app_enabled": true,
        "email_enabled": false,
        "email_frequency": "daily"
    }
    ```
    """
    user_id = user_info.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        db = get_db_service()
        if not hasattr(db, 'db'):
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Update user document with notification settings
        user_ref = db.db.collection("users").document(user_id)
        user_ref.set({
            "notification_settings": settings.model_dump()
        }, merge=True)
        
        return {
            "message": "Notification settings updated",
            "settings": settings.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update notification settings",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to update settings")


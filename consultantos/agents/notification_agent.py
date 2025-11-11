"""
Notification Agent for managing notifications and preferences
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationListRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user requesting notifications.")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of notifications to return.")
    unread_only: bool = Field(False, description="If true, only return unread notifications.")
    type_filter: Optional[str] = Field(None, description="Filter by notification type (e.g., 'alert', 'report', 'system').")


class NotificationSettingsRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user.")
    in_app_enabled: bool = Field(True, description="Enable in-app notifications.")
    email_enabled: bool = Field(False, description="Enable email notifications.")
    email_frequency: str = Field("daily", description="Email frequency: instant, daily, weekly.")


class NotificationActionRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user performing the action.")
    notification_id: str = Field(..., description="ID of the notification to act on.")
    action: str = Field(..., description="Action to perform (e.g., 'mark_read', 'mark_unread', 'delete').")


class NotificationResponse(BaseModel):
    notifications: List[Dict[str, Any]] = Field(..., description="List of notifications.")
    count: int = Field(..., description="Total number of notifications.")
    unread_count: int = Field(..., description="Number of unread notifications.")
    settings: Optional[Dict[str, Any]] = Field(None, description="User notification settings.")
    message: Optional[str] = Field(None, description="Confirmation message for actions.")


class NotificationAgent(BaseAgent):
    """Agent for managing notifications and preferences"""

    def __init__(self, timeout: int = 60):
        super().__init__(name="NotificationAgent", timeout=timeout)
        self.db_service = get_db_service()

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action_type = input_data.get("action_type", "list")

        if action_type == "list":
            request = NotificationListRequest(**input_data)
            notifications = await self._list_notifications(
                user_id=request.user_id,
                limit=request.limit,
                unread_only=request.unread_only,
                type_filter=request.type_filter
            )
            unread_count = sum(1 for n in notifications if not n.get("read", False))
            settings = await self._get_settings(request.user_id)
            return {
                "success": True,
                "data": NotificationResponse(
                    notifications=notifications,
                    count=len(notifications),
                    unread_count=unread_count,
                    settings=settings
                ).model_dump(),
                "error": None
            }

        elif action_type == "settings":
            request = NotificationSettingsRequest(**input_data)
            await self._update_settings(
                user_id=request.user_id,
                in_app_enabled=request.in_app_enabled,
                email_enabled=request.email_enabled,
                email_frequency=request.email_frequency
            )
            settings = await self._get_settings(request.user_id)
            return {
                "success": True,
                "data": NotificationResponse(
                    notifications=[],
                    count=0,
                    unread_count=0,
                    settings=settings,
                    message="Notification settings updated successfully."
                ).model_dump(),
                "error": None
            }

        elif action_type == "action":
            request = NotificationActionRequest(**input_data)
            message = await self._perform_action(
                user_id=request.user_id,
                notification_id=request.notification_id,
                action=request.action
            )
            return {
                "success": True,
                "data": NotificationResponse(
                    notifications=[],
                    count=0,
                    unread_count=0,
                    message=message
                ).model_dump(),
                "error": None
            }

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _list_notifications(
        self,
        user_id: str,
        limit: int,
        unread_only: bool,
        type_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """List notifications for a user"""
        try:
            if not hasattr(self.db_service, 'db'):
                return []

            from google.cloud import firestore
            notifications_ref = self.db_service.db.collection(f"users/{user_id}/notifications")
            query = notifications_ref.order_by("created_at", direction=firestore.Query.DESCENDING)

            if unread_only:
                query = query.where("read", "==", False)

            if type_filter:
                query = query.where("type", "==", type_filter)

            query = query.limit(limit)
            docs = query.stream()

            notifications = []
            for doc in docs:
                data = doc.to_dict()
                created_at = data.get("created_at")
                if hasattr(created_at, 'isoformat'):
                    created_at_str = created_at.isoformat()
                elif isinstance(created_at, datetime):
                    created_at_str = created_at.isoformat()
                else:
                    created_at_str = str(created_at)

                notifications.append({
                    "id": doc.id,
                    "type": data.get("type", "alert"),
                    "title": data.get("title", "Notification"),
                    "description": data.get("summary", data.get("description", "")),
                    "read": data.get("read", False),
                    "created_at": created_at_str,
                    "link": data.get("link")
                })

            return notifications
        except Exception as e:
            logger.error(f"Failed to list notifications: {e}")
            return []

    async def _get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get notification settings for a user"""
        try:
            if not hasattr(self.db_service, 'db'):
                return {
                    "in_app_enabled": True,
                    "email_enabled": False,
                    "email_frequency": "daily"
                }

            user_ref = self.db_service.db.collection("users").document(user_id)
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                settings = user_data.get("notification_settings", {})
                return {
                    "in_app_enabled": settings.get("in_app_enabled", True),
                    "email_enabled": settings.get("email_enabled", False),
                    "email_frequency": settings.get("email_frequency", "daily")
                }
            else:
                return {
                    "in_app_enabled": True,
                    "email_enabled": False,
                    "email_frequency": "daily"
                }
        except Exception as e:
            logger.error(f"Failed to get notification settings: {e}")
            return {
                "in_app_enabled": True,
                "email_enabled": False,
                "email_frequency": "daily"
            }

    async def _update_settings(
        self,
        user_id: str,
        in_app_enabled: bool,
        email_enabled: bool,
        email_frequency: str
    ):
        """Update notification settings for a user"""
        try:
            if not hasattr(self.db_service, 'db'):
                return

            user_ref = self.db_service.db.collection("users").document(user_id)
            user_ref.set({
                "notification_settings": {
                    "in_app_enabled": in_app_enabled,
                    "email_enabled": email_enabled,
                    "email_frequency": email_frequency
                }
            }, merge=True)
        except Exception as e:
            logger.error(f"Failed to update notification settings: {e}")
            raise

    async def _perform_action(
        self,
        user_id: str,
        notification_id: str,
        action: str
    ) -> str:
        """Perform an action on a notification"""
        try:
            if not hasattr(self.db_service, 'db'):
                return f"Action '{action}' completed (in-memory mode)."

            notification_ref = self.db_service.db.collection(f"users/{user_id}/notifications").document(notification_id)
            notification_doc = notification_ref.get()

            if not notification_doc.exists:
                raise ValueError(f"Notification {notification_id} not found")

            if action == "mark_read":
                notification_ref.update({"read": True, "read_at": datetime.now()})
                return f"Notification {notification_id} marked as read."
            elif action == "mark_unread":
                notification_ref.update({"read": False, "read_at": None})
                return f"Notification {notification_id} marked as unread."
            elif action == "delete":
                notification_ref.delete()
                return f"Notification {notification_id} deleted."
            else:
                raise ValueError(f"Unsupported action: {action}")
        except Exception as e:
            logger.error(f"Failed to perform notification action: {e}")
            raise


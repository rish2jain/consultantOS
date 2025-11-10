"""
In-app notification channel using Firestore for storage.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from .base_channel import AlertChannel, AlertDeliveryResult, DeliveryStatus
from consultantos.database import get_db_service


class InAppAlertChannel(AlertChannel):
    """
    In-app notification channel that stores alerts in Firestore.

    Notifications are stored in a user-specific collection and can be:
    - Retrieved via API for dashboard display
    - Marked as read/unread
    - Filtered by date, confidence, type
    - Paginated for performance
    """

    async def send_alert(
        self,
        alert_id: str,
        monitor_id: str,
        title: str,
        summary: str,
        confidence: float,
        changes: list,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Store alert as in-app notification in Firestore"""
        try:
            db = get_db_service()

            # Get user ID from preferences
            user_id = user_preferences.get("user_id")
            if not user_id:
                return AlertDeliveryResult(
                    channel="in_app",
                    status=DeliveryStatus.FAILED,
                    error_message="No user_id in preferences"
                )

            # Build compact notification document
            notification = {
                "alert_id": alert_id,
                "monitor_id": monitor_id,
                "title": self._truncate_text(title, 200),
                "summary": self._truncate_text(summary, 500),
                "confidence": confidence,
                "change_count": len(changes),
                "top_changes": [
                    {
                        "type": change.get("change_type"),
                        "title": self._truncate_text(change.get("title", ""), 150),
                        "confidence": change.get("confidence", 0.0)
                    }
                    for change in changes[:3]  # Store top 3 changes only
                ],
                "created_at": datetime.utcnow(),
                "read": False,
                "read_at": None,
                "priority": self._calculate_priority(confidence),
                "user_id": user_id
            }

            # Store in Firestore under user's notifications collection
            collection_path = f"users/{user_id}/notifications"
            doc_id = f"alert_{alert_id}"

            await db.set_document(collection_path, doc_id, notification)

            return AlertDeliveryResult(
                channel="in_app",
                status=DeliveryStatus.SENT,
                delivered_at=datetime.utcnow(),
                metadata={
                    "user_id": user_id,
                    "notification_id": doc_id,
                    "collection": collection_path
                }
            )

        except Exception as e:
            self.logger.error(f"In-app notification storage failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="in_app",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    async def test_delivery(
        self,
        user_preferences: Dict[str, Any]
    ) -> AlertDeliveryResult:
        """Create test in-app notification"""
        try:
            db = get_db_service()

            user_id = user_preferences.get("user_id")
            if not user_id:
                return AlertDeliveryResult(
                    channel="in_app",
                    status=DeliveryStatus.FAILED,
                    error_message="No user_id in preferences"
                )

            # Create test notification
            test_notification = {
                "alert_id": f"test_{datetime.utcnow().isoformat()}",
                "monitor_id": "test_monitor",
                "title": "🧪 Test Notification",
                "summary": "This is a test in-app notification from ConsultantOS. If you see this, your in-app notifications are working correctly!",
                "confidence": 1.0,
                "change_count": 1,
                "top_changes": [
                    {
                        "type": "test",
                        "title": "Test notification delivery",
                        "confidence": 1.0
                    }
                ],
                "created_at": datetime.utcnow(),
                "read": False,
                "read_at": None,
                "priority": "low",
                "user_id": user_id,
                "is_test": True
            }

            collection_path = f"users/{user_id}/notifications"
            doc_id = f"test_{datetime.utcnow().timestamp()}"

            await db.set_document(collection_path, doc_id, test_notification)

            return AlertDeliveryResult(
                channel="in_app",
                status=DeliveryStatus.SENT,
                delivered_at=datetime.utcnow(),
                metadata={
                    "user_id": user_id,
                    "notification_id": doc_id,
                    "is_test": True
                }
            )

        except Exception as e:
            self.logger.error(f"Test in-app notification failed: {e}", exc_info=True)
            return AlertDeliveryResult(
                channel="in_app",
                status=DeliveryStatus.FAILED,
                error_message=str(e)
            )

    def _calculate_priority(self, confidence: float) -> str:
        """Calculate notification priority based on confidence"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"

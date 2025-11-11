"""
Alert Feedback Agent for managing alert feedback and improvement
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
from consultantos.models.monitoring import AlertFeedbackRequest
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertFeedbackSubmitRequest(BaseModel):
    alert_id: str = Field(..., description="ID of the alert to provide feedback on.")
    user_id: str = Field(..., description="ID of the user providing feedback.")
    feedback: str = Field(..., description="Feedback text: 'helpful', 'not_helpful', 'false_positive', etc.")
    action_taken: Optional[str] = Field(None, description="Action taken based on alert.")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes.")


class AlertFeedbackListRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user requesting feedback.")
    alert_id: Optional[str] = Field(None, description="Filter by alert ID.")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of feedback items to return.")


class AlertFeedbackStatsRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user requesting stats.")
    monitor_id: Optional[str] = Field(None, description="Filter by monitor ID.")


class AlertFeedbackResponse(BaseModel):
    feedback: Optional[Dict[str, Any]] = Field(None, description="Single feedback item.")
    feedback_list: List[Dict[str, Any]] = Field(default_factory=list, description="List of feedback items.")
    stats: Optional[Dict[str, Any]] = Field(None, description="Feedback statistics.")
    message: Optional[str] = Field(None, description="Confirmation message for actions.")


class AlertFeedbackAgent(BaseAgent):
    """Agent for managing alert feedback and improvement"""

    def __init__(self, timeout: int = 60):
        super().__init__(name="AlertFeedbackAgent", timeout=timeout)
        self.db_service = get_db_service()

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action_type = input_data.get("action_type", "submit")

        if action_type == "submit":
            request = AlertFeedbackSubmitRequest(**input_data)
            await self._submit_feedback(
                alert_id=request.alert_id,
                user_id=request.user_id,
                feedback=request.feedback,
                action_taken=request.action_taken,
                notes=request.notes
            )
            return {
                "success": True,
                "data": AlertFeedbackResponse(
                    message="Feedback submitted successfully. Thank you for helping improve our alerts!"
                ).model_dump(),
                "error": None
            }

        elif action_type == "list":
            request = AlertFeedbackListRequest(**input_data)
            feedback_list = await self._list_feedback(
                user_id=request.user_id,
                alert_id=request.alert_id,
                limit=request.limit
            )
            return {
                "success": True,
                "data": AlertFeedbackResponse(feedback_list=feedback_list).model_dump(),
                "error": None
            }

        elif action_type == "stats":
            request = AlertFeedbackStatsRequest(**input_data)
            stats = await self._get_feedback_stats(
                user_id=request.user_id,
                monitor_id=request.monitor_id
            )
            return {
                "success": True,
                "data": AlertFeedbackResponse(stats=stats).model_dump(),
                "error": None
            }

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _submit_feedback(
        self,
        alert_id: str,
        user_id: str,
        feedback: str,
        action_taken: Optional[str],
        notes: Optional[str]
    ):
        """Submit feedback on an alert"""
        try:
            if not hasattr(self.db_service, 'db'):
                logger.warning("Database service not available, feedback not persisted")
                return

            # Get alert
            alert = await self.db_service.get_alert(alert_id)
            if not alert:
                raise ValueError(f"Alert {alert_id} not found")

            # Verify ownership
            monitor = await self.db_service.get_monitor(alert.monitor_id)
            if not monitor or monitor.user_id != user_id:
                raise ValueError("Alert not found or unauthorized")

            # Store feedback and notes in structured format
            feedback_data = {
                "feedback": feedback,
                "notes": notes if notes else None
            }
            alert.user_feedback = json.dumps(feedback_data)
            alert.action_taken = action_taken

            await self.db_service.update_alert(alert)

            logger.info(
                f"Alert feedback received: alert_id={alert_id}, feedback={feedback}, user_id={user_id}"
            )
        except Exception as e:
            logger.error(f"Failed to submit alert feedback: {e}")
            raise

    async def _list_feedback(
        self,
        user_id: str,
        alert_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """List feedback for alerts"""
        try:
            if not hasattr(self.db_service, 'db'):
                return []

            # Get user's monitors
            monitors = await self.db_service.get_user_monitors(user_id, status=None)
            monitor_ids = [m.id for m in monitors]

            feedback_list = []

            # Get alerts with feedback
            for monitor_id in monitor_ids:
                alerts = await self.db_service.get_monitor_alerts(monitor_id, limit=1000)
                for alert in alerts:
                    if alert.user_feedback or alert.action_taken:
                        if alert_id and alert.id != alert_id:
                            continue

                        # Parse JSON feedback if available
                        feedback_text = alert.user_feedback
                        notes_text = None
                        if alert.user_feedback:
                            try:
                                feedback_data = json.loads(alert.user_feedback)
                                feedback_text = feedback_data.get("feedback", alert.user_feedback)
                                notes_text = feedback_data.get("notes")
                            except (json.JSONDecodeError, TypeError):
                                # Fallback for legacy format (plain string)
                                feedback_text = alert.user_feedback
                        
                        feedback_list.append({
                            "alert_id": alert.id,
                            "monitor_id": alert.monitor_id,
                            "title": alert.title,
                            "feedback": feedback_text,
                            "notes": notes_text,
                            "action_taken": alert.action_taken,
                            "created_at": alert.created_at.isoformat() if hasattr(alert.created_at, 'isoformat') else str(alert.created_at),
                            "confidence": alert.confidence
                        })

            # Sort by created_at descending
            feedback_list.sort(
                key=lambda x: x["created_at"],
                reverse=True
            )

            return feedback_list[:limit]
        except Exception as e:
            logger.error(f"Failed to list feedback: {e}")
            return []

    async def _get_feedback_stats(
        self,
        user_id: str,
        monitor_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get feedback statistics"""
        try:
            if not hasattr(self.db_service, 'db'):
                return {
                    "total_feedback": 0,
                    "helpful_count": 0,
                    "not_helpful_count": 0,
                    "false_positive_count": 0,
                    "action_taken_count": 0
                }

            # Get user's monitors
            if monitor_id:
                monitors = [await self.db_service.get_monitor(monitor_id)]
            else:
                monitors = await self.db_service.get_user_monitors(user_id, status=None)

            total_feedback = 0
            helpful_count = 0
            not_helpful_count = 0
            false_positive_count = 0
            action_taken_count = 0

            for monitor in monitors:
                if not monitor:
                    continue
                alerts = await self.db_service.get_monitor_alerts(monitor.id, limit=1000)
                for alert in alerts:
                    if alert.user_feedback:
                        total_feedback += 1
                        # Parse JSON feedback if available
                        feedback_text = alert.user_feedback
                        try:
                            feedback_data = json.loads(alert.user_feedback)
                            feedback_text = feedback_data.get("feedback", alert.user_feedback)
                        except (json.JSONDecodeError, TypeError):
                            # Fallback for legacy format (plain string)
                            feedback_text = alert.user_feedback
                        
                        feedback_lower = feedback_text.lower()
                        if "helpful" in feedback_lower:
                            helpful_count += 1
                        if "not_helpful" in feedback_lower or "unhelpful" in feedback_lower:
                            not_helpful_count += 1
                        if "false_positive" in feedback_lower or "false positive" in feedback_lower:
                            false_positive_count += 1
                    if alert.action_taken:
                        action_taken_count += 1

            return {
                "total_feedback": total_feedback,
                "helpful_count": helpful_count,
                "not_helpful_count": not_helpful_count,
                "false_positive_count": false_positive_count,
                "action_taken_count": action_taken_count,
                "helpful_rate": helpful_count / total_feedback if total_feedback > 0 else 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get feedback stats: {e}")
            return {
                "total_feedback": 0,
                "helpful_count": 0,
                "not_helpful_count": 0,
                "false_positive_count": 0,
                "action_taken_count": 0,
                "helpful_rate": 0.0
            }


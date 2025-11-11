"""
Job Management Agent - Handles job queue, progress tracking, and history
"""
from typing import Dict, Any, List, Optional
import inspect
from datetime import datetime
from consultantos.agents.base_agent import BaseAgent
from consultantos.jobs.queue import JobQueue, JobStatus
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class JobListResult(BaseModel):
    """Job list result"""
    jobs: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0)
    pending: int = Field(default=0)
    running: int = Field(default=0)
    completed: int = Field(default=0)
    failed: int = Field(default=0)


class JobManagementAgent(BaseAgent):
    """Agent for managing jobs: queue, progress, and history"""

    def __init__(self, timeout: int = 30):
        super().__init__(
            name="job_management_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a job management specialist.
        Track job progress, manage queue, and provide job analytics.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage jobs: list, get status, cancel, retry.

        Args:
            input_data: Dictionary containing:
                - action: Action to perform ('list', 'status', 'cancel', 'retry', 'history')
                - user_id: User ID for filtering (optional)
                - status: Filter by status (optional)
                - job_id: Job ID (for status/cancel/retry actions)
                - limit: Limit for list/history (default: 50)

        Returns:
            Result dictionary with job data
        """
        action = input_data.get("action", "list")
        user_id = input_data.get("user_id")
        status = input_data.get("status")
        job_id = input_data.get("job_id")
        limit = input_data.get("limit", 50)

        try:
            # Validate job_id is provided for actions that require it
            if action in ("status", "cancel", "retry") and not job_id:
                raise ValueError(f"job_id is required for {action} action")
            
            job_queue = JobQueue()

            if action == "list":
                return await self._list_jobs(job_queue, user_id, status, limit)
            elif action == "status":
                return await self._get_job_status(job_queue, job_id)
            elif action == "cancel":
                return await self._cancel_job(job_queue, job_id, user_id)
            elif action == "retry":
                return await self._retry_job(job_queue, job_id, user_id)
            elif action == "history":
                return await self._get_job_history(job_queue, user_id, limit)
            else:
                raise ValueError(f"Unknown action: {action}")
        except ValueError as e:
            logger.error(f"Job management error: {e}")
            raise
        except Exception as e:
            logger.error(f"Job management error: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _list_jobs(
        self,
        job_queue: JobQueue,
        user_id: Optional[str],
        status: Optional[str],
        limit: int
    ) -> Dict[str, Any]:
        """List jobs with filtering"""
        try:
            all_jobs = await self._maybe_await(
                job_queue.list_jobs(user_id=user_id, limit=max(limit, 50))
            )

            # Filter by user_id
            if user_id:
                all_jobs = [
                    j for j in all_jobs
                    if (isinstance(j, dict) and j.get('user_id') == user_id)
                    or (not isinstance(j, dict) and getattr(j, 'user_id', None) == user_id)
                ]

            # Filter by status
            if status:
                status_filters = self._parse_status_filter(status)
                all_jobs = [
                    j for j in all_jobs
                    if self._normalize_status_value(
                        j.get('status') if isinstance(j, dict) else getattr(j, 'status', None),
                        default=None
                    ) in status_filters
                ]

            # Limit
            jobs = all_jobs[:limit]

            # Count by status
            status_counts = self._count_statuses(all_jobs)

            result = JobListResult(
                jobs=[self._serialize_job(j) for j in jobs],
                total=len(all_jobs),
                pending=status_counts["pending"],
                running=status_counts["running"],
                completed=status_counts["completed"],
                failed=status_counts["failed"]
            )
            
            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _get_job_status(
        self,
        job_queue: JobQueue,
        job_id: str
    ) -> Dict[str, Any]:
        """Get job status"""
        try:
            job = await self._maybe_await(job_queue.get_status(job_id))
            if not job:
                return {
                    "success": False,
                    "data": None,
                    "error": "Job not found"
                }

            return {
                "success": True,
                "data": self._serialize_job(job),
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _cancel_job(
        self,
        job_queue: JobQueue,
        job_id: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Cancel a job"""
        try:
            job = await self._maybe_await(job_queue.get_status(job_id))
            if not job or job.get('status') in (None, 'not_found'):
                return {
                    "success": False,
                    "data": None,
                    "error": "Job not found"
                }

            normalized_status = self._normalize_status_value(job.get('status'))
            if normalized_status not in {"pending", "running"}:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Cannot cancel job in {normalized_status} state"
                }

            await self._maybe_await(job_queue.update_status(job_id, JobStatus.CANCELLED))

            return {
                "success": True,
                "data": {"job_id": job_id, "status": JobStatus.CANCELLED.value},
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _retry_job(
        self,
        job_queue: JobQueue,
        job_id: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Retry a failed job"""
        try:
            job = await self._maybe_await(job_queue.get_status(job_id))
            if not job or job.get('status') in (None, 'not_found'):
                return {
                    "success": False,
                    "data": None,
                    "error": "Job not found"
                }

            normalized_status = self._normalize_status_value(job.get('status'))
            if normalized_status != "failed":
                return {
                    "success": False,
                    "data": None,
                    "error": "Only failed jobs can be retried"
                }

            await self._maybe_await(job_queue.update_status(job_id, JobStatus.PENDING))

            return {
                "success": True,
                "data": {"job_id": job_id, "status": JobStatus.PENDING.value},
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to retry job: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _get_job_history(
        self,
        job_queue: JobQueue,
        user_id: Optional[str],
        limit: int
    ) -> Dict[str, Any]:
        """Get job history (completed and failed)"""
        try:
            all_jobs = await self._maybe_await(
                job_queue.list_jobs(user_id=user_id, limit=max(limit, 100))
            )

            # Filter completed and failed
            history_jobs = [
                j for j in all_jobs
                if self._normalize_status_value(
                    j.get('status') if isinstance(j, dict) else getattr(j, 'status', None)
                ) in {"completed", "failed"}
            ]
            
            # Sort by created_at descending
            history_jobs.sort(
                key=lambda j: (
                    j.get('created_at') if isinstance(j, dict) else getattr(j, 'created_at', '')
                ),
                reverse=True
            )
            
            # Limit
            jobs = history_jobs[:limit]
            
            return {
                "success": True,
                "data": {
                    "jobs": [self._serialize_job(j) for j in jobs],
                    "total": len(history_jobs)
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to get job history: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _serialize_job(self, job: Any) -> Dict[str, Any]:
        """Serialize job to dict"""
        if isinstance(job, dict):
            status_value = self._normalize_status_value(job.get('status')) or 'pending'
            return {
                "id": job.get('job_id') or job.get('id', ''),
                "status": status_value,
                "progress": job.get('progress', 0),
                "created_at": job.get('created_at', ''),
                "updated_at": job.get('updated_at', job.get('created_at', '')),
                "completed_at": job.get('completed_at'),
                "error": job.get('error'),
                "result": job.get('result'),
                "company": job.get('company', 'Unknown'),
            }

        status_value = self._normalize_status_value(getattr(job, 'status', None)) or 'pending'
        return {
            "id": getattr(job, 'id', ''),
            "status": status_value,
            "progress": getattr(job, 'progress', 0),
            "created_at": getattr(job, 'created_at', ''),
            "updated_at": getattr(job, 'updated_at', ''),
            "completed_at": getattr(job, 'completed_at', None),
            "error": getattr(job, 'error', None),
            "result": getattr(job, 'result', None),
            "company": getattr(job, 'company', 'Unknown'),
        }

    def _parse_status_filter(self, status_filter: str) -> set[str]:
        statuses = set()
        for raw in status_filter.split(','):
            normalized = self._normalize_status_value(raw, default=None)
            if normalized:
                statuses.add(normalized)
        return statuses or {"pending", "running", "completed", "failed"}

    def _count_statuses(self, jobs: List[Any]) -> Dict[str, int]:
        counts = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
        }
        for job in jobs:
            status_value = self._normalize_status_value(
                job.get('status') if isinstance(job, dict) else getattr(job, 'status', None),
                default=None
            )
            if status_value in counts:
                counts[status_value] += 1
        return counts

    def _normalize_status_value(self, status: Optional[Any], default: Optional[str] = "pending") -> Optional[str]:
        if not status:
            return default

        value = str(status).lower().strip()
        mapping = {
            JobStatus.PENDING.value: "pending",
            JobStatus.PROCESSING.value: "running",
            "running": "running",
            JobStatus.COMPLETED.value: "completed",
            JobStatus.FAILED.value: "failed",
            JobStatus.CANCELLED.value: "cancelled",
        }
        return mapping.get(value, default if default is not None else value)

    async def _maybe_await(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return await value
        return value

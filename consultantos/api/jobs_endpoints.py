"""
Job management endpoints
"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from consultantos.jobs.queue import JobQueue, JobStatus
from consultantos.jobs.worker import get_worker

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.get("/{job_id}/status")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get job status

    Args:
        job_id: Job identifier

    Returns:
        Job status information including completion state and results
    """
    queue = JobQueue()
    status = await queue.get_status(job_id)
    return status


@router.post("/worker")
async def process_job_worker(
    job_id: str,
    background_tasks: BackgroundTasks
):
    """
    Worker endpoint for processing jobs

    This endpoint can be called by:
    - Cloud Tasks for reliable async processing
    - Direct HTTP requests for immediate processing
    - Internal worker for poll-based processing

    Args:
        job_id: Job identifier to process

    Returns:
        Success confirmation with job_id
    """
    try:
        # Get worker instance
        worker = get_worker()

        # Process job in background to avoid timeout
        background_tasks.add_task(worker.process_job, job_id)

        logger.info(f"Job {job_id} queued for processing via worker endpoint")

        return {
            "success": True,
            "job_id": job_id,
            "message": "Job processing started",
            "status_url": f"/jobs/{job_id}/status"
        }

    except Exception as e:
        logger.error(f"Failed to process job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process job: {str(e)}"
        )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str) -> Dict[str, Any]:
    """
    Cancel a pending or processing job

    Args:
        job_id: Job identifier

    Returns:
        Cancellation confirmation
    """
    try:
        queue = JobQueue()

        # Get current status
        status = await queue.get_status(job_id)

        if status["status"] not in [JobStatus.PENDING.value, JobStatus.PROCESSING.value]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel job in {status['status']} state"
            )

        # Update status to cancelled
        await queue.update_status(job_id, JobStatus.CANCELLED)

        logger.info(f"Job {job_id} cancelled")

        return {
            "success": True,
            "job_id": job_id,
            "message": "Job cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )

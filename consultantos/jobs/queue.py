"""
Job queue for async report processing
"""
import uuid
import logging
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from consultantos.database import get_db_service
from consultantos.models import AnalysisRequest

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobQueue:
    """Job queue for async analysis processing"""
    
    def __init__(self):
        self.db_service = get_db_service()
    
    async def enqueue(
        self,
        analysis_request: AnalysisRequest,
        user_id: Optional[str] = None
    ) -> str:
        """
        Enqueue analysis job for async processing
        
        Args:
            analysis_request: Analysis request to process
            user_id: Optional user ID
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Store job metadata in database
        job_metadata = {
            "job_id": job_id,
            "status": JobStatus.PENDING.value,
            "request": analysis_request.dict(),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # Store in database (would use proper job table in production)
            # For now, use report metadata table with job prefix
            from consultantos.database import ReportMetadata
            job_record = ReportMetadata(
                report_id=f"job_{job_id}",
                user_id=user_id,
                company=analysis_request.company,
                industry=analysis_request.industry,
                frameworks=analysis_request.frameworks,
                status=JobStatus.PENDING.value,
                confidence_score=0.0,
                execution_time_seconds=0.0
            )
            self.db_service.create_report_metadata(job_record)
            
            logger.info(f"Job {job_id} enqueued for company {analysis_request.company}")
            return job_id
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}", exc_info=True)
            raise
    
    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status dictionary
        """
        try:
            metadata = self.db_service.get_report_metadata(f"job_{job_id}")
            if metadata:
                return {
                    "job_id": job_id,
                    "status": metadata.status,
                    "company": metadata.company,
                    "industry": metadata.industry,
                    "frameworks": metadata.frameworks,
                    "created_at": metadata.created_at,
                    "updated_at": getattr(metadata, 'updated_at', metadata.created_at),
                    "report_id": metadata.report_id if hasattr(metadata, 'report_id') and metadata.report_id and not metadata.report_id.startswith('job_') else None,
                    "error": getattr(metadata, 'error_message', None)
                }
            else:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "error": "Job not found"
                }
        except Exception as e:
            logger.error(f"Failed to get job status: {e}", exc_info=True)
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }
    
    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        report_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Update job status
        
        Args:
            job_id: Job identifier
            status: New status
            report_id: Optional report ID when completed
            error: Optional error message
        """
        try:
            updates = {
                "status": status.value,
                "updated_at": datetime.now().isoformat()
            }
            
            if report_id:
                updates["report_id"] = report_id
            
            if error:
                updates["error_message"] = error
            
            self.db_service.update_report_metadata(f"job_{job_id}", updates)
            logger.info(f"Job {job_id} status updated to {status.value}")
        except Exception as e:
            logger.error(f"Failed to update job status: {e}", exc_info=True)
    
    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List jobs with optional filters
        
        Args:
            user_id: Filter by user ID
            status: Filter by status
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        try:
            # Use report listing with job filter
            reports = self.db_service.list_reports(user_id=user_id, limit=limit * 2)
            
            # Filter for jobs and apply status filter
            jobs = []
            for report in reports:
                if report.report_id and report.report_id.startswith("job_"):
                    job_id = report.report_id.replace("job_", "")
                    job_status = JobStatus(report.status) if report.status in [s.value for s in JobStatus] else JobStatus.PENDING
                    
                    if status is None or job_status == status:
                        jobs.append({
                            "job_id": job_id,
                            "status": job_status.value,
                            "company": report.company,
                            "created_at": report.created_at
                        })
                    
                    if len(jobs) >= limit:
                        break
            
            return jobs
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}", exc_info=True)
            return []


# Convenience functions
async def create_job(analysis_request: AnalysisRequest, user_id: Optional[str] = None) -> str:
    """Create a new job"""
    queue = JobQueue()
    return await queue.enqueue(analysis_request, user_id)


async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get job status"""
    queue = JobQueue()
    return await queue.get_status(job_id)


async def update_job_status(
    job_id: str,
    status: JobStatus,
    report_id: Optional[str] = None,
    error: Optional[str] = None
):
    """Update job status"""
    queue = JobQueue()
    await queue.update_status(job_id, status, report_id, error)


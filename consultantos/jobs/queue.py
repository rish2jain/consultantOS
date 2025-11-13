"""
Job queue for async report processing
"""
import uuid
import logging
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from consultantos import database, models

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
        # Get fresh database service reference to ensure it's initialized
        self.db_service = database.get_db_service()
        if self.db_service is None:
            logger.warning("JobQueue initialized with None db_service")
    
    async def enqueue(
        self,
        analysis_request: models.AnalysisRequest,
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
            "request": analysis_request.model_dump(),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # Store in database (would use proper job table in production)
            # For now, use report metadata table with job prefix
            job_record = database.ReportMetadata(
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
        statuses: Optional[List[JobStatus]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List jobs with optional filters
        
        Includes both:
        - Actual job records (from async jobs with report_id starting with "job_")
        - Completed reports (from sync jobs) treated as completed jobs
        
        Args:
            user_id: Filter by user ID
            status: Filter by single status (deprecated, use statuses)
            statuses: Filter by list of statuses
            limit: Maximum number of jobs to return
        
        Returns:
            List of job dictionaries
        """
        try:
            # Check if db_service is available
            if self.db_service is None:
                logger.warning("Database service is None, returning empty jobs list")
                return []
            
            # Use report listing with job filter
            try:
                reports = self.db_service.list_reports(user_id=user_id, limit=limit * 3)
            except Exception as db_error:
                logger.error(f"Database list_reports failed: {db_error}", exc_info=True)
                return []
            
            # Ensure reports is a list
            if not isinstance(reports, list):
                logger.warning(f"list_reports returned non-list: {type(reports)}")
                return []
            
            # Determine which statuses to filter by
            filter_statuses = statuses if statuses is not None else ([status] if status is not None else None)
            
            # Filter for jobs and apply status filter
            jobs = []
            for report in reports:
                try:
                    # Skip if report_id is missing
                    if not report or not hasattr(report, 'report_id') or not report.report_id:
                        continue
                    
                    # Handle job records (from async jobs)
                    if report.report_id.startswith("job_"):
                        job_id = report.report_id.replace("job_", "")
                        
                        # Safely get job status
                        try:
                            if hasattr(report, 'status') and report.status:
                                if report.status in [s.value for s in JobStatus]:
                                    job_status = JobStatus(report.status)
                                else:
                                    job_status = JobStatus.PENDING
                            else:
                                job_status = JobStatus.PENDING
                        except (ValueError, AttributeError, TypeError) as status_error:
                            logger.warning(f"Failed to parse job status for {job_id}: {status_error}")
                            job_status = JobStatus.PENDING
                        
                        # Apply status filter if specified
                        if filter_statuses is None or job_status in filter_statuses:
                            jobs.append({
                                "job_id": job_id,
                                "status": job_status.value,
                                "company": getattr(report, 'company', 'Unknown') or 'Unknown',
                                "industry": getattr(report, 'industry', None),
                                "frameworks": getattr(report, 'frameworks', []),
                                "created_at": getattr(report, 'created_at', None) or datetime.now().isoformat(),
                                "updated_at": getattr(report, 'updated_at', None) or getattr(report, 'created_at', None) or datetime.now().isoformat(),
                                "result": {
                                    "report_id": getattr(report, 'report_id', None) if not getattr(report, 'report_id', '').startswith('job_') else None
                                } if hasattr(report, 'report_id') and not report.report_id.startswith('job_') else None
                            })
                    
                    # Handle completed reports (from sync jobs) - only include if filtering for completed or no filter
                    elif filter_statuses is None or JobStatus.COMPLETED in filter_statuses:
                        # Only include completed reports (from sync analysis)
                        report_status = getattr(report, 'status', None)
                        # Normalize status to JobStatus enum value
                        if report_status is None:
                            report_status = JobStatus.COMPLETED.value
                        elif isinstance(report_status, JobStatus):
                            report_status = report_status.value
                        elif report_status not in [s.value for s in JobStatus]:
                            report_status = JobStatus.COMPLETED.value
                        
                        if report_status == JobStatus.COMPLETED.value:
                            # Use report_id as job_id for sync jobs
                            job_id = report.report_id
                            
                            jobs.append({
                                "job_id": job_id,
                                "status": JobStatus.COMPLETED.value,
                                "company": getattr(report, 'company', 'Unknown') or 'Unknown',
                                "industry": getattr(report, 'industry', None),
                                "frameworks": getattr(report, 'frameworks', []),
                                "created_at": getattr(report, 'created_at', None) or datetime.now().isoformat(),
                                "updated_at": getattr(report, 'updated_at', None) or getattr(report, 'created_at', None) or datetime.now().isoformat(),
                                "progress": 100,
                                "result": {
                                    "report_id": report.report_id
                                }
                        })
                    
                    if len(jobs) >= limit:
                        break
                except Exception as report_error:
                    logger.warning(f"Failed to process report: {report_error}")
                    continue
            
            return jobs
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}", exc_info=True)
            return []


# Convenience functions
AnalysisRequest = models.AnalysisRequest


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
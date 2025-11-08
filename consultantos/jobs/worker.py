"""
Background worker for processing analysis jobs
"""
import asyncio
import logging
import threading
import uuid
from typing import Optional
from consultantos.jobs.queue import JobQueue, JobStatus
from consultantos.orchestrator import AnalysisOrchestrator
from consultantos.reports import generate_pdf_report
from consultantos.storage import get_storage_service
from consultantos.database import get_db_service, ReportMetadata
from consultantos.models import AnalysisRequest
from datetime import datetime
from consultantos.utils.sanitize import sanitize_input

logger = logging.getLogger(__name__)


class AnalysisWorker:
    """Background worker for processing analysis jobs"""
    
    def __init__(self):
        self.queue = JobQueue()
        self.orchestrator = AnalysisOrchestrator()
        self.storage_service = get_storage_service()
        self.db_service = get_db_service()
        self.running = False
    
    async def process_job(self, job_id: str):
        """
        Process a single job
        
        Args:
            job_id: Job identifier
        """
        try:
            # Get job details
            job_status = await self.queue.get_status(job_id)
            
            if job_status["status"] != JobStatus.PENDING.value:
                logger.warning(f"Job {job_id} is not pending, skipping")
                return
            
            # Update status to processing
            await self.queue.update_status(job_id, JobStatus.PROCESSING)
            
            # Reconstruct analysis request
            job_metadata = self.db_service.get_report_metadata(f"job_{job_id}")
            if not job_metadata:
                raise Exception("Job metadata not found")
            
            # Extract request from metadata (stored in custom field or reconstruct)
            # For now, reconstruct from metadata
            analysis_request = AnalysisRequest(
                company=job_metadata.company,
                industry=job_metadata.industry,
                frameworks=job_metadata.frameworks,
                depth="standard"  # Default
            )
            
            # Execute analysis
            logger.info(f"Processing job {job_id} for {analysis_request.company}")
            report = await self.orchestrator.execute(analysis_request)
            
            # Generate PDF
            pdf_bytes = generate_pdf_report(report)
            
            # Generate collision-safe report ID using UUID and microsecond precision
            # Sanitize company name for safe filename/DB characters
            sanitized_company = sanitize_input(analysis_request.company).replace(' ', '_')
            # Remove any characters that aren't alphanumeric, underscore, or hyphen
            sanitized_company = ''.join(c for c in sanitized_company if c.isalnum() or c in ('_', '-'))
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')  # Include microseconds
            unique_suffix = str(uuid.uuid4())[:8]  # Short UUID for uniqueness
            report_id = f"{sanitized_company}_{timestamp}_{unique_suffix}"
            
            # Upload PDF
            pdf_url = self.storage_service.upload_pdf(report_id, pdf_bytes)
            
            # Store report metadata
            report_metadata = ReportMetadata(
                report_id=report_id,
                user_id=job_metadata.user_id,
                company=analysis_request.company,
                industry=analysis_request.industry,
                frameworks=analysis_request.frameworks,
                status="completed",
                confidence_score=report.executive_summary.confidence_score,
                execution_time_seconds=0.0,  # Would track actual time
                pdf_url=pdf_url
            )
            self.db_service.create_report_metadata(report_metadata)
            
            # Update job status to completed
            await self.queue.update_status(job_id, JobStatus.COMPLETED, report_id=report_id)
            
            logger.info(f"Job {job_id} completed successfully, report_id: {report_id}")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            await self.queue.update_status(job_id, JobStatus.FAILED, error=str(e))
    
    async def start(self, poll_interval: int = 10):
        """
        Start worker loop
        
        Args:
            poll_interval: Seconds between polling for new jobs
        """
        self.running = True
        logger.info("Analysis worker started")
        
        while self.running:
            try:
                # Get pending jobs
                pending_jobs = await self.queue.list_jobs(status=JobStatus.PENDING, limit=10)
                
                if pending_jobs:
                    logger.info(f"Found {len(pending_jobs)} pending jobs")
                    # Process jobs concurrently (limit concurrency)
                    tasks = [self.process_job(job["job_id"]) for job in pending_jobs[:3]]  # Max 3 concurrent
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(poll_interval)
    
    def stop(self):
        """Stop worker"""
        self.running = False
        logger.info("Analysis worker stopped")


# Global worker instance
_worker: Optional[AnalysisWorker] = None
_worker_lock = threading.Lock()


def get_worker() -> AnalysisWorker:
    """Get or create worker instance (thread-safe singleton)"""
    global _worker
    if _worker is None:
        with _worker_lock:
            # Double-checked locking pattern
            if _worker is None:
                _worker = AnalysisWorker()
    return _worker


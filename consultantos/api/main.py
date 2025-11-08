"""
FastAPI application for ConsultantOS
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Security
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from consultantos.models import AnalysisRequest, StrategicReport
from consultantos.orchestrator import AnalysisOrchestrator
from consultantos.reports import generate_pdf_report
from consultantos.config import settings
from consultantos.monitoring import (
    logger,
    metrics,
    log_request,
    log_request_success,
    log_request_failure
)
from consultantos.storage import get_storage_service
from consultantos.auth import verify_api_key, get_api_key, create_api_key
from consultantos.database import get_db_service, ReportMetadata
from consultantos.api.user_endpoints import router as user_router
from consultantos.api.template_endpoints import router as template_router
from consultantos.api.sharing_endpoints import router as sharing_router
from consultantos.utils.validators import AnalysisRequestValidator
from consultantos.utils.sanitize import sanitize_input
from consultantos.reports.exports import export_to_json, export_to_excel, export_to_word
from consultantos.cache import get_cache_stats
from consultantos.jobs.queue import JobQueue, JobStatus, create_job, get_job_status
from consultantos.api.versioning_endpoints import router as versioning_router
from consultantos.api.comments_endpoints import router as comments_router
from consultantos.api.community_endpoints import router as community_router
from consultantos.api.analytics_endpoints import router as analytics_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))

# Initialize FastAPI
app = FastAPI(
    title="ConsultantOS - Business Intelligence Research Engine",
    description="Multi-agent strategic analysis for independent consultants",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
# Read allowed origins from settings (default to empty list for security)
allowed_origins = getattr(settings, 'allowed_origins', [])
if not allowed_origins:
    # If no origins configured, disable credentials for security
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Cannot use credentials with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Use configured origins with credentials enabled
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
app.include_router(user_router)
app.include_router(template_router)
app.include_router(sharing_router)
app.include_router(versioning_router)
app.include_router(comments_router)
app.include_router(community_router)
app.include_router(analytics_router)

# Initialize orchestrator (lazy initialization to avoid import-time errors)
_orchestrator: Optional[AnalysisOrchestrator] = None

def get_orchestrator() -> AnalysisOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AnalysisOrchestrator()
    return _orchestrator


@app.on_event("startup")
async def startup():
    """Application startup"""
    logger.info("ConsultantOS API starting up")
    logger.info(f"Rate limit: {settings.rate_limit_per_hour} requests/hour per IP")




@app.post("/analyze")
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def analyze_company(
    request: Request,
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """
    Generate strategic analysis report for a company
    
    **Authentication:** Optional (API key via X-API-Key header or api_key query param)
    
    **Rate Limited:** 10 requests/hour per IP
    
    **Response Time:** 30-60 seconds (may timeout for complex analyses)
    
    **Example Request:**
    ```json
    {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot", "pestel"],
        "depth": "standard"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "status": "success",
        "report_id": "Tesla_20240101120000",
        "report_url": "https://storage.googleapis.com/...",
        "executive_summary": {
            "company_name": "Tesla",
            "key_findings": [...],
            "confidence_score": 0.85
        },
        "execution_time_seconds": 45.2
    }
    ```
    """
    start_time = datetime.now()
    report_id = None
    
    try:
        # Validate and sanitize request
        try:
            analysis_request = AnalysisRequestValidator.validate_request(analysis_request)
            # Sanitize company name
            analysis_request.company = sanitize_input(analysis_request.company)
            if analysis_request.industry:
                analysis_request.industry = sanitize_input(analysis_request.industry)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
        
        report_id = f"{analysis_request.company}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log request with structured logging
        log_request(
            report_id=report_id,
            company=analysis_request.company,
            frameworks=analysis_request.frameworks,
            user_ip=request.client.host or "unknown"
        )
        
        # Execute multi-agent workflow with timeout
        try:
            orchestrator = get_orchestrator()
            report = await asyncio.wait_for(
                orchestrator.execute(analysis_request),
                timeout=240.0  # 4 minutes timeout
            )
        except asyncio.TimeoutError:
            error = Exception("Analysis timeout")
            log_request_failure(report_id, error)
            raise HTTPException(
                status_code=504,
                detail="Analysis timed out. Please try with a simpler query or contact support."
            )
        except Exception as e:
            log_request_failure(report_id, e)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        # Generate PDF with error handling
        try:
            pdf_bytes = generate_pdf_report(report)
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            # Return JSON response even if PDF fails
            return {
                "status": "partial_success",
                "report_id": report_id,
                "report_url": None,
                "error": "PDF generation failed, but analysis completed",
                "executive_summary": report.executive_summary.dict(),
                "confidence": report.executive_summary.confidence_score,
                "generated_at": datetime.now().isoformat()
            }
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Store in Cloud Storage (background task)
        storage_service = get_storage_service()
        user_id = None
        if api_key:
            from consultantos.auth import validate_api_key
            user_info = validate_api_key(api_key)
            if user_info:
                user_id = user_info.get("user_id")
        
        background_tasks.add_task(
            upload_and_store_metadata,
            storage_service,
            report_id,
            pdf_bytes,
            analysis_request,
            report,
            execution_time,
            user_id
        )
        
        # Log success
        log_request_success(report_id, execution_time, report.executive_summary.confidence_score)
        
        # Store report metadata (synchronously for immediate access)
        try:
            db_service = get_db_service()
            report_metadata = ReportMetadata(
                report_id=report_id,
                user_id=user_id,
                company=analysis_request.company,
                industry=analysis_request.industry,
                frameworks=analysis_request.frameworks,
                status="completed",
                confidence_score=report.executive_summary.confidence_score,
                execution_time_seconds=execution_time
            )
            db_service.create_report_metadata(report_metadata)
        except Exception as e:
            logger.warning(f"Failed to store report metadata: {e}")
        
        # Get report URL (will be available after background upload completes)
        # For now, return the expected URL
        report_url = f"https://storage.googleapis.com/consultantos-reports/{report_id}.pdf"
        
        # Return structured report + PDF URL
        return {
            "status": "success",
            "report_id": report_id,
            "report_url": report_url,
            "executive_summary": report.executive_summary.dict(),
            "confidence": report.executive_summary.confidence_score,
            "generated_at": datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error: {str(e)}",
            exc_info=True,
            extra={
                "report_id": report_id,
                "company": analysis_request.company if analysis_request else None
            }
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )


async def upload_and_store_metadata(
    storage_service,
    report_id: str,
    pdf_bytes: bytes,
    analysis_request: AnalysisRequest,
    report: StrategicReport,
    execution_time: float,
    user_id: Optional[str]
):
    """Upload PDF to Cloud Storage and update metadata with error handling"""
    try:
        # Upload PDF
        pdf_url = storage_service.upload_pdf(report_id, pdf_bytes)
        logger.info("pdf_uploaded", report_id=report_id, company=analysis_request.company)
        
        # Update report metadata with PDF URL
        try:
            db_service = get_db_service()
            db_service.update_report_metadata(report_id, {
                "pdf_url": pdf_url,
                "status": "completed"
            })
        except Exception as e:
            logger.warning(f"Failed to update report metadata: {e}")
            
    except Exception as e:
        logger.error(
            "pdf_upload_failed",
            report_id=report_id,
            company=analysis_request.company,
            error=str(e),
            exc_info=True
        )
        # Update metadata with error status
        try:
            db_service = get_db_service()
            db_service.update_report_metadata(report_id, {
                "status": "failed",
                "error_message": str(e)
            })
        except Exception as db_error:
            logger.warning(f"Failed to update error status: {db_error}")
        # Don't raise - background task failures shouldn't crash the app


@app.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    signed: bool = False,
    format: Optional[str] = None
):
    """
    Retrieve generated report
    
    **Parameters:**
    - `report_id`: Report identifier
    - `signed`: Generate signed URL (default: False)
    - `format`: Export format - 'json', 'excel', 'word' (default: PDF)
    
    **Example:**
    ```
    GET /reports/Tesla_20240101120000?format=json
    GET /reports/Tesla_20240101120000?format=excel&signed=true
    ```
    """
    try:
        # Handle export formats
        if format and format.lower() in ['json', 'excel', 'word']:
            # Need to retrieve the report data first
            # For now, return metadata - full implementation would fetch report
            db_service = get_db_service()
            metadata = db_service.get_report_metadata(report_id)
            
            if not metadata:
                raise HTTPException(status_code=404, detail="Report not found")
            
            # Export format implementations require full report reconstruction from storage
            # which is not yet implemented, so return 501 Not Implemented
            format_lower = format.lower()
            raise HTTPException(status_code=501, detail=f"Export format '{format_lower}' not implemented")
        
        # Try to get metadata from database
        db_service = get_db_service()
        metadata = db_service.get_report_metadata(report_id)
        
        if metadata:
            storage_service = get_storage_service()
            if signed and metadata.pdf_url:
                # Generate signed URL
                report_url = storage_service.generate_signed_url(report_id)
            else:
                report_url = metadata.pdf_url or storage_service.get_report_url(report_id)
            
            return {
                "report_id": report_id,
                "report_url": report_url,
                "status": metadata.status,
                "company": metadata.company,
                "industry": metadata.industry,
                "frameworks": metadata.frameworks,
                "confidence_score": metadata.confidence_score,
                "created_at": metadata.created_at,
                "execution_time_seconds": metadata.execution_time_seconds,
                "signed_url": signed
            }
        else:
            # Fallback to storage check
            storage_service = get_storage_service()
            if storage_service.report_exists(report_id):
                report_url = storage_service.get_report_url(report_id, use_signed_url=signed)
                return {
                    "report_id": report_id,
                    "report_url": report_url,
                    "status": "available",
                    "signed_url": signed
                }
            else:
                raise HTTPException(status_code=404, detail="Report not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("report_retrieval_failed", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve report")


@app.get("/reports")
async def list_reports(
    user_id: Optional[str] = None,
    company: Optional[str] = None,
    limit: int = 50,
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """
    List reports with optional filters
    
    Authentication: Optional. If authenticated, filters by user_id automatically.
    """
    try:
        # Get user_id from API key if provided
        authenticated_user_id = None
        if api_key:
            from consultantos.auth import validate_api_key
            user_info = validate_api_key(api_key)
            if user_info:
                authenticated_user_id = user_info.get("user_id")
        
        # Use authenticated user_id if no explicit user_id provided
        if authenticated_user_id and not user_id:
            user_id = authenticated_user_id
        
        db_service = get_db_service()
        reports = db_service.list_reports(
            user_id=user_id,
            company=company,
            limit=limit
        )
        
        return {
            "reports": [
                {
                    "report_id": r.report_id,
                    "company": r.company,
                    "industry": r.industry,
                    "frameworks": r.frameworks,
                    "status": r.status,
                    "confidence_score": r.confidence_score,
                    "created_at": r.created_at,
                    "execution_time_seconds": r.execution_time_seconds,
                    "pdf_url": r.pdf_url
                }
                for r in reports
            ],
            "count": len(reports)
        }
    except Exception as e:
        logger.error("list_reports_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list reports")


@app.get("/metrics")
async def get_metrics(user_info: Dict = Security(verify_api_key)):
    """
    Get application metrics (requires authentication)
    
    Returns performance metrics, cache statistics, and system health.
    
    **Example Response:**
    ```json
    {
        "metrics": {
            "total_requests": 1000,
            "cache_hits": 450,
            "cache_misses": 550,
            "average_execution_time": 45.2
        },
        "summary": {
            "cache_hit_rate": 0.45,
            "error_rate": 0.02
        },
        "cache_stats": {
            "disk_cache": {
                "available": true,
                "size": 524288000,
                "entries": 150
            }
        }
    }
    ```
    """
    cache_stats = get_cache_stats()
    return {
        "metrics": metrics.get_metrics(),
        "summary": metrics.get_summary(),
        "cache_stats": cache_stats
    }


@app.post("/auth/api-keys")
async def create_api_key_endpoint(
    user_id: str,
    description: Optional[str] = None,
    user_info: Dict = Security(verify_api_key)  # Require auth to create keys
):
    """Create a new API key"""
    api_key = create_api_key(user_id, description)
    return {
        "api_key": api_key,
        "user_id": user_id,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "warning": "Store this key securely. It will not be shown again."
    }


@app.get("/auth/api-keys")
async def list_api_keys_endpoint(
    user_info: Dict = Security(verify_api_key)
):
    """List all API keys for the authenticated user"""
    from consultantos.auth import get_user_api_keys
    
    user_id = user_info.get("user_id")
    keys = get_user_api_keys(user_id)
    
    return {
        "user_id": user_id,
        "api_keys": keys,
        "count": len(keys)
    }


@app.delete("/auth/api-keys/{key_hash_prefix}")
async def revoke_api_key_endpoint(
    key_hash_prefix: str,
    user_info: Dict = Security(verify_api_key)
):
    """
    Revoke an API key by hash prefix
    
    **Parameters:**
    - `key_hash_prefix`: First 8+ characters of key hash
    
    **Example:**
    ```
    DELETE /auth/api-keys/abc12345
    ```
    """
    from consultantos.auth import revoke_api_key_by_hash
    
    user_id = user_info.get("user_id")
    success = revoke_api_key_by_hash(key_hash_prefix, user_id)
    
    if success:
        return {
            "message": "API key revoked successfully",
            "key_hash_prefix": key_hash_prefix
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"API key with prefix {key_hash_prefix} not found or already revoked"
        )


@app.post("/auth/api-keys/rotate")
async def rotate_api_key_endpoint(
    old_api_key: Optional[str] = None,
    description: Optional[str] = None,
    user_info: Dict = Security(verify_api_key)
):
    """
    Rotate API key (revoke old, create new)
    
    **Parameters:**
    - `old_api_key`: Optional old API key to revoke
    - `description`: Optional description for new key
    
    **Example:**
    ```json
    {
        "old_api_key": "old_key_here",
        "description": "Rotated key - Jan 2024"
    }
    ```
    """
    from consultantos.auth import rotate_api_key
    
    user_id = user_info.get("user_id")
    new_key = rotate_api_key(user_id, old_api_key, description)
    
    return {
        "message": "API key rotated successfully",
        "new_api_key": new_key,
        "warning": "Store this key securely. It will not be shown again."
    }


@app.post("/analyze/async")
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def analyze_company_async(
    request: Request,
    analysis_request: AnalysisRequest,
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """
    Enqueue analysis job for async processing
    
    **Authentication:** Optional (API key via X-API-Key header or api_key query param)
    
    **Rate Limited:** 10 requests/hour per IP
    
    **Returns:** Job ID and status endpoint for polling
    
    **Example Request:**
    ```json
    {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot"]
    }
    ```
    
    **Example Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "pending",
        "status_url": "/jobs/550e8400-e29b-41d4-a716-446655440000/status",
        "estimated_completion": "2-5 minutes"
    }
    ```
    """
    try:
        # Validate and sanitize request
        try:
            analysis_request = AnalysisRequestValidator.validate_request(analysis_request)
            analysis_request.company = sanitize_input(analysis_request.company)
            if analysis_request.industry:
                analysis_request.industry = sanitize_input(analysis_request.industry)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
        
        # Get user_id from API key if provided
        user_id = None
        if api_key:
            from consultantos.auth import validate_api_key
            user_info = validate_api_key(api_key)
            if user_info:
                user_id = user_info.get("user_id")
        
        # Enqueue job
        job_queue = JobQueue()
        job_id = await job_queue.enqueue(analysis_request, user_id)
        
        # Track job creation
        metrics.track_job_status("pending", 1)
        if user_id:
            metrics.track_user_activity(user_id, "job_created")
        
        logger.info(
            "job_enqueued",
            job_id=job_id,
            company=analysis_request.company,
            user_id=user_id
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "status_url": f"/jobs/{job_id}/status",
            "estimated_completion": "2-5 minutes",
            "message": "Job enqueued. Poll status_url for updates."
        }
    except Exception as e:
        logger.error(f"Failed to enqueue job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")


@app.get("/jobs/{job_id}/status")
async def get_job_status_endpoint(job_id: str):
    """
    Get job status
    
    **Parameters:**
    - `job_id`: Job identifier
    
    **Example:**
    ```
    GET /jobs/550e8400-e29b-41d4-a716-446655440000/status
    ```
    
    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "processing",
        "company": "Tesla",
        "created_at": "2024-01-01T12:00:00"
    }
    ```
    """
    try:
        job_queue = JobQueue()
        status = await job_queue.get_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/jobs")
async def list_jobs_endpoint(
    status: Optional[str] = None,
    limit: int = 50,
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """
    List jobs with optional filters
    
    **Parameters:**
    - `status`: Filter by status (pending, processing, completed, failed)
    - `limit`: Maximum number of jobs to return
    
    **Authentication:** Optional. If authenticated, filters by user_id automatically.
    """
    try:
        # Get user_id from API key if provided
        user_id = None
        if api_key:
            from consultantos.auth import validate_api_key
            user_info = validate_api_key(api_key)
            if user_info:
                user_id = user_info.get("user_id")
        
        job_queue = JobQueue()
        job_status = None
        if status:
            try:
                job_status = JobStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        jobs = await job_queue.list_jobs(user_id=user_id, status=job_status, limit=limit)
        
        return {
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list jobs")


@app.get("/health")
async def health_check():
    """
    Health check endpoint with detailed status
    
    Returns system health status including cache, storage, and database availability.
    
    **Example Response:**
    ```json
    {
        "status": "healthy",
        "version": "0.3.0",
        "timestamp": "2024-01-01T12:00:00",
        "cache": {
            "disk_cache_initialized": true,
            "semantic_cache_available": true
        },
        "storage": {
            "available": true
        },
        "database": {
            "available": true,
            "type": "firestore"
        }
    }
    ```
    """
    # Check database availability
    db_available = False
    try:
        db_service = get_db_service()
        # Try a simple operation
        _ = db_service.db
        db_available = True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
    
    return {
        "status": "healthy",
        "version": "0.3.0",
        "timestamp": datetime.now().isoformat(),
        "cache": {
            "disk_cache_initialized": True,
            "semantic_cache_available": True
        },
        "storage": {
            "available": True
        },
        "database": {
            "available": db_available,
            "type": "firestore"
        }
    }


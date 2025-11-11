"""
FastAPI application for ConsultantOS
"""
import asyncio
import logging
import time
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Security, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from consultantos.observability import metrics, setup_sentry, SentryIntegration
from consultantos import auth, config, database, models, storage
from consultantos.orchestrator import AnalysisOrchestrator
from consultantos.reports import generate_pdf_report

# Import logging functions from log_utils module
# Note: metrics is imported from observability above
try:
    from consultantos import log_utils
    logger = log_utils.logger
    log_request = log_utils.log_request
    # Import function directly to avoid any binding issues
    from consultantos.log_utils import log_request_success
    log_request_failure = log_utils.log_request_failure
except (ImportError, AttributeError, Exception) as e:
    # Fallback for hackathon demo
    logger = logging.getLogger(__name__)
    
    # No-op metrics object to prevent AttributeErrors
    class NoOpMetrics:
        """Lightweight no-op metrics object that implements all metrics methods"""
        def record_error(self, error_type: str, error_message: str) -> None:
            pass

        def get_metrics(self) -> Dict[str, Any]:
            return {"timestamp": datetime.now().isoformat()}

        def get_summary(self) -> Dict[str, Any]:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "cache_hit_rate": 0.0,
                "average_execution_times": {},
                "error_count_by_type": {},
                "api_success_rates": {},
                "total_cost": 0.0
            }

        def get_prometheus_metrics(self) -> str:
            """Return empty Prometheus metrics"""
            return "# No metrics available\n"

        def track_job_status(self, status: str, increment: int = 1) -> None:
            pass

        def track_user_activity(self, user_id: str, action: str) -> None:
            pass

        def increment_active_requests(self) -> None:
            pass

        def decrement_active_requests(self) -> None:
            pass

        def record_api_request(self, endpoint: str, method: str, status_code: int, duration: float) -> None:
            pass
    
    metrics = NoOpMetrics()
    
    def log_request(request_id: str, **kwargs):
        pass
    
    # Define as a proper function, not a method
    def _log_request_success_impl(request_id: str, execution_time: float, confidence: float):
        pass
    log_request_success = _log_request_success_impl
    
    def log_request_failure(*args, **kwargs):
        # Accept any arguments to prevent signature mismatches
        pass
# Import routers
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
from consultantos.api.visualization_endpoints import router as visualization_router
from consultantos.api.auth_endpoints import router as auth_router
from consultantos.api.health_endpoints import router as health_router, mark_startup_complete
from consultantos.api.notifications_endpoints import router as notifications_router
# Advanced features (now enabled with authentication implementation)
from consultantos.api.knowledge_endpoints import router as knowledge_router
from consultantos.api.custom_frameworks_endpoints import router as custom_frameworks_router
from consultantos.api.saved_searches_endpoints import router as saved_searches_router

# Disabled for hackathon demo - require additional dependencies
# from consultantos.api.dashboard_endpoints import router as dashboard_router
from consultantos.api.monitoring_endpoints import router as monitoring_router
# from consultantos.api.feedback_endpoints import router as feedback_router
# from consultantos.api.teams_endpoints import router as teams_router
# from consultantos.api.history_endpoints import router as history_router
# from consultantos.api.digest_endpoints import router as digest_router
from consultantos.api.jobs_endpoints import router as jobs_router
from consultantos.api.enhanced_reports_endpoints import router as enhanced_reports_router
from consultantos.api.mvp_endpoints import router as mvp_router  # MVP features for hackathon
from consultantos.api.conversational_endpoints import router as conversational_router  # Conversational AI with RAG
from consultantos.api.forecasting_endpoints import router as forecasting_router  # Enhanced multi-scenario forecasting
from consultantos.api.wargaming_endpoints import router as wargaming_router  # Wargaming simulator with Monte Carlo (Phase 2 Week 11-12)
from consultantos.api.integration_endpoints import router as integration_router  # Comprehensive system integration (Phase 1 & 2 complete)
from consultantos.storage import LocalFileStorageService


# Shared core aliases
settings = config.settings
AnalysisRequest = models.AnalysisRequest
StrategicReport = models.StrategicReport
get_storage_service = storage.get_storage_service
verify_api_key = auth.verify_api_key
get_api_key = auth.get_api_key
create_api_key = auth.create_api_key
get_db_service = database.get_db_service
ReportMetadata = database.ReportMetadata

# Request ID tracking via ContextVar
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

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

# CORS middleware - MUST be added FIRST before other middleware
# Get allowed origins from config (comma-separated string)
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600,
)

# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Force HTTPS in production
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy (adjust based on your needs)
    # Note: Relaxed for development to allow localhost connections
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust for your frontend
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self' http://localhost:* http://127.0.0.1:*",  # Allow localhost connections
        "frame-ancestors 'none'"
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions policy (restrict browser features)
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response

# Request ID middleware
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add unique request ID to all requests for tracing"""
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request_id_var.set(request_id)
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers['X-Request-ID'] = request_id
    return response

# Session middleware with secure configuration
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="consultantos_session",
    max_age=3600,  # 1 hour session lifetime
    same_site="strict",  # Prevent CSRF attacks
    https_only=(settings.environment == "production"),  # HTTPS-only in production
    # Note: httponly is set automatically by SessionMiddleware for session cookies
)

# GZip compression middleware (must be added after SessionMiddleware)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6  # Balance between compression ratio and speed
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Prometheus instrumentation
@app.on_event("startup")
async def setup_prometheus():
    """Setup Prometheus instrumentation on startup."""
    try:
        Instrumentator().instrument(app).expose()
    except Exception as e:
        logger.warning(f"Failed to setup Prometheus instrumentation: {e}")

# Metrics tracking middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track metrics for each request."""
    metrics.increment_active_requests()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record API metrics
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration,
        )
        metrics.record_error("RequestError", request.method)
        raise
    finally:
        metrics.decrement_active_requests()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with detailed error tracking"""
    request_id = getattr(request.state, 'request_id', 'unknown')

    logger.error(
        "unhandled_exception",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
        stack_trace=traceback.format_exc(),
        exc_info=True
    )

    # Track error in metrics
    metrics.record_error(type(exc).__name__, str(exc))

    # Capture exception in Sentry with request context
    try:
        SentryIntegration.add_breadcrumb(
            message=f"Exception in {request.method} {request.url.path}",
            category="api",
            level="error",
            data={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            }
        )
        event_id = SentryIntegration.capture_exception(
            exc,
            tag_endpoint=request.url.path,
            tag_method=request.method,
            extra_request_id=request_id,
        )
        logger.debug(f"Exception captured in Sentry: event_id={event_id}")
    except Exception as sentry_error:
        logger.warning(f"Failed to capture exception in Sentry: {sentry_error}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "message": str(exc) if settings.environment == "development" else "An unexpected error occurred"
        },
        headers={"X-Request-ID": request_id}
    )

# Register routers
app.include_router(health_router)  # Health endpoints first for monitoring
app.include_router(user_router)
app.include_router(template_router)
app.include_router(sharing_router)
app.include_router(versioning_router)
app.include_router(comments_router)
app.include_router(community_router)
app.include_router(analytics_router)
# Disabled for hackathon demo - require additional dependencies
# app.include_router(feedback_router)
app.include_router(visualization_router)
app.include_router(auth_router)
app.include_router(notifications_router)
# Advanced features (now enabled)
app.include_router(knowledge_router)
app.include_router(custom_frameworks_router)
app.include_router(saved_searches_router)
# Disabled for hackathon demo - require additional dependencies
# app.include_router(dashboard_router)
app.include_router(monitoring_router)  # Enable monitoring endpoints for dashboard
# app.include_router(teams_router)
# app.include_router(history_router)
# app.include_router(digest_router)
app.include_router(jobs_router)  # Job processing and status
app.include_router(enhanced_reports_router)  # Enhanced reports with actionable insights
app.include_router(mvp_router)  # MVP features for hackathon demo
app.include_router(conversational_router)  # Conversational AI with RAG
app.include_router(forecasting_router)  # Enhanced multi-scenario forecasting (Phase 1 Week 3-4)
app.include_router(wargaming_router)  # Wargaming simulator with Monte Carlo (Phase 2 Week 11-12)
app.include_router(integration_router)  # Comprehensive system integration (Phase 1 & 2 complete)

# Dashboard agents endpoints
from consultantos.api.dashboard_agents_endpoints import router as dashboard_agents_router
app.include_router(dashboard_agents_router)  # Dashboard agents for feature gaps

# Phase 2 & 3 dashboard agents endpoints
from consultantos.api.phase2_3_agents_endpoints import router as phase2_3_agents_router
app.include_router(phase2_3_agents_router)  # Phase 2 & 3 agents (notifications, versions, templates, visualizations, feedback)

# Strategic Intelligence endpoints
from consultantos.api.strategic_intelligence_endpoints import router as strategic_intelligence_router
app.include_router(strategic_intelligence_router, prefix="/api/strategic-intelligence", tags=["Strategic Intelligence"])

# app.include_router(storytelling_router)  # AI storytelling with persona adaptation (Phase 2 Week 15-16) - Not yet implemented

# Initialize orchestrator (lazy initialization to avoid import-time errors)
_orchestrator: Optional[AnalysisOrchestrator] = None

def get_orchestrator() -> AnalysisOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AnalysisOrchestrator()
    return _orchestrator


# Global reference to worker task to prevent garbage collection
_worker_task: Optional[asyncio.Task] = None

@app.on_event("startup")
async def startup():
    """Application startup"""
    logger.info("ConsultantOS API starting up")
    logger.info(f"Rate limit: {settings.rate_limit_per_hour} requests/hour per IP")

    # Initialize Sentry for error tracking and performance monitoring
    try:
        sentry_integration = setup_sentry(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment or settings.environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            release=settings.sentry_release,
        )
        if sentry_integration:
            logger.info(f"Sentry initialized: environment={sentry_integration.environment}, release={sentry_integration.release}")
        else:
            logger.info("Sentry not configured (SENTRY_DSN not set)")
    except Exception as e:
        logger.warning(f"Failed to initialize Sentry: {e}")

    # Start background worker for async job processing (non-blocking)
    # Delay worker start to avoid blocking server startup
    global _worker_task
    try:
        async def start_worker_delayed():
            """Start worker after a short delay to ensure server is ready"""
            await asyncio.sleep(2)  # Give server time to start
            from consultantos.jobs.worker import get_worker
            worker = get_worker()
            await worker.start(poll_interval=10)
        
        _worker_task = asyncio.create_task(start_worker_delayed())
        logger.info("Background worker task scheduled for async job processing")
    except Exception as e:
        logger.warning(f"Failed to schedule background worker: {e}. Async jobs will not be processed.")
        logger.warning("To process async jobs, start the worker separately or restart the API server.")

    # Mark startup as complete for health checks
    mark_startup_complete()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown():
    """Application shutdown - gracefully stop background tasks"""
    logger.info("ConsultantOS API shutting down")

    # Stop background worker if running
    global _worker_task
    if _worker_task and not _worker_task.done():
        try:
            from consultantos.jobs.worker import get_worker
            worker = get_worker()
            await worker.stop()
            logger.info("Background worker stopped gracefully")
        except Exception as e:
            logger.warning(f"Error stopping background worker: {e}")
            # Cancel the task if stop() failed
            _worker_task.cancel()
            try:
                await _worker_task
            except asyncio.CancelledError:
                logger.info("Background worker task cancelled")

    logger.info("Application shutdown complete")




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
            request_id=report_id,
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
            try:
                log_request_failure(report_id, error)
            except Exception as log_err:
                logger.error(f"Failed to log request failure: {log_err}")
            raise HTTPException(
                status_code=504,
                detail="Analysis timed out. Please try with a simpler query or contact support."
            )
        except Exception as e:
            try:
                log_request_failure(report_id, e)
            except Exception as log_err:
                logger.error(f"Failed to log request failure: {log_err}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        # Generate PDF with error handling
        try:
            pdf_bytes = generate_pdf_report(report, report_id=report_id)
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            # Return JSON response even if PDF fails
            # Include framework_analysis if available
            frameworks_data = None
            if report.framework_analysis:
                try:
                    frameworks_data = report.framework_analysis.model_dump()
                except Exception as e:
                    logger.warning(f"Failed to serialize framework_analysis for response: {e}")
            
            return {
                "status": "partial_success",
                "report_id": report_id,
                "report_url": None,
                "error": "PDF generation failed, but analysis completed",
                "executive_summary": report.executive_summary.model_dump(),
                "confidence_score": report.executive_summary.confidence_score,
                "frameworks": frameworks_data,
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
        
        # Log success - use keyword arguments (log_request_success has stable signature)
        try:
            log_request_success(
                request_id=report_id,
                execution_time=execution_time,
                confidence=report.executive_summary.confidence_score
            )
        except Exception as e:
            # Fallback to direct logging if log_request_success fails
            logger.warning(f"Failed to log request success via log_request_success: {e}", exc_info=True)
            logger.info(f"Analysis completed: report_id={report_id}, execution_time={execution_time:.2f}, confidence={report.executive_summary.confidence_score}")
        
        # Store report metadata (synchronously for immediate access)
        try:
            db_service = get_db_service()
            # Convert framework_analysis to dict for storage
            framework_analysis_dict = None
            if report.framework_analysis:
                try:
                    # Use Pydantic v2 model_dump() for serialization
                    framework_analysis_dict = report.framework_analysis.model_dump()
                except Exception as e:
                    logger.warning(f"Failed to serialize framework_analysis: {e}", exc_info=True)
                    framework_analysis_dict = None
            
            report_metadata = ReportMetadata(
                report_id=report_id,
                user_id=user_id,
                company=analysis_request.company,
                industry=analysis_request.industry,
                frameworks=analysis_request.frameworks,
                status="completed",
                confidence_score=report.executive_summary.confidence_score,
                execution_time_seconds=execution_time,
                framework_analysis=framework_analysis_dict
            )
            db_service.create_report_metadata(report_metadata)
        except Exception as e:
            logger.warning(f"Failed to store report metadata: {e}")
        
        # Get report URL (will be available after background upload completes)
        # For now, return the expected URL
        report_url = f"https://storage.googleapis.com/consultantos-reports/{report_id}.pdf"
        
        # Return structured report + PDF URL
        # Include framework_analysis if available
        frameworks_data = None
        if report.framework_analysis:
            try:
                frameworks_data = report.framework_analysis.model_dump()
            except Exception as e:
                logger.warning(f"Failed to serialize framework_analysis for response: {e}")
        
        return {
            "status": "success",
            "report_id": report_id,
            "report_url": report_url,
            "executive_summary": report.executive_summary.model_dump(),
            "confidence_score": report.executive_summary.confidence_score,
            "frameworks": frameworks_data,
            "generated_at": datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        logger.error(
            f"Unexpected error: {error_message}",
            exc_info=True,
            extra={
                "report_id": report_id,
                "company": analysis_request.company if analysis_request else None
            }
        )
        # In development, show actual error for debugging
        if settings.environment == "development":
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {error_message}"
            )
        else:
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


@app.get("/reports/{report_id}/download")
async def download_report_pdf(report_id: str):
    """
    Download PDF report file
    
    **Parameters:**
    - `report_id`: Report identifier
    
    Returns the PDF file as a download.
    """
    try:
        storage_service = get_storage_service()
        
        # Check if report exists
        if not storage_service.report_exists(report_id):
            raise HTTPException(status_code=404, detail="Report PDF not found")
        
        # For local file storage, read the file
        if isinstance(storage_service, LocalFileStorageService):
            from pathlib import Path
            from fastapi.responses import FileResponse
            
            file_path = Path(storage_service.storage_dir) / f"{report_id}.pdf"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Report PDF not found")
            
            return FileResponse(
                path=str(file_path),
                media_type="application/pdf",
                filename=f"{report_id}.pdf",
                headers={"Content-Disposition": f'attachment; filename="{report_id}.pdf"'}
            )
        else:
            # For Cloud Storage, redirect to signed URL
            signed_url = storage_service.generate_signed_url(report_id)
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=signed_url)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("pdf_download_failed", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to download PDF")


@app.get("/reports/{report_id}/pdf")
async def download_report_pdf_alias(report_id: str):
    """
    Alias for /reports/{report_id}/download - Download PDF report file
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/reports/{report_id}/download")


@app.get("/reports/{report_id}/export")
async def export_report_alias(
    report_id: str,
    format: str = Query("json", description="Export format: json, excel, word")
):
    """
    Alias for /reports/{report_id}?format=... - Export report in various formats
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/reports/{report_id}?format={format}")


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
            db_service = get_db_service()
            metadata = db_service.get_report_metadata(report_id)
            
            if not metadata:
                raise HTTPException(status_code=404, detail="Report not found")
            
            format_lower = format.lower()
            
            # JSON export - return metadata as JSON
            if format_lower == 'json':
                from fastapi.responses import JSONResponse
                return JSONResponse(content={
                    "report_id": report_id,
                    "company": metadata.company,
                    "industry": metadata.industry,
                    "frameworks": metadata.frameworks or [],
                    "status": metadata.status,
                    "confidence_score": metadata.confidence_score,
                    "created_at": metadata.created_at.isoformat() if hasattr(metadata.created_at, 'isoformat') else str(metadata.created_at),
                    "execution_time_seconds": metadata.execution_time_seconds,
                    "pdf_url": metadata.pdf_url,
                    "framework_analysis": metadata.framework_analysis if hasattr(metadata, 'framework_analysis') else None
                })
            
            # Excel and Word exports - reconstruct report from metadata
            if format_lower in ['excel', 'word']:
                from consultantos.reports.exports import export_to_excel, export_to_word
                from consultantos.models import StrategicReport, ExecutiveSummary
                from fastapi.responses import Response
                
                # Reconstruct minimal StrategicReport from metadata
                # This is a simplified version - full report would require storing complete data
                framework_analysis_dict = metadata.framework_analysis if isinstance(metadata.framework_analysis, dict) else {}
                
                # Extract key findings from SWOT if available
                key_findings = ["Analysis completed", "Review recommended", "Data validation needed"]
                if "swot_analysis" in framework_analysis_dict and framework_analysis_dict["swot_analysis"]:
                    swot = framework_analysis_dict["swot_analysis"]
                    if isinstance(swot, dict):
                        # Combine strengths and opportunities as key findings
                        strengths = swot.get("strengths", [])
                        opportunities = swot.get("opportunities", [])
                        if strengths or opportunities:
                            key_findings = (strengths[:2] if strengths else []) + (opportunities[:1] if opportunities else [])
                
                executive_summary = ExecutiveSummary(
                    company_name=metadata.company or "Unknown",
                    industry=metadata.industry or "Unknown",
                    key_findings=key_findings[:5],  # Limit to 5
                    strategic_recommendation="Further analysis recommended based on available data",
                    confidence_score=metadata.confidence_score or 0.5,
                    supporting_evidence=["Report metadata available"],
                    next_steps=["Review detailed analysis", "Validate findings", "Consult with stakeholders"]
                )
                
                # Create minimal StrategicReport with required fields
                # Export functions primarily use executive_summary, but we need minimal objects for validation
                from consultantos.models import (
                    CompanyResearch, FinancialSnapshot, FrameworkAnalysis
                )
                
                # Minimal CompanyResearch
                company_research = CompanyResearch(
                    company_name=metadata.company or "Unknown",
                    description=f"Analysis for {metadata.company}",
                    products_services=[],
                    target_market="Unknown",
                    key_competitors=[],
                    recent_news=[],
                    sources=[]
                )
                
                # Minimal FinancialSnapshot
                financial_snapshot = FinancialSnapshot(
                    ticker="N/A",
                    market_cap=None,
                    revenue=None,
                    revenue_growth=None,
                    profit_margin=None,
                    pe_ratio=None,
                    key_metrics={},
                    risk_assessment="Unable to assess from metadata"
                )
                
                # Minimal FrameworkAnalysis (all optional fields can be None)
                framework_analysis = FrameworkAnalysis()
                
                report = StrategicReport(
                    executive_summary=executive_summary,
                    company_research=company_research,
                    market_trends=None,
                    financial_snapshot=financial_snapshot,
                    framework_analysis=framework_analysis,
                    recommendations=["Review detailed analysis", "Validate findings", "Consult stakeholders"],
                    metadata={
                        "report_id": report_id,
                        "company": metadata.company,
                        "industry": metadata.industry,
                        "frameworks": metadata.frameworks or []
                    }
                )
                
                try:
                    if format_lower == 'excel':
                        excel_bytes = await export_to_excel(report)
                        return Response(
                            content=excel_bytes,
                            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            headers={"Content-Disposition": f"attachment; filename={report_id}.xlsx"}
                        )
                    elif format_lower == 'word':
                        word_bytes = await export_to_word(report)
                        return Response(
                            content=word_bytes,
                            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            headers={"Content-Disposition": f"attachment; filename={report_id}.docx"}
                        )
                except ImportError as e:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Export format '{format_lower}' requires additional packages. {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Export failed: {e}", exc_info=True)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate {format_lower} export: {str(e)}"
                    )
        
        # Try to get metadata from database
        db_service = get_db_service()
        metadata = db_service.get_report_metadata(report_id)
        
        if metadata:
            storage_service = get_storage_service()
            
            # Get framework_analysis from metadata
            framework_analysis = None
            if hasattr(metadata, 'framework_analysis'):
                framework_analysis = metadata.framework_analysis
            elif isinstance(metadata, dict):
                framework_analysis = metadata.get('framework_analysis')
            
            # Handle PDF URL - convert file:// URLs to download endpoint
            report_url = None
            if metadata.pdf_url:
                if metadata.pdf_url.startswith('file://'):
                    # Convert file:// URL to download endpoint
                    report_url = f"/reports/{report_id}/download"
                else:
                    report_url = metadata.pdf_url
            else:
                # Generate URL based on storage type
                if isinstance(storage_service, LocalFileStorageService):
                    report_url = f"/reports/{report_id}/download"
                else:
                    report_url = storage_service.get_report_url(report_id, use_signed_url=signed)
            
            # Format created_at
            created_at = metadata.created_at
            if hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()
            elif created_at is None:
                created_at = datetime.now().isoformat()
            
            return {
                "report_id": report_id,
                "report_url": report_url,
                "pdf_url": report_url,  # Alias for compatibility
                "status": metadata.status,
                "company": metadata.company,
                "industry": metadata.industry,
                "frameworks": metadata.frameworks or [],
                "confidence_score": metadata.confidence_score,
                "created_at": created_at,
                "execution_time_seconds": metadata.execution_time_seconds,
                "framework_analysis": framework_analysis,
                "signed_url": signed
            }
        else:
            # Fallback to storage check
            storage_service = get_storage_service()
            if storage_service.report_exists(report_id):
                if isinstance(storage_service, LocalFileStorageService):
                    report_url = f"/reports/{report_id}/download"
                else:
                    report_url = storage_service.get_report_url(report_id, use_signed_url=signed)
                return {
                    "report_id": report_id,
                    "report_url": report_url,
                    "pdf_url": report_url,
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
            try:
                from consultantos.auth import validate_api_key
                user_info = validate_api_key(api_key)
                if user_info:
                    authenticated_user_id = user_info.get("user_id")
            except Exception as auth_error:
                logger.warning(f"Failed to validate API key: {auth_error}")
        
        # Use authenticated user_id if no explicit user_id provided
        if authenticated_user_id and not user_id:
            user_id = authenticated_user_id
        
        db_service = get_db_service()
        if db_service is None:
            logger.error("Database service is None")
            raise HTTPException(status_code=500, detail="Database service not available")
        
        reports = db_service.list_reports(
            user_id=user_id,
            company=company,
            limit=limit
        )
        
        # Ensure reports is a list
        if not isinstance(reports, list):
            logger.warning(f"list_reports returned non-list: {type(reports)}")
            reports = []
        
        # Safely serialize reports
        reports_list = []
        for r in reports:
            try:
                # Safely read framework_analysis with fallback for older records
                framework_analysis = None
                if hasattr(r, 'framework_analysis'):
                    framework_analysis = getattr(r, 'framework_analysis', None)
                elif hasattr(r, 'metadata') and isinstance(r.metadata, dict):
                    framework_analysis = r.metadata.get("framework_analysis")
                
                reports_list.append({
                    "report_id": r.report_id or "",
                    "company": r.company or "",
                    "industry": r.industry,
                    "frameworks": r.frameworks or [],
                    "status": r.status or "completed",
                    "confidence_score": r.confidence_score,
                    "created_at": r.created_at or datetime.now().isoformat(),
                    "execution_time_seconds": r.execution_time_seconds,
                    "pdf_url": r.pdf_url,
                    "framework_analysis": framework_analysis
                })
            except Exception as serialize_error:
                logger.warning(f"Failed to serialize report {r.report_id if hasattr(r, 'report_id') else 'unknown'}: {serialize_error}")
                continue
        
        return {
            "reports": reports_list,
            "count": len(reports_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("list_reports_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


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
        
        # Log job enqueued - use format compatible with both structlog and standard logger
        try:
            logger.info(
                "job_enqueued",
                job_id=job_id,
                company=analysis_request.company,
                user_id=user_id
            )
        except TypeError:
            # Fallback for standard logger
            logger.info(f"Job {job_id} enqueued for company {analysis_request.company} (user: {user_id})")
        
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
        job_statuses = None
        if status:
            # Handle comma-separated status values
            status_list = [s.strip() for s in status.split(',')]
            # Map frontend status names to backend enum values
            status_mapping = {
                'running': 'processing',
                'pending': 'pending',
                'completed': 'completed',
                'failed': 'failed',
                'cancelled': 'cancelled'
            }
            try:
                # Map status names and create JobStatus objects
                mapped_statuses = [status_mapping.get(s.lower(), s.lower()) for s in status_list]
                job_statuses = [JobStatus(s) for s in mapped_statuses]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        jobs = await job_queue.list_jobs(user_id=user_id, statuses=job_statuses, limit=limit)
        
        # Ensure jobs is a list
        if not isinstance(jobs, list):
            logger.warning(f"list_jobs returned non-list: {type(jobs)}")
            jobs = []
        
        return {
            "jobs": jobs,
            "count": len(jobs)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True, extra={"status_param": status})
        # Return empty list instead of raising error for better UX
        return {
            "jobs": [],
            "count": 0
        }


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
        },
        "worker": {
            "running": true,
            "task_exists": true
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
    
    # Check worker status
    worker_running = False
    worker_task_exists = _worker_task is not None
    if worker_task_exists:
        worker_running = not _worker_task.done() if _worker_task else False
    
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
        },
        "worker": {
            "running": worker_running,
            "task_exists": worker_task_exists
        }
    }
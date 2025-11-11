"""
API endpoints for dashboard agents
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from consultantos.agents import (
    DashboardAnalyticsAgent,
    DashboardDataAgent,
    ReportManagementAgent,
    JobManagementAgent,
)
from consultantos.auth import get_optional_user_id, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard-agents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/overview")
async def get_dashboard_overview(
    user_id: Optional[str] = Depends(get_optional_user_id),
    alert_limit: int = Query(10, ge=1, le=100),
    report_limit: int = Query(5, ge=1, le=50)
):
    """
    Get consolidated dashboard overview data.
    
    Aggregates monitors, stats, alerts, jobs, and reports in a single call
    to reduce waterfall requests and improve performance.
    
    Args:
        user_id: Authenticated user ID
        alert_limit: Maximum number of alerts to return
        report_limit: Maximum number of reports to return
    
    Returns:
        DashboardOverview with all consolidated data
    """
    try:
        agent = DashboardDataAgent()
        result = await agent.execute({
            "user_id": user_id,
            "alert_limit": alert_limit,
            "report_limit": report_limit
        })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to load dashboard overview")
            )
        
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard overview: {str(e)}")


@router.get("/analytics")
async def get_dashboard_analytics(
    user_id: Optional[str] = Depends(get_optional_user_id),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get comprehensive dashboard analytics.
    
    Provides productivity metrics, business metrics, and dashboard analytics
    including report status pipeline, confidence distribution, and framework effectiveness.
    
    Args:
        user_id: Authenticated user ID
        days: Number of days to analyze
    
    Returns:
        DashboardAnalyticsResult with productivity, business, and dashboard metrics
    """
    try:
        agent = DashboardAnalyticsAgent()
        result = await agent.execute({
            "user_id": user_id,
            "days": days
        })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate analytics")
            )
        
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")


@router.get("/reports")
async def list_reports(
    user_id: Optional[str] = Depends(get_optional_user_id),
    action: str = Query("list", regex="^(list|filter|search)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    company: Optional[str] = None,
    industry: Optional[str] = None,
    frameworks: Optional[List[str]] = Query(None),
    status: Optional[str] = None,
    search_query: Optional[str] = None
):
    """
    List, filter, or search reports.
    
    Supports full report management with filtering, searching, and pagination.
    
    Args:
        user_id: Authenticated user ID
        action: Action to perform (list, filter, search)
        page: Page number
        page_size: Number of items per page
        company: Filter by company name
        industry: Filter by industry
        frameworks: Filter by frameworks (list)
        status: Filter by status
        search_query: Search query for keyword search
    
    Returns:
        ReportListResult with reports and metadata
    """
    try:
        agent = ReportManagementAgent()
        
        input_data = {
            "action": action,
            "user_id": user_id,
            "page": page,
            "page_size": page_size
        }
        
        if action == "filter":
            input_data["filters"] = {
                "company": company,
                "industry": industry,
                "frameworks": frameworks,
                "status": status
            }
        elif action == "search":
            if not search_query:
                raise HTTPException(status_code=400, detail="search_query required for search action")
            input_data["search_query"] = search_query
        
        result = await agent.execute(input_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to process report request")
            )
        
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report management error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process report request: {str(e)}")


@router.get("/jobs")
async def list_jobs(
    user_id: Optional[str] = Depends(get_optional_user_id),
    action: str = Query("list", regex="^(list|status|history)$"),
    status: Optional[str] = None,
    job_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """
    List jobs, get job status, or view job history.
    
    Supports job queue management with filtering and status tracking.
    
    Args:
        user_id: Authenticated user ID
        action: Action to perform (list, status, history)
        status: Filter by status (comma-separated for multiple)
        job_id: Job ID (required for status action)
        limit: Maximum number of jobs to return
    
    Returns:
        JobListResult or job status data
    """
    try:
        agent = JobManagementAgent()
        
        input_data = {
            "action": action,
            "user_id": user_id,
            "limit": limit
        }
        
        if status:
            input_data["status"] = status
        
        if job_id:
            input_data["job_id"] = job_id
        elif action == "status":
            raise HTTPException(status_code=400, detail="job_id required for status action")
        
        result = await agent.execute(input_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to process job request")
            )
        
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job management error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process job request: {str(e)}")


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Cancel a job.
    
    Args:
        job_id: Job ID to cancel
        user_id: Authenticated user ID
    
    Returns:
        Cancellation result
    """
    try:
        agent = JobManagementAgent()
        result = await agent.execute({
            "action": "cancel",
            "job_id": job_id,
            "user_id": user_id
        })
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to cancel job")
            )
        
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel job error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

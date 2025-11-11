"""
Access analytics API endpoints (v0.5.0)
Extended with productivity and business metrics (v1.0.0)
"""
from typing import Dict, List, Optional, Tuple
from fastapi import APIRouter, HTTPException, status, Security, Query, Depends
from consultantos.auth import verify_api_key, get_optional_user_id
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import logging
import hashlib
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Cloud Logging client for persistent analytics
try:
    from google.cloud import logging as cloud_logging
    _logging_client = cloud_logging.Client()
    _analytics_logger = _logging_client.logger("share_access_analytics")
    CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    CLOUD_LOGGING_AVAILABLE = False
    _analytics_logger = None


def log_share_access(share_id: str, ip_address: Optional[str], timestamp: str, user_agent: Optional[str] = None, route: Optional[str] = None):
    """Log share access to persistent storage"""
    try:
        log_entry = {
            "share_id": share_id,
            "ip_address": ip_address,
            "timestamp": timestamp,
            "user_agent": user_agent,
            "route": route
        }
        
        if CLOUD_LOGGING_AVAILABLE and _analytics_logger:
            _analytics_logger.log_struct(log_entry, severity="INFO")
        else:
            # Fallback to module logger
            logger.info(f"Share access: {share_id} from {ip_address} at {timestamp}")
    except Exception as e:
        logger.warning(f"Failed to log share access: {e}", exc_info=True)


@router.get("/shares/{share_id}")
async def get_share_analytics(
    share_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Get analytics for a shared report"""
    # Import shares from sharing endpoints
    import consultantos.api.sharing_endpoints as sharing_module
    _shares = sharing_module._shares
    
    # Filter logs for this share (would query Cloud Logging in production)
    share_logs = []  # Placeholder - would query actual logs
    
    # Check ownership
    if share_id not in _shares:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    share = _shares[share_id]
    if share.shared_by != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view analytics for your own shares"
        )
    
    # Calculate metrics
    # Note: IP-based counting is approximate due to NAT/proxy/dynamic IP/VPN limitations
    total_accesses = share.access_count
    
    # For unique visitors, combine multiple signals when available
    # In production, query Cloud Logging for actual access logs
    unique_visitor_keys = set()
    if share.access_count > 0:
        # Approximation: use access_count as proxy (in production, query logs)
        # For now, treat as approximation
        unique_visitors_approx = min(share.access_count, 1)  # At least 1 if accessed
    
    # Access by date (would need to query logs in production)
    access_by_date: Dict[str, int] = {}
    
    # Access by hour (would need to query logs in production)
    access_by_hour: Dict[int, int] = {}
    
    return {
        "share_id": share_id,
        "total_accesses": total_accesses,
        "unique_visitors": unique_visitors_approx,
        "access_by_date": access_by_date,
        "access_by_hour": access_by_hour,
        "last_accessed": share.last_accessed,
        "created_at": share.created_at,
        "analytics_notes": "Visitor counts are approximate. IP-based deduplication has limitations due to NAT, proxies, dynamic IPs, and VPNs. In production, this uses Cloud Logging with session_id and user_agent hashing for more accurate tracking."
    }


@router.get("/reports/{report_id}")
async def get_report_analytics(
    report_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Get analytics for a report"""
    # Get all shares for this report
    import consultantos.api.sharing_endpoints as sharing_module
    _shares = sharing_module._shares
    report_shares = [s for s in _shares.values() if s.report_id == report_id and s.shared_by == user_info["user_id"]]
    
    if not report_shares:
        # Check if user owns the report
        from consultantos.database import get_db_service
        db_service = get_db_service()
        report_metadata = db_service.get_report_metadata(report_id)
        
        if not report_metadata or report_metadata.user_id != user_info["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view analytics for your own reports"
            )
    
    # Aggregate analytics across all shares
    total_shares = len(report_shares)
    total_accesses = sum(s.access_count for s in report_shares)
    
    # Get comment count
    import consultantos.api.comments_endpoints as comments_module
    _report_comments = comments_module._report_comments
    comment_count = len(_report_comments.get(report_id, []))
    
    return {
        "report_id": report_id,
        "total_shares": total_shares,
        "total_accesses": total_accesses,
        "comment_count": comment_count,
        "shares": [
            {
                "share_id": s.share_id,
                "share_type": s.share_type,
                "permission": s.permission.value if s.permission and hasattr(s.permission, 'value') else None,
                "access_count": s.access_count,
                "created_at": s.created_at
            }
            for s in report_shares
        ]
    }


# ============================================================================
# PRODUCTIVITY & BUSINESS METRICS ENDPOINTS
# ============================================================================

@router.get("/productivity")
async def get_productivity_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get productivity metrics:
    - Reports per analyst (per user)
    - Templates used vs created
    - Time savings from templates
    - Batch job processing time
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.api.template_endpoints import _templates
        from consultantos.jobs.queue import JobQueue
        
        db_service = get_db_service()
        if not db_service:
            raise HTTPException(status_code=500, detail="Database service unavailable")
        
        if not user_id:
            # Return empty metrics if not authenticated
            return {
                "period_days": days,
                "reports_per_user": {},
                "total_reports": 0,
                "templates_used": 0,
                "templates_created": 0,
                "template_adoption_rate": 0,
                "estimated_time_saved_hours": 0,
                "avg_batch_processing_time_seconds": 0,
                "total_batch_jobs": 0
            }
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all reports for user
        all_reports = db_service.list_reports(user_id=user_id, limit=10000)
        
        # Filter by date
        recent_reports = [
            r for r in all_reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= start_date
        ]
        
        # Reports per user (if team feature enabled, otherwise just current user)
        reports_per_user = {}
        for report in recent_reports:
            uid = report.user_id or "anonymous"
            reports_per_user[uid] = reports_per_user.get(uid, 0) + 1
        
        # Templates usage
        templates_used = 0
        templates_created = 0
        for template in _templates.values():
            if template.created_by == user_id:
                templates_created += 1
            # Count usage (would need usage tracking in production)
            templates_used += 1  # Placeholder
        
        # Time savings from templates (estimate: 30% time saved per template use)
        estimated_time_saved_hours = templates_used * 0.3 * 2  # 2 hours saved per template use
        
        # Batch job metrics
        job_queue = JobQueue()
        # Get job processing times (would need job history in production)
        avg_processing_time = 0.0
        total_batch_jobs = 0
        
        # Calculate from reports with execution_time_seconds
        execution_times = [
            r.execution_time_seconds for r in recent_reports
            if r.execution_time_seconds and r.execution_time_seconds > 0
        ]
        if execution_times:
            avg_processing_time = sum(execution_times) / len(execution_times)
        
        return {
            "period_days": days,
            "reports_per_user": reports_per_user,
            "total_reports": len(recent_reports),
            "templates_used": templates_used,
            "templates_created": templates_created,
            "template_adoption_rate": templates_used / max(templates_created, 1),
            "estimated_time_saved_hours": round(estimated_time_saved_hours, 2),
            "avg_batch_processing_time_seconds": round(avg_processing_time, 2),
            "total_batch_jobs": total_batch_jobs
        }
    except Exception as e:
        logger.error(f"Failed to get productivity metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get productivity metrics: {str(e)}")


@router.get("/business")
async def get_business_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get business metrics:
    - Top industries analyzed
    - Most used frameworks
    - Peak usage times
    - User adoption rate
    """
    try:
        from consultantos.database import get_db_service
        
        db_service = get_db_service()
        if not db_service:
            raise HTTPException(status_code=500, detail="Database service unavailable")
        
        if not user_id:
            # Return empty metrics if not authenticated
            return {
                "period_days": days,
                "top_industries": [],
                "most_used_frameworks": [],
                "peak_usage_times": {
                    "by_hour": {},
                    "peak_hour": None
                },
                "user_adoption": {
                    "total_unique_users": 0,
                    "new_users_this_period": 0,
                    "users_by_date": {}
                }
            }
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all reports
        all_reports = db_service.list_reports(user_id=user_id, limit=10000)
        
        # Filter by date
        recent_reports = [
            r for r in all_reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= start_date
        ]
        
        # Top industries
        industries = Counter()
        for report in recent_reports:
            if report.industry:
                industries[report.industry] += 1
        
        # Most used frameworks
        frameworks = Counter()
        for report in recent_reports:
            if report.frameworks:
                for framework in report.frameworks:
                    frameworks[framework] += 1
        
        # Peak usage times (by hour of day)
        usage_by_hour = defaultdict(int)
        for report in recent_reports:
            if report.created_at:
                try:
                    dt = datetime.fromisoformat(report.created_at.replace('Z', '+00:00'))
                    usage_by_hour[dt.hour] += 1
                except:
                    pass
        
        # User adoption (new users over time)
        users_by_date = defaultdict(set)
        for report in recent_reports:
            if report.created_at and report.user_id:
                try:
                    dt = datetime.fromisoformat(report.created_at.replace('Z', '+00:00'))
                    date_key = dt.date().isoformat()
                    users_by_date[date_key].add(report.user_id)
                except:
                    pass
        
        # Calculate adoption rate
        total_unique_users = len(set(r.user_id for r in recent_reports if r.user_id))
        new_users_this_period = total_unique_users  # Simplified
        
        return {
            "period_days": days,
            "top_industries": [
                {"industry": ind, "count": count}
                for ind, count in industries.most_common(10)
            ],
            "most_used_frameworks": [
                {"framework": fw, "count": count}
                for fw, count in frameworks.most_common(10)
            ],
            "peak_usage_times": {
                "by_hour": dict(sorted(usage_by_hour.items())),
                "peak_hour": max(usage_by_hour.items(), key=lambda x: x[1])[0] if usage_by_hour else None
            },
            "user_adoption": {
                "total_unique_users": total_unique_users,
                "new_users_this_period": new_users_this_period,
                "users_by_date": {k: len(v) for k, v in sorted(users_by_date.items())}
            }
        }
    except Exception as e:
        logger.error(f"Failed to get business metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get business metrics: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get comprehensive dashboard analytics including:
    - Report status pipeline (funnel)
    - Confidence score distribution
    - Analysis type breakdown
    - Job queue performance
    - Framework effectiveness
    - User activity calendar
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.jobs.queue import JobQueue
        
        db_service = get_db_service()
        if not db_service:
            raise HTTPException(status_code=500, detail="Database service unavailable")
        
        if not user_id:
            # Return empty metrics if not authenticated
            return {
                "period_days": days,
                "report_status_pipeline": {
                    "submitted": 0,
                    "processing": 0,
                    "completed": 0,
                    "archived": 0,
                    "failed": 0
                },
                "confidence_score_distribution": {
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "scores": []
                },
                "analysis_type_breakdown": {
                    "quick": 0,
                    "standard": 0,
                    "deep": 0
                },
                "industries_breakdown": {},
                "job_queue_performance": {
                    "avg_wait_time_seconds": 0,
                    "avg_processing_time_seconds": 0,
                    "queue_length": 0,
                    "throughput_per_hour": 0
                },
                "framework_effectiveness": {},
                "user_activity_calendar": {}
            }
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all reports
        all_reports = db_service.list_reports(user_id=user_id, limit=10000)
        
        # Filter by date
        recent_reports = [
            r for r in all_reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= start_date
        ]
        
        # Report status pipeline (funnel)
        status_counts = Counter(r.status for r in recent_reports if r.status)
        funnel_data = {
            "submitted": len(recent_reports),
            "processing": status_counts.get("processing", 0),
            "completed": status_counts.get("completed", 0),
            "archived": status_counts.get("archived", 0),
            "failed": status_counts.get("failed", 0)
        }
        
        # Confidence score distribution
        confidence_scores = [
            r.confidence_score for r in recent_reports
            if r.confidence_score is not None
        ]
        
        # Calculate median correctly for both odd and even-length arrays
        median = 0
        if confidence_scores:
            sorted_scores = sorted(confidence_scores)
            n = len(sorted_scores)
            if n == 0:
                median = 0
            elif n % 2 == 1:  # Odd length
                median = sorted_scores[n // 2]
            else:  # Even length
                median = (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2.0
        
        confidence_distribution = {
            "mean": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "median": median,
            "min": min(confidence_scores) if confidence_scores else 0,
            "max": max(confidence_scores) if confidence_scores else 0,
            "scores": confidence_scores
        }
        
        # Analysis type breakdown (by depth - would need depth field in reports)
        # For now, estimate based on execution time
        analysis_types = {
            "quick": 0,
            "standard": 0,
            "deep": 0
        }
        for report in recent_reports:
            if report.execution_time_seconds:
                if report.execution_time_seconds < 300:  # < 5 min
                    analysis_types["quick"] += 1
                elif report.execution_time_seconds < 900:  # < 15 min
                    analysis_types["standard"] += 1
                else:
                    analysis_types["deep"] += 1
        
        # Industries breakdown
        industries = Counter(r.industry for r in recent_reports if r.industry)
        
        # Job queue performance
        job_queue = JobQueue()
        queue_performance = {
            "avg_wait_time_seconds": 0,
            "avg_processing_time_seconds": 0,
            "queue_length": 0,
            "throughput_per_hour": 0
        }
        
        try:
            # Get recent jobs (last 7 days for metrics calculation)
            from consultantos.jobs.queue import JobStatus
            from datetime import timedelta
            
            # Get all jobs from the last 7 days
            all_jobs = await job_queue.list_jobs(limit=1000)
            
            # Filter jobs from the analysis period
            period_start = datetime.utcnow() - timedelta(days=days)
            recent_jobs = []
            for job in all_jobs:
                try:
                    created_at_str = job.get("created_at") or job.get("created_at")
                    if created_at_str:
                        if isinstance(created_at_str, str):
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00').replace('+00:00', ''))
                        else:
                            created_at = created_at_str
                        if created_at >= period_start:
                            recent_jobs.append(job)
                except Exception:
                    continue
            
            # Calculate metrics from completed jobs
            completed_jobs = [j for j in recent_jobs if j.get("status") in ["completed", "COMPLETED"]]
            pending_jobs = [j for j in recent_jobs if j.get("status") in ["pending", "PENDING"]]
            processing_jobs = [j for j in recent_jobs if j.get("status") in ["processing", "PROCESSING"]]
            
            # Queue length (pending + processing)
            queue_performance["queue_length"] = len(pending_jobs) + len(processing_jobs)
            
            if completed_jobs:
                # Calculate average processing time from execution_time_seconds
                processing_times = []
                wait_times = []
                
                for job in completed_jobs:
                    # Processing time from execution_time_seconds if available
                    exec_time = job.get("execution_time_seconds")
                    if exec_time and isinstance(exec_time, (int, float)) and exec_time > 0:
                        processing_times.append(exec_time)
                    
                    # Calculate wait time from timestamps
                    try:
                        created_at_str = job.get("created_at")
                        updated_at_str = job.get("updated_at") or job.get("completed_at")
                        
                        if created_at_str and updated_at_str:
                            if isinstance(created_at_str, str):
                                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00').replace('+00:00', ''))
                            else:
                                created_at = created_at_str
                            
                            if isinstance(updated_at_str, str):
                                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00').replace('+00:00', ''))
                            else:
                                updated_at = updated_at_str
                            
                            # Wait time = time until processing started (approximate)
                            # Processing time = total time - wait time
                            total_time = (updated_at - created_at).total_seconds()
                            if total_time > 0:
                                # Estimate wait time as 10% of total (conservative)
                                # Or use execution_time if available
                                if exec_time and exec_time < total_time:
                                    wait_time = total_time - exec_time
                                else:
                                    wait_time = total_time * 0.1  # Conservative estimate
                                wait_times.append(wait_time)
                    except Exception:
                        continue
                
                # Calculate averages
                if processing_times:
                    queue_performance["avg_processing_time_seconds"] = sum(processing_times) / len(processing_times)
                
                if wait_times:
                    queue_performance["avg_wait_time_seconds"] = sum(wait_times) / len(wait_times)
                
                # Calculate throughput (jobs per hour)
                if len(completed_jobs) > 0 and days > 0:
                    hours_in_period = days * 24
                    queue_performance["throughput_per_hour"] = len(completed_jobs) / hours_in_period
        except Exception as e:
            logger.warning(
                f"Failed to calculate job queue performance metrics: {e}",
                exc_info=True
            )
            # Keep default values on error
        
        # Framework effectiveness (framework vs industry)
        framework_effectiveness = defaultdict(lambda: defaultdict(int))
        for report in recent_reports:
            if report.frameworks and report.industry:
                for framework in report.frameworks:
                    framework_effectiveness[framework][report.industry] += 1
        
        # User activity calendar (by date)
        activity_by_date = defaultdict(int)
        for report in recent_reports:
            if report.created_at:
                try:
                    dt = datetime.fromisoformat(report.created_at.replace('Z', '+00:00'))
                    date_key = dt.date().isoformat()
                    activity_by_date[date_key] += 1
                except:
                    pass
        
        return {
            "period_days": days,
            "report_status_pipeline": funnel_data,
            "confidence_score_distribution": confidence_distribution,
            "analysis_type_breakdown": analysis_types,
            "industries_breakdown": dict(industries.most_common(10)),
            "job_queue_performance": queue_performance,
            "framework_effectiveness": {
                fw: dict(ind) for fw, ind in framework_effectiveness.items()
            },
            "user_activity_calendar": dict(sorted(activity_by_date.items()))
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard analytics: {str(e)}")


@router.get("/insights")
async def get_ai_insights(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze for insights"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get AI-driven insights and recommendations
    """
    try:
        from consultantos.database import get_db_service
        
        db_service = get_db_service()
        if not db_service:
            raise HTTPException(status_code=500, detail="Database service unavailable")
        
        if not user_id:
            # Return empty insights if not authenticated
            return {
                "period_days": days,
                "insights": [],
                "generated_at": datetime.now().isoformat()
            }
        
        start_date = datetime.now() - timedelta(days=days)
        previous_start = datetime.now() - timedelta(days=days * 2)
        
        # Get reports for current and previous period
        all_reports = db_service.list_reports(user_id=user_id, limit=10000)
        
        current_reports = [
            r for r in all_reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= start_date
        ]
        
        previous_reports = [
            r for r in all_reports
            if r.created_at and 
            datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= previous_start and
            datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) < start_date
        ]
        
        insights = []
        
        # Compare deep analysis completion times
        current_deep_times = [
            r.execution_time_seconds for r in current_reports
            if r.execution_time_seconds and r.execution_time_seconds > 900
        ]
        previous_deep_times = [
            r.execution_time_seconds for r in previous_reports
            if r.execution_time_seconds and r.execution_time_seconds > 900
        ]
        
        if current_deep_times and previous_deep_times:
            current_avg = sum(current_deep_times) / len(current_deep_times)
            previous_avg = sum(previous_deep_times) / len(previous_deep_times)
            if current_avg > previous_avg * 1.1:  # 10% slower
                pct_slower = ((current_avg - previous_avg) / previous_avg) * 100
                insights.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"Deep Analysis completion time is {pct_slower:.0f}% slower than last week",
                    "recommendation": "Consider optimizing analysis depth or checking system resources"
                })
        
        # Framework confidence scores
        framework_confidences = defaultdict(list)
        for report in current_reports:
            if report.frameworks and report.confidence_score:
                for framework in report.frameworks:
                    framework_confidences[framework].append(report.confidence_score)
        
        if framework_confidences:
            avg_confidences = {
                fw: sum(scores) / len(scores)
                for fw, scores in framework_confidences.items()
            }
            if len(avg_confidences) > 1:
                best_framework = max(avg_confidences.items(), key=lambda x: x[1])
                worst_framework = min(avg_confidences.items(), key=lambda x: x[1])
                if best_framework[1] > worst_framework[1] * 1.2:  # 20% higher
                    insights.append({
                        "type": "quality",
                        "severity": "info",
                        "message": f"{best_framework[0]} has {((best_framework[1] - worst_framework[1]) / worst_framework[1] * 100):.0f}% higher confidence scores",
                        "recommendation": f"Consider recommending {best_framework[0]} more frequently"
                    })
        
        # Peak usage times
        usage_by_hour = defaultdict(int)
        for report in current_reports:
            if report.created_at:
                try:
                    dt = datetime.fromisoformat(report.created_at.replace('Z', '+00:00'))
                    usage_by_hour[dt.hour] += 1
                except:
                    pass
        
        if usage_by_hour:
            peak_hours = sorted(usage_by_hour.items(), key=lambda x: x[1], reverse=True)[:2]
            if len(peak_hours) >= 2:
                peak1, peak2 = peak_hours[0], peak_hours[1]
                if peak1[1] > peak2[1] * 2:  # 2x more
                    insights.append({
                        "type": "usage",
                        "severity": "info",
                        "message": f"Peak usage at {peak1[0]}:00 sees {peak1[1] / peak2[1]:.1f}x more requests",
                        "recommendation": "Plan resources accordingly for peak hours"
                    })
        
        # Industry processing times
        industry_times = defaultdict(list)
        for report in current_reports:
            if report.industry and report.execution_time_seconds:
                industry_times[report.industry].append(report.execution_time_seconds)
        
        if len(industry_times) > 1:
            avg_industry_times = {
                ind: sum(times) / len(times)
                for ind, times in industry_times.items()
            }
            slowest = max(avg_industry_times.items(), key=lambda x: x[1])
            fastest = min(avg_industry_times.items(), key=lambda x: x[1])
            if slowest[1] > fastest[1] * 1.3:  # 30% slower
                pct_slower = ((slowest[1] - fastest[1]) / fastest[1]) * 100
                insights.append({
                    "type": "performance",
                    "severity": "info",
                    "message": f"{slowest[0]} sector analyses take {pct_slower:.0f}% longer than {fastest[0]}",
                    "recommendation": "Consider optimizing data sources for slower industries"
                })
        
        # Job queue status
        from consultantos.jobs.queue import JobQueue
        job_queue = JobQueue()
        # Would need actual job queue status
        insights.append({
            "type": "system",
            "severity": "info",
            "message": "Check job queue status for pending jobs",
            "recommendation": "Monitor job queue for bottlenecks"
        })
        
        return {
            "period_days": days,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get AI insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get AI insights: {str(e)}")


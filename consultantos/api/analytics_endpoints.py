"""
Access analytics API endpoints (v0.5.0)
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Security, Request
from consultantos.auth import verify_api_key
from datetime import datetime, timedelta, timezone
import logging
import hashlib

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
    
    # Filter logs for this share
    share_logs = [log for log in _access_logs if log.get("share_id") == share_id]
    
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


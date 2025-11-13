"""
Dashboard Data Agent - Aggregates dashboard overview data efficiently
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
from consultantos.monitoring.intelligence_monitor import IntelligenceMonitor
from consultantos.jobs.queue import JobQueue
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class DashboardOverview(BaseModel):
    """Consolidated dashboard overview data"""
    monitors: List[Dict[str, Any]] = Field(default_factory=list, description="List of monitors")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Dashboard statistics")
    recent_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Recent alerts")
    active_jobs: List[Dict[str, Any]] = Field(default_factory=list, description="Active jobs")
    recent_reports: List[Dict[str, Any]] = Field(default_factory=list, description="Recent reports")
    generated_at: datetime = Field(default_factory=lambda: datetime.now())


class DashboardDataAgent(BaseAgent):
    """Agent for aggregating dashboard overview data efficiently"""

    def __init__(self, timeout: int = 30):
        super().__init__(
            name="dashboard_data_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a dashboard data aggregation specialist.
        Efficiently gather and consolidate data from multiple sources
        to provide a comprehensive dashboard overview.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate dashboard overview data from multiple sources.

        Args:
            input_data: Dictionary containing:
                - user_id: User ID for filtering
                - alert_limit: Limit for recent alerts (default: 10)
                - report_limit: Limit for recent reports (default: 5)

        Returns:
            DashboardOverview with consolidated data
        """
        user_id = input_data.get("user_id")
        alert_limit = input_data.get("alert_limit", 10)
        report_limit = input_data.get("report_limit", 5)

        # Initialize services
        db_service = get_db_service()
        if not db_service:
            raise Exception("Database service unavailable")

        # Lazy import to avoid circular dependency issues
        # Import AnalysisOrchestrator only when needed, inside try-except
        monitor_service = None
        try:
            # Use importlib to avoid circular import issues
            import importlib
            orchestrator_module = importlib.import_module('consultantos.orchestrator')
            AnalysisOrchestrator = getattr(orchestrator_module, 'AnalysisOrchestrator', None)
            
            if AnalysisOrchestrator is None:
                raise ImportError("AnalysisOrchestrator not found in orchestrator module")
            
            from consultantos.cache import get_disk_cache
            monitor_service = IntelligenceMonitor(
                orchestrator=AnalysisOrchestrator(),
                db_service=db_service,
                cache_service=get_disk_cache(),
            )
        except Exception as e:
            logger.warning(f"Failed to initialize monitor service (orchestrator may be unavailable): {e}")
            monitor_service = None

        # Gather data in parallel using asyncio.gather
        async def _noop_list():
            return []
        
        async def _noop_dict():
            return {}
        
        coros = []
        if monitor_service:
            coros.append(self._get_monitors(monitor_service, user_id))
            coros.append(self._get_stats(monitor_service, user_id))
            coros.append(self._get_recent_alerts(monitor_service, user_id, alert_limit))
        else:
            coros.append(_noop_list())
            coros.append(_noop_dict())
            coros.append(_noop_list())
        
        coros.append(self._get_active_jobs(user_id))
        coros.append(self._get_recent_reports(db_service, user_id, report_limit))
        
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        # Unpack results with error handling
        monitors = results[0] if not isinstance(results[0], Exception) else []
        stats = results[1] if not isinstance(results[1], Exception) else {}
        alerts = results[2] if not isinstance(results[2], Exception) else []
        jobs = results[3] if not isinstance(results[3], Exception) else []
        reports = results[4] if not isinstance(results[4], Exception) else []
        
        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error in parallel data gathering (index {i}): {result}")

        overview = DashboardOverview(
            monitors=monitors,
            stats=stats,
            recent_alerts=alerts,
            active_jobs=jobs,
            recent_reports=reports
        )

        return {
            "success": True,
            "data": overview.model_dump(),
            "error": None
        }

    async def _get_monitors(
        self, 
        monitor_service: IntelligenceMonitor, 
        user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get monitors for user"""
        try:
            monitors = await monitor_service.db.get_user_monitors(user_id)
            return [self._serialize_monitor(m) for m in monitors]
        except Exception as e:
            logger.error(f"Failed to get monitors: {e}")
            return []

    async def _get_stats(
        self, 
        monitor_service: IntelligenceMonitor, 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            stats = await monitor_service.db.get_monitoring_stats(user_id)
            return stats.model_dump() if hasattr(stats, 'model_dump') else dict(stats)
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    async def _get_recent_alerts(
        self, 
        monitor_service: IntelligenceMonitor, 
        user_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            monitors = await monitor_service.db.get_user_monitors(user_id)
            all_alerts = []
            
            # Get alerts from first 5 monitors
            for monitor in monitors[:5]:
                alerts = await monitor_service.db.get_monitor_alerts(monitor.id, limit=limit)
                all_alerts.extend([self._serialize_alert(a) for a in alerts])
            
            # Sort by created_at descending and limit
            all_alerts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return all_alerts[:limit]
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []

    async def _get_active_jobs(self, user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get active jobs"""
        try:
            job_queue = JobQueue()
            all_jobs = job_queue.list_jobs()
            
            # Filter by user_id if provided and status (using safe attribute access)
            active_jobs = [
                j for j in all_jobs
                if getattr(j, 'status', None) in ['pending', 'running'] 
                and (not user_id or getattr(j, 'user_id', None) == user_id)
            ]
            
            return [self._serialize_job(j) for j in active_jobs]
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []

    async def _get_recent_reports(
        self, 
        db_service: Any, 
        user_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recent reports"""
        try:
            reports = db_service.list_reports(user_id=user_id, limit=limit)
            return [self._serialize_report(r) for r in reports]
        except Exception as e:
            logger.error(f"Failed to get reports: {e}")
            return []

    def _serialize_monitor(self, monitor: Any) -> Dict[str, Any]:
        """Serialize monitor to dict"""
        return {
            "id": getattr(monitor, 'id', ''),
            "company": getattr(monitor, 'company', ''),
            "industry": getattr(monitor, 'industry', ''),
            "status": getattr(monitor, 'status', 'unknown'),
            "config": getattr(monitor, 'config', {}),
            "created_at": getattr(monitor, 'created_at', ''),
            "last_check": getattr(monitor, 'last_check', None),
            "total_alerts": getattr(monitor, 'total_alerts', 0),
            "error_count": getattr(monitor, 'error_count', 0),
            "last_error": getattr(monitor, 'last_error', None),
        }

    def _serialize_alert(self, alert: Any) -> Dict[str, Any]:
        """Serialize alert to dict"""
        return {
            "id": getattr(alert, 'id', ''),
            "monitor_id": getattr(alert, 'monitor_id', ''),
            "title": getattr(alert, 'title', ''),
            "summary": getattr(alert, 'summary', ''),
            "confidence": getattr(alert, 'confidence', 0),
            "created_at": getattr(alert, 'created_at', ''),
            "read": getattr(alert, 'read', False),
        }

    def _serialize_job(self, job: Any) -> Dict[str, Any]:
        """Serialize job to dict"""
        return {
            "id": getattr(job, 'id', ''),
            "status": getattr(job, 'status', 'unknown'),
            "created_at": getattr(job, 'created_at', ''),
            "updated_at": getattr(job, 'updated_at', ''),
            "progress": getattr(job, 'progress', 0),
        }

    def _serialize_report(self, report: Any) -> Dict[str, Any]:
        """Serialize report to dict"""
        return {
            "report_id": getattr(report, 'report_id', ''),
            "company": getattr(report, 'company', ''),
            "industry": getattr(report, 'industry', ''),
            "frameworks": getattr(report, 'frameworks', []),
            "status": getattr(report, 'status', 'unknown'),
            "confidence_score": getattr(report, 'confidence_score', None),
            "created_at": getattr(report, 'created_at', ''),
        }


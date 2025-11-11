"""
Dashboard Analytics Agent - Generates analytics and metrics for dashboard
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
from consultantos.jobs.queue import JobQueue
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ProductivityMetrics(BaseModel):
    """Productivity metrics for dashboard"""
    reports_per_day: float = Field(..., description="Average reports generated per day")
    avg_processing_time: float = Field(..., description="Average processing time in seconds")
    success_rate: float = Field(..., description="Success rate as percentage (0-100)")
    total_reports: int = Field(..., description="Total number of reports")
    reports_this_month: int = Field(..., description="Reports generated this month")
    reports_last_month: int = Field(..., description="Reports generated last month")


class BusinessMetrics(BaseModel):
    """Business metrics for dashboard"""
    total_frameworks_used: int = Field(..., description="Total number of frameworks used")
    framework_distribution: Dict[str, int] = Field(..., description="Count of each framework usage")
    avg_confidence_score: float = Field(..., description="Average confidence score across all reports")
    high_confidence_reports: int = Field(..., description="Number of reports with confidence > 0.8")
    industry_distribution: Dict[str, int] = Field(..., description="Reports by industry")
    company_distribution: Dict[str, int] = Field(..., description="Reports by company")


class DashboardAnalytics(BaseModel):
    """Comprehensive dashboard analytics"""
    report_status_pipeline: Dict[str, int] = Field(..., description="Count of reports by status")
    confidence_distribution: List[float] = Field(..., description="List of confidence scores")
    framework_effectiveness: Dict[str, float] = Field(..., description="Average confidence per framework")
    job_queue_metrics: Dict[str, Any] = Field(..., description="Job queue performance metrics")
    user_activity: Dict[str, int] = Field(..., description="Activity metrics by day")


class DashboardAnalyticsResult(BaseModel):
    """Complete dashboard analytics result"""
    productivity: ProductivityMetrics
    business: BusinessMetrics
    dashboard: DashboardAnalytics
    generated_at: datetime = Field(default_factory=datetime.now)


class DashboardAnalyticsAgent(BaseAgent):
    """Agent for generating comprehensive dashboard analytics"""

    def __init__(self, timeout: int = 30):
        super().__init__(
            name="dashboard_analytics_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a dashboard analytics specialist that generates insights from user data.
        Analyze reports, jobs, and user activity to provide actionable metrics.
        Focus on productivity, business impact, and system performance.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard analytics.

        Args:
            input_data: Dictionary containing:
                - user_id: User ID for filtering (optional)
                - days: Number of days to analyze (default: 30)

        Returns:
            DashboardAnalyticsResult with productivity, business, and dashboard metrics
        """
        user_id = input_data.get("user_id")
        days = input_data.get("days", 30)
        start_date = datetime.now() - timedelta(days=days)

        db_service = get_db_service()
        if not db_service:
            raise Exception("Database service unavailable")

        # Get all reports
        all_reports = db_service.list_reports(user_id=user_id, limit=10000)
        
        # Filter by date
        recent_reports = [
            r for r in all_reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= start_date
        ]

        # Calculate productivity metrics
        productivity = self._calculate_productivity_metrics(recent_reports, days)

        # Calculate business metrics
        business = self._calculate_business_metrics(recent_reports)

        # Calculate dashboard analytics
        dashboard = self._calculate_dashboard_analytics(recent_reports, days)

        result = DashboardAnalyticsResult(
            productivity=productivity,
            business=business,
            dashboard=dashboard
        )

        return {
            "success": True,
            "data": result.model_dump(),
            "error": None
        }

    def _calculate_productivity_metrics(
        self, 
        reports: List[Any], 
        days: int
    ) -> ProductivityMetrics:
        """Calculate productivity metrics"""
        total_reports = len(reports)
        reports_per_day = total_reports / days if days > 0 else 0

        # Calculate reports this month
        now = datetime.now()
        first_day_of_month = datetime(now.year, now.month, 1)
        reports_this_month = sum(
            1 for r in reports
            if r.created_at and datetime.fromisoformat(r.created_at.replace('Z', '+00:00')) >= first_day_of_month
        )

        # Calculate reports last month
        if now.month == 1:
            last_month_start = datetime(now.year - 1, 12, 1)
        else:
            last_month_start = datetime(now.year, now.month - 1, 1)
        last_month_end = first_day_of_month
        reports_last_month = sum(
            1 for r in reports
            if r.created_at and (
                lambda created: last_month_start <= created < last_month_end
            )(datetime.fromisoformat(r.created_at.replace('Z', '+00:00')))
        )

        # Calculate average processing time (if available in report metadata)
        processing_times = []
        for r in reports:
            if hasattr(r, 'processing_time') and r.processing_time:
                processing_times.append(r.processing_time)
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

        # Calculate success rate
        successful = sum(1 for r in reports if r.status == "completed")
        success_rate = (successful / total_reports * 100) if total_reports > 0 else 0

        return ProductivityMetrics(
            reports_per_day=round(reports_per_day, 2),
            avg_processing_time=round(avg_processing_time, 2),
            success_rate=round(success_rate, 2),
            total_reports=total_reports,
            reports_this_month=reports_this_month,
            reports_last_month=reports_last_month
        )

    def _calculate_business_metrics(self, reports: List[Any]) -> BusinessMetrics:
        """Calculate business metrics"""
        frameworks_used = {}
        confidence_scores = []
        industries = {}
        companies = {}

        for r in reports:
            # Framework distribution
            if hasattr(r, 'frameworks') and r.frameworks:
                for fw in r.frameworks:
                    frameworks_used[fw] = frameworks_used.get(fw, 0) + 1

            # Confidence scores
            if hasattr(r, 'confidence_score') and r.confidence_score is not None:
                confidence_scores.append(r.confidence_score)

            # Industry distribution
            if hasattr(r, 'industry') and r.industry:
                industries[r.industry] = industries.get(r.industry, 0) + 1

            # Company distribution
            if hasattr(r, 'company') and r.company:
                companies[r.company] = companies.get(r.company, 0) + 1

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        high_confidence = sum(1 for c in confidence_scores if c > 0.8)

        return BusinessMetrics(
            total_frameworks_used=len(frameworks_used),
            framework_distribution=frameworks_used,
            avg_confidence_score=round(avg_confidence, 3),
            high_confidence_reports=high_confidence,
            industry_distribution=industries,
            company_distribution=companies
        )

    def _calculate_dashboard_analytics(
        self, 
        reports: List[Any], 
        days: int
    ) -> DashboardAnalytics:
        """Calculate dashboard analytics"""
        # Report status pipeline
        status_counts = {}
        for r in reports:
            status = getattr(r, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Confidence distribution
        confidence_scores = [
            r.confidence_score for r in reports
            if hasattr(r, 'confidence_score') and r.confidence_score is not None
        ]

        # Framework effectiveness (average confidence per framework)
        framework_confidence = {}
        framework_counts = {}
        for r in reports:
            if hasattr(r, 'frameworks') and r.frameworks and hasattr(r, 'confidence_score') and r.confidence_score:
                for fw in r.frameworks:
                    if fw not in framework_confidence:
                        framework_confidence[fw] = 0
                        framework_counts[fw] = 0
                    framework_confidence[fw] += r.confidence_score
                    framework_counts[fw] += 1

        framework_effectiveness = {
            fw: round(framework_confidence[fw] / framework_counts[fw], 3)
            for fw in framework_confidence
        }

        # Job queue metrics
        try:
            job_queue = JobQueue()
            job_queue_metrics = {
                "pending": len([j for j in job_queue.list_jobs() if j.status == "pending"]),
                "running": len([j for j in job_queue.list_jobs() if j.status == "running"]),
                "completed": len([j for j in job_queue.list_jobs() if j.status == "completed"]),
                "failed": len([j for j in job_queue.list_jobs() if j.status == "failed"]),
            }
        except Exception as e:
            logger.warning(f"Failed to get job queue metrics: {e}")
            job_queue_metrics = {"pending": 0, "running": 0, "completed": 0, "failed": 0}

        # User activity (simplified - reports per day)
        activity = {}
        for r in reports:
            if r.created_at:
                date = datetime.fromisoformat(r.created_at.replace('Z', '+00:00')).date()
                date_str = date.isoformat()
                activity[date_str] = activity.get(date_str, 0) + 1

        return DashboardAnalytics(
            report_status_pipeline=status_counts,
            confidence_distribution=confidence_scores,
            framework_effectiveness=framework_effectiveness,
            job_queue_metrics=job_queue_metrics,
            user_activity=activity
        )


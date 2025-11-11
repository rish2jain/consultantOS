"""
Unit tests for dashboard agents
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from consultantos.agents import (
    DashboardAnalyticsAgent,
    DashboardDataAgent,
    ReportManagementAgent,
    JobManagementAgent,
)


# ============================================================================
# DASHBOARD ANALYTICS AGENT TESTS
# ============================================================================

class TestDashboardAnalyticsAgent:
    """Tests for DashboardAnalyticsAgent"""

    @pytest.mark.asyncio
    async def test_analytics_agent_execution(self):
        """Test analytics agent generates metrics correctly"""
        agent = DashboardAnalyticsAgent()

        # Mock database service
        mock_report = Mock()
        mock_report.created_at = (datetime.now() - timedelta(days=1)).isoformat()
        mock_report.status = "completed"
        mock_report.confidence_score = 0.85
        mock_report.frameworks = ["porter", "swot"]
        mock_report.industry = "Technology"
        mock_report.company = "Tesla"
        mock_report.processing_time = 45.5

        mock_db = Mock()
        mock_db.list_reports.return_value = [mock_report]

        with patch('consultantos.agents.dashboard_analytics_agent.get_db_service', return_value=mock_db):
            with patch('consultantos.agents.dashboard_analytics_agent.JobQueue') as mock_job_queue:
                mock_queue = Mock()
                mock_queue.list_jobs.return_value = []
                mock_job_queue.return_value = mock_queue

                result = await agent.execute({
                    "user_id": "test_user",
                    "days": 30
                })

                assert result["success"] is True
                assert "data" in result
                assert "productivity" in result["data"]
                assert "business" in result["data"]
                assert "dashboard" in result["data"]
                assert result["data"]["productivity"]["total_reports"] == 1
                assert result["data"]["business"]["avg_confidence_score"] == 0.85

    @pytest.mark.asyncio
    async def test_analytics_agent_no_reports(self):
        """Test analytics agent with no reports"""
        agent = DashboardAnalyticsAgent()

        mock_db = Mock()
        mock_db.list_reports.return_value = []

        with patch('consultantos.agents.dashboard_analytics_agent.get_db_service', return_value=mock_db):
            with patch('consultantos.agents.dashboard_analytics_agent.JobQueue') as mock_job_queue:
                mock_queue = Mock()
                mock_queue.list_jobs.return_value = []
                mock_job_queue.return_value = mock_queue

                result = await agent.execute({
                    "user_id": "test_user",
                    "days": 30
                })

                assert result["success"] is True
                assert result["data"]["productivity"]["total_reports"] == 0
                assert result["data"]["productivity"]["reports_per_day"] == 0.0

    @pytest.mark.asyncio
    async def test_analytics_agent_database_unavailable(self):
        """Test analytics agent handles database unavailable"""
        agent = DashboardAnalyticsAgent()

        with patch('consultantos.agents.dashboard_analytics_agent.get_db_service', return_value=None):
            with pytest.raises(Exception, match="Database service unavailable"):
                await agent.execute({
                    "user_id": "test_user",
                    "days": 30
                })


# ============================================================================
# DASHBOARD DATA AGENT TESTS
# ============================================================================

class TestDashboardDataAgent:
    """Tests for DashboardDataAgent"""

    @pytest.mark.asyncio
    async def test_data_agent_execution(self):
        """Test data agent aggregates dashboard data"""
        agent = DashboardDataAgent()

        # Mock services
        mock_db = Mock()
        mock_db.list_reports.return_value = []

        mock_monitor = Mock()
        mock_monitor.id = "monitor_1"
        mock_monitor.company = "Tesla"
        mock_monitor.industry = "EV"
        mock_monitor.status = "active"
        mock_monitor.config = {}
        mock_monitor.created_at = datetime.now().isoformat()
        mock_monitor.last_check = None
        mock_monitor.total_alerts = 5
        mock_monitor.error_count = 0
        mock_monitor.last_error = None

        mock_stats = Mock()
        mock_stats.model_dump.return_value = {
            "total_monitors": 1,
            "active_monitors": 1
        }

        mock_alert = Mock()
        mock_alert.id = "alert_1"
        mock_alert.monitor_id = "monitor_1"
        mock_alert.title = "Test Alert"
        mock_alert.summary = "Test summary"
        mock_alert.confidence = 0.8
        mock_alert.created_at = datetime.now().isoformat()
        mock_alert.read = False

        mock_monitor_service = Mock()
        mock_monitor_service.db.get_user_monitors = AsyncMock(return_value=[mock_monitor])
        mock_monitor_service.db.get_monitoring_stats = AsyncMock(return_value=mock_stats)
        mock_monitor_service.db.get_monitor_alerts = AsyncMock(return_value=[mock_alert])

        with patch('consultantos.agents.dashboard_data_agent.get_db_service', return_value=mock_db):
            with patch('consultantos.agents.dashboard_data_agent.IntelligenceMonitor', return_value=mock_monitor_service):
                with patch('consultantos.agents.dashboard_data_agent.JobQueue') as mock_job_queue:
                    mock_queue = Mock()
                    mock_queue.list_jobs.return_value = []
                    mock_job_queue.return_value = mock_queue

                    result = await agent.execute({
                        "user_id": "test_user",
                        "alert_limit": 10,
                        "report_limit": 5
                    })

                    assert result["success"] is True
                    assert "data" in result
                    assert len(result["data"]["monitors"]) == 1
                    assert len(result["data"]["recent_alerts"]) == 1
                    assert "stats" in result["data"]

    @pytest.mark.asyncio
    async def test_data_agent_database_unavailable(self):
        """Test data agent handles database unavailable"""
        agent = DashboardDataAgent()

        with patch('consultantos.agents.dashboard_data_agent.get_db_service', return_value=None):
            with pytest.raises(Exception, match="Database service unavailable"):
                await agent.execute({
                    "user_id": "test_user",
                    "alert_limit": 10,
                    "report_limit": 5
                })


# ============================================================================
# REPORT MANAGEMENT AGENT TESTS
# ============================================================================

class TestReportManagementAgent:
    """Tests for ReportManagementAgent"""

    @pytest.mark.asyncio
    async def test_report_agent_list(self):
        """Test report agent list action"""
        agent = ReportManagementAgent()

        mock_report = Mock()
        mock_report.report_id = "report_1"
        mock_report.company = "Tesla"
        mock_report.industry = "EV"
        mock_report.frameworks = ["porter", "swot"]
        mock_report.status = "completed"
        mock_report.confidence_score = 0.85
        mock_report.created_at = datetime.now().isoformat()
        mock_report.updated_at = None

        mock_db = Mock()
        mock_db.list_reports.return_value = [mock_report]

        with patch('consultantos.agents.report_management_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action": "list",
                "user_id": "test_user",
                "page": 1,
                "page_size": 50
            })

            assert result["success"] is True
            assert len(result["data"]["reports"]) == 1
            assert result["data"]["reports"][0]["company"] == "Tesla"

    @pytest.mark.asyncio
    async def test_report_agent_filter(self):
        """Test report agent filter action"""
        agent = ReportManagementAgent()

        mock_report = Mock()
        mock_report.report_id = "report_1"
        mock_report.company = "Tesla"
        mock_report.industry = "EV"
        mock_report.frameworks = ["porter"]
        mock_report.status = "completed"
        mock_report.confidence_score = 0.85
        mock_report.created_at = datetime.now().isoformat()

        mock_db = Mock()
        mock_db.list_reports.return_value = [mock_report]

        with patch('consultantos.agents.report_management_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action": "filter",
                "user_id": "test_user",
                "filters": {
                    "company": "Tesla",
                    "status": "completed"
                },
                "page": 1,
                "page_size": 50
            })

            assert result["success"] is True
            assert result["data"]["filtered"] == 1

    @pytest.mark.asyncio
    async def test_report_agent_search(self):
        """Test report agent search action"""
        agent = ReportManagementAgent()

        mock_report = Mock()
        mock_report.report_id = "report_1"
        mock_report.company = "Tesla"
        mock_report.industry = "EV"
        mock_report.frameworks = ["porter"]
        mock_report.status = "completed"
        mock_report.confidence_score = 0.85
        mock_report.created_at = datetime.now().isoformat()

        mock_db = Mock()
        mock_db.list_reports.return_value = [mock_report]

        with patch('consultantos.agents.report_management_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action": "search",
                "user_id": "test_user",
                "search_query": "Tesla",
                "page": 1,
                "page_size": 50
            })

            assert result["success"] is True
            assert len(result["data"]["reports"]) == 1

    @pytest.mark.asyncio
    async def test_report_agent_invalid_action(self):
        """Test report agent handles invalid action"""
        agent = ReportManagementAgent()

        mock_db = Mock()
        with patch('consultantos.agents.report_management_agent.get_db_service', return_value=mock_db):
            with pytest.raises(ValueError, match="Unknown action"):
                await agent.execute({
                    "action": "invalid",
                    "user_id": "test_user"
                })


# ============================================================================
# JOB MANAGEMENT AGENT TESTS
# ============================================================================

class TestJobManagementAgent:
    """Tests for JobManagementAgent"""

    @pytest.mark.asyncio
    async def test_job_agent_list(self):
        """Test job agent list action"""
        agent = JobManagementAgent()

        mock_job = Mock()
        mock_job.id = "job_1"
        mock_job.status = "running"
        mock_job.progress = 50
        mock_job.created_at = datetime.now().isoformat()
        mock_job.updated_at = datetime.now().isoformat()
        mock_job.completed_at = None
        mock_job.error = None
        mock_job.result = None
        mock_job.user_id = "test_user"

        mock_queue = Mock()
        mock_queue.list_jobs.return_value = [mock_job]
        mock_queue.get_job.return_value = mock_job

        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            result = await agent.execute({
                "action": "list",
                "user_id": "test_user",
                "status": "running",
                "limit": 50
            })

            assert result["success"] is True
            assert len(result["data"]["jobs"]) == 1
            assert result["data"]["jobs"][0]["status"] == "running"
            assert result["data"]["running"] == 1

    @pytest.mark.asyncio
    async def test_job_agent_status(self):
        """Test job agent status action"""
        agent = JobManagementAgent()

        mock_job = Mock()
        mock_job.id = "job_1"
        mock_job.status = "running"
        mock_job.progress = 50
        mock_job.created_at = datetime.now().isoformat()
        mock_job.updated_at = datetime.now().isoformat()

        mock_queue = Mock()
        mock_queue.get_job.return_value = mock_job

        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            result = await agent.execute({
                "action": "status",
                "job_id": "job_1"
            })

            assert result["success"] is True
            assert result["data"]["status"] == "running"

    @pytest.mark.asyncio
    async def test_job_agent_cancel(self):
        """Test job agent cancel action"""
        agent = JobManagementAgent()

        mock_job = Mock()
        mock_job.id = "job_1"
        mock_job.status = "running"
        mock_job.user_id = "test_user"

        mock_queue = Mock()
        mock_queue.get_job.return_value = mock_job
        mock_queue.cancel_job = Mock()

        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            result = await agent.execute({
                "action": "cancel",
                "job_id": "job_1",
                "user_id": "test_user"
            })

            assert result["success"] is True
            assert result["data"]["status"] == "cancelled"
            mock_queue.cancel_job.assert_called_once_with("job_1")

    @pytest.mark.asyncio
    async def test_job_agent_cancel_not_found(self):
        """Test job agent cancel with job not found"""
        agent = JobManagementAgent()

        mock_queue = Mock()
        mock_queue.get_job.return_value = None

        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            result = await agent.execute({
                "action": "cancel",
                "job_id": "nonexistent",
                "user_id": "test_user"
            })

            assert result["success"] is False
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_job_agent_history(self):
        """Test job agent history action"""
        agent = JobManagementAgent()

        mock_job_completed = Mock()
        mock_job_completed.id = "job_1"
        mock_job_completed.status = "completed"
        mock_job_completed.created_at = datetime.now().isoformat()
        mock_job_completed.user_id = "test_user"

        mock_job_failed = Mock()
        mock_job_failed.id = "job_2"
        mock_job_failed.status = "failed"
        mock_job_failed.created_at = (datetime.now() - timedelta(hours=1)).isoformat()
        mock_job_failed.user_id = "test_user"

        mock_queue = Mock()
        mock_queue.list_jobs.return_value = [mock_job_completed, mock_job_failed]

        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            result = await agent.execute({
                "action": "history",
                "user_id": "test_user",
                "limit": 50
            })

            assert result["success"] is True
            assert len(result["data"]["jobs"]) == 2
            assert result["data"]["total"] == 2

    @pytest.mark.asyncio
    async def test_job_agent_invalid_action(self):
        """Test job agent handles invalid action"""
        agent = JobManagementAgent()

        mock_queue = Mock()
        with patch('consultantos.agents.job_management_agent.JobQueue', return_value=mock_queue):
            with pytest.raises(ValueError, match="Unknown action"):
                await agent.execute({
                    "action": "invalid",
                    "user_id": "test_user"
                })


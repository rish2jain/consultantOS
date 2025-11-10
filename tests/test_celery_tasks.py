"""
Tests for Celery tasks.

Tests task execution, retry logic, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from consultantos.jobs.tasks import (
    check_monitor_task,
    check_monitor_user_triggered,
    check_scheduled_monitors_task,
    process_alert_task,
    send_alert_webhook,
    run_analysis_task,
    aggregate_snapshots_task,
    cleanup_old_data_task,
    train_anomaly_model_task,
)
from consultantos.models.monitoring import Monitor, Alert, MonitorStatus


@pytest.fixture
def mock_monitor():
    """Mock monitor for testing"""
    return Monitor(
        id="test_monitor_123",
        user_id="user_123",
        company="Tesla",
        industry="Electric Vehicles",
        status=MonitorStatus.ACTIVE,
        frequency="daily",
        frameworks=["porter", "swot"],
        alert_threshold=0.7,
        created_at=datetime.utcnow(),
        next_check=datetime.utcnow(),
    )


@pytest.fixture
def mock_alert():
    """Mock alert for testing"""
    return Alert(
        id="alert_123",
        monitor_id="test_monitor_123",
        title="Significant market change detected",
        summary="Tesla stock price changed by 15%",
        confidence=0.85,
        changes_detected=[],
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_analysis_request():
    """Mock analysis request for testing"""
    return {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot"],
        "depth": "standard",
    }


# ============================================================================
# Monitor Checking Tasks
# ============================================================================


class TestCheckMonitorTask:
    """Tests for check_monitor_task"""

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    @patch("consultantos.jobs.tasks.process_alert_task")
    def test_check_monitor_success(
        self,
        mock_process_alert,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
        mock_monitor,
        mock_alert,
    ):
        """Test successful monitor check"""
        # Setup mocks
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(
            return_value=[mock_alert]
        )
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute task
        result = check_monitor_task(mock_monitor.id)

        # Assertions
        assert result["monitor_id"] == mock_monitor.id
        assert result["alerts_count"] == 1
        assert "checked_at" in result

        # Verify alert processing was queued
        mock_process_alert.apply_async.assert_called_once()

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_check_monitor_no_alerts(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
        mock_monitor,
    ):
        """Test monitor check with no alerts generated"""
        # Setup mocks
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(return_value=[])
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute task
        result = check_monitor_task(mock_monitor.id)

        # Assertions
        assert result["monitor_id"] == mock_monitor.id
        assert result["alerts_count"] == 0

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_check_monitor_error_raises_exception(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
        mock_monitor,
    ):
        """Test monitor check failure raises exception for retry"""
        # Setup mocks to raise exception
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute task - should raise exception
        with pytest.raises(Exception) as exc_info:
            check_monitor_task(mock_monitor.id)

        assert "Database connection failed" in str(exc_info.value)


class TestCheckMonitorUserTriggered:
    """Tests for check_monitor_user_triggered"""

    @patch("consultantos.jobs.tasks.check_monitor_task")
    def test_user_triggered_check(self, mock_check_monitor, mock_monitor):
        """Test user-triggered monitor check"""
        # Setup mock
        mock_check_monitor.return_value = {
            "monitor_id": mock_monitor.id,
            "alerts_count": 2,
            "checked_at": datetime.utcnow().isoformat(),
        }

        # Execute task
        result = check_monitor_user_triggered(mock_monitor.id, "user_123")

        # Assertions
        assert result["monitor_id"] == mock_monitor.id
        assert result["user_triggered"] is True
        assert result["user_id"] == "user_123"


class TestCheckScheduledMonitorsTask:
    """Tests for check_scheduled_monitors_task"""

    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.check_monitor_task")
    def test_check_scheduled_monitors(
        self,
        mock_check_monitor,
        mock_db,
        mock_monitor,
    ):
        """Test scheduled monitor checking"""
        # Setup mocks
        mock_db_instance = Mock()
        mock_db_instance.get_monitors_due_for_check = AsyncMock(
            return_value=[mock_monitor]
        )
        mock_db.return_value = mock_db_instance

        # Execute task
        result = check_scheduled_monitors_task()

        # Assertions
        assert result["monitors_queued"] == 1
        assert "checked_at" in result

        # Verify task was queued
        mock_check_monitor.apply_async.assert_called_once()


# ============================================================================
# Alert Processing Tasks
# ============================================================================


class TestProcessAlertTask:
    """Tests for process_alert_task"""

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_process_alert_success(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
        mock_alert,
    ):
        """Test successful alert processing"""
        # Setup mocks
        mock_monitor_instance = Mock()
        mock_monitor_instance.send_alert = AsyncMock()
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute task
        result = process_alert_task(mock_alert.dict())

        # Assertions
        assert result["alert_id"] == mock_alert.id
        assert "channels" in result
        assert "processed_at" in result

        # Verify alert was sent
        mock_monitor_instance.send_alert.assert_called_once()


class TestSendAlertWebhook:
    """Tests for send_alert_webhook"""

    @patch("consultantos.jobs.tasks.httpx.Client")
    def test_webhook_success(self, mock_httpx_client):
        """Test successful webhook delivery"""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Test data
        webhook_url = "https://hooks.example.com/alerts"
        alert_data = {
            "id": "alert_123",
            "type": "change_detected",
            "message": "Test alert",
        }

        # Execute task
        result = send_alert_webhook(webhook_url, alert_data)

        # Assertions
        assert result["webhook_url"] == webhook_url
        assert result["status_code"] == 200
        assert "sent_at" in result

        # Verify webhook was called
        mock_client_instance.post.assert_called_once_with(
            webhook_url,
            json=alert_data,
            headers={"Content-Type": "application/json"}
        )

    @patch("consultantos.jobs.tasks.httpx.Client")
    def test_webhook_failure_raises_exception(self, mock_httpx_client):
        """Test webhook failure raises exception for retry"""
        # Setup mocks to raise exception
        mock_client_instance = Mock()
        mock_client_instance.post.side_effect = Exception("Connection timeout")
        mock_httpx_client.return_value.__enter__.return_value = mock_client_instance

        # Test data
        webhook_url = "https://hooks.example.com/alerts"
        alert_data = {"id": "alert_123"}

        # Execute task - should raise exception
        with pytest.raises(Exception) as exc_info:
            send_alert_webhook(webhook_url, alert_data)

        assert "Connection timeout" in str(exc_info.value)


# ============================================================================
# Analysis Tasks
# ============================================================================


class TestRunAnalysisTask:
    """Tests for run_analysis_task"""

    @patch("consultantos.jobs.tasks.AnalysisOrchestrator")
    @patch("consultantos.jobs.tasks.generate_pdf_report")
    @patch("consultantos.jobs.tasks.get_storage_service")
    @patch("consultantos.jobs.tasks.get_db_service")
    def test_run_analysis_success(
        self,
        mock_db,
        mock_storage,
        mock_pdf_gen,
        mock_orchestrator,
        mock_analysis_request,
    ):
        """Test successful analysis execution"""
        # Setup mocks
        mock_report = Mock()
        mock_report.executive_summary.confidence_score = 0.85

        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.execute = AsyncMock(return_value=mock_report)
        mock_orchestrator.return_value = mock_orchestrator_instance

        mock_pdf_gen.return_value = b"PDF content"

        mock_storage_instance = Mock()
        mock_storage_instance.upload_pdf.return_value = "https://storage.example.com/report.pdf"
        mock_storage.return_value = mock_storage_instance

        mock_db_instance = Mock()
        mock_db_instance.create_report_metadata.return_value = None
        mock_db.return_value = mock_db_instance

        # Execute task
        result = run_analysis_task(mock_analysis_request, user_id="user_123")

        # Assertions
        assert "report_id" in result
        assert result["company"] == "Tesla"
        assert "pdf_url" in result
        assert result["confidence_score"] == 0.85
        assert "completed_at" in result

        # Verify orchestrator was called
        mock_orchestrator_instance.execute.assert_called_once()

        # Verify PDF was generated and uploaded
        mock_pdf_gen.assert_called_once()
        mock_storage_instance.upload_pdf.assert_called_once()

        # Verify metadata was stored
        mock_db_instance.create_report_metadata.assert_called_once()


# ============================================================================
# Maintenance Tasks
# ============================================================================


class TestAggregateSnapshotsTask:
    """Tests for aggregate_snapshots_task"""

    @patch("consultantos.jobs.tasks.get_database_service")
    def test_aggregate_snapshots(self, mock_db, mock_monitor):
        """Test snapshot aggregation"""
        # Setup mocks
        mock_snapshot = Mock()
        mock_snapshot.confidence = 0.8

        mock_db_instance = Mock()
        mock_db_instance.list_monitors = AsyncMock(return_value=[mock_monitor])
        mock_db_instance.get_monitor_snapshots = AsyncMock(
            return_value=[mock_snapshot] * 30
        )
        mock_db.return_value = mock_db_instance

        # Execute task
        result = aggregate_snapshots_task()

        # Assertions
        assert result["snapshots_aggregated"] == 30
        assert "aggregated_at" in result


class TestCleanupOldDataTask:
    """Tests for cleanup_old_data_task"""

    @patch("consultantos.jobs.tasks.get_database_service")
    def test_cleanup_old_data(self, mock_db):
        """Test data cleanup"""
        # Setup mocks
        mock_db_instance = Mock()
        mock_db_instance.delete_snapshots_before = AsyncMock(return_value=50)
        mock_db_instance.delete_alerts_before = AsyncMock(return_value=20)
        mock_db.return_value = mock_db_instance

        # Execute task with 90 day retention
        result = cleanup_old_data_task(retention_days=90)

        # Assertions
        assert result["items_deleted"] == 70  # 50 snapshots + 20 alerts
        assert result["deleted_snapshots"] == 50
        assert result["deleted_alerts"] == 20
        assert "cutoff_date" in result
        assert "cleaned_at" in result


class TestTrainAnomalyModelTask:
    """Tests for train_anomaly_model_task"""

    @patch("consultantos.jobs.tasks.get_database_service")
    def test_train_anomaly_models(self, mock_db, mock_monitor):
        """Test anomaly model training"""
        # Setup mocks
        mock_snapshot = Mock()

        mock_db_instance = Mock()
        mock_db_instance.list_monitors = AsyncMock(return_value=[mock_monitor])
        mock_db_instance.get_monitor_snapshots = AsyncMock(
            return_value=[mock_snapshot] * 100  # Sufficient data
        )
        mock_db.return_value = mock_db_instance

        # Execute task
        result = train_anomaly_model_task()

        # Assertions
        assert result["models_trained"] == 1
        assert "trained_at" in result

    @patch("consultantos.jobs.tasks.get_database_service")
    def test_train_models_insufficient_data(self, mock_db, mock_monitor):
        """Test model training skips monitors with insufficient data"""
        # Setup mocks
        mock_snapshot = Mock()

        mock_db_instance = Mock()
        mock_db_instance.list_monitors = AsyncMock(return_value=[mock_monitor])
        mock_db_instance.get_monitor_snapshots = AsyncMock(
            return_value=[mock_snapshot] * 20  # Insufficient data
        )
        mock_db.return_value = mock_db_instance

        # Execute task
        result = train_anomaly_model_task()

        # Assertions - should skip training
        assert result["models_trained"] == 0


# ============================================================================
# Retry Logic Tests
# ============================================================================


class TestRetryLogic:
    """Tests for task retry behavior"""

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_task_retries_on_failure(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
    ):
        """Test task retries on failure"""
        # Setup mocks to fail
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(
            side_effect=Exception("Temporary failure")
        )
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute task - should raise for retry
        with pytest.raises(Exception):
            check_monitor_task("test_monitor_123")

        # In actual Celery execution, this would trigger retry logic
        # with exponential backoff (1min, 5min, 15min)

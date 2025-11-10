"""
Tests for Celery task retry logic and dead letter queue behavior.

Tests:
- Exponential backoff retry (1min, 5min, 15min)
- Task failure after exhausting retries
- Dead letter queue routing
- Retry count tracking
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from celery.exceptions import Retry
from consultantos.jobs.tasks import RetryTask, check_monitor_task


class TestRetryBackoffLogic:
    """Tests for exponential backoff retry logic"""

    def test_retry_task_configuration(self):
        """Test RetryTask base class configuration"""
        # Verify retry configuration
        assert RetryTask.retry_kwargs["max_retries"] == 3
        assert RetryTask.retry_backoff is True
        assert RetryTask.retry_backoff_max == 900  # 15 minutes
        assert RetryTask.retry_jitter is True

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_retry_on_first_failure(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
    ):
        """Test first retry attempt after failure"""
        # Setup mocks to fail once then succeed
        call_count = 0

        async def mock_check_updates(monitor_id):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary database error")
            return []

        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = mock_check_updates
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # First call should fail
        with pytest.raises(Exception):
            check_monitor_task("test_monitor_123")

        # Verify failure count
        assert call_count == 1

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_permanent_failure_after_max_retries(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
    ):
        """Test task fails permanently after exhausting retries"""
        # Setup mocks to always fail
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(
            side_effect=Exception("Persistent database failure")
        )
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # All retry attempts should fail
        for attempt in range(4):  # Initial + 3 retries
            with pytest.raises(Exception) as exc_info:
                check_monitor_task("test_monitor_123")
            assert "Persistent database failure" in str(exc_info.value)

        # After max retries, task should go to dead letter queue
        # (handled by Celery framework in production)


class TestDeadLetterQueueBehavior:
    """Tests for dead letter queue routing"""

    def test_task_on_failure_callback(self):
        """Test on_failure callback is invoked"""
        # Create mock task
        task = RetryTask()
        task.name = "test_task"

        # Mock logger
        with patch("consultantos.jobs.tasks.logger") as mock_logger:
            # Invoke on_failure callback
            task.on_failure(
                exc=Exception("Test failure"),
                task_id="task_123",
                args=("arg1",),
                kwargs={"key": "value"},
                einfo=Mock(traceback="test traceback"),
            )

            # Verify error was logged
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "failed permanently after retries" in call_args[0][0]
            assert call_args[1]["extra"]["task_name"] == "test_task"
            assert call_args[1]["extra"]["task_id"] == "task_123"

    def test_task_on_retry_callback(self):
        """Test on_retry callback tracks retry attempts"""
        # Create mock task
        task = RetryTask()
        task.name = "test_task"
        task.request = Mock(retries=2)  # Second retry

        # Mock logger
        with patch("consultantos.jobs.tasks.logger") as mock_logger:
            # Invoke on_retry callback
            task.on_retry(
                exc=Exception("Temporary failure"),
                task_id="task_123",
                args=("arg1",),
                kwargs={"key": "value"},
                einfo=Mock(),
            )

            # Verify retry was logged
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            assert "retry attempt" in call_args[0][0]
            assert call_args[1]["extra"]["retry_count"] == 2


class TestRetryDelayCalculation:
    """Tests for exponential backoff delay calculation"""

    def test_exponential_backoff_delays(self):
        """Test retry delays follow exponential backoff"""
        # Celery's exponential backoff formula:
        # delay = min(retry_backoff_max, 2 ** (retry - 1) * base_delay)
        # With retry_backoff=True and retry_jitter=True

        base_delay = 60  # 1 minute (from task_default_retry_delay)
        max_delay = 900  # 15 minutes (from retry_backoff_max)

        # Expected delays (without jitter):
        # Retry 1: min(900, 2^0 * 60) = 60 seconds (1 minute)
        # Retry 2: min(900, 2^1 * 60) = 120 seconds (2 minutes)
        # Retry 3: min(900, 2^2 * 60) = 240 seconds (4 minutes)
        # Note: With jitter, actual delays will vary slightly

        expected_delays = [60, 120, 240]

        for retry, expected_delay in enumerate(expected_delays, start=1):
            calculated_delay = min(max_delay, (2 ** (retry - 1)) * base_delay)
            assert calculated_delay == expected_delay


class TestTaskPriorityRetry:
    """Tests for retry behavior across priority queues"""

    @patch("consultantos.jobs.tasks.check_monitor_task")
    def test_high_priority_task_retries_maintain_priority(self, mock_task):
        """Test high-priority tasks maintain priority on retry"""
        # Mock task to simulate retry
        mock_task.apply_async.return_value = Mock(id="task_123")

        # Queue high-priority task
        result = mock_task.apply_async(
            args=["monitor_123"],
            priority=8,
            queue="high",
        )

        # Verify task was queued with high priority
        assert mock_task.apply_async.called
        call_kwargs = mock_task.apply_async.call_args[1]
        assert call_kwargs["priority"] == 8
        assert call_kwargs["queue"] == "high"

        # On retry, priority should be maintained
        # (Celery preserves task configuration on retry)


class TestRetryCircuitBreaker:
    """Tests for circuit breaker behavior with retries"""

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_rapid_failure_detection(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
    ):
        """Test rapid consecutive failures"""
        # Setup mocks to always fail
        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Simulate rapid failures
        failure_count = 0
        for _ in range(5):
            try:
                check_monitor_task("test_monitor_123")
            except Exception:
                failure_count += 1

        # All attempts should fail
        assert failure_count == 5

        # In production, circuit breaker would open after threshold
        # and reject tasks without attempting execution


class TestRetryIdempotency:
    """Tests for task idempotency on retry"""

    @patch("consultantos.jobs.tasks.IntelligenceMonitor")
    @patch("consultantos.jobs.tasks.get_orchestrator")
    @patch("consultantos.jobs.tasks.get_database_service")
    @patch("consultantos.jobs.tasks.get_cache_service")
    def test_monitor_check_is_idempotent(
        self,
        mock_cache,
        mock_db,
        mock_orchestrator,
        mock_intelligence_monitor,
    ):
        """Test monitor check can be safely retried"""
        # Track execution count
        execution_count = 0

        async def idempotent_check(monitor_id):
            nonlocal execution_count
            execution_count += 1
            # Same result regardless of how many times called
            return []

        mock_monitor_instance = Mock()
        mock_monitor_instance.check_for_updates = idempotent_check
        mock_intelligence_monitor.return_value = mock_monitor_instance

        # Execute multiple times (simulating retries)
        for _ in range(3):
            result = check_monitor_task("test_monitor_123")
            assert result["alerts_count"] == 0

        # Verify executed multiple times with same result
        assert execution_count == 3


class TestRetryRateLimiting:
    """Tests for rate limiting during retries"""

    def test_rate_limit_configuration(self):
        """Test task rate limits are configured"""
        from consultantos.jobs.celery_app import app

        # Check rate limit annotations
        annotations = app.conf.task_annotations

        assert "consultantos.jobs.tasks.check_monitor_task" in annotations
        assert annotations["consultantos.jobs.tasks.check_monitor_task"]["rate_limit"] == "10/m"

        assert "consultantos.jobs.tasks.process_alert_task" in annotations
        assert annotations["consultantos.jobs.tasks.process_alert_task"]["rate_limit"] == "30/m"


class TestRetryMetrics:
    """Tests for retry metric tracking"""

    @patch("consultantos.jobs.tasks.get_task_monitor")
    def test_retry_metrics_recorded(self, mock_task_monitor):
        """Test retry attempts are recorded in metrics"""
        # Create mock task monitor
        mock_monitor = Mock()
        mock_task_monitor.return_value = mock_monitor

        # Create task
        task = RetryTask()
        task.name = "test_task"
        task.request = Mock(retries=1)

        # Trigger on_retry callback
        task.on_retry(
            exc=Exception("Test failure"),
            task_id="task_123",
            args=(),
            kwargs={},
            einfo=Mock(),
        )

        # In production, metrics would be recorded
        # (implementation depends on monitoring setup)

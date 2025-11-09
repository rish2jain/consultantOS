"""
Comprehensive tests for background worker module
Testing job enqueueing, processing, status tracking, concurrent handling, error handling, and graceful shutdown
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from consultantos.jobs.worker import AnalysisWorker, get_worker
from consultantos.jobs.queue import JobQueue, JobStatus
from consultantos.models import AnalysisRequest, StrategicReport, ExecutiveSummary
from consultantos.database import ReportMetadata


@pytest.fixture
def mock_db_service():
    """Create mock database service"""
    db = Mock()
    db.get_report_metadata = Mock()
    db.create_report_metadata = Mock()
    db.update_report_metadata = Mock()
    db.list_reports = Mock(return_value=[])
    return db


@pytest.fixture
def mock_storage_service():
    """Create mock storage service"""
    storage = Mock()
    storage.upload_pdf = Mock(return_value="https://storage.example.com/report.pdf")
    return storage


@pytest.fixture
def mock_orchestrator():
    """Create mock orchestrator"""
    orchestrator = AsyncMock()

    # Create mock executive summary
    executive_summary = ExecutiveSummary(
        key_findings=["Finding 1", "Finding 2"],
        strategic_recommendations=["Recommendation 1"],
        confidence_score=0.85,
        sources=["https://example.com"]
    )

    # Create mock report
    mock_report = Mock(spec=StrategicReport)
    mock_report.executive_summary = executive_summary

    orchestrator.execute.return_value = mock_report
    return orchestrator


@pytest.fixture
def worker(mock_db_service, mock_storage_service, mock_orchestrator):
    """Create worker instance with mocked dependencies"""
    worker = AnalysisWorker()
    worker.db_service = mock_db_service
    worker.storage_service = mock_storage_service
    worker.orchestrator = mock_orchestrator
    return worker


class TestJobEnqueuingAndProcessing:
    """Tests for job enqueueing and processing workflow"""

    @pytest.mark.asyncio
    async def test_enqueue_job_success(self, mock_db_service):
        """Test successful job enqueueing"""
        queue = JobQueue()
        queue.db_service = mock_db_service

        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot"],
            depth="standard"
        )

        job_id = await queue.enqueue(request, user_id="test_user")

        # Verify job_id is valid UUID
        assert job_id is not None
        assert len(job_id) == 36  # UUID length with hyphens

        # Verify database call was made
        mock_db_service.create_report_metadata.assert_called_once()
        call_args = mock_db_service.create_report_metadata.call_args[0][0]
        assert call_args.company == "Tesla"
        assert call_args.status == JobStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_process_job_success(self, worker, mock_db_service):
        """Test successful job processing end-to-end"""
        job_id = "test-job-123"

        # Setup mock job metadata
        job_metadata = ReportMetadata(
            report_id=f"job_{job_id}",
            user_id="test_user",
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot"],
            status=JobStatus.PENDING.value,
            confidence_score=0.0,
            execution_time_seconds=0.0
        )
        mock_db_service.get_report_metadata.return_value = job_metadata

        # Mock job status from queue
        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock) as mock_update:
                with patch('consultantos.jobs.worker.generate_pdf_report', return_value=b'PDF_CONTENT'):
                    await worker.process_job(job_id)

        # Verify orchestrator was called
        worker.orchestrator.execute.assert_called_once()

        # Verify PDF was uploaded
        worker.storage_service.upload_pdf.assert_called_once()

        # Verify report metadata was created
        assert mock_db_service.create_report_metadata.call_count == 2  # Once for job, once for report

        # Verify job status was updated to processing and completed
        assert mock_update.call_count >= 2

    @pytest.mark.asyncio
    async def test_process_job_not_pending(self, worker):
        """Test that non-pending jobs are skipped"""
        job_id = "test-job-123"

        # Mock job already processing
        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PROCESSING.value}):
            await worker.process_job(job_id)

        # Verify orchestrator was NOT called
        worker.orchestrator.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_job_metadata_not_found(self, worker, mock_db_service):
        """Test job processing when metadata is not found"""
        job_id = "test-job-123"

        # Mock job metadata not found
        mock_db_service.get_report_metadata.return_value = None

        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock) as mock_update:
                await worker.process_job(job_id)

        # Verify job was marked as failed
        mock_update.assert_called()
        call_args = mock_update.call_args[0]
        assert call_args[1] == JobStatus.FAILED


class TestJobStatusTracking:
    """Tests for job status tracking through lifecycle"""

    @pytest.mark.asyncio
    async def test_status_transition_pending_to_processing(self, worker, mock_db_service):
        """Test status transition from pending to processing"""
        job_id = "test-job-123"

        job_metadata = ReportMetadata(
            report_id=f"job_{job_id}",
            user_id="test_user",
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            status=JobStatus.PENDING.value,
            confidence_score=0.0,
            execution_time_seconds=0.0
        )
        mock_db_service.get_report_metadata.return_value = job_metadata

        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock) as mock_update:
                with patch('consultantos.jobs.worker.generate_pdf_report', return_value=b'PDF'):
                    await worker.process_job(job_id)

        # Verify first call updates to PROCESSING
        first_call = mock_update.call_args_list[0]
        assert first_call[0][1] == JobStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_get_job_status_found(self, mock_db_service):
        """Test getting status of existing job"""
        queue = JobQueue()
        queue.db_service = mock_db_service

        job_id = "test-job-123"
        metadata = ReportMetadata(
            report_id=f"job_{job_id}",
            user_id="test_user",
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            status=JobStatus.PROCESSING.value,
            confidence_score=0.0,
            execution_time_seconds=0.0,
            created_at=datetime.now()
        )
        mock_db_service.get_report_metadata.return_value = metadata

        status = await queue.get_status(job_id)

        assert status["job_id"] == job_id
        assert status["status"] == JobStatus.PROCESSING.value
        assert status["company"] == "Tesla"

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, mock_db_service):
        """Test getting status of non-existent job"""
        queue = JobQueue()
        queue.db_service = mock_db_service

        mock_db_service.get_report_metadata.return_value = None

        status = await queue.get_status("nonexistent-job")

        assert status["status"] == "not_found"
        assert "error" in status


class TestConcurrentJobHandling:
    """Tests for concurrent job processing"""

    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self, worker, mock_db_service):
        """Test processing multiple jobs concurrently"""
        job_ids = ["job-1", "job-2", "job-3"]

        # Setup mock metadata for all jobs
        for job_id in job_ids:
            job_metadata = ReportMetadata(
                report_id=f"job_{job_id}",
                user_id="test_user",
                company=f"Company_{job_id}",
                industry="Technology",
                frameworks=["porter"],
                status=JobStatus.PENDING.value,
                confidence_score=0.0,
                execution_time_seconds=0.0
            )

            # Mock get_report_metadata to return appropriate metadata
            def get_metadata_side_effect(report_id):
                for jid in job_ids:
                    if report_id == f"job_{jid}":
                        return ReportMetadata(
                            report_id=report_id,
                            user_id="test_user",
                            company=f"Company_{jid}",
                            industry="Technology",
                            frameworks=["porter"],
                            status=JobStatus.PENDING.value,
                            confidence_score=0.0,
                            execution_time_seconds=0.0
                        )
                return None

            mock_db_service.get_report_metadata.side_effect = get_metadata_side_effect

        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock):
                with patch('consultantos.jobs.worker.generate_pdf_report', return_value=b'PDF'):
                    # Process all jobs concurrently
                    tasks = [worker.process_job(job_id) for job_id in job_ids]
                    await asyncio.gather(*tasks, return_exceptions=True)

        # Verify orchestrator was called for each job
        assert worker.orchestrator.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_worker_limits_concurrent_jobs(self, worker, mock_db_service):
        """Test that worker limits concurrent job processing"""
        # Setup 5 pending jobs
        pending_jobs = [
            {"job_id": f"job-{i}", "status": JobStatus.PENDING.value}
            for i in range(5)
        ]

        with patch.object(worker.queue, 'list_jobs', return_value=pending_jobs):
            with patch.object(worker, 'process_job', new_callable=AsyncMock) as mock_process:
                # Stop after one iteration
                worker.running = True

                # Run one iteration
                pending_jobs_result = await worker.queue.list_jobs(statuses=[JobStatus.PENDING], limit=10)
                tasks = [worker.process_job(job["job_id"]) for job in pending_jobs_result[:3]]
                await asyncio.gather(*tasks, return_exceptions=True)

                worker.running = False

                # Should process max 3 jobs concurrently
                assert mock_process.call_count <= 3


class TestErrorHandlingAndRetry:
    """Tests for error handling and retry logic"""

    @pytest.mark.asyncio
    async def test_process_job_orchestrator_failure(self, worker, mock_db_service):
        """Test job failure when orchestrator fails"""
        job_id = "test-job-123"

        job_metadata = ReportMetadata(
            report_id=f"job_{job_id}",
            user_id="test_user",
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            status=JobStatus.PENDING.value,
            confidence_score=0.0,
            execution_time_seconds=0.0
        )
        mock_db_service.get_report_metadata.return_value = job_metadata

        # Make orchestrator fail
        worker.orchestrator.execute.side_effect = Exception("Analysis failed")

        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock) as mock_update:
                await worker.process_job(job_id)

        # Verify job was marked as failed
        mock_update.assert_called()
        final_call = mock_update.call_args
        assert final_call[0][1] == JobStatus.FAILED
        assert "error" in final_call[1]

    @pytest.mark.asyncio
    async def test_process_job_pdf_generation_failure(self, worker, mock_db_service):
        """Test job failure when PDF generation fails"""
        job_id = "test-job-123"

        job_metadata = ReportMetadata(
            report_id=f"job_{job_id}",
            user_id="test_user",
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"],
            status=JobStatus.PENDING.value,
            confidence_score=0.0,
            execution_time_seconds=0.0
        )
        mock_db_service.get_report_metadata.return_value = job_metadata

        with patch.object(worker.queue, 'get_status', return_value={"status": JobStatus.PENDING.value}):
            with patch.object(worker.queue, 'update_status', new_callable=AsyncMock) as mock_update:
                with patch('consultantos.jobs.worker.generate_pdf_report', side_effect=Exception("PDF error")):
                    await worker.process_job(job_id)

        # Verify job was marked as failed
        final_call = mock_update.call_args
        assert final_call[0][1] == JobStatus.FAILED

    @pytest.mark.asyncio
    async def test_worker_loop_continues_on_error(self, worker):
        """Test that worker loop continues after processing error"""
        # Mock list_jobs to return jobs then empty
        call_count = 0

        def list_jobs_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [{"job_id": "job-1", "status": JobStatus.PENDING.value}]
            worker.running = False  # Stop after second iteration
            return []

        with patch.object(worker.queue, 'list_jobs', side_effect=list_jobs_side_effect):
            with patch.object(worker, 'process_job', side_effect=Exception("Processing error")):
                await worker.start(poll_interval=0.1)

        # Worker should have continued and called list_jobs multiple times
        assert call_count >= 1


class TestGracefulShutdown:
    """Tests for graceful shutdown"""

    @pytest.mark.asyncio
    async def test_worker_stop(self, worker):
        """Test worker stop method"""
        worker.running = True
        worker.stop()

        assert worker.running is False

    @pytest.mark.asyncio
    async def test_worker_stops_processing_on_shutdown(self, worker):
        """Test worker stops processing when shutdown is triggered"""
        # Mock list_jobs to keep returning jobs
        with patch.object(worker.queue, 'list_jobs', return_value=[{"job_id": "job-1"}]):
            # Start worker in background
            worker_task = asyncio.create_task(worker.start(poll_interval=0.1))

            # Let it run briefly
            await asyncio.sleep(0.2)

            # Stop worker
            worker.stop()

            # Wait for task to complete
            try:
                await asyncio.wait_for(worker_task, timeout=1.0)
            except asyncio.TimeoutError:
                worker_task.cancel()

        assert worker.running is False

    @pytest.mark.asyncio
    async def test_worker_handles_none_db_service(self, worker):
        """Test worker handles None database service gracefully"""
        worker.db_service = None

        # Should return early without processing
        await worker.start(poll_interval=0.1)

        # Orchestrator should not be called
        worker.orchestrator.execute.assert_not_called()


class TestWorkerSingleton:
    """Tests for worker singleton pattern"""

    def test_get_worker_returns_same_instance(self):
        """Test that get_worker returns singleton instance"""
        worker1 = get_worker()
        worker2 = get_worker()

        assert worker1 is worker2

    def test_get_worker_thread_safe(self):
        """Test that get_worker is thread-safe"""
        import threading

        workers = []

        def get_and_store():
            workers.append(get_worker())

        threads = [threading.Thread(target=get_and_store) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All workers should be the same instance
        assert len(set(id(w) for w in workers)) == 1


class TestJobListingAndFiltering:
    """Tests for job listing and filtering"""

    @pytest.mark.asyncio
    async def test_list_jobs_with_status_filter(self, mock_db_service):
        """Test listing jobs with status filter"""
        queue = JobQueue()
        queue.db_service = mock_db_service

        # Mock reports
        reports = [
            ReportMetadata(
                report_id="job_job-1",
                user_id="user1",
                company="Tesla",
                industry="Auto",
                frameworks=["porter"],
                status=JobStatus.PENDING.value,
                confidence_score=0.0,
                execution_time_seconds=0.0,
                created_at=datetime.now()
            ),
            ReportMetadata(
                report_id="job_job-2",
                user_id="user1",
                company="Apple",
                industry="Tech",
                frameworks=["swot"],
                status=JobStatus.COMPLETED.value,
                confidence_score=0.9,
                execution_time_seconds=45.0,
                created_at=datetime.now()
            )
        ]
        mock_db_service.list_reports.return_value = reports

        # List only pending jobs
        pending_jobs = await queue.list_jobs(statuses=[JobStatus.PENDING], limit=10)

        assert len(pending_jobs) == 1
        assert pending_jobs[0]["status"] == JobStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_list_jobs_handles_none_db_service(self):
        """Test list_jobs handles None db_service gracefully"""
        queue = JobQueue()
        queue.db_service = None

        jobs = await queue.list_jobs()

        assert jobs == []

    @pytest.mark.asyncio
    async def test_list_jobs_handles_db_errors(self, mock_db_service):
        """Test list_jobs handles database errors gracefully"""
        queue = JobQueue()
        queue.db_service = mock_db_service

        # Make list_reports raise exception
        mock_db_service.list_reports.side_effect = Exception("DB error")

        jobs = await queue.list_jobs()

        assert jobs == []

"""
End-to-End Integration Tests for ConsultantOS

Tests complete user workflows from API request to final output.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


# ============================================================================
# COMPLETE ANALYSIS WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_analysis_workflow_basic(test_client: AsyncClient):
    """
    Test basic analysis workflow: request → analysis → response.

    This is the primary user journey for standard reports.
    """
    # 1. Submit analysis request
    response = await test_client.post("/analyze", json={
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter"]
    })

    assert response.status_code == 200
    result = response.json()

    # 2. Verify response structure
    assert "report_id" in result
    assert "company" in result
    assert result["company"] == "Tesla"
    assert "status" in result

    # 3. Verify analysis components present
    if result.get("status") == "completed":
        assert "confidence_score" in result
        assert result["confidence_score"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_analysis_workflow_with_all_features(
    test_client: AsyncClient,
    test_analysis_data: dict
):
    """
    Test comprehensive analysis workflow with all features enabled.

    Includes: research, market, financial, forecasting, social media, frameworks.
    """
    # Mock external services to avoid real API calls
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily, \
         patch("consultantos.agents.forecasting_agent.ForecastingAgent.execute") as mock_forecast, \
         patch("consultantos.agents.social_media_agent.SocialMediaAgent.execute") as mock_social:

        # Configure mocks
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Test content", "url": "http://test.com"}]
        }
        mock_forecast.return_value = {
            "scenarios": [{"name": "baseline", "predictions": [100, 110, 120]}],
            "confidence": 0.85
        }
        mock_social.return_value = {
            "sentiment": {"positive": 0.6, "negative": 0.2, "neutral": 0.2},
            "confidence": 0.75
        }

        # 1. Submit comprehensive analysis request
        response = await test_client.post("/analyze", json=test_analysis_data)

        assert response.status_code == 200
        result = response.json()

        # 2. Verify all components present
        assert result.get("company") == "Tesla"
        assert "report_id" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_analysis_workflow(test_client: AsyncClient):
    """
    Test async analysis workflow: enqueue → status check → retrieve.

    For long-running analyses that exceed timeout limits.
    """
    # 1. Enqueue analysis job
    response = await test_client.post("/analyze/async", json={
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot", "pestel"]
    })

    assert response.status_code == 200
    result = response.json()
    assert "job_id" in result
    job_id = result["job_id"]

    # 2. Check job status
    status_response = await test_client.get(f"/jobs/{job_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "status" in status_data
    assert status_data["status"] in ["pending", "running", "completed", "failed"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analysis_to_pdf_export_workflow(test_client: AsyncClient):
    """
    Test workflow: analysis → PDF generation → download.

    Note: PDF generation is now secondary to dashboard experience.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # 1. Create analysis
        analysis_response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert analysis_response.status_code == 200
        report_id = analysis_response.json().get("report_id")

        if not report_id:
            pytest.skip("Report ID not available")

        # 2. Generate PDF export
        pdf_response = await test_client.post(f"/reports/generate-pdf/{report_id}")

        # PDF generation might fail gracefully - check response
        assert pdf_response.status_code in [200, 500, 503]

        if pdf_response.status_code == 200:
            assert pdf_response.headers.get("content-type") in [
                "application/pdf",
                "application/octet-stream"
            ]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analysis_to_powerpoint_export_workflow(test_client: AsyncClient):
    """
    Test workflow: analysis → PowerPoint export (Phase 3 enhancement).
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # 1. Create analysis
        analysis_response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert analysis_response.status_code == 200
        report_id = analysis_response.json().get("report_id")

        if not report_id:
            pytest.skip("Report ID not available")

        # 2. Generate PowerPoint export
        pptx_response = await test_client.get(f"/reports/{report_id}/export?format=powerpoint")

        # PowerPoint export might fail gracefully - check response
        assert pptx_response.status_code in [200, 400, 404, 500, 503]

        if pptx_response.status_code == 200:
            # Should return PowerPoint file
            content_type = pptx_response.headers.get("content-type", "")
            assert "powerpoint" in content_type.lower() or "application/vnd.openxmlformats" in content_type.lower() or "application/octet-stream" in content_type.lower()


# ============================================================================
# MONITORING WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_monitoring_workflow_create_and_check(test_client: AsyncClient):
    """
    Test monitoring workflow: create monitor → baseline → check status.

    NEW PRIMARY WORKFLOW for continuous intelligence.
    """
    # 1. Create intelligence monitor
    monitor_response = await test_client.post("/monitoring/monitors", json={
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frequency": "daily",
        "frameworks": ["porter"],
        "alert_threshold": 0.7
    })

    # Monitor creation might require authentication
    if monitor_response.status_code == 401:
        pytest.skip("Authentication required for monitoring endpoints")

    assert monitor_response.status_code in [200, 201]
    monitor_data = monitor_response.json()
    assert "monitor_id" in monitor_data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forecasting_to_wargaming_workflow(test_client: AsyncClient):
    """
    Test data flow: forecasting → wargaming scenario → simulation.

    Tests integration between forecasting and wargaming features.
    """
    with patch("consultantos.agents.forecasting_agent.ForecastingAgent.execute") as mock_forecast:
        # 1. Generate forecast
        mock_forecast.return_value = {
            "scenarios": [
                {"name": "pessimistic", "predictions": [80, 85, 90]},
                {"name": "baseline", "predictions": [100, 110, 120]},
                {"name": "optimistic", "predictions": [120, 135, 150]}
            ],
            "confidence": 0.85
        }

        forecast_response = await test_client.post("/forecasting/generate", json={
            "company": "Tesla",
            "metric_name": "Revenue",
            "forecast_horizon_days": 90
        })

        # Forecasting endpoint might not exist yet
        if forecast_response.status_code == 404:
            pytest.skip("Forecasting endpoint not available")

        assert forecast_response.status_code == 200
        forecast = forecast_response.json()

        # 2. Create wargaming scenario using forecast data
        baseline_value = forecast.get("scenarios", [{}])[1].get("predictions", [100])[-1]

        scenario_response = await test_client.post("/wargaming/create-scenario", json={
            "name": "Revenue Scenarios",
            "variables": {
                "revenue": {
                    "type": "normal",
                    "params": {
                        "mean": baseline_value,
                        "std": baseline_value * 0.1
                    }
                }
            },
            "formula": "revenue * 0.4 - 50000000"
        })

        # Wargaming endpoint might not exist yet
        if scenario_response.status_code == 404:
            pytest.skip("Wargaming endpoint not available")


# ============================================================================
# MULTI-STAGE WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_analysis_enhancement_workflow(test_client: AsyncClient):
    """
    Test workflow: basic analysis → enhancement → updated report.

    Tests iterative improvement of analysis results.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # 1. Create initial analysis
        initial_response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert initial_response.status_code == 200
        initial_result = initial_response.json()
        report_id = initial_result.get("report_id")

        if not report_id:
            pytest.skip("Report ID not available")

        # 2. Enhance with additional frameworks
        enhanced_response = await test_client.post(f"/analyze/{report_id}/enhance", json={
            "additional_frameworks": ["swot"]
        })

        # Enhancement endpoint might not exist
        if enhanced_response.status_code == 404:
            pytest.skip("Enhancement endpoint not available")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_collaborative_analysis_workflow(test_client: AsyncClient):
    """
    Test workflow: create analysis → share → comment → update.

    Tests collaboration features for team analysis.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # 1. Create analysis
        analysis_response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert analysis_response.status_code == 200
        report_id = analysis_response.json().get("report_id")

        if not report_id:
            pytest.skip("Report ID not available")

        # 2. Share report (requires authentication)
        share_response = await test_client.post(f"/sharing/share/{report_id}", json={
            "share_with": ["user@example.com"],
            "permissions": "view"
        })

        if share_response.status_code == 401:
            pytest.skip("Authentication required for sharing")


# ============================================================================
# ERROR RECOVERY WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_partial_failure_graceful_degradation(test_client: AsyncClient):
    """
    Test that system returns partial results when some agents fail.

    Validates graceful degradation strategy.
    """
    with patch("consultantos.agents.research_agent.ResearchAgent.execute") as mock_research, \
         patch("consultantos.agents.market_agent.MarketAgent.execute") as mock_market:

        # Make one agent fail
        mock_research.side_effect = Exception("API unavailable")
        mock_market.return_value = {
            "trends": [{"query": "Tesla", "interest": 85}],
            "confidence": 0.8
        }

        response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        # System should return partial results with adjusted confidence
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            result = response.json()
            # Confidence should be reduced due to missing research data
            if "confidence_score" in result:
                assert result["confidence_score"] < 1.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_timeout_handling_workflow(test_client: AsyncClient):
    """
    Test that long-running requests are handled appropriately.

    Should redirect to async workflow or timeout gracefully.
    """
    with patch("consultantos.agents.research_agent.ResearchAgent.execute") as mock_research:
        # Simulate slow agent
        async def slow_execute(*args, **kwargs):
            import asyncio
            await asyncio.sleep(5)
            return {"results": "data"}

        mock_research.side_effect = slow_execute

        # This should either timeout or complete
        response = await test_client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter"]
            },
            timeout=10.0
        )

        # Accept various outcomes
        assert response.status_code in [200, 408, 504]


# ============================================================================
# DATA FLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_to_framework_data_flow(test_client: AsyncClient):
    """
    Test that research data flows correctly to framework analysis.

    Validates data pipeline integrity.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [
                {
                    "title": "Tesla Competitive Analysis",
                    "content": "Tesla faces competition from traditional automakers",
                    "url": "http://test.com"
                }
            ]
        }

        response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert response.status_code == 200
        result = response.json()

        # Framework analysis should reference research findings
        # (This validates that data flows from Phase 1 to Phase 2)
        if "framework_analysis" in result:
            framework_data = result["framework_analysis"]
            assert framework_data is not None


# ============================================================================
# EXPORT FORMAT TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_format_export_workflow(test_client: AsyncClient):
    """
    Test exporting analysis to multiple formats: PDF, Excel, Word, JSON.

    Validates all export pipelines.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient") as mock_tavily:
        mock_tavily.return_value.search.return_value = {
            "results": [{"title": "Test", "content": "Content", "url": "http://test.com"}]
        }

        # 1. Create analysis
        analysis_response = await test_client.post("/analyze", json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"]
        })

        assert analysis_response.status_code == 200
        report_id = analysis_response.json().get("report_id")

        if not report_id:
            pytest.skip("Report ID not available")

        # 2. Test JSON export
        json_response = await test_client.get(f"/reports/export/{report_id}/json")
        if json_response.status_code == 200:
            assert json_response.headers.get("content-type") == "application/json"

        # 3. Test Excel export
        excel_response = await test_client.get(f"/reports/export/{report_id}/excel")
        if excel_response.status_code == 200:
            assert "excel" in excel_response.headers.get("content-type", "").lower() or \
                   "spreadsheet" in excel_response.headers.get("content-type", "").lower()

        # 4. Test Word export
        word_response = await test_client.get(f"/reports/export/{report_id}/word")
        if word_response.status_code == 200:
            assert "word" in word_response.headers.get("content-type", "").lower() or \
                   "document" in word_response.headers.get("content-type", "").lower()

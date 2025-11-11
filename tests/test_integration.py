"""
Integration tests for ConsultantOS comprehensive analysis system.

Tests end-to-end workflows connecting all agents from Phase 1 (core research),
Phase 2 (advanced analytics), and Phase 3 (output generation).
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator
from consultantos.integration.data_flow import DataFlowManager
from consultantos.agents import get_available_agents, is_agent_available
from consultantos.models.integration import (
    ComprehensiveAnalysisRequest,
    ComprehensiveAnalysisResult,
    Phase1Results,
    Phase2Results,
    Phase3Results,
    ForecastResult,
    SocialMediaInsight,
    Dashboard,
    Narrative
)
from consultantos.models import (
    FinancialSnapshot,
    MarketTrends as MarketTrendResult,
    ExecutiveSummary
)


class TestAgentAvailability:
    """Test agent availability and graceful degradation."""

    def test_get_available_agents(self):
        """Test getting list of available agents."""
        agents = get_available_agents()

        assert "core" in agents
        assert "advanced" in agents
        assert "all" in agents

        # Core agents should always be available
        assert len(agents["core"]) == 7
        assert "ResearchAgent" in agents["core"]
        assert "MarketAgent" in agents["core"]
        assert "FinancialAgent" in agents["core"]
        assert "FrameworkAgent" in agents["core"]
        assert "SynthesisAgent" in agents["core"]
        assert "QualityAgent" in agents["core"]
        assert "DecisionIntelligenceEngine" in agents["core"]

    def test_is_agent_available_core(self):
        """Test checking availability of core agents."""
        assert is_agent_available("ResearchAgent") is True
        assert is_agent_available("MarketAgent") is True
        assert is_agent_available("FinancialAgent") is True

    def test_is_agent_available_advanced(self):
        """Test checking availability of advanced agents."""
        # These may or may not be available depending on dependencies
        result = is_agent_available("EnhancedForecastingAgent")
        assert isinstance(result, bool)

        result = is_agent_available("SocialMediaAgent")
        assert isinstance(result, bool)


class TestDataFlowManager:
    """Test data flow between agents."""

    @pytest.mark.asyncio
    async def test_forecast_from_financial_data(self):
        """Test creating forecast from financial data."""
        # Mock financial snapshot
        financial_result = FinancialSnapshot(
            ticker="TSLA",
            current_price=250.0,
            market_cap=800000000000,
            pe_ratio=60.0,
            revenue=80000000000,
            risk_assessment="Moderate"
        )

        # Test forecast generation
        # This will return None if agent unavailable, which is acceptable
        forecast = await DataFlowManager.forecast_from_financial_data(
            financial_result,
            forecast_horizon_days=90
        )

        # If agent is available, forecast should have data
        # The agent may return a dict with success/data structure or a ForecastResult
        if is_agent_available("EnhancedForecastingAgent") and forecast is not None:
            assert isinstance(forecast, ForecastResult) or (
                isinstance(forecast, dict) and 
                ("success" in forecast or "data" in forecast)
            )

    @pytest.mark.asyncio
    async def test_wargame_from_market_analysis(self):
        """Test creating wargaming scenarios from market data."""
        # Mock market result
        market_result = Mock(spec=MarketTrendResult)
        market_result.trends = ["AI adoption", "Electric vehicles"]
        market_result.emerging_topics = ["Autonomous driving"]

        # Test wargaming generation
        wargame = await DataFlowManager.wargame_from_market_analysis(
            market_result,
            company="Tesla",
            industry="Electric Vehicles"
        )

        # If agent is available, should return result or None
        if is_agent_available("WargamingAgent"):
            assert wargame is None or hasattr(wargame, "scenario_name")

    def test_extract_key_metrics(self):
        """Test extracting key metrics from comprehensive results."""
        result = ComprehensiveAnalysisResult(
            analysis_id="test-123",
            company="Tesla",
            industry="Electric Vehicles",
            confidence_score=0.85
        )

        metrics = DataFlowManager.extract_key_metrics(result)

        assert metrics["company"] == "Tesla"
        assert metrics["industry"] == "Electric Vehicles"
        assert metrics["confidence_score"] == 0.85
        assert "timestamp" in metrics

    def test_build_data_pipeline(self):
        """Test building execution pipeline."""
        pipeline = DataFlowManager.build_data_pipeline(
            company="Tesla",
            industry="Electric Vehicles",
            enable_features=["forecasting", "social_media", "dashboard"]
        )

        # Should have at least Phase 1 stages
        assert len(pipeline) >= 3

        # Check Phase 1 stages present
        stage_names = [stage["stage"] for stage in pipeline]
        assert "core_research" in stage_names
        assert "framework_analysis" in stage_names
        assert "synthesis" in stage_names

        # Phase 2 and 3 stages conditional on agent availability
        for stage in pipeline:
            assert "phase" in stage
            assert "agents" in stage
            assert "parallel" in stage
            assert "dependencies" in stage

    def test_validate_data_flow(self):
        """Test data flow validation between agents."""
        # Valid forecasting data
        forecast_data = {
            "historical_data": {"revenue": 80000000000},
            "metric_name": "Revenue"
        }
        assert DataFlowManager.validate_data_flow(
            "FinancialAgent",
            "EnhancedForecastingAgent",
            forecast_data
        ) is True

        # Invalid data (missing required fields)
        invalid_data = {"company": "Tesla"}
        assert DataFlowManager.validate_data_flow(
            "ResearchAgent",
            "EnhancedForecastingAgent",
            invalid_data
        ) is False


class TestAnalysisOrchestrator:
    """Test comprehensive analysis orchestration."""

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_basic(self):
        """Test basic comprehensive analysis with all features disabled."""
        orchestrator = AnalysisOrchestrator()

        # Mock the standard execute method to avoid external API calls
        with patch.object(orchestrator, 'execute', new_callable=AsyncMock) as mock_execute:
            # Create mock Phase 1 report
            mock_report = Mock()
            mock_report.company_research = None
            mock_report.market_trends = None
            mock_report.financial_snapshot = None
            mock_report.framework_analysis = None
            mock_report.executive_summary = ExecutiveSummary(
                company_name="Tesla",
                industry="Electric Vehicles",
                key_findings=["Finding 1", "Finding 2", "Finding 3"],
                strategic_recommendation="Continue current strategy",
                confidence_score=0.8,
                supporting_evidence=["Evidence 1", "Evidence 2"],
                next_steps=["Step 1"]
            )
            mock_report.metadata = {}
            mock_execute.return_value = mock_report

            # Execute comprehensive analysis with all advanced features disabled
            result = await orchestrator.execute_comprehensive_analysis(
                company="Tesla",
                industry="Electric Vehicles",
                enable_forecasting=False,
                enable_social_media=False,
                enable_dark_data=False,
                enable_wargaming=False,
                enable_dashboard=False,
                enable_narratives=False
            )

            # Validate basic structure
            assert isinstance(result, ComprehensiveAnalysisResult)
            assert result.company == "Tesla"
            assert result.industry == "Electric Vehicles"
            assert result.analysis_id is not None
            assert result.phase1 is not None
            assert isinstance(result.enabled_features, list)
            assert result.confidence_score > 0

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_with_errors(self):
        """Test comprehensive analysis with Phase 1 errors."""
        orchestrator = AnalysisOrchestrator()

        # Mock execute to raise exception
        with patch.object(orchestrator, 'execute', side_effect=Exception("API Error")):
            result = await orchestrator.execute_comprehensive_analysis(
                company="Tesla",
                industry="Electric Vehicles",
                enable_forecasting=False,
                enable_social_media=False
            )

            # Should return result with errors
            assert isinstance(result, ComprehensiveAnalysisResult)
            assert len(result.all_errors) > 0
            assert result.partial_results is True
            assert result.confidence_score > 0  # Should still have some confidence


class TestIntegrationEndpoints:
    """Test integration API endpoints."""

    def test_comprehensive_analysis_request_validation(self):
        """Test request model validation."""
        # Valid request
        request = ComprehensiveAnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles"
        )
        assert request.company == "Tesla"
        assert request.industry == "Electric Vehicles"
        assert request.enable_forecasting is True  # Default
        assert request.frameworks == ["porter", "swot"]  # Default

        # Custom request
        custom_request = ComprehensiveAnalysisRequest(
            company="Apple",
            industry="Technology",
            enable_forecasting=True,
            enable_social_media=True,
            enable_dark_data=True,
            frameworks=["porter", "swot", "pestel"],
            forecast_horizon_days=180
        )
        assert custom_request.forecast_horizon_days == 180
        assert "pestel" in custom_request.frameworks

    def test_comprehensive_analysis_result_structure(self):
        """Test result model structure."""
        result = ComprehensiveAnalysisResult(
            analysis_id="test-456",
            company="Apple",
            industry="Technology",
            confidence_score=0.9
        )

        # Validate structure
        assert result.analysis_id == "test-456"
        assert result.phase1 is not None
        assert result.phase2 is not None
        assert result.phase3 is not None
        assert isinstance(result.enabled_features, list)
        assert isinstance(result.all_errors, dict)

        # Can be serialized
        result_dict = result.model_dump()
        assert "analysis_id" in result_dict
        assert "company" in result_dict
        assert "phase1" in result_dict


class TestPhaseIntegration:
    """Test integration between different analysis phases."""

    def test_phase1_to_phase2_data_flow(self):
        """Test data flows from Phase 1 to Phase 2."""
        # Create Phase 1 results
        phase1 = Phase1Results(
            financial=FinancialSnapshot(
                ticker="AAPL",
                current_price=180.0,
                market_cap=2800000000000,
                risk_assessment="Low"
            ),
            market=Mock(spec=MarketTrendResult)
        )

        # Phase 2 should be able to use Phase 1 data
        assert phase1.financial is not None
        assert phase1.financial.current_price == 180.0

        # Can be used for forecasting
        forecast_data = {
            "historical_data": {
                "current_price": phase1.financial.current_price,
                "market_cap": phase1.financial.market_cap
            },
            "metric_name": "Price"
        }
        assert forecast_data["historical_data"]["current_price"] == 180.0

    def test_phase2_to_phase3_data_flow(self):
        """Test data flows from Phase 2 to Phase 3."""
        # Create Phase 2 results
        phase2 = Phase2Results(
            forecast=Mock(spec=ForecastResult),
            social_media=Mock(spec=SocialMediaInsight)
        )

        # Create comprehensive result for Phase 3 input
        comprehensive = ComprehensiveAnalysisResult(
            analysis_id="test-789",
            company="Microsoft",
            industry="Technology",
            phase2=phase2
        )

        # Phase 3 can access Phase 2 data
        assert comprehensive.phase2.forecast is not None
        assert comprehensive.phase2.social_media is not None


class TestGracefulDegradation:
    """Test graceful degradation when agents are unavailable."""

    @pytest.mark.asyncio
    async def test_missing_advanced_agents(self):
        """Test system works when advanced agents are missing."""
        orchestrator = AnalysisOrchestrator()

        # Mock Phase 1 to succeed
        with patch.object(orchestrator, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_report = Mock()
            mock_report.company_research = None
            mock_report.market_trends = None
            mock_report.financial_snapshot = None
            mock_report.framework_analysis = None
            mock_report.executive_summary = ExecutiveSummary(
                company_name="Test Corp",
                industry="Testing",
                key_findings=["Finding 1", "Finding 2", "Finding 3"],
                strategic_recommendation="Test recommendation",
                confidence_score=0.7,
                supporting_evidence=["Evidence 1"],
                next_steps=["Step 1"]
            )
            mock_report.metadata = {}
            mock_execute.return_value = mock_report

            # Try to enable all features
            result = await orchestrator.execute_comprehensive_analysis(
                company="Test Corp",
                industry="Testing",
                enable_forecasting=True,
                enable_social_media=True,
                enable_dark_data=True,
                enable_wargaming=True,
                enable_dashboard=True,
                enable_narratives=True
            )

            # Should complete without crashing
            assert isinstance(result, ComprehensiveAnalysisResult)
            assert result.company == "Test Corp"

            # Features that require unavailable agents won't be in enabled_features
            # but system should still work

    def test_partial_phase1_results(self):
        """Test handling partial Phase 1 results."""
        # Phase 1 with some missing data
        phase1 = Phase1Results(
            research=None,  # Missing
            market=Mock(spec=MarketTrendResult),  # Available
            financial=None,  # Missing
            errors={"research": "API error", "financial": "Timeout"}
        )

        assert phase1.market is not None
        assert len(phase1.errors) == 2
        assert "research" in phase1.errors


class TestConfidenceScoring:
    """Test confidence score calculation across phases."""

    def test_confidence_with_all_phases_success(self):
        """Test confidence when all phases succeed."""
        result = ComprehensiveAnalysisResult(
            analysis_id="test-success",
            company="Test",
            industry="Test",
            enabled_features=["core_research", "forecasting", "social_media", "dashboard"],
            confidence_score=0.9,
            partial_results=False
        )

        assert result.confidence_score >= 0.7
        assert result.partial_results is False

    def test_confidence_with_errors(self):
        """Test confidence degradation with errors."""
        result = ComprehensiveAnalysisResult(
            analysis_id="test-errors",
            company="Test",
            industry="Test",
            enabled_features=["core_research"],
            all_errors={"forecasting": "Error", "social_media": "Error"},
            confidence_score=0.5,
            partial_results=True
        )

        assert result.confidence_score < 0.9
        assert result.partial_results is True
        assert len(result.all_errors) == 2


@pytest.mark.asyncio
async def test_end_to_end_integration():
    """
    End-to-end integration test simulating full workflow.

    Tests the complete flow from request to comprehensive result
    with mocked external dependencies.
    """
    orchestrator = AnalysisOrchestrator()

    # Mock Phase 1 execution
    with patch.object(orchestrator, 'execute', new_callable=AsyncMock) as mock_execute:
        # Create realistic mock report
        mock_report = Mock()
        mock_report.company_research = None
        mock_report.market_trends = None
        mock_report.financial_snapshot = FinancialSnapshot(
            ticker="TSLA",
            current_price=250.0,
            market_cap=800000000000,
            risk_assessment="Moderate"
        )
        mock_report.framework_analysis = None
        mock_report.executive_summary = ExecutiveSummary(
            company_name="Tesla",
            industry="Electric Vehicles",
            key_findings=["Strong brand", "Growing market", "Innovation leader"],
            strategic_recommendation="Continue expansion strategy",
            confidence_score=0.85,
            supporting_evidence=["Market leadership", "Strong financials"],
            next_steps=["Expand production", "New markets"]
        )
        mock_report.metadata = {}
        mock_execute.return_value = mock_report

        # Execute comprehensive analysis
        result = await orchestrator.execute_comprehensive_analysis(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot"],
            enable_forecasting=False,  # Disable to avoid dependencies
            enable_social_media=False,
            enable_dashboard=False,
            enable_narratives=False
        )

        # Validate complete result
        assert isinstance(result, ComprehensiveAnalysisResult)
        assert result.company == "Tesla"
        assert result.industry == "Electric Vehicles"
        assert result.analysis_id is not None
        assert len(result.analysis_id) > 0

        # Phase 1 should be complete
        assert result.phase1 is not None
        assert result.phase1.synthesis is not None
        assert result.phase1.synthesis.confidence_score == 0.85

        # Metadata should be present
        assert result.execution_time_seconds >= 0
        assert isinstance(result.enabled_features, list)
        assert "core_research" in result.enabled_features

        # Should have reasonable confidence
        assert 0.3 <= result.confidence_score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

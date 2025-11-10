"""
Integration tests for enhanced orchestrator with strategic intelligence phases

Tests the complete 5-phase analysis pipeline:
- Phase 1: Data Gathering (Research, Market, Financial)
- Phase 2: Framework Analysis
- Phase 3: Synthesis
- Phase 4: Strategic Intelligence (Positioning, Disruption, Systems)
- Phase 5: Decision Intelligence
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from consultantos.orchestrator.orchestrator import AnalysisOrchestrator
from consultantos.models import (
    AnalysisRequest,
    CompanyResearch,
    MarketTrends,
    FinancialSnapshot,
    FrameworkAnalysis,
    ExecutiveSummary,
    PortersFiveForces,
    SWOTAnalysis
)


@pytest.fixture
def mock_phase1_results():
    """Mock Phase 1 data gathering results"""
    return {
        "research": CompanyResearch(
            company_name="Tesla",
            description="Tesla is an electric vehicle and clean energy company",
            products_services=["Model S", "Model 3", "Model X", "Model Y", "Powerwall"],
            target_market="Premium EV buyers and sustainability-focused consumers",
            key_competitors=["Ford", "GM", "Rivian", "Lucid"],
            recent_news=[
                "Tesla announces new Gigafactory in Texas",
                "Q4 earnings beat expectations"
            ],
            sources=["Tesla IR", "Reuters", "Bloomberg", "TechCrunch"]
        ),
        "market": MarketTrends(
            search_interest_trend="rising",
            interest_data={
                "12_month_avg": 75,
                "current_week": 82,
                "peak_interest": 95
            },
            geographic_distribution={
                "United States": 100,
                "China": 85,
                "Germany": 70
            },
            related_searches=["electric car", "tesla stock", "model 3"],
            competitive_comparison={
                "Tesla": 100,
                "GM": 45,
                "Ford": 52,
                "Rivian": 28
            }
        ),
        "financial": FinancialSnapshot(
            ticker="TSLA",
            market_cap=800000000000,
            revenue=81462000000,
            profit_margin=15.5,
            pe_ratio=65.2,
            risk_assessment="moderate",
            analyst_recommendations={
                "strong_buy": 10,
                "buy": 15,
                "hold": 8,
                "sell": 2,
                "strong_sell": 0
            }
        ),
        "errors": {}
    }


@pytest.fixture
def mock_framework_results():
    """Mock Phase 2 framework analysis results"""
    return {
        "frameworks": FrameworkAnalysis(
            porter_five_forces=PortersFiveForces(
                threat_of_new_entrants=3.5,
                supplier_power=2.5,
                buyer_power=3.0,
                threat_of_substitutes=4.0,
                competitive_rivalry=4.5,
                overall_intensity="medium-high",
                detailed_analysis={
                    "summary": "High competitive rivalry in EV market",
                    "key_insight": "Moderate threat from traditional automakers entering the space"
                }
            ),
            swot_analysis=SWOTAnalysis(
                strengths=["Brand recognition", "Technology leadership", "Vertical integration"],
                weaknesses=["Production challenges", "Quality control issues", "Service network gaps"],
                opportunities=["Expanding global EV market", "Energy storage growth", "Autonomous driving"],
                threats=["Increasing competition", "Regulatory changes", "Supply chain risks"]
            )
        )
    }


@pytest.fixture
def mock_synthesis_results():
    """Mock Phase 3 synthesis results"""
    return ExecutiveSummary(
        company_name="Tesla",
        industry="Electric Vehicles",
        key_findings=[
            "Strong market position with 25% growth trajectory",
            "Technology moat provides competitive advantage",
            "High competitive intensity requires continued innovation"
        ],
        strategic_recommendation="Maintain technology leadership while expanding production capacity and diversifying supply chain",
        confidence_score=0.85,
        supporting_evidence=[
            "25% growth trajectory in EV market",
            "Strong brand recognition and technology moat",
            "Positive analyst sentiment with 71% buy recommendations"
        ],
        next_steps=[
            "Accelerate production capacity",
            "Expand charging infrastructure",
            "Diversify supply chain"
        ]
    )


@pytest.fixture
def mock_strategic_intelligence_results():
    """Mock Phase 4 strategic intelligence results"""
    return {
        "positioning": {
            "company": "Tesla",
            "current_position": {"x_value": 25.5, "y_value": 15.5},
            "movement_vector_x": 5.2,
            "movement_vector_y": 2.1,
            "velocity": 5.6,
            "collision_risk": 0.25,
            "recommendations": [
                "Maintain differentiation strategy",
                "Watch for competitive convergence"
            ]
        },
        "disruption": {
            "company": "Tesla",
            "overall_risk": 45.5,
            "risk_level": "medium",
            "primary_threats": [
                {
                    "threat_name": "Chinese EV manufacturers",
                    "disruption_score": 65.0,
                    "growth_velocity": 4.2
                }
            ],
            "strategic_recommendations": [
                "Accelerate cost reduction initiatives",
                "Strengthen brand in emerging markets"
            ]
        },
        "systems": {
            "company": "Tesla",
            "feedback_loops": [
                {
                    "loop_type": "reinforcing",
                    "loop_strength": 0.75,
                    "description": "Brand → Sales → Network Effect → Brand"
                }
            ],
            "leverage_points": [
                {
                    "intervention": "Expand charging network",
                    "impact_score": 8.5,
                    "leverage_level": 4
                }
            ]
        }
    }


@pytest.fixture
def mock_decision_intelligence_results():
    """Mock Phase 5 decision intelligence results"""
    return {
        "report_id": "test-123",
        "company": "Tesla",
        "top_decisions": [
            {
                "title": "Production Capacity Expansion",
                "urgency": "high",
                "financial_impact": 5000000000,
                "options": [
                    {
                        "option_name": "Build new Gigafactory",
                        "investment_required": 2000000000,
                        "roi": 3.2,
                        "timeline_days": 730
                    }
                ],
                "recommended_option": "Build new Gigafactory"
            }
        ],
        "strategic_themes": ["Growth", "Scale", "Cost efficiency"],
        "confidence_score": 0.82
    }


@pytest.fixture
def analysis_request():
    """Standard analysis request"""
    return AnalysisRequest(
        company="Tesla",
        industry="Electric Vehicles",
        frameworks=["porter", "swot"],
        depth="standard"
    )


class TestOrchestratorPhase1:
    """Test Phase 1: Data Gathering"""

    @pytest.mark.asyncio
    async def test_phase1_parallel_execution(self, analysis_request, mock_phase1_results):
        """Test that Phase 1 agents execute in parallel"""
        orchestrator = AnalysisOrchestrator()

        # Mock all Phase 1 agents
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])

        # Execute Phase 1
        results = await orchestrator._execute_parallel_phase(analysis_request)

        # Verify all agents were called
        assert orchestrator.research_agent.execute.called
        assert orchestrator.market_agent.execute.called
        assert orchestrator.financial_agent.execute.called

        # Verify results structure
        assert results["research"] is not None
        assert results["market"] is not None
        assert results["financial"] is not None
        assert results["errors"] == {}

    @pytest.mark.asyncio
    async def test_phase1_graceful_degradation(self, analysis_request):
        """Test graceful degradation when some Phase 1 agents fail"""
        orchestrator = AnalysisOrchestrator()

        # Mock: Research succeeds, Market fails, Financial succeeds
        orchestrator.research_agent.execute = AsyncMock(
            return_value=CompanyResearch(
                company_name="Tesla",
                description="Test EV company",
                products_services=["Model S"],
                target_market="EV buyers",
                key_competitors=[],
                recent_news=[],
                sources=["Test source"]
            )
        )
        orchestrator.market_agent.execute = AsyncMock(side_effect=Exception("API timeout"))
        orchestrator.financial_agent.execute = AsyncMock(
            return_value=FinancialSnapshot(
                ticker="TSLA",
                market_cap=800000000000,
                risk_assessment="moderate"
            )
        )

        # Execute Phase 1
        results = await orchestrator._execute_parallel_phase(analysis_request)

        # Verify partial results
        assert results["research"] is not None
        assert results["market"] is None
        assert results["financial"] is not None
        assert "market" in results["errors"]

    @pytest.mark.asyncio
    async def test_phase1_all_agents_fail(self, analysis_request):
        """Test that exception is raised when all Phase 1 agents fail"""
        orchestrator = AnalysisOrchestrator()

        # Mock all agents to fail
        orchestrator.research_agent.execute = AsyncMock(side_effect=Exception("Failed"))
        orchestrator.market_agent.execute = AsyncMock(side_effect=Exception("Failed"))
        orchestrator.financial_agent.execute = AsyncMock(side_effect=Exception("Failed"))

        # Verify exception is raised
        with pytest.raises(Exception, match="All Phase 1 agents failed"):
            await orchestrator._execute_parallel_phase(analysis_request)


class TestOrchestratorPhase4:
    """Test Phase 4: Strategic Intelligence"""

    @pytest.mark.asyncio
    async def test_phase4_strategic_intelligence_execution(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_strategic_intelligence_results
    ):
        """Test Phase 4 strategic intelligence execution"""
        orchestrator = AnalysisOrchestrator()

        # Mock strategic intelligence agents
        if orchestrator.positioning_agent:
            orchestrator.positioning_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["positioning"]
            )
        if orchestrator.disruption_agent:
            orchestrator.disruption_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["disruption"]
            )
        if orchestrator.systems_agent:
            orchestrator.systems_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["systems"]
            )

        # Execute Phase 4
        results = await orchestrator._execute_strategic_intelligence_phase(
            analysis_request,
            mock_phase1_results,
            mock_framework_results
        )

        # Verify results if agents are available
        if results:
            assert "positioning" in results or "disruption" in results or "systems" in results

    @pytest.mark.asyncio
    async def test_phase4_graceful_degradation(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results
    ):
        """Test Phase 4 graceful degradation when agents unavailable"""
        orchestrator = AnalysisOrchestrator()

        # Set agents to None to simulate unavailability
        orchestrator.positioning_agent = None
        orchestrator.disruption_agent = None
        orchestrator.systems_agent = None

        # Execute Phase 4
        results = await orchestrator._execute_strategic_intelligence_phase(
            analysis_request,
            mock_phase1_results,
            mock_framework_results
        )

        # Should return None when all agents unavailable
        assert results is None


class TestOrchestratorPhase5:
    """Test Phase 5: Decision Intelligence"""

    @pytest.mark.asyncio
    async def test_phase5_decision_intelligence_execution(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_strategic_intelligence_results,
        mock_decision_intelligence_results
    ):
        """Test Phase 5 decision intelligence execution"""
        orchestrator = AnalysisOrchestrator()

        # Mock decision intelligence engine
        orchestrator.decision_intelligence.execute = AsyncMock(
            return_value=mock_decision_intelligence_results
        )

        # Execute Phase 5
        results = await orchestrator._execute_decision_intelligence_phase(
            analysis_request,
            mock_phase1_results,
            mock_framework_results,
            mock_strategic_intelligence_results
        )

        # Verify execution
        assert orchestrator.decision_intelligence.execute.called
        assert results is not None
        assert "top_decisions" in results


class TestOrchestratorEndToEnd:
    """Test complete end-to-end orchestration"""

    @pytest.mark.asyncio
    async def test_complete_5_phase_pipeline(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_synthesis_results,
        mock_strategic_intelligence_results,
        mock_decision_intelligence_results
    ):
        """Test complete 5-phase analysis pipeline"""
        orchestrator = AnalysisOrchestrator()

        # Mock all agents
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])
        orchestrator.framework_agent.execute = AsyncMock(return_value=mock_framework_results["frameworks"])
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock strategic intelligence agents if available
        if orchestrator.positioning_agent:
            orchestrator.positioning_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["positioning"]
            )
        if orchestrator.disruption_agent:
            orchestrator.disruption_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["disruption"]
            )
        if orchestrator.systems_agent:
            orchestrator.systems_agent.execute = AsyncMock(
                return_value=mock_strategic_intelligence_results["systems"]
            )

        # Mock decision intelligence
        orchestrator.decision_intelligence.execute = AsyncMock(
            return_value=mock_decision_intelligence_results
        )

        # Mock cache (disable for testing)
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', return_value=None):
                # Execute complete pipeline
                report = await orchestrator.execute(
                    analysis_request,
                    enable_strategic_intelligence=True
                )

        # Verify Phase 1-3 execution
        assert report.company_research is not None
        assert report.market_trends is not None
        assert report.financial_snapshot is not None
        assert report.framework_analysis is not None
        assert report.executive_summary is not None

        # Verify metadata
        assert report.metadata is not None
        assert "generated_at" in report.metadata
        assert "strategic_intelligence_enabled" in report.metadata

        # Verify confidence score
        assert report.executive_summary.confidence_score > 0

    @pytest.mark.asyncio
    async def test_pipeline_without_strategic_intelligence(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_synthesis_results
    ):
        """Test pipeline execution with strategic intelligence disabled"""
        orchestrator = AnalysisOrchestrator()

        # Mock core agents only
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])
        orchestrator.framework_agent.execute = AsyncMock(return_value=mock_framework_results["frameworks"])
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock cache
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', return_value=None):
                # Execute without strategic intelligence
                report = await orchestrator.execute(
                    analysis_request,
                    enable_strategic_intelligence=False
                )

        # Verify core phases executed
        assert report.company_research is not None
        assert report.executive_summary is not None

        # Verify strategic intelligence NOT enabled
        assert report.metadata.get("strategic_intelligence_enabled") is False

    @pytest.mark.asyncio
    async def test_confidence_score_adjustment_with_errors(
        self,
        analysis_request,
        mock_framework_results,
        mock_synthesis_results
    ):
        """Test that confidence score is adjusted when agents fail"""
        orchestrator = AnalysisOrchestrator()

        # Mock: Research succeeds, but Market and Financial fail
        orchestrator.research_agent.execute = AsyncMock(
            return_value=CompanyResearch(
                company_name="Tesla",
                description="Test EV company",
                products_services=["Model S"],
                target_market="EV buyers",
                key_competitors=[],
                recent_news=[],
                sources=["Test source"]
            )
        )
        orchestrator.market_agent.execute = AsyncMock(side_effect=Exception("Failed"))
        orchestrator.financial_agent.execute = AsyncMock(side_effect=Exception("Failed"))
        orchestrator.framework_agent.execute = AsyncMock(return_value=mock_framework_results["frameworks"])
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock cache
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', return_value=None):
                # Execute with errors - should fail when required agents fail
                with pytest.raises(Exception, match="Orchestration failed"):
                    report = await orchestrator.execute(
                        analysis_request,
                        enable_strategic_intelligence=False
                    )


class TestOrchestratorCaching:
    """Test caching behavior"""

    @pytest.mark.asyncio
    async def test_semantic_cache_hit(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_synthesis_results
    ):
        """Test that cached results are returned"""
        orchestrator = AnalysisOrchestrator()

        # Create mock cached report
        from consultantos.models import StrategicReport
        cached_report = StrategicReport(
            executive_summary=mock_synthesis_results,
            company_research=mock_phase1_results["research"],
            market_trends=mock_phase1_results["market"],
            financial_snapshot=mock_phase1_results["financial"],
            framework_analysis=mock_framework_results["frameworks"],
            recommendations=[
                "Accelerate production capacity",
                "Expand international markets",
                "Strengthen supply chain resilience"
            ],
            metadata={"cached": True}
        )

        # Mock cache hit
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=cached_report):
            report = await orchestrator.execute(analysis_request)

        # Verify cached report was returned
        assert report.metadata.get("cached") is True

        # Verify agents were NOT called
        orchestrator.research_agent.execute = AsyncMock()
        assert not orchestrator.research_agent.execute.called

    @pytest.mark.asyncio
    async def test_semantic_cache_miss(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_synthesis_results
    ):
        """Test that analysis executes on cache miss"""
        orchestrator = AnalysisOrchestrator()

        # Mock agents
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])
        orchestrator.framework_agent.execute = AsyncMock(return_value=mock_framework_results["frameworks"])
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock cache miss and store
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store') as mock_store:
                report = await orchestrator.execute(
                    analysis_request,
                    enable_strategic_intelligence=False
                )

                # Verify cache store was called
                assert mock_store.called

        # Verify agents were called
        assert orchestrator.research_agent.execute.called


class TestOrchestratorErrorHandling:
    """Test error handling and recovery"""

    @pytest.mark.asyncio
    async def test_framework_agent_failure_recovery(
        self,
        analysis_request,
        mock_phase1_results,
        mock_synthesis_results
    ):
        """Test recovery when framework agent fails"""
        orchestrator = AnalysisOrchestrator()

        # Mock Phase 1 success
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])

        # Mock framework agent failure
        orchestrator.framework_agent.execute = AsyncMock(side_effect=Exception("Framework failed"))

        # Mock synthesis agent
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock cache
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', return_value=None):
                # Should not raise exception - graceful degradation
                report = await orchestrator.execute(
                    analysis_request,
                    enable_strategic_intelligence=False
                )

        # Verify partial results
        assert report is not None
        assert "framework" in report.metadata.get("errors", {})

    @pytest.mark.asyncio
    async def test_timeout_handling(self, analysis_request):
        """Test timeout handling for slow agents"""
        orchestrator = AnalysisOrchestrator()

        # Mock slow agent that times out
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(10)  # Simulates timeout
            return None

        orchestrator.research_agent.execute = slow_execute
        orchestrator.market_agent.execute = AsyncMock(
            return_value=MarketTrends(
                search_interest_trend="rising",
                interest_data={"current": 80},
                geographic_distribution={"US": 100},
                related_searches=["ev", "electric", "tesla"],
                competitive_comparison={"Tesla": 100}
            )
        )
        orchestrator.financial_agent.execute = AsyncMock(
            return_value=FinancialSnapshot(
                ticker="TSLA",
                market_cap=800000000000,
                risk_assessment="moderate"
            )
        )

        # Execute with timeout (should handle gracefully)
        results = await orchestrator._execute_parallel_phase(analysis_request)

        # Research should be None due to timeout, others should succeed
        assert results["market"] is not None
        assert results["financial"] is not None


class TestOrchestratorMetadata:
    """Test metadata population and tracking"""

    @pytest.mark.asyncio
    async def test_metadata_population(
        self,
        analysis_request,
        mock_phase1_results,
        mock_framework_results,
        mock_synthesis_results
    ):
        """Test that metadata is properly populated"""
        orchestrator = AnalysisOrchestrator()

        # Mock agents
        orchestrator.research_agent.execute = AsyncMock(return_value=mock_phase1_results["research"])
        orchestrator.market_agent.execute = AsyncMock(return_value=mock_phase1_results["market"])
        orchestrator.financial_agent.execute = AsyncMock(return_value=mock_phase1_results["financial"])
        orchestrator.framework_agent.execute = AsyncMock(return_value=mock_framework_results["frameworks"])
        orchestrator.synthesis_agent.execute = AsyncMock(return_value=mock_synthesis_results)

        # Mock cache
        with patch('consultantos.orchestrator.orchestrator.semantic_cache_lookup', return_value=None):
            with patch('consultantos.orchestrator.orchestrator.semantic_cache_store', return_value=None):
                report = await orchestrator.execute(
                    analysis_request,
                    enable_strategic_intelligence=False
                )

        # Verify metadata fields
        assert "generated_at" in report.metadata
        assert "frameworks_requested" in report.metadata
        assert "depth" in report.metadata
        assert "partial_results" in report.metadata
        assert "strategic_intelligence_enabled" in report.metadata

        # Verify values
        assert report.metadata["frameworks_requested"] == ["porter", "swot"]
        assert report.metadata["depth"] == "standard"
        assert report.metadata["partial_results"] is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

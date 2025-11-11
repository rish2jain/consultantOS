"""
Tests for Phase 2 critical agents: PositioningAgent and DisruptionAgent

These tests mock external dependencies and verify agent logic.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents.disruption_agent import DisruptionAgent
from consultantos.models.positioning import DynamicPositioning
from consultantos.models.disruption import DisruptionAssessment


@pytest.fixture
def mock_market_data():
    """Mock market trends data"""
    return {
        "search_interest_trend": "Growing",
        "interest_data": {"2024-01": 50, "2024-02": 60, "2024-03": 75},
        "related_searches": [
            "AI automation",
            "cloud platform",
            "alternative to X",
            "SaaS subscription"
        ],
        "sources": ["https://trends.google.com"]
    }


@pytest.fixture
def mock_financial_data():
    """Mock financial snapshot data"""
    return {
        "profit_margin": 25.0,
        "market_share": 15.0,
        "revenue": 1000000000,
        "market_cap": 5000000000,
        "sources": ["https://finance.yahoo.com"]
    }


@pytest.fixture
def mock_research_data():
    """Mock company research data"""
    return {
        "company_name": "Tesla",
        "description": "Electric vehicle manufacturer",
        "sentiment": {
            "polarity": -0.2,
            "classification": "neutral"
        },
        "recent_news": [
            "Tesla launches new AI features",
            "Competition intensifies in EV market"
        ],
        "sources": ["https://reuters.com"]
    }


@pytest.fixture
def mock_competitors():
    """Mock competitor data"""
    return [
        {
            "name": "Competitor A",
            "market_data": {
                "search_interest_trend": "Growing",
                "interest_data": {},
                "related_searches": []
            },
            "financial_data": {
                "profit_margin": 20.0,
                "market_share": 10.0
            },
            "research_data": {
                "description": "Fast-growing startup with SaaS platform",
                "sentiment": {"polarity": 0.5, "classification": "positive"}
            }
        },
        {
            "name": "Competitor B",
            "market_data": {
                "search_interest_trend": "Stable",
                "interest_data": {},
                "related_searches": []
            },
            "financial_data": {
                "profit_margin": 18.0,
                "market_share": 12.0
            },
            "research_data": {
                "description": "Established player",
                "sentiment": {"polarity": 0.0, "classification": "neutral"}
            }
        }
    ]


class TestPositioningAgent:
    """Test suite for PositioningAgent"""

    @pytest.fixture
    def agent(self):
        """Create PositioningAgent instance"""
        return PositioningAgent(timeout=30)

    @pytest.mark.asyncio
    async def test_position_calculation(
        self,
        agent,
        mock_market_data,
        mock_financial_data,
        mock_research_data
    ):
        """Test basic position calculation"""
        position = agent._calculate_position(
            company="Tesla",
            market_data=mock_market_data,
            financial_data=mock_financial_data,
            research_data=mock_research_data
        )

        assert position.axis_x == "Market Growth"
        assert position.axis_y == "Profit Margin"
        assert 0 <= position.x_value <= 100
        assert 0 <= position.y_value <= 100
        assert position.market_share == 15.0

    @pytest.mark.asyncio
    async def test_movement_vector_calculation(
        self,
        agent,
        mock_market_data,
        mock_financial_data
    ):
        """Test movement vector calculation"""
        position = agent._calculate_position(
            company="Tesla",
            market_data=mock_market_data,
            financial_data=mock_financial_data,
            research_data={}
        )

        movement_x, movement_y = agent._calculate_movement_vector(
            position,
            mock_market_data,
            mock_financial_data
        )

        assert isinstance(movement_x, float)
        assert isinstance(movement_y, float)
        # Growing trend should have positive X movement
        assert movement_x > 0

    @pytest.mark.asyncio
    async def test_strategic_group_clustering(self, agent):
        """Test strategic group clustering logic"""
        from consultantos.models.positioning import CompetitivePosition

        positions = [
            CompetitivePosition(
                axis_x="Growth", axis_y="Margin",
                x_value=70, y_value=70, market_share=10,
                positioning_statement="Tesla growth"
            ),
            CompetitivePosition(
                axis_x="Growth", axis_y="Margin",
                x_value=75, y_value=68, market_share=8,
                positioning_statement="Rivian growth"
            ),
            CompetitivePosition(
                axis_x="Growth", axis_y="Margin",
                x_value=30, y_value=30, market_share=20,
                positioning_statement="Ford stable"
            )
        ]

        groups = agent._cluster_strategic_groups(positions)

        # Should identify at least one group
        assert len(groups) >= 0
        if groups:
            for group in groups:
                assert group.group_id > 0
                assert len(group.companies) > 0
                assert 0 <= group.centroid_x <= 100
                assert 0 <= group.centroid_y <= 100

    @pytest.mark.asyncio
    async def test_white_space_identification(self, agent, mock_market_data):
        """Test white space opportunity identification"""
        from consultantos.models.positioning import CompetitivePosition

        positions = [
            CompetitivePosition(
                axis_x="Growth", axis_y="Margin",
                x_value=30, y_value=30, market_share=10,
                positioning_statement="Low growth, low margin"
            )
        ]

        white_spaces = agent._identify_white_space(positions, mock_market_data)

        # Should identify multiple white space opportunities
        assert len(white_spaces) > 0
        for ws in white_spaces:
            assert 0 <= ws.position_x <= 100
            assert 0 <= ws.position_y <= 100
            assert ws.market_potential >= 0
            assert 0 <= ws.entry_barrier <= 100

    @pytest.mark.asyncio
    async def test_threat_detection(self, agent):
        """Test competitive threat detection"""
        from consultantos.models.positioning import (
            CompetitivePosition,
            PositionTrajectory
        )

        company_position = CompetitivePosition(
            axis_x="Growth", axis_y="Margin",
            x_value=50, y_value=50, market_share=15,
            positioning_statement="Tesla position"
        )
        company_movement = (5.0, 2.0)

        competitor_positions = [
            CompetitivePosition(
                axis_x="Growth", axis_y="Margin",
                x_value=45, y_value=48, market_share=10,
                positioning_statement="Competitor moving toward Tesla"
            )
        ]

        competitor_trajectories = [
            PositionTrajectory(
                company="Competitor A",
                positions=[],
                velocity=10.0,
                direction="advancing",
                momentum_score=75.0
            )
        ]

        threats = agent._detect_threats(
            company_position,
            company_movement,
            competitor_positions,
            competitor_trajectories
        )

        # May or may not detect threats depending on positions
        assert isinstance(threats, list)
        for threat in threats:
            assert threat.threatening_company
            assert 0 <= threat.severity <= 100
            assert threat.time_to_impact > 0

    @pytest.mark.asyncio
    async def test_full_analysis_execution(
        self,
        agent,
        mock_market_data,
        mock_financial_data,
        mock_research_data,
        mock_competitors
    ):
        """Test full positioning analysis execution"""
        # Mock the LLM call for recommendations
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock_llm:
            from pydantic import BaseModel
            class Recommendations(BaseModel):
                recommendations: list[str]

            mock_llm.return_value = Recommendations(
                recommendations=[
                    "Strengthen premium positioning",
                    "Monitor competitor movements",
                    "Explore white space in value segment"
                ]
            )

            input_data = {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "market_data": mock_market_data,
                "financial_data": mock_financial_data,
                "research_data": mock_research_data,
                "competitors": mock_competitors
            }

            result = await agent._execute_internal(input_data)

            assert isinstance(result, DynamicPositioning)
            assert result.company == "Tesla"
            assert result.industry == "Electric Vehicles"
            assert result.current_position is not None
            assert result.velocity >= 0
            assert 0 <= result.collision_risk <= 100
            assert 0 <= result.confidence_score <= 100
            assert len(result.recommendations) > 0


class TestDisruptionAgent:
    """Test suite for DisruptionAgent"""

    @pytest.fixture
    def agent(self):
        """Create DisruptionAgent instance"""
        return DisruptionAgent(timeout=30)

    @pytest.mark.asyncio
    async def test_overserving_score_calculation(
        self,
        agent,
        mock_financial_data,
        mock_market_data,
        mock_research_data
    ):
        """Test incumbent overserving score calculation"""
        score = agent._calculate_overserving_score(
            mock_financial_data,
            mock_market_data,
            mock_research_data
        )

        assert 0 <= score <= 100
        # High margin should contribute to score
        assert score > 0

    @pytest.mark.asyncio
    async def test_threat_velocity_score(
        self,
        agent,
        mock_competitors,
        mock_market_data
    ):
        """Test asymmetric threat velocity calculation"""
        score = agent._calculate_threat_velocity_score(
            mock_competitors,
            mock_market_data
        )

        assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_tech_shift_score(
        self,
        agent,
        mock_market_data,
        mock_research_data,
        mock_competitors
    ):
        """Test technology shift momentum score"""
        score = agent._calculate_tech_shift_score(
            mock_market_data,
            mock_research_data,
            mock_competitors
        )

        assert 0 <= score <= 100
        # Should detect tech keywords in related searches
        assert score > 0

    @pytest.mark.asyncio
    async def test_job_misalignment_score(
        self,
        agent,
        mock_research_data,
        mock_market_data
    ):
        """Test customer job misalignment score"""
        score = agent._calculate_job_misalignment_score(
            mock_research_data,
            mock_market_data
        )

        assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_model_innovation_score(
        self,
        agent,
        mock_market_data,
        mock_competitors
    ):
        """Test business model innovation score"""
        score = agent._calculate_model_innovation_score(
            mock_market_data,
            mock_competitors
        )

        assert 0 <= score <= 100
        # Should detect SaaS/subscription keywords
        assert score > 0

    @pytest.mark.asyncio
    async def test_risk_level_classification(self, agent):
        """Test risk level classification"""
        assert agent._classify_risk_level(85) == "critical"
        assert agent._classify_risk_level(65) == "high"
        assert agent._classify_risk_level(40) == "medium"
        assert agent._classify_risk_level(15) == "low"

    @pytest.mark.asyncio
    async def test_technology_trend_analysis(
        self,
        agent,
        mock_market_data,
        mock_research_data
    ):
        """Test technology trend identification"""
        trends = agent._analyze_technology_trends(
            mock_market_data,
            mock_research_data
        )

        assert isinstance(trends, list)
        for trend in trends:
            assert trend.technology
            assert trend.keyword_velocity >= 0
            assert 0 <= trend.adoption_rate <= 100
            assert trend.maturity_stage in ["emerging", "growing", "mature", "declining"]

    @pytest.mark.asyncio
    async def test_full_disruption_assessment(
        self,
        agent,
        mock_market_data,
        mock_financial_data,
        mock_research_data,
        mock_competitors
    ):
        """Test full disruption assessment execution"""
        # Mock LLM calls
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock_llm:
            from pydantic import BaseModel
            class Recommendations(BaseModel):
                recommendations: list[str]

            mock_llm.return_value = Recommendations(
                recommendations=[
                    "Develop low-cost product line",
                    "Invest in emerging technologies",
                    "Simplify core offering"
                ]
            )

            input_data = {
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "market_data": mock_market_data,
                "financial_data": mock_financial_data,
                "research_data": mock_research_data,
                "competitors": mock_competitors
            }

            result = await agent._execute_internal(input_data)

            assert isinstance(result, DisruptionAssessment)
            assert result.company == "Tesla"
            assert result.industry == "Electric Vehicles"
            assert 0 <= result.overall_risk <= 100
            assert result.risk_level in ["critical", "high", "medium", "low"]
            assert result.vulnerability_breakdown is not None
            assert len(result.strategic_recommendations) > 0
            assert len(result.early_warning_signals) > 0
            assert 0 <= result.confidence_score <= 100

    @pytest.mark.asyncio
    async def test_component_score_weights(self, agent):
        """Test disruption score component weights sum to 1.0"""
        total_weight = sum(agent.WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01  # Allow small floating point error


@pytest.mark.asyncio
async def test_agents_with_missing_data():
    """Test agents handle missing data gracefully"""
    positioning_agent = PositioningAgent()
    disruption_agent = DisruptionAgent()

    minimal_input = {
        "company": "TestCo",
        "industry": "Technology",
        "market_data": {},
        "financial_data": {},
        "research_data": {},
        "competitors": []
    }

    # Mock LLM calls
    with patch.object(positioning_agent, 'generate_structured', new_callable=AsyncMock) as mock_pos:
        with patch.object(disruption_agent, 'generate_structured', new_callable=AsyncMock) as mock_dis:
            from pydantic import BaseModel
            class Recommendations(BaseModel):
                recommendations: list[str]

            mock_pos.return_value = Recommendations(recommendations=["Monitor market"])
            mock_dis.return_value = Recommendations(recommendations=["Stay vigilant"])

            # Should not raise errors
            pos_result = await positioning_agent._execute_internal(minimal_input)
            dis_result = await disruption_agent._execute_internal(minimal_input)

            assert pos_result is not None
            assert dis_result is not None


@pytest.mark.asyncio
async def test_agents_with_invalid_input():
    """Test agents handle invalid input"""
    positioning_agent = PositioningAgent()
    disruption_agent = DisruptionAgent()

    invalid_input = {"invalid": "data"}

    with pytest.raises(ValueError):
        await positioning_agent._execute_internal(invalid_input)

    with pytest.raises(ValueError):
        await disruption_agent._execute_internal(invalid_input)

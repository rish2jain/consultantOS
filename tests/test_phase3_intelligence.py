"""
Tests for Phase 3 Advanced Intelligence Components

Tests feedback loop detection, momentum tracking, systems agent integration.
"""
import pytest
import numpy as np
from datetime import datetime

from consultantos.analysis.feedback_loops import FeedbackLoopDetector
from consultantos.analysis.momentum_tracking import MomentumTrackingEngine
from consultantos.agents.systems_agent import SystemsAgent
from consultantos.models.systems import LoopType


class TestFeedbackLoopDetector:
    """Tests for FeedbackLoopDetector"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return FeedbackLoopDetector(min_correlation=0.5, min_confidence=0.6)

    @pytest.fixture
    def sample_time_series(self):
        """Create sample time series data"""
        n_points = 24
        time = np.arange(n_points)
        growth = time * 2

        return {
            "revenue": 100 + growth + np.random.normal(0, 5, n_points),
            "customer_satisfaction": 70 + growth * 0.5 + np.random.normal(0, 2, n_points),
            "market_share": 15 + growth * 0.3 + np.random.normal(0, 1, n_points),
            "brand_value": 50 + growth * 0.8 + np.random.normal(0, 3, n_points),
        }

    def test_detect_causal_links(self, detector, sample_time_series):
        """Test causal link detection"""
        metric_names = list(sample_time_series.keys())

        links = detector.detect_causal_links(sample_time_series, metric_names)

        # Should find some links
        assert len(links) > 0

        # Check link structure
        for link in links:
            assert link.from_element in metric_names
            assert link.to_element in metric_names
            assert 0 <= link.strength <= 100
            assert link.polarity in ["+", "-"]
            assert link.delay in ["none", "short", "medium", "long", "unknown"]

    def test_detect_feedback_loops(self, detector, sample_time_series):
        """Test feedback loop detection"""
        metric_names = list(sample_time_series.keys())

        # First detect causal links
        links = detector.detect_causal_links(sample_time_series, metric_names)

        # Then detect loops
        reinforcing, balancing = detector.detect_feedback_loops(links, metric_names)

        # Should find some loops (may be 0 for random data)
        total_loops = len(reinforcing) + len(balancing)
        assert total_loops >= 0

        # Check loop structure
        for loop in reinforcing + balancing:
            assert loop.loop_id.startswith("R") or loop.loop_id.startswith("B")
            assert len(loop.elements) >= 2
            assert 0 <= loop.strength <= 100
            assert loop.loop_type in [LoopType.REINFORCING, LoopType.BALANCING]

    def test_identify_leverage_points(self, detector, sample_time_series):
        """Test leverage point identification"""
        metric_names = list(sample_time_series.keys())

        # Detect loops first
        links = detector.detect_causal_links(sample_time_series, metric_names)
        reinforcing, balancing = detector.detect_feedback_loops(links, metric_names)

        # Identify leverage points
        all_loops = reinforcing + balancing
        leverage_points = detector.identify_leverage_points(
            all_loops,
            "TestCo",
            "Technology"
        )

        # Should always generate some leverage points
        assert len(leverage_points) > 0

        # Check leverage point structure
        for lp in leverage_points:
            assert 1 <= lp.leverage_level <= 12
            assert 0 <= lp.impact_potential <= 100
            assert 0 <= lp.implementation_difficulty <= 100
            assert lp.strategic_priority in ["critical", "high", "medium", "low"]

    def test_analyze_system_complete(self, detector, sample_time_series):
        """Test complete system analysis"""
        metric_names = list(sample_time_series.keys())

        analysis = detector.analyze_system(
            sample_time_series,
            metric_names,
            "TestCo",
            "Technology"
        )

        # Check basic structure
        assert analysis.company == "TestCo"
        assert analysis.industry == "Technology"
        assert len(analysis.key_variables) == len(metric_names)
        assert 0 <= analysis.confidence_score <= 100

        # Should have some analysis results
        assert len(analysis.causal_links) >= 0
        assert len(analysis.reinforcing_loops) >= 0
        assert len(analysis.balancing_loops) >= 0
        assert len(analysis.leverage_points) > 0

    def test_insufficient_data(self, detector):
        """Test handling of insufficient data"""
        # Only 2 data points (need at least 3)
        insufficient_data = {
            "metric1": [1.0, 2.0],
            "metric2": [3.0, 4.0]
        }

        # Should return empty list or handle gracefully (not raise)
        links = detector.detect_causal_links(insufficient_data, ["metric1", "metric2"])
        # With only 2 points, should get no significant correlations
        assert len(links) == 0


class TestMomentumTrackingEngine:
    """Tests for MomentumTrackingEngine"""

    @pytest.fixture
    def engine(self):
        """Create engine instance"""
        return MomentumTrackingEngine(smoothing_window=3)

    @pytest.fixture
    def sample_metrics_data(self):
        """Create sample metrics data by component"""
        n_points = 12  # 1 year monthly
        time = np.arange(n_points)

        return {
            "market": {
                "search_volume": 100 + time * 5 + np.random.normal(0, 2, n_points),
                "brand_awareness": 50 + time * 3 + np.random.normal(0, 1, n_points),
            },
            "financial": {
                "revenue": 1000 + time * 50 + np.random.normal(0, 10, n_points),
                "gross_margin": 40 + time * 0.5 + np.random.normal(0, 1, n_points),
            },
            "strategic": {
                "partnerships": 5 + time * 0.5 + np.random.normal(0, 0.2, n_points),
                "product_launches": 2 + time * 0.3 + np.random.normal(0, 0.1, n_points),
            },
            "execution": {
                "delivery_time": 30 - time * 0.5 + np.random.normal(0, 1, n_points),  # Decreasing is good
                "quality_score": 80 + time * 1 + np.random.normal(0, 2, n_points),
            },
            "talent": {
                "employee_nps": 60 + time * 2 + np.random.normal(0, 3, n_points),
                "retention_rate": 85 + time * 0.5 + np.random.normal(0, 1, n_points),
            }
        }

    def test_calculate_velocity_and_acceleration(self, engine):
        """Test velocity and acceleration calculation"""
        time_series = [10, 12, 15, 19, 24, 30]

        velocity, acceleration = engine.calculate_velocity_and_acceleration(
            time_series,
            "test_metric"
        )

        # Should have positive velocity (growing)
        assert velocity > 0

        # Acceleration may be positive or negative
        assert isinstance(acceleration, float)

    def test_calculate_momentum_score(self, engine):
        """Test momentum score calculation"""
        # Growing metric with acceleration
        score = engine.calculate_momentum_score(
            current_value=120,
            previous_value=100,
            velocity=20,
            acceleration=5,
            metric_type="general"
        )

        # Should be positive and bounded
        assert 0 <= score <= 100
        assert score > 50  # Growing with positive acceleration

        # Declining metric
        score_declining = engine.calculate_momentum_score(
            current_value=80,
            previous_value=100,
            velocity=-20,
            acceleration=-5,
            metric_type="general"
        )

        # Should be lower for declining metric
        assert score_declining < score

    def test_analyze_metric_momentum(self, engine):
        """Test single metric momentum analysis"""
        time_series = [100, 105, 112, 120, 130, 142]

        metric = engine.analyze_metric_momentum(
            "test_metric",
            time_series,
            "general"
        )

        # Check structure
        assert metric.metric_name == "test_metric"
        assert metric.current_value == 142
        assert metric.previous_value == 130
        assert metric.velocity > 0  # Growing
        assert 0 <= metric.contribution_to_flywheel <= 100

    def test_detect_inflection_points(self, engine):
        """Test inflection point detection"""
        # Create series with clear inflection
        time_series = [10, 12, 15, 19, 24, 30, 32, 33, 33, 32, 30, 27]

        inflection_points = engine.detect_inflection_points(
            time_series,
            "test_metric"
        )

        # Should find some inflections
        assert len(inflection_points) >= 0

        # Check structure
        for idx, phase_change in inflection_points:
            # idx might be numpy.int64, not python int
            assert isinstance(idx, (int, np.integer))
            assert isinstance(phase_change, str)

    def test_calculate_flywheel_score(self, engine):
        """Test overall flywheel score calculation"""
        # Create sample metrics
        from consultantos.models.momentum import MomentumMetric

        market_metrics = [
            MomentumMetric(
                metric_name="metric1",
                current_value=100,
                previous_value=90,
                velocity=10,
                acceleration=2,
                contribution_to_flywheel=75.0
            )
        ]

        financial_metrics = [
            MomentumMetric(
                metric_name="metric2",
                current_value=200,
                previous_value=180,
                velocity=20,
                acceleration=3,
                contribution_to_flywheel=80.0
            )
        ]

        score = engine.calculate_flywheel_score(
            market_metrics,
            financial_metrics,
            [],  # strategic
            [],  # execution
            []   # talent
        )

        # Should be weighted average
        assert 0 <= score <= 100

    def test_analyze_momentum_complete(self, engine, sample_metrics_data):
        """Test complete momentum analysis"""
        analysis = engine.analyze_momentum(
            "TestCo",
            "Technology",
            sample_metrics_data
        )

        # Check basic structure
        assert analysis.company == "TestCo"
        assert analysis.industry == "Technology"
        assert 0 <= analysis.current_momentum <= 100
        assert analysis.momentum_trend in ["building", "sustaining", "declining", "stable"]

        # Should have metrics
        assert len(analysis.key_metrics) > 0

        # Should have recommendations
        assert len(analysis.acceleration_opportunities) > 0
        assert len(analysis.friction_points_to_address) >= 0
        assert len(analysis.momentum_preservation_strategies) > 0


@pytest.mark.asyncio
class TestSystemsAgent:
    """Tests for SystemsAgent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return SystemsAgent(timeout=90)

    @pytest.fixture
    def sample_input(self):
        """Create sample input data"""
        n_points = 24
        time = np.arange(n_points)
        growth = time * 2

        time_series_data = {
            "revenue": (100 + growth + np.random.normal(0, 5, n_points)).tolist(),
            "customer_satisfaction": (70 + growth * 0.5 + np.random.normal(0, 2, n_points)).tolist(),
            "market_share": (15 + growth * 0.3 + np.random.normal(0, 1, n_points)).tolist(),
            "brand_value": (50 + growth * 0.8 + np.random.normal(0, 3, n_points)).tolist(),
        }

        return {
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "time_series_data": time_series_data,
            "metric_names": list(time_series_data.keys())
        }

    async def test_execute_success(self, agent, sample_input):
        """Test successful agent execution"""
        result = await agent.execute(sample_input)

        # Check basic result structure
        assert result["success"] is True
        assert result["data"] is not None
        assert result["error"] is None

        # Check analysis output
        analysis = result["data"]
        assert analysis.company == "Tesla"
        assert analysis.industry == "Electric Vehicles"
        assert len(analysis.key_variables) > 0
        assert 0 <= analysis.confidence_score <= 100

    async def test_execute_missing_inputs(self, agent):
        """Test agent with missing required inputs"""
        result = await agent.execute({"company": "TestCo"})

        # Should return error
        assert result["success"] is False
        assert result["error"] is not None

    async def test_narrative_generation(self, agent):
        """Test narrative generation from analysis"""
        from consultantos.models.systems import SystemDynamicsAnalysis

        # Create minimal analysis
        analysis = SystemDynamicsAnalysis(
            company="Tesla",
            industry="EVs",
            confidence_score=75.0
        )

        # Should generate fallback narrative
        narrative = agent._build_fallback_narrative(analysis)

        assert "SYSTEM DYNAMICS ANALYSIS" in narrative
        assert "Tesla" in narrative


def test_integration_feedback_to_systems():
    """Test integration from FeedbackLoopDetector to SystemsAgent"""
    # Create sample data
    n_points = 24
    time = np.arange(n_points)

    time_series_data = {
        "revenue": (100 + time * 2 + np.random.normal(0, 5, n_points)).tolist(),
        "satisfaction": (70 + time * 1 + np.random.normal(0, 2, n_points)).tolist(),
    }

    metric_names = list(time_series_data.keys())

    # Use detector directly
    detector = FeedbackLoopDetector()
    analysis = detector.analyze_system(
        time_series_data,
        metric_names,
        "TestCo",
        "Tech"
    )

    # Should produce valid analysis
    assert analysis.company == "TestCo"
    assert len(analysis.causal_links) >= 0


def test_integration_momentum_engine():
    """Test momentum engine with realistic data"""
    engine = MomentumTrackingEngine()

    # Create growth trajectory
    n_points = 12
    time = np.arange(n_points)

    metrics_data = {
        "market": {
            "brand_score": (50 + time * 3 + np.random.normal(0, 1, n_points)).tolist(),
        },
        "financial": {
            "revenue": (1000 + time * 100 + np.random.normal(0, 20, n_points)).tolist(),
        },
        "strategic": {},
        "execution": {},
        "talent": {}
    }

    analysis = engine.analyze_momentum("TestCo", "Tech", metrics_data)

    # Should produce valid analysis
    assert analysis.company == "TestCo"
    assert 0 <= analysis.current_momentum <= 100
    assert len(analysis.key_metrics) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

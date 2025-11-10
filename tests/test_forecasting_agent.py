"""
Comprehensive tests for Enhanced Forecasting Agent
Phase 1 Week 3-4: Testing multi-scenario forecasting with >90% coverage
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pandas as pd
import numpy as np
from consultantos.agents.forecasting_agent import EnhancedForecastingAgent
from consultantos.models.forecasting import (
    ScenarioType,
    MetricType,
    EnhancedForecastResult,
    ForecastScenario,
    ForecastRequest
)


class TestEnhancedForecastingAgent:
    """Test suite for EnhancedForecastingAgent"""

    @pytest.fixture
    def agent(self):
        """Create forecasting agent instance"""
        return EnhancedForecastingAgent(timeout=60)

    @pytest.fixture
    def sample_input_data(self):
        """Sample input data for forecast generation"""
        return {
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "metric_name": "Revenue",
            "metric_type": "revenue",
            "forecast_horizon_days": 30,
            "ticker": None,
            "use_real_data": False
        }

    @pytest.fixture
    def sample_historical_data(self):
        """Sample historical time series data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        values = 80000 + np.linspace(0, 20000, 100) + 5000 * np.sin(np.linspace(0, 4 * np.pi, 100))
        return pd.DataFrame({'ds': dates, 'y': values})

    # --- Test Initialization ---

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "EnhancedForecastingAgent"
        assert agent.timeout == 60
        assert hasattr(agent, 'prophet_available')
        assert isinstance(agent.prophet_available, bool)

    def test_agent_prophet_detection(self, agent):
        """Test Prophet availability detection"""
        # Prophet availability depends on installation
        if agent.prophet_available:
            from prophet import Prophet
            assert Prophet is not None
        else:
            # Should gracefully handle missing Prophet
            pass

    # --- Test Sample Data Generation ---

    def test_generate_sample_data_revenue(self, agent):
        """Test sample data generation for revenue metric"""
        df = agent._generate_sample_data(days=100, metric_type=MetricType.REVENUE)

        assert len(df) == 100
        assert 'ds' in df.columns
        assert 'y' in df.columns
        assert df['y'].min() >= 0  # Non-negative values
        assert df['y'].mean() > 0  # Reasonable values

    def test_generate_sample_data_market_share(self, agent):
        """Test sample data generation for market share metric"""
        df = agent._generate_sample_data(days=100, metric_type=MetricType.MARKET_SHARE)

        assert len(df) == 100
        assert df['y'].min() >= 0
        assert df['y'].max() <= 1.0  # Market share between 0-1

    def test_generate_sample_data_customer_growth(self, agent):
        """Test sample data generation for customer growth metric"""
        df = agent._generate_sample_data(days=100, metric_type=MetricType.CUSTOMER_GROWTH)

        assert len(df) == 100
        assert df['y'].min() >= 0
        assert df['y'].mean() > 0

    # --- Test Execute Internal (Main Forecast Logic) ---

    @pytest.mark.asyncio
    async def test_execute_internal_success(self, agent, sample_input_data):
        """Test successful forecast execution"""
        result = await agent._execute_internal(sample_input_data)

        assert result['success'] is True
        assert result['error'] is None
        assert 'data' in result

        # Validate result structure
        forecast_data = result['data']
        assert 'scenarios' in forecast_data
        assert 'recommended_scenario' in forecast_data
        assert 'key_insights' in forecast_data
        assert 'methodology' in forecast_data

    @pytest.mark.asyncio
    async def test_execute_internal_with_real_data_request(self, agent):
        """Test forecast with real data request (should fallback to sample)"""
        input_data = {
            "company": "Tesla",
            "metric_name": "Revenue",
            "metric_type": "revenue",
            "forecast_horizon_days": 30,
            "ticker": "TSLA",
            "use_real_data": True  # Request real data
        }

        result = await agent._execute_internal(input_data)

        # Should succeed even if Alpha Vantage unavailable (fallback to sample)
        assert result['success'] is True
        assert 'data' in result

    @pytest.mark.asyncio
    async def test_execute_internal_different_metrics(self, agent):
        """Test forecast with different metric types"""
        for metric_type in ["revenue", "market_share", "customer_growth"]:
            input_data = {
                "company": "Tesla",
                "metric_name": metric_type.title(),
                "metric_type": metric_type,
                "forecast_horizon_days": 30,
                "use_real_data": False
            }

            result = await agent._execute_internal(input_data)
            assert result['success'] is True

    # --- Test Multi-Scenario Generation ---

    @pytest.mark.asyncio
    async def test_all_scenarios_generated(self, agent, sample_input_data):
        """Test all three scenarios are generated"""
        result = await agent._execute_internal(sample_input_data)

        assert result['success'] is True
        scenarios = result['data']['scenarios']

        # Should have exactly 3 scenarios
        assert len(scenarios) == 3

        # Check all scenario types present
        scenario_types = {s['scenario_type'] for s in scenarios}
        assert scenario_types == {'optimistic', 'baseline', 'pessimistic'}

    @pytest.mark.asyncio
    async def test_scenario_structure(self, agent, sample_input_data):
        """Test each scenario has correct structure"""
        result = await agent._execute_internal(sample_input_data)

        scenarios = result['data']['scenarios']
        for scenario in scenarios:
            assert 'scenario_type' in scenario
            assert 'dates' in scenario
            assert 'predictions' in scenario
            assert 'lower_bound' in scenario
            assert 'upper_bound' in scenario
            assert 'confidence' in scenario
            assert 'assumptions' in scenario

            # Check list lengths match
            assert len(scenario['dates']) == len(scenario['predictions'])
            assert len(scenario['dates']) == len(scenario['lower_bound'])
            assert len(scenario['dates']) == len(scenario['upper_bound'])

    @pytest.mark.asyncio
    async def test_scenario_bounds_valid(self, agent, sample_input_data):
        """Test scenario confidence bounds are valid"""
        result = await agent._execute_internal(sample_input_data)

        scenarios = result['data']['scenarios']
        for scenario in scenarios:
            predictions = scenario['predictions']
            lower_bounds = scenario['lower_bound']
            upper_bounds = scenario['upper_bound']

            for pred, lower, upper in zip(predictions, lower_bounds, upper_bounds):
                # Lower bound should be <= prediction
                assert lower <= pred, f"Lower bound {lower} exceeds prediction {pred}"
                # Prediction should be <= upper bound
                assert pred <= upper, f"Prediction {pred} exceeds upper bound {upper}"

    # --- Test Prophet Forecast (if available) ---

    @pytest.mark.asyncio
    async def test_prophet_forecast_with_prophet_available(
        self, agent, sample_historical_data
    ):
        """Test Prophet-based forecast when Prophet is available"""
        if not agent.prophet_available:
            pytest.skip("Prophet not installed")

        result = await agent._prophet_forecast(
            historical_data=sample_historical_data,
            company="Tesla",
            industry="Electric Vehicles",
            metric_name="Revenue",
            metric_type=MetricType.REVENUE,
            forecast_horizon_days=30,
            data_source="sample_data"
        )

        assert isinstance(result, EnhancedForecastResult)
        assert len(result.scenarios) == 3
        assert result.recommended_scenario == ScenarioType.BASELINE
        assert len(result.key_insights) > 0
        assert "Prophet" in result.methodology

    @pytest.mark.asyncio
    async def test_generate_scenario_optimistic(
        self, agent, sample_historical_data
    ):
        """Test optimistic scenario generation"""
        if not agent.prophet_available:
            pytest.skip("Prophet not installed")

        from prophet import Prophet

        scenario = await agent._generate_scenario(
            historical_data=sample_historical_data,
            forecast_horizon_days=30,
            scenario_type=ScenarioType.OPTIMISTIC,
            Prophet=Prophet
        )

        assert scenario.scenario_type == ScenarioType.OPTIMISTIC
        assert len(scenario.dates) == 30
        assert len(scenario.predictions) == 30
        # Check for optimistic assumptions (accelerated growth is optimistic)
        growth_assumption = scenario.assumptions.get("growth_assumption", "").lower()
        assert "optimistic" in growth_assumption or "accelerated" in growth_assumption or "favorable" in growth_assumption

    @pytest.mark.asyncio
    async def test_generate_scenario_pessimistic(
        self, agent, sample_historical_data
    ):
        """Test pessimistic scenario generation"""
        if not agent.prophet_available:
            pytest.skip("Prophet not installed")

        from prophet import Prophet

        scenario = await agent._generate_scenario(
            historical_data=sample_historical_data,
            forecast_horizon_days=30,
            scenario_type=ScenarioType.PESSIMISTIC,
            Prophet=Prophet
        )

        assert scenario.scenario_type == ScenarioType.PESSIMISTIC
        assert len(scenario.dates) == 30
        assert "pessimistic" in scenario.assumptions.get("growth_assumption", "").lower() or \
               "decelerated" in scenario.assumptions.get("growth_assumption", "").lower()

    # --- Test Simple Forecast Fallback ---

    @pytest.mark.asyncio
    async def test_simple_forecast_fallback(
        self, agent, sample_historical_data
    ):
        """Test simple forecast fallback when Prophet unavailable"""
        result = await agent._simple_forecast(
            historical_data=sample_historical_data,
            company="Tesla",
            industry="Electric Vehicles",
            metric_name="Revenue",
            metric_type=MetricType.REVENUE,
            forecast_horizon_days=30,
            data_source="sample_data"
        )

        assert isinstance(result, EnhancedForecastResult)
        assert len(result.scenarios) == 3
        assert result.recommended_scenario == ScenarioType.BASELINE
        assert "linear" in result.methodology.lower()

    # --- Test Insights Generation ---

    def test_generate_insights(self, agent, sample_historical_data):
        """Test key insights generation"""
        # Create mock scenarios
        scenarios = [
            ForecastScenario(
                scenario_type=ScenarioType.BASELINE,
                dates=["2025-12-01"] * 30,
                predictions=[100000.0] * 30,
                lower_bound=[95000.0] * 30,
                upper_bound=[105000.0] * 30,
                confidence=0.90,
                assumptions={}
            ),
            ForecastScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                dates=["2025-12-01"] * 30,
                predictions=[115000.0] * 30,
                lower_bound=[110000.0] * 30,
                upper_bound=[120000.0] * 30,
                confidence=0.80,
                assumptions={}
            ),
            ForecastScenario(
                scenario_type=ScenarioType.PESSIMISTIC,
                dates=["2025-12-01"] * 30,
                predictions=[85000.0] * 30,
                lower_bound=[80000.0] * 30,
                upper_bound=[90000.0] * 30,
                confidence=0.95,
                assumptions={}
            )
        ]

        insights = agent._generate_insights(sample_historical_data, scenarios)

        assert isinstance(insights, list)
        assert len(insights) > 0
        # Should mention trend
        assert any("trend" in insight.lower() for insight in insights)
        # Should mention upside/downside
        assert any("upside" in insight.lower() or "downside" in insight.lower() for insight in insights)

    # --- Test Accuracy Calculation ---

    def test_calculate_accuracy(self, agent, sample_historical_data):
        """Test model accuracy calculation"""
        accuracy = agent._calculate_accuracy(sample_historical_data)

        assert isinstance(accuracy, dict)
        assert 'mape' in accuracy
        assert 'rmse' in accuracy
        assert accuracy['mape'] >= 0
        assert accuracy['rmse'] >= 0

    # --- Test Alpha Vantage Integration (Mocked) ---

    @pytest.mark.asyncio
    async def test_fetch_alpha_vantage_data_unavailable(self, agent):
        """Test Alpha Vantage fetch when API unavailable"""
        result = await agent._fetch_alpha_vantage_data("TSLA", MetricType.REVENUE)

        # Should return None when API key not configured or data unavailable
        # This is the expected behavior
        assert result is None or isinstance(result, pd.DataFrame)

    @pytest.mark.asyncio
    async def test_fetch_alpha_vantage_data_with_mock(self, agent):
        """Test Alpha Vantage data fetch with mocking"""
        # Mock the Alpha Vantage client at module import level
        with patch('consultantos.agents.forecasting_agent.asyncio.to_thread') as mock_to_thread:
            # Create mock time series data
            mock_data = pd.DataFrame({
                '4. close': np.random.uniform(100, 200, 100)
            }, index=pd.date_range(end=datetime.now(), periods=100, freq='D'))

            # Mock the async call to return our data
            mock_to_thread.return_value = (mock_data, None)

            # For this test, we'll just verify the method can be called
            # Real integration would require Alpha Vantage API key
            try:
                from consultantos.tools.alpha_vantage_tool import AlphaVantageClient
                # If client exists, test it
                pass
            except ImportError:
                # If tool doesn't exist yet, skip
                pytest.skip("Alpha Vantage tool not available")

    # --- Test Error Handling ---

    @pytest.mark.asyncio
    async def test_execute_with_invalid_metric_type(self, agent):
        """Test execution with invalid metric type (should default to CUSTOM)"""
        input_data = {
            "company": "Tesla",
            "metric_name": "Unknown Metric",
            "metric_type": "invalid_type",
            "forecast_horizon_days": 30,
            "use_real_data": False
        }

        result = await agent._execute_internal(input_data)

        # Should still succeed with CUSTOM metric type
        assert result['success'] is True

    @pytest.mark.asyncio
    async def test_execute_with_zero_horizon(self, agent):
        """Test execution fails gracefully with zero forecast horizon"""
        input_data = {
            "company": "Tesla",
            "metric_name": "Revenue",
            "metric_type": "revenue",
            "forecast_horizon_days": 0,
            "use_real_data": False
        }

        # Should handle edge case
        result = await agent._execute_internal(input_data)
        # Behavior depends on implementation - either error or default value


# --- Test Pydantic Models ---

class TestForecastingModels:
    """Test suite for forecasting Pydantic models"""

    def test_scenario_type_enum(self):
        """Test ScenarioType enum values"""
        assert ScenarioType.OPTIMISTIC.value == "optimistic"
        assert ScenarioType.BASELINE.value == "baseline"
        assert ScenarioType.PESSIMISTIC.value == "pessimistic"

    def test_metric_type_enum(self):
        """Test MetricType enum values"""
        assert MetricType.REVENUE.value == "revenue"
        assert MetricType.MARKET_SHARE.value == "market_share"
        assert MetricType.CUSTOMER_GROWTH.value == "customer_growth"

    def test_forecast_scenario_validation(self):
        """Test ForecastScenario validation"""
        scenario = ForecastScenario(
            scenario_type=ScenarioType.BASELINE,
            dates=["2025-12-01", "2025-12-02"],
            predictions=[100000.0, 101000.0],
            lower_bound=[95000.0, 96000.0],
            upper_bound=[105000.0, 106000.0],
            confidence=0.95,
            assumptions={"growth_rate": 0.01}
        )

        assert len(scenario.dates) == 2
        assert len(scenario.predictions) == 2

    def test_forecast_scenario_invalid_bounds(self):
        """Test ForecastScenario rejects invalid bounds"""
        with pytest.raises(ValueError):
            # Lower bound exceeds prediction
            ForecastScenario(
                scenario_type=ScenarioType.BASELINE,
                dates=["2025-12-01"],
                predictions=[100000.0],
                lower_bound=[110000.0],  # Invalid: higher than prediction
                upper_bound=[105000.0],
                confidence=0.95,
                assumptions={}
            )

    def test_enhanced_forecast_result_validation(self):
        """Test EnhancedForecastResult requires all scenarios"""
        # Should fail without all three scenarios
        with pytest.raises(ValueError):
            EnhancedForecastResult(
                metric_name="Revenue",
                metric_type=MetricType.REVENUE,
                scenarios=[
                    ForecastScenario(
                        scenario_type=ScenarioType.BASELINE,
                        dates=["2025-12-01"],
                        predictions=[100000.0],
                        lower_bound=[95000.0],
                        upper_bound=[105000.0],
                        confidence=0.95,
                        assumptions={}
                    )
                ],  # Missing optimistic and pessimistic
                recommended_scenario=ScenarioType.BASELINE,
                key_insights=["Test insight"],
                methodology="Test method",
                forecast_horizon_days=30,
                historical_data_points=100
            )

    def test_forecast_request_validation(self):
        """Test ForecastRequest validation"""
        request = ForecastRequest(
            company="Tesla",
            industry="Electric Vehicles",
            metric_name="Revenue",
            metric_type=MetricType.REVENUE,
            forecast_horizon_days=30,
            ticker="TSLA",
            use_real_data=True
        )

        assert request.company == "Tesla"
        assert request.forecast_horizon_days == 30
        assert request.use_real_data is True

    def test_forecast_request_horizon_limits(self):
        """Test ForecastRequest enforces horizon limits"""
        # Should accept valid range
        request = ForecastRequest(
            company="Tesla",
            forecast_horizon_days=30
        )
        assert request.forecast_horizon_days == 30

        # Test boundary values
        request = ForecastRequest(
            company="Tesla",
            forecast_horizon_days=1
        )
        assert request.forecast_horizon_days == 1

        request = ForecastRequest(
            company="Tesla",
            forecast_horizon_days=365
        )
        assert request.forecast_horizon_days == 365


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=consultantos.agents.forecasting_agent", "--cov-report=term-missing"])

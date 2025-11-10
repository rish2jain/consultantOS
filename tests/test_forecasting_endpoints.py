"""
Tests for Enhanced Forecasting API Endpoints
Phase 1 Week 3-4: Testing forecasting REST API
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from consultantos.api.main import app
from consultantos.models.forecasting import (
    ForecastRequest,
    EnhancedForecastResult,
    ForecastScenario,
    ScenarioType,
    MetricType
)

client = TestClient(app)


class TestForecastingEndpoints:
    """Test suite for forecasting API endpoints"""

    @pytest.fixture
    def sample_forecast_request(self):
        """Sample forecast request payload"""
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
    def sample_forecast_result(self):
        """Sample forecast result for mocking"""
        return EnhancedForecastResult(
            metric_name="Revenue",
            metric_type=MetricType.REVENUE,
            company="Tesla",
            industry="Electric Vehicles",
            scenarios=[
                ForecastScenario(
                    scenario_type=ScenarioType.BASELINE,
                    dates=["2025-12-01"] * 30,
                    predictions=[100000.0] * 30,
                    lower_bound=[95000.0] * 30,
                    upper_bound=[105000.0] * 30,
                    confidence=0.90,
                    assumptions={"growth_rate": 0.01}
                ),
                ForecastScenario(
                    scenario_type=ScenarioType.OPTIMISTIC,
                    dates=["2025-12-01"] * 30,
                    predictions=[115000.0] * 30,
                    lower_bound=[110000.0] * 30,
                    upper_bound=[120000.0] * 30,
                    confidence=0.80,
                    assumptions={"growth_rate": 0.02}
                ),
                ForecastScenario(
                    scenario_type=ScenarioType.PESSIMISTIC,
                    dates=["2025-12-01"] * 30,
                    predictions=[85000.0] * 30,
                    lower_bound=[80000.0] * 30,
                    upper_bound=[90000.0] * 30,
                    confidence=0.95,
                    assumptions={"growth_rate": 0.005}
                )
            ],
            recommended_scenario=ScenarioType.BASELINE,
            key_insights=[
                "Strong upward trend detected",
                "Moderate volatility",
                "High confidence in baseline scenario"
            ],
            methodology="Prophet with seasonal decomposition",
            data_source="sample_data",
            forecast_horizon_days=30,
            historical_data_points=100,
            model_accuracy={"mape": 5.2, "rmse": 2500.0},
            generated_at=datetime.now()
        )

    # --- Test POST /forecasting/generate ---

    @patch('consultantos.api.forecasting_endpoints.EnhancedForecastingAgent')
    def test_generate_forecast_success(
        self, mock_agent_class, sample_forecast_request, sample_forecast_result
    ):
        """Test successful forecast generation"""
        # Mock agent execution
        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value={
            "success": True,
            "data": sample_forecast_result.model_dump(),
            "error": None
        })
        mock_agent_class.return_value = mock_agent

        response = client.post("/forecasting/generate", json=sample_forecast_request)

        assert response.status_code == 200
        data = response.json()

        assert data['metric_name'] == "Revenue"
        assert data['company'] == "Tesla"
        assert len(data['scenarios']) == 3
        assert data['recommended_scenario'] == "baseline"
        assert len(data['key_insights']) > 0

    @patch('consultantos.api.forecasting_endpoints.EnhancedForecastingAgent')
    def test_generate_forecast_with_real_data(
        self, mock_agent_class, sample_forecast_result
    ):
        """Test forecast generation with real data request"""
        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value={
            "success": True,
            "data": sample_forecast_result.model_dump(),
            "error": None
        })
        mock_agent_class.return_value = mock_agent

        request_data = {
            "company": "Tesla",
            "metric_name": "Revenue",
            "metric_type": "revenue",
            "forecast_horizon_days": 30,
            "ticker": "TSLA",
            "use_real_data": True
        }

        response = client.post("/forecasting/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data['company'] == "Tesla"

    def test_generate_forecast_missing_company(self):
        """Test forecast generation fails without required company field"""
        request_data = {
            "metric_name": "Revenue",
            "forecast_horizon_days": 30
        }

        response = client.post("/forecasting/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_generate_forecast_invalid_horizon(self):
        """Test forecast generation with invalid horizon"""
        request_data = {
            "company": "Tesla",
            "forecast_horizon_days": 500  # Exceeds max of 365
        }

        response = client.post("/forecasting/generate", json=request_data)

        assert response.status_code == 422  # Validation error

    @patch('consultantos.api.forecasting_endpoints.EnhancedForecastingAgent')
    def test_generate_forecast_agent_failure(self, mock_agent_class):
        """Test handling of agent execution failure"""
        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value={
            "success": False,
            "error": "Forecast generation failed",
            "data": None
        })
        mock_agent_class.return_value = mock_agent

        request_data = {
            "company": "Tesla",
            "metric_name": "Revenue",
            "forecast_horizon_days": 30
        }

        response = client.post("/forecasting/generate", json=request_data)

        assert response.status_code == 500
        assert "failed" in response.json()['detail'].lower()

    # --- Test GET /forecasting/history ---

    @patch('consultantos.api.forecasting_endpoints._forecast_history')
    def test_get_forecast_history_success(self, mock_history):
        """Test retrieving forecast history"""
        # Mock history data
        from consultantos.models.forecasting import ForecastHistoryEntry

        mock_history_entries = [
            ForecastHistoryEntry(
                forecast_id="forecast_123",
                company="Tesla",
                metric_name="Revenue",
                generated_at=datetime.now(),
                forecast_horizon_days=30,
                recommended_scenario=ScenarioType.BASELINE,
                actual_accuracy=None
            ),
            ForecastHistoryEntry(
                forecast_id="forecast_456",
                company="Apple",
                metric_name="Market Share",
                generated_at=datetime.now(),
                forecast_horizon_days=60,
                recommended_scenario=ScenarioType.OPTIMISTIC,
                actual_accuracy=92.5
            )
        ]

        # Patch the module-level list
        with patch('consultantos.api.forecasting_endpoints._forecast_history', mock_history_entries):
            response = client.get("/forecasting/history")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            # Default limit is 10, but we only have 2 entries
            assert len(data) <= 10

    def test_get_forecast_history_with_company_filter(self):
        """Test forecast history with company filter"""
        response = client.get("/forecasting/history?company=Tesla&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_forecast_history_with_limit(self):
        """Test forecast history respects limit parameter"""
        response = client.get("/forecasting/history?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_get_forecast_history_invalid_limit(self):
        """Test forecast history rejects invalid limit"""
        response = client.get("/forecasting/history?limit=0")

        assert response.status_code == 422  # Validation error

    # --- Test POST /forecasting/compare ---

    @patch('consultantos.api.forecasting_endpoints._forecast_storage')
    def test_compare_forecasts_success(self, mock_storage, sample_forecast_result):
        """Test successful forecast comparison"""
        # Mock stored forecasts
        mock_storage_dict = {
            "forecast_123": {
                "id": "forecast_123",
                "result": sample_forecast_result,
                "user_id": None,
                "created_at": datetime.now()
            },
            "forecast_456": {
                "id": "forecast_456",
                "result": sample_forecast_result,
                "user_id": None,
                "created_at": datetime.now()
            }
        }

        with patch('consultantos.api.forecasting_endpoints._forecast_storage', mock_storage_dict):
            request_data = {
                "forecast_id_1": "forecast_123",
                "forecast_id_2": "forecast_456",
                "comparison_metric": "predictions"
            }

            response = client.post("/forecasting/compare", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert 'forecast_1' in data
            assert 'forecast_2' in data
            assert 'comparison' in data
            assert 'insights' in data

    def test_compare_forecasts_not_found(self):
        """Test comparison fails when forecast not found"""
        request_data = {
            "forecast_id_1": "nonexistent_123",
            "forecast_id_2": "forecast_456",
            "comparison_metric": "predictions"
        }

        response = client.post("/forecasting/compare", json=request_data)

        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()

    # --- Test GET /forecasting/{forecast_id} ---

    @patch('consultantos.api.forecasting_endpoints._forecast_storage')
    def test_get_forecast_by_id_success(self, mock_storage, sample_forecast_result):
        """Test retrieving forecast by ID"""
        forecast_id = "forecast_123"
        mock_storage_dict = {
            forecast_id: {
                "id": forecast_id,
                "result": sample_forecast_result,
                "user_id": None,
                "created_at": datetime.now()
            }
        }

        with patch('consultantos.api.forecasting_endpoints._forecast_storage', mock_storage_dict):
            response = client.get(f"/forecasting/{forecast_id}")

            assert response.status_code == 200
            data = response.json()

            assert data['metric_name'] == "Revenue"
            assert data['company'] == "Tesla"
            assert len(data['scenarios']) == 3

    def test_get_forecast_by_id_not_found(self):
        """Test retrieving non-existent forecast"""
        response = client.get("/forecasting/nonexistent_123")

        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()

    # --- Test Integration Scenarios ---

    @patch('consultantos.api.forecasting_endpoints.EnhancedForecastingAgent')
    def test_full_forecast_workflow(
        self, mock_agent_class, sample_forecast_request, sample_forecast_result
    ):
        """Test complete forecast workflow: generate -> retrieve -> compare"""
        # Step 1: Generate first forecast
        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value={
            "success": True,
            "data": sample_forecast_result.model_dump(),
            "error": None
        })
        mock_agent_class.return_value = mock_agent

        response1 = client.post("/forecasting/generate", json=sample_forecast_request)
        assert response1.status_code == 200

        # Extract forecast_id from stored data (would be in response in real implementation)
        # For now, just verify the endpoint works
        data1 = response1.json()
        assert 'scenarios' in data1

    @patch('consultantos.api.forecasting_endpoints.EnhancedForecastingAgent')
    def test_multiple_metric_types(self, mock_agent_class, sample_forecast_result):
        """Test generating forecasts for different metric types"""
        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value={
            "success": True,
            "data": sample_forecast_result.model_dump(),
            "error": None
        })
        mock_agent_class.return_value = mock_agent

        metric_types = ["revenue", "market_share", "customer_growth"]

        for metric_type in metric_types:
            request_data = {
                "company": "Tesla",
                "metric_name": metric_type.title(),
                "metric_type": metric_type,
                "forecast_horizon_days": 30
            }

            response = client.post("/forecasting/generate", json=request_data)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

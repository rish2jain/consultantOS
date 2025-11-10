"""
Tests for MVP agents
"""
import pytest
from datetime import datetime
from consultantos.agents.conversational_agent_mvp import ConversationalAgentMVP
from consultantos.agents.forecasting_agent_mvp import ForecastingAgentMVP
from consultantos.models.mvp import ChatResponse, ForecastResult


@pytest.mark.asyncio
async def test_conversational_agent_basic_query():
    """Test conversational agent with basic query"""
    agent = ConversationalAgentMVP(timeout=30)

    result = await agent.execute({
        "query": "What is competitive strategy?",
        "conversation_id": "test_conv_1"
    })

    assert result["success"] is True
    assert result["data"] is not None
    assert "response" in result["data"]
    assert "conversation_id" in result["data"]
    assert result["data"]["conversation_id"] == "test_conv_1"

    # Validate response structure
    chat_response = ChatResponse(**result["data"])
    assert isinstance(chat_response.response, str)
    assert len(chat_response.response) > 0
    assert chat_response.conversation_id == "test_conv_1"


@pytest.mark.asyncio
async def test_conversational_agent_empty_query():
    """Test conversational agent with empty query"""
    agent = ConversationalAgentMVP(timeout=30)

    result = await agent.execute({
        "query": "",
        "conversation_id": "test_conv_empty"
    })

    assert result["success"] is False
    assert "error" in result
    assert result["error"] == "Query is required"


@pytest.mark.asyncio
async def test_conversational_agent_conversation_history():
    """Test conversational agent maintains conversation history"""
    agent = ConversationalAgentMVP(timeout=30)

    # First query
    result1 = await agent.execute({
        "query": "What is SWOT analysis?",
        "conversation_id": "test_conv_history"
    })
    assert result1["success"] is True

    # Second query in same conversation
    result2 = await agent.execute({
        "query": "Can you give me an example?",
        "conversation_id": "test_conv_history"
    })
    assert result2["success"] is True

    # Verify conversation history is maintained
    assert "test_conv_history" in agent.conversation_history
    assert len(agent.conversation_history["test_conv_history"]) == 2


@pytest.mark.asyncio
async def test_forecasting_agent_basic_forecast():
    """Test forecasting agent with basic parameters"""
    agent = ForecastingAgentMVP(timeout=30)

    result = await agent.execute({
        "metric_name": "Revenue",
        "periods": 30
    })

    assert result["success"] is True
    assert result["data"] is not None

    # Validate forecast structure
    forecast = ForecastResult(**result["data"])
    assert forecast.metric_name == "Revenue"
    assert len(forecast.predictions) == 30
    assert forecast.confidence_level > 0

    # Validate first prediction
    first_pred = forecast.predictions[0]
    assert hasattr(first_pred, 'date')
    assert hasattr(first_pred, 'value')
    assert hasattr(first_pred, 'lower_bound')
    assert hasattr(first_pred, 'upper_bound')
    assert first_pred.lower_bound <= first_pred.value <= first_pred.upper_bound


@pytest.mark.asyncio
async def test_forecasting_agent_custom_periods():
    """Test forecasting agent with custom periods"""
    agent = ForecastingAgentMVP(timeout=30)

    result = await agent.execute({
        "metric_name": "Sales",
        "periods": 7
    })

    assert result["success"] is True
    forecast = ForecastResult(**result["data"])
    assert len(forecast.predictions) == 7
    assert forecast.metric_name == "Sales"


@pytest.mark.asyncio
async def test_forecasting_agent_prediction_values():
    """Test forecasting agent prediction values are reasonable"""
    agent = ForecastingAgentMVP(timeout=30)

    result = await agent.execute({
        "metric_name": "Revenue",
        "periods": 10
    })

    assert result["success"] is True
    forecast = ForecastResult(**result["data"])

    for pred in forecast.predictions:
        # Values should be non-negative
        assert pred.value >= 0
        assert pred.lower_bound >= 0
        assert pred.upper_bound >= 0

        # Confidence intervals should be valid
        assert pred.lower_bound <= pred.value <= pred.upper_bound

        # Date format should be valid
        date_obj = datetime.strptime(pred.date, '%Y-%m-%d')
        assert date_obj is not None


@pytest.mark.asyncio
async def test_forecasting_agent_sample_data_generation():
    """Test sample data generation is consistent"""
    agent = ForecastingAgentMVP(timeout=30)

    # Generate sample data
    data = agent._generate_sample_data(days=100)

    assert "dates" in data
    assert "values" in data
    assert len(data["dates"]) == 100
    assert len(data["values"]) == 100

    # All values should be non-negative
    assert all(v >= 0 for v in data["values"])

    # Dates should be in chronological order
    for i in range(len(data["dates"]) - 1):
        assert data["dates"][i] < data["dates"][i + 1]


@pytest.mark.asyncio
async def test_conversational_agent_timeout():
    """Test conversational agent respects timeout"""
    agent = ConversationalAgentMVP(timeout=1)

    # This should complete within timeout
    result = await agent.execute({
        "query": "Hi",
        "conversation_id": "test_timeout"
    })

    # Should succeed with short query
    assert result["success"] is True


def test_chat_response_model():
    """Test ChatResponse model validation"""
    response = ChatResponse(
        response="Test response",
        conversation_id="conv_123",
        timestamp=datetime.now()
    )

    assert response.response == "Test response"
    assert response.conversation_id == "conv_123"
    assert isinstance(response.timestamp, datetime)


def test_forecast_result_model():
    """Test ForecastResult model validation"""
    from consultantos.models.mvp import ForecastPrediction

    predictions = [
        ForecastPrediction(
            date="2025-12-01",
            value=100000.0,
            lower_bound=95000.0,
            upper_bound=105000.0
        )
    ]

    result = ForecastResult(
        metric_name="Revenue",
        predictions=predictions,
        confidence_level=0.95,
        generated_at=datetime.now()
    )

    assert result.metric_name == "Revenue"
    assert len(result.predictions) == 1
    assert result.confidence_level == 0.95
    assert result.predictions[0].value == 100000.0

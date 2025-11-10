"""
MVP API Endpoints for Hackathon Demo
Conversational AI and Forecasting features
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from consultantos.models.mvp import ChatRequest, ChatResponse, ForecastResult
from consultantos.agents.conversational_agent_mvp import ConversationalAgentMVP
from consultantos.agents.forecasting_agent_mvp import ForecastingAgentMVP

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mvp", tags=["mvp"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Conversational AI endpoint for business intelligence queries

    **Example Request:**
    ```json
    {
        "query": "What are Tesla's competitive advantages?",
        "conversation_id": "conv_123"
    }
    ```

    **Example Response:**
    ```json
    {
        "response": "Based on analysis, Tesla's key competitive advantages include...",
        "conversation_id": "conv_123",
        "timestamp": "2025-11-09T12:00:00"
    }
    ```
    """
    try:
        agent = ConversationalAgentMVP(timeout=30)

        result = await agent.execute({
            "query": request.query,
            "conversation_id": request.conversation_id
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Chat failed: {result.get('error', 'Unknown error')}"
            )

        # Return ChatResponse
        data = result.get("data", {})
        return ChatResponse(**data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/forecast", response_model=ForecastResult)
async def forecast_endpoint(
    metric_name: str = "Revenue",
    periods: int = 30
):
    """
    Time series forecasting endpoint using Prophet

    **Parameters:**
    - `metric_name`: Name of metric to forecast (default: Revenue)
    - `periods`: Number of days to forecast (default: 30)

    **Example Request:**
    ```
    GET /mvp/forecast?metric_name=Revenue&periods=30
    ```

    **Example Response:**
    ```json
    {
        "metric_name": "Revenue",
        "predictions": [
            {
                "date": "2025-12-01",
                "value": 100000.0,
                "lower_bound": 95000.0,
                "upper_bound": 105000.0
            }
        ],
        "confidence_level": 0.95,
        "generated_at": "2025-11-09T12:00:00"
    }
    ```
    """
    try:
        # Validate parameters
        if periods < 1 or periods > 365:
            raise HTTPException(
                status_code=400,
                detail="Periods must be between 1 and 365 days"
            )

        agent = ForecastingAgentMVP(timeout=30)

        result = await agent.execute({
            "metric_name": metric_name,
            "periods": periods
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Forecast failed: {result.get('error', 'Unknown error')}"
            )

        # Return ForecastResult
        data = result.get("data", {})
        return ForecastResult(**data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("/health")
async def mvp_health_check():
    """
    MVP health check endpoint

    **Example Response:**
    ```json
    {
        "status": "healthy",
        "features": ["conversational_ai", "forecasting"],
        "agents": {
            "conversational": "ready",
            "forecasting": "ready"
        }
    }
    ```
    """
    try:
        # Test agent initialization
        conversational_status = "ready"
        forecasting_status = "ready"

        try:
            _ = ConversationalAgentMVP(timeout=5)
        except Exception as e:
            logger.warning(f"Conversational agent initialization failed: {e}")
            conversational_status = "unavailable"

        try:
            _ = ForecastingAgentMVP(timeout=5)
        except Exception as e:
            logger.warning(f"Forecasting agent initialization failed: {e}")
            forecasting_status = "unavailable"

        return {
            "status": "healthy",
            "features": ["conversational_ai", "forecasting"],
            "agents": {
                "conversational": conversational_status,
                "forecasting": forecasting_status
            },
            "message": "MVP endpoints operational"
        }

    except Exception as e:
        logger.error(f"MVP health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

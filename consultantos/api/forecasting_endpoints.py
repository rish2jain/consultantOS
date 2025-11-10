"""
Forecasting API endpoints for enhanced multi-scenario forecasting
Phase 1 Week 3-4: Enhanced Forecasting Agent endpoints
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from consultantos.models.forecasting import (
    ForecastRequest,
    EnhancedForecastResult,
    ForecastComparisonRequest,
    ForecastHistoryEntry,
    ScenarioType
)
from consultantos.agents.forecasting_agent import EnhancedForecastingAgent
from consultantos.auth import get_optional_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forecasting", tags=["forecasting"])

# In-memory storage for demo (replace with Firestore in production)
_forecast_storage: dict = {}
_forecast_history: List[ForecastHistoryEntry] = []


@router.post("/generate", response_model=EnhancedForecastResult)
async def generate_forecast(
    request: ForecastRequest,
    user_id: Optional[str] = Depends(get_optional_user_id)
) -> EnhancedForecastResult:
    """
    Generate multi-scenario forecast with optimistic/baseline/pessimistic scenarios

    **Key Features:**
    - Prophet-based time series forecasting with seasonal decomposition
    - Three scenario types: optimistic, baseline, pessimistic
    - Optional Alpha Vantage integration for real financial data
    - Fallback to sample data when real data unavailable
    - Support for multiple metrics: revenue, market share, customer growth

    **Args:**
    - company: Company name (required)
    - industry: Industry context (optional)
    - metric_name: Name of metric to forecast (default: "Revenue")
    - metric_type: Type of metric (revenue/market_share/customer_growth/custom)
    - forecast_horizon_days: Number of days to forecast (1-365, default: 30)
    - ticker: Stock ticker for real data (optional)
    - use_real_data: Whether to use real financial data if available (default: False)

    **Returns:**
    - EnhancedForecastResult with three scenarios, insights, and recommendations
    """
    try:
        # Initialize forecasting agent
        agent = EnhancedForecastingAgent(timeout=60)

        # Prepare input data
        input_data = {
            "company": request.company,
            "industry": request.industry,
            "metric_name": request.metric_name,
            "metric_type": request.metric_type.value,
            "forecast_horizon_days": request.forecast_horizon_days,
            "ticker": request.ticker,
            "use_real_data": request.use_real_data
        }

        # Execute forecast generation
        result = await agent.execute(input_data)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Forecast generation failed: {result.get('error', 'Unknown error')}"
            )

        # Parse result
        forecast_data = result["data"]
        forecast_result = EnhancedForecastResult(**forecast_data)

        # Generate forecast ID and store
        forecast_id = f"forecast_{uuid.uuid4().hex[:12]}"
        _forecast_storage[forecast_id] = {
            "id": forecast_id,
            "result": forecast_result,
            "user_id": user_id,
            "created_at": datetime.now()
        }

        # Add to history
        history_entry = ForecastHistoryEntry(
            forecast_id=forecast_id,
            company=request.company,
            metric_name=request.metric_name,
            generated_at=forecast_result.generated_at,
            forecast_horizon_days=request.forecast_horizon_days,
            recommended_scenario=forecast_result.recommended_scenario,
            actual_accuracy=None  # Will be updated later when actual data available
        )
        _forecast_history.append(history_entry)

        logger.info(
            f"Forecast generated successfully",
            extra={
                "forecast_id": forecast_id,
                "company": request.company,
                "metric": request.metric_name,
                "user_id": user_id
            }
        )

        return forecast_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.get("/history", response_model=List[ForecastHistoryEntry])
async def get_forecast_history(
    user_id: Optional[str] = Depends(get_optional_user_id),
    company: Optional[str] = Query(None, description="Filter by company"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
) -> List[ForecastHistoryEntry]:
    """
    Get historical forecast accuracy and tracking

    **Features:**
    - View past forecasts with accuracy metrics
    - Filter by company
    - Track forecast performance over time

    **Args:**
    - company: Optional company filter
    - limit: Maximum number of results (1-100, default: 10)

    **Returns:**
    - List of ForecastHistoryEntry objects with forecast metadata
    """
    try:
        # Filter history
        filtered_history = _forecast_history

        # Filter by user if authenticated (for multi-tenant support)
        if user_id:
            filtered_history = [
                entry for entry in filtered_history
                if _forecast_storage.get(entry.forecast_id, {}).get("user_id") == user_id
            ]

        # Filter by company if provided
        if company:
            filtered_history = [
                entry for entry in filtered_history
                if entry.company.lower() == company.lower()
            ]

        # Sort by generated_at descending (most recent first)
        filtered_history = sorted(
            filtered_history,
            key=lambda x: x.generated_at,
            reverse=True
        )

        # Apply limit
        return filtered_history[:limit]

    except Exception as e:
        logger.error(f"Failed to retrieve forecast history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve forecast history: {str(e)}"
        )


@router.post("/compare")
async def compare_forecasts(
    request: ForecastComparisonRequest,
    user_id: Optional[str] = Depends(get_optional_user_id)
) -> dict:
    """
    Compare two forecast scenarios for analysis

    **Features:**
    - Side-by-side comparison of forecasts
    - Scenario-level comparison
    - Difference analysis and insights

    **Args:**
    - forecast_id_1: First forecast ID
    - forecast_id_2: Second forecast ID
    - comparison_metric: Metric to compare (default: "predictions")

    **Returns:**
    - Comparison analysis with differences and insights
    """
    try:
        # Retrieve forecasts
        forecast_1 = _forecast_storage.get(request.forecast_id_1)
        forecast_2 = _forecast_storage.get(request.forecast_id_2)

        if not forecast_1:
            raise HTTPException(
                status_code=404,
                detail=f"Forecast {request.forecast_id_1} not found"
            )

        if not forecast_2:
            raise HTTPException(
                status_code=404,
                detail=f"Forecast {request.forecast_id_2} not found"
            )

        # Check user permissions (optional - for multi-tenant)
        if user_id:
            if forecast_1.get("user_id") != user_id or forecast_2.get("user_id") != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to compare these forecasts"
                )

        # Get forecast results
        result_1: EnhancedForecastResult = forecast_1["result"]
        result_2: EnhancedForecastResult = forecast_2["result"]

        # Compare baseline scenarios
        baseline_1 = next(
            s for s in result_1.scenarios
            if s.scenario_type == ScenarioType.BASELINE
        )
        baseline_2 = next(
            s for s in result_2.scenarios
            if s.scenario_type == ScenarioType.BASELINE
        )

        # Calculate differences
        import numpy as np
        avg_pred_1 = np.mean(baseline_1.predictions)
        avg_pred_2 = np.mean(baseline_2.predictions)
        difference = avg_pred_2 - avg_pred_1
        percent_change = (difference / avg_pred_1 * 100) if avg_pred_1 > 0 else 0

        # Build comparison response
        comparison = {
            "forecast_1": {
                "id": request.forecast_id_1,
                "company": result_1.company,
                "metric": result_1.metric_name,
                "generated_at": result_1.generated_at.isoformat(),
                "average_prediction": float(avg_pred_1),
                "recommended_scenario": result_1.recommended_scenario.value
            },
            "forecast_2": {
                "id": request.forecast_id_2,
                "company": result_2.company,
                "metric": result_2.metric_name,
                "generated_at": result_2.generated_at.isoformat(),
                "average_prediction": float(avg_pred_2),
                "recommended_scenario": result_2.recommended_scenario.value
            },
            "comparison": {
                "absolute_difference": float(difference),
                "percent_change": float(percent_change),
                "comparison_metric": request.comparison_metric
            },
            "insights": [
                f"Forecast 2 {'higher' if difference > 0 else 'lower'} than Forecast 1 by {abs(percent_change):.1f}%",
                f"Average prediction difference: {abs(difference):.2f}",
                f"Both forecasts recommend {result_1.recommended_scenario.value} scenario"
                if result_1.recommended_scenario == result_2.recommended_scenario
                else f"Different recommendations: {result_1.recommended_scenario.value} vs {result_2.recommended_scenario.value}"
            ]
        }

        logger.info(
            f"Forecast comparison completed",
            extra={
                "forecast_1": request.forecast_id_1,
                "forecast_2": request.forecast_id_2,
                "user_id": user_id
            }
        )

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast comparison failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare forecasts: {str(e)}"
        )


@router.get("/{forecast_id}", response_model=EnhancedForecastResult)
async def get_forecast(
    forecast_id: str,
    user_id: Optional[str] = Depends(get_optional_user_id)
) -> EnhancedForecastResult:
    """
    Retrieve a specific forecast by ID

    **Args:**
    - forecast_id: Forecast identifier

    **Returns:**
    - EnhancedForecastResult object
    """
    try:
        forecast = _forecast_storage.get(forecast_id)

        if not forecast:
            raise HTTPException(
                status_code=404,
                detail=f"Forecast {forecast_id} not found"
            )

        # Check user permissions (optional - for multi-tenant)
        if user_id and forecast.get("user_id") != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this forecast"
            )

        return forecast["result"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve forecast {forecast_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve forecast: {str(e)}"
        )

"""
Forecasting Agent MVP for Hackathon
Prophet-based time series forecasting with sample data
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.mvp import ForecastResult, ForecastPrediction

logger = logging.getLogger(__name__)


class ForecastingAgentMVP(BaseAgent):
    """
    Minimal forecasting agent for MVP demo
    Uses Prophet with hardcoded sample data
    """

    def __init__(self, timeout: int = 30):
        """Initialize forecasting agent"""
        super().__init__(name="ForecastingAgentMVP", timeout=timeout)

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute time series forecast

        Args:
            input_data: Dict with optional 'metric_name' and 'periods' (days to forecast)

        Returns:
            Dict with ForecastResult data
        """
        metric_name = input_data.get("metric_name", "Revenue")
        periods = input_data.get("periods", 30)  # Default 30-day forecast

        try:
            # Import Prophet (lazy import to avoid startup issues if not installed)
            try:
                from prophet import Prophet
            except ImportError:
                logger.warning("Prophet not installed, using simple linear forecast fallback")
                return await self._simple_forecast_fallback(metric_name, periods)

            # Generate sample historical data (100 days)
            historical_data = self._generate_sample_data(days=100)

            # Create DataFrame for Prophet
            df = pd.DataFrame({
                'ds': historical_data['dates'],
                'y': historical_data['values']
            })

            # Initialize and fit Prophet model
            model = Prophet(
                interval_width=0.95,
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False
            )

            # Fit model in thread pool to avoid blocking
            import asyncio
            await asyncio.to_thread(model.fit, df)

            # Create future dataframe for predictions
            future = model.make_future_dataframe(periods=periods)

            # Generate forecast
            forecast = await asyncio.to_thread(model.predict, future)

            # Extract predictions (last 'periods' rows are future predictions)
            predictions = []
            forecast_data = forecast.tail(periods)

            for _, row in forecast_data.iterrows():
                prediction = ForecastPrediction(
                    date=row['ds'].strftime('%Y-%m-%d'),
                    value=float(row['yhat']),
                    lower_bound=float(row['yhat_lower']),
                    upper_bound=float(row['yhat_upper'])
                )
                predictions.append(prediction)

            # Create result
            result = ForecastResult(
                metric_name=metric_name,
                predictions=predictions,
                confidence_level=0.95,
                generated_at=datetime.now()
            )

            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }

        except Exception as e:
            logger.error(f"Forecasting agent failed: {e}", exc_info=True)
            # Fallback to simple forecast on error
            try:
                return await self._simple_forecast_fallback(metric_name, periods)
            except Exception as fallback_error:
                logger.error(f"Fallback forecast also failed: {fallback_error}")
                return {
                    "success": False,
                    "error": str(e),
                    "data": None
                }

    def _generate_sample_data(self, days: int = 100) -> Dict[str, List]:
        """
        Generate sample historical data with trend and seasonality

        Args:
            days: Number of historical days

        Returns:
            Dict with 'dates' and 'values' lists
        """
        import numpy as np

        # Generate dates
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days, 0, -1)]

        # Generate values with trend + seasonality + noise
        base_value = 80000.0
        trend = np.linspace(0, 20000, days)  # Upward trend
        seasonality = 5000 * np.sin(np.linspace(0, 4 * np.pi, days))  # Seasonal pattern
        noise = np.random.normal(0, 2000, days)  # Random noise

        values = base_value + trend + seasonality + noise
        values = np.maximum(values, 0)  # Ensure non-negative

        return {
            'dates': dates,
            'values': values.tolist()
        }

    async def _simple_forecast_fallback(self, metric_name: str, periods: int) -> Dict[str, Any]:
        """
        Simple linear forecast fallback when Prophet is unavailable

        Args:
            metric_name: Name of metric being forecasted
            periods: Number of periods to forecast

        Returns:
            Dict with ForecastResult data
        """
        import numpy as np

        # Generate simple forecast with linear trend
        start_date = datetime.now() + timedelta(days=1)
        base_value = 100000.0
        daily_growth = 500.0

        predictions = []
        for i in range(periods):
            date = start_date + timedelta(days=i)
            value = base_value + (daily_growth * i)
            # Simple confidence intervals (±10%)
            lower = value * 0.9
            upper = value * 1.1

            prediction = ForecastPrediction(
                date=date.strftime('%Y-%m-%d'),
                value=value,
                lower_bound=lower,
                upper_bound=upper
            )
            predictions.append(prediction)

        result = ForecastResult(
            metric_name=metric_name,
            predictions=predictions,
            confidence_level=0.90,
            generated_at=datetime.now()
        )

        return {
            "success": True,
            "data": result.model_dump(),
            "error": "Using simple forecast (Prophet unavailable)"
        }

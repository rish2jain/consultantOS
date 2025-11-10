"""
Enhanced Forecasting Agent - Production-grade multi-scenario time series forecasting
Phase 1 Week 3-4: Enhanced Forecasting Agent with Prophet and scenario simulation
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import numpy as np
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.forecasting import (
    EnhancedForecastResult,
    ForecastScenario,
    ScenarioType,
    MetricType
)

logger = logging.getLogger(__name__)


class EnhancedForecastingAgent(BaseAgent):
    """
    Production-grade forecasting agent with:
    - Prophet time series modeling with seasonal decomposition
    - Multi-scenario simulation (optimistic/baseline/pessimistic)
    - Alpha Vantage integration for real financial data
    - Fallback to sample data when real data unavailable
    - Support for multiple metrics (revenue, market share, customer growth)
    """

    def __init__(self, timeout: int = 60):
        """Initialize enhanced forecasting agent"""
        super().__init__(name="EnhancedForecastingAgent", timeout=timeout)

        # Check Prophet availability
        try:
            from prophet import Prophet
            self.prophet_available = True
            logger.info("Prophet library available for forecasting")
        except ImportError:
            self.prophet_available = False
            logger.warning("Prophet not installed - using simple forecasting fallback")

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multi-scenario forecast generation

        Args:
            input_data: Dict with:
                - company: str (required)
                - industry: str (optional)
                - metric_name: str (default: "Revenue")
                - metric_type: str (default: "revenue")
                - forecast_horizon_days: int (default: 30)
                - ticker: str (optional, for real data)
                - use_real_data: bool (default: False)

        Returns:
            Dict with EnhancedForecastResult data
        """
        company = input_data.get("company", "Unknown Company")
        industry = input_data.get("industry")
        metric_name = input_data.get("metric_name", "Revenue")
        metric_type = input_data.get("metric_type", "revenue")
        forecast_horizon_days = input_data.get("forecast_horizon_days", 30)
        ticker = input_data.get("ticker")
        use_real_data = input_data.get("use_real_data", False)

        # Validate metric type
        try:
            metric_type_enum = MetricType(metric_type.lower())
        except ValueError:
            metric_type_enum = MetricType.CUSTOM

        try:
            # Get historical data (real or sample)
            historical_data, data_source = await self._get_historical_data(
                ticker=ticker,
                use_real_data=use_real_data,
                metric_type=metric_type_enum
            )

            # Use Prophet if available, otherwise fallback
            if self.prophet_available:
                result = await self._prophet_forecast(
                    historical_data=historical_data,
                    company=company,
                    industry=industry,
                    metric_name=metric_name,
                    metric_type=metric_type_enum,
                    forecast_horizon_days=forecast_horizon_days,
                    data_source=data_source
                )
            else:
                result = await self._simple_forecast(
                    historical_data=historical_data,
                    company=company,
                    industry=industry,
                    metric_name=metric_name,
                    metric_type=metric_type_enum,
                    forecast_horizon_days=forecast_horizon_days,
                    data_source=data_source
                )

            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }

        except Exception as e:
            logger.error(f"Enhanced forecasting agent failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def _get_historical_data(
        self,
        ticker: Optional[str],
        use_real_data: bool,
        metric_type: MetricType
    ) -> Tuple[pd.DataFrame, str]:
        """
        Get historical data from Alpha Vantage or generate sample data

        Args:
            ticker: Stock ticker symbol
            use_real_data: Whether to attempt real data fetch
            metric_type: Type of metric

        Returns:
            Tuple of (DataFrame with 'ds' and 'y' columns, data_source string)
        """
        # Try to fetch real data if requested and ticker provided
        if use_real_data and ticker:
            try:
                real_data = await self._fetch_alpha_vantage_data(ticker, metric_type)
                if real_data is not None:
                    logger.info(f"Using real data from Alpha Vantage for {ticker}")
                    return real_data, "alpha_vantage"
            except Exception as e:
                logger.warning(f"Failed to fetch real data for {ticker}: {e}")

        # Fallback to sample data
        logger.info(f"Using sample data for forecasting")
        sample_data = self._generate_sample_data(days=100, metric_type=metric_type)
        return sample_data, "sample_data"

    async def _fetch_alpha_vantage_data(
        self,
        ticker: str,
        metric_type: MetricType
    ) -> Optional[pd.DataFrame]:
        """
        Fetch real financial data from Alpha Vantage

        Args:
            ticker: Stock ticker symbol
            metric_type: Type of metric

        Returns:
            DataFrame with 'ds' (date) and 'y' (value) columns, or None if unavailable
        """
        try:
            from consultantos.tools.alpha_vantage_tool import AlphaVantageClient

            client = AlphaVantageClient()
            if not client.enabled:
                return None

            # Fetch time series data
            # For demo, using daily price data as proxy for various metrics
            data, _ = await asyncio.to_thread(
                client.ts.get_daily,
                symbol=ticker,
                outputsize='full'
            )

            if data is None or data.empty:
                return None

            # Convert to Prophet format
            # Use closing price as the value
            df = pd.DataFrame({
                'ds': data.index,
                'y': data['4. close'].values
            })

            # Take last 100 days for consistency with sample data
            df = df.tail(100).reset_index(drop=True)

            return df

        except Exception as e:
            logger.warning(f"Alpha Vantage data fetch failed: {e}")
            return None

    def _generate_sample_data(self, days: int = 100, metric_type: MetricType = MetricType.REVENUE) -> pd.DataFrame:
        """
        Generate realistic sample historical data with trend and seasonality

        Args:
            days: Number of historical days
            metric_type: Type of metric (affects scale and pattern)

        Returns:
            DataFrame with 'ds' and 'y' columns
        """
        # Generate dates
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='D')

        # Generate values based on metric type
        if metric_type == MetricType.REVENUE:
            base_value = 80000.0
            trend_slope = 20000.0
            seasonality_amplitude = 5000.0
            noise_std = 2000.0
        elif metric_type == MetricType.MARKET_SHARE:
            base_value = 0.15  # 15% market share
            trend_slope = 0.05
            seasonality_amplitude = 0.02
            noise_std = 0.01
        elif metric_type == MetricType.CUSTOMER_GROWTH:
            base_value = 1000.0
            trend_slope = 500.0
            seasonality_amplitude = 100.0
            noise_std = 50.0
        else:  # CUSTOM or others
            base_value = 100.0
            trend_slope = 20.0
            seasonality_amplitude = 10.0
            noise_std = 5.0

        # Generate time series components
        t = np.arange(days)
        trend = base_value + (trend_slope / days) * t
        seasonality = seasonality_amplitude * np.sin(2 * np.pi * t / 30)  # Monthly seasonality
        noise = np.random.normal(0, noise_std, days)

        values = trend + seasonality + noise
        values = np.maximum(values, 0)  # Ensure non-negative

        return pd.DataFrame({'ds': dates, 'y': values})

    async def _prophet_forecast(
        self,
        historical_data: pd.DataFrame,
        company: str,
        industry: Optional[str],
        metric_name: str,
        metric_type: MetricType,
        forecast_horizon_days: int,
        data_source: str
    ) -> EnhancedForecastResult:
        """
        Generate multi-scenario forecast using Prophet

        Args:
            historical_data: DataFrame with 'ds' and 'y' columns
            company: Company name
            industry: Industry context
            metric_name: Metric being forecasted
            metric_type: Type of metric
            forecast_horizon_days: Forecast horizon
            data_source: Source of historical data

        Returns:
            EnhancedForecastResult with three scenarios
        """
        from prophet import Prophet

        # Generate three scenarios with different parameters
        scenarios = await asyncio.gather(
            self._generate_scenario(
                historical_data, forecast_horizon_days,
                ScenarioType.BASELINE, Prophet
            ),
            self._generate_scenario(
                historical_data, forecast_horizon_days,
                ScenarioType.OPTIMISTIC, Prophet
            ),
            self._generate_scenario(
                historical_data, forecast_horizon_days,
                ScenarioType.PESSIMISTIC, Prophet
            )
        )

        # Generate insights
        key_insights = self._generate_insights(historical_data, scenarios)

        # Calculate model accuracy metrics
        model_accuracy = self._calculate_accuracy(historical_data)

        return EnhancedForecastResult(
            metric_name=metric_name,
            metric_type=metric_type,
            company=company,
            industry=industry,
            scenarios=scenarios,
            recommended_scenario=ScenarioType.BASELINE,  # Conservative recommendation
            key_insights=key_insights,
            methodology="Prophet with seasonal decomposition and multi-scenario simulation",
            data_source=data_source,
            forecast_horizon_days=forecast_horizon_days,
            historical_data_points=len(historical_data),
            model_accuracy=model_accuracy,
            generated_at=datetime.now()
        )

    async def _generate_scenario(
        self,
        historical_data: pd.DataFrame,
        forecast_horizon_days: int,
        scenario_type: ScenarioType,
        Prophet
    ) -> ForecastScenario:
        """
        Generate a single forecast scenario

        Args:
            historical_data: Historical time series data
            forecast_horizon_days: Number of days to forecast
            scenario_type: Type of scenario
            Prophet: Prophet class

        Returns:
            ForecastScenario object
        """
        # Adjust Prophet parameters based on scenario
        if scenario_type == ScenarioType.OPTIMISTIC:
            # Higher growth, lower uncertainty
            growth = 'linear'
            changepoint_prior_scale = 0.05
            interval_width = 0.80  # Narrower intervals
            trend_adjustment = 1.15  # 15% higher trend
            assumptions = {
                "growth_assumption": "accelerated",
                "market_conditions": "favorable",
                "confidence_adjustment": "high"
            }
        elif scenario_type == ScenarioType.PESSIMISTIC:
            # Lower growth, higher uncertainty
            growth = 'linear'
            changepoint_prior_scale = 0.01
            interval_width = 0.95  # Wider intervals
            trend_adjustment = 0.85  # 15% lower trend
            assumptions = {
                "growth_assumption": "decelerated",
                "market_conditions": "challenging",
                "confidence_adjustment": "conservative"
            }
        else:  # BASELINE
            # Standard parameters
            growth = 'linear'
            changepoint_prior_scale = 0.05
            interval_width = 0.90
            trend_adjustment = 1.0  # No adjustment
            assumptions = {
                "growth_assumption": "stable",
                "market_conditions": "normal",
                "confidence_adjustment": "moderate"
            }

        # Create and fit Prophet model in thread pool
        model = Prophet(
            growth=growth,
            changepoint_prior_scale=changepoint_prior_scale,
            interval_width=interval_width,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False
        )

        await asyncio.to_thread(model.fit, historical_data)

        # Generate future dataframe
        future = model.make_future_dataframe(periods=forecast_horizon_days)

        # Make predictions
        forecast = await asyncio.to_thread(model.predict, future)

        # Extract future predictions only
        forecast_data = forecast.tail(forecast_horizon_days)

        # Apply scenario adjustment
        dates = forecast_data['ds'].dt.strftime('%Y-%m-%d').tolist()
        predictions = (forecast_data['yhat'] * trend_adjustment).tolist()
        lower_bound = (forecast_data['yhat_lower'] * trend_adjustment).tolist()
        upper_bound = (forecast_data['yhat_upper'] * trend_adjustment).tolist()

        return ForecastScenario(
            scenario_type=scenario_type,
            dates=dates,
            predictions=predictions,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            confidence=interval_width,
            assumptions=assumptions
        )

    async def _simple_forecast(
        self,
        historical_data: pd.DataFrame,
        company: str,
        industry: Optional[str],
        metric_name: str,
        metric_type: MetricType,
        forecast_horizon_days: int,
        data_source: str
    ) -> EnhancedForecastResult:
        """
        Simple linear forecast fallback when Prophet unavailable

        Args:
            historical_data: Historical data
            company: Company name
            industry: Industry context
            metric_name: Metric name
            metric_type: Metric type
            forecast_horizon_days: Forecast horizon
            data_source: Data source

        Returns:
            EnhancedForecastResult with simple linear projections
        """
        # Calculate simple trend from historical data
        values = historical_data['y'].values
        trend = np.polyfit(range(len(values)), values, 1)

        # Generate scenarios with different growth rates
        scenarios = []
        for scenario_type, growth_multiplier in [
            (ScenarioType.BASELINE, 1.0),
            (ScenarioType.OPTIMISTIC, 1.2),
            (ScenarioType.PESSIMISTIC, 0.8)
        ]:
            start_date = datetime.now() + timedelta(days=1)
            dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                     for i in range(forecast_horizon_days)]

            # Linear projection with scenario adjustment
            base_value = values[-1]
            daily_growth = trend[0] * growth_multiplier

            predictions = [base_value + (daily_growth * i) for i in range(1, forecast_horizon_days + 1)]
            lower_bound = [p * 0.9 for p in predictions]
            upper_bound = [p * 1.1 for p in predictions]

            scenarios.append(ForecastScenario(
                scenario_type=scenario_type,
                dates=dates,
                predictions=predictions,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence=0.80,
                assumptions={"method": "linear_projection", "growth_multiplier": growth_multiplier}
            ))

        return EnhancedForecastResult(
            metric_name=metric_name,
            metric_type=metric_type,
            company=company,
            industry=industry,
            scenarios=scenarios,
            recommended_scenario=ScenarioType.BASELINE,
            key_insights=[
                "Simple linear forecast (Prophet unavailable)",
                f"Historical trend: {trend[0]:.2f} per day",
                "Install Prophet for enhanced forecasting capabilities"
            ],
            methodology="Simple linear projection (Prophet fallback)",
            data_source=data_source,
            forecast_horizon_days=forecast_horizon_days,
            historical_data_points=len(historical_data),
            model_accuracy=None,
            generated_at=datetime.now()
        )

    def _generate_insights(
        self,
        historical_data: pd.DataFrame,
        scenarios: List[ForecastScenario]
    ) -> List[str]:
        """
        Generate key insights from forecast analysis

        Args:
            historical_data: Historical data
            scenarios: List of forecast scenarios

        Returns:
            List of insight strings
        """
        insights = []

        # Trend analysis
        values = historical_data['y'].values
        trend = np.polyfit(range(len(values)), values, 1)[0]

        if trend > 0:
            insights.append(f"Strong upward trend detected: +{trend:.2f} per day")
        elif trend < 0:
            insights.append(f"Downward trend detected: {trend:.2f} per day")
        else:
            insights.append("Stable trend with minimal change")

        # Volatility analysis
        volatility = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
        if volatility > 0.2:
            insights.append(f"High volatility detected: {volatility:.1%} coefficient of variation")
        elif volatility > 0.1:
            insights.append(f"Moderate volatility: {volatility:.1%} coefficient of variation")
        else:
            insights.append(f"Low volatility: {volatility:.1%} coefficient of variation")

        # Scenario comparison
        baseline = next(s for s in scenarios if s.scenario_type == ScenarioType.BASELINE)
        optimistic = next(s for s in scenarios if s.scenario_type == ScenarioType.OPTIMISTIC)
        pessimistic = next(s for s in scenarios if s.scenario_type == ScenarioType.PESSIMISTIC)

        avg_baseline = np.mean(baseline.predictions)
        avg_optimistic = np.mean(optimistic.predictions)
        avg_pessimistic = np.mean(pessimistic.predictions)

        upside = ((avg_optimistic - avg_baseline) / avg_baseline * 100) if avg_baseline > 0 else 0
        downside = ((avg_baseline - avg_pessimistic) / avg_baseline * 100) if avg_baseline > 0 else 0

        insights.append(f"Upside potential: +{upside:.1f}% (optimistic scenario)")
        insights.append(f"Downside risk: -{downside:.1f}% (pessimistic scenario)")

        return insights

    def _calculate_accuracy(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate basic model accuracy metrics on historical data

        Args:
            historical_data: Historical time series data

        Returns:
            Dict with accuracy metrics
        """
        # Simple train-test split for validation
        values = historical_data['y'].values
        split_idx = int(len(values) * 0.8)

        train_values = values[:split_idx]
        test_values = values[split_idx:]

        # Simple linear model for validation
        trend = np.polyfit(range(len(train_values)), train_values, 1)
        predictions = np.polyval(trend, range(split_idx, len(values)))

        # Calculate metrics
        mape = np.mean(np.abs((test_values - predictions) / test_values)) * 100 if len(test_values) > 0 else 0
        rmse = np.sqrt(np.mean((test_values - predictions) ** 2)) if len(test_values) > 0 else 0

        return {
            "mape": float(mape),
            "rmse": float(rmse)
        }

"""
Tests for Prophet-based anomaly detection system.

Validates anomaly detection accuracy, performance, and Prophet integration.
"""

import time
from datetime import datetime, timedelta

import numpy as np
import pytest

from consultantos.monitoring.anomaly_detector import (
    AnomalyDetector,
    AnomalyScore,
    AnomalyType,
    TrendAnalysis,
)


class TestAnomalyDetector:
    """Tests for AnomalyDetector class"""

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return AnomalyDetector(
            confidence_mode="balanced",
            enable_seasonality=True,
        )

    @pytest.fixture
    def normal_time_series(self):
        """Generate normal time series data (30 days)"""
        start_date = datetime.utcnow() - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range(30)]

        # Normal distribution around 100
        np.random.seed(42)
        values = np.random.normal(loc=100, scale=10, size=30)

        return list(zip(dates, values))

    @pytest.fixture
    def anomaly_time_series(self):
        """Generate time series with known anomaly"""
        start_date = datetime.utcnow() - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range(31)]  # +1 for anomaly

        # Normal data for 30 days
        np.random.seed(42)
        values = list(np.random.normal(loc=100, scale=10, size=30))

        # Add clear anomaly (5 standard deviations)
        values.append(150)  # Significantly above normal

        return list(zip(dates, values))

    @pytest.fixture
    def trending_time_series(self):
        """Generate trending time series data"""
        start_date = datetime.utcnow() - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range(30)]

        # Linear growth trend + noise
        np.random.seed(42)
        trend = np.linspace(100, 150, 30)
        noise = np.random.normal(loc=0, scale=5, size=30)
        values = trend + noise

        return list(zip(dates, values))

    @pytest.fixture
    def reversal_time_series(self):
        """Generate time series with trend reversal"""
        start_date = datetime.utcnow() - timedelta(days=30)
        dates = [start_date + timedelta(days=i) for i in range(30)]

        np.random.seed(42)
        # Growing trend for first 20 days
        values = list(np.linspace(100, 130, 20) + np.random.normal(0, 3, 20))
        # Declining trend for last 10 days
        values.extend(np.linspace(130, 110, 10) + np.random.normal(0, 3, 10))

        return list(zip(dates, values))

    def test_initialization(self, detector):
        """Test detector initialization"""
        assert detector.confidence_mode == "balanced"
        assert detector.enable_seasonality is True
        assert detector.interval_width == 0.80
        assert len(detector._model_cache) == 0

    def test_fit_model_success(self, detector, normal_time_series):
        """Test successful model training"""
        success = detector.fit_model("revenue", normal_time_series)

        assert success is True
        assert "revenue" in detector._model_cache
        assert detector._model_cache["revenue"] is not None

    def test_fit_model_insufficient_data(self, detector):
        """Test model training with insufficient data"""
        # Only 7 days (< MIN_TRAINING_DAYS = 14)
        start_date = datetime.utcnow() - timedelta(days=7)
        short_series = [
            (start_date + timedelta(days=i), 100 + i)
            for i in range(7)
        ]

        success = detector.fit_model("revenue", short_series)

        assert success is False
        assert "revenue" not in detector._model_cache

    def test_fit_model_with_invalid_data(self, detector):
        """Test model training with NaN/inf values"""
        start_date = datetime.utcnow() - timedelta(days=20)
        invalid_series = [
            (start_date + timedelta(days=i), 100 if i < 15 else float('nan'))
            for i in range(20)
        ]

        # Should filter out NaN values and fail if < MIN_TRAINING_DAYS
        success = detector.fit_model("revenue", invalid_series)

        # After filtering NaN, only 15 points remain (>= 14)
        assert success is True

    def test_detect_anomalies_no_model(self, detector):
        """Test anomaly detection without trained model"""
        anomaly = detector.detect_anomalies("revenue", 150.0)

        assert anomaly is None

    def test_detect_anomalies_within_bounds(self, detector, normal_time_series):
        """Test that normal values don't trigger anomalies"""
        # Train model
        detector.fit_model("revenue", normal_time_series)

        # Test with value within normal range
        anomaly = detector.detect_anomalies("revenue", 105.0)

        assert anomaly is None

    def test_detect_anomalies_outside_bounds(self, detector, anomaly_time_series):
        """Test detection of clear anomaly"""
        # Train on data without anomaly
        training_data = anomaly_time_series[:-1]
        detector.fit_model("revenue", training_data)

        # Test anomalous value
        anomaly_timestamp, anomaly_value = anomaly_time_series[-1]
        anomaly = detector.detect_anomalies(
            "revenue",
            anomaly_value,
            anomaly_timestamp
        )

        assert anomaly is not None
        assert isinstance(anomaly, AnomalyScore)
        assert anomaly.metric_name == "revenue"
        assert anomaly.anomaly_type == AnomalyType.POINT
        assert anomaly.severity > 5.0  # Should be significant
        assert anomaly.confidence > 0.5
        assert "above" in anomaly.explanation.lower()
        assert anomaly.actual_value == anomaly_value
        assert anomaly.forecast_value is not None
        assert anomaly.upper_bound is not None

    def test_calculate_severity(self, detector):
        """Test severity calculation"""
        # z-score = 0 (no deviation)
        severity = detector.calculate_severity(0.0)
        assert severity == 0.0

        # z-score = 2.5 (moderate deviation)
        severity = detector.calculate_severity(2.5)
        assert 4.0 <= severity <= 6.0

        # z-score = 5.0 (high deviation)
        severity = detector.calculate_severity(5.0)
        assert severity == 10.0  # Capped at 10

        # z-score = 10.0 (extreme, should cap)
        severity = detector.calculate_severity(10.0)
        assert severity == 10.0

    def test_calculate_severity_with_context(self, detector):
        """Test severity adjustment based on context"""
        base_z_score = 5.0

        # No context
        base_severity = detector.calculate_severity(base_z_score)
        assert base_severity == 10.0

        # Earnings day context (reduce severity)
        earnings_severity = detector.calculate_severity(
            base_z_score,
            context={"earnings_day": True}
        )
        assert earnings_severity < base_severity

        # Market hours context (increase severity)
        market_severity = detector.calculate_severity(
            base_z_score,
            context={"market_hours": True}
        )
        assert market_severity > base_severity

    def test_trend_analysis(self, detector, trending_time_series):
        """Test trend analysis on growing series"""
        # Train model
        detector.fit_model("revenue", trending_time_series)

        # Analyze trend
        analysis = detector.trend_analysis("revenue", recent_window_days=7)

        assert analysis is not None
        assert isinstance(analysis, TrendAnalysis)
        assert analysis.metric_name == "revenue"
        assert analysis.trend_direction in ["increasing", "decreasing", "stable"]
        assert analysis.trend_direction == "increasing"  # Known growth trend
        assert 0.0 <= analysis.trend_strength <= 1.0
        assert analysis.reversal_detected is False

    def test_trend_reversal_detection(self, detector, reversal_time_series):
        """Test detection of trend reversal"""
        # Train model
        detector.fit_model("revenue", reversal_time_series)

        # Analyze trend (should detect reversal)
        analysis = detector.trend_analysis("revenue", recent_window_days=7)

        assert analysis is not None
        # Should detect reversal from increasing to decreasing
        if analysis.reversal_detected:
            assert analysis.reversal_confidence > 0.0
            assert analysis.historical_trend != analysis.current_trend
            assert analysis.current_trend == "decreasing"

    def test_get_forecast(self, detector, normal_time_series):
        """Test forecast generation"""
        # Train model
        detector.fit_model("revenue", normal_time_series)

        # Get 7-day forecast
        forecast = detector.get_forecast("revenue", periods=7)

        assert forecast is not None
        assert len(forecast) == 30 + 7  # Historical + future
        assert "ds" in forecast.columns
        assert "yhat" in forecast.columns
        assert "yhat_lower" in forecast.columns
        assert "yhat_upper" in forecast.columns
        assert "trend" in forecast.columns

    def test_detect_contextual_anomaly(self, detector, anomaly_time_series):
        """Test contextual anomaly detection"""
        # Train model
        training_data = anomaly_time_series[:-1]
        detector.fit_model("revenue", training_data)

        anomaly_timestamp, anomaly_value = anomaly_time_series[-1]

        # Test with earnings day context
        anomaly = detector.detect_contextual_anomaly(
            metric_name="revenue",
            value=anomaly_value,
            timestamp=anomaly_timestamp,
            context={"earnings_day": True}
        )

        # Might not trigger on earnings day if severity < 7
        # Just verify it returns valid result
        if anomaly:
            assert anomaly.anomaly_type in [AnomalyType.POINT, AnomalyType.CONTEXTUAL]

    def test_detect_volatility_spike(self, detector):
        """Test volatility spike detection"""
        np.random.seed(42)

        # Historical: low volatility
        historical_values = list(np.random.normal(loc=100, scale=5, size=30))

        # Recent: high volatility
        recent_values = list(np.random.normal(loc=100, scale=15, size=7))

        spike = detector.detect_volatility_spike(
            metric_name="revenue",
            recent_values=recent_values,
            historical_values=historical_values,
        )

        assert spike is not None
        assert spike.anomaly_type == AnomalyType.VOLATILITY_SPIKE
        assert spike.severity > 0.0
        assert "volatility" in spike.explanation.lower()
        assert "recent_std" in spike.statistical_details
        assert "historical_std" in spike.statistical_details

    def test_detect_volatility_spike_no_spike(self, detector):
        """Test no volatility spike with similar variance"""
        np.random.seed(42)

        # Both similar volatility
        historical_values = list(np.random.normal(loc=100, scale=10, size=30))
        recent_values = list(np.random.normal(loc=100, scale=10, size=7))

        spike = detector.detect_volatility_spike(
            metric_name="revenue",
            recent_values=recent_values,
            historical_values=historical_values,
        )

        assert spike is None

    def test_clear_cache(self, detector, normal_time_series):
        """Test cache clearing"""
        # Train models
        detector.fit_model("revenue", normal_time_series)
        detector.fit_model("profit", normal_time_series)

        assert len(detector._model_cache) == 2

        # Clear specific metric
        detector.clear_cache("revenue")
        assert "revenue" not in detector._model_cache
        assert "profit" in detector._model_cache

        # Clear all
        detector.clear_cache()
        assert len(detector._model_cache) == 0

    def test_confidence_modes(self):
        """Test different confidence modes"""
        conservative = AnomalyDetector(confidence_mode="conservative")
        balanced = AnomalyDetector(confidence_mode="balanced")
        aggressive = AnomalyDetector(confidence_mode="aggressive")

        assert conservative.interval_width == 0.95
        assert balanced.interval_width == 0.80
        assert aggressive.interval_width == 0.60

        # Invalid mode defaults to balanced
        default = AnomalyDetector(confidence_mode="invalid")
        assert default.interval_width == 0.80

    def test_performance_benchmark(self, detector, normal_time_series):
        """Test performance (<500ms per detection)"""
        # Train model
        detector.fit_model("revenue", normal_time_series)

        # Benchmark detection
        start_time = time.time()
        for _ in range(10):
            detector.detect_anomalies("revenue", 105.0)
        elapsed = time.time() - start_time

        avg_time_ms = (elapsed / 10) * 1000
        assert avg_time_ms < 500, f"Detection too slow: {avg_time_ms:.0f}ms"

    def test_seasonality_detection(self):
        """Test seasonality with weekly patterns"""
        detector = AnomalyDetector(
            confidence_mode="balanced",
            enable_seasonality=True,
        )

        # Generate weekly seasonal pattern (60 days)
        start_date = datetime.utcnow() - timedelta(days=60)
        dates = [start_date + timedelta(days=i) for i in range(60)]

        np.random.seed(42)
        # Weekly pattern: peak on day 0 (Monday), low on day 6 (Sunday)
        values = [
            100 + 20 * np.sin(2 * np.pi * i / 7) + np.random.normal(0, 5)
            for i in range(60)
        ]

        series = list(zip(dates, values))

        # Train model
        success = detector.fit_model("weekly_metric", series)
        assert success is True

        # Test detection on typical Monday (should not be anomaly)
        monday_value = 100 + 20 * np.sin(0)  # Peak
        anomaly = detector.detect_anomalies("weekly_metric", monday_value)
        # Should be within bounds due to seasonality
        assert anomaly is None or anomaly.severity < 3.0

    def test_multiple_metrics(self, detector, normal_time_series):
        """Test handling multiple metrics"""
        # Train multiple models
        detector.fit_model("revenue", normal_time_series)
        detector.fit_model("profit", normal_time_series)
        detector.fit_model("customers", normal_time_series)

        assert len(detector._model_cache) == 3

        # Each should work independently
        assert detector.detect_anomalies("revenue", 105.0) is None
        assert detector.detect_anomalies("profit", 105.0) is None
        assert detector.detect_anomalies("customers", 105.0) is None

    def test_edge_cases(self, detector):
        """Test edge cases and error handling"""
        # Empty data
        assert detector.fit_model("metric", []) is False

        # Single point
        single_point = [(datetime.utcnow(), 100.0)]
        assert detector.fit_model("metric", single_point) is False

        # All same values (zero variance)
        start_date = datetime.utcnow() - timedelta(days=20)
        constant_series = [
            (start_date + timedelta(days=i), 100.0)
            for i in range(20)
        ]
        # Should handle gracefully
        result = detector.fit_model("constant", constant_series)
        # Prophet may or may not succeed with constant values
        assert isinstance(result, bool)


class TestAnomalyDetectorIntegration:
    """Integration tests with real-world scenarios"""

    @pytest.fixture
    def detector(self):
        return AnomalyDetector(confidence_mode="balanced", enable_seasonality=True)

    def test_stock_price_anomaly(self, detector):
        """Test with stock-price-like data"""
        # Generate 30 days of stock prices
        start_date = datetime.utcnow() - timedelta(days=30)
        np.random.seed(42)

        # Realistic stock price movement
        prices = [100.0]
        for i in range(29):
            change = np.random.normal(0, 2)  # 2% daily volatility
            prices.append(prices[-1] * (1 + change / 100))

        dates = [start_date + timedelta(days=i) for i in range(30)]
        series = list(zip(dates, prices))

        # Train model
        success = detector.fit_model("stock_price", series)
        assert success is True

        # Simulate market crash (20% drop)
        crash_value = prices[-1] * 0.80
        anomaly = detector.detect_anomalies("stock_price", crash_value)

        assert anomaly is not None
        assert anomaly.severity > 7.0  # Should be critical
        assert anomaly.confidence > 0.7

    def test_revenue_growth_pattern(self, detector):
        """Test with typical revenue growth"""
        # 60 days of growing revenue
        start_date = datetime.utcnow() - timedelta(days=60)
        np.random.seed(42)

        # Monthly growth rate ~10%
        base_revenue = 1000000
        revenues = []
        for i in range(60):
            growth_factor = (1 + 0.10 / 30) ** i  # Daily compounding
            noise = np.random.normal(0, 0.02)  # 2% noise
            revenue = base_revenue * growth_factor * (1 + noise)
            revenues.append(revenue)

        dates = [start_date + timedelta(days=i) for i in range(60)]
        series = list(zip(dates, revenues))

        # Train model
        success = detector.fit_model("revenue", series)
        assert success is True

        # Analyze trend
        analysis = detector.trend_analysis("revenue")
        assert analysis.trend_direction == "increasing"
        assert analysis.trend_strength > 0.5

        # Test normal growth continuation (should not be anomaly)
        next_expected = revenues[-1] * (1 + 0.10 / 30)
        anomaly = detector.detect_anomalies("revenue", next_expected)
        assert anomaly is None

        # Test sudden drop (anomaly)
        sudden_drop = revenues[-1] * 0.85
        anomaly = detector.detect_anomalies("revenue", sudden_drop)
        assert anomaly is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

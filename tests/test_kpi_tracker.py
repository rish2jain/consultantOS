"""
Tests for KPI tracker and alert engine
"""
import pytest
from datetime import datetime

from consultantos.analytics.kpi_tracker import KPITracker, KPITrackerError, AlertEngine
from consultantos.models.analytics import (
    KPI,
    Formula,
    TrendDirection,
    AlertSeverity,
)


@pytest.fixture
def tracker():
    """Create KPI tracker fixture"""
    return KPITracker(history_limit=100)


@pytest.fixture
def alert_engine():
    """Create alert engine fixture"""
    return AlertEngine()


@pytest.fixture
def sample_formula():
    """Create sample formula"""
    return Formula(
        formula_id="formula-1",
        name="Revenue Formula",
        expression="revenue * margin_percent / 100",
        variables=["revenue", "margin_percent"],
        category="financial",
    )


@pytest.fixture
def sample_kpi(sample_formula):
    """Create sample KPI"""
    return KPI(
        kpi_id="kpi-1",
        name="Gross Profit",
        formula=sample_formula,
        target_value=1000,
        alert_threshold=500,
    )


class TestKPIEvaluation:
    """Test KPI evaluation"""

    @pytest.mark.asyncio
    async def test_evaluate_simple_kpi(self, tracker, sample_kpi):
        """Test evaluating simple KPI"""
        context = {"revenue": 10000, "margin_percent": 25}

        result = await tracker.evaluate_kpi(sample_kpi, context)

        assert result.current_value == 2500
        assert result.kpi_id == "kpi-1"

    @pytest.mark.asyncio
    async def test_evaluate_kpi_with_trend(self, tracker, sample_kpi):
        """Test KPI evaluation with trend calculation"""
        context = {"revenue": 10000, "margin_percent": 25}

        # First evaluation
        result1 = await tracker.evaluate_kpi(sample_kpi, context)
        assert result1.current_value == 2500
        assert result1.trend == TrendDirection.STABLE

        # Update sample_kpi current value and evaluate again
        sample_kpi.current_value = 2500
        context2 = {"revenue": 11000, "margin_percent": 25}
        result2 = await tracker.evaluate_kpi(sample_kpi, context2)

        assert result2.current_value == 2750
        assert result2.trend == TrendDirection.UP
        assert result2.percentage_change > 0

    @pytest.mark.asyncio
    async def test_evaluate_kpi_downtrend(self, tracker, sample_kpi):
        """Test KPI with downward trend"""
        context1 = {"revenue": 10000, "margin_percent": 25}
        result1 = await tracker.evaluate_kpi(sample_kpi, context1)

        sample_kpi.current_value = 2500
        context2 = {"revenue": 8000, "margin_percent": 25}
        result2 = await tracker.evaluate_kpi(sample_kpi, context2)

        assert result2.current_value == 2000
        assert result2.trend == TrendDirection.DOWN


class TestAlertChecking:
    """Test alert checking"""

    @pytest.mark.asyncio
    async def test_check_threshold_alert(self, tracker, sample_kpi):
        """Test threshold alert"""
        sample_kpi.current_value = 600
        sample_kpi.alert_threshold = 500

        alerts = await tracker.check_alerts(sample_kpi)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.asyncio
    async def test_check_min_value_alert(self, tracker, sample_kpi):
        """Test minimum value alert"""
        sample_kpi.current_value = 100
        sample_kpi.min_value = 200

        alerts = await tracker.check_alerts(sample_kpi)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_check_max_value_alert(self, tracker, sample_kpi):
        """Test maximum value alert"""
        sample_kpi.current_value = 5000
        sample_kpi.max_value = 3000

        alerts = await tracker.check_alerts(sample_kpi)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_no_alert_within_range(self, tracker, sample_kpi):
        """Test no alert when within range"""
        sample_kpi.current_value = 1500
        sample_kpi.min_value = 1000
        sample_kpi.max_value = 2000
        sample_kpi.alert_threshold = 500

        alerts = await tracker.check_alerts(sample_kpi)

        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_disabled_alerts(self, tracker, sample_kpi):
        """Test disabled alerts"""
        sample_kpi.current_value = 600
        sample_kpi.alert_threshold = 500
        sample_kpi.alert_enabled = False

        alerts = await tracker.check_alerts(sample_kpi)

        assert len(alerts) == 0


class TestTrendAnalysis:
    """Test trend analysis"""

    @pytest.mark.asyncio
    async def test_get_trend_upward(self, tracker, sample_kpi):
        """Test upward trend detection"""
        context = {"revenue": 10000, "margin_percent": 20}
        for i in range(5):
            sample_kpi.current_value = 1000 + (i * 100)
            await tracker.evaluate_kpi(sample_kpi, context)

        trend = await tracker.get_trend("kpi-1", period=5)
        assert trend == TrendDirection.UP

    @pytest.mark.asyncio
    async def test_get_trend_downward(self, tracker, sample_kpi):
        """Test downward trend detection"""
        context = {"revenue": 10000, "margin_percent": 20}
        for i in range(5):
            sample_kpi.current_value = 2000 - (i * 100)
            await tracker.evaluate_kpi(sample_kpi, context)

        trend = await tracker.get_trend("kpi-1", period=5)
        assert trend == TrendDirection.DOWN

    @pytest.mark.asyncio
    async def test_get_trend_insufficient_data(self, tracker):
        """Test trend with insufficient data"""
        trend = await tracker.get_trend("nonexistent", period=5)
        assert trend is None


class TestMovingAverage:
    """Test moving average calculation"""

    @pytest.mark.asyncio
    async def test_moving_average(self, tracker, sample_kpi):
        """Test moving average calculation"""
        context = {"revenue": 10000, "margin_percent": 20}

        values = [1000, 1100, 1200, 1300, 1400]
        for value in values:
            sample_kpi.current_value = value
            await tracker.evaluate_kpi(sample_kpi, context)

        avg = await tracker.get_moving_average("kpi-1", window=5)

        expected = sum(values) / len(values)
        assert avg == expected


class TestVolatility:
    """Test volatility calculation"""

    @pytest.mark.asyncio
    async def test_volatility_calculation(self, tracker, sample_kpi):
        """Test standard deviation calculation"""
        context = {"revenue": 10000, "margin_percent": 20}

        values = [100, 200, 150, 180, 170]
        for value in values:
            sample_kpi.current_value = value
            await tracker.evaluate_kpi(sample_kpi, context)

        volatility = await tracker.get_volatility("kpi-1", window=5)

        assert volatility is not None
        assert volatility > 0


class TestComparisonToTarget:
    """Test target comparison"""

    @pytest.mark.asyncio
    async def test_compare_to_target_above(self, tracker, sample_kpi):
        """Test comparing to target above"""
        sample_kpi.current_value = 1200
        sample_kpi.target_value = 1000

        percentage = await tracker.compare_to_target(sample_kpi)

        assert percentage == 120

    @pytest.mark.asyncio
    async def test_compare_to_target_below(self, tracker, sample_kpi):
        """Test comparing to target below"""
        sample_kpi.current_value = 800
        sample_kpi.target_value = 1000

        percentage = await tracker.compare_to_target(sample_kpi)

        assert percentage == 80

    @pytest.mark.asyncio
    async def test_compare_to_target_none(self, tracker, sample_kpi):
        """Test comparing with no target"""
        sample_kpi.current_value = 1000
        sample_kpi.target_value = None

        percentage = await tracker.compare_to_target(sample_kpi)

        assert percentage is None


class TestForecasting:
    """Test forecasting"""

    @pytest.mark.asyncio
    async def test_forecast_uptrend(self, tracker, sample_kpi):
        """Test forecasting uptrend"""
        context = {"revenue": 10000, "margin_percent": 20}

        # Create uptrend
        for i in range(10):
            sample_kpi.current_value = 100 + (i * 10)
            await tracker.evaluate_kpi(sample_kpi, context)

        forecast = await tracker.forecast("kpi-1", periods=3)

        assert forecast is not None
        assert len(forecast) == 3
        # In uptrend, forecast should be increasing
        assert forecast[0] < forecast[1] < forecast[2]

    @pytest.mark.asyncio
    async def test_forecast_insufficient_data(self, tracker):
        """Test forecast with insufficient data"""
        forecast = await tracker.forecast("nonexistent", periods=3)
        assert forecast is None


class TestAlertEngine:
    """Test alert engine"""

    @pytest.mark.asyncio
    async def test_create_alert_rule(self, alert_engine):
        """Test creating alert rule"""
        await alert_engine.create_rule(
            rule_id="rule-1",
            kpi_id="kpi-1",
            condition=">",
            threshold=1000,
            severity=AlertSeverity.WARNING,
        )

        assert "rule-1" in alert_engine.alert_rules

    @pytest.mark.asyncio
    async def test_evaluate_alert_rule_triggered(self, alert_engine, sample_kpi):
        """Test evaluating triggered rule"""
        await alert_engine.create_rule(
            rule_id="rule-1",
            kpi_id="kpi-1",
            condition=">",
            threshold=1000,
            severity=AlertSeverity.WARNING,
        )

        sample_kpi.current_value = 1500

        alerts = await alert_engine.evaluate_rules(sample_kpi)

        assert len(alerts) == 1

    @pytest.mark.asyncio
    async def test_evaluate_alert_rule_not_triggered(self, alert_engine, sample_kpi):
        """Test evaluating non-triggered rule"""
        await alert_engine.create_rule(
            rule_id="rule-1",
            kpi_id="kpi-1",
            condition=">",
            threshold=1000,
            severity=AlertSeverity.WARNING,
        )

        sample_kpi.current_value = 500

        alerts = await alert_engine.evaluate_rules(sample_kpi)

        assert len(alerts) == 0


class TestAlertManagement:
    """Test alert management"""

    @pytest.mark.asyncio
    async def test_get_alerts_by_kpi(self, tracker, sample_kpi):
        """Test getting alerts for specific KPI"""
        sample_kpi.current_value = 600
        sample_kpi.alert_threshold = 500

        await tracker.check_alerts(sample_kpi)

        alerts = tracker.get_alerts(kpi_id="kpi-1")

        assert len(alerts) > 0

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, tracker, sample_kpi):
        """Test acknowledging alert"""
        sample_kpi.current_value = 600
        sample_kpi.alert_threshold = 500

        alerts = await tracker.check_alerts(sample_kpi)

        if alerts:
            alert_id = alerts[0].alert_id
            result = tracker.acknowledge_alert(alert_id)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_all_alerts(self, tracker):
        """Test getting all alerts"""
        alerts = tracker.get_alerts()
        assert isinstance(alerts, list)

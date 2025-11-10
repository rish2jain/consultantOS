"""
KPI tracker with real-time monitoring and alert engine
Supports threshold-based alerts and trend analysis
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

from consultantos.models.analytics import (
    KPI,
    KPIAlert,
    KPIHistory,
    TrendDirection,
    AlertSeverity,
    Formula,
)
from consultantos.analytics.formula_parser import FormulaParser


logger = logging.getLogger(__name__)


class KPITrackerError(Exception):
    """KPI tracker error"""
    pass


class KPITracker:
    """
    Track KPIs with historical data and trend analysis
    """

    def __init__(self, history_limit: int = 100):
        """
        Initialize KPI tracker

        Args:
            history_limit: Maximum history entries per KPI
        """
        self.history_limit = history_limit
        self.formula_parser = FormulaParser(safe_mode=True)
        self.kpi_history: Dict[str, deque] = {}
        self.alerts: Dict[str, List[KPIAlert]] = {}

    async def evaluate_kpi(
        self,
        kpi: KPI,
        context: Dict[str, Any],
    ) -> KPI:
        """
        Evaluate KPI formula and update value

        Args:
            kpi: KPI definition
            context: Data context for formula evaluation

        Returns:
            Updated KPI with current value
        """
        try:
            # Evaluate formula
            value = await self.formula_parser.parse_and_evaluate(
                kpi.formula.expression,
                context,
                kpi.formula.variables,
            )

            # Update KPI
            previous_value = kpi.current_value
            kpi.current_value = value
            kpi.updated_at = datetime.utcnow()

            # Calculate trend
            if previous_value is not None:
                if value > previous_value:
                    kpi.trend = TrendDirection.UP
                    kpi.percentage_change = ((value - previous_value) / previous_value * 100)
                elif value < previous_value:
                    kpi.trend = TrendDirection.DOWN
                    kpi.percentage_change = ((value - previous_value) / previous_value * 100)
                else:
                    kpi.trend = TrendDirection.STABLE
                    kpi.percentage_change = 0

            # Store in history
            self._store_history(kpi.kpi_id, value, context)

            logger.debug(f"Evaluated KPI {kpi.name}: {value}")
            return kpi

        except Exception as e:
            logger.error(f"Error evaluating KPI {kpi.name}: {str(e)}")
            raise KPITrackerError(f"Failed to evaluate KPI: {str(e)}")

    async def check_alerts(
        self,
        kpi: KPI,
    ) -> List[KPIAlert]:
        """
        Check if KPI exceeds alert thresholds

        Args:
            kpi: KPI to check

        Returns:
            List of triggered alerts
        """
        alerts = []

        if not kpi.alert_enabled or kpi.current_value is None:
            return alerts

        if kpi.alert_threshold is not None:
            if kpi.current_value > kpi.alert_threshold:
                alert = KPIAlert(
                    kpi_id=kpi.kpi_id,
                    severity=AlertSeverity.WARNING,
                    message=f"{kpi.name} exceeded threshold: {kpi.current_value} > {kpi.alert_threshold}",
                    threshold_value=kpi.alert_threshold,
                    actual_value=kpi.current_value,
                )
                alerts.append(alert)
                self._store_alert(kpi.kpi_id, alert)

        if kpi.min_value is not None and kpi.current_value < kpi.min_value:
            alert = KPIAlert(
                kpi_id=kpi.kpi_id,
                severity=AlertSeverity.CRITICAL,
                message=f"{kpi.name} below minimum: {kpi.current_value} < {kpi.min_value}",
                threshold_value=kpi.min_value,
                actual_value=kpi.current_value,
            )
            alerts.append(alert)
            self._store_alert(kpi.kpi_id, alert)

        if kpi.max_value is not None and kpi.current_value > kpi.max_value:
            alert = KPIAlert(
                kpi_id=kpi.kpi_id,
                severity=AlertSeverity.CRITICAL,
                message=f"{kpi.name} exceeds maximum: {kpi.current_value} > {kpi.max_value}",
                threshold_value=kpi.max_value,
                actual_value=kpi.current_value,
            )
            alerts.append(alert)
            self._store_alert(kpi.kpi_id, alert)

        return alerts

    async def get_trend(
        self,
        kpi_id: str,
        period: int = 10,
    ) -> Optional[TrendDirection]:
        """
        Calculate trend direction based on history

        Args:
            kpi_id: KPI ID
            period: Number of historical points to consider

        Returns:
            Trend direction
        """
        history = self.get_history(kpi_id, limit=period)
        if len(history) < 2:
            return None

        values = [h.value for h in history]
        first = values[0]
        last = values[-1]

        if last > first:
            return TrendDirection.UP
        elif last < first:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE

    async def get_moving_average(
        self,
        kpi_id: str,
        window: int = 5,
    ) -> Optional[float]:
        """
        Calculate moving average for KPI

        Args:
            kpi_id: KPI ID
            window: Window size

        Returns:
            Moving average value
        """
        history = self.get_history(kpi_id, limit=window)
        if not history:
            return None

        values = [h.value for h in history]
        return sum(values) / len(values)

    async def get_volatility(
        self,
        kpi_id: str,
        window: int = 10,
    ) -> Optional[float]:
        """
        Calculate volatility (standard deviation)

        Args:
            kpi_id: KPI ID
            window: Window size

        Returns:
            Standard deviation of values
        """
        history = self.get_history(kpi_id, limit=window)
        if len(history) < 2:
            return None

        values = [h.value for h in history]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    async def compare_to_target(
        self,
        kpi: KPI,
    ) -> Optional[float]:
        """
        Compare current KPI value to target

        Args:
            kpi: KPI object

        Returns:
            Percentage to target (100 = at target)
        """
        if kpi.current_value is None or kpi.target_value is None:
            return None

        if kpi.target_value == 0:
            return None

        percentage = (kpi.current_value / kpi.target_value) * 100
        return round(percentage, 2)

    async def forecast(
        self,
        kpi_id: str,
        periods: int = 5,
    ) -> Optional[List[float]]:
        """
        Simple linear regression forecast

        Args:
            kpi_id: KPI ID
            periods: Number of periods to forecast

        Returns:
            Forecasted values
        """
        history = self.get_history(kpi_id, limit=20)
        if len(history) < 2:
            return None

        values = [h.value for h in history]
        n = len(values)

        # Calculate slope and intercept
        x = list(range(n))
        y = values

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return None

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Forecast
        forecast = []
        for i in range(n, n + periods):
            predicted = slope * i + intercept
            forecast.append(predicted)

        return forecast

    def get_history(
        self,
        kpi_id: str,
        limit: Optional[int] = None,
    ) -> List[KPIHistory]:
        """Get KPI history"""
        if kpi_id not in self.kpi_history:
            return []

        history = list(self.kpi_history[kpi_id])
        if limit:
            history = history[-limit:]

        return history

    def get_alerts(
        self,
        kpi_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[KPIAlert]:
        """Get alerts for KPI or all KPIs"""
        if kpi_id:
            alerts = self.alerts.get(kpi_id, [])
        else:
            alerts = []
            for kpi_alerts in self.alerts.values():
                alerts.extend(kpi_alerts)

        # Sort by timestamp descending
        alerts.sort(key=lambda a: a.triggered_at, reverse=True)

        if limit:
            alerts = alerts[:limit]

        return alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for kpi_alerts in self.alerts.values():
            for alert in kpi_alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    return True
        return False

    def _store_history(
        self,
        kpi_id: str,
        value: float,
        context: Dict[str, Any],
    ) -> None:
        """Store KPI value in history"""
        if kpi_id not in self.kpi_history:
            self.kpi_history[kpi_id] = deque(maxlen=self.history_limit)

        history_entry = KPIHistory(
            kpi_id=kpi_id,
            value=value,
            timestamp=datetime.utcnow(),
            context=context,
        )

        self.kpi_history[kpi_id].append(history_entry)

    def _store_alert(self, kpi_id: str, alert: KPIAlert) -> None:
        """Store alert"""
        if kpi_id not in self.alerts:
            self.alerts[kpi_id] = []

        self.alerts[kpi_id].append(alert)

        # Keep only recent alerts
        self.alerts[kpi_id] = self.alerts[kpi_id][-100:]


class AlertEngine:
    """
    Advanced alert engine with notification support
    """

    def __init__(self):
        """Initialize alert engine"""
        self.alert_rules: Dict[str, Dict[str, Any]] = {}

    async def create_rule(
        self,
        rule_id: str,
        kpi_id: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity = AlertSeverity.WARNING,
        notification_channels: Optional[List[str]] = None,
    ) -> None:
        """
        Create alert rule

        Args:
            rule_id: Rule identifier
            kpi_id: KPI to monitor
            condition: Condition string (">", "<", ">=", "<=", "==", "!=")
            threshold: Threshold value
            severity: Alert severity
            notification_channels: Where to send alerts
        """
        self.alert_rules[rule_id] = {
            "kpi_id": kpi_id,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "notification_channels": notification_channels or [],
            "created_at": datetime.utcnow(),
        }

        logger.info(f"Created alert rule: {rule_id}")

    async def evaluate_rules(
        self,
        kpi: KPI,
    ) -> List[KPIAlert]:
        """
        Evaluate all rules for a KPI

        Args:
            kpi: KPI to evaluate

        Returns:
            List of triggered alerts
        """
        alerts = []

        for rule_id, rule in self.alert_rules.items():
            if rule["kpi_id"] != kpi.kpi_id:
                continue

            if await self._evaluate_condition(
                kpi.current_value,
                rule["condition"],
                rule["threshold"],
            ):
                alert = KPIAlert(
                    kpi_id=kpi.kpi_id,
                    severity=rule["severity"],
                    message=f"Rule '{rule_id}' triggered: {kpi.name} {rule['condition']} {rule['threshold']}",
                    threshold_value=rule["threshold"],
                    actual_value=kpi.current_value,
                )
                alerts.append(alert)

        return alerts

    async def _evaluate_condition(
        self,
        value: Optional[float],
        condition: str,
        threshold: float,
    ) -> bool:
        """Evaluate a condition"""
        if value is None:
            return False

        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            return False


__all__ = [
    "KPITracker",
    "KPITrackerError",
    "AlertEngine",
]

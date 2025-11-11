"""
Root Cause Analysis for Monitoring Alerts

Analyzes alert changes to identify root causes, contributing factors,
and actionable recommendations with mitigation strategies.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

from consultantos.models.monitoring import Alert, Change, ChangeType

logger = logging.getLogger(__name__)


class CauseFactor(BaseModel):
    """Contributing factor to a change"""
    factor: str = Field(description="Description of contributing factor")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence this is a root cause")
    category: str = Field(description="internal, external, market, competitive, etc.")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")


class RootCauseAnalysis(BaseModel):
    """Root cause analysis result"""
    primary_cause: str = Field(description="Most likely root cause")
    contributing_factors: List[CauseFactor] = Field(default_factory=list)
    impact_assessment: str = Field(description="Expected impact if not addressed")
    recommended_actions: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)
    time_to_impact: Optional[str] = None  # "immediate", "short-term", "medium-term"
    severity: str = Field(description="critical, high, medium, low")


class EnhancedAlertExplanation(BaseModel):
    """Enhanced alert with root cause explanation"""
    alert_id: str
    summary: str = Field(description="Executive summary of the alert")

    # What happened
    what_happened: List[str] = Field(description="List of changes detected")

    # Why it matters
    why_it_matters: str = Field(description="Business impact explanation")

    # Root cause
    root_cause_analysis: RootCauseAnalysis

    # What to do
    recommended_actions: List[Dict[str, str]] = Field(
        description="Prioritized actions with owner, timeline, expected outcome"
    )

    # Context
    historical_context: Optional[str] = None
    related_alerts: List[str] = Field(default_factory=list)


class RootCauseAnalyzer:
    """
    Analyzes alerts to determine root causes and provide actionable insights.

    Uses pattern matching, correlation analysis, and domain knowledge to
    identify underlying causes of changes.
    """

    def __init__(self):
        self.logger = logger

        # Knowledge base of common patterns
        self.cause_patterns = self._build_cause_patterns()

    def analyze_alert(
        self,
        alert: Alert,
        historical_data: Optional[Dict] = None
    ) -> EnhancedAlertExplanation:
        """
        Perform root cause analysis on an alert.

        Args:
            alert: Alert to analyze
            historical_data: Optional historical context

        Returns:
            Enhanced alert explanation with root cause analysis
        """
        # Analyze changes to identify root causes
        root_cause = self._identify_root_cause(alert.changes_detected, historical_data)

        # Generate "what happened" summary
        what_happened = [
            f"{change.title} ({change.change_type.value})"
            for change in alert.changes_detected
        ]

        # Determine business impact
        why_it_matters = self._assess_business_impact(alert.changes_detected, root_cause)

        # Generate prioritized actions
        recommended_actions = self._generate_prioritized_actions(
            alert.changes_detected,
            root_cause
        )

        # Create executive summary
        summary = self._create_executive_summary(alert, root_cause)

        # Find related alerts
        related_alerts = self._find_related_alerts(alert, historical_data)

        # Historical context
        historical_context = self._build_historical_context(alert, historical_data)

        return EnhancedAlertExplanation(
            alert_id=alert.id,
            summary=summary,
            what_happened=what_happened,
            why_it_matters=why_it_matters,
            root_cause_analysis=root_cause,
            recommended_actions=recommended_actions,
            historical_context=historical_context,
            related_alerts=related_alerts
        )

    def _identify_root_cause(
        self,
        changes: List[Change],
        historical_data: Optional[Dict]
    ) -> RootCauseAnalysis:
        """Identify root cause from changes"""

        # Analyze change types
        change_types = [c.change_type for c in changes]

        # Pattern matching
        primary_cause, confidence = self._match_cause_pattern(change_types, changes)

        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(changes)

        # Assess impact
        impact_assessment = self._assess_impact(changes)

        # Determine time to impact
        time_to_impact = self._estimate_time_to_impact(changes)

        # Determine severity
        severity = self._calculate_severity(changes)

        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(
            primary_cause,
            change_types
        )

        # Generate recommendations
        recommended_actions = self._generate_recommendations(
            primary_cause,
            change_types
        )

        return RootCauseAnalysis(
            primary_cause=primary_cause,
            contributing_factors=contributing_factors,
            impact_assessment=impact_assessment,
            recommended_actions=recommended_actions,
            mitigation_strategies=mitigation_strategies,
            time_to_impact=time_to_impact,
            severity=severity
        )

    def _match_cause_pattern(
        self,
        change_types: List[ChangeType],
        changes: List[Change]
    ) -> Tuple[str, float]:
        """Match changes to known cause patterns"""

        # Pattern 1: Competitive pressure
        if (ChangeType.COMPETITIVE_LANDSCAPE in change_types and
            ChangeType.MARKET_TREND in change_types):
            return (
                "Increased competitive pressure from new market entrants or competitor actions",
                0.85
            )

        # Pattern 2: Market shift
        if ChangeType.MARKET_TREND in change_types:
            # Check for demand-related keywords in changes
            demand_keywords = ['demand', 'adoption', 'growth', 'decline']
            has_demand_signal = any(
                any(keyword in change.description.lower() for keyword in demand_keywords)
                for change in changes
            )
            if has_demand_signal:
                return (
                    "Market demand shift driven by changing customer preferences or external factors",
                    0.80
                )

        # Pattern 3: Financial performance issue
        if ChangeType.FINANCIAL_METRIC in change_types:
            return (
                "Financial performance deviation indicating operational or market challenges",
                0.75
            )

        # Pattern 4: Regulatory change
        if ChangeType.REGULATORY in change_types:
            return (
                "Regulatory environment change requiring compliance and strategic adjustments",
                0.90
            )

        # Pattern 5: Strategic realignment
        if ChangeType.STRATEGIC_SHIFT in change_types:
            return (
                "Internal strategic realignment or pivot in response to market conditions",
                0.70
            )

        # Pattern 6: Technology disruption
        if ChangeType.TECHNOLOGY in change_types:
            return (
                "Technological advancement creating disruption or new opportunities",
                0.75
            )

        # Pattern 7: Leadership change
        if ChangeType.LEADERSHIP in change_types:
            return (
                "Leadership transition driving organizational and strategic changes",
                0.80
            )

        # Default: Multiple factors
        return (
            f"Multiple contributing factors across {len(set(change_types))} areas",
            0.65
        )

    def _identify_contributing_factors(self, changes: List[Change]) -> List[CauseFactor]:
        """Identify all contributing factors"""
        factors = []

        change_types = [c.change_type for c in changes]

        # Internal factors
        internal_types = [ChangeType.STRATEGIC_SHIFT, ChangeType.LEADERSHIP, ChangeType.FINANCIAL_METRIC]
        internal_changes = [c for c in changes if c.change_type in internal_types]
        if internal_changes:
            factors.append(CauseFactor(
                factor="Internal operational or strategic decisions",
                confidence=0.7,
                category="internal",
                evidence=[c.title for c in internal_changes]
            ))

        # External market factors
        market_types = [ChangeType.MARKET_TREND, ChangeType.COMPETITIVE_LANDSCAPE]
        market_changes = [c for c in changes if c.change_type in market_types]
        if market_changes:
            factors.append(CauseFactor(
                factor="External market dynamics and competitive forces",
                confidence=0.8,
                category="market",
                evidence=[c.title for c in market_changes]
            ))

        # Regulatory factors
        if ChangeType.REGULATORY in change_types:
            reg_changes = [c for c in changes if c.change_type == ChangeType.REGULATORY]
            factors.append(CauseFactor(
                factor="Regulatory compliance requirements",
                confidence=0.9,
                category="regulatory",
                evidence=[c.title for c in reg_changes]
            ))

        # Technology factors
        if ChangeType.TECHNOLOGY in change_types:
            tech_changes = [c for c in changes if c.change_type == ChangeType.TECHNOLOGY]
            factors.append(CauseFactor(
                factor="Technological advancement or disruption",
                confidence=0.75,
                category="technology",
                evidence=[c.title for c in tech_changes]
            ))

        return factors

    def _assess_impact(self, changes: List[Change]) -> str:
        """Assess expected impact if not addressed"""

        change_types = [c.change_type for c in changes]
        high_impact_types = [
            ChangeType.COMPETITIVE_LANDSCAPE,
            ChangeType.REGULATORY,
            ChangeType.STRATEGIC_SHIFT,
            ChangeType.FINANCIAL_METRIC
        ]

        critical_count = sum(1 for ct in change_types if ct in high_impact_types)

        if critical_count >= 3:
            return (
                "CRITICAL IMPACT: Multiple high-severity changes requiring immediate executive attention. "
                "Failure to address could result in significant market share loss, regulatory penalties, "
                "or strategic misalignment within 3-6 months."
            )
        elif critical_count >= 2:
            return (
                "HIGH IMPACT: Significant changes that could affect competitive position and financial "
                "performance. Recommend strategic review within 2-4 weeks to mitigate risks."
            )
        elif critical_count >= 1:
            return (
                "MODERATE IMPACT: Important changes requiring monitoring and potential tactical adjustments. "
                "Address within 1-2 months to prevent escalation."
            )
        else:
            return (
                "LOW IMPACT: Minor changes for awareness and tracking. "
                "Monitor trends but no immediate action required."
            )

    def _estimate_time_to_impact(self, changes: List[Change]) -> str:
        """Estimate how soon impact will be felt"""

        change_types = [c.change_type for c in changes]

        # Immediate impact types
        immediate_types = [ChangeType.REGULATORY, ChangeType.FINANCIAL_METRIC]
        if any(ct in immediate_types for ct in change_types):
            return "immediate"

        # Short-term (1-3 months)
        short_term_types = [ChangeType.COMPETITIVE_LANDSCAPE, ChangeType.LEADERSHIP]
        if any(ct in short_term_types for ct in change_types):
            return "short-term"

        # Medium-term (3-12 months)
        return "medium-term"

    def _calculate_severity(self, changes: List[Change]) -> str:
        """Calculate overall severity"""

        # Count high-confidence changes
        high_conf_count = sum(1 for c in changes if c.confidence >= 0.8)
        total_count = len(changes)

        if high_conf_count >= 3 or (high_conf_count >= 2 and total_count >= 4):
            return "critical"
        elif high_conf_count >= 2 or total_count >= 3:
            return "high"
        elif high_conf_count >= 1 or total_count >= 2:
            return "medium"
        else:
            return "low"

    def _generate_mitigation_strategies(
        self,
        primary_cause: str,
        change_types: List[ChangeType]
    ) -> List[str]:
        """Generate mitigation strategies"""
        strategies = []

        if ChangeType.COMPETITIVE_LANDSCAPE in change_types:
            strategies.append(
                "Conduct competitive intelligence deep-dive to understand competitor strategies and intentions"
            )
            strategies.append(
                "Accelerate product roadmap to maintain competitive differentiation"
            )

        if ChangeType.MARKET_TREND in change_types:
            strategies.append(
                "Launch targeted market research to validate demand trends and customer sentiment"
            )
            strategies.append(
                "Consider strategic pivot or product repositioning based on market signals"
            )

        if ChangeType.FINANCIAL_METRIC in change_types:
            strategies.append(
                "Implement cost optimization initiatives to improve margins"
            )
            strategies.append(
                "Review pricing strategy and value proposition alignment"
            )

        if ChangeType.REGULATORY in change_types:
            strategies.append(
                "Engage compliance team and legal counsel for regulatory impact assessment"
            )
            strategies.append(
                "Develop compliance roadmap with clear milestones and accountability"
            )

        # Default strategies
        if not strategies:
            strategies.append(
                "Establish cross-functional task force to assess situation and develop response plan"
            )
            strategies.append(
                "Increase monitoring frequency to detect further changes early"
            )

        return strategies

    def _generate_recommendations(
        self,
        primary_cause: str,
        change_types: List[ChangeType]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []

        # Always recommend monitoring
        recs.append("Increase monitoring frequency to 2x current cadence for early detection")

        # Type-specific recommendations
        if ChangeType.COMPETITIVE_LANDSCAPE in change_types:
            recs.append("Schedule competitive strategy review with executive team within 2 weeks")

        if ChangeType.FINANCIAL_METRIC in change_types:
            recs.append("Conduct financial variance analysis to identify drivers")

        if ChangeType.REGULATORY in change_types:
            recs.append("Initiate compliance gap analysis and remediation planning")

        return recs

    def _assess_business_impact(
        self,
        changes: List[Change],
        root_cause: RootCauseAnalysis
    ) -> str:
        """Assess why this matters to the business"""

        # Extract key metrics
        severity = root_cause.severity
        time_to_impact = root_cause.time_to_impact

        impact_statement = f"This alert indicates {severity}-severity changes with {time_to_impact} impact. "

        # Add specific impact based on change types
        change_types = [c.change_type for c in changes]

        if ChangeType.COMPETITIVE_LANDSCAPE in change_types:
            impact_statement += (
                "Competitive position may be at risk, potentially affecting market share and pricing power. "
            )

        if ChangeType.FINANCIAL_METRIC in change_types:
            impact_statement += (
                "Financial performance deviation could impact investor confidence and strategic initiatives. "
            )

        if ChangeType.REGULATORY in change_types:
            impact_statement += (
                "Regulatory changes may require significant compliance investments and operational adjustments. "
            )

        impact_statement += root_cause.impact_assessment

        return impact_statement

    def _generate_prioritized_actions(
        self,
        changes: List[Change],
        root_cause: RootCauseAnalysis
    ) -> List[Dict[str, str]]:
        """Generate prioritized action items"""
        actions = []

        # Action 1: Immediate assessment
        actions.append({
            "priority": "1 - URGENT",
            "action": f"Assess root cause: {root_cause.primary_cause}",
            "owner": "Strategy Team",
            "timeline": "24-48 hours",
            "expected_outcome": "Clear understanding of situation and impact scope"
        })

        # Action 2: Mitigation
        if root_cause.mitigation_strategies:
            actions.append({
                "priority": "2 - HIGH",
                "action": root_cause.mitigation_strategies[0],
                "owner": "Operations/Strategy",
                "timeline": "1-2 weeks",
                "expected_outcome": "Risk mitigation and containment"
            })

        # Action 3: Strategic response
        actions.append({
            "priority": "3 - MEDIUM",
            "action": "Develop strategic response plan with clear KPIs",
            "owner": "Executive Team",
            "timeline": "2-4 weeks",
            "expected_outcome": "Comprehensive response strategy with accountability"
        })

        return actions

    def _create_executive_summary(self, alert: Alert, root_cause: RootCauseAnalysis) -> str:
        """Create executive-friendly summary"""

        change_count = len(alert.changes_detected)
        severity = root_cause.severity.upper()

        summary = (
            f"🔔 {severity} ALERT: {change_count} significant changes detected for {alert.monitor_id}. "
            f"Root cause: {root_cause.primary_cause}. "
            f"Impact: {root_cause.time_to_impact} ({root_cause.impact_assessment[:100]}...). "
            f"Recommended action: {root_cause.recommended_actions[0] if root_cause.recommended_actions else 'Review and assess'}."
        )

        return summary

    def _find_related_alerts(
        self,
        alert: Alert,
        historical_data: Optional[Dict]
    ) -> List[str]:
        """Find related historical alerts"""
        # In production, query database for alerts with similar patterns
        # For now, return placeholder
        return []

    def _build_historical_context(
        self,
        alert: Alert,
        historical_data: Optional[Dict]
    ) -> str:
        """Build historical context"""
        if not historical_data:
            return "No historical context available for comparison."

        # In production, analyze historical trends
        return "Historical analysis pending - increase monitoring frequency to build trend data."

    def _build_cause_patterns(self) -> Dict:
        """Build knowledge base of common cause patterns"""
        # In production, this could be ML-based or loaded from a database
        return {
            "competitive_pressure": {
                "signals": [ChangeType.COMPETITIVE_LANDSCAPE, ChangeType.MARKET_TREND],
                "confidence": 0.85
            },
            "market_shift": {
                "signals": [ChangeType.MARKET_TREND],
                "confidence": 0.80
            }
            # Add more patterns as we learn
        }

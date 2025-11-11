"""
Tests for Root Cause Analyzer
"""
import pytest
from datetime import datetime
from consultantos.monitoring.root_cause_analyzer import (
    RootCauseAnalyzer,
    RootCauseAnalysis,
    CauseFactor,
    EnhancedAlertExplanation
)
from consultantos.models.monitoring import Alert, Change, ChangeType, MonitorStatus


@pytest.fixture
def analyzer():
    """Create a root cause analyzer instance"""
    return RootCauseAnalyzer()


@pytest.fixture
def sample_alert():
    """Create a sample alert for testing"""
    changes = [
        Change(
            title="Revenue decreased by 15%",
            change_type=ChangeType.FINANCIAL_METRIC,
            description="Revenue dropped from 100M to 85M",
            previous_value="100M",
            current_value="85M",
            confidence=0.9,
            detected_at=datetime.utcnow()
        ),
        Change(
            title="Market share declined",
            change_type=ChangeType.MARKET_TREND,
            description="Market share dropped from 25% to 20%",
            previous_value="25%",
            current_value="20%",
            confidence=0.85,
            detected_at=datetime.utcnow()
        )
    ]
    
    return Alert(
        id="alert_123",
        monitor_id="monitor_123",
        title="Significant Revenue Decline Detected",
        summary="Revenue and market share have declined",
        changes_detected=changes,
        confidence=0.88,
        created_at=datetime.utcnow(),
        severity="high"
    )


class TestRootCauseAnalyzer:
    """Tests for RootCauseAnalyzer class"""

    @pytest.mark.asyncio
    async def test_analyze_alert_basic(self, analyzer, sample_alert):
        """Test basic alert analysis"""
        result = analyzer.analyze_alert(sample_alert)
        
        assert isinstance(result, EnhancedAlertExplanation)
        assert result.alert_id == "alert_123"
        assert result.summary is not None
        assert len(result.what_happened) > 0
        assert result.why_it_matters is not None
        assert isinstance(result.root_cause_analysis, RootCauseAnalysis)
        assert result.root_cause_analysis.primary_cause is not None

    @pytest.mark.asyncio
    async def test_analyze_alert_with_historical_data(self, analyzer, sample_alert):
        """Test alert analysis with historical context"""
        historical = {
            "previous_alerts": ["alert_001", "alert_002"],
            "trend": "declining"
        }
        
        result = analyzer.analyze_alert(sample_alert, historical_data=historical)
        
        assert result.root_cause_analysis is not None
        assert len(result.recommended_actions) > 0

    def test_identify_root_cause_financial(self, analyzer, sample_alert):
        """Test root cause identification for financial changes"""
        changes = sample_alert.changes_detected
        root_cause = analyzer._identify_root_cause(changes, None)
        
        assert root_cause is not None
        assert isinstance(root_cause, RootCauseAnalysis)
        assert root_cause.primary_cause is not None
        assert root_cause.severity in ["critical", "high", "medium", "low"]

    def test_identify_root_cause_market(self, analyzer):
        """Test root cause identification for market changes"""
        changes = [
            Change(
                title="Competitor launched new product",
                change_type=ChangeType.COMPETITIVE_LANDSCAPE,
                description="Major competitor launched disruptive product",
                previous_value="stable",
                current_value="disrupted",
                confidence=0.9,
                detected_at=datetime.utcnow()
            )
        ]
        
        root_cause = analyzer._identify_root_cause(changes, None)
        
        assert root_cause is not None
        # Check that contributing factors contain competitive/market info
        assert len(root_cause.contributing_factors) > 0
        # At least one factor should mention competitive or market
        factors_text = " ".join([f.factor.lower() for f in root_cause.contributing_factors])
        assert "competitive" in factors_text or "market" in factors_text or "competitor" in factors_text

    def test_assess_business_impact(self, analyzer, sample_alert):
        """Test business impact assessment"""
        root_cause = analyzer._identify_root_cause(sample_alert.changes_detected, None)
        impact = analyzer._assess_business_impact(sample_alert.changes_detected, root_cause)
        
        assert impact is not None
        assert len(impact) > 0

    def test_generate_mitigation_strategies(self, analyzer, sample_alert):
        """Test mitigation strategy generation"""
        root_cause = analyzer._identify_root_cause(sample_alert.changes_detected, None)
        strategies = analyzer._generate_mitigation_strategies(root_cause, sample_alert.changes_detected)
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all(isinstance(s, str) for s in strategies)

    def test_analyze_alert_graceful_degradation(self, analyzer):
        """Test that analyzer handles invalid input gracefully"""
        # Create invalid alert
        invalid_alert = Alert(
            id="invalid",
            monitor_id="monitor_123",
            title="Test",
            summary="Test",
            changes_detected=[],
            confidence=0.5,
            created_at=datetime.utcnow(),
            severity="low"
        )
        
        # Should not raise exception
        result = analyzer.analyze_alert(invalid_alert)
        assert result is not None
        assert result.alert_id == "invalid"


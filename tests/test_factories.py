"""
Tests for Faker-based test data factories.

Validates that factories generate valid, realistic data conforming to
Pydantic models and business logic constraints.
"""

import pytest
from datetime import datetime
from consultantos.models import (
    AnalysisRequest,
    CompanyResearch,
    MarketTrends,
    FinancialSnapshot,
    PortersFiveForces,
    SWOTAnalysis,
    PESTELAnalysis,
    BlueOceanStrategy
)
from consultantos.models.monitoring import (
    MonitoringConfig,
    Monitor,
    Change,
    Alert,
    MonitoringFrequency,
    MonitorStatus,
    ChangeType
)
from tests.factories import ConsultantOSFactory


class TestConsultantOSFactory:
    """Test suite for ConsultantOSFactory"""

    def test_factory_with_seed_reproducibility(self):
        """Factories with same seed produce identical sequences"""
        factory1 = ConsultantOSFactory(seed=42)
        factory2 = ConsultantOSFactory(seed=42)

        req1 = factory1.analysis_request()
        req2 = factory2.analysis_request()

        assert req1["company"] == req2["company"]
        assert req1["industry"] == req2["industry"]
        assert req1["frameworks"] == req2["frameworks"]
        assert req1["depth"] == req2["depth"]

    def test_factory_without_seed_variability(self):
        """Factories without seed produce different data"""
        factory1 = ConsultantOSFactory()
        factory2 = ConsultantOSFactory()

        companies = [factory1.analysis_request()["company"] for _ in range(10)]
        companies2 = [factory2.analysis_request()["company"] for _ in range(10)]

        # Very unlikely to be identical if truly random
        assert companies != companies2


class TestAnalysisRequestFactory:
    """Test analysis request generation"""

    def test_analysis_request_valid_structure(self, factory):
        """Generated analysis request has valid structure"""
        data = factory.analysis_request()

        assert "company" in data
        assert "industry" in data
        assert "frameworks" in data
        assert "depth" in data

    def test_analysis_request_validates_with_pydantic(self, factory):
        """Generated data validates with AnalysisRequest model"""
        data = factory.analysis_request()
        request = AnalysisRequest(**data)

        assert request.company == data["company"]
        assert request.industry == data["industry"]
        assert request.frameworks == data["frameworks"]
        assert request.depth == data["depth"]

    def test_analysis_request_custom_company(self, factory):
        """Can override company name"""
        data = factory.analysis_request(company="CustomCorp")
        assert data["company"] == "CustomCorp"

    def test_analysis_request_custom_frameworks(self, factory):
        """Can override frameworks list"""
        frameworks = ["porter", "swot"]
        data = factory.analysis_request(frameworks=frameworks)
        assert data["frameworks"] == frameworks

    def test_analysis_request_depth_values(self, factory):
        """Depth is one of valid values"""
        valid_depths = {"quick", "standard", "deep"}
        data = factory.analysis_request()
        assert data["depth"] in valid_depths

    def test_analysis_request_frameworks_valid(self, factory):
        """All generated frameworks are valid"""
        valid_frameworks = {
            "porter", "swot", "pestel", "blue_ocean",
            "ansoff", "bcg_matrix", "value_chain"
        }
        data = factory.analysis_request()
        assert all(fw in valid_frameworks for fw in data["frameworks"])
        assert len(data["frameworks"]) >= 2  # At least 2 frameworks


class TestCompanyResearchFactory:
    """Test company research generation"""

    def test_company_research_valid_structure(self, factory):
        """Generated company research has valid structure"""
        data = factory.company_research()

        assert "company_name" in data
        assert "description" in data
        assert "products_services" in data
        assert "target_market" in data
        assert "key_competitors" in data
        assert "recent_news" in data
        assert "sources" in data

    def test_company_research_validates_with_pydantic(self, factory):
        """Generated data validates with CompanyResearch model"""
        data = factory.company_research()
        research = CompanyResearch(**data)

        assert research.company_name == data["company_name"]
        assert len(research.products_services) >= 2
        assert len(research.key_competitors) >= 3
        assert len(research.sources) >= 5

    def test_company_research_custom_company(self, factory):
        """Can override company name"""
        data = factory.company_research(company_name="TechCorp")
        assert data["company_name"] == "TechCorp"

    def test_company_research_list_lengths(self, factory):
        """Lists have reasonable lengths"""
        data = factory.company_research()

        assert 2 <= len(data["products_services"]) <= 5
        assert 3 <= len(data["key_competitors"]) <= 7
        assert 3 <= len(data["recent_news"]) <= 6
        assert 5 <= len(data["sources"]) <= 10


class TestFinancialSnapshotFactory:
    """Test financial snapshot generation"""

    def test_financial_snapshot_valid_structure(self, factory):
        """Generated financial snapshot has valid structure"""
        data = factory.financial_snapshot()

        assert "ticker" in data
        assert "market_cap" in data
        assert "revenue" in data
        assert "revenue_growth" in data
        assert "profit_margin" in data
        assert "risk_assessment" in data

    def test_financial_snapshot_validates_with_pydantic(self, factory):
        """Generated data validates with FinancialSnapshot model"""
        data = factory.financial_snapshot()
        snapshot = FinancialSnapshot(**data)

        assert snapshot.ticker == data["ticker"]
        assert snapshot.market_cap == data["market_cap"]

    def test_financial_snapshot_market_cap_realistic(self, factory):
        """Market cap values are realistic for company size"""
        # Mid-sized company should have market cap between $2B and $10B
        data = factory.financial_snapshot(company_size="mid")
        assert 2e9 <= data["market_cap"] <= 10e9

        # Large company should have market cap between $10B and $200B
        data = factory.financial_snapshot(company_size="large")
        assert 10e9 <= data["market_cap"] <= 200e9

    def test_financial_snapshot_pe_ratio_optional(self, factory):
        """P/E ratio can be None (unprofitable companies)"""
        # Generate multiple to test optional nature
        snapshots = [factory.financial_snapshot() for _ in range(20)]
        pe_ratios = [s["pe_ratio"] for s in snapshots]

        # Some should be None (unprofitable)
        assert any(pe is None for pe in pe_ratios)
        # Most should have value
        assert any(pe is not None for pe in pe_ratios)


class TestFrameworkFactories:
    """Test business framework generation"""

    def test_porters_five_forces_valid_structure(self, factory):
        """Generated Porter's Five Forces has valid structure"""
        data = factory.porters_five_forces()

        # Check all forces present
        assert "supplier_power" in data
        assert "buyer_power" in data
        assert "competitive_rivalry" in data
        assert "threat_of_substitutes" in data
        assert "threat_of_new_entrants" in data
        assert "overall_intensity" in data
        assert "detailed_analysis" in data

    def test_porters_five_forces_validates_with_pydantic(self, factory):
        """Generated data validates with PortersFiveForces model"""
        data = factory.porters_five_forces()
        forces = PortersFiveForces(**data)

        assert 1 <= forces.supplier_power <= 5
        assert 1 <= forces.buyer_power <= 5
        assert 1 <= forces.competitive_rivalry <= 5
        assert 1 <= forces.threat_of_substitutes <= 5
        assert 1 <= forces.threat_of_new_entrants <= 5
        assert forces.overall_intensity in ["Low", "Moderate", "High"]

    def test_swot_analysis_valid_structure(self, factory):
        """Generated SWOT analysis has valid structure"""
        data = factory.swot_analysis()

        assert "strengths" in data
        assert "weaknesses" in data
        assert "opportunities" in data
        assert "threats" in data

    def test_swot_analysis_validates_with_pydantic(self, factory):
        """Generated data validates with SWOTAnalysis model"""
        data = factory.swot_analysis()
        swot = SWOTAnalysis(**data)

        # Each quadrant should have 3-5 items
        assert 3 <= len(swot.strengths) <= 5
        assert 3 <= len(swot.weaknesses) <= 5
        assert 3 <= len(swot.opportunities) <= 5
        assert 3 <= len(swot.threats) <= 5

    def test_pestel_analysis_validates_with_pydantic(self, factory):
        """Generated data validates with PESTELAnalysis model"""
        data = factory.pestel_analysis()
        pestel = PESTELAnalysis(**data)

        # Check all dimensions present
        assert len(pestel.political) >= 2
        assert len(pestel.economic) >= 2
        assert len(pestel.social) >= 2
        assert len(pestel.technological) >= 2
        assert len(pestel.environmental) >= 2
        assert len(pestel.legal) >= 2

    def test_blue_ocean_strategy_validates_with_pydantic(self, factory):
        """Generated data validates with BlueOceanStrategy model"""
        data = factory.blue_ocean_strategy()
        bos = BlueOceanStrategy(**data)

        # Check all four actions present
        assert len(bos.eliminate) >= 2
        assert len(bos.reduce) >= 2
        assert len(bos.raise_factors) >= 2  # Note: uses 'raise' alias
        assert len(bos.create) >= 2


class TestMonitoringFactories:
    """Test monitoring-related generation"""

    def test_monitoring_config_valid_structure(self, factory):
        """Generated monitoring config has valid structure"""
        data = factory.monitoring_config()

        assert "frequency" in data
        assert "frameworks" in data
        assert "alert_threshold" in data
        assert "notification_channels" in data

    def test_monitoring_config_validates_with_pydantic(self, factory):
        """Generated data validates with MonitoringConfig model"""
        data = factory.monitoring_config()
        config = MonitoringConfig(**data)

        assert config.frequency in [e.value for e in MonitoringFrequency]
        assert 0.0 <= config.alert_threshold <= 1.0
        assert len(config.frameworks) >= 2

    def test_monitoring_config_alert_threshold_range(self, factory):
        """Alert threshold is in valid range"""
        configs = [factory.monitoring_config() for _ in range(10)]
        thresholds = [c["alert_threshold"] for c in configs]

        assert all(0.6 <= t <= 0.9 for t in thresholds)

    def test_monitor_valid_structure(self, factory):
        """Generated monitor has valid structure"""
        data = factory.monitor()

        assert "id" in data
        assert "user_id" in data
        assert "company" in data
        assert "industry" in data
        assert "config" in data
        assert "status" in data
        assert "created_at" in data

    def test_monitor_validates_with_pydantic(self, factory):
        """Generated data validates with Monitor model"""
        data = factory.monitor()
        monitor = Monitor(**data)

        assert monitor.status in [e.value for e in MonitorStatus]
        assert isinstance(monitor.created_at, datetime)
        assert isinstance(monitor.config, MonitoringConfig)

    def test_monitor_custom_user_id(self, factory):
        """Can override user_id"""
        user_id = "test-user-123"
        data = factory.monitor(user_id=user_id)
        assert data["user_id"] == user_id

    def test_monitor_error_status_has_error_message(self, factory):
        """Monitors with error status have error message"""
        data = factory.monitor(status="error")
        assert data["status"] == "error"
        assert data["error_count"] >= 0
        assert data["last_error"] is not None

    def test_change_valid_structure(self, factory):
        """Generated change has valid structure"""
        data = factory.change()

        assert "change_type" in data
        assert "title" in data
        assert "description" in data
        assert "confidence" in data
        assert "source_urls" in data
        assert "detected_at" in data

    def test_change_validates_with_pydantic(self, factory):
        """Generated data validates with Change model"""
        data = factory.change()
        change = Change(**data)

        assert change.change_type in [e.value for e in ChangeType]
        assert 0.0 <= change.confidence <= 1.0
        assert isinstance(change.detected_at, datetime)
        assert len(change.source_urls) >= 1

    def test_alert_valid_structure(self, factory):
        """Generated alert has valid structure"""
        data = factory.alert()

        assert "id" in data
        assert "monitor_id" in data
        assert "title" in data
        assert "summary" in data
        assert "confidence" in data
        assert "changes_detected" in data
        assert "created_at" in data
        assert "read" in data

    def test_alert_validates_with_pydantic(self, factory):
        """Generated data validates with Alert model"""
        data = factory.alert()
        alert = Alert(**data)

        assert 0.0 <= alert.confidence <= 1.0
        assert isinstance(alert.created_at, datetime)
        assert len(alert.changes_detected) >= 1
        assert isinstance(alert.read, bool)


class TestBulkGeneration:
    """Test bulk data generation"""

    def test_analysis_requests_bulk(self, factory):
        """Can generate multiple analysis requests"""
        requests = factory.analysis_requests(count=10)

        assert len(requests) == 10
        # All should be valid
        for req_data in requests:
            request = AnalysisRequest(**req_data)
            assert request is not None

    def test_monitors_bulk_same_user(self, factory):
        """Bulk monitors share same user_id"""
        user_id = "test-user-123"
        monitors = factory.monitors(count=5, user_id=user_id)

        assert len(monitors) == 5
        assert all(m["user_id"] == user_id for m in monitors)

    def test_alerts_bulk_same_monitor(self, factory):
        """Bulk alerts share same monitor_id"""
        monitor_id = "test-monitor-123"
        alerts = factory.alerts(count=5, monitor_id=monitor_id)

        assert len(alerts) == 5
        assert all(a["monitor_id"] == monitor_id for a in alerts)


class TestEdgeCases:
    """Test edge case generation"""

    def test_edge_case_company_names(self, factory):
        """Edge case company names cover validation boundaries"""
        # Minimum valid length
        min_name = factory.edge_case_company_name("min_length")
        assert len(min_name) == 2

        # Maximum valid length
        max_name = factory.edge_case_company_name("max_length")
        assert len(max_name) == 200

        # Empty (invalid)
        empty_name = factory.edge_case_company_name("empty")
        assert empty_name == ""

        # Too short (invalid)
        too_short = factory.edge_case_company_name("too_short")
        assert len(too_short) < 2

        # Too long (invalid)
        too_long = factory.edge_case_company_name("too_long")
        assert len(too_long) > 200

    def test_edge_case_confidences(self, factory):
        """Edge case confidence scores cover validation boundaries"""
        # Minimum valid
        assert factory.edge_case_confidence("min") == 0.0

        # Maximum valid
        assert factory.edge_case_confidence("max") == 1.0

        # Below minimum (invalid)
        assert factory.edge_case_confidence("below_min") < 0.0

        # Above maximum (invalid)
        assert factory.edge_case_confidence("above_max") > 1.0

    def test_edge_case_frameworks(self, factory):
        """Edge case framework lists cover validation boundaries"""
        # Empty (invalid)
        empty = factory.edge_case_frameworks("empty")
        assert len(empty) == 0

        # Single framework
        single = factory.edge_case_frameworks("single")
        assert len(single) == 1

        # Maximum frameworks (all available)
        max_fw = factory.edge_case_frameworks("max")
        assert len(max_fw) == 7

        # Invalid frameworks
        invalid = factory.edge_case_frameworks("invalid")
        assert all(fw not in ["porter", "swot", "pestel"] for fw in invalid)


class TestCustomProviders:
    """Test custom Faker providers"""

    def test_framework_provider(self, faker):
        """Framework provider generates valid frameworks"""
        framework = faker.framework()
        valid_frameworks = {
            "porter", "swot", "pestel", "blue_ocean",
            "ansoff", "bcg_matrix", "value_chain"
        }
        assert framework in valid_frameworks

    def test_industry_provider(self, faker):
        """Industry provider generates valid industries"""
        industry = faker.industry()
        assert isinstance(industry, str)
        assert len(industry) > 0

    def test_monitoring_frequency_provider(self, faker):
        """Monitoring frequency provider generates valid frequencies"""
        frequency = faker.monitoring_frequency()
        assert frequency in ["hourly", "daily", "weekly", "monthly"]

    def test_change_type_provider(self, faker):
        """Change type provider generates valid change types"""
        change_type = faker.change_type()
        valid_types = [
            "competitive_landscape", "market_trend", "financial_metric",
            "strategic_shift", "regulatory", "technology", "leadership"
        ]
        assert change_type in valid_types

    def test_financial_data_provider_market_cap(self, faker):
        """Financial provider generates realistic market caps"""
        # Test different company sizes
        micro_cap = faker.market_cap(size="micro")
        assert 50e6 <= micro_cap <= 300e6

        large_cap = faker.market_cap(size="large")
        assert 10e9 <= large_cap <= 200e9

    def test_financial_data_provider_confidence_score(self, faker):
        """Financial provider generates valid confidence scores"""
        scores = [faker.confidence_score() for _ in range(100)]

        assert all(0.5 <= score <= 1.0 for score in scores)
        # Should have variation
        assert len(set(scores)) > 10

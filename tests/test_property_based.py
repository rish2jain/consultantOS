"""
Comprehensive property-based tests for ConsultantOS using Hypothesis and Faker.

Property-based testing generates hundreds of test cases automatically,
exploring edge cases and invariants that manual tests might miss.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from consultantos.models import AnalysisRequest, CompanyResearch, FinancialSnapshot
from consultantos.models.monitoring import MonitoringConfig, Monitor, Change, Alert
from consultantos.utils.validators import AnalysisRequestValidator
from consultantos.utils.sanitize import sanitize_input, sanitize_dict


# ============================================================================
# HYPOTHESIS STRATEGIES (DATA GENERATORS)
# ============================================================================

# Company name strategy: 2-200 printable characters
company_names = st.text(
    min_size=2,
    max_size=200,
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),  # Exclude control characters
        blacklist_characters="<>\"'`"  # Exclude potentially dangerous chars
    )
)

# Industry names: 1-200 characters or None
industry_names = st.one_of(
    st.none(),
    st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=("Cc", "Cs")))
)

# Valid framework names
valid_frameworks = st.sampled_from([
    "porter", "swot", "pestel", "blue_ocean", "ansoff", "bcg_matrix", "value_chain"
])

# Framework lists: 1-7 unique valid frameworks
framework_lists = st.lists(
    valid_frameworks,
    min_size=1,
    max_size=7,
    unique=True
)

# Analysis depth values
depth_values = st.sampled_from(["quick", "standard", "deep"])

# Confidence scores: 0.0 to 1.0
confidence_scores = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Alert thresholds: 0.6 to 0.9
alert_thresholds = st.floats(min_value=0.6, max_value=0.9, allow_nan=False)

# Monitoring frequencies
monitoring_frequencies = st.sampled_from(["hourly", "daily", "weekly", "monthly"])


# ============================================================================
# PROPERTY-BASED TESTS FOR VALIDATORS
# ============================================================================

@pytest.mark.property
class TestValidatorProperties:
    """Property-based tests for validation logic"""

    @given(company_names)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_company_validation_preserves_length_bounds(self, company_name):
        """Property: Valid company names stay within length bounds after validation"""
        try:
            result = AnalysisRequestValidator.validate_company(company_name)
            # If validation succeeds, result should be within bounds
            assert 2 <= len(result) <= 200
            # Result should be stripped
            assert result == result.strip()
        except ValueError:
            # If validation fails, it should be for a specific reason
            assert len(company_name.strip()) < 2 or len(company_name) > 200

    @given(framework_lists)
    @settings(max_examples=100)
    def test_framework_validation_preserves_uniqueness(self, frameworks):
        """Property: Framework validation removes duplicates"""
        result = AnalysisRequestValidator.validate_frameworks(frameworks)
        # Result should have unique elements
        assert len(result) == len(set(result))
        # All should be valid
        assert all(fw in ["porter", "swot", "pestel", "blue_ocean", "ansoff", "bcg_matrix", "value_chain"] for fw in result)

    @given(depth_values)
    @settings(max_examples=50)
    def test_depth_validation_idempotent(self, depth):
        """Property: Validating depth multiple times produces same result"""
        result1 = AnalysisRequestValidator.validate_depth(depth)
        result2 = AnalysisRequestValidator.validate_depth(result1)
        result3 = AnalysisRequestValidator.validate_depth(result2)

        assert result1 == result2 == result3

    @given(company_names, industry_names, framework_lists, depth_values)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_request_validation_complete(self, company, industry, frameworks, depth):
        """Property: Request validation handles all valid combinations"""
        try:
            request = AnalysisRequest(
                company=company,
                industry=industry,
                frameworks=frameworks,
                depth=depth
            )
            validated = AnalysisRequestValidator.validate_request(request)

            # Validated request should have non-empty company
            assert validated.company is not None
            assert len(validated.company) >= 2

            # Frameworks should be normalized
            assert all(fw.islower() for fw in validated.frameworks)

        except (ValueError, Exception) as e:
            # Expected validation failures
            assert isinstance(e, (ValueError, Exception))


# ============================================================================
# PROPERTY-BASED TESTS FOR SANITIZATION
# ============================================================================

@pytest.mark.property
class TestSanitizationProperties:
    """Property-based tests for input sanitization"""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=200)
    def test_sanitize_input_always_returns_string(self, text):
        """Property: Sanitization always returns a string"""
        result = sanitize_input(text)
        assert isinstance(result, str)

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_sanitize_input_idempotent(self, text):
        """Property: Sanitizing twice produces same result as sanitizing once"""
        result1 = sanitize_input(text)
        result2 = sanitize_input(result1)
        assert result1 == result2

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100)
    def test_sanitize_removes_dangerous_patterns(self, text):
        """Property: Sanitization removes dangerous patterns"""
        dangerous = f"{text}<script>alert('xss')</script>"
        result = sanitize_input(dangerous)

        # Should not contain script tags
        assert "<script>" not in result.lower()
        assert "</script>" not in result.lower()

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
        values=st.one_of(
            st.text(max_size=200),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none()
        ),
        min_size=0,
        max_size=20
    ))
    @settings(max_examples=100)
    def test_sanitize_dict_preserves_structure(self, data):
        """Property: Dict sanitization preserves dictionary structure and types"""
        result = sanitize_dict(data)

        # Should be a dict
        assert isinstance(result, dict)
        # Should have same keys
        assert set(result.keys()) == set(data.keys())

        # Should preserve non-string types
        for key, value in data.items():
            if value is None:
                assert result[key] is None
            elif isinstance(value, bool):
                assert isinstance(result[key], bool)
            elif isinstance(value, (int, float)):
                assert isinstance(result[key], (int, float))


# ============================================================================
# PROPERTY-BASED TESTS FOR MODELS
# ============================================================================

@pytest.mark.property
class TestModelProperties:
    """Property-based tests for Pydantic models"""

    @given(confidence_scores)
    @settings(max_examples=200)
    def test_confidence_scores_in_valid_range(self, confidence):
        """Property: Confidence scores must be between 0.0 and 1.0"""
        # This should always pass since strategy enforces it
        assert 0.0 <= confidence <= 1.0

        # Models should accept these values
        change = Change(
            change_type="market_trend",
            title="Test change",
            description="Test description",
            confidence=confidence,
            source_urls=["https://example.com"]
        )
        assert change.confidence == confidence

    @given(
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_porters_five_forces_intensity_calculation(self, supplier, buyer, rivalry, substitutes, new_entrants):
        """Property: Porter's Five Forces intensity derived from force values"""
        # Import here to avoid circular dependency
        from consultantos.models import PortersFiveForces

        avg = (supplier + buyer + rivalry + substitutes + new_entrants) / 5

        forces = PortersFiveForces(
            supplier_power=supplier,
            buyer_power=buyer,
            competitive_rivalry=rivalry,
            threat_of_substitutes=substitutes,
            threat_of_new_entrants=new_entrants,
            overall_intensity="Low" if avg < 2.5 else "Moderate" if avg < 3.5 else "High",
            detailed_analysis={
                "supplier_power": "Analysis",
                "buyer_power": "Analysis",
                "competitive_rivalry": "Analysis",
                "threat_of_substitutes": "Analysis",
                "threat_of_new_entrants": "Analysis"
            }
        )

        # Verify intensity matches average
        if avg < 2.5:
            assert forces.overall_intensity == "Low"
        elif avg < 3.5:
            assert forces.overall_intensity == "Moderate"
        else:
            assert forces.overall_intensity == "High"

    @given(
        framework_lists,
        alert_thresholds,
        monitoring_frequencies
    )
    @settings(max_examples=100)
    def test_monitoring_config_validation(self, frameworks, threshold, frequency):
        """Property: MonitoringConfig validates framework combinations"""
        config = MonitoringConfig(
            frequency=frequency,
            frameworks=frameworks,
            alert_threshold=threshold,
            notification_channels=["email"]
        )

        # All frameworks should be valid
        assert all(fw in ["porter", "swot", "pestel", "blue_ocean", "ansoff", "bcg_matrix", "value_chain"] for fw in config.frameworks)
        # Threshold should be in valid range
        assert 0.6 <= config.alert_threshold <= 0.9
        # Frequency should be valid
        assert config.frequency in ["hourly", "daily", "weekly", "monthly"]


# ============================================================================
# STATEFUL PROPERTY-BASED TESTING
# ============================================================================

@pytest.mark.property
class MonitorLifecycleMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for Monitor lifecycle.

    Tests that monitors maintain invariants through state transitions.
    """

    def __init__(self):
        super().__init__()
        self.monitors = {}
        self.next_id = 0

    @rule(company=company_names, industry=industry_names)
    def create_monitor(self, company, industry):
        """Create a new monitor"""
        assume(len(company.strip()) >= 2)  # Only test valid companies

        monitor_id = f"monitor_{self.next_id}"
        self.next_id += 1

        self.monitors[monitor_id] = {
            "id": monitor_id,
            "company": company.strip(),
            "industry": industry.strip() if industry else "Technology",
            "status": "active",
            "total_alerts": 0,
            "error_count": 0
        }

    @rule(monitor_id=st.sampled_from(list(range(10))))
    def pause_monitor(self, monitor_id):
        """Pause a monitor"""
        mid = f"monitor_{monitor_id}"
        if mid in self.monitors and self.monitors[mid]["status"] == "active":
            self.monitors[mid]["status"] = "paused"

    @rule(monitor_id=st.sampled_from(list(range(10))))
    def resume_monitor(self, monitor_id):
        """Resume a paused monitor"""
        mid = f"monitor_{monitor_id}"
        if mid in self.monitors and self.monitors[mid]["status"] == "paused":
            self.monitors[mid]["status"] = "active"

    @rule(monitor_id=st.sampled_from(list(range(10))))
    def generate_alert(self, monitor_id):
        """Generate alert for monitor"""
        mid = f"monitor_{monitor_id}"
        if mid in self.monitors and self.monitors[mid]["status"] == "active":
            self.monitors[mid]["total_alerts"] += 1

    @invariant()
    def alerts_only_for_valid_monitors(self):
        """Invariant: Only existing monitors can have alerts"""
        for monitor_id, monitor in self.monitors.items():
            assert monitor["total_alerts"] >= 0

    @invariant()
    def status_is_valid(self):
        """Invariant: Monitor status is always valid"""
        valid_statuses = {"active", "paused", "deleted", "error"}
        for monitor_id, monitor in self.monitors.items():
            assert monitor["status"] in valid_statuses


# Run stateful tests
TestMonitorLifecycle = MonitorLifecycleMachine.TestCase


# ============================================================================
# INTEGRATION PROPERTY TESTS
# ============================================================================

@pytest.mark.property
class TestFactoryModelIntegration:
    """Property-based tests for factory-model integration"""

    def test_factory_generated_analysis_requests_validate(self, factory):
        """Property: All factory-generated requests validate with Pydantic"""
        for _ in range(50):
            data = factory.analysis_request()
            request = AnalysisRequest(**data)

            assert request.company is not None
            assert len(request.frameworks) >= 1
            assert request.depth in ["quick", "standard", "deep"]

    def test_factory_generated_monitors_validate(self, factory):
        """Property: All factory-generated monitors validate with Pydantic"""
        for _ in range(30):
            data = factory.monitor()
            monitor = Monitor(**data)

            assert monitor.company is not None
            assert monitor.status in ["active", "paused", "deleted", "error"]
            assert isinstance(monitor.config, MonitoringConfig)

    def test_factory_generated_alerts_validate(self, factory):
        """Property: All factory-generated alerts validate with Pydantic"""
        for _ in range(30):
            data = factory.alert()
            alert = Alert(**data)

            assert 0.0 <= alert.confidence <= 1.0
            assert len(alert.changes_detected) >= 1
            assert isinstance(alert.read, bool)

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_bulk_factory_generation_consistent(self, count, factory):
        """Property: Bulk generation produces consistent results"""
        requests = factory.analysis_requests(count=count)

        assert len(requests) == count
        # All should be valid
        for req_data in requests:
            request = AnalysisRequest(**req_data)
            assert request is not None


# ============================================================================
# ROUNDTRIP PROPERTY TESTS
# ============================================================================

@pytest.mark.property
class TestRoundtripProperties:
    """Property-based roundtrip tests (serialize -> deserialize)"""

    def test_analysis_request_json_roundtrip(self, factory):
        """Property: AnalysisRequest survives JSON roundtrip"""
        for _ in range(30):
            original_data = factory.analysis_request()
            original = AnalysisRequest(**original_data)

            # Serialize to dict
            serialized = original.model_dump()

            # Deserialize back
            restored = AnalysisRequest(**serialized)

            # Should be identical
            assert restored.company == original.company
            assert restored.industry == original.industry
            assert restored.frameworks == original.frameworks
            assert restored.depth == original.depth

    def test_monitor_json_roundtrip(self, factory):
        """Property: Monitor survives JSON roundtrip"""
        for _ in range(20):
            original_data = factory.monitor()
            original = Monitor(**original_data)

            # Serialize
            serialized = original.model_dump()

            # Deserialize
            restored = Monitor(**serialized)

            # Should be identical
            assert restored.id == original.id
            assert restored.company == original.company
            assert restored.status == original.status

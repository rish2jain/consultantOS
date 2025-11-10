# Faker Test Data Factories Guide

Comprehensive guide to using Faker-based test data factories in ConsultantOS.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Factory Reference](#factory-reference)
5. [Custom Providers](#custom-providers)
6. [Pytest Fixtures](#pytest-fixtures)
7. [Property-Based Testing](#property-based-testing)
8. [Edge Cases](#edge-cases)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)

---

## Overview

The ConsultantOS test factories provide **realistic, varied test data generation** using:

- **Faker**: Realistic data generation (companies, names, URLs, dates)
- **Custom Providers**: Domain-specific data (frameworks, industries, monitoring configs)
- **Reproducible Seeds**: Deterministic generation for CI/CD
- **Property-Based Testing**: Automated test case generation with Hypothesis

### Benefits

- ✅ **Realistic Data**: Generate data that mimics production patterns
- ✅ **Reproducibility**: Seeded randomness for consistent test runs
- ✅ **Coverage**: Automated edge case exploration
- ✅ **Maintainability**: Centralized test data generation
- ✅ **Flexibility**: Easy customization and extension

---

## Installation

Already installed via `requirements.txt`:

```bash
pip install Faker>=20.0.0 hypothesis>=6.90.0
```

---

## Quick Start

### Basic Usage

```python
from tests.factories import ConsultantOSFactory

# Create factory instance
factory = ConsultantOSFactory()

# Generate single analysis request
request = factory.analysis_request()
print(request)
# {
#     "company": "Smith, Johnson and Associates",
#     "industry": "Technology",
#     "frameworks": ["porter", "swot", "pestel"],
#     "depth": "standard"
# }

# Generate multiple monitors
monitors = factory.monitors(count=10, user_id="user-123")
```

### Using in Tests

```python
def test_analysis_request(factory):
    """factory fixture provided by conftest.py"""
    data = factory.analysis_request()
    request = AnalysisRequest(**data)

    assert request.company is not None
    assert len(request.frameworks) >= 2
```

### Reproducible Generation

```python
# Same seed = same data
factory1 = ConsultantOSFactory(seed=42)
factory2 = ConsultantOSFactory(seed=42)

assert factory1.analysis_request() == factory2.analysis_request()
```

---

## Factory Reference

### Core Analysis Models

#### `analysis_request(company=None, industry=None, frameworks=None, depth=None)`

Generates AnalysisRequest data.

```python
# Default: random values
request = factory.analysis_request()

# Custom company
request = factory.analysis_request(company="Tesla")

# Custom frameworks
request = factory.analysis_request(frameworks=["porter", "swot"])

# Specific depth
request = factory.analysis_request(depth="deep")
```

#### `company_research(company_name=None)`

Generates CompanyResearch with realistic details.

```python
research = factory.company_research()
# {
#     "company_name": "...",
#     "description": "...",
#     "products_services": ["...", "...", "..."],
#     "key_competitors": ["...", "...", "..."],
#     "recent_news": ["...", "..."],
#     "sources": ["https://...", "https://..."]
# }

# Custom company
research = factory.company_research(company_name="Apple")
```

#### `financial_snapshot(ticker=None, company_size="mid")`

Generates FinancialSnapshot with realistic metrics based on company size.

```python
# Mid-sized company ($2B-$10B market cap)
snapshot = factory.financial_snapshot(company_size="mid")

# Large company ($10B-$200B market cap)
snapshot = factory.financial_snapshot(company_size="large")

# Mega-cap company ($200B-$3T market cap)
snapshot = factory.financial_snapshot(company_size="mega")
```

**Company Size Categories:**
- `micro`: $50M - $300M
- `small`: $300M - $2B
- `mid`: $2B - $10B (default)
- `large`: $10B - $200B
- `mega`: $200B - $3T

### Framework Analysis Models

#### `porters_five_forces()`

Generates Porter's Five Forces analysis with realistic force ratings (1-5).

```python
forces = factory.porters_five_forces()
# {
#     "supplier_power": 3,
#     "buyer_power": 4,
#     "competitive_rivalry": 5,
#     "threat_of_substitutes": 2,
#     "threat_of_new_entrants": 3,
#     "overall_intensity": "Moderate",
#     "detailed_analysis": { ... }
# }
```

#### `swot_analysis()`, `pestel_analysis()`, `blue_ocean_strategy()`

```python
swot = factory.swot_analysis()
pestel = factory.pestel_analysis()
bos = factory.blue_ocean_strategy()
```

### Monitoring Models

#### `monitoring_config(frequency=None, frameworks=None, alert_threshold=None)`

```python
config = factory.monitoring_config()
# {
#     "frequency": "daily",
#     "frameworks": ["porter", "swot"],
#     "alert_threshold": 0.75,
#     "notification_channels": ["email", "slack"],
#     "keywords": ["innovation", "product"],
#     "competitors": ["CompetitorA", "CompetitorB"]
# }

# Custom frequency
config = factory.monitoring_config(frequency="hourly")

# Custom threshold
config = factory.monitoring_config(alert_threshold=0.8)
```

#### `monitor(company=None, industry=None, status=None, user_id=None)`

```python
monitor = factory.monitor(
    company="Tesla",
    status="active",
    user_id="user-123"
)
```

#### `alert(monitor_id=None, confidence=None, num_changes=None)`

```python
alert = factory.alert(
    monitor_id="monitor-456",
    confidence=0.85,
    num_changes=3
)
```

#### `change(change_type=None, confidence=None)`

```python
change = factory.change(
    change_type="competitive_landscape",
    confidence=0.9
)
```

### Bulk Generation

```python
# Generate 10 analysis requests
requests = factory.analysis_requests(count=10)

# Generate 10 monitors for same user
monitors = factory.monitors(count=10, user_id="user-123")

# Generate 10 alerts for same monitor
alerts = factory.alerts(count=10, monitor_id="monitor-456")
```

---

## Custom Providers

### BusinessFrameworkProvider

```python
# Single framework
framework = factory.fake.framework()  # "porter"

# List of frameworks (2-4)
frameworks = factory.fake.frameworks()  # ["swot", "pestel", "porter"]

# Specific count
frameworks = factory.fake.frameworks(count=3)

# Framework description
desc = factory.fake.framework_description("porter")
# "Porter's Five Forces - Competitive forces analysis"
```

**Available Frameworks:**
- `porter` - Porter's Five Forces
- `swot` - SWOT Analysis
- `pestel` - PESTEL Analysis
- `blue_ocean` - Blue Ocean Strategy
- `ansoff` - Ansoff Matrix
- `bcg_matrix` - BCG Matrix
- `value_chain` - Value Chain Analysis

### IndustryProvider

```python
# Main industry
industry = factory.fake.industry()  # "Technology"

# Sub-industry
sub = factory.fake.sub_industry()  # "Cloud Computing"

# Sub-industry for specific industry
sub = factory.fake.sub_industry("Technology")  # "Software"
```

**Available Industries:**
Technology, Healthcare, Finance, Retail, Manufacturing, Energy, Transportation, Telecommunications, Real Estate, Entertainment, Education, Hospitality, Agriculture, Aerospace, Automotive, Pharmaceuticals, E-commerce, Software, Biotechnology, Consulting, Media, Insurance

### MonitoringProvider

```python
# Change type
change_type = factory.fake.change_type()
# "competitive_landscape", "market_trend", etc.

# Monitoring frequency
freq = factory.fake.monitoring_frequency()  # "daily"

# Monitor status
status = factory.fake.monitor_status()  # "active"

# Notification channel
channel = factory.fake.notification_channel()  # "email"

# Multiple channels (1-3)
channels = factory.fake.notification_channels()
```

### FinancialDataProvider

```python
# Market capitalization by size
market_cap = factory.fake.market_cap(size="large")

# Revenue (optionally based on market cap)
revenue = factory.fake.revenue(market_cap=10e9)

# Growth percentages
revenue_growth = factory.fake.revenue_growth()  # -10 to +50%
profit_margin = factory.fake.profit_margin()    # -20 to +40%

# P/E ratio (None for unprofitable)
pe_ratio = factory.fake.pe_ratio()  # 5-100 or None

# Stock price
price = factory.fake.stock_price()  # $5-$500

# Confidence score
confidence = factory.fake.confidence_score()  # 0.5-1.0
```

---

## Pytest Fixtures

Available in `conftest.py`:

### Faker Fixtures

```python
def test_with_faker_session(faker_session):
    """Session-scoped Faker (same across all tests)"""
    company = faker_session.company()
```

```python
def test_with_faker(faker):
    """Function-scoped Faker (fresh each test)"""
    company = faker.company()
```

### Factory Fixtures

```python
def test_with_factory_session(factory_session):
    """Session-scoped factory (same seed)"""
    request = factory_session.analysis_request()
```

```python
def test_with_factory(factory):
    """Function-scoped factory (seeded, reproducible)"""
    request = factory.analysis_request()
```

```python
def test_with_unique_factory(unique_factory):
    """Non-deterministic factory (truly random)"""
    request = unique_factory.analysis_request()
```

### Data Fixtures

```python
def test_with_sample_data(
    sample_analysis_request,
    sample_monitor,
    sample_alert,
    sample_user
):
    """Pre-generated sample data"""
    assert sample_analysis_request["company"] is not None
```

### Edge Case Fixtures

```python
def test_edge_cases(
    edge_case_companies,
    edge_case_confidences,
    edge_case_framework_lists
):
    """Edge case data for boundary testing"""

    # Minimum valid length (2 chars)
    assert len(edge_case_companies["min_length"]) == 2

    # Maximum valid length (200 chars)
    assert len(edge_case_companies["max_length"]) == 200

    # Invalid cases
    assert edge_case_companies["empty"] == ""
    assert len(edge_case_companies["too_short"]) < 2
    assert len(edge_case_companies["too_long"]) > 200
```

---

## Property-Based Testing

### Using Hypothesis with Factories

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=100))
def test_bulk_generation(count, factory):
    """Generate variable number of requests"""
    requests = factory.analysis_requests(count=count)
    assert len(requests) == count
```

### Custom Strategies

Available in `conftest.py`:

```python
from tests.conftest import analysis_request_strategy, confidence_score_strategy

@given(analysis_request_strategy())
def test_request_validation(request_data):
    request = AnalysisRequest(**request_data)
    assert request.company is not None

@given(confidence_score_strategy())
def test_confidence_range(confidence):
    assert 0.0 <= confidence <= 1.0
```

### Property Test Examples

```python
@given(st.text(min_size=2, max_size=200))
def test_company_validation_preserves_length(company_name):
    """Property: Valid companies stay within bounds"""
    result = AnalysisRequestValidator.validate_company(company_name)
    assert 2 <= len(result) <= 200

@given(framework_lists)
def test_framework_validation_removes_duplicates(frameworks):
    """Property: Validation removes duplicates"""
    result = AnalysisRequestValidator.validate_frameworks(frameworks)
    assert len(result) == len(set(result))
```

---

## Edge Cases

### Using Edge Case Generators

```python
# Company name edge cases
min_valid = factory.edge_case_company_name("min_length")  # "AB"
max_valid = factory.edge_case_company_name("max_length")  # "A"*200
special = factory.edge_case_company_name("special_chars")  # "Company & Co."
unicode = factory.edge_case_company_name("unicode")  # "Société 日本"
whitespace = factory.edge_case_company_name("whitespace")  # "  Multi   Space  "
empty = factory.edge_case_company_name("empty")  # ""
too_short = factory.edge_case_company_name("too_short")  # "A"
too_long = factory.edge_case_company_name("too_long")  # "A"*201

# Confidence edge cases
min_conf = factory.edge_case_confidence("min")  # 0.0
max_conf = factory.edge_case_confidence("max")  # 1.0
below_min = factory.edge_case_confidence("below_min")  # -0.1
above_max = factory.edge_case_confidence("above_max")  # 1.1

# Framework list edge cases
empty_list = factory.edge_case_frameworks("empty")  # []
single = factory.edge_case_frameworks("single")  # ["porter"]
max_fw = factory.edge_case_frameworks("max")  # All 7 frameworks
invalid = factory.edge_case_frameworks("invalid")  # ["invalid_framework"]
duplicate = factory.edge_case_frameworks("duplicate")  # ["porter", "swot", "porter"]
```

### Edge Case Testing Pattern

```python
def test_validation_edge_cases(edge_case_companies):
    """Test validation with boundary values"""

    # Valid boundaries
    assert AnalysisRequestValidator.validate_company(
        edge_case_companies["min_length"]
    ) == edge_case_companies["min_length"]

    # Invalid boundaries
    with pytest.raises(ValueError):
        AnalysisRequestValidator.validate_company(
            edge_case_companies["too_long"]
        )
```

---

## Best Practices

### 1. Use Seeded Factories for Reproducibility

```python
# ✅ Good: Reproducible in CI
factory = ConsultantOSFactory(seed=42)

# ❌ Avoid: Non-deterministic failures in CI
factory = ConsultantOSFactory()  # Random seed
```

### 2. Use Fixtures for Common Data

```python
# ✅ Good: Reusable fixture
@pytest.fixture
def sample_monitor(factory):
    return factory.monitor(status="active")

def test_monitor_pause(sample_monitor):
    # Use pre-generated data
    ...

# ❌ Avoid: Recreating data in each test
def test_monitor_pause(factory):
    monitor = factory.monitor(status="active")
    ...
```

### 3. Customize Only What Matters

```python
# ✅ Good: Override specific fields
monitor = factory.monitor(
    company="Tesla",  # Test-specific
    # Let factory generate: industry, config, timestamps
)

# ❌ Avoid: Over-specification
monitor = factory.monitor(
    company="Tesla",
    industry="EV",
    config=MonitoringConfig(...),  # Unnecessary detail
)
```

### 4. Use Edge Cases for Boundary Testing

```python
# ✅ Good: Test boundaries explicitly
def test_company_length_limits(edge_case_companies):
    validate(edge_case_companies["min_length"])  # Should pass
    with pytest.raises(ValueError):
        validate(edge_case_companies["too_short"])  # Should fail

# ❌ Avoid: Only testing happy path
def test_company_validation(factory):
    company = factory.fake.company()  # Always valid
    validate(company)
```

### 5. Combine Faker with Property-Based Testing

```python
# ✅ Good: Comprehensive coverage
@given(st.text(min_size=2, max_size=200))
def test_all_valid_companies(company_name):
    result = validate_company(company_name)
    assert 2 <= len(result) <= 200

# ❌ Limited: Only a few examples
def test_few_companies(factory):
    for _ in range(10):
        company = factory.fake.company()
        validate_company(company)
```

---

## Advanced Usage

### Creating Custom Factories

```python
from tests.factories import ConsultantOSFactory

class CustomFactory(ConsultantOSFactory):
    """Extended factory with custom generators"""

    def premium_monitor(self):
        """Generate premium tier monitor"""
        return self.monitor(
            config=self.monitoring_config(
                frequency="hourly",
                alert_threshold=0.9,
                notification_channels=["email", "slack", "webhook"]
            )
        )

factory = CustomFactory(seed=42)
monitor = factory.premium_monitor()
```

### Conditional Generation

```python
def generate_monitor_with_alerts(factory, alert_count):
    """Generate monitor with specific number of alerts"""
    monitor = factory.monitor(total_alerts=alert_count)
    alerts = factory.alerts(
        count=alert_count,
        monitor_id=monitor["id"]
    )
    return monitor, alerts

monitor, alerts = generate_monitor_with_alerts(factory, alert_count=5)
```

### Stateful Testing

```python
from hypothesis.stateful import RuleBasedStateMachine, rule

class MonitorStateMachine(RuleBasedStateMachine):
    """Stateful property-based testing"""

    def __init__(self):
        super().__init__()
        self.factory = ConsultantOSFactory(seed=42)
        self.monitors = []

    @rule()
    def create_monitor(self):
        monitor = self.factory.monitor()
        self.monitors.append(monitor)

    @rule(monitor_idx=st.integers(min_value=0, max_value=10))
    def pause_monitor(self, monitor_idx):
        if monitor_idx < len(self.monitors):
            self.monitors[monitor_idx]["status"] = "paused"

TestMonitorState = MonitorStateMachine.TestCase
```

### Locale-Specific Data

```python
# Japanese locale
factory_jp = ConsultantOSFactory(locale="ja_JP")
company_jp = factory_jp.fake.company()  # Japanese company name

# German locale
factory_de = ConsultantOSFactory(locale="de_DE")
company_de = factory_de.fake.company()  # German company name
```

---

## Running Tests

```bash
# Run all tests
pytest tests/

# Run only property-based tests
pytest -m property tests/

# Run with coverage
pytest --cov=consultantos tests/

# Run with specific seed (reproducibility)
PYTEST_FAKER_SEED=42 pytest tests/

# Run factory tests only
pytest tests/test_factories.py -v

# Run property tests with more examples
pytest tests/test_property_based.py --hypothesis-seed=42
```

---

## Troubleshooting

### Issue: Non-Deterministic Test Failures

**Solution:** Use seeded factories

```python
# Instead of:
factory = ConsultantOSFactory()

# Use:
factory = ConsultantOSFactory(seed=42)
```

### Issue: Faker Data Doesn't Match Validation

**Solution:** Use custom providers or edge cases

```python
# Instead of generic Faker:
company = faker.company()  # Might be too long

# Use custom provider:
company = faker.company()[:200]  # Truncate to max length

# Or use edge cases:
company = factory.edge_case_company_name("max_length")
```

### Issue: Property Tests Too Slow

**Solution:** Reduce `max_examples`

```python
from hypothesis import settings

@given(...)
@settings(max_examples=50)  # Default is 100
def test_something(...):
    ...
```

---

## References

- **Faker Documentation**: https://faker.readthedocs.io/
- **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Pytest Documentation**: https://docs.pytest.org/

---

## Support

For issues or questions:
1. Check test examples in `tests/test_factories.py`
2. Review property tests in `tests/test_property_based.py`
3. Consult this guide
4. Review Faker/Hypothesis documentation

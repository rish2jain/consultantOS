# Validation Quick Reference Guide

## Schema Validation Ranges

### Financial Data
| Field | Type | Range | Notes |
|-------|------|-------|-------|
| ticker | string | `^[A-Z]{1,5}$` | 1-5 uppercase letters |
| market_cap | float | 0 to 1e15 | $0 to $1 quadrillion |
| revenue | float | 0 to 1e13 | $0 to $10 trillion |
| revenue_growth | float | -1.0 to 10.0 | -100% to +1000% |
| profit_margin | float | -1.0 to 1.0 | -100% to +100% |
| pe_ratio | float | -100 to 1000 | Allows negative for losses |

### Market Data
| Field | Type | Values | Notes |
|-------|------|--------|-------|
| search_interest_trend | string | Growing, Stable, Declining, Unknown | Exact match required |
| interest_score | float | 0 to 100 | Google Trends range |
| geographic_distribution | dict | {region: 0-100} | Score per region |
| interest_data | dict | Required | Time series data |

### Research Data
| Field | Type | Validation | Notes |
|-------|------|------------|-------|
| company_name | string | min_length=1 (after strip) | Required, non-empty |
| description | string | min_length=10 | Brief overview |
| sources | list[string] | Must start with http:// or https:// | Invalid URLs filtered |
| products_services | list | Must be list type | Can be empty |
| key_competitors | list | Must be list type | Can be empty |

### Monitor Snapshot
| Field | Type | Validation | Notes |
|-------|------|------------|-------|
| monitor_id | string | Required, non-empty | Unique monitor ID |
| timestamp | datetime | Required | Snapshot timestamp |
| company | string | Required, non-empty | Company name |
| industry | string | Required, non-empty | Industry sector |
| competitive_forces | dict | Values must be strings | Porter's 5 Forces |
| market_trends | list | Must be list type | Trend strings |
| financial_metrics | dict | Non-negative for most metrics | Allows negative growth/margin |

## Validation Response Format

All validators return a tuple:
```python
(is_valid: bool, error_message: Optional[str], cleaned_data: Dict)
```

### Examples

**Success:**
```python
(True, None, {
    "ticker": "AAPL",
    "market_cap": 3000000000000.0,
    "revenue": 400000000000.0,
    ...
})
```

**Failure with cleaned data:**
```python
(False, "Financial data validation failed: ticker format invalid", {
    "ticker": "UNKNOWN",  # Safe default
    "market_cap": None,
    "revenue": None,
    ...
})
```

## Common Validation Patterns

### Pattern 1: Validate Agent Output
```python
from consultantos.utils.schemas import FinancialDataSchema, log_validation_metrics

# Get LLM output
result = await self.generate_structured(prompt, response_model=FinancialSnapshot)

# Validate
result_dict = result.model_dump()
is_valid, error_msg, cleaned_data = FinancialDataSchema.validate_financial_snapshot(result_dict)

# Log
log_validation_metrics("financial", is_valid, error_msg)

# Handle
if not is_valid:
    logger.warning(f"Validation failed: {error_msg}")

# Return cleaned data
return FinancialSnapshot(**cleaned_data)
```

### Pattern 2: Unified Validation
```python
from consultantos.utils.schemas import validate_and_clean_data

is_valid, error_msg, cleaned = validate_and_clean_data(data, "financial")
is_valid, error_msg, cleaned = validate_and_clean_data(data, "market")
is_valid, error_msg, cleaned = validate_and_clean_data(data, "research")
is_valid, error_msg, cleaned = validate_and_clean_data(data, "snapshot")
```

### Pattern 3: Fallback Validation
```python
try:
    result = await generate_data()
    is_valid, error_msg, cleaned = validate(result)
    return Model(**cleaned)
except Exception as e:
    # Fallback data
    fallback = create_fallback_data()
    is_valid, error_msg, cleaned_fallback = validate(fallback)
    log_validation_metrics("fallback", is_valid, error_msg)
    return Model(**cleaned_fallback)
```

## Logging Conventions

### Structured Logging
```python
# Success
logger.info(f"financial_validation_passed: ticker={ticker}")

# Failure
logger.warning(f"financial_validation_failed: ticker={ticker}, error={error_msg}")

# Metrics
log_validation_metrics(data_type="financial", is_valid=True, error_message=None)
```

### Log Keys
- `{type}_validation_passed` - Successful validation
- `{type}_validation_failed` - Failed validation with details
- `{type}_fallback` - Fallback data validation
- `validation_metrics` - Structured metrics for monitoring

## Error Messages

### Financial Validation Errors
```
"Financial data validation failed: ticker format invalid"
"Financial data validation failed: market_cap must be non-negative"
"Financial data validation failed: revenue_growth outside acceptable range"
"Financial data validation failed: profit_margin must be between -100% and +100%"
```

### Market Validation Errors
```
"Market trends validation failed: Invalid trend direction"
"Market trends validation failed: interest_data must be a dictionary"
"Market trends validation failed: interest score outside 0-100 range"
```

### Research Validation Errors
```
"Research data validation failed: company_name is required"
"Research data validation failed: description must be at least 10 characters"
"Research data validation failed: sources must be a list"
```

### Snapshot Validation Errors
```
"Snapshot validation failed: monitor_id is required"
"Snapshot validation failed: competitive_rivalry must be a string"
"Snapshot validation failed: revenue cannot be negative"
"Snapshot validation failed: market_trends must be a list"
```

## Default/Fallback Values

### Financial Data Fallbacks
```python
{
    "ticker": "UNKNOWN",
    "market_cap": None,
    "revenue": None,
    "revenue_growth": None,
    "profit_margin": None,
    "pe_ratio": None,
    "key_metrics": {},
    "risk_assessment": "High - Data validation issues"
}
```

### Market Data Fallbacks
```python
{
    "search_interest_trend": "Unknown",
    "interest_data": {},
    "geographic_distribution": {},
    "related_searches": [],
    "competitive_comparison": {}
}
```

### Research Data Fallbacks
```python
{
    "company_name": "Unknown",
    "description": "Limited research data available",
    "products_services": [],
    "target_market": "Unknown",
    "key_competitors": [],
    "recent_news": [],
    "sources": []
}
```

## Testing Validators

### Test Template
```python
def test_valid_data():
    """Valid data should pass validation"""
    valid_data = {...}  # Complete valid structure
    is_valid, error_msg, cleaned = Validator.validate(valid_data)

    assert is_valid is True
    assert error_msg is None
    assert cleaned["field"] == expected_value

def test_invalid_data():
    """Invalid data should fail gracefully"""
    invalid_data = {...}  # Data with validation errors
    is_valid, error_msg, cleaned = Validator.validate(invalid_data)

    assert is_valid is False
    assert error_msg is not None
    assert "expected error" in error_msg.lower()
    # Check fallback values
    assert cleaned["field"] == safe_default
```

### Run Tests
```bash
# All validation tests
pytest tests/test_validators.py -v

# Specific test class
pytest tests/test_validators.py::TestFinancialDataValidation -v

# Specific test
pytest tests/test_validators.py::TestFinancialDataValidation::test_valid_financial_snapshot -v

# With coverage
pytest tests/test_validators.py --cov=consultantos.utils.schemas --cov-report=html
```

## Debugging Validation Issues

### 1. Check Validation Logs
```bash
# Filter validation logs
grep "validation_failed" logs/app.log

# Count failures by type
grep "validation_failed" logs/app.log | cut -d: -f1 | sort | uniq -c
```

### 2. Inspect Failure Cases
```python
try:
    validated = schema.validate(df)
except SchemaErrors as e:
    print(e.failure_cases)  # Shows which rows/columns failed
    print(e.data)  # Shows the data that failed
```

### 3. Test Individual Validators
```python
# Quick validation test in Python REPL
from consultantos.utils.schemas import FinancialDataSchema

test_data = {"ticker": "TEST", ...}
is_valid, error, cleaned = FinancialDataSchema.validate_financial_snapshot(test_data)
print(f"Valid: {is_valid}")
print(f"Error: {error}")
print(f"Cleaned: {cleaned}")
```

## Performance Considerations

### Validation Overhead
- Financial: ~3-5ms per validation
- Market: ~2-3ms per validation
- Research: ~3-4ms per validation
- Snapshot: ~5-7ms per validation

### Optimization Tips
1. **Cache validated data** - Don't re-validate same data
2. **Batch validation** - Validate multiple records together
3. **Skip validation in development** - Use environment flag
4. **Limit validation depth** - Only validate critical fields in hot paths

### Environment Flags
```python
# In config.py
ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "true").lower() == "true"
VALIDATION_LOG_LEVEL = os.getenv("VALIDATION_LOG_LEVEL", "WARNING")

# In schemas.py
if not config.ENABLE_VALIDATION:
    return True, None, data  # Skip validation
```

## Best Practices

### ✅ DO
- Always validate external data sources
- Log all validation failures
- Return partial data on validation failure
- Test validators comprehensively
- Use structured logging
- Handle both SchemaError and SchemaErrors

### ❌ DON'T
- Fail entire analysis on validation error
- Ignore validation failures silently
- Return unvalidated data to users
- Skip validation in production
- Raise exceptions from validators
- Log sensitive data in validation errors

## Maintenance

### Adding New Validators
1. Create schema class in `consultantos/utils/schemas.py`
2. Define validation rules using Pandera
3. Implement `validate_{type}` static method
4. Add to unified `validate_and_clean_data` function
5. Create comprehensive tests in `tests/test_validators.py`
6. Update documentation

### Updating Validation Rules
1. Modify schema definition
2. Update tests to match new rules
3. Run full test suite
4. Update documentation
5. Deploy with monitoring

### Monitoring Validation Health
Track these metrics:
- Validation failure rate by data type
- Most common validation errors
- Validation performance (latency)
- Data source reliability scores

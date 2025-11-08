"""
Tests for utility modules
"""
import pytest
from consultantos.utils.validators import AnalysisRequestValidator
from consultantos.utils.sanitize import sanitize_input, sanitize_dict
from consultantos.utils.retry import retry_with_backoff, RetryConfig
from consultantos.utils.circuit_breaker import CircuitBreaker, CircuitState
from consultantos.models import AnalysisRequest
from datetime import datetime


class TestValidators:
    """Tests for input validators"""
    
    def test_validate_company_valid(self):
        """Test valid company name"""
        result = AnalysisRequestValidator.validate_company("Tesla Inc")
        assert result == "Tesla Inc"
    
    def test_validate_company_too_short(self):
        """Test company name too short"""
        with pytest.raises(ValueError, match="at least 2 characters"):
            AnalysisRequestValidator.validate_company("A")
    
    def test_validate_company_empty(self):
        """Test empty company name"""
        with pytest.raises(ValueError, match="required"):
            AnalysisRequestValidator.validate_company("")
    
    def test_validate_company_too_long(self):
        """Test company name too long"""
        long_name = "A" * 201
        with pytest.raises(ValueError, match="too long"):
            AnalysisRequestValidator.validate_company(long_name)
    
    def test_validate_frameworks_valid(self):
        """Test valid frameworks"""
        result = AnalysisRequestValidator.validate_frameworks(["porter", "swot"])
        assert result == ["porter", "swot"]
    
    def test_validate_frameworks_invalid(self):
        """Test invalid framework"""
        with pytest.raises(ValueError, match="Invalid frameworks"):
            AnalysisRequestValidator.validate_frameworks(["invalid_framework"])
    
    def test_validate_frameworks_empty(self):
        """Test empty frameworks list"""
        with pytest.raises(ValueError, match="At least one framework"):
            AnalysisRequestValidator.validate_frameworks([])
    
    def test_validate_frameworks_duplicates(self):
        """Test duplicate frameworks are removed"""
        result = AnalysisRequestValidator.validate_frameworks(["porter", "swot", "porter"])
        assert result == ["porter", "swot"]
        assert len(result) == 2
    
    def test_validate_depth_valid(self):
        """Test valid depth"""
        assert AnalysisRequestValidator.validate_depth("standard") == "standard"
        assert AnalysisRequestValidator.validate_depth("quick") == "quick"
        assert AnalysisRequestValidator.validate_depth("deep") == "deep"
    
    def test_validate_depth_invalid(self):
        """Test invalid depth"""
        with pytest.raises(ValueError, match="Invalid depth"):
            AnalysisRequestValidator.validate_depth("invalid")
    
    def test_validate_request_complete(self):
        """Test complete request validation"""
        request = AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter", "swot"],
            depth="standard"
        )
        validated = AnalysisRequestValidator.validate_request(request)
        assert validated.company == "Tesla"
        assert validated.frameworks == ["porter", "swot"]


class TestSanitize:
    """Tests for input sanitization"""
    
    def test_sanitize_input_normal(self):
        """Test normal input"""
        result = sanitize_input("Tesla Inc")
        assert result == "Tesla Inc"
    
    def test_sanitize_input_html(self):
        """Test HTML sanitization"""
        result = sanitize_input("<script>alert('xss')</script>Tesla")
        assert "<script>" not in result
        assert "Tesla" in result
    
    def test_sanitize_input_sql_injection(self):
        """Test SQL injection prevention"""
        result = sanitize_input("Tesla'; DROP TABLE companies;--")
        assert "';" not in result
        assert "DROP" in result  # Still present but escaped
    
    def test_sanitize_input_max_length(self):
        """Test max length enforcement"""
        long_input = "A" * 2000
        result = sanitize_input(long_input, max_length=1000)
        assert len(result) <= 1000
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        data = {
            "company": "<script>alert('xss')</script>Tesla",
            "industry": "Electric Vehicles",
            "nested": {
                "key": "value'; DROP TABLE;--"
            }
        }
        sanitized = sanitize_dict(data)
        assert "<script>" not in sanitized["company"]
        assert sanitized["industry"] == "Electric Vehicles"


class TestCircuitBreaker:
    """Tests for circuit breaker"""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        cb = CircuitBreaker(failure_threshold=3, name="test")
        assert cb.get_state() == CircuitState.CLOSED
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold"""
        cb = CircuitBreaker(failure_threshold=2, name="test")
        
        # Simulate failures
        cb.failure_count = 2
        cb.last_failure_time = datetime.now()
        cb.state = CircuitState.OPEN
        
        assert cb.get_state() == CircuitState.OPEN
    
    def test_circuit_breaker_stats(self):
        """Test circuit breaker statistics"""
        cb = CircuitBreaker(name="test")
        stats = cb.get_stats()
        assert "state" in stats
        assert "failure_count" in stats
        assert stats["state"] == "closed"
    
    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset"""
        cb = CircuitBreaker(name="test")
        cb.state = CircuitState.OPEN
        cb.failure_count = 5
        
        cb.reset()
        
        assert cb.get_state() == CircuitState.CLOSED
        assert cb.failure_count == 0


class TestRetry:
    """Tests for retry logic"""
    
    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test retry succeeds on first attempt"""
        call_count = 0
        
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_with_backoff(success_func, max_retries=3)
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self):
        """Test retry succeeds after initial failures"""
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_backoff(flaky_func, max_retries=3, initial_delay=0.1)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_fails_after_max_retries(self):
        """Test retry fails after max retries"""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise Exception("Always fails")
        
        with pytest.raises(Exception, match="Always fails"):
            await retry_with_backoff(failing_func, max_retries=3, initial_delay=0.1)
        
        assert call_count == 3


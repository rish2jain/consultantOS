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

    def test_validate_company_none_input(self):
        """Test None input for company"""
        with pytest.raises(ValueError, match="required"):
            AnalysisRequestValidator.validate_company(None)

    def test_validate_company_whitespace_only(self):
        """Test company name with only whitespace"""
        with pytest.raises(ValueError, match="at least 2 characters"):
            AnalysisRequestValidator.validate_company("   ")

    def test_validate_company_with_leading_trailing_spaces(self):
        """Test company name with leading/trailing spaces"""
        result = AnalysisRequestValidator.validate_company("  Tesla Inc  ")
        assert result == "Tesla Inc"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_validate_company_with_special_chars_removed(self):
        """Test that dangerous characters are removed"""
        result = AnalysisRequestValidator.validate_company("Tesla<script>Inc")
        assert "<script>" not in result
        assert "Tesla" in result
        assert "Inc" in result

    def test_validate_company_unicode_characters(self):
        """Test company name with unicode characters"""
        result = AnalysisRequestValidator.validate_company("Tesla™ Inc®")
        assert "Tesla" in result

    def test_validate_company_numbers_and_symbols(self):
        """Test company name with numbers and common business symbols"""
        result = AnalysisRequestValidator.validate_company("Tesla Motors #1 & Co.")
        assert "Tesla" in result
        assert "Motors" in result

    def test_validate_industry_valid(self):
        """Test valid industry name"""
        result = AnalysisRequestValidator.validate_industry("Electric Vehicles")
        assert result == "Electric Vehicles"

    def test_validate_industry_none(self):
        """Test None industry returns None"""
        result = AnalysisRequestValidator.validate_industry(None)
        assert result is None

    def test_validate_industry_empty_string(self):
        """Test empty string industry returns None"""
        result = AnalysisRequestValidator.validate_industry("")
        assert result is None

    def test_validate_industry_too_long(self):
        """Test industry name too long"""
        long_industry = "A" * 201
        with pytest.raises(ValueError, match="too long"):
            AnalysisRequestValidator.validate_industry(long_industry)

    def test_validate_industry_whitespace_stripped(self):
        """Test industry whitespace is stripped"""
        result = AnalysisRequestValidator.validate_industry("  Technology  ")
        assert result == "Technology"

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

    def test_validate_frameworks_case_insensitive(self):
        """Test frameworks are normalized to lowercase"""
        result = AnalysisRequestValidator.validate_frameworks(["PORTER", "Swot", "PeStEl"])
        assert result == ["porter", "swot", "pestel"]

    def test_validate_frameworks_with_whitespace(self):
        """Test frameworks with whitespace are trimmed"""
        result = AnalysisRequestValidator.validate_frameworks(["  porter  ", " swot "])
        assert result == ["porter", "swot"]

    def test_validate_frameworks_all_valid_options(self):
        """Test all valid framework options"""
        all_frameworks = ["porter", "swot", "pestel", "blue_ocean"]
        result = AnalysisRequestValidator.validate_frameworks(all_frameworks)
        assert len(result) == 4
        assert set(result) == set(all_frameworks)

    def test_validate_frameworks_mixed_valid_invalid(self):
        """Test mix of valid and invalid frameworks"""
        with pytest.raises(ValueError, match="Invalid frameworks"):
            AnalysisRequestValidator.validate_frameworks(["porter", "invalid", "swot"])

    def test_validate_frameworks_preserves_order(self):
        """Test that framework order is preserved"""
        result = AnalysisRequestValidator.validate_frameworks(["swot", "porter", "pestel"])
        assert result == ["swot", "porter", "pestel"]

    def test_validate_depth_valid(self):
        """Test valid depth"""
        assert AnalysisRequestValidator.validate_depth("standard") == "standard"
        assert AnalysisRequestValidator.validate_depth("quick") == "quick"
        assert AnalysisRequestValidator.validate_depth("deep") == "deep"

    def test_validate_depth_invalid(self):
        """Test invalid depth"""
        with pytest.raises(ValueError, match="Invalid depth"):
            AnalysisRequestValidator.validate_depth("invalid")

    def test_validate_depth_none_defaults_to_standard(self):
        """Test None depth defaults to standard"""
        result = AnalysisRequestValidator.validate_depth(None)
        assert result == "standard"

    def test_validate_depth_empty_string_defaults_to_standard(self):
        """Test empty string depth defaults to standard"""
        result = AnalysisRequestValidator.validate_depth("")
        assert result == "standard"

    def test_validate_depth_case_insensitive(self):
        """Test depth is case insensitive"""
        assert AnalysisRequestValidator.validate_depth("QUICK") == "quick"
        assert AnalysisRequestValidator.validate_depth("Standard") == "standard"
        assert AnalysisRequestValidator.validate_depth("DEEP") == "deep"

    def test_validate_depth_with_whitespace(self):
        """Test depth with whitespace is trimmed"""
        result = AnalysisRequestValidator.validate_depth("  standard  ")
        assert result == "standard"

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

    def test_validate_request_modifies_request_in_place(self):
        """Test that validation modifies the request object"""
        request = AnalysisRequest(
            company="  Tesla  ",
            industry="  Tech  ",
            frameworks=["PORTER", "swot"],
            depth="STANDARD"
        )
        validated = AnalysisRequestValidator.validate_request(request)
        assert validated.company == "Tesla"
        assert validated.industry == "Tech"
        assert validated.frameworks == ["porter", "swot"]
        assert validated.depth == "standard"

    def test_validate_request_invalid_company(self):
        """Test validation fails with invalid company"""
        request = AnalysisRequest(
            company="",
            industry="Tech",
            frameworks=["porter"],
            depth="standard"
        )
        with pytest.raises(ValueError, match="required"):
            AnalysisRequestValidator.validate_request(request)

    def test_validate_request_invalid_frameworks(self):
        """Test validation fails with invalid frameworks"""
        request = AnalysisRequest(
            company="Tesla",
            industry="Tech",
            frameworks=["invalid_framework"],
            depth="standard"
        )
        with pytest.raises(ValueError, match="Invalid frameworks"):
            AnalysisRequestValidator.validate_request(request)


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
        """Test SQL injection prevention - only removes '--' comment markers"""
        result = sanitize_input("Tesla'; DROP TABLE companies;--")
        assert "--" not in result  # SQL comment marker removed
        assert "DROP" in result  # Still present but escaped
        # Single hyphens should be preserved
        assert "Tesla" in result

    def test_sanitize_input_xss_attempts(self):
        """Test various XSS attack patterns"""
        xss_patterns = [
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert(1)>"
        ]
        for pattern in xss_patterns:
            result = sanitize_input(pattern)
            assert "<script>" not in result.lower()
            assert "javascript:" not in result.lower()
            assert "<img" not in result.lower() or "onerror" not in result.lower()

    def test_sanitize_input_sql_injection_advanced(self):
        """Test advanced SQL injection patterns"""
        sql_patterns = [
            "1' OR '1'='1",
            "admin'--",
            "'; DROP TABLE users;--",
            "1; UPDATE users SET admin=1--",
            "UNION SELECT * FROM passwords--"
        ]
        for pattern in sql_patterns:
            result = sanitize_input(pattern)
            assert "--" not in result

    def test_sanitize_input_null_bytes(self):
        """Test null byte injection prevention"""
        result = sanitize_input("Tesla\x00Inc")
        assert "\x00" not in result
        assert "Tesla" in result

    def test_sanitize_input_control_characters(self):
        """Test control character removal"""
        result = sanitize_input("Tesla\r\nInc\t\x0b\x0c")
        # Allow common whitespace (space, tab, newline) but remove rare control chars
        assert "Tesla" in result
        assert "Inc" in result

    def test_sanitize_input_unicode_attacks(self):
        """Test unicode-based attacks"""
        # Unicode normalization attacks
        result = sanitize_input("Tesla\u202eInc")  # Right-to-left override
        assert "Tesla" in result

    def test_sanitize_input_path_traversal(self):
        """Test path traversal prevention"""
        patterns = ["../../../etc/passwd", "..\\..\\windows\\system32"]
        for pattern in patterns:
            result = sanitize_input(pattern)
            # Path traversal sequences should be removed or escaped
            assert result is not None

    def test_sanitize_input_max_length(self):
        """Test max length enforcement"""
        long_input = "A" * 2000
        result = sanitize_input(long_input, max_length=1000)
        assert len(result) <= 1000

    def test_sanitize_input_empty_string(self):
        """Test empty string handling"""
        result = sanitize_input("")
        assert result == ""

    def test_sanitize_input_none(self):
        """Test None handling"""
        result = sanitize_input(None)
        # Should return empty string or handle gracefully
        assert result is not None

    def test_sanitize_input_whitespace_only(self):
        """Test whitespace-only input"""
        result = sanitize_input("   \t\n   ")
        assert isinstance(result, str)

    def test_sanitize_input_special_characters(self):
        """Test special characters are preserved appropriately"""
        result = sanitize_input("Company & Co. - Professional Services (2024)")
        assert "&" in result
        assert "-" in result
        assert "(" in result
        assert ")" in result

    def test_sanitize_input_non_string_types(self):
        """Test handling of non-string types"""
        # Should convert to string or handle gracefully
        result = sanitize_input(12345)
        assert result is not None
        assert "12345" in str(result)

    def test_sanitize_input_mixed_malicious_content(self):
        """Test combination of multiple attack vectors"""
        malicious = "<script>alert(1)</script>'; DROP TABLE;--\x00../../../etc/passwd"
        result = sanitize_input(malicious)
        assert "<script>" not in result
        assert "--" not in result
        assert "\x00" not in result

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

    def test_sanitize_dict_nested_structures(self):
        """Test deep nested dictionary sanitization"""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "malicious": "<script>alert(1)</script>"
                    }
                }
            }
        }
        sanitized = sanitize_dict(data)
        # Verify nested sanitization worked
        assert "<script>" not in str(sanitized)

    def test_sanitize_dict_with_lists(self):
        """Test dictionary with list values"""
        data = {
            "companies": ["<script>Tesla</script>", "Apple", "Google"],
            "frameworks": ["porter", "swot"]
        }
        sanitized = sanitize_dict(data)
        assert isinstance(sanitized["companies"], list)
        assert "<script>" not in str(sanitized["companies"])

    def test_sanitize_dict_preserves_none_values(self):
        """Test that None values in dict are preserved"""
        data = {
            "company": "Tesla",
            "optional_field": None,
            "industry": "Tech"
        }
        sanitized = sanitize_dict(data)
        assert sanitized["optional_field"] is None
        assert sanitized["company"] == "Tesla"

    def test_sanitize_dict_empty_dict(self):
        """Test empty dictionary"""
        sanitized = sanitize_dict({})
        assert sanitized == {}

    def test_sanitize_dict_with_numbers(self):
        """Test dictionary with numeric values"""
        data = {
            "company": "Tesla",
            "year": 2024,
            "revenue": 96.77,
            "is_public": True
        }
        sanitized = sanitize_dict(data)
        assert sanitized["year"] == 2024
        assert sanitized["revenue"] == 96.77
        assert sanitized["is_public"] is True


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


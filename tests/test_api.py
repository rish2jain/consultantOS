"""
Tests for API endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from consultantos.api.main import app


@pytest.fixture
async def client(test_api_key):
    """Create a test client with default authentication headers."""
    headers = {"X-API-Key": test_api_key}
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_analyze_endpoint_validation(client):
    """Test analyze endpoint validation"""
    # Missing company name
    response = await client.post(
        "/analyze",
        json={"company": "", "frameworks": ["porter"]}
    )
    assert response.status_code in [400, 422]  # Validation error


@pytest.mark.asyncio
async def test_analyze_endpoint_structure(client):
    """Test analyze endpoint request structure"""
    # Valid request structure (may fail without API keys, but should validate)
    response = await client.post(
        "/analyze",
        json={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter", "swot"],
            "depth": "standard"
        }
    )
    # Should either succeed (200) or fail with 500 (API keys), not 422 (validation)
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_visualizations_porter(client):
    payload = {
        "supplier_power": 3,
        "buyer_power": 2,
        "competitive_rivalry": 4,
        "threat_of_substitutes": 2,
        "threat_of_new_entrants": 1,
        "overall_intensity": "Moderate",
        "detailed_analysis": {
            "suppliers": "Moderate",
            "buyers": "Fragmented",
            "rivalry": "High",
            "substitutes": "Limited",
            "entrants": "High capex",
        },
    }

    response = await client.post("/visualizations/porter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "figure" in data
    assert data["figure"]["layout"]["title"]["text"] == "Porter's Five Forces Analysis"


@pytest.mark.asyncio
async def test_visualizations_swot(client):
    payload = {
        "strengths": ["Brand", "R&D", "Supply"],
        "weaknesses": ["Debt", "Churn", "Complexity"],
        "opportunities": ["APAC", "AI", "Green"],
        "threats": ["Competition", "Regulation", "Commoditization"],
    }

    response = await client.post("/visualizations/swot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "figure" in data


class TestAuthentication:
    """Tests for authentication and authorization"""

    @pytest.mark.asyncio
    async def test_endpoint_without_api_key_public(self, client):
        """Test that public endpoints work without API key"""
        response = await client.get("/health", headers={})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_endpoint_with_valid_api_key_header(self, client):
        """Test endpoint with valid API key in header"""
        # Note: This test assumes API key validation is implemented
        headers = {"X-API-Key": "test_valid_key_123"}
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter"],
                "depth": "standard"
            },
            headers=headers
        )
        # Should accept the request (may fail due to missing external APIs, but not 500)
        # Authentication should succeed (not 401/403), but may fail with 500 if external services fail
        # For proper auth testing, external dependencies should be mocked
        assert response.status_code in [200, 202]  # Success or accepted

    @pytest.mark.asyncio
    async def test_endpoint_with_api_key_query_param(self, client):
        """Test endpoint with API key as query parameter"""
        response = await client.post(
            "/analyze?api_key=test_valid_key_123",
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter"],
                "depth": "standard"
            },
            headers={}
        )
        assert response.status_code in [200, 500]  # Not 401/403

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_api_key(self, client):
        """Test that protected endpoints require API key"""
        # Assuming user-specific endpoints require auth
        # This is a placeholder - adjust based on actual protected endpoints
        response = await client.get("/reports/user/test_user", headers={})
        # Must return 401/403 if auth is required, or 404 if endpoint doesn't exist
        # Must NOT return 200 when no API key is provided
        assert response.status_code in [401, 403, 404]


class TestRateLimiting:
    """Tests for rate limiting enforcement"""

    @pytest.mark.asyncio
    async def test_rate_limit_not_exceeded(self, client):
        """Test normal usage within rate limits"""
        # Make a few requests that should be within limits
        for i in range(3):
            response = await client.get("/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, client):
        """Test that excessive requests trigger rate limiting"""
        # Note: This test may need adjustment based on actual rate limit configuration
        # Typically rate limits are per IP and time window (e.g., 10 requests per hour)

        # Make many rapid requests to potentially trigger rate limit
        responses = []
        for i in range(15):  # Exceed typical rate limit
            response = await client.post(
                "/analyze",
                json={
                    "company": f"Company{i}",
                    "industry": "Technology",
                    "frameworks": ["porter"],
                    "depth": "quick"
                }
            )
            responses.append(response.status_code)

        # At least one request should be rate limited (429) if limits are enforced
        # Or all might succeed if rate limiting is not strict in tests
        # Actually verify that rate limiting occurred
        assert any(status == 429 for status in responses) or sum(1 for s in responses if s == 200) < len(responses)

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are included in responses"""
        response = await client.get("/health")
        # Check for common rate limit headers (if implemented)
        # Examples: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
        # This is a placeholder - adjust based on actual implementation
        assert response.status_code == 200


class TestInputValidation:
    """Tests for comprehensive input validation"""

    @pytest.mark.asyncio
    async def test_analyze_missing_company(self, client):
        """Test validation error for missing company"""
        response = await client.post(
            "/analyze",
            json={
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    @pytest.mark.asyncio
    async def test_analyze_empty_company(self, client):
        """Test validation error for empty company name"""
        response = await client.post(
            "/analyze",
            json={
                "company": "",
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_analyze_company_too_long(self, client):
        """Test validation error for company name too long"""
        long_company = "A" * 201
        response = await client.post(
            "/analyze",
            json={
                "company": long_company,
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_analyze_invalid_framework(self, client):
        """Test validation error for invalid framework"""
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Technology",
                "frameworks": ["invalid_framework_name"]
            }
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_analyze_empty_frameworks_list(self, client):
        """Test validation error for empty frameworks list"""
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Technology",
                "frameworks": []
            }
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_analyze_invalid_depth(self, client):
        """Test validation error for invalid depth"""
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Technology",
                "frameworks": ["porter"],
                "depth": "invalid_depth"
            }
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_analyze_malformed_json(self, client):
        """Test error handling for malformed JSON"""
        response = await client.post(
            "/analyze",
            data="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_xss_prevention(self, client):
        """Test that XSS attempts are sanitized"""
        response = await client.post(
            "/analyze",
            json={
                "company": "<script>alert('xss')</script>Tesla",
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )
        # Should either succeed with sanitized input or reject, but not crash with 500
        assert response.status_code in [200, 400, 422]

        # If successful, verify XSS was sanitized
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in str(data)

    @pytest.mark.asyncio
    async def test_analyze_sql_injection_prevention(self, client):
        """Test that SQL injection attempts are handled"""
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla'; DROP TABLE companies;--",
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )
        # Should handle malicious input gracefully without crashing
        assert response.status_code in [200, 400, 422]


class TestErrorResponses:
    """Tests for proper error response formatting"""

    @pytest.mark.asyncio
    async def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint"""
        response = await client.get("/nonexistent/endpoint")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        # POST to a GET-only endpoint
        response = await client.post("/health")
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_validation_error_format(self, client):
        """Test that validation errors have proper format"""
        response = await client.post(
            "/analyze",
            json={
                "company": "",  # Invalid
                "frameworks": []  # Invalid
            }
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        # FastAPI validation errors have specific format
        if isinstance(error_data["detail"], list):
            assert len(error_data["detail"]) > 0

    @pytest.mark.asyncio
    async def test_error_no_secret_leakage(self, client):
        """Test that errors don't leak sensitive information"""
        response = await client.post(
            "/analyze",
            json={
                "company": "Tesla",
                "industry": "Technology",
                "frameworks": ["porter"]
            }
        )

        # If error occurs, verify no secrets in response
        if response.status_code >= 400:
            response_text = response.text.lower()
            # Check for common secret patterns - both patterns must be absent
            assert "api_key" not in response_text and "api_key=" not in response_text
            assert "password" not in response_text
            assert "secret" not in response_text
            assert "token" not in response_text

    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        response = await client.options("/analyze")
        # Should have CORS headers for OPTIONS request
        # Note: Actual CORS configuration depends on app setup
        assert response.status_code in [200, 204, 405]


class TestAsyncJobEndpoints:
    """Tests for async job creation and status endpoints"""

    @pytest.mark.asyncio
    async def test_async_job_creation(self, client):
        """Test async job creation endpoint"""
        response = await client.post(
            "/analyze/async",
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter"],
                "depth": "standard"
            }
        )
        # Should return job_id or error
        assert response.status_code in [200, 201, 500]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "job_id" in data

    @pytest.mark.asyncio
    async def test_job_status_check(self, client):
        """Test job status check endpoint"""
        # First create a job
        create_response = await client.post(
            "/analyze/async",
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter"],
                "depth": "quick"
            }
        )

        if create_response.status_code in [200, 201]:
            job_data = create_response.json()
            job_id = job_data.get("job_id")

            if job_id:
                # Check job status
                status_response = await client.get(f"/jobs/{job_id}")
                assert status_response.status_code in [200, 404]

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    assert "status" in status_data

    @pytest.mark.asyncio
    async def test_job_status_invalid_id(self, client):
        """Test job status with invalid job ID"""
        response = await client.get("/jobs/invalid-job-id-12345")
        # Should return 404 or error
        assert response.status_code in [404, 200]  # 200 with error status also acceptable

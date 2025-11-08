"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from consultantos.api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_endpoint_validation():
    """Test analyze endpoint validation"""
    # Missing company name
    response = client.post(
        "/analyze",
        json={"company": "", "frameworks": ["porter"]}
    )
    assert response.status_code in [400, 422]  # Validation error


def test_analyze_endpoint_structure():
    """Test analyze endpoint request structure"""
    # Valid request structure (may fail without API keys, but should validate)
    response = client.post(
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


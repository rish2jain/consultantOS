#!/usr/bin/env python3
"""
Test script for health endpoints and monitoring infrastructure
"""
import asyncio
import requests
import json
from datetime import datetime

# Base URL (adjust if server is running on different port)
BASE_URL = "http://localhost:8080"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def test_health_endpoint(endpoint, expected_status=200):
    """Test a health endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing: {endpoint}")
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")

        if response.status_code == expected_status:
            print("  ✓ Status code matches expected")
        else:
            print(f"  ✗ Expected {expected_status}, got {response.status_code}")

        # Pretty print JSON response
        try:
            data = response.json()
            print("  Response:")
            print(json.dumps(data, indent=4))
        except (json.JSONDecodeError, ValueError):
            print(f"  Response (text): {response.text[:200]}")

        return response.status_code == expected_status
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_prometheus_metrics():
    """Test Prometheus metrics endpoint"""
    url = f"{BASE_URL}/health/metrics"
    print(f"Testing: /health/metrics (Prometheus format)")
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  ✓ Status code OK")

            # Check for expected metric types
            text = response.text
            expected_metrics = [
                "consultantos_requests_total",
                "consultantos_cache_hits",
                "consultantos_cache_misses",
                "TYPE",
                "HELP"
            ]

            print("  Checking for expected metrics:")
            for metric in expected_metrics:
                if metric in text:
                    print(f"    ✓ {metric} found")
                else:
                    print(f"    ✗ {metric} not found")

            # Show first few lines
            lines = text.split('\n')[:10]
            print("\n  First 10 lines:")
            for line in lines:
                print(f"    {line}")

            return True
        else:
            print(f"  ✗ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_request_id_tracking():
    """Test request ID middleware"""
    url = f"{BASE_URL}/health/live"
    print(f"Testing: Request ID tracking")

    try:
        # Test 1: Auto-generated request ID
        print("\n  Test 1: Auto-generated request ID")
        response = requests.get(url, timeout=5)
        request_id = response.headers.get('X-Request-ID')
        if request_id:
            print(f"    ✓ Request ID generated: {request_id}")
        else:
            print(f"    ✗ No X-Request-ID header in response")

        # Test 2: Custom request ID
        print("\n  Test 2: Custom request ID")
        custom_id = "test-request-12345"
        response = requests.get(url, headers={'X-Request-ID': custom_id}, timeout=5)
        returned_id = response.headers.get('X-Request-ID')
        if returned_id == custom_id:
            print(f"    ✓ Custom request ID preserved: {returned_id}")
        else:
            print(f"    ✗ Expected {custom_id}, got {returned_id}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all health endpoint tests"""
    print(f"\n{'*' * 60}")
    print(f"  ConsultantOS Health Endpoint Test Suite")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"  Base URL: {BASE_URL}")
    print(f"{'*' * 60}")

    results = {}

    # Test liveness probe
    print_section("Liveness Probe")
    results['liveness'] = test_health_endpoint("/health/live", 200)

    # Test readiness probe
    print_section("Readiness Probe")
    results['readiness'] = test_health_endpoint("/health/ready", 200)

    # Test startup probe
    print_section("Startup Probe")
    results['startup'] = test_health_endpoint("/health/startup", 200)

    # Test detailed health check
    print_section("Detailed Health Check")
    results['detailed'] = test_health_endpoint("/health/detailed", 200)

    # Test Prometheus metrics
    print_section("Prometheus Metrics")
    results['metrics'] = test_prometheus_metrics()

    # Test request ID tracking
    print_section("Request ID Tracking")
    results['request_id'] = test_request_id_tracking()

    # Summary
    print_section("Test Summary")
    passed = sum(results.values())
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {test_name:20s} {status}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  ✓ All tests passed!")
        return 0
    else:
        print(f"\n  ✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys

    print("\nNote: This script requires the ConsultantOS server to be running.")
    print("Start the server with: python main.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)

    exit_code = main()
    sys.exit(exit_code)

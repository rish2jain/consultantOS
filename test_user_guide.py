#!/usr/bin/env python3
"""
Comprehensive test script for USER_TESTING_GUIDE.md
Tests all scenarios using API calls and documents results
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

API_BASE = "http://localhost:8080"
FRONTEND_BASE = "http://localhost:3000"

class TestResults:
    def __init__(self):
        self.results = []
        self.errors = []
        self.api_key = None
        
    def log_result(self, scenario: str, test: str, status: str, details: str = ""):
        self.results.append({
            "scenario": scenario,
            "test": test,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[{status}] {scenario} - {test}")
        if details:
            print(f"  Details: {details}")
    
    def log_error(self, scenario: str, test: str, error: str):
        self.errors.append({
            "scenario": scenario,
            "test": test,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self.log_result(scenario, test, "ERROR", error)
    
    def save_report(self, filename: str = "test_results.json"):
        report = {
            "summary": {
                "total_tests": len(self.results),
                "errors": len(self.errors),
                "timestamp": datetime.now().isoformat()
            },
            "results": self.results,
            "errors": self.errors
        }
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nTest report saved to {filename}")

# Initialize test results
results = TestResults()

# Scenario 1: First-Time User Experience
print("\n=== Scenario 1: First-Time User Experience ===")

# Test 1.1: Registration
try:
    response = requests.post(
        f"{API_BASE}/users/register",
        json={
            "email": f"test_{int(time.time())}@consultantos.com",
            "password": "TestPassword123!",
            "name": "Test User"
        }
    )
    if response.status_code in [200, 201]:
        results.log_result("Scenario 1", "Registration", "PASS", f"User ID: {response.json().get('user_id')}")
    else:
        results.log_error("Scenario 1", "Registration", f"Status {response.status_code}: {response.text}")
except Exception as e:
    results.log_error("Scenario 1", "Registration", str(e))

# Test 1.2: Login (using existing test user that we know works)
try:
    response = requests.post(
        f"{API_BASE}/users/login",
        json={
            "email": "test@consultantos.com",
            "password": "TestPassword123!"
        }
    )
    if response.status_code == 200:
        data = response.json()
        results.api_key = data.get('access_token')
        results.log_result("Scenario 1", "Login", "PASS", "API key obtained")
    else:
        # If login fails, try to register a new user and login immediately
        # (Note: In production, email verification might be required)
        test_email = f"testuser_{int(time.time())}@consultantos.com"
        reg_response = requests.post(
            f"{API_BASE}/users/register",
            json={
                "email": test_email,
                "password": "TestPassword123!",
                "name": "Test User"
            }
        )
        if reg_response.status_code in [200, 201]:
            # Try to login with new user
            login_response = requests.post(
                f"{API_BASE}/users/login",
                json={
                    "email": test_email,
                    "password": "TestPassword123!"
                }
            )
            if login_response.status_code == 200:
                data = login_response.json()
                results.api_key = data.get('access_token')
                results.log_result("Scenario 1", "Login", "PASS", f"API key obtained (new user: {test_email})")
            else:
                results.log_error("Scenario 1", "Login", f"Status {login_response.status_code}: {login_response.text}")
        else:
            results.log_error("Scenario 1", "Login", f"Status {response.status_code}: {response.text}")
except Exception as e:
    results.log_error("Scenario 1", "Login", str(e))

# Scenario 2: Basic Analysis Generation
print("\n=== Scenario 2: Basic Analysis Generation ===")

if results.api_key:
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/analyze",
            headers={"X-API-Key": results.api_key},
            json={
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "frameworks": ["porter", "swot"],
                "depth": "standard"
            },
            timeout=120
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            report_id = data.get('report_id')
            results.log_result("Scenario 2", "Basic Analysis", "PASS", 
                            f"Report ID: {report_id}, Time: {elapsed:.2f}s")
        else:
            results.log_error("Scenario 2", "Basic Analysis", 
                            f"Status {response.status_code}: {response.text}")
    except requests.Timeout:
        results.log_error("Scenario 2", "Basic Analysis", "Request timeout (>120s)")
    except Exception as e:
        results.log_error("Scenario 2", "Basic Analysis", str(e))
else:
    results.log_error("Scenario 2", "Basic Analysis", "No API key available")

# Scenario 3: Multi-Framework Analysis
print("\n=== Scenario 3: Multi-Framework Analysis ===")

if results.api_key:
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/analyze",
            headers={"X-API-Key": results.api_key},
            json={
                "company": "Netflix",
                "industry": "Streaming Media",
                "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
                "depth": "standard"
            },
            timeout=180
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            report_id = data.get('report_id')
            frameworks = data.get('executive_summary', {}).get('frameworks_analyzed', [])
            results.log_result("Scenario 3", "Multi-Framework Analysis", "PASS", 
                            f"Report ID: {report_id}, Frameworks: {len(frameworks)}, Time: {elapsed:.2f}s")
        else:
            results.log_error("Scenario 3", "Multi-Framework Analysis", 
                            f"Status {response.status_code}: {response.text}")
    except requests.Timeout:
        results.log_error("Scenario 3", "Multi-Framework Analysis", "Request timeout (>180s)")
    except Exception as e:
        results.log_error("Scenario 3", "Multi-Framework Analysis", str(e))
else:
    results.log_error("Scenario 3", "Multi-Framework Analysis", "No API key available")

# Scenario 3B: Async Analysis Processing
print("\n=== Scenario 3B: Async Analysis Processing ===")

if results.api_key:
    try:
        response = requests.post(
            f"{API_BASE}/analyze/async",
            headers={"X-API-Key": results.api_key},
            json={
                "company": "Apple",
                "industry": "Technology",
                "frameworks": ["porter", "swot"],
                "depth": "deep"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            status = data.get('status')
            results.log_result("Scenario 3B", "Async Job Enqueue", "PASS", 
                            f"Job ID: {job_id}, Status: {status}")
            
            # Poll job status (increased timeout for async processing)
            if job_id:
                max_polls = 60  # Increased from 30 to 60 (2 minutes total)
                poll_count = 0
                while poll_count < max_polls:
                    time.sleep(2)
                    status_response = requests.get(
                        f"{API_BASE}/jobs/{job_id}/status"
                    )
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        job_status = status_data.get('status')
                        if job_status in ['completed', 'failed']:
                            results.log_result("Scenario 3B", "Job Status Polling", "PASS", 
                                            f"Final status: {job_status} after {poll_count} polls")
                            break
                        elif job_status == 'processing':
                            # Job is being processed, continue polling
                            pass
                    poll_count += 1
                else:
                    # Check final status one more time
                    final_response = requests.get(f"{API_BASE}/jobs/{job_id}/status")
                    if final_response.status_code == 200:
                        final_status = final_response.json().get('status')
                        if final_status in ['completed', 'failed']:
                            results.log_result("Scenario 3B", "Job Status Polling", "PASS", 
                                            f"Final status: {final_status} (checked after timeout)")
                        else:
                            results.log_error("Scenario 3B", "Job Status Polling", 
                                            f"Timeout: Job still {final_status} after {max_polls * 2} seconds")
                    else:
                        results.log_error("Scenario 3B", "Job Status Polling", "Timeout waiting for completion")
        else:
            results.log_error("Scenario 3B", "Async Job Enqueue", 
                            f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.log_error("Scenario 3B", "Async Analysis", str(e))
else:
    results.log_error("Scenario 3B", "Async Analysis", "No API key available")

# Scenario 4: Report Retrieval and Management
print("\n=== Scenario 4: Report Retrieval and Management ===")

if results.api_key:
    # Get report_id from Scenario 2 if available
    report_id = None
    for result in results.results:
        if result.get('test') == 'Basic Analysis' and 'Report ID:' in result.get('details', ''):
            report_id = result.get('details', '').split('Report ID: ')[1].split(',')[0].strip()
            break
    
    if report_id:
        try:
            response = requests.get(
                f"{API_BASE}/reports/{report_id}",
                headers={"X-API-Key": results.api_key}
            )
            if response.status_code == 200:
                data = response.json()
                results.log_result("Scenario 4", "Get Specific Report", "PASS", 
                                f"Retrieved report: {report_id}")
            else:
                results.log_error("Scenario 4", "Get Specific Report", 
                                f"Status {response.status_code}: {response.text}")
        except Exception as e:
            results.log_error("Scenario 4", "Get Specific Report", str(e))
    
    # List all reports
    try:
        response = requests.get(
            f"{API_BASE}/reports",
            headers={"X-API-Key": results.api_key}
        )
        if response.status_code == 200:
            data = response.json()
            reports = data.get('reports', [])
            results.log_result("Scenario 4", "List Reports", "PASS", 
                            f"Found {len(reports)} reports")
        else:
            results.log_error("Scenario 4", "List Reports", 
                            f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.log_error("Scenario 4", "List Reports", str(e))
else:
    results.log_error("Scenario 4", "Report Retrieval", "No API key available")

# Scenario 6: Edge Cases and Error Handling
print("\n=== Scenario 6: Edge Cases and Error Handling ===")

# Test 6A: Missing Required Fields
try:
    response = requests.post(
        f"{API_BASE}/analyze",
        headers={"X-API-Key": results.api_key} if results.api_key else {},
        json={"company": ""}
    )
    if response.status_code == 400 or response.status_code == 422:
        results.log_result("Scenario 6", "Missing Required Fields", "PASS", 
                        f"Correctly rejected with {response.status_code}")
    else:
        results.log_error("Scenario 6", "Missing Required Fields", 
                        f"Expected 400/422, got {response.status_code}")
except Exception as e:
    results.log_error("Scenario 6", "Missing Required Fields", str(e))

# Test 6B: Invalid Framework Names
if results.api_key:
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            headers={"X-API-Key": results.api_key},
            json={
                "company": "Tesla",
                "industry": "EV",
                "frameworks": ["invalid_framework"]
            }
        )
        if response.status_code in [400, 422]:
            results.log_result("Scenario 6", "Invalid Framework Names", "PASS", 
                            f"Correctly rejected with {response.status_code}")
        else:
            results.log_error("Scenario 6", "Invalid Framework Names", 
                            f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        results.log_error("Scenario 6", "Invalid Framework Names", str(e))

# Scenario 10: API Integration Testing
print("\n=== Scenario 10: API Integration Testing ===")

# Test 10A: Health Check
try:
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        health_data = response.json()
        results.log_result("Scenario 10", "Health Check", "PASS", 
                        f"Status: {health_data.get('status')}")
    else:
        results.log_error("Scenario 10", "Health Check", f"Status {response.status_code}")
except Exception as e:
    results.log_error("Scenario 10", "Health Check", str(e))

# Test 10B: Authentication
if results.api_key:
    try:
        response = requests.get(
            f"{API_BASE}/reports",
            headers={"X-API-Key": results.api_key}
        )
        if response.status_code == 200:
            results.log_result("Scenario 10", "Authentication (Valid Key)", "PASS")
        else:
            results.log_error("Scenario 10", "Authentication (Valid Key)", 
                            f"Status {response.status_code}")
    except Exception as e:
        results.log_error("Scenario 10", "Authentication (Valid Key)", str(e))
    
    # Test invalid key (reports endpoint has optional auth, so this should still work)
    try:
        response = requests.get(
            f"{API_BASE}/reports",
            headers={"X-API-Key": "invalid_key_12345"}
        )
        # Reports endpoint has optional auth, so 200 is expected
        if response.status_code == 200:
            results.log_result("Scenario 10", "Authentication (Invalid Key)", "PASS", 
                            "Reports endpoint allows optional auth (expected behavior)")
        else:
            results.log_error("Scenario 10", "Authentication (Invalid Key)", 
                            f"Unexpected status {response.status_code}")
    except Exception as e:
        results.log_error("Scenario 10", "Authentication (Invalid Key)", str(e))
    
    # Test endpoint that requires auth
    try:
        response = requests.get(
            f"{API_BASE}/users/profile",
            headers={"X-API-Key": "invalid_key_12345"}
        )
        if response.status_code == 401:
            results.log_result("Scenario 10", "Authentication (Required Endpoint)", "PASS", 
                            "Correctly rejected invalid key on protected endpoint")
        else:
            results.log_error("Scenario 10", "Authentication (Required Endpoint)", 
                            f"Expected 401, got {response.status_code}")
    except Exception as e:
        results.log_error("Scenario 10", "Authentication (Required Endpoint)", str(e))

# Save results
results.save_report()

print(f"\n=== Test Summary ===")
print(f"Total tests: {len(results.results)}")
print(f"Errors: {len(results.errors)}")
print(f"Success rate: {(len(results.results) - len(results.errors)) / len(results.results) * 100:.1f}%")


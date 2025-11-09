#!/usr/bin/env python3
"""
Quick test to verify async job processing works
"""
import requests
import time

API_BASE = "http://localhost:8080"

# Login to get API key
print("Logging in...")
response = requests.post(
    f"{API_BASE}/users/login",
    json={
        "email": "test@consultantos.com",
        "password": "TestPassword123!"
    },
    timeout=10
)

if response.status_code != 200:
    print(f"Login failed: {response.status_code}")
    exit(1)

api_key = response.json().get('access_token')
print(f"✓ Login successful, API key obtained")

# Enqueue async job
print("\nEnqueuing async job...")
response = requests.post(
    f"{API_BASE}/analyze/async",
    headers={"X-API-Key": api_key},
    json={
        "company": "Microsoft",
        "industry": "Technology",
        "frameworks": ["porter"],
        "depth": "standard"
    },
    timeout=10
)

if response.status_code != 200:
    print(f"✗ Enqueue failed: {response.status_code} - {response.text}")
    exit(1)

data = response.json()
job_id = data.get('job_id')
print(f"✓ Job enqueued: {job_id}")

# Poll job status
print("\nPolling job status (max 60 seconds)...")
max_polls = 30
poll_count = 0
start_time = time.time()

while poll_count < max_polls:
    time.sleep(2)
    poll_count += 1
    elapsed = time.time() - start_time
    
    try:
        status_response = requests.get(f"{API_BASE}/jobs/{job_id}/status", timeout=10)
    except requests.exceptions.Timeout:
        print(f"  Poll {poll_count}: Request timeout")
        continue
    except requests.exceptions.RequestException as e:
        print(f"  Poll {poll_count}: Request error: {e}")
        continue
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        job_status = status_data.get('status')
        print(f"  Poll {poll_count} ({elapsed:.1f}s): Status = {job_status}")
        
        if job_status in ['completed', 'failed']:
            print(f"\n✓ Job finished with status: {job_status}")
            if job_status == 'completed':
                report_id = status_data.get('report_id')
                print(f"  Report ID: {report_id}")
            exit(0)
    else:
        print(f"  Poll {poll_count}: Error {status_response.status_code}")

print(f"\n✗ Timeout: Job did not complete within {max_polls * 2} seconds")
exit(1)


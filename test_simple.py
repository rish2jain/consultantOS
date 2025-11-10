#!/usr/bin/env python3
"""
Simple integration test without heavy dependencies.
Tests basic integration without loading LLM models.
"""
import sys

print("=== Simple Integration Test ===\n")

# Test 1: Basic imports
print("1. Testing basic module structure...")
try:
    import consultantos
    import consultantos.api
    import consultantos.models
    import consultantos.agents
    print("   ✓ Core modules importable")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: Integration models (without instantiation)
print("\n2. Testing integration model definitions...")
try:
    from consultantos.models.integration import (
        ComprehensiveAnalysisRequest,
        ComprehensiveAnalysisResult
    )
    print("   ✓ Integration models defined")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 3: Agent availability utilities
print("\n3. Testing agent utilities...")
try:
    from consultantos.agents import get_available_agents
    agents = get_available_agents()
    print(f"   ✓ Agent detection works: {len(agents)} agents")
    for agent in agents:
        print(f"      - {agent}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 4: API endpoints exist
print("\n4. Testing API endpoint structure...")
try:
    from consultantos.api import integration_endpoints
    from consultantos.api import mvp_endpoints
    print("   ✓ Integration endpoints module exists")
    print("   ✓ MVP endpoints module exists")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 5: Integration files exist
print("\n5. Testing integration file structure...")
import os
required_files = [
    'consultantos/models/integration.py',
    'consultantos/integration/data_flow.py',
    'consultantos/api/integration_endpoints.py',
]
for filepath in required_files:
    if os.path.exists(filepath):
        print(f"   ✓ {filepath}")
    else:
        print(f"   ✗ Missing: {filepath}")
        sys.exit(1)

print("\n=== ✅ ALL BASIC TESTS PASSED ===")
print("\nNOTE: This was a basic structure test.")
print("Run 'python -m pytest tests/test_integration.py' for full integration tests.")

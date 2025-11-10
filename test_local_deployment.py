#!/usr/bin/env python3
"""
Comprehensive local testing script for ConsultantOS deployment validation.

This script tests:
1. Docker build validation
2. Import validation
3. Health endpoint checks
4. Configuration validation
5. Basic API functionality

Run this before deploying to catch issues early.
"""
import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Tuple
import importlib.util

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class TestResult:
    """Test result container"""
    def __init__(self, name: str, passed: bool, message: str = "", details: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

class LocalDeploymentTester:
    """Comprehensive local deployment testing"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.project_root = Path(__file__).parent
        self.docker_image = "consultantos:local-test"
        self.container_name = "consultantos-test"
        self.port = 8080
        
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    def print_test(self, name: str):
        """Print test name"""
        print(f"{BLUE}Testing: {name}...{RESET}", end=" ", flush=True)
    
    def print_result(self, result: TestResult):
        """Print test result"""
        if result.passed:
            print(f"{GREEN}✓ PASSED{RESET}")
            if result.message:
                print(f"  {result.message}")
        else:
            print(f"{RED}✗ FAILED{RESET}")
            if result.message:
                print(f"  {RED}{result.message}{RESET}")
            if result.details:
                print(f"  {YELLOW}Details: {result.details}{RESET}")
        
        self.results.append(result)
    
    def test_imports(self) -> TestResult:
        """Test that all critical imports work"""
        self.print_test("Critical Imports")
        
        critical_imports = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "consultantos.api.main",
            "consultantos.config",
            "consultantos.database",
            "consultantos.storage",
            "consultantos.cache",
        ]
        
        failed_imports = []
        for module_name in critical_imports:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append(f"{module_name}: {str(e)}")
            except Exception as e:
                failed_imports.append(f"{module_name}: {str(e)}")
        
        if failed_imports:
            return TestResult(
                "Critical Imports",
                False,
                f"Failed to import {len(failed_imports)} modules",
                "\n".join(failed_imports)
            )
        
        return TestResult("Critical Imports", True, f"All {len(critical_imports)} imports successful")
    
    def test_configuration(self) -> TestResult:
        """Test configuration loading"""
        self.print_test("Configuration")
        
        try:
            from consultantos import config
            settings = config.settings
            
            # Check required settings exist
            required_attrs = [
                'environment',
                'log_level',
                'rate_limit_per_hour',
            ]
            
            missing = []
            for attr in required_attrs:
                if not hasattr(settings, attr):
                    missing.append(attr)
            
            if missing:
                return TestResult(
                    "Configuration",
                    False,
                    f"Missing configuration attributes: {', '.join(missing)}"
                )
            
            return TestResult("Configuration", True, "Configuration loaded successfully")
            
        except Exception as e:
            return TestResult(
                "Configuration",
                False,
                f"Failed to load configuration: {str(e)}"
            )
    
    def test_dockerfile_exists(self) -> TestResult:
        """Test that Dockerfile exists and is valid"""
        self.print_test("Dockerfile Validation")
        
        dockerfile_path = self.project_root / "Dockerfile"
        if not dockerfile_path.exists():
            return TestResult(
                "Dockerfile Validation",
                False,
                "Dockerfile not found"
            )
        
        # Check for common issues in Dockerfile
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check for healthcheck (required for Cloud Run)
        if "HEALTHCHECK" not in content:
            issues.append("Missing HEALTHCHECK directive")
        
        # Check for PORT environment variable handling
        if "${PORT:-8080}" not in content and "PORT" not in content:
            issues.append("Missing PORT environment variable handling")
        
        # Check for proper CMD
        if "CMD" not in content:
            issues.append("Missing CMD directive")
        
        if issues:
            return TestResult(
                "Dockerfile Validation",
                False,
                f"Found {len(issues)} issues",
                "\n".join(issues)
            )
        
        return TestResult("Dockerfile Validation", True, "Dockerfile looks valid")
    
    def test_requirements_txt(self) -> TestResult:
        """Test requirements.txt exists and is parseable"""
        self.print_test("Requirements.txt")
        
        requirements_path = self.project_root / "requirements.txt"
        if not requirements_path.exists():
            return TestResult(
                "Requirements.txt",
                False,
                "requirements.txt not found"
            )
        
        try:
            with open(requirements_path, 'r') as f:
                lines = f.readlines()
            
            # Check for common issues
            issues = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for invalid version specifiers
                if '==' in line and '>=' in line:
                    issues.append(f"Line {i}: Conflicting version specifiers")
            
            if issues:
                return TestResult(
                    "Requirements.txt",
                    False,
                    f"Found {len(issues)} issues",
                    "\n".join(issues)
                )
            
            return TestResult("Requirements.txt", True, f"Found {len([l for l in lines if l.strip() and not l.strip().startswith('#')])} packages")
            
        except Exception as e:
            return TestResult(
                "Requirements.txt",
                False,
                f"Failed to parse: {str(e)}"
            )
    
    def test_docker_build(self) -> TestResult:
        """Test Docker build locally"""
        self.print_test("Docker Build")
        
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return TestResult(
                    "Docker Build",
                    False,
                    "Docker is not available or not running"
                )
            
            # Try to build the Docker image
            print(f"\n  {YELLOW}Building Docker image (this may take a few minutes)...{RESET}")
            build_result = subprocess.run(
                ["docker", "build", "-t", self.docker_image, "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if build_result.returncode != 0:
                # Extract error message
                error_lines = build_result.stderr.split('\n')[-10:]  # Last 10 lines
                return TestResult(
                    "Docker Build",
                    False,
                    "Docker build failed",
                    "\n".join(error_lines)
                )
            
            return TestResult("Docker Build", True, "Docker image built successfully")
            
        except subprocess.TimeoutExpired:
            return TestResult(
                "Docker Build",
                False,
                "Docker build timed out (exceeded 10 minutes)"
            )
        except FileNotFoundError:
            return TestResult(
                "Docker Build",
                False,
                "Docker command not found. Is Docker installed?"
            )
        except Exception as e:
            return TestResult(
                "Docker Build",
                False,
                f"Unexpected error: {str(e)}"
            )
    
    def test_docker_run(self) -> TestResult:
        """Test running Docker container"""
        self.print_test("Docker Run")
        
        try:
            # Stop and remove existing container if it exists
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["docker", "rm", self.container_name],
                capture_output=True,
                timeout=5
            )
            
            # Start container
            print(f"\n  {YELLOW}Starting container...{RESET}")
            run_result = subprocess.run(
                [
                    "docker", "run", "-d",
                    "--name", self.container_name,
                    "-p", f"{self.port}:8080",
                    "-e", "GEMINI_API_KEY=test-key-placeholder",
                    "-e", "TAVILY_API_KEY=test-key-placeholder",
                    "-e", "ENVIRONMENT=development",
                    self.docker_image
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if run_result.returncode != 0:
                return TestResult(
                    "Docker Run",
                    False,
                    "Failed to start container",
                    run_result.stderr
                )
            
            # Wait for container to be ready
            print(f"  {YELLOW}Waiting for container to be ready...{RESET}")
            time.sleep(10)
            
            # Check if container is running
            ps_result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if self.container_name not in ps_result.stdout:
                # Get logs
                logs_result = subprocess.run(
                    ["docker", "logs", self.container_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return TestResult(
                    "Docker Run",
                    False,
                    "Container started but is not running",
                    logs_result.stdout[-500:]  # Last 500 chars
                )
            
            return TestResult("Docker Run", True, "Container is running")
            
        except Exception as e:
            return TestResult(
                "Docker Run",
                False,
                f"Error: {str(e)}"
            )
    
    def test_health_endpoints(self) -> TestResult:
        """Test health endpoints"""
        self.print_test("Health Endpoints")
        
        try:
            base_url = f"http://localhost:{self.port}"
            
            # Test liveness
            try:
                response = requests.get(f"{base_url}/health/live", timeout=5)
                if response.status_code != 200:
                    return TestResult(
                        "Health Endpoints",
                        False,
                        f"Liveness probe failed: {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                return TestResult(
                    "Health Endpoints",
                    False,
                    f"Failed to connect to liveness endpoint: {str(e)}"
                )
            
            # Test readiness (may fail if services not configured, that's OK)
            try:
                response = requests.get(f"{base_url}/health/ready", timeout=5)
                # 503 is acceptable if services aren't configured
                if response.status_code not in [200, 503]:
                    return TestResult(
                        "Health Endpoints",
                        False,
                        f"Readiness probe returned unexpected status: {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                return TestResult(
                    "Health Endpoints",
                    False,
                    f"Failed to connect to readiness endpoint: {str(e)}"
                )
            
            # Test main health endpoint
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code != 200:
                    return TestResult(
                        "Health Endpoints",
                        False,
                        f"Main health endpoint failed: {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                return TestResult(
                    "Health Endpoints",
                    False,
                    f"Failed to connect to main health endpoint: {str(e)}"
                )
            
            return TestResult("Health Endpoints", True, "All health endpoints responding")
            
        except Exception as e:
            return TestResult(
                "Health Endpoints",
                False,
                f"Unexpected error: {str(e)}"
            )
    
    def test_api_docs(self) -> TestResult:
        """Test API documentation endpoints"""
        self.print_test("API Documentation")
        
        try:
            base_url = f"http://localhost:{self.port}"
            
            # Test OpenAPI schema
            response = requests.get(f"{base_url}/openapi.json", timeout=5)
            if response.status_code != 200:
                return TestResult(
                    "API Documentation",
                    False,
                    f"OpenAPI schema failed: {response.status_code}"
                )
            
            # Test docs endpoint
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code != 200:
                return TestResult(
                    "API Documentation",
                    False,
                    f"Docs endpoint failed: {response.status_code}"
                )
            
            return TestResult("API Documentation", True, "API docs accessible")
            
        except Exception as e:
            return TestResult(
                "API Documentation",
                False,
                f"Error: {str(e)}"
            )
    
    def cleanup(self):
        """Clean up test containers"""
        try:
            print(f"\n{YELLOW}Cleaning up test containers...{RESET}")
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                timeout=5
            )
            subprocess.run(
                ["docker", "rm", self.container_name],
                capture_output=True,
                timeout=5
            )
            print(f"{GREEN}Cleanup complete{RESET}")
        except Exception:
            pass  # Ignore cleanup errors
    
    def run_all_tests(self, skip_docker: bool = False):
        """Run all tests"""
        self.print_header("ConsultantOS Local Deployment Testing")
        
        print(f"{BOLD}This script validates your code before deployment.{RESET}\n")
        print(f"Project root: {self.project_root}\n")
        
        # Basic validation tests (always run)
        self.print_header("Basic Validation")
        result = self.test_imports()
        self.print_result(result)
        
        result = self.test_configuration()
        self.print_result(result)
        
        result = self.test_dockerfile_exists()
        self.print_result(result)
        
        result = self.test_requirements_txt()
        self.print_result(result)
        
        if not skip_docker:
            # Docker tests
            self.print_header("Docker Validation")
            result = self.test_docker_build()
            self.print_result(result)
            
            if result.passed:
                result = self.test_docker_run()
                self.print_result(result)
                
                if result.passed:
                    # Runtime tests
                    self.print_header("Runtime Validation")
                    result = self.test_health_endpoints()
                    self.print_result(result)
                    
                    result = self.test_api_docs()
                    self.print_result(result)
        
        # Summary
        self.print_header("Test Summary")
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}\n")
        
        for result in self.results:
            status = f"{GREEN}✓{RESET}" if result.passed else f"{RED}✗{RESET}"
            print(f"  {status} {result.name}")
        
        if passed == total:
            print(f"\n{BOLD}{GREEN}All tests passed! Ready for deployment.{RESET}\n")
            return 0
        else:
            print(f"\n{BOLD}{RED}Some tests failed. Please fix issues before deploying.{RESET}\n")
            return 1

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test ConsultantOS locally before deployment"
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker build and run tests (faster, less comprehensive)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up test containers and exit"
    )
    
    args = parser.parse_args()
    
    tester = LocalDeploymentTester()
    
    if args.cleanup:
        tester.cleanup()
        return 0
    
    try:
        exit_code = tester.run_all_tests(skip_docker=args.skip_docker)
        return exit_code
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        tester.cleanup()
        return 1
    except Exception as e:
        print(f"\n{RED}Unexpected error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        tester.cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())



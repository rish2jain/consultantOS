"""
Load testing for ConsultantOS using Locust.

Run with:
    locust -f tests/load_test.py --host=http://localhost:8080
"""
from locust import HttpUser, task, between, events
import json
import random
import time


class ConsultantOSUser(HttpUser):
    """Simulated user for load testing."""

    # Wait between 1-5 seconds between tasks
    wait_time = between(1, 5)

    # Test data
    companies = [
        "Tesla", "Apple", "Microsoft", "Google", "Amazon",
        "Meta", "Netflix", "Nvidia", "AMD", "Intel"
    ]

    industries = [
        "Electric Vehicles", "Consumer Electronics", "Cloud Computing",
        "Search & Advertising", "E-commerce", "Social Media",
        "Streaming", "Semiconductors", "Technology"
    ]

    frameworks = [
        ["porter"],
        ["swot"],
        ["pestel"],
        ["porter", "swot"],
        ["porter", "swot", "pestel"],
        ["blue_ocean"],
        ["ansoff"]
    ]

    def on_start(self):
        """Called when a simulated user starts."""
        self.client.verify = False  # For local testing
        print(f"User {self.user_id} starting load test")

    @task(5)
    def analyze_company(self):
        """Main analysis endpoint (highest weight)."""
        company = random.choice(self.companies)
        industry = random.choice(self.industries)
        framework_set = random.choice(self.frameworks)

        payload = {
            "company": company,
            "industry": industry,
            "frameworks": framework_set,
            "depth": "standard"
        }

        with self.client.post(
            "/analyze",
            json=payload,
            catch_response=True,
            name="/analyze [standard]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "completed":
                    response.success()
                else:
                    response.failure(f"Analysis failed: {data.get('status')}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(3)
    def chat_query(self):
        """Conversational chat endpoint."""
        queries = [
            "What is competitive intelligence?",
            "Explain Porter's Five Forces",
            "How do I analyze market trends?",
            "What are the key metrics for financial analysis?",
            "Compare SWOT vs PESTEL analysis"
        ]

        query = random.choice(queries)

        with self.client.post(
            "/conversational/chat",
            json={"query": query},
            catch_response=True,
            name="/conversational/chat"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("response"):
                    response.success()
                else:
                    response.failure("Empty response")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def get_forecast(self):
        """Forecasting endpoint."""
        company = random.choice(self.companies)
        periods = random.choice([7, 14, 30])

        with self.client.get(
            f"/forecasting/generate?company={company}&periods={periods}",
            catch_response=True,
            name="/forecasting/generate"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("forecasts"):
                    response.success()
                else:
                    response.failure("No forecast data")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def health_check(self):
        """Health check endpoint (lightweight)."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def metrics_endpoint(self):
        """Prometheus metrics endpoint."""
        with self.client.get(
            "/metrics",
            catch_response=True,
            name="/metrics"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


class BurstUser(HttpUser):
    """User that simulates burst traffic patterns."""

    wait_time = between(0.1, 0.5)  # Very short wait times

    @task
    def burst_analyze(self):
        """Rapid-fire analysis requests."""
        payload = {
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "frameworks": ["porter"],
            "depth": "quick"
        }

        self.client.post("/analyze", json=payload, name="/analyze [burst]")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("=" * 60)
    print("ConsultantOS Load Test Starting")
    print("=" * 60)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    print("=" * 60)
    print("ConsultantOS Load Test Complete")
    print("=" * 60)

    # Print summary statistics
    stats = environment.stats
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Failures: {stats.total.num_failures}")
    print(f"Median Response Time: {stats.total.median_response_time}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"99th Percentile: {stats.total.get_response_time_percentile(0.99)}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print("=" * 60)

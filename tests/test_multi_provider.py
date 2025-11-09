"""
Tests for multi-provider LLM system.

Tests cover:
- Individual provider functionality
- Provider manager fallback mechanisms
- Routing strategies (cost, capability, load_balance)
- Cost tracking
- Health monitoring
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from consultantos.llm.provider_interface import LLMProvider
from consultantos.llm.gemini_provider import GeminiProvider
from consultantos.llm.openai_provider import OpenAIProvider
from consultantos.llm.anthropic_provider import AnthropicProvider
from consultantos.llm.provider_manager import ProviderManager, ProviderHealth
from consultantos.llm.cost_tracker import LLMCostTracker


class TestResponse(BaseModel):
    """Test response model."""
    company: str
    analysis: str


class MockProvider(LLMProvider):
    """Mock provider for testing."""

    def __init__(self, api_key: str, should_fail: bool = False):
        super().__init__(api_key)
        self.should_fail = should_fail
        self.generation_count = 0

    def get_default_model(self) -> str:
        return "mock-model"

    async def generate(
        self,
        prompt: str,
        response_model,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ):
        self.generation_count += 1
        if self.should_fail:
            raise Exception("Mock provider failure")

        # Mock successful response
        self._track_usage(100)  # Track 100 tokens
        return response_model(
            company="Tesla",
            analysis="Mock analysis"
        )

    def get_cost_per_token(self) -> float:
        return 0.001

    def get_rate_limits(self):
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 10000,
            "requests_per_day": 1000
        }


@pytest.fixture
def mock_gemini_provider():
    """Create mock Gemini provider."""
    return MockProvider("test-gemini-key")


@pytest.fixture
def mock_openai_provider():
    """Create mock OpenAI provider."""
    provider = MockProvider("test-openai-key")
    provider._provider_name = "openai"
    return provider


@pytest.fixture
def mock_anthropic_provider():
    """Create mock Anthropic provider."""
    provider = MockProvider("test-anthropic-key")
    provider._provider_name = "anthropic"
    return provider


@pytest.fixture
def provider_manager():
    """Create provider manager with mock providers."""
    manager = ProviderManager(
        gemini_api_key="test-gemini-key",
        primary_provider="gemini",
        enable_fallback=True,
        routing_strategy="fallback"
    )

    # Replace with mock providers and initialize health
    from consultantos.llm.provider_manager import ProviderHealth

    manager.providers["gemini"] = MockProvider("test-gemini-key")
    manager.providers["openai"] = MockProvider("test-openai-key")
    manager.providers["anthropic"] = MockProvider("test-anthropic-key")

    manager.health["gemini"] = ProviderHealth("gemini")
    manager.health["openai"] = ProviderHealth("openai")
    manager.health["anthropic"] = ProviderHealth("anthropic")

    return manager


class TestProviderHealth:
    """Test ProviderHealth tracking."""

    def test_initial_health(self):
        """Test initial health state."""
        health = ProviderHealth("test-provider")

        assert health.is_healthy is True
        assert health.total_requests == 0
        assert health.failed_requests == 0
        assert health.consecutive_failures == 0

    def test_record_success(self):
        """Test recording successful requests."""
        health = ProviderHealth("test-provider")

        health.record_success()

        assert health.total_requests == 1
        assert health.failed_requests == 0
        assert health.consecutive_failures == 0
        assert health.is_healthy is True

    def test_record_failure(self):
        """Test recording failed requests."""
        health = ProviderHealth("test-provider")

        health.record_failure()

        assert health.total_requests == 1
        assert health.failed_requests == 1
        assert health.consecutive_failures == 1
        assert health.is_healthy is True  # Not unhealthy yet

    def test_unhealthy_after_consecutive_failures(self):
        """Test provider becomes unhealthy after 3 consecutive failures."""
        health = ProviderHealth("test-provider")

        for _ in range(3):
            health.record_failure()

        assert health.consecutive_failures == 3
        assert health.is_healthy is False

    def test_failure_rate(self):
        """Test failure rate calculation."""
        health = ProviderHealth("test-provider")

        health.record_success()
        health.record_success()
        health.record_failure()

        assert health.get_failure_rate() == pytest.approx(1/3)


@pytest.mark.asyncio
class TestProviderManager:
    """Test ProviderManager functionality."""

    async def test_generate_with_fallback_success(self, provider_manager):
        """Test successful generation with primary provider."""
        result = await provider_manager.generate_with_fallback(
            "Test prompt",
            TestResponse
        )

        assert result.company == "Tesla"
        assert result.analysis == "Mock analysis"

        # Primary provider should have been used
        assert provider_manager.providers["gemini"].generation_count == 1

    async def test_generate_with_fallback_failure(self, provider_manager):
        """Test fallback when primary provider fails."""
        # Make primary provider fail
        provider_manager.providers["gemini"].should_fail = True

        result = await provider_manager.generate_with_fallback(
            "Test prompt",
            TestResponse
        )

        assert result.company == "Tesla"

        # Primary should have failed, fallback should have succeeded
        assert provider_manager.providers["gemini"].generation_count == 1
        assert provider_manager.providers["openai"].generation_count == 1

    async def test_all_providers_fail(self, provider_manager):
        """Test exception when all providers fail."""
        # Make all providers fail
        for provider in provider_manager.providers.values():
            provider.should_fail = True

        with pytest.raises(Exception, match="All LLM providers failed"):
            await provider_manager.generate_with_fallback(
                "Test prompt",
                TestResponse
            )

    async def test_route_by_cost(self, provider_manager):
        """Test cost-based routing."""
        # Set different costs for providers
        provider_manager.providers["gemini"].get_cost_per_token = lambda: 0.001
        provider_manager.providers["openai"].get_cost_per_token = lambda: 0.01
        provider_manager.providers["anthropic"].get_cost_per_token = lambda: 0.05

        result = await provider_manager.route_by_cost(
            "Test prompt",
            TestResponse
        )

        assert result.company == "Tesla"

        # Cheapest provider (gemini) should have been used
        assert provider_manager.providers["gemini"].generation_count == 1
        assert provider_manager.providers["openai"].generation_count == 0

    async def test_route_by_capability(self, provider_manager):
        """Test capability-based routing."""
        result = await provider_manager.route_by_capability(
            "analytical",
            "Test prompt",
            TestResponse
        )

        assert result.company == "Tesla"

        # OpenAI should be used for analytical tasks
        assert provider_manager.providers["openai"].generation_count == 1

    async def test_route_by_load_balance(self, provider_manager):
        """Test load balancing."""
        # Make multiple requests
        for _ in range(3):
            await provider_manager.route_by_load_balance(
                "Test prompt",
                TestResponse
            )

        # Requests should be distributed
        total_requests = sum(
            p.generation_count
            for p in provider_manager.providers.values()
        )
        assert total_requests == 3

    async def test_health_tracking(self, provider_manager):
        """Test health tracking during failures."""
        # Make primary fail
        provider_manager.providers["gemini"].should_fail = True

        # Generate should fallback
        await provider_manager.generate_with_fallback(
            "Test prompt",
            TestResponse
        )

        # Check health was recorded
        gemini_health = provider_manager.health["gemini"]
        assert gemini_health.failed_requests == 1

        openai_health = provider_manager.health["openai"]
        assert openai_health.total_requests == 1
        assert openai_health.failed_requests == 0

    def test_get_provider_stats(self, provider_manager):
        """Test getting provider statistics."""
        stats = provider_manager.get_provider_stats()

        assert "gemini" in stats
        assert "openai" in stats
        assert "anthropic" in stats

        for provider_name, provider_stats in stats.items():
            assert "is_healthy" in provider_stats
            assert "total_requests" in provider_stats
            assert "tokens_used" in provider_stats
            assert "estimated_cost" in provider_stats


@pytest.mark.asyncio
class TestCostTracker:
    """Test LLM cost tracking."""

    @pytest.fixture
    def cost_tracker(self):
        """Create fresh cost tracker."""
        return LLMCostTracker()

    async def test_track_usage(self, cost_tracker):
        """Test tracking LLM usage."""
        await cost_tracker.track_usage(
            provider="gemini",
            model="gemini-1.5-pro",
            tokens_used=1000,
            cost_per_1k_tokens=0.001,
            user_id="test-user",
            analysis_id="test-analysis"
        )

        assert len(cost_tracker.usage_records) == 1
        record = cost_tracker.usage_records[0]

        assert record.provider == "gemini"
        assert record.tokens_used == 1000
        assert record.cost_usd == pytest.approx(0.001)

    async def test_daily_cost(self, cost_tracker):
        """Test calculating daily cost."""
        await cost_tracker.track_usage(
            provider="gemini",
            model="gemini-1.5-pro",
            tokens_used=1000,
            cost_per_1k_tokens=0.001
        )

        await cost_tracker.track_usage(
            provider="openai",
            model="gpt-4",
            tokens_used=500,
            cost_per_1k_tokens=0.01
        )

        daily_cost = await cost_tracker.get_daily_cost()
        assert daily_cost == pytest.approx(0.006)

    async def test_cost_by_provider(self, cost_tracker):
        """Test cost breakdown by provider."""
        await cost_tracker.track_usage(
            provider="gemini",
            model="gemini-1.5-pro",
            tokens_used=1000,
            cost_per_1k_tokens=0.001
        )

        await cost_tracker.track_usage(
            provider="openai",
            model="gpt-4",
            tokens_used=500,
            cost_per_1k_tokens=0.01
        )

        by_provider = await cost_tracker.get_cost_by_provider()

        assert by_provider["gemini"] == pytest.approx(0.001)
        assert by_provider["openai"] == pytest.approx(0.005)

    async def test_budget_alert(self, cost_tracker, caplog):
        """Test budget alert when limit exceeded."""
        cost_tracker.set_daily_budget(0.01)

        # Exceed budget
        await cost_tracker.track_usage(
            provider="gemini",
            model="gemini-1.5-pro",
            tokens_used=20000,  # $0.02
            cost_per_1k_tokens=0.001
        )

        # Check for warning log
        assert any("budget exceeded" in record.message.lower() for record in caplog.records)

    async def test_usage_stats(self, cost_tracker):
        """Test comprehensive usage statistics."""
        await cost_tracker.track_usage(
            provider="gemini",
            model="gemini-1.5-pro",
            tokens_used=1000,
            cost_per_1k_tokens=0.001,
            agent_name="research"
        )

        await cost_tracker.track_usage(
            provider="openai",
            model="gpt-4",
            tokens_used=500,
            cost_per_1k_tokens=0.01,
            agent_name="framework"
        )

        stats = await cost_tracker.get_usage_stats()

        assert stats["total_cost"] == pytest.approx(0.006)
        assert stats["total_tokens"] == 1500
        assert stats["total_requests"] == 2
        assert "gemini" in stats["by_provider"]
        assert "research" in stats["by_agent"]


@pytest.mark.asyncio
class TestProviderIntegration:
    """Integration tests for provider system."""

    async def test_end_to_end_generation(self, provider_manager):
        """Test end-to-end generation flow."""
        # Generate with primary
        result = await provider_manager.generate(
            "Analyze Tesla",
            TestResponse
        )

        assert result.company == "Tesla"

        # Check stats
        stats = provider_manager.get_provider_stats()
        assert stats["gemini"]["total_requests"] > 0

    async def test_automatic_failover(self, provider_manager):
        """Test automatic failover to backup provider."""
        # Fail primary
        provider_manager.providers["gemini"].should_fail = True

        # Should automatically failover
        result = await provider_manager.generate(
            "Analyze Tesla",
            TestResponse
        )

        assert result.company == "Tesla"

        # Check failover happened
        stats = provider_manager.get_provider_stats()
        assert stats["gemini"]["failed_requests"] > 0
        assert stats["openai"]["total_requests"] > 0

    async def test_cost_optimization_routing(self, provider_manager):
        """Test cost-optimized routing strategy."""
        provider_manager.routing_strategy = "cost"

        # Set different costs
        provider_manager.providers["gemini"].get_cost_per_token = lambda: 0.001
        provider_manager.providers["openai"].get_cost_per_token = lambda: 0.01

        # Should route to cheapest
        result = await provider_manager.generate(
            "Analyze Tesla",
            TestResponse
        )

        assert result.company == "Tesla"
        assert provider_manager.providers["gemini"].generation_count > 0

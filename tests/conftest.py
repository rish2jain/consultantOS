"""
Test configuration and fixtures for ConsultantOS
"""
import os
import pytest
import vcr as vcrpy
from pathlib import Path


# VCR Configuration
CASSETTES_DIR = Path(__file__).parent / "fixtures" / "vcr_cassettes"


def scrub_sensitive_data(response):
    """
    Filter sensitive data from VCR cassettes.

    Removes API keys, tokens, and other sensitive information
    from recorded HTTP interactions.
    """
    # Remove sensitive headers
    if 'headers' in response:
        sensitive_headers = [
            'Authorization',
            'X-API-Key',
            'Cookie',
            'Set-Cookie',
            'api-key',
            'apikey'
        ]
        for header in sensitive_headers:
            if header in response['headers']:
                response['headers'][header] = ['REDACTED']

    return response


@pytest.fixture(scope="module")
def vcr_config():
    """
    VCR configuration fixture used across all tests.

    Returns:
        dict: VCR configuration settings
    """
    return {
        "cassette_library_dir": str(CASSETTES_DIR),
        "record_mode": os.environ.get("VCR_RECORD_MODE", "once"),
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["Authorization", "X-API-Key", "Cookie"],
        "filter_post_data_parameters": ["api_key", "apikey", "key"],
        "before_record_response": scrub_sensitive_data,
        "decode_compressed_response": True,
        "serializer": "yaml",
        "record_on_exception": False,
    }


@pytest.fixture(scope="function")
def vcr_cassette_name(request):
    """
    Generate cassette name based on test class and method.

    Args:
        request: pytest request fixture

    Returns:
        str: Cassette filename (e.g., "TestResearchAgent.test_execution.yaml")
    """
    if request.cls:
        return f"{request.cls.__name__}.{request.function.__name__}"
    return request.function.__name__


@pytest.fixture(scope="function")
def vcr_instance(vcr_config, vcr_cassette_name):
    """
    Create a VCR instance configured for the current test.

    Args:
        vcr_config: VCR configuration dictionary
        vcr_cassette_name: Generated cassette filename

    Returns:
        VCR: Configured VCR instance
    """
    return vcrpy.VCR(**vcr_config)


@pytest.fixture(scope="function")
def vcr_cassette(vcr_instance, vcr_cassette_name):
    """
    Context manager for VCR cassette recording/playback.

    Usage in tests:
        async def test_something(vcr_cassette):
            with vcr_cassette:
                # API calls here will be recorded/replayed
                result = await agent.execute(...)

    Args:
        vcr_instance: Configured VCR instance
        vcr_cassette_name: Cassette filename

    Returns:
        cassette context manager
    """
    cassette_path = f"{vcr_cassette_name}.yaml"
    return vcr_instance.use_cassette(cassette_path)


# Helper function for manual cassette usage
def use_cassette(cassette_name, **kwargs):
    """
    Decorator for using VCR cassettes in tests.

    Usage:
        @use_cassette("my_test_cassette")
        async def test_something():
            # API calls recorded/replayed
            pass

    Args:
        cassette_name: Name of the cassette file (without .yaml)
        **kwargs: Additional VCR configuration overrides

    Returns:
        Decorator function
    """
    config = {
        "cassette_library_dir": str(CASSETTES_DIR),
        "record_mode": os.environ.get("VCR_RECORD_MODE", "once"),
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["Authorization", "X-API-Key", "Cookie"],
        "filter_post_data_parameters": ["api_key", "apikey", "key"],
        "before_record_response": scrub_sensitive_data,
        "decode_compressed_response": True,
        "serializer": "yaml",
        "record_on_exception": False,
    }
    config.update(kwargs)

    return vcrpy.use_cassette(
        str(CASSETTES_DIR / f"{cassette_name}.yaml"),
        **config
    )


# Test data fixtures for common scenarios
@pytest.fixture
def tesla_test_data():
    """Test data for Tesla analysis"""
    return {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "ticker": "TSLA"
    }


@pytest.fixture
def apple_test_data():
    """Test data for Apple analysis"""
    return {
        "company": "Apple",
        "industry": "Consumer Electronics",
        "ticker": "AAPL"
    }


@pytest.fixture
def microsoft_test_data():
    """Test data for Microsoft analysis"""
    return {
        "company": "Microsoft",
        "industry": "Software and Cloud Services",
        "ticker": "MSFT"
    }


# Environment setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment variables.

    Ensures required environment variables are set for testing.
    Uses dummy values when VCR cassettes are being used (no real API calls).
    """
    # Set dummy API keys if not present (VCR doesn't need real keys for playback)
    if "TAVILY_API_KEY" not in os.environ:
        os.environ["TAVILY_API_KEY"] = "test_tavily_key_for_vcr"

    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = "test_gemini_key_for_vcr"

    yield

    # Cleanup if needed (optional)
    pass


# ============================================================================
# FAKER FIXTURES FOR TEST DATA GENERATION
# ============================================================================

from faker import Faker
from tests.factories import ConsultantOSFactory


@pytest.fixture(scope="session")
def faker_seed() -> int:
    """
    Global seed for reproducible test data generation.

    In CI, uses PYTEST_FAKER_SEED environment variable.
    Locally, uses fixed seed for reproducibility during development.

    Returns:
        Seed value for Faker and random
    """
    return int(os.environ.get("PYTEST_FAKER_SEED", 12345))


@pytest.fixture(scope="session")
def faker_session(faker_seed: int) -> Faker:
    """
    Session-scoped Faker instance with deterministic seed.

    This fixture provides consistent data across all tests in a session.
    Use for session-level test data that should be identical across runs.

    Args:
        faker_seed: Seed value from faker_seed fixture

    Returns:
        Configured Faker instance
    """
    Faker.seed(faker_seed)
    fake = Faker("en_US")

    # Add custom providers
    from tests.factories import (
        BusinessFrameworkProvider,
        IndustryProvider,
        MonitoringProvider,
        FinancialDataProvider
    )
    fake.add_provider(BusinessFrameworkProvider)
    fake.add_provider(IndustryProvider)
    fake.add_provider(MonitoringProvider)
    fake.add_provider(FinancialDataProvider)

    return fake


@pytest.fixture
def faker(faker_seed: int) -> Faker:
    """
    Function-scoped Faker instance with deterministic seed.

    Each test gets a fresh Faker instance with the same seed,
    ensuring reproducibility while maintaining test isolation.

    Args:
        faker_seed: Seed value from faker_seed fixture

    Returns:
        Configured Faker instance
    """
    Faker.seed(faker_seed)
    fake = Faker("en_US")

    # Add custom providers
    from tests.factories import (
        BusinessFrameworkProvider,
        IndustryProvider,
        MonitoringProvider,
        FinancialDataProvider
    )
    fake.add_provider(BusinessFrameworkProvider)
    fake.add_provider(IndustryProvider)
    fake.add_provider(MonitoringProvider)
    fake.add_provider(FinancialDataProvider)

    return fake


@pytest.fixture(scope="session")
def factory_session(faker_seed: int) -> ConsultantOSFactory:
    """
    Session-scoped factory for consistent test data generation.

    Use for generating baseline test data that should be identical
    across all tests in a session.

    Args:
        faker_seed: Seed value from faker_seed fixture

    Returns:
        ConsultantOSFactory with session seed
    """
    return ConsultantOSFactory(seed=faker_seed)


@pytest.fixture
def factory(faker_seed: int) -> ConsultantOSFactory:
    """
    Function-scoped factory for test data generation.

    Each test gets a fresh factory instance with the same seed,
    ensuring reproducibility while maintaining test isolation.

    Args:
        faker_seed: Seed value from faker_seed fixture

    Returns:
        ConsultantOSFactory instance
    """
    return ConsultantOSFactory(seed=faker_seed)


@pytest.fixture
def unique_factory() -> ConsultantOSFactory:
    """
    Factory without seed for generating unique data in each test.

    Use when you need truly random data that differs between test runs.
    Useful for stress testing and exploring edge cases.

    Returns:
        ConsultantOSFactory without seed (non-deterministic)
    """
    return ConsultantOSFactory()


# Common test data fixtures
@pytest.fixture
def sample_analysis_request(factory: ConsultantOSFactory):
    """Generate a sample AnalysisRequest"""
    return factory.analysis_request()


@pytest.fixture
def sample_monitor(factory: ConsultantOSFactory):
    """Generate a sample Monitor"""
    return factory.monitor()


@pytest.fixture
def sample_alert(factory: ConsultantOSFactory):
    """Generate a sample Alert"""
    return factory.alert()


@pytest.fixture
def sample_user(factory: ConsultantOSFactory):
    """Generate a sample user"""
    return factory.user()


@pytest.fixture
def edge_case_companies(factory: ConsultantOSFactory):
    """Generate edge case company names for validation testing"""
    return {
        "min_length": factory.edge_case_company_name("min_length"),
        "max_length": factory.edge_case_company_name("max_length"),
        "special_chars": factory.edge_case_company_name("special_chars"),
        "unicode": factory.edge_case_company_name("unicode"),
        "whitespace": factory.edge_case_company_name("whitespace"),
        "empty": factory.edge_case_company_name("empty"),
        "too_short": factory.edge_case_company_name("too_short"),
        "too_long": factory.edge_case_company_name("too_long")
    }

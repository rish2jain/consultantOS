"""
Configuration management for ConsultantOS
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional import for Google Secret Manager
try:
    from google.cloud import secretmanager
    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    SECRET_MANAGER_AVAILABLE = False
    secretmanager = None


class Settings(BaseSettings):
    """Application settings"""

    # API Keys - Research Tools
    tavily_api_key: Optional[str] = None

    # API Keys - Financial Data
    finnhub_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None

    # API Keys - LLM Providers
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = "gemini-1.5-flash-002"

    # API Keys - Alerting
    slack_bot_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None

    # API Keys - Social Media
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None

    # Grok API via laozhang.ai
    laozhang_api_key: Optional[str] = None
    laozhang_model: str = "grok-4-fast-reasoning-latest"  # Fastest with reasoning: 1.94s. Options: grok-4-fast-non-reasoning-latest (1.80s), grok-4-fast (4.18s), grok-4-all (112s)

    # Reddit API Configuration
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "ConsultantOS:v1.0 (by /u/consultantos)"

    # API Keys - Billing
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # Google Cloud
    gcp_project_id: Optional[str] = None

    # Frontend Configuration
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"

    # Stripe Price IDs (configure these with actual Stripe Price IDs from dashboard)
    stripe_price_id_pro: str = "price_pro_monthly"
    stripe_price_id_enterprise: str = "price_enterprise_monthly"

    # Application
    environment: str = "development"
    log_level: str = "INFO"

    # Rate Limiting
    rate_limit_per_hour: int = 10

    # Caching
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_dir: str = ""  # Empty string means use default temp directory

    # Task Queue (Celery + Redis)
    redis_url: Optional[str] = None
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # Observability - Prometheus
    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 9090

    # Observability - Sentry
    sentry_dsn: Optional[str] = None
    sentry_environment: Optional[str] = None  # Will default to 'environment' if not set
    sentry_traces_sample_rate: Optional[float] = None  # Auto-set based on environment if not provided
    sentry_release: Optional[str] = None  # Git SHA recommended
    enable_sentry_profiling: bool = False
    sentry_profiles_sample_rate: float = 0.1

    # Operational
    health_check_timeout: int = 5
    graceful_shutdown_timeout: int = 30
    request_timeout: int = 300

    # Security
    session_secret: Optional[str] = None  # Secret key for session management

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_secret(secret_id: str, default_env_var: Optional[str] = None) -> str:
    """
    Retrieve secret from Google Secret Manager with fallback to environment variable.
    
    Args:
        secret_id: Secret name in Secret Manager
        default_env_var: Environment variable name as fallback
    
    Returns:
        Secret value as string
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Try Secret Manager first (if available)
    if SECRET_MANAGER_AVAILABLE:
        try:
            project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
            if project_id and secretmanager:
                client = secretmanager.SecretManagerServiceClient()
                secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                response = client.access_secret_version(request={"name": secret_name})
                secret_value = response.payload.data.decode('UTF-8')
                logger.info(f"Retrieved secret {secret_id} from Secret Manager")
                return secret_value
        except Exception as e:
            logger.warning(f"Failed to retrieve secret {secret_id} from Secret Manager: {e}")
    
    # Fallback to environment variable
    if default_env_var:
        env_value = os.getenv(default_env_var)
        if env_value:
            logger.info(f"Using environment variable {default_env_var} as fallback")
            return env_value
    
    # Final fallback: direct environment variable with secret_id name
    env_value = os.getenv(secret_id.upper().replace("-", "_"))
    if env_value:
        logger.info(f"Using environment variable {secret_id.upper().replace('-', '_')} as fallback")
        return env_value
    
    raise ValueError(f"Secret {secret_id} not found in Secret Manager or environment variables")


# Initialize settings
settings = Settings()

# Load secrets if not already set
import logging
_config_logger = logging.getLogger(__name__)

# Required key: gemini_api_key
if not settings.gemini_api_key:
    try:
        settings.gemini_api_key = get_secret("gemini-api-key", "GEMINI_API_KEY")
        if not settings.gemini_api_key:
            if settings.environment == "development" or settings.environment == "test":
                _config_logger.warning("GEMINI_API_KEY is not configured. Analysis features will be unavailable. Set GEMINI_API_KEY for full functionality.")
                settings.gemini_api_key = "test-key-placeholder"  # Allow app to start in dev/test
            else:
                raise RuntimeError("GEMINI_API_KEY is required but not configured. Set it via environment variable or Secret Manager.")
    except ValueError as e:
        if settings.environment == "development" or settings.environment == "test":
            _config_logger.warning(f"Failed to load required secret 'gemini-api-key' (GEMINI_API_KEY): {e}. Using placeholder for testing.")
            settings.gemini_api_key = "test-key-placeholder"  # Allow app to start in dev/test
        else:
            raise RuntimeError(f"Failed to load required secret 'gemini-api-key' (GEMINI_API_KEY): {e}. This key is required for the application to function.")

# Optional key: tavily_api_key
if not settings.tavily_api_key:
    try:
        settings.tavily_api_key = get_secret("tavily-api-key", "TAVILY_API_KEY")
        if not settings.tavily_api_key:
            _config_logger.warning("TAVILY_API_KEY is not configured. Some features may be unavailable.")
    except ValueError as e:
        _config_logger.warning(f"TAVILY_API_KEY not found in Secret Manager or environment variables: {e}. Some features may be unavailable.")

# Optional key: finnhub_api_key
if not settings.finnhub_api_key:
    try:
        settings.finnhub_api_key = get_secret("finnhub-api-key", "FINNHUB_API_KEY")
        if not settings.finnhub_api_key:
            _config_logger.warning("FINNHUB_API_KEY is not configured. Financial data will use yfinance only.")
    except ValueError as e:
        _config_logger.warning(f"FINNHUB_API_KEY not found in Secret Manager or environment variables: {e}. Financial data will use yfinance only.")

# Session secret (required for security)
if not settings.session_secret:
    try:
        settings.session_secret = get_secret("session-secret", "SESSION_SECRET")
    except ValueError:
        # Generate a random session secret if not configured (development only)
        if settings.environment == "development" or settings.environment == "test":
            import secrets
            settings.session_secret = secrets.token_urlsafe(32)
            _config_logger.warning("SESSION_SECRET not configured. Generated temporary session secret for development. Set SESSION_SECRET for production.")
        else:
            raise RuntimeError("SESSION_SECRET is required for production. Set it via environment variable or Secret Manager.")
# Optional key: slack_bot_token
if not settings.slack_bot_token:
    try:
        settings.slack_bot_token = get_secret("slack-bot-token", "SLACK_BOT_TOKEN")
        if settings.slack_bot_token:
            _config_logger.info("Slack bot token loaded successfully")
    except ValueError:
        _config_logger.debug("SLACK_BOT_TOKEN not configured. Slack bot features will be unavailable.")

# Optional key: slack_webhook_url  
if not settings.slack_webhook_url:
    try:
        settings.slack_webhook_url = get_secret("slack-webhook-url", "SLACK_WEBHOOK_URL")
        if settings.slack_webhook_url:
            _config_logger.info("Slack webhook URL loaded successfully")
    except ValueError:
        _config_logger.debug("SLACK_WEBHOOK_URL not configured. Slack webhook features will be unavailable.")

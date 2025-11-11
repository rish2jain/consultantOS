"""
Configuration management for ConsultantOS
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
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

    # API Keys - LLM Providers
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = "gemini-1.5-flash-002"

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

    # Observability
    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 9090

    # Operational
    health_check_timeout: int = 5
    graceful_shutdown_timeout: int = 30
    request_timeout: int = 300

    # Security
    session_secret: Optional[str] = None  # Secret key for session management

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env that aren't in the model
    )


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
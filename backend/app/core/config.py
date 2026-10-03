"""Environment and Application Configuration."""
from functools import lru_cache
from decimal import Decimal
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable loading."""

    # Project Information
    PROJECT_NAME: str = "PayAgent-Sentinel"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Multi-LLM Credentials
    GEMINI_API_KEY: str = ""
    NEBIUS_API_KEY: str = ""
    NEBIUS_BASE_URL: str = "https://api.tokenfactory.nebius.com/v1"

    # PayPal Configuration
    PAYPAL_ENV: Literal["sandbox", "live"] = "sandbox"
    PAYPAL_CLIENT_ID: str = "mock_client_id"
    PAYPAL_CLIENT_SECRET: str = "mock_client_secret"
    PAYPAL_WEBHOOK_ID: str = ""

    @property
    def paypal_base_url(self) -> str:
        """Return PayPal API base URL based on active environment."""
        if self.PAYPAL_ENV == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    # Sentinel Policy Engine Limits ($100 hard cap per procurement)
    SENTINEL_POLICY_HMAC_SECRET: str = "dev-sentinel-hmac-secret-change-in-production-32bytes"
    SENTINEL_MAX_SINGLE_TRANSACTION: Decimal = Decimal("100.00")
    SENTINEL_MAX_DAILY_VELOCITY: Decimal = Decimal("1000.00")
    SENTINEL_EMERGENCY_KILLSWITCH: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()

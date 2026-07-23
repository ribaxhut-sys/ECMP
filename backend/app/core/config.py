"""Application configuration via environment variables (Pydantic Settings)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_JWT_SECRETS = frozenset(
    {
        "",
        "change-me-in-production",
        "changeme",
        "secret",
        "jwt-secret",
        "dev",
        "test",
    }
)


class Settings(BaseSettings):
    """Runtime configuration for the ECMP foundation API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ECMP"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_prefix: str = ""
    allowed_origins: str = "http://localhost:3000"
    allowed_hosts: str = "localhost,127.0.0.1"

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "ecmp"
    postgres_password: str = "ecmp"
    postgres_db: str = "ecmp"
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    # JWT / session
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    refresh_cookie_name: str = "ecmp_refresh_token"
    refresh_cookie_path: str = "/api/v1/auth"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def trusted_hosts(self) -> list[str]:
        hosts = [h.strip() for h in self.allowed_hosts.split(",") if h.strip()]
        return hosts or ["localhost", "127.0.0.1"]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def docs_enabled(self) -> bool:
        return self.is_development

    @property
    def refresh_cookie_secure(self) -> bool:
        """Secure flag required in non-development environments."""
        return not self.is_development

    @property
    def access_token_expire_seconds(self) -> int:
        return self.jwt_access_token_expire_minutes * 60

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.jwt_refresh_token_expire_days * 24 * 60 * 60


def validate_runtime_config(settings: Settings | None = None) -> None:
    """Fail fast on unsafe non-development configuration (RC1 secret guard)."""
    cfg = settings or get_settings()
    if cfg.is_development:
        return

    secret = (cfg.jwt_secret_key or "").strip()
    if secret.lower() in _INSECURE_JWT_SECRETS or len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be a strong secret (>=32 chars) outside development"
        )

    if not cfg.cors_origins:
        raise RuntimeError("ALLOWED_ORIGINS must be set outside development")

    if any(origin == "*" for origin in cfg.cors_origins):
        raise RuntimeError("Wildcard ALLOWED_ORIGINS is forbidden outside development")

    if cfg.debug:
        raise RuntimeError("DEBUG must be false outside development")


@lru_cache
def get_settings() -> Settings:
    return Settings()

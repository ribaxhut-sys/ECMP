"""Application configuration via environment variables (Pydantic Settings)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

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

# Shared weak/default credential denylist (R2-01).
_INSECURE_PASSWORDS = frozenset(
    {
        "",
        "ecmp",
        "admin",
        "password",
        "postgres",
        "changeme",
        "change-me",
        "secret",
        "root",
        "test",
        "dev",
    }
)

_ALLOWED_JWT_ALGORITHMS = frozenset({"HS256"})
_ALLOWED_EMAIL_PROVIDERS = frozenset({"logging", "noop"})
_LOCAL_HOST_MARKERS = ("localhost", "127.0.0.1", "0.0.0.0", "::1")


@dataclass(frozen=True)
class ConfigIssue:
    """Single configuration problem with an actionable fix."""

    variable: str
    problem: str
    suggested_fix: str


class ConfigValidationError(RuntimeError):
    """Fail-fast startup error listing every configuration issue found."""

    def __init__(self, issues: list[ConfigIssue]) -> None:
        if not issues:
            raise ValueError("ConfigValidationError requires at least one issue")
        self.issues = list(issues)
        lines = ["Configuration validation failed:"]
        for index, issue in enumerate(self.issues, start=1):
            lines.append(f"  {index}. Variable: {issue.variable}")
            lines.append(f"     Problem: {issue.problem}")
            lines.append(f"     Suggested fix: {issue.suggested_fix}")
        super().__init__("\n".join(lines))


class Settings(BaseSettings):
    """Runtime configuration for the ECMP foundation API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "ECMP"
    app_version: str = "1.0.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # R6-01 release provenance (baked at Docker build via ARG→ENV; not hardcoded).
    git_commit: str = Field(default="unknown", alias="GIT_COMMIT")
    git_branch: str = Field(default="unknown", alias="GIT_BRANCH")
    build_time: str = Field(default="unknown", alias="BUILD_TIME")
    git_tree_state: str = Field(default="unknown", alias="GIT_TREE_STATE")

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

    # Optional: validated outside development when present (compose / tools profile).
    pgadmin_default_password: str | None = None

    # Login brute-force protection (R2-03) — in-memory, no Redis.
    login_rate_limit_enabled: bool = True
    login_max_failed_attempts: int = 5
    login_lockout_seconds: int = 300

    # Password policy / reset (Identity & Password Management)
    password_min_length: int = Field(default=8, alias="PASSWORD_MIN_LENGTH", ge=8, le=72)
    password_reset_token_expire_minutes: int = Field(
        default=15,
        alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
        ge=1,
        le=1440,
    )
    password_reset_frontend_base_url: str = Field(
        default="http://localhost:3000",
        alias="PASSWORD_RESET_FRONTEND_BASE_URL",
    )
    email_provider: str = Field(default="logging", alias="EMAIL_PROVIDER")

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
        return self.environment in {"development", "test"}

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def docs_enabled(self) -> bool:
        return self.is_development

    @property
    def refresh_cookie_secure(self) -> bool:
        """Secure flag required in non-development environments."""
        return not self.is_development

    @property
    def refresh_cookie_samesite(self) -> Literal["lax", "strict", "none"]:
        """SameSite=Lax keeps CSRF surface low for same-site FE/BE deployments."""
        return "lax"

    @property
    def access_token_expire_seconds(self) -> int:
        return self.jwt_access_token_expire_minutes * 60

    @property
    def refresh_token_expire_seconds(self) -> int:
        return self.jwt_refresh_token_expire_days * 24 * 60 * 60


def _is_weak_password(value: str, *, min_length: int = 8) -> bool:
    cleaned = (value or "").strip()
    return cleaned.lower() in _INSECURE_PASSWORDS or len(cleaned) < min_length


def _contains_local_host(value: str) -> bool:
    lowered = (value or "").strip().lower()
    return any(marker in lowered for marker in _LOCAL_HOST_MARKERS)


def _origin_is_valid(origin: str) -> bool:
    parsed = urlparse(origin)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def collect_runtime_config_issues(settings: Settings) -> list[ConfigIssue]:
    """Return all configuration issues without raising (R6-03 inventory helper)."""
    issues: list[ConfigIssue] = []

    # --- Always validate structural JWT / DB completeness ---
    if not (settings.jwt_secret_key or "").strip():
        issues.append(
            ConfigIssue(
                variable="JWT_SECRET_KEY",
                problem="Secret is missing or empty.",
                suggested_fix="Set JWT_SECRET_KEY to a cryptographically random string of at least 32 characters.",
            )
        )

    algorithm = (settings.jwt_algorithm or "").strip().upper()
    if algorithm not in _ALLOWED_JWT_ALGORITHMS:
        issues.append(
            ConfigIssue(
                variable="JWT_ALGORITHM",
                problem=f"Unsupported algorithm '{settings.jwt_algorithm}'.",
                suggested_fix="Set JWT_ALGORITHM=HS256 (only algorithm supported by the foundation stack).",
            )
        )

    if settings.jwt_access_token_expire_minutes < 1:
        issues.append(
            ConfigIssue(
                variable="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                problem="Access token lifetime must be >= 1 minute.",
                suggested_fix="Set JWT_ACCESS_TOKEN_EXPIRE_MINUTES to a positive integer (recommended: 15).",
            )
        )

    if settings.jwt_refresh_token_expire_days < 1:
        issues.append(
            ConfigIssue(
                variable="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
                problem="Refresh token lifetime must be >= 1 day.",
                suggested_fix="Set JWT_REFRESH_TOKEN_EXPIRE_DAYS to a positive integer (recommended: 7).",
            )
        )

    email_provider = (settings.email_provider or "").strip().lower()
    if email_provider not in _ALLOWED_EMAIL_PROVIDERS:
        issues.append(
            ConfigIssue(
                variable="EMAIL_PROVIDER",
                problem=f"Unknown provider '{settings.email_provider}'.",
                suggested_fix="Use EMAIL_PROVIDER=logging (development only) or EMAIL_PROVIDER=noop until SMTP is wired (R6-04+).",
            )
        )

    if settings.database_url_override:
        db_url = settings.database_url_override.strip()
        if not db_url.startswith(("postgresql", "postgres")):
            issues.append(
                ConfigIssue(
                    variable="DATABASE_URL",
                    problem="Override URL is not a PostgreSQL connection string.",
                    suggested_fix="Use postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB or unset DATABASE_URL and use POSTGRES_* vars.",
                )
            )
    else:
        if not (settings.postgres_host or "").strip():
            issues.append(
                ConfigIssue(
                    variable="POSTGRES_HOST",
                    problem="Database host is missing.",
                    suggested_fix="Set POSTGRES_HOST to the Postgres hostname (compose service name is 'postgres').",
                )
            )
        if not (settings.postgres_user or "").strip():
            issues.append(
                ConfigIssue(
                    variable="POSTGRES_USER",
                    problem="Database user is missing.",
                    suggested_fix="Set POSTGRES_USER to a non-empty role name.",
                )
            )
        if not (settings.postgres_db or "").strip():
            issues.append(
                ConfigIssue(
                    variable="POSTGRES_DB",
                    problem="Database name is missing.",
                    suggested_fix="Set POSTGRES_DB to the target database name.",
                )
            )
        if not (settings.postgres_password or "").strip():
            issues.append(
                ConfigIssue(
                    variable="POSTGRES_PASSWORD",
                    problem="Database password is missing.",
                    suggested_fix="Set POSTGRES_PASSWORD to a strong secret (compose refuses empty via ${POSTGRES_PASSWORD:?...}).",
                )
            )

    # Storage is System Settings (DB), not env — no REDIS_* in foundation stack.
    # Documented in R6-03; no env gate required here.

    if settings.is_development:
        return issues

    # --- Staging / production hard gates ---
    secret = (settings.jwt_secret_key or "").strip()
    if secret.lower() in _INSECURE_JWT_SECRETS or len(secret) < 32:
        issues.append(
            ConfigIssue(
                variable="JWT_SECRET_KEY",
                problem="Secret is weak, placeholder, or shorter than 32 characters.",
                suggested_fix="Generate a strong secret (>=32 chars), e.g. `openssl rand -hex 32`, and inject via vault/.env (never commit).",
            )
        )

    if _is_weak_password(settings.postgres_password):
        issues.append(
            ConfigIssue(
                variable="POSTGRES_PASSWORD",
                problem="Password is weak or matches a known default denylist entry.",
                suggested_fix="Set POSTGRES_PASSWORD to a unique secret (>=8 chars) that is not a documented default (ecmp/admin/password/...).",
            )
        )

    if settings.pgadmin_default_password is not None and _is_weak_password(
        settings.pgadmin_default_password
    ):
        issues.append(
            ConfigIssue(
                variable="PGADMIN_DEFAULT_PASSWORD",
                problem="pgAdmin password is weak or matches a known default.",
                suggested_fix="Set a strong PGADMIN_DEFAULT_PASSWORD or omit pgAdmin (tools profile) outside development.",
            )
        )

    if not settings.cors_origins:
        issues.append(
            ConfigIssue(
                variable="ALLOWED_ORIGINS",
                problem="No browser origins configured (fail-closed CORS).",
                suggested_fix="Set ALLOWED_ORIGINS to the exact frontend origin(s), comma-separated (no wildcard).",
            )
        )
    else:
        if any(origin == "*" for origin in settings.cors_origins):
            issues.append(
                ConfigIssue(
                    variable="ALLOWED_ORIGINS",
                    problem="Wildcard origin '*' is forbidden outside development.",
                    suggested_fix="Replace '*' with explicit https origins, e.g. https://app.example.com.",
                )
            )
        for origin in settings.cors_origins:
            if not _origin_is_valid(origin):
                issues.append(
                    ConfigIssue(
                        variable="ALLOWED_ORIGINS",
                        problem=f"Origin '{origin}' is not a valid absolute http(s) URL.",
                        suggested_fix="Use full origins including scheme, e.g. https://app.example.com (no path).",
                    )
                )
            elif _contains_local_host(origin):
                issues.append(
                    ConfigIssue(
                        variable="ALLOWED_ORIGINS",
                        problem=f"Origin '{origin}' uses a localhost/loopback host.",
                        suggested_fix="Point ALLOWED_ORIGINS at the public/staging frontend origin (no localhost/127.0.0.1).",
                    )
                )
            elif settings.is_production and urlparse(origin).scheme != "https":
                issues.append(
                    ConfigIssue(
                        variable="ALLOWED_ORIGINS",
                        problem=f"Origin '{origin}' is not HTTPS (required in production).",
                        suggested_fix="Terminate TLS at the reverse proxy and set https:// origins only.",
                    )
                )

    if settings.debug:
        issues.append(
            ConfigIssue(
                variable="DEBUG",
                problem="DEBUG=true is not allowed outside development/test.",
                suggested_fix="Set DEBUG=false (or unset) for staging and production.",
            )
        )

    reset_base = (settings.password_reset_frontend_base_url or "").strip()
    if not reset_base:
        issues.append(
            ConfigIssue(
                variable="PASSWORD_RESET_FRONTEND_BASE_URL",
                problem="Password-reset frontend base URL is missing.",
                suggested_fix="Set PASSWORD_RESET_FRONTEND_BASE_URL to the public frontend origin (no trailing path required).",
            )
        )
    else:
        if not _origin_is_valid(reset_base):
            issues.append(
                ConfigIssue(
                    variable="PASSWORD_RESET_FRONTEND_BASE_URL",
                    problem=f"Value '{reset_base}' is not a valid absolute http(s) URL.",
                    suggested_fix="Use a full origin such as https://app.example.com.",
                )
            )
        if _contains_local_host(reset_base):
            issues.append(
                ConfigIssue(
                    variable="PASSWORD_RESET_FRONTEND_BASE_URL",
                    problem="URL uses localhost/loopback (invalid outside development).",
                    suggested_fix="Set PASSWORD_RESET_FRONTEND_BASE_URL to the real public frontend origin.",
                )
            )
        elif settings.is_production and urlparse(reset_base).scheme != "https":
            issues.append(
                ConfigIssue(
                    variable="PASSWORD_RESET_FRONTEND_BASE_URL",
                    problem="Production password-reset links must use HTTPS.",
                    suggested_fix="Set PASSWORD_RESET_FRONTEND_BASE_URL to an https:// origin behind TLS.",
                )
            )

    if email_provider == "logging":
        issues.append(
            ConfigIssue(
                variable="EMAIL_PROVIDER",
                problem="logging provider is development-only.",
                suggested_fix="Set EMAIL_PROVIDER=noop until a real SMTP/provider is approved (SMTP is out of scope for R6-03).",
            )
        )

    # Frontend/backend origin consistency hint (non-blocking shape already covered).
    if settings.cors_origins and reset_base:
        normalized_reset = reset_base.rstrip("/")
        if normalized_reset not in {o.rstrip("/") for o in settings.cors_origins}:
            issues.append(
                ConfigIssue(
                    variable="PASSWORD_RESET_FRONTEND_BASE_URL",
                    problem=(
                        "Reset base URL is not present in ALLOWED_ORIGINS "
                        f"('{normalized_reset}' vs {settings.cors_origins})."
                    ),
                    suggested_fix="Align PASSWORD_RESET_FRONTEND_BASE_URL with one of the ALLOWED_ORIGINS values.",
                )
            )

    return issues


def validate_runtime_config(settings: Settings | None = None) -> None:
    """Fail fast on unsafe or incomplete configuration (R2 / R6-03)."""
    cfg = settings or get_settings()
    issues = collect_runtime_config_issues(cfg)
    if issues:
        raise ConfigValidationError(issues)


@lru_cache
def get_settings() -> Settings:
    return Settings()

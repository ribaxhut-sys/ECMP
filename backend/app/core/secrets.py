"""Secrets inventory and redaction (TASK-PLATFORM-SECMIG-P5-002).

Approved configuration source for backend secrets is environment variables
(and git-ignored ``.env`` via Pydantic Settings) — DEP-001 §2.

This module must never log or return secret values.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable
from urllib.parse import urlsplit, urlunsplit

if TYPE_CHECKING:
    from app.core.config import Settings

REDACTED = "***REDACTED***"

# ---------------------------------------------------------------------------
# Inventory — every backend secret / credential material
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SecretInventoryItem:
    """One secret consumed by the foundation backend."""

    env_var: str
    settings_field: str
    required: bool
    notes: str


SECRET_INVENTORY: tuple[SecretInventoryItem, ...] = (
    SecretInventoryItem(
        env_var="JWT_SECRET_KEY",
        settings_field="jwt_secret_key",
        required=True,
        notes="HS256 signing key for lab/dev access tokens; mandatory at startup.",
    ),
    SecretInventoryItem(
        env_var="POSTGRES_PASSWORD",
        settings_field="postgres_password",
        required=True,
        notes=(
            "DB password when DATABASE_URL is unset; required unless "
            "DATABASE_URL supplies credentials."
        ),
    ),
    SecretInventoryItem(
        env_var="DATABASE_URL",
        settings_field="database_url_override",
        required=False,
        notes="Optional full DSN; may embed password — treat as secret.",
    ),
    SecretInventoryItem(
        env_var="PGADMIN_DEFAULT_PASSWORD",
        settings_field="pgadmin_default_password",
        required=False,
        notes="Optional compose tools-profile password; validated when set.",
    ),
)

SECRET_ENV_VARS: frozenset[str] = frozenset(item.env_var for item in SECRET_INVENTORY)
SECRET_SETTINGS_FIELDS: frozenset[str] = frozenset(
    item.settings_field for item in SECRET_INVENTORY
)
MANDATORY_SECRET_ENV_VARS: frozenset[str] = frozenset(
    item.env_var for item in SECRET_INVENTORY if item.required
)

_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|authorization|"
    r"refresh[_-]?token|access[_-]?token|cookie|jwt|bearer|private[_-]?key|"
    r"database[_-]?url|dsn|credential)",
    re.IGNORECASE,
)

# Runtime values registered after settings load (used by log filter).
_runtime_secret_values: tuple[str, ...] = ()


def collect_secret_values(settings: Settings) -> tuple[str, ...]:
    """Extract non-empty secret strings from Settings for scrubbing."""
    values: list[str] = []
    for field in SECRET_SETTINGS_FIELDS:
        raw = getattr(settings, field, None)
        if isinstance(raw, str) and raw.strip():
            values.append(raw)
    # database_url embeds password even when built from discrete fields
    try:
        url = settings.database_url
    except Exception:  # noqa: BLE001 — never fail scrubbing
        url = ""
    if isinstance(url, str) and url.strip():
        values.append(url)
        redacted_url = redact_connection_string(url)
        # Also scrub the password segment alone when parseable
        password = _password_from_url(url)
        if password:
            values.append(password)
        del redacted_url
    # Longest first so overlapping replacements prefer full secrets
    unique = sorted({v for v in values if v}, key=len, reverse=True)
    return tuple(unique)


def register_runtime_secrets(settings: Settings) -> None:
    """Register secret values for log/exception scrubbing (call at startup)."""
    global _runtime_secret_values
    _runtime_secret_values = collect_secret_values(settings)


def clear_runtime_secrets() -> None:
    """Clear registered secrets (tests / shutdown)."""
    global _runtime_secret_values
    _runtime_secret_values = ()


def runtime_secret_values() -> tuple[str, ...]:
    return _runtime_secret_values


def _password_from_url(url: str) -> str | None:
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if parts.password:
        return parts.password
    return None


def redact_connection_string(url: str) -> str:
    """Mask userinfo password in a database URL."""
    if not url:
        return url
    try:
        parts = urlsplit(url)
    except ValueError:
        return REDACTED
    if not parts.password:
        return url
    # urlsplit keeps username/password in netloc; rebuild safely
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    user = parts.username or ""
    auth = f"{user}:{REDACTED}@" if user else f":{REDACTED}@"
    netloc = f"{auth}{host}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def redact_text(text: str, extra_secrets: Iterable[str] | None = None) -> str:
    """Replace known secret substrings in free-form text."""
    if not text:
        return text
    secrets = list(_runtime_secret_values)
    if extra_secrets:
        secrets.extend(s for s in extra_secrets if s)
    secrets = sorted({s for s in secrets if s and len(s) >= 4}, key=len, reverse=True)
    scrubbed = text
    for secret in secrets:
        if secret in scrubbed:
            scrubbed = scrubbed.replace(secret, REDACTED)
    return scrubbed


def redact_mapping(value: Any) -> Any:
    """Recursively mask secret-like keys in dict/list structures."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            if _SENSITIVE_KEY_RE.search(key_str):
                cleaned[key_str] = REDACTED
            else:
                cleaned[key_str] = redact_mapping(item)
        return cleaned
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    if isinstance(value, tuple):
        return [redact_mapping(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def safe_exception_text(exc: BaseException) -> str:
    """Exception text safe for logs (secret values scrubbed)."""
    return redact_text(f"{type(exc).__name__}: {exc}")


class SecretRedactingFilter(logging.Filter):
    """Logging filter that scrubs registered secret values from records.

    Tracebacks are sanitized here: ``logging.Formatter`` renders
    ``exc_info`` into ``exc_text`` *after* filters run, so we pre-render
    and redact ``exc_text`` before emit. Otherwise ``logger.exception()``
    leaks secrets that only appear in the traceback body.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            scrubbed = redact_text(msg)
            if scrubbed != msg:
                record.msg = scrubbed
                record.args = ()
            if record.exc_info and not record.exc_text:
                try:
                    record.exc_text = logging.Formatter().formatException(
                        record.exc_info
                    )
                except Exception:  # noqa: BLE001 — fall back to safe text
                    exc = record.exc_info[1]
                    record.exc_text = safe_exception_text(exc) if exc else ""
            if record.exc_text:
                record.exc_text = redact_text(record.exc_text)
            stack_info = getattr(record, "stack_info", None)
            if isinstance(stack_info, str) and stack_info:
                record.stack_info = redact_text(stack_info)
        except Exception:  # noqa: BLE001 — never break logging
            return True
        return True

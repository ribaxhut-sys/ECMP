"""Password hashing and JWT / refresh-token primitives."""

from __future__ import annotations

import hashlib
import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from app.core.config import Settings
from app.core.user_messages import m

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_TEMP_PASSWORD_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*"


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (never store plaintext)."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Uses passlib/bcrypt constant-time comparison internally.
    """
    return _pwd_context.verify(plain_password, password_hash)


def generate_temporary_password(*, length: int = 16) -> str:
    """Cryptographically secure temporary password (never log the return value)."""
    if length < 8:
        length = 8
    return "".join(secrets.choice(_TEMP_PASSWORD_ALPHABET) for _ in range(length))


def generate_password_reset_token() -> str:
    """Opaque single-use reset token (URL-safe). Never store or log the return value."""
    return secrets.token_urlsafe(32)


def hash_password_reset_token(raw_token: str) -> str:
    """SHA-256 hash for at-rest storage of password-reset tokens."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def tokens_equal(left: str, right: str) -> bool:
    """Constant-time equality for opaque token strings."""
    return secrets.compare_digest(left, right)


def create_access_token(
    *,
    subject: str,
    settings: Settings,
    claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT access token (default TTL from settings, 15 min)."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload: dict[str, Any] = {}
    if claims:
        payload.update(claims)
    payload["sub"] = subject
    payload["exp"] = expire
    payload["type"] = "access"
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except PyJWTError as exc:
        raise ValueError(m("auth.invalid_token")) from exc
    if payload.get("type") not in (None, "access"):
        raise ValueError(m("auth.invalid_token"))
    return payload


def generate_refresh_token() -> str:
    """Opaque refresh token (URL-safe). Never log the return value."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 hash for at-rest storage of refresh tokens."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

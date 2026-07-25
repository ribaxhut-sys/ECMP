"""Password hashing and JWT / refresh-token primitives."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext

from app.core.config import Settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (never store plaintext)."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return _pwd_context.verify(plain_password, password_hash)


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
        raise ValueError("Invalid or expired token") from exc
    if payload.get("type") not in (None, "access"):
        raise ValueError("Invalid or expired token")
    return payload


def generate_refresh_token() -> str:
    """Opaque refresh token (URL-safe). Never log the return value."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 hash for at-rest storage of refresh tokens."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

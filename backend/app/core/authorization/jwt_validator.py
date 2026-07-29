"""OIDC access-token JWT validator (TASK-PLATFORM-SECMIG-P2-001).

Validates RS256 tokens against cached JWKS. Fail-closed on any check failure.
"""

from __future__ import annotations

from typing import Any

import jwt
from jwt.exceptions import PyJWTError

from app.core.authorization.jwks_cache import JwksCache

_ALLOWED_ALGORITHMS = ("RS256",)
_CLOCK_SKEW_SECONDS = 30


class JwtValidator:
    """Validate IdP-issued access tokens (offline JWKS verification)."""

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_cache: JwksCache,
        leeway_seconds: int = _CLOCK_SKEW_SECONDS,
    ) -> None:
        self._issuer = issuer.strip()
        self._audience = audience.strip()
        self._jwks_cache = jwks_cache
        self._leeway = leeway_seconds

    def validate(self, token: str) -> dict[str, Any]:
        """Return validated claims or raise ``ValueError`` (fail-closed)."""
        if not token or not token.strip():
            raise ValueError("Empty token")

        try:
            header = jwt.get_unverified_header(token)
        except PyJWTError as exc:
            raise ValueError("Invalid JWT header") from exc

        alg = header.get("alg")
        if alg != "RS256":
            raise ValueError(f"Unsupported JWT alg '{alg}'")

        kid = header.get("kid")
        if not kid or not isinstance(kid, str):
            raise ValueError("JWT header missing kid")

        try:
            key = self._jwks_cache.get_key(kid)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        try:
            return jwt.decode(
                token,
                key=key,
                algorithms=list(_ALLOWED_ALGORITHMS),
                issuer=self._issuer,
                audience=self._audience,
                leeway=self._leeway,
                options={
                    "require": ["exp", "iss", "aud", "sub"],
                    "verify_nbf": True,
                },
            )
        except PyJWTError as exc:
            raise ValueError("Invalid or expired token") from exc

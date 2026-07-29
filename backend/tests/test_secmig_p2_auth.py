"""SEC-MIG Phase 2 — Backend JWT Integration Foundation tests.

TASK-PLATFORM-SECMIG-P2-001
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.security import HTTPAuthorizationCredentials

from app.core.authorization.auth_strategy import (
    DevAuthenticationStrategy,
    JwtAuthenticationStrategy,
    build_authentication_strategy,
    configure_authentication,
    get_authentication_strategy,
    reset_authentication_strategy,
)
from app.core.authorization.jwks_cache import JwksCache
from app.core.authorization.jwt_validator import JwtValidator
from app.core.authorization.role_mapper import RoleMapper
from app.core.config import (
    ConfigValidationError,
    Settings,
    collect_runtime_config_issues,
    validate_runtime_config,
)
from app.core.errors import UnauthenticatedError
from app.core.security import create_access_token
from app.modules.iam.permission_resolver import PermissionResolver

_ISSUER = "http://localhost:8180/realms/ecmp"
_AUDIENCE = "ecmp-api"
_KID = "test-key-1"


@pytest.fixture(autouse=True)
def _reset_strategy() -> Any:
    reset_authentication_strategy(None)
    yield
    reset_authentication_strategy(None)


@pytest.fixture(scope="module")
def rsa_material() -> dict[str, Any]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()

    def _b64url_uint(value: int) -> str:
        length = (value.bit_length() + 7) // 8
        return jwt.utils.base64url_encode(value.to_bytes(length, "big")).decode("ascii")

    jwk = {
        "kty": "RSA",
        "kid": _KID,
        "use": "sig",
        "alg": "RS256",
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return {"private_pem": pem, "jwks": {"keys": [jwk]}}


def _jwt_settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "environment": "development",
        "ecmp_auth_mode": "jwt",
        "ecmp_env": "local",
        "oidc_issuer": _ISSUER,
        "oidc_audience": _AUDIENCE,
        "oidc_jwks_url": "http://jwks.test/certs",
        "jwt_secret_key": "test-secret-key-for-secmig-p2-foundation",
        "jwt_algorithm": "HS256",
        "jwt_access_token_expire_minutes": 15,
    }
    base.update(overrides)
    return Settings(**base)


def _dev_settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "environment": "development",
        "ecmp_auth_mode": "dev",
        "ecmp_env": "local",
        "jwt_secret_key": "test-secret-key-for-secmig-p2-foundation",
        "jwt_algorithm": "HS256",
        "jwt_access_token_expire_minutes": 15,
    }
    base.update(overrides)
    return Settings(**base)


def _sign_rs256(
    claims: dict[str, Any],
    rsa_material: dict[str, Any],
    *,
    kid: str = _KID,
    headers: dict[str, Any] | None = None,
) -> str:
    hdr = {"kid": kid, "alg": "RS256"}
    if headers:
        hdr.update(headers)
    return jwt.encode(
        claims,
        rsa_material["private_pem"],
        algorithm="RS256",
        headers=hdr,
    )


def _valid_claims(**overrides: Any) -> dict[str, Any]:
    now = datetime.now(UTC)
    subject = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "iss": _ISSUER,
        "aud": _AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "nbf": now - timedelta(seconds=5),
        "roles": ["cs_agent"],
        "sid": "session-1",
        "orgUnitId": "OU-JKT-01",
    }
    payload.update(overrides)
    return payload


def _cache_for(rsa_material: dict[str, Any], *, ttl: int = 600) -> JwksCache:
    return JwksCache(
        "http://jwks.test/certs",
        ttl_seconds=ttl,
        fetcher=lambda _url: rsa_material["jwks"],
    )


# --- Strategy selection -------------------------------------------------------


def test_build_strategy_selects_dev() -> None:
    strategy = build_authentication_strategy(_dev_settings())
    assert isinstance(strategy, DevAuthenticationStrategy)


def test_build_strategy_selects_jwt() -> None:
    strategy = build_authentication_strategy(_jwt_settings())
    assert isinstance(strategy, JwtAuthenticationStrategy)


def test_configure_authentication_sets_process_strategy() -> None:
    configure_authentication(_dev_settings())
    assert isinstance(get_authentication_strategy(), DevAuthenticationStrategy)
    configure_authentication(_jwt_settings())
    assert isinstance(get_authentication_strategy(), JwtAuthenticationStrategy)


def test_default_auth_mode_is_dev() -> None:
    settings = Settings(
        environment="development",
        jwt_secret_key="test-secret-key-for-secmig-p2-foundation",
    )
    assert settings.ecmp_auth_mode == "dev"
    assert isinstance(build_authentication_strategy(settings), DevAuthenticationStrategy)


# --- Startup guard ------------------------------------------------------------


def test_startup_guard_rejects_dev_on_shared_env() -> None:
    settings = _dev_settings(ecmp_env="shared")
    issues = collect_runtime_config_issues(settings)
    assert any(i.variable == "ECMP_AUTH_MODE" for i in issues)
    with pytest.raises(ConfigValidationError):
        validate_runtime_config(settings)


def test_startup_guard_allows_jwt_on_shared_env() -> None:
    settings = _jwt_settings(ecmp_env="shared")
    variables = {i.variable for i in collect_runtime_config_issues(settings)}
    assert "ECMP_AUTH_MODE" not in variables


def test_jwt_mode_requires_oidc_config() -> None:
    settings = _jwt_settings(oidc_issuer=None, oidc_audience=None, oidc_jwks_url=None)
    variables = {i.variable for i in collect_runtime_config_issues(settings)}
    assert "OIDC_ISSUER" in variables
    assert "OIDC_AUDIENCE" in variables
    assert "OIDC_JWKS_URL" in variables


# --- Role mapping -------------------------------------------------------------


def test_role_mapper_maps_idp_roles() -> None:
    mapper = RoleMapper()
    assert mapper.map_many(["cs_agent", "viewer", "unknown"]) == ("AGENT", "VIEWER")


def test_role_mapper_passthrough_internal_codes() -> None:
    mapper = RoleMapper()
    assert mapper.map_many(["AGENT", "SUPERVISOR"]) == ("AGENT", "SUPERVISOR")


def test_role_mapper_deduplicates() -> None:
    mapper = RoleMapper()
    assert mapper.map_many(["cs_agent", "AGENT", "cs_agent"]) == ("AGENT",)


# --- JWKS cache ---------------------------------------------------------------


def test_jwks_cache_fetches_once_within_ttl(rsa_material: dict[str, Any]) -> None:
    fetches = {"n": 0}

    def fetcher(_url: str) -> dict[str, Any]:
        fetches["n"] += 1
        return rsa_material["jwks"]

    cache = JwksCache("http://jwks.test/certs", ttl_seconds=600, fetcher=fetcher)
    key1 = cache.get_key(_KID)
    key2 = cache.get_key(_KID)
    assert key1 is not None and key2 is not None
    assert fetches["n"] == 1
    assert cache.fetch_count == 1


def test_jwks_cache_refreshes_after_ttl(rsa_material: dict[str, Any]) -> None:
    cache = JwksCache(
        "http://jwks.test/certs",
        ttl_seconds=1,
        fetcher=lambda _url: rsa_material["jwks"],
    )
    cache.get_key(_KID)
    time.sleep(1.05)
    cache.get_key(_KID)
    assert cache.fetch_count == 2


def test_jwks_cache_unknown_kid_fail_closed(rsa_material: dict[str, Any]) -> None:
    cache = _cache_for(rsa_material)
    with pytest.raises(ValueError, match="Unknown kid"):
        cache.get_key("missing-kid")


# --- JWT validation -----------------------------------------------------------


def test_jwt_validator_accepts_valid_token(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    token = _sign_rs256(_valid_claims(), rsa_material)
    claims = validator.validate(token)
    assert claims["aud"] == _AUDIENCE
    assert claims["iss"] == _ISSUER
    assert "sub" in claims


def test_jwt_validator_rejects_wrong_issuer(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    token = _sign_rs256(_valid_claims(iss="http://evil/realms/x"), rsa_material)
    with pytest.raises(ValueError):
        validator.validate(token)


def test_jwt_validator_rejects_wrong_audience(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    token = _sign_rs256(_valid_claims(aud="other-api"), rsa_material)
    with pytest.raises(ValueError):
        validator.validate(token)


def test_jwt_validator_rejects_expired(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    now = datetime.now(UTC)
    token = _sign_rs256(
        _valid_claims(
            iat=now - timedelta(hours=2),
            exp=now - timedelta(hours=1),
            nbf=now - timedelta(hours=2),
        ),
        rsa_material,
    )
    with pytest.raises(ValueError):
        validator.validate(token)


def test_jwt_validator_rejects_future_nbf(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    now = datetime.now(UTC)
    token = _sign_rs256(
        _valid_claims(nbf=now + timedelta(hours=1), exp=now + timedelta(hours=2)),
        rsa_material,
    )
    with pytest.raises(ValueError):
        validator.validate(token)


def test_jwt_validator_rejects_non_rs256(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    # HS256 token must fail closed even if somehow presented to jwt mode validator.
    token = jwt.encode(
        _valid_claims(),
        "not-a-real-secret-but-long-enough-for-test",
        algorithm="HS256",
        headers={"kid": _KID},
    )
    with pytest.raises(ValueError, match="Unsupported JWT alg"):
        validator.validate(token)


def test_jwt_validator_rejects_missing_kid(rsa_material: dict[str, Any]) -> None:
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    token = jwt.encode(
        _valid_claims(),
        rsa_material["private_pem"],
        algorithm="RS256",
        headers={"alg": "RS256"},
    )
    with pytest.raises(ValueError, match="missing kid"):
        validator.validate(token)


# --- Jwt strategy + principal mapping + permissions ---------------------------


def test_jwt_strategy_maps_principal_and_resolves_permissions(
    rsa_material: dict[str, Any],
) -> None:
    settings = _jwt_settings()
    cache = _cache_for(rsa_material)
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=cache,
    )
    strategy = JwtAuthenticationStrategy(
        settings,
        validator=validator,
        role_mapper=RoleMapper(),
    )
    token = _sign_rs256(_valid_claims(), rsa_material)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    session = MagicMock()
    resolver = MagicMock()
    resolver.resolve_for_role_codes.return_value = frozenset({"complaints:read"})

    # Patch PermissionResolver construction via session path: stub scalars unused;
    # instead monkeypatch strategy authenticate by checking extract + call resolve.
    user_id, roles, payload = strategy.extract_identity(creds)
    assert roles == ("AGENT",)
    assert payload.get("sid") == "session-1"
    assert payload.get("orgUnitId") == "OU-JKT-01"
    assert isinstance(user_id, uuid.UUID)

    # Full authenticate with mocked resolver method
    original = PermissionResolver.resolve_for_role_codes

    def _fake_resolve(self: PermissionResolver, role_codes: Any) -> frozenset[str]:
        assert tuple(role_codes) == ("AGENT",)
        return frozenset({"complaints:create", "complaints:read"})

    PermissionResolver.resolve_for_role_codes = _fake_resolve  # type: ignore[method-assign]
    try:
        principal = strategy.authenticate(creds, session)
    finally:
        PermissionResolver.resolve_for_role_codes = original  # type: ignore[method-assign]

    assert principal.user_id == user_id
    assert principal.roles == ("AGENT",)
    assert principal.sid == "session-1"
    assert principal.org_unit_id == "OU-JKT-01"
    assert principal.permissions == frozenset({"complaints:create", "complaints:read"})
    assert principal.force_password_change is False


def test_jwt_strategy_ignores_permissions_claim(rsa_material: dict[str, Any]) -> None:
    settings = _jwt_settings()
    validator = JwtValidator(
        issuer=_ISSUER,
        audience=_AUDIENCE,
        jwks_cache=_cache_for(rsa_material),
    )
    strategy = JwtAuthenticationStrategy(settings, validator=validator)
    token = _sign_rs256(
        _valid_claims(permissions=["should:not:apply", "*"]),
        rsa_material,
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    session = MagicMock()

    original = PermissionResolver.resolve_for_role_codes

    def _fake_resolve(self: PermissionResolver, role_codes: Any) -> frozenset[str]:
        return frozenset({"complaints:read"})

    PermissionResolver.resolve_for_role_codes = _fake_resolve  # type: ignore[method-assign]
    try:
        principal = strategy.authenticate(creds, session)
    finally:
        PermissionResolver.resolve_for_role_codes = original  # type: ignore[method-assign]

    assert principal.permissions == frozenset({"complaints:read"})
    assert "should:not:apply" not in principal.permissions


def test_jwt_strategy_rejects_invalid_token(rsa_material: dict[str, Any]) -> None:
    strategy = JwtAuthenticationStrategy(
        _jwt_settings(),
        validator=JwtValidator(
            issuer=_ISSUER,
            audience=_AUDIENCE,
            jwks_cache=_cache_for(rsa_material),
        ),
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-jwt")
    with pytest.raises(UnauthenticatedError):
        strategy.extract_identity(creds)


def test_permission_resolver_role_codes_empty() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = []
    perms = PermissionResolver(session).resolve_for_role_codes(())
    assert perms == frozenset()
    session.scalars.assert_not_called()


def test_permission_resolver_role_codes_queries_matrix() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = ["complaints:read", "complaints:create"]
    perms = PermissionResolver(session).resolve_for_role_codes(["AGENT", "viewer"])
    assert perms == frozenset({"complaints:read", "complaints:create"})
    session.scalars.assert_called_once()


# --- Dev mode regression ------------------------------------------------------


def test_dev_strategy_unchanged_hs256_path() -> None:
    settings = _dev_settings()
    strategy = DevAuthenticationStrategy(settings)
    user_id = uuid.uuid4()
    token = create_access_token(
        subject=str(user_id),
        settings=settings,
        claims={"roles": ["AGENT"], "permissions": ["complaints:read"]},
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    session = MagicMock()
    principal = strategy.authenticate(creds, session)
    assert principal.user_id == user_id
    assert principal.roles == ("AGENT",)
    assert principal.permissions == frozenset({"complaints:read"})


def test_authenticate_bearer_dev_regression() -> None:
    from app.core.authorization.authentication import authenticate_bearer

    settings = _dev_settings()
    user_id = uuid.uuid4()
    token = create_access_token(
        subject=str(user_id),
        settings=settings,
        claims={"roles": ["AGENT"]},
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    resolved_id, roles, payload = authenticate_bearer(creds, settings)
    assert resolved_id == user_id
    assert roles == ("AGENT",)
    assert payload.get("sub") == str(user_id)


def test_authenticate_bearer_jwt_mode(rsa_material: dict[str, Any]) -> None:
    settings = _jwt_settings()
    strategy = JwtAuthenticationStrategy(
        settings,
        validator=JwtValidator(
            issuer=_ISSUER,
            audience=_AUDIENCE,
            jwks_cache=_cache_for(rsa_material),
        ),
    )
    token = _sign_rs256(_valid_claims(roles=["viewer"]), rsa_material)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user_id, roles, payload = strategy.extract_identity(creds)
    assert roles == ("VIEWER",)
    assert payload["aud"] == _AUDIENCE
    assert isinstance(user_id, uuid.UUID)

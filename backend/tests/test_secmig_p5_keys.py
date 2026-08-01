"""TASK-PLATFORM-SECMIG-P5-003 — Internal key registry foundation tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.keys import (
    PLATFORM_HS256_KID,
    InMemoryKeyRegistry,
    KeyAlgorithm,
    KeyNotFoundError,
    KeyPurpose,
    KeyStatus,
    ManagedKey,
    NoActiveKeyError,
    build_registry_from_settings,
    clear_key_registry,
    configure_key_registry,
    get_key_registry,
    validate_key_metadata,
)
from app.core.security import create_access_token, decode_access_token
from app.main import create_app

pytestmark = pytest.mark.security

_LAB_JWT = "change-me-in-production"
_LAB_DB = "ecmp"


def _settings(**kwargs: object) -> Settings:
    values: dict[str, object] = {
        "environment": "development",
        "jwt_secret_key": _LAB_JWT,
        "postgres_password": _LAB_DB,
    }
    values.update(kwargs)
    return Settings(_env_file=None, **values)  # type: ignore[arg-type]


def _hs256(
    *,
    kid: str = PLATFORM_HS256_KID,
    status: KeyStatus = KeyStatus.ACTIVE,
    material: str | None = _LAB_JWT,
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> ManagedKey:
    return ManagedKey(
        kid=kid,
        purpose=KeyPurpose.JWT_HS256_SIGNING,
        algorithm=KeyAlgorithm.HS256,
        status=status,
        created_at=created_at or datetime.now(UTC),
        expires_at=expires_at,
        material=material,
    )


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    clear_key_registry()
    yield
    clear_key_registry()
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Metadata validation
# ---------------------------------------------------------------------------


def test_metadata_validation_accepts_complete_hs256_key() -> None:
    validate_key_metadata(_hs256())


def test_metadata_validation_rejects_empty_kid() -> None:
    with pytest.raises(ValueError, match="kid"):
        validate_key_metadata(_hs256(kid=""))


def test_metadata_validation_rejects_expires_before_created() -> None:
    created = datetime.now(UTC)
    with pytest.raises(ValueError, match="expires_at"):
        validate_key_metadata(
            _hs256(created_at=created, expires_at=created - timedelta(seconds=1))
        )


def test_metadata_validation_rejects_active_hs256_without_material() -> None:
    with pytest.raises(ValueError, match="material"):
        validate_key_metadata(_hs256(material=""))


def test_metadata_validation_rejects_purpose_algorithm_mismatch() -> None:
    key = ManagedKey(
        kid="bad",
        purpose=KeyPurpose.JWT_HS256_SIGNING,
        algorithm=KeyAlgorithm.RS256,
        status=KeyStatus.PENDING,
        created_at=datetime.now(UTC),
        material=None,
    )
    with pytest.raises(ValueError, match="HS256"):
        validate_key_metadata(key)


def test_managed_key_repr_redacts_material() -> None:
    secret = "ReprLeakKeyMaterial-ABCDEFGH"
    rendered = repr(_hs256(material=secret))
    assert secret not in rendered
    assert "REDACTED" in rendered


def test_metadata_dict_omits_material() -> None:
    meta = _hs256().metadata_dict()
    assert set(meta) >= {
        "kid",
        "purpose",
        "algorithm",
        "status",
        "created_at",
        "expires_at",
    }
    assert "material" not in meta


# ---------------------------------------------------------------------------
# Active key + kid lookup
# ---------------------------------------------------------------------------


def test_get_active_key_returns_active_hs256() -> None:
    registry = InMemoryKeyRegistry()
    registry.register(_hs256())
    active = registry.get_active_key(KeyPurpose.JWT_HS256_SIGNING)
    assert active.kid == PLATFORM_HS256_KID
    assert active.status == KeyStatus.ACTIVE
    assert active.material == _LAB_JWT


def test_get_active_key_raises_when_missing() -> None:
    registry = InMemoryKeyRegistry()
    with pytest.raises(NoActiveKeyError):
        registry.get_active_key(KeyPurpose.JWT_HS256_SIGNING)


def test_get_key_by_kid() -> None:
    registry = InMemoryKeyRegistry()
    registry.register(_hs256(kid="k1", status=KeyStatus.PENDING, material=None))
    registry.register(_hs256(kid="k2", material="other-secret-value-01"))
    found = registry.get_key("k1")
    assert found.status == KeyStatus.PENDING
    assert registry.get_key("k2").material == "other-secret-value-01"


def test_get_key_unknown_kid() -> None:
    registry = InMemoryKeyRegistry()
    with pytest.raises(KeyNotFoundError, match="missing"):
        registry.get_key("missing")


def test_register_rejects_second_active_same_purpose() -> None:
    registry = InMemoryKeyRegistry()
    registry.register(_hs256(kid="a"))
    with pytest.raises(ValueError, match="already has active"):
        registry.register(_hs256(kid="b", material="second-secret-value-99"))


# ---------------------------------------------------------------------------
# Manual rotation (no scheduler)
# ---------------------------------------------------------------------------


def test_manual_rotate_retires_previous_and_activates_new() -> None:
    registry = InMemoryKeyRegistry()
    registry.register(_hs256(kid="old", material="old-secret-value-0001"))
    new = _hs256(kid="new", material="new-secret-value-0002")
    registry.rotate(new)
    assert registry.get_active_key(KeyPurpose.JWT_HS256_SIGNING).kid == "new"
    assert registry.get_key("old").status == KeyStatus.RETIRED
    assert registry.get_key("new").status == KeyStatus.ACTIVE


def test_activate_retires_previous_active() -> None:
    registry = InMemoryKeyRegistry()
    registry.register(_hs256(kid="old", material="old-secret-value-0001"))
    registry.register(
        _hs256(kid="next", status=KeyStatus.PENDING, material="next-secret-value-02")
    )
    registry.activate("next")
    assert registry.get_active_key(KeyPurpose.JWT_HS256_SIGNING).kid == "next"
    assert registry.get_key("old").status == KeyStatus.RETIRED


# ---------------------------------------------------------------------------
# Settings bootstrap + process registry
# ---------------------------------------------------------------------------


def test_build_registry_from_settings_seeds_platform_hs256() -> None:
    settings = _settings()
    registry = build_registry_from_settings(settings)
    active = registry.get_active_key(KeyPurpose.JWT_HS256_SIGNING)
    assert active.kid == PLATFORM_HS256_KID
    assert active.algorithm == KeyAlgorithm.HS256
    assert active.material == _LAB_JWT


def test_configure_and_get_key_registry() -> None:
    settings = _settings()
    configure_key_registry(build_registry_from_settings(settings))
    active = get_key_registry().get_active_key(KeyPurpose.JWT_HS256_SIGNING)
    assert active.kid == PLATFORM_HS256_KID


# ---------------------------------------------------------------------------
# Backward compatibility — JWT / JWKS paths unchanged
# ---------------------------------------------------------------------------


def test_hs256_token_roundtrip_unchanged_with_registry_configured() -> None:
    """Registry must not alter JWT payload or HS256 encode/decode behavior."""
    settings = _settings()
    configure_key_registry(build_registry_from_settings(settings))
    token = create_access_token(subject="00000000-0000-4000-8000-000000000001", settings=settings)
    # No kid injected into header (external JWT behavior unchanged)
    header = pyjwt.get_unverified_header(token)
    assert "kid" not in header
    payload = decode_access_token(token, settings)
    assert payload["sub"] == "00000000-0000-4000-8000-000000000001"
    assert payload["type"] == "access"


def test_rs256_jwks_path_still_resolves_by_kid() -> None:
    """JWKS verification path remains independent of the in-memory registry."""
    from cryptography.hazmat.primitives.asymmetric import rsa

    from app.core.authorization.jwks_cache import JwksCache
    from app.core.authorization.jwt_validator import JwtValidator

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def _b64url_uint(value: int) -> str:
        length = (value.bit_length() + 7) // 8
        return pyjwt.utils.base64url_encode(value.to_bytes(length, "big")).decode("ascii")

    kid = "idp-compat-key-1"
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": _b64url_uint(public_numbers.n),
                "e": _b64url_uint(public_numbers.e),
            }
        ]
    }
    cache = JwksCache("http://jwks.test/certs", fetcher=lambda _url: jwks)
    assert cache.get_key(kid) is not None

    settings = _settings()
    configure_key_registry(build_registry_from_settings(settings))
    # Both lookup styles coexist: registry (HS256) and JWKS (RS256 kid)
    assert get_key_registry().get_key(PLATFORM_HS256_KID).algorithm == KeyAlgorithm.HS256

    from cryptography.hazmat.primitives import serialization

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    now = datetime.now(UTC)
    token = pyjwt.encode(
        {
            "sub": "00000000-0000-4000-8000-000000000099",
            "iss": "http://idp.test/realms/ecmp",
            "aud": "ecmp-api",
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "nbf": now - timedelta(seconds=1),
        },
        pem,
        algorithm="RS256",
        headers={"kid": kid},
    )
    validator = JwtValidator(
        issuer="http://idp.test/realms/ecmp",
        audience="ecmp-api",
        jwks_cache=cache,
    )
    claims = validator.validate(token)
    assert claims["sub"] == "00000000-0000-4000-8000-000000000099"


def test_create_app_configures_key_registry() -> None:
    settings = _settings()
    get_settings.cache_clear()
    clear_key_registry()
    with (
        patch("app.main.get_settings", return_value=settings),
        TestClient(create_app()) as client,
    ):
        response = client.get("/live")
        assert response.status_code == 200
        active = get_key_registry().get_active_key(KeyPurpose.JWT_HS256_SIGNING)
        assert active.material == _LAB_JWT
    clear_key_registry()
    get_settings.cache_clear()

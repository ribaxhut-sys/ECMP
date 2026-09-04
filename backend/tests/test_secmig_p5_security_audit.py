"""TASK-PLATFORM-SECMIG-P5-004 — Security audit foundation tests."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from starlette.datastructures import Headers

from app.core.authorization.permission_check import require_permissions
from app.core.authorization.principal import Principal
from app.core.config import Settings
from app.core.enums import AuditAction
from app.core.errors import PermissionDeniedError, UnauthenticatedError
from app.core.secrets import REDACTED, clear_runtime_secrets, register_runtime_secrets
from app.modules.audit.security_events import (
    ENTITY_TYPE_SECURITY,
    SECURITY_EVENT_ACTIONS,
    SecurityEventType,
    build_trace_metadata,
    resolve_request_trace_ids,
    write_security_event,
)
from app.modules.audit.service import AuditService, redact_sensitive

pytestmark = pytest.mark.security


def _request(
    *,
    request_id: str | None = "req-fixed-1",
    correlation_id: str | None = None,
    headers: dict[str, str] | None = None,
    path: str = "/api/v1/auth/login",
) -> MagicMock:
    req = MagicMock(spec=Request)
    state = SimpleNamespace()
    if request_id is not None:
        state.request_id = request_id
    if correlation_id is not None:
        state.correlation_id = correlation_id
    req.state = state
    req.headers = Headers(headers or {})
    req.url.path = path
    req.client = SimpleNamespace(host="127.0.0.1")
    return req


# --- Taxonomy -----------------------------------------------------------------


def test_security_event_taxonomy_is_centralized() -> None:
    assert SecurityEventType.LOGIN_FAILED == "security.login_failed"
    assert SecurityEventType.TOKEN_REJECTED == "security.token_rejected"
    assert SecurityEventType.PERMISSION_DENIED == "security.permission_denied"
    assert SecurityEventType.LOCKOUT == "security.lockout"
    assert set(SECURITY_EVENT_ACTIONS) == set(SecurityEventType)
    assert SECURITY_EVENT_ACTIONS[SecurityEventType.LOGIN_FAILED] == AuditAction.LOGIN
    assert (
        SECURITY_EVENT_ACTIONS[SecurityEventType.PERMISSION_DENIED] == AuditAction.UPDATE
    )


# --- Traceability -------------------------------------------------------------


def test_request_id_propagation_into_metadata() -> None:
    req = _request(request_id="abc-123", correlation_id="corr-9")
    meta = build_trace_metadata(req, extra={"reasonCode": "UNAUTHENTICATED"})
    assert meta["requestId"] == "abc-123"
    assert meta["correlationId"] == "corr-9"
    assert meta["reasonCode"] == "UNAUTHENTICATED"


def test_correlation_id_falls_back_to_request_id() -> None:
    req = _request(request_id="only-req", correlation_id=None)
    request_id, correlation_id = resolve_request_trace_ids(req)
    assert request_id == "only-req"
    assert correlation_id == "only-req"


def test_correlation_id_from_header_when_state_missing() -> None:
    req = _request(
        request_id=None,
        headers={
            "X-Request-ID": "hdr-req",
            "X-Correlation-Id": "hdr-corr",
        },
    )
    # Clear state attribute so header path is used
    req.state = SimpleNamespace()
    request_id, correlation_id = resolve_request_trace_ids(req)
    assert request_id == "hdr-req"
    assert correlation_id == "hdr-corr"


def test_request_id_generated_when_absent() -> None:
    request_id, correlation_id = resolve_request_trace_ids(None)
    assert request_id
    assert correlation_id == request_id
    uuid.UUID(request_id)  # valid UUID


# --- Security event creation --------------------------------------------------


def test_write_security_event_persists_taxonomy_and_trace() -> None:
    repo = MagicMock()
    captured: list[object] = []

    def capture_add(row: object) -> object:
        captured.append(row)
        return row

    repo.add.side_effect = capture_add
    session = MagicMock()

    with patch(
        "app.modules.audit.security_events.AuditRepository",
        return_value=repo,
    ):
        write_security_event(
            session,
            request=_request(request_id="trace-1"),
            event_type=SecurityEventType.LOGIN_FAILED,
            new_values={"reason": "invalid_credentials", "password": "leak"},
            metadata_extra={"reasonCode": "UNAUTHENTICATED"},
            commit=True,
        )

    assert len(captured) == 1
    row = captured[0]
    assert row.event_type == SecurityEventType.LOGIN_FAILED.value
    assert row.entity_type == ENTITY_TYPE_SECURITY
    assert row.action == AuditAction.LOGIN.value
    assert row.metadata_json["requestId"] == "trace-1"
    assert row.metadata_json["correlationId"] == "trace-1"
    assert row.new_values["password"] == REDACTED
    assert row.new_values["reason"] == "invalid_credentials"
    repo.commit.assert_called_once()


def test_write_security_event_never_raises() -> None:
    session = MagicMock()
    with patch(
        "app.modules.audit.security_events.AuditService",
        side_effect=RuntimeError("db down"),
    ):
        write_security_event(
            session,
            request=_request(),
            event_type=SecurityEventType.TOKEN_REJECTED,
            new_values={"reason": "boom"},
        )


# --- Secret redaction in audit ------------------------------------------------


def test_audit_redaction_uses_p5_002_library(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PGADMIN_DEFAULT_PASSWORD", raising=False)
    settings = Settings(
        _env_file=None,
        environment="development",
        jwt_secret_key="super-secret-jwt-key-32chars!!",
        postgres_password="DbPass-Should-Scrub",
        pgadmin_default_password=None,
    )
    try:
        register_runtime_secrets(settings)
        cleaned = redact_sensitive(
            {
                "username": "admin",
                "password": "plain",
                "note": "token=super-secret-jwt-key-32chars!!",
                "nested": {"api_key": "abc", "ok": 1},
            }
        )
        assert cleaned["username"] == "admin"
        assert cleaned["password"] == REDACTED
        assert cleaned["nested"]["api_key"] == REDACTED
        assert cleaned["nested"]["ok"] == 1
        assert REDACTED in cleaned["note"]
        assert "super-secret-jwt-key-32chars!!" not in cleaned["note"]
    finally:
        clear_runtime_secrets()


def test_audit_service_log_redacts_via_shared_library() -> None:
    repo = MagicMock()
    repo.add.side_effect = lambda row: row
    service = AuditService(repo)
    result = service.log(
        event_type=SecurityEventType.TOKEN_REJECTED.value,
        entity_type=ENTITY_TYPE_SECURITY,
        action=AuditAction.LOGIN,
        metadata={
            "requestId": "r1",
            "correlationId": "r1",
            "authorization": "Bearer secret-token",
        },
        new_values={"token": "abc", "reason": "invalid"},
    )
    assert result.metadata is not None
    assert result.metadata["authorization"] == REDACTED
    assert result.metadata["requestId"] == "r1"
    assert result.new_values is not None
    assert result.new_values["token"] == REDACTED
    assert result.new_values["reason"] == "invalid"


# --- Backward compatibility ---------------------------------------------------


def test_legacy_audit_action_and_check_permissions_unchanged() -> None:
    """Pure permission check still raises without requiring Request/Session."""
    principal = Principal(user_id=uuid.uuid4(), permissions=frozenset())
    with pytest.raises(PermissionDeniedError) as exc:
        from app.core.authorization.permission_check import check_permissions

        check_permissions(principal, "audit:read")
    assert exc.value.code == "FORBIDDEN"


def test_require_permissions_still_returns_principal_on_success() -> None:
    gate = require_permissions("complaints:read")
    ok = Principal(
        user_id=uuid.uuid4(),
        permissions=frozenset({"complaints:read"}),
    )
    request = _request(request_id="compat-1")
    session = MagicMock()
    assert gate(principal=ok, request=request, session=session) is ok


def test_unauthenticated_error_shape_unchanged() -> None:
    err = UnauthenticatedError("Invalid or expired token")
    assert err.status_code == 401
    assert err.code == "UNAUTHENTICATED"
    assert err.message == "Invalid or expired token"


def test_password_event_types_remain_distinct_from_security_taxonomy() -> None:
    password_events = {
        "password.changed",
        "password.change_failed",
        "password.reset_requested",
    }
    security_values = {e.value for e in SecurityEventType}
    assert password_events.isdisjoint(security_values)

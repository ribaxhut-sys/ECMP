"""SEC-MIG Phase 4 — Organization Scope Enforcement tests.

TASK-PLATFORM-SECMIG-P4-001 / P4-001R rework.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.org_unit_guard import (
    OrgUnitGuard,
    enforce_org_scope,
    is_machine_service_identity,
    is_service_account_allowlisted,
    org_scope_enforcement_enabled,
)
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import NotFoundError, OrgScopeDeniedError
from app.db.session import get_db_session
from app.main import create_app
from app.models import Branch, User
from app.modules.assignments.router import get_assignment_service
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.router import get_cm_batch1_attachment_service, get_cm_batch1_service
from app.modules.cm_batch1.schemas import (
    ComplaintBatch1Response,
    DuplicateDecisionResponse,
    TransferAttachmentsResponse,
)
from app.modules.complaints.router import get_complaint_service
from app.modules.users.router import get_user_service
from app.modules.users.schemas import UserResponse


def _jwt_settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "environment": "development",
        "ecmp_auth_mode": "jwt",
        "ecmp_env": "shared",
        "oidc_issuer": "http://localhost:8180/realms/ecmp",
        "oidc_audience": "ecmp-api",
        "oidc_jwks_url": "http://jwks.test/certs",
        "jwt_secret_key": "test-secret-key-for-secmig-p4-org-scope",
        "jwt_algorithm": "HS256",
        "ecmp_org_scope_service_allowlist": "",
        "ecmp_org_scope_service_subjects": "",
    }
    base.update(overrides)
    return Settings(**base)


def _dev_settings() -> Settings:
    return Settings(
        environment="development",
        ecmp_auth_mode="dev",
        ecmp_env="local",
        jwt_secret_key="test-secret-key-for-secmig-p4-org-scope",
        jwt_algorithm="HS256",
    )


def _principal(
    *,
    org_unit_id: str | None,
    roles: tuple[str, ...] = ("SUPERVISOR",),
    permissions: frozenset[str] | None = None,
    user_id: uuid.UUID | None = None,
) -> Principal:
    return Principal(
        user_id=user_id or uuid.uuid4(),
        roles=roles,
        permissions=permissions
        or frozenset(
            {
                "complaints:assign",
                "complaints:update",
                "complaints:read",
                "complaints:create",
                "complaints:close",
            }
        ),
        org_unit_id=org_unit_id,
    )


# --- Guard ------------------------------------------------------------------


def test_org_scope_disabled_in_dev_mode() -> None:
    assert org_scope_enforcement_enabled(_dev_settings()) is False
    # Must not raise even on mismatch / missing claim.
    enforce_org_scope(_principal(org_unit_id=None), "OU-A", _dev_settings())
    enforce_org_scope(_principal(org_unit_id="OU-A"), "OU-B", _dev_settings())


def test_same_unit_allowed_in_jwt_mode() -> None:
    settings = _jwt_settings()
    enforce_org_scope(_principal(org_unit_id="OU-JKT-01"), "OU-JKT-01", settings)


def test_cross_unit_denied(caplog: pytest.LogCaptureFixture) -> None:
    settings = _jwt_settings()
    with caplog.at_level(logging.WARNING, logger="app.authz.org_scope"):
        with pytest.raises(OrgScopeDeniedError) as exc:
            enforce_org_scope(_principal(org_unit_id="OU-A"), "OU-B", settings)
    assert exc.value.status_code == 403
    assert exc.value.code == "ORG_SCOPE_DENIED"
    assert exc.value.details is not None
    assert exc.value.details.get("reason") == "org_unit_mismatch"
    # M-3: response must not expose protected resource ownership.
    assert "resourceOrgUnitId" not in exc.value.details
    assert "principalOrgUnitId" not in exc.value.details
    assert any("ORG_SCOPE_DENIED" in r.getMessage() for r in caplog.records)


def test_missing_claim_denied_fail_closed() -> None:
    settings = _jwt_settings()
    with pytest.raises(OrgScopeDeniedError) as exc:
        enforce_org_scope(_principal(org_unit_id=None), "OU-A", settings)
    assert exc.value.code == "ORG_SCOPE_DENIED"
    assert exc.value.details is not None
    assert exc.value.details.get("reason") == "missing_org_unit_claim"
    assert "resourceOrgUnitId" not in exc.value.details


def test_missing_resource_org_denied() -> None:
    settings = _jwt_settings()
    with pytest.raises(OrgScopeDeniedError) as exc:
        enforce_org_scope(_principal(org_unit_id="OU-A"), None, settings)
    assert exc.value.details is not None
    assert exc.value.details.get("reason") == "missing_resource_org_unit"


def test_service_account_default_deny() -> None:
    settings = _jwt_settings()
    sa = _principal(org_unit_id=None, roles=("SVC_KPI_READER",))
    assert is_service_account_allowlisted(sa, settings) is False
    with pytest.raises(OrgScopeDeniedError):
        OrgUnitGuard(settings).enforce(sa, "OU-A")


def test_service_account_role_allowlist_alone_insufficient() -> None:
    """M-2: human (or any) subject with allowlisted role but not in subjects → deny."""
    settings = _jwt_settings(ecmp_org_scope_service_allowlist="SVC_KPI_READER,AGENT")
    human = _principal(org_unit_id=None, roles=("AGENT",))
    assert is_machine_service_identity(human, settings) is False
    assert is_service_account_allowlisted(human, settings) is False
    with pytest.raises(OrgScopeDeniedError):
        OrgUnitGuard(settings).enforce(human, "OU-A")


def test_service_account_allowlisted_with_subject_and_role() -> None:
    subject = uuid.uuid4()
    settings = _jwt_settings(
        ecmp_org_scope_service_allowlist="SVC_KPI_READER",
        ecmp_org_scope_service_subjects=str(subject),
    )
    sa = _principal(
        org_unit_id=None,
        roles=("SVC_KPI_READER",),
        user_id=subject,
    )
    assert is_machine_service_identity(sa, settings) is True
    assert is_service_account_allowlisted(sa, settings) is True
    OrgUnitGuard(settings).enforce(sa, "OU-A")


def test_service_account_subject_without_role_denied() -> None:
    subject = uuid.uuid4()
    settings = _jwt_settings(
        ecmp_org_scope_service_allowlist="SVC_KPI_READER",
        ecmp_org_scope_service_subjects=str(subject),
    )
    sa = _principal(org_unit_id=None, roles=("AGENT",), user_id=subject)
    assert is_machine_service_identity(sa, settings) is True
    assert is_service_account_allowlisted(sa, settings) is False
    with pytest.raises(OrgScopeDeniedError):
        OrgUnitGuard(settings).enforce(sa, "OU-A")


# --- Resolver ---------------------------------------------------------------


def test_resolver_normalize() -> None:
    assert OrgUnitResolver.normalize("  OU-A  ") == "OU-A"
    assert OrgUnitResolver.normalize("") is None
    assert OrgUnitResolver.normalize(None) is None


def test_resolver_declared() -> None:
    session = MagicMock()
    resolver = OrgUnitResolver(session)
    assert resolver.resolve_declared("OU-SIT-01") == "OU-SIT-01"
    assert resolver.resolve_declared("  ") is None


def test_resolver_complaint_uses_branch_code() -> None:
    complaint_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    complaint = MagicMock()
    complaint.deleted_at = None
    complaint.branch_id = branch_id
    branch = MagicMock()
    branch.deleted_at = None
    branch.code = "OU-JKT-01"

    session = MagicMock()

    def _get(model: object, key: object) -> object | None:
        if key == complaint_id:
            return complaint
        if key == branch_id:
            return branch
        return None

    session.get.side_effect = _get
    assert OrgUnitResolver(session).resolve_complaint(complaint_id) == "OU-JKT-01"


def test_resolver_complaint_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        OrgUnitResolver(session).resolve_complaint(uuid.uuid4())


def test_resolver_cm_complaint_from_outbox_payload() -> None:
    complaint_id = uuid.uuid4()
    cm_row = MagicMock(spec=CmBatch1ComplaintORM)
    cm_row.id = complaint_id
    cm_row.owning_unit_id = None

    session = MagicMock()
    session.get.return_value = cm_row
    session.scalar.return_value = json.dumps(
        {
            "complaintId": str(complaint_id),
            "recordingUnitId": "OU-SIT-01",
            "createdBy": str(uuid.uuid4()),
        }
    )
    assert OrgUnitResolver(session).resolve_cm_complaint(complaint_id) == "OU-SIT-01"


def test_resolver_cm_complaint_prefers_owning_unit_column() -> None:
    complaint_id = uuid.uuid4()
    cm_row = MagicMock(spec=CmBatch1ComplaintORM)
    cm_row.id = complaint_id
    cm_row.owning_unit_id = "OU-COLUMN-01"

    session = MagicMock()
    session.get.return_value = cm_row
    session.scalar.return_value = json.dumps({"recordingUnitId": "OU-OUTBOX-01"})
    assert OrgUnitResolver(session).resolve_cm_complaint(complaint_id) == "OU-COLUMN-01"
    session.scalar.assert_not_called()


def test_resolver_cm_complaint_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        OrgUnitResolver(session).resolve_cm_complaint(uuid.uuid4())


def test_resolver_case_uses_owning_unit_id() -> None:
    """P0 gap closure: CAP-008 Case (Aggregate) org scope, by id or case number."""
    case_id = uuid.uuid4()
    case_row = MagicMock()
    case_row.owning_unit_id = "OU-CASE-01"

    session = MagicMock()
    session.get.return_value = case_row
    assert OrgUnitResolver(session).resolve_case(str(case_id)) == "OU-CASE-01"

    # Fallback to case_number lookup (SqlAlchemyCaseRepository.get parity).
    session_by_number = MagicMock()
    session_by_number.get.return_value = None
    session_by_number.scalar.return_value = case_row
    assert (
        OrgUnitResolver(session_by_number).resolve_case("CASE-2026-000001")
        == "OU-CASE-01"
    )


def test_resolver_case_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    session.scalar.return_value = None
    with pytest.raises(NotFoundError):
        OrgUnitResolver(session).resolve_case(str(uuid.uuid4()))


def test_resolver_escalation_uses_parent_complaint() -> None:
    """P0 gap closure: escalation → parent Complaint → Branch.code."""
    escalation_id = uuid.uuid4()
    complaint_id = uuid.uuid4()
    branch_id = uuid.uuid4()

    escalation_row = MagicMock()
    escalation_row.deleted_at = None
    escalation_row.complaint_id = complaint_id

    complaint = MagicMock()
    complaint.deleted_at = None
    complaint.branch_id = branch_id
    branch = MagicMock()
    branch.deleted_at = None
    branch.code = "OU-ESC-01"

    session = MagicMock()

    def _get(model: object, key: object) -> object | None:
        if key == escalation_id:
            return escalation_row
        if key == complaint_id:
            return complaint
        if key == branch_id:
            return branch
        return None

    session.get.side_effect = _get
    assert OrgUnitResolver(session).resolve_escalation(escalation_id) == "OU-ESC-01"


def test_resolver_escalation_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        OrgUnitResolver(session).resolve_escalation(uuid.uuid4())


# --- HTTP integration (M-4) -------------------------------------------------


def _complaint_response(complaint_id: uuid.UUID) -> MagicMock:
    now = datetime.now(UTC)
    resp = MagicMock()
    resp.id = complaint_id
    resp.model_dump = MagicMock(
        return_value={
            "id": str(complaint_id),
            "complaintNumber": "CMP-TEST",
            "status": "IN_PROGRESS",
            "subject": "s",
            "description": "d",
            "priority": "MEDIUM",
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
    )
    # Pydantic response_model will re-validate; return a simple namespace-like
    # object only works if we bypass response validation — use real schema.
    return resp


@pytest.fixture()
def org_http_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """HTTP TestClient with jwt org-scope settings + stubbed services."""
    settings = _jwt_settings()
    monkeypatch.setattr(
        "app.modules.complaints.router.get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        "app.modules.assignments.router.get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        "app.modules.cm_batch1.router.get_settings",
        lambda: settings,
    )
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings",
        lambda: settings,
    )

    complaint_id = uuid.uuid4()
    replay_complaint_id = uuid.uuid4()
    resource_org_by_id: dict[str, str] = {
        str(complaint_id): "OU-A",
        str(replay_complaint_id): "OU-B",
    }

    def _resolve_complaint(_self: OrgUnitResolver, cid: uuid.UUID) -> str | None:
        key = str(cid)
        if key not in resource_org_by_id:
            raise NotFoundError("Complaint not found")
        return resource_org_by_id[key]

    def _resolve_cm(_self: OrgUnitResolver, cid: str | uuid.UUID) -> str | None:
        key = str(cid).strip()
        if key not in resource_org_by_id:
            raise NotFoundError("Complaint not found")
        return resource_org_by_id[key]

    monkeypatch.setattr(OrgUnitResolver, "resolve_complaint", _resolve_complaint)
    monkeypatch.setattr(OrgUnitResolver, "resolve_cm_complaint", _resolve_cm)
    monkeypatch.setattr(
        OrgUnitResolver,
        "resolve_declared",
        lambda _self, value: OrgUnitResolver.normalize(value),
    )

    from app.core.enums import ComplaintStatus
    from app.modules.complaints.schemas import (
        CloseComplaintResult,
        ComplaintResponse,
    )

    now = datetime.now(UTC)

    def _full_complaint(cid: uuid.UUID) -> ComplaintResponse:
        return ComplaintResponse.model_validate(
            {
                "id": cid,
                "complaintNumber": "CMP-ORG-001",
                "status": ComplaintStatus.IN_PROGRESS,
                "subject": "org-scope",
                "description": "test",
                "priority": "MEDIUM",
                "sourceType": "CUSTOMER",
                "sourceId": uuid.uuid4(),
                "targetType": "BRANCH",
                "targetId": uuid.uuid4(),
                "customerId": uuid.uuid4(),
                "reportedAt": now,
                "createdAt": now,
                "updatedAt": now,
            }
        )

    complaint_svc = MagicMock()
    complaint_svc.get.side_effect = lambda cid: _full_complaint(cid)
    complaint_svc.update.side_effect = lambda cid, payload, actor_user_id: _full_complaint(
        cid
    )
    complaint_svc.close.side_effect = lambda cid, payload, actor_user_id: CloseComplaintResult(
        complaintId=cid,
        status=ComplaintStatus.CLOSED,
        closedAt=now,
        closedBy=actor_user_id,
    )
    complaint_svc.change_status.side_effect = (
        lambda cid, payload, actor_user_id: _full_complaint(cid)
    )

    assignment_svc = MagicMock()
    assignment_svc.list_assignments.return_value = []

    cm_store: dict[str, Any] = {
        "replay_org": "OU-B",
        "created_org": "OU-A",
        # Pre-seed for FIX 2 peek: Replay key maps to OU-B owned aggregate.
        "idempotent": {
            "replay-key": str(replay_complaint_id),
        },
        "commits": 0,
        "outbox_events": [],
    }

    class _CmService:
        def peek_idempotent(self, request_id: str) -> str | None:
            return cm_store["idempotent"].get(request_id.strip())

        def peek_by_channel_message(self, message_id: str) -> str | None:
            return None

        def create_complaint(self, body: Any, **kwargs: Any) -> ComplaintBatch1Response:
            # Replay path returns resource owned by cm_store["replay_org"].
            rid = kwargs.get("request_id") or ""
            authorize = kwargs.get("authorize_replay")
            if rid in cm_store["idempotent"]:
                cid = uuid.UUID(cm_store["idempotent"][rid])
                resource_org_by_id[str(cid)] = cm_store["replay_org"]
                if authorize is not None:
                    authorize(str(cid))
                cm_store["commits"] += 1
                cm_store["outbox_events"].append("ComplaintCreateReplayed")
                return ComplaintBatch1Response(
                    complaintId=str(cid),
                    complaintNumber="CMP-REPLAY",
                    status="REGISTERED",
                    customerId="CUST-1",
                    caseCreated=False,
                    replayed=True,
                )
            cid = uuid.uuid4()
            resource_org_by_id[str(cid)] = OrgUnitResolver.normalize(
                getattr(body, "recording_unit_id", None)
            ) or cm_store["created_org"]
            cm_store["commits"] += 1
            cm_store["outbox_events"].append("ComplaintCreated")
            return ComplaintBatch1Response(
                complaintId=str(cid),
                complaintNumber="CMP-NEW",
                status="REGISTERED",
                customerId=getattr(body, "customer_id", "CUST-1") or "CUST-1",
                caseCreated=False,
                replayed=False,
            )

        def get_complaint(self, cid: str) -> ComplaintBatch1Response:
            return ComplaintBatch1Response(
                complaintId=cid,
                complaintNumber="CMP-GET",
                status="REGISTERED",
                customerId="CUST-1",
                caseCreated=False,
                replayed=False,
            )

        def record_duplicate_decision(
            self, body: Any, *, actor_id: str | None = None
        ) -> DuplicateDecisionResponse:
            _ = actor_id
            cm_store["commits"] += 1
            cm_store["outbox_events"].append("DuplicateDecisionRecorded")
            return DuplicateDecisionResponse(
                decisionId=str(uuid.uuid4()),
                decision=body.decision,
                customerId=getattr(body, "customer_id", None) or "CUST-1",
                survivingComplaintId=getattr(body, "surviving_complaint_id", None),
                warning=True,
                hardBlock=False,
                caseCreated=False,
                policyVersion="cm-batch1-dup-v1",
                createdAt=datetime.now(UTC),
            )

    class _TrackingAttachments:
        def __init__(self) -> None:
            self.transfer_calls = 0
            self.commits = 0

        def bind_staging_to_complaint(self, **kwargs: Any) -> None:
            return None

        def transfer(self, body: Any, *, actor_id: str | None = None) -> Any:
            _ = actor_id
            self.transfer_calls += 1
            self.commits += 1
            cm_store["commits"] += 1
            cm_store["outbox_events"].append("AttachmentTransferred")
            return TransferAttachmentsResponse(
                stagingToken=body.staging_token,
                survivingComplaintId=body.surviving_complaint_id,
                transferredCount=1,
                attachments=[],
                discarded=False,
            )

    app = create_app()
    session = MagicMock()
    attachments_svc = _TrackingAttachments()

    def _session_dep() -> Any:
        yield session

    state: dict[str, Principal] = {
        "principal": _principal(org_unit_id="OU-A"),
    }

    app.dependency_overrides[get_db_session] = _session_dep
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_complaint_service] = lambda: complaint_svc
    app.dependency_overrides[get_assignment_service] = lambda: assignment_svc
    app.dependency_overrides[get_cm_batch1_service] = lambda: _CmService()
    app.dependency_overrides[get_cm_batch1_attachment_service] = (
        lambda: attachments_svc
    )

    client = TestClient(app)
    try:
        yield {
            "client": client,
            "settings": settings,
            "state": state,
            "complaint_id": complaint_id,
            "replay_complaint_id": replay_complaint_id,
            "resource_org_by_id": resource_org_by_id,
            "cm_store": cm_store,
            "attachments": attachments_svc,
        }
    finally:
        app.dependency_overrides.clear()
        client.close()


def test_http_same_unit_get_allows(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    resp = client.get(f"/api/v1/complaints/{cid}")
    assert resp.status_code == 200


def test_http_cross_unit_get_denied(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-B")
    resp = client.get(f"/api/v1/complaints/{cid}")
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "ORG_SCOPE_DENIED"
    details = body.get("details") or {}
    assert details.get("reason") == "org_unit_mismatch"
    assert "resourceOrgUnitId" not in details


def test_http_missing_claim_denied(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["state"]["principal"] = _principal(org_unit_id=None)
    resp = client.get(f"/api/v1/complaints/{cid}")
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert resp.json()["details"]["reason"] == "missing_org_unit_claim"


def test_http_close_endpoint_org_guard(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    # Cross-unit close denied.
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-B")
    denied = client.post(
        f"/api/v1/complaints/{cid}/close",
        json={"notes": "closing notes for org scope"},
    )
    assert denied.status_code == 403
    assert denied.json()["code"] == "ORG_SCOPE_DENIED"

    # Same-unit close allowed.
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    allowed = client.post(
        f"/api/v1/complaints/{cid}/close",
        json={"notes": "closing notes for org scope"},
    )
    assert allowed.status_code == 200


def test_http_update_endpoint_org_guard(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-B")
    denied = client.put(
        f"/api/v1/complaints/{cid}",
        json={"subject": "updated subject"},
    )
    assert denied.status_code == 403
    assert denied.json()["code"] == "ORG_SCOPE_DENIED"

    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    allowed = client.put(
        f"/api/v1/complaints/{cid}",
        json={"subject": "updated subject"},
    )
    assert allowed.status_code == 200


def test_http_assignments_read_org_guard(org_http_client: dict[str, Any]) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-B")
    denied = client.get(f"/api/v1/complaints/{cid}/assignments")
    assert denied.status_code == 403
    assert denied.json()["code"] == "ORG_SCOPE_DENIED"

    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    allowed = client.get(f"/api/v1/complaints/{cid}/assignments")
    assert allowed.status_code == 200


def test_http_idempotent_replay_validates_actual_resource(
    org_http_client: dict[str, Any],
) -> None:
    """C-3 + FIX 2: declared OU-A must not authorize replay of OU-B owned aggregate.

    Denied replay MUST NOT commit and MUST NOT write outbox events.
    """
    client: TestClient = org_http_client["client"]
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    org_http_client["cm_store"]["replay_org"] = "OU-B"
    replay_cid = org_http_client["replay_complaint_id"]
    org_http_client["resource_org_by_id"][str(replay_cid)] = "OU-B"
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/complaints",
        headers={"Idempotency-Key": "replay-key"},
        json={
            "customerId": "CUST-1",
            "category": "CAT",
            "channel": "WEB",
            "subject": "replay",
            "description": "idempotent cross-unit probe",
            "recordingUnitId": "OU-A",
        },
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "ORG_SCOPE_DENIED"
    assert "resourceOrgUnitId" not in (body.get("details") or {})
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_attachment_transfer_same_unit_allowed(
    org_http_client: dict[str, Any],
) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-A"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")

    resp = client.post(
        "/api/v1/cm/attachments/transfer",
        json={
            "stagingToken": "STG-ORG-SAME",
            "survivingComplaintId": str(cid),
        },
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["discarded"] is False
    assert org_http_client["attachments"].transfer_calls == 1


def test_http_attachment_transfer_cross_unit_denied(
    org_http_client: dict[str, Any],
) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-B"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/attachments/transfer",
        json={
            "stagingToken": "STG-ORG-CROSS",
            "survivingComplaintId": str(cid),
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert org_http_client["attachments"].transfer_calls == 0
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_duplicate_decision_transfer_same_unit_allowed(
    org_http_client: dict[str, Any],
) -> None:
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-A"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")

    resp = client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "link_existing",
            "survivingComplaintId": str(cid),
            "stagingToken": "STG-DUP-SAME",
            "customerId": "CUST-1",
        },
    )
    assert resp.status_code == 200
    assert org_http_client["attachments"].transfer_calls == 1
    assert "DuplicateDecisionRecorded" in org_http_client["cm_store"]["outbox_events"]
    assert "AttachmentTransferred" in org_http_client["cm_store"]["outbox_events"]


def test_http_duplicate_decision_transfer_cross_unit_denied_no_commit(
    org_http_client: dict[str, Any],
) -> None:
    """FIX 1+2: cross-unit D-06 transfer via decisions → 403, no commit/outbox."""
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-B"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "link_existing",
            "survivingComplaintId": str(cid),
            "stagingToken": "STG-DUP-CROSS",
            "customerId": "CUST-1",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert org_http_client["attachments"].transfer_calls == 0
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_link_existing_without_staging_cross_unit_denied_no_commit(
    org_http_client: dict[str, Any],
) -> None:
    """CR-1: link_existing without stagingToken still requires org scope."""
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-B"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "link_existing",
            "survivingComplaintId": str(cid),
            "customerId": "CUST-1",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert org_http_client["attachments"].transfer_calls == 0
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_blocked_with_surviving_cross_unit_denied_no_commit(
    org_http_client: dict[str, Any],
) -> None:
    """CR-1: blocked + survivingComplaintId must pass OrgUnitGuard."""
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-B"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "blocked",
            "survivingComplaintId": str(cid),
            "customerId": "CUST-1",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_recommend_only_with_surviving_cross_unit_denied_no_commit(
    org_http_client: dict[str, Any],
) -> None:
    """CR-1: recommend_only + survivingComplaintId must pass OrgUnitGuard."""
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-B"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")
    before_commits = org_http_client["cm_store"]["commits"]
    before_outbox = list(org_http_client["cm_store"]["outbox_events"])

    resp = client.post(
        "/api/v1/cm/duplicates/decisions",
        json={
            "decision": "recommend_only",
            "survivingComplaintId": str(cid),
            "customerId": "CUST-1",
        },
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "ORG_SCOPE_DENIED"
    assert org_http_client["cm_store"]["commits"] == before_commits
    assert org_http_client["cm_store"]["outbox_events"] == before_outbox


def test_http_duplicate_decision_surviving_same_unit_succeeds(
    org_http_client: dict[str, Any],
) -> None:
    """Regression: same-unit survivingComplaintId decisions still succeed."""
    client: TestClient = org_http_client["client"]
    cid = org_http_client["complaint_id"]
    org_http_client["resource_org_by_id"][str(cid)] = "OU-A"
    org_http_client["state"]["principal"] = _principal(org_unit_id="OU-A")

    for decision in ("link_existing", "blocked", "recommend_only"):
        org_http_client["cm_store"]["commits"] = 0
        org_http_client["cm_store"]["outbox_events"].clear()
        org_http_client["attachments"].transfer_calls = 0
        payload: dict[str, Any] = {
            "decision": decision,
            "survivingComplaintId": str(cid),
            "customerId": "CUST-1",
        }
        resp = client.post("/api/v1/cm/duplicates/decisions", json=payload)
        assert resp.status_code == 200, f"{decision}: {resp.text}"
        assert "DuplicateDecisionRecorded" in org_http_client["cm_store"]["outbox_events"]
        assert org_http_client["attachments"].transfer_calls == 0
        assert org_http_client["cm_store"]["commits"] >= 1


# --- P0 attachment ownership gap closure ------------------------------------


def _attachment_entity(*, aggregate_type: str, aggregate_id: uuid.UUID) -> Any:
    from app.modules.attachment.domain.entity import Attachment as AttachmentEntity

    return AttachmentEntity(
        id=uuid.uuid4(),
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        file_name="f.pdf",
        original_name="f.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=4,
        storage_provider="local",
        storage_path="f.pdf",
        checksum_sha256="abc",
        uploaded_by=None,
    )


def test_download_attachment_cross_unit_denied_for_complaint_aggregate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.attachment.router import download_attachment

    entity = _attachment_entity(aggregate_type="Complaint", aggregate_id=uuid.uuid4())
    service = MagicMock()
    service.download.return_value = (entity, b"data")
    batch1 = MagicMock()
    batch1.try_get_by_platform_id.return_value = None
    batch1.try_get.return_value = None
    batch1.resolve_platform_attachment_id.side_effect = lambda aid: aid

    monkeypatch.setattr(OrgUnitResolver, "resolve_complaint", lambda self, cid: "OU-A")
    settings = _jwt_settings()
    principal = _principal(org_unit_id="OU-B")

    with pytest.raises(OrgScopeDeniedError):
        download_attachment(uuid.uuid4(), service, batch1, principal, MagicMock(), settings)


def test_download_attachment_same_unit_allowed_for_complaint_aggregate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.attachment.router import download_attachment

    entity = _attachment_entity(aggregate_type="Complaint", aggregate_id=uuid.uuid4())
    service = MagicMock()
    service.download.return_value = (entity, b"data")
    batch1 = MagicMock()
    batch1.try_get_by_platform_id.return_value = None
    batch1.try_get.return_value = None
    batch1.resolve_platform_attachment_id.side_effect = lambda aid: aid

    monkeypatch.setattr(OrgUnitResolver, "resolve_complaint", lambda self, cid: "OU-A")
    settings = _jwt_settings()
    principal = _principal(org_unit_id="OU-A")

    resp = download_attachment(
        uuid.uuid4(), service, batch1, principal, MagicMock(), settings
    )
    assert resp.body == b"data"


def test_download_attachment_batch1_linked_cross_unit_denied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.attachment.router import download_attachment

    entity = _attachment_entity(aggregate_type="Complaint", aggregate_id=uuid.uuid4())
    service = MagicMock()
    service.download.return_value = (entity, b"data")
    linked = MagicMock()
    linked.complaint_id = str(uuid.uuid4())
    batch1 = MagicMock()
    batch1.try_get_by_platform_id.return_value = linked
    batch1.resolve_platform_attachment_id.side_effect = lambda aid: aid

    monkeypatch.setattr(OrgUnitResolver, "resolve_cm_complaint", lambda self, cid: "OU-A")
    settings = _jwt_settings()
    principal = _principal(org_unit_id="OU-B")

    with pytest.raises(OrgScopeDeniedError):
        download_attachment(uuid.uuid4(), service, batch1, principal, MagicMock(), settings)


def test_download_attachment_not_a_real_complaint_skips_enforcement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CAPABILITY-011 is aggregate-agnostic (no FK to Complaint) — an
    ``aggregate_id`` with no real Complaint row must not block download."""
    from app.modules.attachment.router import download_attachment

    entity = _attachment_entity(aggregate_type="Complaint", aggregate_id=uuid.uuid4())
    service = MagicMock()
    service.download.return_value = (entity, b"data")
    batch1 = MagicMock()
    batch1.try_get_by_platform_id.return_value = None
    batch1.try_get.return_value = None
    batch1.resolve_platform_attachment_id.side_effect = lambda aid: aid

    def _raise_not_found(self: OrgUnitResolver, cid: uuid.UUID) -> str | None:
        raise NotFoundError("Complaint not found")

    monkeypatch.setattr(OrgUnitResolver, "resolve_complaint", _raise_not_found)
    settings = _jwt_settings()
    principal = _principal(org_unit_id="OU-B")

    resp = download_attachment(
        uuid.uuid4(), service, batch1, principal, MagicMock(), settings
    )
    assert resp.body == b"data"


# --- UX-CU-002 R2 — users:create Unit-scope guard reuse -----------------------


class _StubUserService:
    """Returns the declared payload verbatim — service.create() is not under test here."""

    def create(self, payload: Any, *, actor_user_id: uuid.UUID, actor_roles: Any) -> UserResponse:
        _ = actor_user_id, actor_roles
        now = datetime.now(UTC)
        return UserResponse.model_validate(
            {
                "id": uuid.uuid4(),
                "username": payload.username,
                "email": payload.email,
                "fullName": payload.full_name,
                "roleId": payload.role_id,
                "branchId": payload.branch_id,
                "isActive": payload.is_active,
                "forcePasswordChange": True,
                "createdAt": now,
                "updatedAt": now,
            }
        )


class _BranchLookupSession:
    """Fake session — only ``.get(Branch, id)`` is exercised by the users router."""

    def __init__(self, branches: dict[uuid.UUID, str]) -> None:
        self._branches = branches

    def get(self, model: type, key: object) -> Any:
        if model is Branch and key in self._branches:
            return SimpleNamespace(id=key, code=self._branches[key], deleted_at=None)
        return None


@pytest.fixture()
def users_http_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """HTTP TestClient for POST /api/v1/users with jwt org-scope settings."""
    settings = _jwt_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )

    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    session = _BranchLookupSession({branch_a: "OU-A", branch_b: "OU-B"})

    app = create_app()
    state: dict[str, Any] = {
        "principal": _principal(
            org_unit_id="OU-A",
            roles=("ADMIN",),
            permissions=frozenset({"users:create"}),
        )
    }
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: _StubUserService()
    client = TestClient(app)
    try:
        yield {
            "client": client,
            "state": state,
            "branch_a": branch_a,
            "branch_b": branch_b,
        }
    finally:
        app.dependency_overrides.clear()
        client.close()


def _create_user_payload(branch_id: uuid.UUID | None) -> dict[str, Any]:
    return {
        "username": "new.agent",
        "email": "new.agent@example.com",
        "fullName": "New Agent",
        "password": "Sementara123!",
        "roleId": str(uuid.uuid4()),
        "branchId": str(branch_id) if branch_id else None,
        "isActive": True,
    }


def test_http_create_user_same_unit_allowed(users_http_client: dict[str, Any]) -> None:
    client: TestClient = users_http_client["client"]
    resp = client.post(
        "/api/v1/users", json=_create_user_payload(users_http_client["branch_a"])
    )
    assert resp.status_code == 201, resp.text


def test_http_create_user_cross_unit_denied(users_http_client: dict[str, Any]) -> None:
    """T-1 (UX-CU-002 §6) — admin scoped to OU-A must not place a user in OU-B."""
    client: TestClient = users_http_client["client"]
    resp = client.post(
        "/api/v1/users", json=_create_user_payload(users_http_client["branch_b"])
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "ORG_SCOPE_DENIED"
    assert body["details"]["reason"] == "org_unit_mismatch"


def test_http_create_user_missing_admin_claim_denied(
    users_http_client: dict[str, Any],
) -> None:
    client: TestClient = users_http_client["client"]
    users_http_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:create"}),
    )
    resp = client.post(
        "/api/v1/users", json=_create_user_payload(users_http_client["branch_a"])
    )
    assert resp.status_code == 403
    assert resp.json()["details"]["reason"] == "missing_org_unit_claim"


def test_http_create_user_head_office_role_denied_when_enforced(
    users_http_client: dict[str, Any],
) -> None:
    """Known consequence (see UX-CU-002 follow-up): OrgUnitGuard has no GLOBAL/HQ
    bypass, so a declared-unit-less (head-office) create is denied once org-scope
    enforcement is on — identical to how cm_batch1's optional recordingUnitId
    already behaves. Not a new rule introduced by this change; documented here so
    the behavior is explicit and covered rather than discovered later."""
    client: TestClient = users_http_client["client"]
    resp = client.post("/api/v1/users", json=_create_user_payload(None))
    assert resp.status_code == 403
    assert resp.json()["details"]["reason"] == "missing_resource_org_unit"


def test_http_create_user_org_scope_noop_in_dev_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression — Mode A (dev) must behave exactly as before this change."""
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    session = _BranchLookupSession({branch_a: "OU-A", branch_b: "OU-B"})

    app = create_app()
    principal = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:create"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: _StubUserService()
    client = TestClient(app)
    try:
        # Cross-unit and missing-claim cases that would 403 under jwt mode
        # must both succeed here — org-scope enforcement is jwt-mode only.
        resp = client.post("/api/v1/users", json=_create_user_payload(branch_b))
        assert resp.status_code == 201, resp.text
    finally:
        app.dependency_overrides.clear()
        client.close()


# --- UM-SEC-001 — users:read (list) and users:update (status) scope reuse ---


class _UsersScopeSession:
    """Fake session for the list/status scope tests — no real DB involved.

    Supports the two lookup shapes the router actually issues: ``session.get``
    (Branch, User — same pattern OrgUnitResolver already uses elsewhere) and
    the single ``session.scalar(select(Branch.id).where(Branch.code == ...))``
    call used to resolve an admin's own branch id when no ``branchId`` filter
    was supplied.
    """

    def __init__(
        self,
        *,
        branches_by_id: dict[uuid.UUID, Any] | None = None,
        users_by_id: dict[uuid.UUID, Any] | None = None,
        branch_id_by_code: dict[str, uuid.UUID] | None = None,
    ) -> None:
        self._branches_by_id = branches_by_id or {}
        self._users_by_id = users_by_id or {}
        self._branch_id_by_code = branch_id_by_code or {}

    def get(self, model: type, key: object) -> Any:
        if model is Branch:
            return self._branches_by_id.get(key)
        if model is User:
            return self._users_by_id.get(key)
        return None

    def scalar(self, stmt: Any) -> Any:
        code = stmt.whereclause.right.value
        return self._branch_id_by_code.get(code)


def _fake_branch(branch_id: uuid.UUID, code: str) -> SimpleNamespace:
    return SimpleNamespace(id=branch_id, code=code, deleted_at=None)


def _fake_member(user_id: uuid.UUID, branch_id: uuid.UUID | None) -> SimpleNamespace:
    return SimpleNamespace(id=user_id, branch_id=branch_id, deleted_at=None)


def _fake_user_response(**overrides: Any) -> UserResponse:
    now = datetime.now(UTC)
    base: dict[str, Any] = {
        "id": uuid.uuid4(),
        "username": "member.one",
        "email": "member.one@example.com",
        "fullName": "Member One",
        "roleId": uuid.uuid4(),
        "isActive": True,
        "createdAt": now,
        "updatedAt": now,
    }
    base.update(overrides)
    return UserResponse.model_validate(base)


@pytest.fixture()
def users_scope_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """HTTP TestClient covering GET /users and PATCH /users/{id}/status."""
    settings = _jwt_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )

    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    member_in_a = uuid.uuid4()
    member_in_b = uuid.uuid4()
    member_head_office = uuid.uuid4()

    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={
            member_in_a: _fake_member(member_in_a, branch_a),
            member_in_b: _fake_member(member_in_b, branch_b),
            member_head_office: _fake_member(member_head_office, None),
        },
        branch_id_by_code={"OU-A": branch_a, "OU-B": branch_b},
    )

    list_service = MagicMock()
    list_service.list.return_value = ([], 0)
    list_service.update_status.return_value = _fake_user_response()
    list_service.get.return_value = _fake_user_response()

    app = create_app()
    state: dict[str, Any] = {
        "principal": _principal(
            org_unit_id="OU-A",
            roles=("ADMIN",),
            permissions=frozenset({"users:read", "users:update"}),
        )
    }
    app.dependency_overrides[get_current_principal] = lambda: state["principal"]
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: list_service
    client = TestClient(app)
    try:
        yield {
            "client": client,
            "state": state,
            "service": list_service,
            "branch_a": branch_a,
            "branch_b": branch_b,
            "member_in_a": member_in_a,
            "member_in_b": member_in_b,
            "member_head_office": member_head_office,
        }
    finally:
        app.dependency_overrides.clear()
        client.close()


# --- List (TASK 1 / TASK 2 / TASK 7 — Regional/Branch cannot read another Unit) ---


def test_http_list_users_branch_admin_defaults_to_own_unit(
    users_scope_client: dict[str, Any],
) -> None:
    """No branchId filter supplied → silently narrowed to the admin's own unit."""
    client: TestClient = users_scope_client["client"]
    resp = client.get("/api/v1/users")
    assert resp.status_code == 200, resp.text
    kwargs = users_scope_client["service"].list.call_args.kwargs
    assert kwargs["branch_id"] == users_scope_client["branch_a"]


def test_http_list_users_branch_admin_same_unit_explicit_allowed(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    resp = client.get(
        "/api/v1/users", params={"branchId": str(users_scope_client["branch_a"])}
    )
    assert resp.status_code == 200, resp.text
    kwargs = users_scope_client["service"].list.call_args.kwargs
    assert kwargs["branch_id"] == users_scope_client["branch_a"]


def test_http_list_users_branch_admin_cross_unit_denied(
    users_scope_client: dict[str, Any],
) -> None:
    """T-1-class read: Regional/Branch admin cannot ask to see another Unit."""
    client: TestClient = users_scope_client["client"]
    resp = client.get(
        "/api/v1/users", params={"branchId": str(users_scope_client["branch_b"])}
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "ORG_SCOPE_DENIED"
    assert body["details"]["reason"] == "org_unit_mismatch"
    users_scope_client["service"].list.assert_not_called()


def test_http_list_users_head_office_unrestricted(
    users_scope_client: dict[str, Any],
) -> None:
    """Documented open gap (UX-UM-001 §8.1): no repo rule yet says whether
    head-office-scoped roles should be GLOBAL-scoped for list reads, so the
    endpoint's pre-existing unrestricted behavior is preserved for them
    rather than 403ing every head-office administrator off the member list."""
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:read"}),
    )
    resp = client.get("/api/v1/users")
    assert resp.status_code == 200, resp.text
    kwargs = users_scope_client["service"].list.call_args.kwargs
    assert kwargs["branch_id"] is None


def test_http_list_users_explicit_cross_unit_still_open_in_dev_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Narrower, still-open gap: an explicit ?branchId= override is only
    denied under org_scope_enforcement_enabled (jwt mode). Unlike the
    unfiltered case (see test_http_list_users_dev_mode_defaults_to_own_unit
    below), this path is untouched by UM-BUG-005."""
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        branch_id_by_code={"OU-A": branch_a, "OU-B": branch_b},
    )
    service = MagicMock()
    service.list.return_value = ([], 0)

    app = create_app()
    principal = _principal(
        org_unit_id="OU-A", roles=("ADMIN",), permissions=frozenset({"users:read"})
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.get("/api/v1/users", params={"branchId": str(branch_b)})
        assert resp.status_code == 200, resp.text
        assert service.list.call_args.kwargs["branch_id"] == branch_b
    finally:
        app.dependency_overrides.clear()
        client.close()


def test_http_list_users_dev_mode_defaults_to_own_unit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """UM-BUG-005 — Mode A issues no orgUnitId claim, so a branch-scoped
    principal (Supervisor et al.) must still be narrowed to their own unit
    when no ?branchId= is supplied, sourced from the DB membership record
    instead of a claim (see resolve_principal_membership)."""
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    supervisor_id = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={supervisor_id: _fake_member(supervisor_id, branch_a)},
        branch_id_by_code={"OU-A": branch_a, "OU-B": branch_b},
    )
    service = MagicMock()
    service.list.return_value = ([], 0)

    app = create_app()
    # No org_unit_id claim — dev mode never issues one.
    principal = _principal(
        user_id=supervisor_id,
        org_unit_id=None,
        roles=("SUPERVISOR",),
        permissions=frozenset({"users:read"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.get("/api/v1/users")
        assert resp.status_code == 200, resp.text
        assert service.list.call_args.kwargs["branch_id"] == branch_a
    finally:
        app.dependency_overrides.clear()
        client.close()


def test_http_list_users_dev_mode_head_office_unrestricted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No-branch membership (Head Office / admin) stays unrestricted in dev
    mode too — same open gap as the jwt-mode case, not a new bypass."""
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    admin_id = uuid.uuid4()
    session = _UsersScopeSession(users_by_id={admin_id: _fake_member(admin_id, None)})
    service = MagicMock()
    service.list.return_value = ([], 0)

    app = create_app()
    principal = _principal(
        user_id=admin_id,
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:read"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.get("/api/v1/users")
        assert resp.status_code == 200, resp.text
        assert service.list.call_args.kwargs["branch_id"] is None
    finally:
        app.dependency_overrides.clear()
        client.close()


# --- Status update (TASK 3 / TASK 7 — Regional/Branch cannot activate/deactivate another Unit) ---


def test_http_update_status_branch_role_denied_even_same_unit(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id="OU-A",
        roles=("SUPERVISOR",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_a']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 403
    users_scope_client["service"].update_status.assert_not_called()


def test_http_update_status_branch_role_denied_cross_unit(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id="OU-A",
        roles=("SUPERVISOR",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_b']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 403
    users_scope_client["service"].update_status.assert_not_called()


def test_http_update_status_manager_same_unit_allowed(
    users_scope_client: dict[str, Any],
) -> None:
    """UM-BUG-007 — Manager (BC-8.4) may activate/deactivate within own unit."""
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id="OU-A",
        roles=("MANAGER",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_a']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 200, resp.text
    users_scope_client["service"].update_status.assert_called_once()


def test_http_update_status_manager_cross_unit_denied(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id="OU-A",
        roles=("MANAGER",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_b']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 403
    users_scope_client["service"].update_status.assert_not_called()


def test_http_update_status_manager_without_branch_denied(
    users_scope_client: dict[str, Any],
) -> None:
    """Fail-closed: a Manager with no resolvable branch manages nobody."""
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("MANAGER",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_a']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 403
    users_scope_client["service"].update_status.assert_not_called()


def test_http_update_status_manager_dev_mode_same_branch_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """UM-BUG-007 in Mode A — no orgUnitId claim, DB membership fallback."""
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    manager_id = uuid.uuid4()
    member_in_a = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={
            manager_id: _fake_member(manager_id, branch_a),
            member_in_a: _fake_member(member_in_a, branch_a),
        },
    )
    service = MagicMock()
    service.update_status.return_value = _fake_user_response()

    app = create_app()
    principal = _principal(
        user_id=manager_id,
        org_unit_id=None,
        roles=("MANAGER",),
        permissions=frozenset({"users:update"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.patch(
            f"/api/v1/users/{member_in_a}/status", json={"isActive": False}
        )
        assert resp.status_code == 200, resp.text
        service.update_status.assert_called_once()
    finally:
        app.dependency_overrides.clear()
        client.close()


def test_http_update_status_manager_dev_mode_cross_branch_denied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    manager_id = uuid.uuid4()
    member_in_b = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={
            manager_id: _fake_member(manager_id, branch_a),
            member_in_b: _fake_member(member_in_b, branch_b),
        },
    )
    service = MagicMock()
    service.update_status.return_value = _fake_user_response()

    app = create_app()
    principal = _principal(
        user_id=manager_id,
        org_unit_id=None,
        roles=("MANAGER",),
        permissions=frozenset({"users:update"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.patch(
            f"/api/v1/users/{member_in_b}/status", json={"isActive": False}
        )
        assert resp.status_code == 403
        service.update_status.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        client.close()


def test_http_update_status_head_office_admin_allowed(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_a']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 200, resp.text
    users_scope_client["service"].update_status.assert_called_once()


def test_http_update_status_super_admin_allowed(
    users_scope_client: dict[str, Any],
) -> None:
    """SUPER_ADMIN is the ADMIN family repo-wide (rbac.py, role_assignment_policy)."""
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("SUPER_ADMIN",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_in_a']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 200, resp.text
    users_scope_client["service"].update_status.assert_called_once()


def test_http_update_status_head_office_admin_can_update_head_office_member(
    users_scope_client: dict[str, Any],
) -> None:
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:update"}),
    )
    resp = client.patch(
        f"/api/v1/users/{users_scope_client['member_head_office']}/status",
        json={"isActive": False},
    )
    assert resp.status_code == 200, resp.text


def test_http_update_status_role_gate_applies_in_dev_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    member_in_b = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={member_in_b: _fake_member(member_in_b, branch_b)},
    )
    service = MagicMock()
    service.update_status.return_value = _fake_user_response()

    app = create_app()
    principal = _principal(
        org_unit_id="OU-A",
        roles=("SUPERVISOR",),
        permissions=frozenset({"users:update"}),
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        resp = client.patch(
            f"/api/v1/users/{member_in_b}/status", json={"isActive": False}
        )
        assert resp.status_code == 403
        service.update_status.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        client.close()


# --- Membership Detail (UM-SEC-002 — GET /users/{id}) -----------------------


def test_http_get_user_same_unit_allowed(users_scope_client: dict[str, Any]) -> None:
    client: TestClient = users_scope_client["client"]
    resp = client.get(f"/api/v1/users/{users_scope_client['member_in_a']}")
    assert resp.status_code == 200, resp.text
    users_scope_client["service"].get.assert_called_once_with(
        users_scope_client["member_in_a"]
    )


def test_http_get_user_cross_unit_denied(users_scope_client: dict[str, Any]) -> None:
    """T-1-class read: Regional/Branch admin cannot view another Unit's
    Membership Detail."""
    client: TestClient = users_scope_client["client"]
    resp = client.get(f"/api/v1/users/{users_scope_client['member_in_b']}")
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == "ORG_SCOPE_DENIED"
    assert body["details"]["reason"] == "org_unit_mismatch"
    users_scope_client["service"].get.assert_not_called()


def test_http_get_user_missing_admin_claim_denied(
    users_scope_client: dict[str, Any],
) -> None:
    """Missing authorization claim — same fail-closed reason code already
    used by users:create and the status-update endpoint."""
    client: TestClient = users_scope_client["client"]
    users_scope_client["state"]["principal"] = _principal(
        org_unit_id=None,
        roles=("ADMIN",),
        permissions=frozenset({"users:read"}),
    )
    resp = client.get(f"/api/v1/users/{users_scope_client['member_in_a']}")
    assert resp.status_code == 403
    assert resp.json()["details"]["reason"] == "missing_org_unit_claim"
    users_scope_client["service"].get.assert_not_called()


def test_http_get_user_head_office_target_denied_for_branch_admin(
    users_scope_client: dict[str, Any],
) -> None:
    """Document only (TASK 4): repository does not define a Head Office
    bypass for single-resource actions — it never has, for any endpoint this
    milestone or UM-SEC-001 touched. OrgUnitGuard's existing, already-shipped
    fail-closed behavior is reused unmodified: a head-office member (no
    branch) is not "in" any admin's unit, so viewing them is denied exactly
    like updating their status already is (UM-SEC-001)."""
    client: TestClient = users_scope_client["client"]
    resp = client.get(f"/api/v1/users/{users_scope_client['member_head_office']}")
    assert resp.status_code == 403
    assert resp.json()["details"]["reason"] == "missing_resource_org_unit"


def test_http_get_user_org_scope_noop_in_dev_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _dev_settings()
    monkeypatch.setattr("app.modules.users.router.get_settings", lambda: settings)
    monkeypatch.setattr(
        "app.core.authorization.org_unit_guard.get_settings", lambda: settings
    )
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    member_in_b = uuid.uuid4()
    session = _UsersScopeSession(
        branches_by_id={
            branch_a: _fake_branch(branch_a, "OU-A"),
            branch_b: _fake_branch(branch_b, "OU-B"),
        },
        users_by_id={member_in_b: _fake_member(member_in_b, branch_b)},
    )
    service = MagicMock()
    service.get.return_value = _fake_user_response()

    app = create_app()
    principal = _principal(
        org_unit_id="OU-A", roles=("ADMIN",), permissions=frozenset({"users:read"})
    )
    app.dependency_overrides[get_current_principal] = lambda: principal
    app.dependency_overrides[get_db_session] = lambda: session
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_user_service] = lambda: service
    client = TestClient(app)
    try:
        # Regression: cross-unit membership detail read is untouched in Mode A.
        resp = client.get(f"/api/v1/users/{member_in_b}")
        assert resp.status_code == 200, resp.text
        service.get.assert_called_once_with(member_in_b)
    finally:
        app.dependency_overrides.clear()
        client.close()

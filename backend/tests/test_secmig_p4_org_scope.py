"""SEC-MIG Phase 4 — Organization Scope Enforcement tests.

TASK-PLATFORM-SECMIG-P4-001 / P4-001R rework.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
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
from app.modules.assignments.router import get_assignment_service
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_batch1.router import get_cm_batch1_attachment_service, get_cm_batch1_service
from app.modules.cm_batch1.schemas import (
    ComplaintBatch1Response,
    DuplicateDecisionResponse,
    TransferAttachmentsResponse,
)
from app.modules.complaints.router import get_complaint_service


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


def test_resolver_cm_complaint_not_found() -> None:
    session = MagicMock()
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        OrgUnitResolver(session).resolve_cm_complaint(uuid.uuid4())


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

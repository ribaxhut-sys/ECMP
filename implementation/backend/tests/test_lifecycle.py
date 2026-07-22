"""Sprint-02B integration tests: TC-003 (assign), TC-004 (status), FR-020 (notification stub)."""

from __future__ import annotations

from conftest import (
    ASSIGN_PAYLOAD,
    FOREIGN_SUPERVISOR_HEADERS,
    HANDLER_HEADERS,
    HEADERS,
    NOPERM_HEADERS,
    READONLY_HEADERS,
    SUPERVISOR_HEADERS,
    VALID_PAYLOAD,
)
from sqlalchemy.orm import Session

from app.db import get_engine
from app.models import AuditLogModel, CaseModel, NotificationLogModel, OutboxModel


def _create_case(client) -> str:
    res = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert res.status_code == 201
    return res.json()["caseId"]


def _assign(client, case_id: str, headers=SUPERVISOR_HEADERS, payload=None):
    return client.post(
        f"/v1/cases/{case_id}/assign",
        json=payload or ASSIGN_PAYLOAD,
        headers=headers,
    )


def test_tc003_assign_updates_assignee_and_emits_events(client):
    """TC-003: assign REGISTERED → ASSIGNED; EVT-002 + EVT-003 + audit in one txn."""
    case_id = _create_case(client)
    res = _assign(client, case_id)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ASSIGNED"
    assert body["assigneeId"] == "USR-2001"
    assert body["unitId"] == "UNIT-01"

    fetched = client.get(f"/v1/cases/{case_id}", headers=HEADERS)
    assert fetched.json()["status"] == "ASSIGNED"

    with Session(get_engine()) as session:
        audits = (
            session.query(AuditLogModel)
            .filter(AuditLogModel.action == "case.assign")
            .all()
        )
        assert len(audits) == 1
        assert audits[0].entity_id == case_id

        evt002 = (
            session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-002").one()
        )
        assert evt002.event_name == "CaseAssigned"
        assert set(evt002.payload.keys()) == {
            "caseId",
            "assigneeId",
            "unitId",
            "assignedBy",
            "previousAssigneeId",
            "assignedAt",
        }
        assert evt002.payload["previousAssigneeId"] is None
        assert evt002.payload["assignedBy"] == "supervisor.1"

        status_changed = [
            r
            for r in session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-003").all()
            if r.payload.get("toStatus") == "ASSIGNED"
        ]
        assert len(status_changed) == 1
        assert status_changed[0].payload["fromStatus"] == "REGISTERED"


def test_tc003_reassign_from_assigned_is_invalid_state(client):
    """API-003: assignable only from REGISTERED/REOPENED — ASSIGNED → 409 INVALID_STATE."""
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    res = _assign(
        client,
        case_id,
        payload={"assigneeId": "USR-3001", "unitId": "UNIT-01"},
    )
    assert res.status_code == 409
    assert res.json()["code"] == "INVALID_STATE"
    assert client.get(f"/v1/cases/{case_id}", headers=HEADERS).json()["assigneeId"] == "USR-2001"


def test_tc003_cross_unit_forbidden(client):
    case_id = _create_case(client)
    res = _assign(client, case_id, headers=FOREIGN_SUPERVISOR_HEADERS)
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"

    with Session(get_engine()) as session:
        case = session.get(CaseModel, case_id)
        assert case.status == "REGISTERED"
        assert case.assignee_id is None
        assert session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-002").count() == 0


def test_tc003_assign_invalid_state_409(client):
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    # Advance to IN_PROGRESS (not assignable).
    assert (
        client.post(
            f"/v1/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
            headers=HANDLER_HEADERS,
        ).status_code
        == 200
    )
    res = _assign(client, case_id)
    assert res.status_code == 409
    assert res.json()["code"] == "INVALID_STATE"

    with Session(get_engine()) as session:
        case = session.get(CaseModel, case_id)
        assert case.status == "IN_PROGRESS"
        # Only the first assign's EVT-002 exists.
        assert session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-002").count() == 1


def test_tc003_assign_authz(client):
    case_id = _create_case(client)
    assert (
        client.post(
            f"/v1/cases/{case_id}/assign", json=ASSIGN_PAYLOAD
        ).status_code
        == 401
    )
    assert _assign(client, case_id, headers=READONLY_HEADERS).status_code == 403
    assert _assign(client, case_id, headers=NOPERM_HEADERS).status_code == 403


def test_tc003_assign_not_found(client):
    res = _assign(client, "CASE-NOTFOUND1")
    assert res.status_code == 404
    assert res.json()["code"] == "NOT_FOUND"


def test_tc004_invalid_transition_rejected_state_unchanged(client):
    """TC-004: REGISTERED→CLOSED → 409 INVALID_TRANSITION; no event; state unchanged."""
    case_id = _create_case(client)
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "CLOSED", "resolutionCode": "RESOLVED_REFUND"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 409
    assert res.json()["code"] == "INVALID_TRANSITION"

    fetched = client.get(f"/v1/cases/{case_id}", headers=HEADERS)
    assert fetched.json()["status"] == "REGISTERED"

    with Session(get_engine()) as session:
        assert session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-003").count() == 0
        assert (
            session.query(AuditLogModel)
            .filter(AuditLogModel.action == "case.status_change")
            .count()
            == 0
        )


def test_tc004_valid_transition_emits_evt003(client):
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "IN_PROGRESS"

    with Session(get_engine()) as session:
        rows = [
            r
            for r in session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-003").all()
            if r.payload.get("toStatus") == "IN_PROGRESS"
        ]
        assert len(rows) == 1
        assert set(rows[0].payload.keys()) == {
            "caseId",
            "fromStatus",
            "toStatus",
            "changedBy",
            "changedAt",
            "reason",
        }
        assert rows[0].payload["fromStatus"] == "ASSIGNED"
        assert (
            session.query(AuditLogModel)
            .filter(AuditLogModel.action == "case.status_change")
            .count()
            == 1
        )


def test_tc004_closed_requires_resolution_code_400(client):
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
        headers=HANDLER_HEADERS,
    )
    client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "PENDING_REVIEW"},
        headers=HANDLER_HEADERS,
    )
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "CLOSED"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 400
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_tc004_close_emits_evt005(client):
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    for to in ("IN_PROGRESS", "PENDING_REVIEW"):
        assert (
            client.post(
                f"/v1/cases/{case_id}/status",
                json={"toStatus": to},
                headers=HANDLER_HEADERS,
            ).status_code
            == 200
        )
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "CLOSED", "resolutionCode": "RESOLVED_REFUND"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "CLOSED"

    with Session(get_engine()) as session:
        closed = session.query(OutboxModel).filter(OutboxModel.event_id == "EVT-005").one()
        assert closed.payload["resolutionCode"] == "RESOLVED_REFUND"


def test_tc004_non_assignee_cannot_start_handling(client):
    case_id = _create_case(client)
    assert _assign(
        client, case_id, payload={"assigneeId": "USR-OTHER", "unitId": "UNIT-01"}
    ).status_code == 200
    # Handler token is USR-2001 — not the assignee.
    res = client.post(
        f"/v1/cases/{case_id}/status",
        json={"toStatus": "IN_PROGRESS"},
        headers=HANDLER_HEADERS,
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_tc004_status_authz(client):
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200
    assert (
        client.post(
            f"/v1/cases/{case_id}/status", json={"toStatus": "IN_PROGRESS"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            f"/v1/cases/{case_id}/status",
            json={"toStatus": "IN_PROGRESS"},
            headers=READONLY_HEADERS,
        ).status_code
        == 403
    )


def test_fr020_notification_stub_on_drain(client):
    """FR-020 / TC-020: drain delivers CaseAssigned (and CaseCreated) idempotently."""
    case_id = _create_case(client)
    assert _assign(client, case_id).status_code == 200

    drain = client.post("/_dev/outbox/drain", headers=HEADERS)
    assert drain.status_code == 200
    assert drain.json()["count"] >= 2  # EVT-001 + EVT-002 (+ EVT-003)

    with Session(get_engine()) as session:
        logs = session.query(NotificationLogModel).all()
        event_ids = {r.event_id for r in logs}
        assert "EVT-001" in event_ids
        assert "EVT-002" in event_ids
        assert all(r.status == "DELIVERED" for r in logs)
        assert "EVT-003" not in event_ids  # status changes not in FR-020 stub scope

    # Idempotent: second drain creates no new notification rows.
    client.post("/_dev/outbox/drain", headers=HEADERS)
    with Session(get_engine()) as session:
        assert session.query(NotificationLogModel).count() == len(logs)

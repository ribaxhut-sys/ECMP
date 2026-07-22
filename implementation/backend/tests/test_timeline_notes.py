"""Sprint-06: timeline (API-006) + notes (API-007/008)."""

from __future__ import annotations

from tests.conftest import (
    ASSIGN_PAYLOAD,
    HEADERS,
    NOPERM_HEADERS,
    READONLY_HEADERS,
    SUPERVISOR_HEADERS,
    VALID_PAYLOAD,
)


def _create_case(client) -> str:
    res = client.post("/v1/cases", json=VALID_PAYLOAD, headers=HEADERS)
    assert res.status_code == 201
    return res.json()["caseId"]


def test_timeline_includes_create_and_assign(client):
    case_id = _create_case(client)
    assign = client.post(
        f"/v1/cases/{case_id}/assign",
        json=ASSIGN_PAYLOAD,
        headers=SUPERVISOR_HEADERS,
    )
    assert assign.status_code == 200

    res = client.get(f"/v1/cases/{case_id}/timeline", headers=HEADERS)
    assert res.status_code == 200
    entries = res.json()["entries"]
    assert len(entries) >= 2
    assert entries[0]["actionCode"] == "case.create"
    assert entries[0]["summary"] == "Case created"
    assert "detail" in entries[0]
    assign_entry = next(e for e in entries if e["actionCode"] == "case.assign")
    assert "USR-2001" in assign_entry["summary"]
    assert assign_entry["detail"]["assigneeId"] == "USR-2001"


def test_timeline_404_and_403(client):
    missing = client.get("/v1/cases/CASE-0000000000/timeline", headers=HEADERS)
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"

    forbidden = client.get(
        f"/v1/cases/{_create_case(client)}/timeline",
        headers=NOPERM_HEADERS,
    )
    assert forbidden.status_code == 403


def test_notes_append_only_list_and_create(client):
    case_id = _create_case(client)

    empty = client.get(f"/v1/cases/{case_id}/notes", headers=HEADERS)
    assert empty.status_code == 200
    assert empty.json()["items"] == []

    created = client.post(
        f"/v1/cases/{case_id}/notes",
        json={"body": "First note"},
        headers=HEADERS,
    )
    assert created.status_code == 201
    note = created.json()
    assert note["body"] == "First note"
    assert note["authorUserId"] == "cs.agent.1"
    assert note["caseId"] == case_id

    second = client.post(
        f"/v1/cases/{case_id}/notes",
        json={"body": "Second note"},
        headers=HEADERS,
    )
    assert second.status_code == 201

    listed = client.get(f"/v1/cases/{case_id}/notes", headers=READONLY_HEADERS)
    assert listed.status_code == 200
    bodies = [n["body"] for n in listed.json()["items"]]
    assert bodies == ["First note", "Second note"]


def test_notes_create_forbidden_without_permission(client):
    case_id = _create_case(client)
    res = client.post(
        f"/v1/cases/{case_id}/notes",
        json={"body": "Nope"},
        headers=READONLY_HEADERS,
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_timeline_empty_only_create_entry(client):
    """Fresh case still has case.create audit — empty means no transitions beyond create."""
    case_id = _create_case(client)
    res = client.get(f"/v1/cases/{case_id}/timeline", headers=HEADERS)
    assert res.status_code == 200
    entries = res.json()["entries"]
    assert len(entries) == 1
    assert entries[0]["actionCode"] == "case.create"


def test_notes_404_unknown_case(client):
    missing_list = client.get("/v1/cases/CASE-0000000000/notes", headers=HEADERS)
    assert missing_list.status_code == 404
    missing_create = client.post(
        "/v1/cases/CASE-0000000000/notes",
        json={"body": "x"},
        headers=HEADERS,
    )
    assert missing_create.status_code == 404


def test_notes_list_forbidden_without_read(client):
    case_id = _create_case(client)
    res = client.get(f"/v1/cases/{case_id}/notes", headers=NOPERM_HEADERS)
    assert res.status_code == 403


def test_notes_chronological_order(client):
    case_id = _create_case(client)
    for body in ("A", "B", "C"):
        assert (
            client.post(
                f"/v1/cases/{case_id}/notes",
                json={"body": body},
                headers=HEADERS,
            ).status_code
            == 201
        )
    items = client.get(f"/v1/cases/{case_id}/notes", headers=HEADERS).json()["items"]
    assert [n["body"] for n in items] == ["A", "B", "C"]

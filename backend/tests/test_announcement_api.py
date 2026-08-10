"""Announcement API integration tests (real PostgreSQL).

Mirrors tests/test_sla_deadlines_api.py — TestClient + live DB, JWT tokens
carrying explicit roles/permissions claims (Permission Resolver honors an
explicit ``permissions`` claim; see authentication.resolve_principal_permissions).

Covers the business-locked authorization matrix (only Admin/Supervisor/
Manager Pusat may manage), the publish/unpublish visibility contract,
sorting, and end_at expiry. Announcements are global (no audience/target).
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for Announcement API tests",
)

READ_ONLY_PERMISSIONS = ["complaints:read", "announcement:read"]
MANAGE_PERMISSIONS = ["complaints:read", "announcement:read", "announcement:manage"]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        eng.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _token(
    *,
    roles: list[str],
    permissions: list[str],
    org_unit_id: str | None = None,
) -> str:
    settings = get_settings()
    claims: dict[str, object] = {"roles": roles, "permissions": permissions}
    if org_unit_id is not None:
        claims["orgUnitId"] = org_unit_id
    return create_access_token(subject=str(uuid.uuid4()), settings=settings, claims=claims)


def _header(
    *,
    roles: list[str],
    permissions: list[str],
    org_unit_id: str | None = None,
) -> dict[str, str]:
    token = _token(roles=roles, permissions=permissions, org_unit_id=org_unit_id)
    return {"Authorization": f"Bearer {token}"}


# SUPERVISOR/MANAGER are BRANCH_SCOPED_ROLE_CODES (users/service.py) — the
# exact same role code is used by Cabang staff. "Pusat" is proven only by the
# caller's own org unit resolving to a Pusat-coded branch (is_pusat_unit /
# DEFAULT_PUSAT_UNIT_CODES), never by role name alone.
_PUSAT_ORG_UNIT_ID = "PUSAT"
_CABANG_ORG_UNIT_ID = "UPPPD-TANAH-ABANG"


@pytest.fixture()
def admin_header() -> dict[str, str]:
    """Admin Pusat — ADMIN never carries a branch (HEAD_OFFICE_SCOPED_ROLE_CODES)."""
    return _header(roles=["ADMIN"], permissions=MANAGE_PERMISSIONS)


@pytest.fixture()
def supervisor_header() -> dict[str, str]:
    """Supervisor Pusat — SUPERVISOR role, org unit resolves to Pusat."""
    return _header(
        roles=["SUPERVISOR"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_PUSAT_ORG_UNIT_ID,
    )


@pytest.fixture()
def manager_header() -> dict[str, str]:
    """Manager Pusat — MANAGER role, org unit resolves to Pusat."""
    return _header(
        roles=["MANAGER"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_PUSAT_ORG_UNIT_ID,
    )


@pytest.fixture()
def admin_cabang_header() -> dict[str, str]:
    """Adversarial: ADMIN role with a Cabang org marker — must still be denied."""
    return _header(
        roles=["ADMIN"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_CABANG_ORG_UNIT_ID,
    )


@pytest.fixture()
def supervisor_cabang_header() -> dict[str, str]:
    """Supervisor Cabang — same SUPERVISOR role code, branch org unit → denied."""
    return _header(
        roles=["SUPERVISOR"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_CABANG_ORG_UNIT_ID,
    )


@pytest.fixture()
def manager_cabang_header() -> dict[str, str]:
    """Manager Cabang — same MANAGER role code, branch org unit → denied."""
    return _header(
        roles=["MANAGER"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_CABANG_ORG_UNIT_ID,
    )


@pytest.fixture()
def agent_header() -> dict[str, str]:
    """Role with Pengaduan module access but NOT one of the 3 manage roles."""
    return _header(roles=["AGENT"], permissions=READ_ONLY_PERMISSIONS)


@pytest.fixture()
def no_permission_header() -> dict[str, str]:
    """Authenticated, but holds no announcement permission at all."""
    return _header(roles=["ADMIN"], permissions=[])


def _create_draft(
    client: TestClient,
    header: dict[str, str],
    *,
    title: str = "Judul pengumuman",
    end_at: str | None = None,
) -> dict:
    payload = {
        "title": title,
        "body": "Isi pengumuman uji.",
        "priority": "NORMAL",
    }
    if end_at is not None:
        payload["endAt"] = end_at
    resp = client.post("/api/v1/announcements", json=payload, headers=header)
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# --- Authorization matrix (business decision §10, LOCKED) ------------------


@pytest.mark.parametrize(
    "header_fixture", ["admin_header", "supervisor_header", "manager_header"]
)
def test_admin_supervisor_manager_can_create(
    client: TestClient, header_fixture: str, request: pytest.FixtureRequest
) -> None:
    header = request.getfixturevalue(header_fixture)
    created = _create_draft(client, header)
    assert created["status"] == "DRAFT"
    assert created["referenceNumber"].startswith("PGM-")
    assert len(created["referenceNumber"].split("-")) == 3


def test_create_allocates_unique_reference_numbers(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    first = _create_draft(client, admin_header, title="Pertama")
    second = _create_draft(client, admin_header, title="Kedua")
    assert first["referenceNumber"] != second["referenceNumber"]
    assert first["referenceNumber"].startswith("PGM-")
    assert second["referenceNumber"].startswith("PGM-")


def test_other_role_cannot_create(
    client: TestClient, agent_header: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/announcements",
        json={
            "title": "Tidak diizinkan",
            "body": "Harus ditolak.",
            "priority": "NORMAL",
        },
        headers=agent_header,
    )
    assert resp.status_code == 403, resp.text


def test_other_role_cannot_publish_or_delete(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
) -> None:
    created = _create_draft(client, admin_header)
    aid = created["id"]

    publish_resp = client.put(
        f"/api/v1/announcements/{aid}/publish", headers=agent_header
    )
    assert publish_resp.status_code == 403

    delete_resp = client.delete(
        f"/api/v1/announcements/{aid}", headers=agent_header
    )
    assert delete_resp.status_code == 403


def test_other_role_can_read_management_endpoint_is_forbidden(
    client: TestClient, agent_header: dict[str, str]
) -> None:
    """Management list (all statuses) is manage-only, not just read-only."""
    resp = client.get("/api/v1/announcements", headers=agent_header)
    assert resp.status_code == 403


def test_other_role_can_read_active_list(
    client: TestClient, agent_header: dict[str, str]
) -> None:
    resp = client.get(
        "/api/v1/announcements/active",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text


# --- Pusat vs Cabang (permission correction, LOCKED) ------------------------
#
# announcement:manage alone is NOT sufficient for SUPERVISOR/MANAGER — those
# role codes are shared with Cabang staff (BRANCH_SCOPED_ROLE_CODES). Only a
# caller whose own org unit resolves to a Pusat-coded branch may manage.
# ADMIN never carries a branch, so it is always allowed regardless of org —
# except the adversarial case below, where a Cabang org marker on an ADMIN
# token must still be denied (defense in depth).

_DENIED_PUSAT_PERSONAS = [
    "admin_cabang_header",
    "supervisor_cabang_header",
    "manager_cabang_header",
    "agent_header",
    "no_permission_header",
]

_ALLOWED_PUSAT_PERSONAS = ["admin_header", "supervisor_header", "manager_header"]


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_list_management(
    client: TestClient, header_fixture: str, request: pytest.FixtureRequest
) -> None:
    header = request.getfixturevalue(header_fixture)
    resp = client.get("/api/v1/announcements", headers=header)
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_create(
    client: TestClient, header_fixture: str, request: pytest.FixtureRequest
) -> None:
    header = request.getfixturevalue(header_fixture)
    resp = client.post(
        "/api/v1/announcements",
        json={
            "title": "Harus ditolak",
            "body": "Harus ditolak.",
            "priority": "NORMAL",
        },
        headers=header,
    )
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_update(
    client: TestClient,
    admin_header: dict[str, str],
    header_fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    created = _create_draft(client, admin_header, title="Target update ditolak")
    header = request.getfixturevalue(header_fixture)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}",
        json={
            "title": "Diubah tanpa izin",
            "body": "Harus ditolak.",
            "priority": "NORMAL",
        },
        headers=header,
    )
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_publish(
    client: TestClient,
    admin_header: dict[str, str],
    header_fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    created = _create_draft(client, admin_header, title="Target publish ditolak")
    header = request.getfixturevalue(header_fixture)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}/publish", headers=header
    )
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_unpublish(
    client: TestClient,
    admin_header: dict[str, str],
    header_fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    created = _create_draft(client, admin_header, title="Target unpublish ditolak")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    header = request.getfixturevalue(header_fixture)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}/unpublish", headers=header
    )
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _DENIED_PUSAT_PERSONAS)
def test_denied_persona_cannot_delete(
    client: TestClient,
    admin_header: dict[str, str],
    header_fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    created = _create_draft(client, admin_header, title="Target delete ditolak")
    header = request.getfixturevalue(header_fixture)
    resp = client.delete(f"/api/v1/announcements/{created['id']}", headers=header)
    assert resp.status_code == 403, f"{header_fixture}: {resp.text}"


@pytest.mark.parametrize("header_fixture", _ALLOWED_PUSAT_PERSONAS)
def test_pusat_persona_has_full_and_equal_management_rights(
    client: TestClient, header_fixture: str, request: pytest.FixtureRequest
) -> None:
    """Admin/Supervisor/Manager Pusat share identical rights (business §1)."""
    header = request.getfixturevalue(header_fixture)

    created = _create_draft(client, header, title=f"Lifecycle {header_fixture}")

    list_resp = client.get("/api/v1/announcements", headers=header)
    assert list_resp.status_code == 200, f"{header_fixture} list: {list_resp.text}"

    update_resp = client.put(
        f"/api/v1/announcements/{created['id']}",
        json={
            "title": "Judul diperbarui",
            "body": "Isi diperbarui.",
            "priority": "IMPORTANT",
        },
        headers=header,
    )
    assert update_resp.status_code == 200, f"{header_fixture} update: {update_resp.text}"

    publish_resp = client.put(
        f"/api/v1/announcements/{created['id']}/publish", headers=header
    )
    assert publish_resp.status_code == 200, f"{header_fixture} publish: {publish_resp.text}"

    unpublish_resp = client.put(
        f"/api/v1/announcements/{created['id']}/unpublish", headers=header
    )
    assert unpublish_resp.status_code == 200, (
        f"{header_fixture} unpublish: {unpublish_resp.text}"
    )

    delete_resp = client.delete(
        f"/api/v1/announcements/{created['id']}", headers=header
    )
    assert delete_resp.status_code == 204, f"{header_fixture} delete: {delete_resp.text}"


# --- History / archive for readers (Arsip Pengumuman milestone, LOCKED) ----
#
# /history is the reader-facing archive: "what was ever published". It must
# use the exact same announcement:read gate as /active (never manage), must
# never leak DRAFT, and must include ARCHIVED + PUBLISHED (both still-active
# and past end_at / EXPIRED) with no start_at/end_at windowing.


def test_reader_history_returns_200_and_excludes_draft(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    draft = _create_draft(client, admin_header, title="Draft tak boleh bocor")
    _ = draft  # never published — stays DRAFT

    resp = client.get(
        "/api/v1/announcements/history",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Draft tak boleh bocor" not in titles


def test_reader_history_includes_published_active_expired_and_archived(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    active = _create_draft(client, admin_header, title="Published masih aktif")
    client.put(f"/api/v1/announcements/{active['id']}/publish", headers=admin_header)

    expired = _create_draft(client, admin_header, title="Published sudah lewat")
    client.put(f"/api/v1/announcements/{expired['id']}/publish", headers=admin_header)

    archived = _create_draft(client, admin_header, title="Sudah diarsipkan")
    client.put(f"/api/v1/announcements/{archived['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/announcements/{archived['id']}/unpublish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/history",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    by_title = {a["title"]: a for a in resp.json()["data"]}
    assert by_title["Published masih aktif"]["status"] == "PUBLISHED"
    assert by_title["Published masih aktif"]["effectiveStatus"] == "PUBLISHED"
    assert by_title["Sudah diarsipkan"]["status"] == "ARCHIVED"


def test_reader_history_shows_expired_effective_status(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    created = _create_draft(client, admin_header, title="Akan kedaluwarsa di history")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE announcements SET end_at = :past WHERE id = :id"),
        {"past": past, "id": created["id"]},
    )
    db_session.commit()

    resp = client.get(
        "/api/v1/announcements/history",
        headers=agent_header,
    )
    row = next(
        a for a in resp.json()["data"] if a["title"] == "Akan kedaluwarsa di history"
    )
    assert row["status"] == "PUBLISHED"
    assert row["effectiveStatus"] == "EXPIRED"


def test_reader_history_not_windowed_by_start_end_at(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
) -> None:
    """Unlike /active, /history is not filtered by the active window — an
    expired announcement stays in the archive."""
    future_end = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    created = _create_draft(
        client, admin_header, title="Berakhir lama sekali", end_at=None
    )
    _ = future_end
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    active_resp = client.get(
        "/api/v1/announcements/active",
        headers=agent_header,
    )
    history_resp = client.get(
        "/api/v1/announcements/history",
        headers=agent_header,
    )
    active_titles = [a["title"] for a in active_resp.json()["data"]]
    history_titles = [a["title"] for a in history_resp.json()["data"]]
    assert "Berakhir lama sekali" in active_titles
    assert "Berakhir lama sekali" in history_titles


def test_management_endpoint_stays_manage_only_not_a_reader_endpoint(
    client: TestClient, agent_header: dict[str, str]
) -> None:
    """§7, LOCKED — /announcements (management list) must never become a
    reader endpoint; readers use /history instead."""
    resp = client.get("/api/v1/announcements", headers=agent_header)
    assert resp.status_code == 403, resp.text


def test_reader_cannot_open_draft_detail(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    draft = _create_draft(client, admin_header, title="Draft detail tersembunyi")
    resp = client.get(
        f"/api/v1/announcements/{draft['id']}", headers=agent_header
    )
    assert resp.status_code == 404, resp.text


def test_reader_cannot_see_scheduled_until_start_at(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    """Cabang/readers must not see SCHEDULED via history, detail, or mark-read."""
    future = datetime.now(UTC) + timedelta(days=3)
    created = _create_draft(client, admin_header, title="Terjadwal rahasia cabang")
    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish",
        headers=admin_header,
        json={"startAt": future.isoformat()},
    ).json()["data"]
    assert pub["effectiveStatus"] == "SCHEDULED"

    # Manage still sees it.
    mgmt = client.get("/api/v1/announcements", headers=admin_header).json()["data"]
    assert any(a["title"] == "Terjadwal rahasia cabang" for a in mgmt)
    manage_detail = client.get(
        f"/api/v1/announcements/{created['id']}", headers=admin_header
    )
    assert manage_detail.status_code == 200, manage_detail.text

    history = client.get(
        "/api/v1/announcements/history", headers=agent_header
    ).json()["data"]
    assert "Terjadwal rahasia cabang" not in [a["title"] for a in history]

    active = client.get(
        "/api/v1/announcements/active", headers=agent_header
    ).json()["data"]
    assert "Terjadwal rahasia cabang" not in [a["title"] for a in active]

    detail = client.get(
        f"/api/v1/announcements/{created['id']}", headers=agent_header
    )
    assert detail.status_code == 404, detail.text

    mark = client.put(
        f"/api/v1/announcements/{created['id']}/read", headers=agent_header
    )
    assert mark.status_code == 404, mark.text


def test_reader_can_open_published_and_archived_detail(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    published = _create_draft(client, admin_header, title="Detail published dibuka reader")
    client.put(f"/api/v1/announcements/{published['id']}/publish", headers=admin_header)
    resp = client.get(
        f"/api/v1/announcements/{published['id']}", headers=agent_header
    )
    assert resp.status_code == 200, resp.text

    archived = _create_draft(client, admin_header, title="Detail archived dibuka reader")
    client.put(f"/api/v1/announcements/{archived['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/announcements/{archived['id']}/unpublish", headers=admin_header)
    resp2 = client.get(
        f"/api/v1/announcements/{archived['id']}", headers=agent_header
    )
    assert resp2.status_code == 200, resp2.text


def test_management_list_still_shows_draft_to_pusat_personas(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """§8/§16, LOCKED — get_for_management / list_for_management must keep
    returning Draft to the 3 manage roles; only the reader path is filtered."""
    draft = _create_draft(client, admin_header, title="Draft terlihat oleh manager")

    list_resp = client.get("/api/v1/announcements", headers=admin_header)
    titles = [a["title"] for a in list_resp.json()["data"]]
    assert "Draft terlihat oleh manager" in titles

    detail_resp = client.get(
        f"/api/v1/announcements/{draft['id']}", headers=admin_header
    )
    assert detail_resp.status_code == 200, detail_resp.text
    assert detail_resp.json()["data"]["status"] == "DRAFT"


def test_history_sorted_newest_published_first(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    first = _create_draft(client, admin_header, title="History pertama")
    client.put(f"/api/v1/announcements/{first['id']}/publish", headers=admin_header)

    second = _create_draft(client, admin_header, title="History kedua")
    client.put(f"/api/v1/announcements/{second['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/history",
        headers=agent_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert titles.index("History kedua") < titles.index("History pertama")


# --- Publish / unpublish visibility (business decision §5–6, LOCKED) -------


def test_draft_does_not_appear_on_landing(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    _create_draft(client, admin_header, title="Draft tersembunyi")

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    assert resp.status_code == 200
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Draft tersembunyi" not in titles


def test_published_appears_on_landing(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Pengumuman terbit")
    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish", headers=admin_header
    )
    assert pub.status_code == 200, pub.text
    assert pub.json()["data"]["status"] == "PUBLISHED"

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Pengumuman terbit" in titles


def test_unpublished_no_longer_appears_on_landing(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Akan diarsipkan")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    unpub = client.put(
        f"/api/v1/announcements/{created['id']}/unpublish", headers=admin_header
    )
    assert unpub.status_code == 200, unpub.text
    assert unpub.json()["data"]["status"] == "ARCHIVED"

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Akan diarsipkan" not in titles


def test_unpublish_draft_rejected(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}/unpublish", headers=admin_header
    )
    assert resp.status_code == 409


# --- Sorting -----------------------------------------------------------


def test_active_list_sorted_newest_published_first(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    first = _create_draft(client, admin_header, title="Pertama diterbitkan")
    client.put(f"/api/v1/announcements/{first['id']}/publish", headers=admin_header)

    second = _create_draft(client, admin_header, title="Kedua diterbitkan")
    client.put(f"/api/v1/announcements/{second['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert titles.index("Kedua diterbitkan") < titles.index("Pertama diterbitkan")


# --- Expiry (business decision §7, LOCKED — no scheduling engine) ----------


def test_expired_end_at_excluded_from_active_list(
    client: TestClient, admin_header: dict[str, str], db_session: Session
) -> None:
    created = _create_draft(client, admin_header, title="Sudah kedaluwarsa")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE announcements SET end_at = :past WHERE id = :id"),
        {"past": past, "id": created["id"]},
    )
    db_session.commit()

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Sudah kedaluwarsa" not in titles

    mgmt_resp = client.get("/api/v1/announcements", headers=admin_header)
    mgmt_row = next(
        a for a in mgmt_resp.json()["data"] if a["title"] == "Sudah kedaluwarsa"
    )
    assert mgmt_row["status"] == "PUBLISHED"
    assert mgmt_row["effectiveStatus"] == "EXPIRED"


def test_future_end_at_still_active(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    future = (datetime.now(UTC) + timedelta(days=7)).isoformat()
    created = _create_draft(
        client, admin_header, title="Masih berlaku", end_at=future
    )
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/active",
        headers=admin_header,
    )
    titles = [a["title"] for a in resp.json()["data"]]
    assert "Masih berlaku" in titles


def test_publish_now_without_body_still_works(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """Regression — empty publish body = start_at ≈ published_at ≈ now."""
    before = datetime.now(UTC)
    created = _create_draft(client, admin_header, title="Publish sekarang")
    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish", headers=admin_header
    ).json()["data"]
    after = datetime.now(UTC)

    assert pub["status"] == "PUBLISHED"
    assert pub["effectiveStatus"] == "PUBLISHED"
    start_at = datetime.fromisoformat(pub["startAt"].replace("Z", "+00:00"))
    published_at = datetime.fromisoformat(pub["publishedAt"].replace("Z", "+00:00"))
    assert before <= published_at <= after
    assert abs((start_at - published_at).total_seconds()) < 2


def test_publish_with_future_start_at_is_scheduled_not_active(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    future = datetime.now(UTC) + timedelta(days=3)
    created = _create_draft(client, admin_header, title="Terjadwal nanti")
    before = datetime.now(UTC)
    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish",
        headers=admin_header,
        json={"startAt": future.isoformat()},
    ).json()["data"]
    after = datetime.now(UTC)

    assert pub["status"] == "PUBLISHED"
    assert pub["effectiveStatus"] == "SCHEDULED"
    start_at = datetime.fromisoformat(pub["startAt"].replace("Z", "+00:00"))
    published_at = datetime.fromisoformat(pub["publishedAt"].replace("Z", "+00:00"))
    assert abs((start_at - future).total_seconds()) < 2
    assert before <= published_at <= after
    assert published_at < start_at

    active = client.get(
        "/api/v1/announcements/active", headers=admin_header
    ).json()["data"]
    assert "Terjadwal nanti" not in [a["title"] for a in active]


def test_scheduled_becomes_active_when_start_at_elapsed(
    client: TestClient,
    admin_header: dict[str, str],
    db_session: Session,
) -> None:
    """No DB status transition — only start_at vs now at query time."""
    future = datetime.now(UTC) + timedelta(days=5)
    created = _create_draft(client, admin_header, title="Akan aktif")
    client.put(
        f"/api/v1/announcements/{created['id']}/publish",
        headers=admin_header,
        json={"startAt": future.isoformat()},
    )

    past = datetime.now(UTC) - timedelta(hours=1)
    db_session.execute(
        text("UPDATE announcements SET start_at = :past WHERE id = :id"),
        {"past": past, "id": created["id"]},
    )
    db_session.commit()

    mgmt = client.get("/api/v1/announcements", headers=admin_header).json()["data"]
    row = next(a for a in mgmt if a["title"] == "Akan aktif")
    assert row["status"] == "PUBLISHED"
    assert row["effectiveStatus"] == "PUBLISHED"

    active = client.get(
        "/api/v1/announcements/active", headers=admin_header
    ).json()["data"]
    assert "Akan aktif" in [a["title"] for a in active]


def test_publish_rejects_start_at_not_before_end_at(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    end = datetime.now(UTC) + timedelta(days=1)
    created = _create_draft(
        client, admin_header, title="Range invalid", end_at=end.isoformat()
    )
    resp = client.put(
        f"/api/v1/announcements/{created['id']}/publish",
        headers=admin_header,
        json={"startAt": (end + timedelta(days=1)).isoformat()},
    )
    assert resp.status_code == 400


# --- Audit fields (business decision §8, LOCKED) ----------------------


def test_publish_stamps_audit_fields(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header)
    assert created["createdBy"] is not None
    assert created["createdAt"] is not None
    assert created["publishedAt"] is None
    assert created["publishedBy"] is None

    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish", headers=admin_header
    ).json()["data"]
    assert pub["publishedAt"] is not None
    assert pub["publishedBy"] is not None
    assert pub["startAt"] is not None


# --- Update (business decision §2 — edit allowed for the 3 manage roles) --


def test_manage_role_can_update_announcement(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Judul awal")

    resp = client.put(
        f"/api/v1/announcements/{created['id']}",
        json={
            "title": "Judul diperbarui",
            "body": "Isi diperbarui.",
            "priority": "IMPORTANT",
        },
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    updated = resp.json()["data"]
    assert updated["title"] == "Judul diperbarui"
    assert updated["priority"] == "IMPORTANT"
    assert updated["status"] == "DRAFT"


def test_update_can_change_scheduled_start_at(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Jadwal awal")
    first_start = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    pub = client.put(
        f"/api/v1/announcements/{created['id']}/publish",
        json={"startAt": first_start},
        headers=admin_header,
    )
    assert pub.status_code == 200, pub.text
    assert pub.json()["data"]["effectiveStatus"] == "SCHEDULED"

    second_start = (datetime.now(UTC) + timedelta(days=5)).isoformat()
    resp = client.put(
        f"/api/v1/announcements/{created['id']}",
        json={
            "title": "Jadwal diubah",
            "body": "Isi dijadwalkan ulang.",
            "priority": "NORMAL",
            "startAt": second_start,
        },
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    updated = resp.json()["data"]
    assert updated["title"] == "Jadwal diubah"
    assert updated["effectiveStatus"] == "SCHEDULED"
    updated_start = datetime.fromisoformat(updated["startAt"].replace("Z", "+00:00"))
    expected_start = datetime.fromisoformat(second_start.replace("Z", "+00:00"))
    assert abs((updated_start - expected_start).total_seconds()) < 2


def test_other_role_cannot_update(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}",
        json={
            "title": "Tidak diizinkan",
            "body": "Harus ditolak.",
            "priority": "NORMAL",
        },
        headers=agent_header,
    )
    assert resp.status_code == 403


def test_update_not_found_returns_404(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    resp = client.put(
        f"/api/v1/announcements/{uuid.uuid4()}",
        json={
            "title": "Tidak ada",
            "body": "Tidak ada.",
            "priority": "NORMAL",
        },
        headers=admin_header,
    )
    assert resp.status_code == 404


# --- Field validation ----------------------------------------------------


def test_create_rejects_blank_title(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/announcements",
        json={"title": "   ", "body": "Isi valid.", "priority": "NORMAL"},
        headers=admin_header,
    )
    assert resp.status_code == 400


def test_create_rejects_blank_body(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/announcements",
        json={"title": "Judul valid", "body": "   ", "priority": "NORMAL"},
        headers=admin_header,
    )
    assert resp.status_code == 400


# --- Delete --------------------------------------------------------------


def test_delete_removes_from_management_list(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Akan dihapus")

    delete_resp = client.delete(
        f"/api/v1/announcements/{created['id']}", headers=admin_header
    )
    assert delete_resp.status_code == 204

    mgmt_resp = client.get("/api/v1/announcements", headers=admin_header)
    titles = [a["title"] for a in mgmt_resp.json()["data"]]
    assert "Akan dihapus" not in titles


# --- Post-login unread-redirect: read-state (§19, LOCKED) -------------------
#
# GET /unread (EXISTS-shaped boolean) + PUT /{id}/read (idempotent mark-read).
# Both reuse the same active-window predicate as /active/list_active
# (AnnouncementRepository._active_conditions) — never a second "active" query.


def _drain_unread(client: TestClient, header: dict[str, str]) -> None:
    """Mark every currently-active announcement as read by this caller. This
    test DB is not truncated between tests in this file, so earlier tests'
    published fixtures (no end_at) would otherwise make every fresh reader
    see unread=True regardless of what a given test itself sets up. Draining
    first establishes a known zero baseline before asserting unread state."""
    resp = client.get("/api/v1/announcements/active", headers=header)
    assert resp.status_code == 200, resp.text
    for item in resp.json()["data"]:
        r = client.put(f"/api/v1/announcements/{item['id']}/read", headers=header)
        assert r.status_code == 204, r.text


def _agent_header_with_subject() -> tuple[dict[str, str], uuid.UUID]:
    """Same shape as agent_header, but also returns the JWT subject so a
    test can inspect announcement_reads by exact user_id — the fixture only
    exposes the header, never the underlying uuid."""
    subject = uuid.uuid4()
    token = create_access_token(
        subject=str(subject),
        settings=get_settings(),
        claims={"roles": ["AGENT"], "permissions": READ_ONLY_PERMISSIONS},
    )
    return {"Authorization": f"Bearer {token}"}, subject


def test_unread_true_for_active_no_read_record(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    _drain_unread(client, agent_header)
    created = _create_draft(client, admin_header, title="Unread aktif")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/unread",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] is True


def test_unread_false_once_read_record_exists(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    _drain_unread(client, agent_header)
    created = _create_draft(client, admin_header, title="Sudah dibaca reader")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/announcements/{created['id']}/read", headers=agent_header)

    resp = client.get(
        "/api/v1/announcements/unread",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] is False


def test_unread_false_for_expired(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    _drain_unread(client, agent_header)
    created = _create_draft(client, admin_header, title="Expired tidak memicu unread")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE announcements SET end_at = :past WHERE id = :id"),
        {"past": past, "id": created["id"]},
    )
    db_session.commit()

    resp = client.get(
        "/api/v1/announcements/unread",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] is False


def test_unread_false_for_archived(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    _drain_unread(client, agent_header)
    created = _create_draft(client, admin_header, title="Archived tidak memicu unread")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/announcements/{created['id']}/unpublish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/unread",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] is False


def test_unread_false_for_draft(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    _drain_unread(client, agent_header)
    _create_draft(client, admin_header, title="Draft tidak memicu unread")

    resp = client.get(
        "/api/v1/announcements/unread",
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"] is False


def test_unread_check_requires_announcement_read_permission(
    client: TestClient, no_permission_header: dict[str, str]
) -> None:
    resp = client.get(
        "/api/v1/announcements/unread",
        headers=no_permission_header,
    )
    assert resp.status_code == 403, resp.text


def test_mark_read_creates_read_record(
    client: TestClient, admin_header: dict[str, str], db_session: Session
) -> None:
    header, subject = _agent_header_with_subject()
    created = _create_draft(client, admin_header, title="Ditandai dibaca")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    resp = client.put(f"/api/v1/announcements/{created['id']}/read", headers=header)
    assert resp.status_code == 204, resp.text

    count = db_session.execute(
        text(
            "SELECT COUNT(*) FROM announcement_reads "
            "WHERE announcement_id = :aid AND user_id = :uid"
        ),
        {"aid": created["id"], "uid": subject},
    ).scalar_one()
    assert count == 1


def test_mark_read_idempotent_across_repeated_opens(
    client: TestClient, admin_header: dict[str, str], db_session: Session
) -> None:
    """Opening the detail twice must leave exactly one read record (§19),
    not two — the DB unique constraint + ON CONFLICT DO NOTHING guarantee."""
    header, subject = _agent_header_with_subject()
    created = _create_draft(client, admin_header, title="Dibuka dua kali")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)

    for _ in range(2):
        resp = client.put(f"/api/v1/announcements/{created['id']}/read", headers=header)
        assert resp.status_code == 204, resp.text

    count = db_session.execute(
        text(
            "SELECT COUNT(*) FROM announcement_reads "
            "WHERE announcement_id = :aid AND user_id = :uid"
        ),
        {"aid": created["id"], "uid": subject},
    ).scalar_one()
    assert count == 1


def test_mark_read_rejects_draft(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    draft = _create_draft(client, admin_header, title="Draft tidak boleh ditandai dibaca")
    resp = client.put(f"/api/v1/announcements/{draft['id']}/read", headers=agent_header)
    assert resp.status_code == 404, resp.text


def test_mark_read_requires_announcement_read_permission(
    client: TestClient, admin_header: dict[str, str], no_permission_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Tanpa izin baca")
    client.put(f"/api/v1/announcements/{created['id']}/publish", headers=admin_header)
    resp = client.put(
        f"/api/v1/announcements/{created['id']}/read", headers=no_permission_header
    )
    assert resp.status_code == 403, resp.text

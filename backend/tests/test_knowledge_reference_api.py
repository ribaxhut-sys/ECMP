"""Knowledge Reference (`@`) on Complaint Resolution — integration tests
(real PostgreSQL).

Mirrors tests/test_knowledge_api.py's fixtures/patterns. Covers:
  - referenceOnly search: ACTIVE + in-window only, permission matrix
    (Agent/Supervisor/Manager/Admin, Pusat or Cabang — all may search).
  - Reference persistence: `@[title](knowledge:<uuid>)` marker embedded in
    complaint_resolutions.resolution_notes — validated on submit, retrieved
    verbatim on read, multiple references per resolution, historical
    integrity across revisions and Knowledge archive/supersede.
  - File authorization unchanged — no new bypass through the reference path.
"""

from __future__ import annotations

import io
import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
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
    reason="PostgreSQL not available for Knowledge Reference API tests",
)

READ_ONLY_PERMISSIONS = [
    "complaints:read",
    "complaints:update",
    "knowledge:read",
    "attachment:read",
]
MANAGE_PERMISSIONS = [
    "complaints:read",
    "complaints:update",
    "knowledge:read",
    "knowledge:manage",
    "attachment:read",
]

_PUSAT_ORG_UNIT_ID = "PUSAT"
_CABANG_ORG_UNIT_ID = "UPPPD-TANAH-ABANG"


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


@pytest.fixture()
def storage_root(tmp_path: Path, db_session: Session) -> Path:
    """Point storage.root.path at a temp dir — uploads in this file never
    touch the repo's real storage dir."""
    from app.models import Setting

    row = db_session.scalar(select(Setting).where(Setting.key == "storage.root.path"))
    if row is None:
        pytest.skip("storage settings seed not migrated (0017_attachments)")
    previous = row.value
    row.value = str(tmp_path)
    db_session.commit()
    try:
        yield tmp_path
    finally:
        row.value = previous
        db_session.commit()


@pytest.fixture()
def seeded_user_id(db_session: Session, storage_root: Path) -> uuid.UUID:
    """attachments.uploaded_by carries a real FK to users.id."""
    from app.models import Role, User

    role = db_session.scalar(select(Role).where(Role.code == "ADMIN"))
    if role is None:
        pytest.skip("ADMIN role not seeded (alembic upgrade to 0020_roles)")
    user = User(
        role_id=role.id,
        email=f"{uuid.uuid4().hex}@example.test",
        username=uuid.uuid4().hex[:16],
        full_name="Knowledge Reference Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id


def _token(
    *,
    roles: list[str],
    permissions: list[str],
    org_unit_id: str | None = None,
    subject: uuid.UUID | None = None,
) -> str:
    settings = get_settings()
    claims: dict[str, object] = {"roles": roles, "permissions": permissions}
    if org_unit_id is not None:
        claims["orgUnitId"] = org_unit_id
    return create_access_token(
        subject=str(subject or uuid.uuid4()), settings=settings, claims=claims
    )


def _header(
    *,
    roles: list[str],
    permissions: list[str],
    org_unit_id: str | None = None,
    subject: uuid.UUID | None = None,
) -> dict[str, str]:
    token = _token(
        roles=roles, permissions=permissions, org_unit_id=org_unit_id, subject=subject
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_header(seeded_user_id: uuid.UUID) -> dict[str, str]:
    return _header(roles=["ADMIN"], permissions=MANAGE_PERMISSIONS, subject=seeded_user_id)


@pytest.fixture()
def agent_header(seeded_user_id: uuid.UUID) -> dict[str, str]:
    """Agent Pusat — holds complaints:update, submits the resolution."""
    return _header(
        roles=["AGENT"],
        permissions=READ_ONLY_PERMISSIONS,
        org_unit_id=_PUSAT_ORG_UNIT_ID,
        subject=seeded_user_id,
    )


# --- Knowledge fixtures (reuses Knowledge module API — no new machinery) ---


def _create_active_knowledge(
    client: TestClient,
    admin_header: dict[str, str],
    *,
    title: str,
    knowledge_type: str = "SOP",
    **extra: object,
) -> dict:
    payload: dict[str, object] = {"title": title, "knowledgeType": knowledge_type}
    payload.update(extra)
    created = client.post("/api/v1/knowledge", json=payload, headers=admin_header)
    assert created.status_code == 201, created.text
    kid = created.json()["data"]["id"]

    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    upload = client.post(
        f"/api/v1/knowledge/{kid}/files",
        headers=admin_header,
        files=files,
        data={"role": "PRIMARY"},
    )
    assert upload.status_code == 201, upload.text

    pub = client.put(f"/api/v1/knowledge/{kid}/publish", headers=admin_header)
    assert pub.status_code == 200, pub.text
    return pub.json()["data"]


# --- Complaint fixture (legacy ECMF `complaints` table — what
# ResolutionRepository/ComplaintResolution actually FK against) ------------


def _create_in_progress_complaint(db_session: Session) -> uuid.UUID:
    from app.models import Complaint

    now = datetime.now(UTC)
    complaint = Complaint(
        complaint_number=f"CMP-KREF-{uuid.uuid4().hex[:10]}",
        source_type="CUSTOMER",
        source_id=uuid.uuid4(),
        target_type="BRANCH",
        subject="Uji Knowledge Reference",
        description="Pengaduan uji untuk fitur @ Knowledge Reference.",
        status="IN_PROGRESS",
        priority="MEDIUM",
        reported_at=now,
        created_at=now,
        updated_at=now,
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint.id


def _reopen_to_in_progress(db_session: Session, complaint_id: uuid.UUID) -> None:
    """Test-only state reset — simulates the (out-of-scope) reopen flow just
    enough to submit a second resolution and observe historical integrity
    across revisions. Never asserts anything about reopen itself."""
    db_session.execute(
        text("UPDATE complaints SET status = 'IN_PROGRESS' WHERE id = :id"),
        {"id": complaint_id},
    )
    db_session.commit()


def _marker(title: str, knowledge_id: str) -> str:
    return f"@[{title}](knowledge:{knowledge_id})"


# --- referenceOnly search: ACTIVE + in-window only, always ------------------


def test_reference_search_excludes_draft(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    draft = client.post(
        "/api/v1/knowledge",
        json={"title": "Draft tidak boleh muncul di @", "knowledgeType": "SOP"},
        headers=admin_header,
    ).json()["data"]

    resp = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true"},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    titles = [k["title"] for k in resp.json()["data"]]
    assert draft["title"] not in titles


def test_reference_search_caps_at_ten_results(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """``@`` dropdown must stay scannable — hard cap 10 even when more match."""
    prefix = "LimitCapRef"
    for i in range(12):
        _create_active_knowledge(
            client,
            admin_header,
            title=f"{prefix} {i:02d}",
        )

    resp = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true", "q": prefix},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert len(data) == 10
    assert all(prefix in row["title"] for row in data)

    # Explicit limit cannot exceed the reference hard cap.
    resp = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true", "q": prefix, "limit": 50},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]) == 10


def test_reference_search_excludes_archived(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    knowledge = _create_active_knowledge(client, admin_header, title="Akan diarsipkan untuk @")
    client.put(f"/api/v1/knowledge/{knowledge['id']}/archive", headers=admin_header)

    resp = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true"},
        headers=admin_header,
    )
    titles = [k["title"] for k in resp.json()["data"]]
    assert knowledge["title"] not in titles


def test_reference_search_excludes_expired(
    client: TestClient, admin_header: dict[str, str], db_session: Session
) -> None:
    knowledge = _create_active_knowledge(client, admin_header, title="Kedaluwarsa untuk @")
    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE knowledge SET effective_to = :past WHERE id = :id"),
        {"past": past, "id": knowledge["id"]},
    )
    db_session.commit()

    resp = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true"},
        headers=admin_header,
    )
    titles = [k["title"] for k in resp.json()["data"]]
    assert knowledge["title"] not in titles


def test_reference_search_forces_effective_window_even_for_manager(
    client: TestClient, admin_header: dict[str, str], db_session: Session
) -> None:
    """The management-list window bypass (caller_may_manage) must never
    leak into referenceOnly — a Pusat Admin drafting a resolution must not
    be offered a lapsed-but-ACTIVE record either."""
    knowledge = _create_active_knowledge(
        client, admin_header, title="Kedaluwarsa tetap tersembunyi dari manager"
    )
    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE knowledge SET effective_to = :past WHERE id = :id"),
        {"past": past, "id": knowledge["id"]},
    )
    db_session.commit()

    # Sanity: the SAME Admin sees it in the plain management search (no window bypass removed).
    plain = client.get("/api/v1/knowledge", headers=admin_header)
    assert knowledge["title"] in [k["title"] for k in plain.json()["data"]]

    ref_search = client.get(
        "/api/v1/knowledge",
        params={"referenceOnly": "true"},
        headers=admin_header,
    )
    assert knowledge["title"] not in [k["title"] for k in ref_search.json()["data"]]


def test_reference_search_by_title_document_number_summary(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    knowledge = _create_active_knowledge(
        client,
        admin_header,
        title="Persyaratan Pengajuan Pembatalan",
        documentNumber="SOP-PMB-01",
        summary="Ketentuan pembatalan permohonan wajib pajak.",
    )

    for query in ("Pembatalan", "SOP-PMB-01", "wajib pajak"):
        resp = client.get(
            "/api/v1/knowledge",
            params={"referenceOnly": "true", "q": query},
            headers=admin_header,
        )
        titles = [k["title"] for k in resp.json()["data"]]
        assert knowledge["title"] in titles, f"query={query!r}: {titles}"


# --- referenceOnly search: permission matrix (Pengaduan module access) -----


@pytest.mark.parametrize(
    "roles, org_unit_id",
    [
        (["AGENT"], _PUSAT_ORG_UNIT_ID),
        (["AGENT"], _CABANG_ORG_UNIT_ID),
        (["SUPERVISOR"], _PUSAT_ORG_UNIT_ID),
        (["SUPERVISOR"], _CABANG_ORG_UNIT_ID),
        (["MANAGER"], _PUSAT_ORG_UNIT_ID),
        (["MANAGER"], _CABANG_ORG_UNIT_ID),
        (["ADMIN"], None),
        (["ADMIN"], _CABANG_ORG_UNIT_ID),
    ],
)
def test_reference_search_allowed_for_every_business_role_pusat_or_cabang(
    client: TestClient, roles: list[str], org_unit_id: str | None
) -> None:
    """§4/§19, LOCKED — every role that has Pengaduan module access (i.e.
    already holds knowledge:read) may use `@`, Pusat or Cabang, without
    needing knowledge:manage."""
    header = _header(roles=roles, permissions=READ_ONLY_PERMISSIONS, org_unit_id=org_unit_id)
    resp = client.get(
        "/api/v1/knowledge", params={"referenceOnly": "true"}, headers=header
    )
    assert resp.status_code == 200, f"{roles}@{org_unit_id}: {resp.text}"


# --- Reference persistence on resolution_notes ------------------------------


def test_resolve_persists_knowledge_marker(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    knowledge = _create_active_knowledge(client, admin_header, title="SOP Dirujuk di Penyelesaian")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = f"Penyelesaian telah dilakukan sesuai {_marker(knowledge['title'], knowledge['id'])}."

    resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Kesalahan input data",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["resolution"]["resolutionNotes"] == notes

    get_resp = client.get(
        f"/api/v1/complaints/{complaint_id}/resolution", headers=agent_header
    )
    assert get_resp.status_code == 200, get_resp.text
    assert knowledge["id"] in get_resp.json()["data"]["resolutionNotes"]


def test_resolve_accepts_multiple_knowledge_references(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    first = _create_active_knowledge(client, admin_header, title="SOP Pertama")
    second = _create_active_knowledge(client, admin_header, title="Peraturan Kedua", knowledge_type="PERATURAN")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = (
        f"Berdasarkan {_marker(first['title'], first['id'])} dan "
        f"{_marker(second['title'], second['id'])}, penyelesaian dilakukan."
    )

    resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Kesalahan prosedur",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text
    saved = resp.json()["data"]["resolution"]["resolutionNotes"]
    assert first["id"] in saved
    assert second["id"] in saved


def test_resolve_without_reference_still_works(
    client: TestClient, agent_header: dict[str, str], db_session: Session
) -> None:
    """Regression — plain text with no `@` marker must keep working exactly
    as before this feature existed."""
    complaint_id = _create_in_progress_complaint(db_session)
    resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Tanpa rujukan",
            "resolutionNotes": "Penyelesaian dilakukan tanpa merujuk Pengetahuan apa pun.",
        },
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text


def test_resolve_rejects_unknown_knowledge_reference(
    client: TestClient, agent_header: dict[str, str], db_session: Session
) -> None:
    complaint_id = _create_in_progress_complaint(db_session)
    fake_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Rujukan palsu",
            "resolutionNotes": f"Penyelesaian sesuai {_marker('Tidak Ada', fake_id)}.",
        },
        headers=agent_header,
    )
    assert resp.status_code == 400, resp.text


def test_resolve_ignores_malformed_marker_as_plain_text(
    client: TestClient, agent_header: dict[str, str], db_session: Session
) -> None:
    """A broken/hand-edited marker degrades to plain text rather than
    failing the whole resolution (§14, LOCKED — safe degradation)."""
    complaint_id = _create_in_progress_complaint(db_session)
    resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Marker rusak",
            "resolutionNotes": "Penyelesaian sesuai @[SOP Rusak](knowledge:not-a-uuid).",
        },
        headers=agent_header,
    )
    assert resp.status_code == 200, resp.text


# --- Historical integrity across revisions and Knowledge lifecycle ---------


def test_historical_reference_survives_a_later_revision(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    """A prior resolution revision keeps citing the Knowledge it was written
    against even after a newer revision (different/no reference) exists —
    each row is immutable (KM Reference §16, LOCKED)."""
    old_knowledge = _create_active_knowledge(client, admin_header, title="SOP Versi Lama Dirujuk")
    complaint_id = _create_in_progress_complaint(db_session)

    first_notes = f"Penyelesaian awal sesuai {_marker(old_knowledge['title'], old_knowledge['id'])}."
    first = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Revisi pertama",
            "resolutionNotes": first_notes,
        },
        headers=agent_header,
    )
    assert first.status_code == 200, first.text
    first_resolution_id = first.json()["data"]["resolution"]["id"]

    # Out-of-scope reopen simulated purely to reach a second resolve() call.
    _reopen_to_in_progress(db_session, complaint_id)

    second_notes = "Penyelesaian direvisi tanpa rujukan Pengetahuan."
    second = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Revisi kedua",
            "resolutionNotes": second_notes,
        },
        headers=agent_header,
    )
    assert second.status_code == 200, second.text

    # Current (GET) reflects the newest revision only.
    current = client.get(
        f"/api/v1/complaints/{complaint_id}/resolution", headers=agent_header
    )
    assert current.json()["data"]["resolutionNotes"] == second_notes

    # The FIRST revision row, on disk, is untouched — still cites old_knowledge.
    stored_first_notes = db_session.execute(
        text("SELECT resolution_notes FROM complaint_resolutions WHERE id = :id"),
        {"id": first_resolution_id},
    ).scalar_one()
    assert stored_first_notes == first_notes
    assert old_knowledge["id"] in stored_first_notes


def test_archived_referenced_knowledge_still_readable_but_not_offered_again(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    """KM Reference §17, LOCKED: archiving a referenced Knowledge does not
    break the old reference (detail stays open), but it disappears from
    the @ search used for NEW resolutions."""
    v1 = _create_active_knowledge(client, admin_header, title="SOP Sebelum Diarsipkan", versionLabel="1.0")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = f"Penyelesaian sesuai {_marker(v1['title'], v1['id'])}."
    resolve_resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Sebelum arsip",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )
    assert resolve_resp.status_code == 200, resolve_resp.text

    client.put(f"/api/v1/knowledge/{v1['id']}/archive", headers=admin_header)

    # Old reference: detail still opens (any knowledge:read holder).
    detail = client.get(f"/api/v1/knowledge/{v1['id']}", headers=agent_header)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["status"] == "ARCHIVED"

    # Saved resolution text is unchanged.
    current = client.get(
        f"/api/v1/complaints/{complaint_id}/resolution", headers=agent_header
    )
    assert current.json()["data"]["resolutionNotes"] == notes

    # But no longer offered for a NEW reference.
    ref_search = client.get(
        "/api/v1/knowledge", params={"referenceOnly": "true"}, headers=agent_header
    )
    assert v1["title"] not in [k["title"] for k in ref_search.json()["data"]]


def test_superseding_version_does_not_change_old_reference(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    """KM Reference §16, LOCKED: a laporan citing v2.0 keeps pointing at
    v2.0's Knowledge id even after v2.1 is published and v2.0 is archived —
    never re-resolved by title."""
    v1 = _create_active_knowledge(client, admin_header, title="SOP Pengaduan", versionLabel="2.0")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = f"Penyelesaian sesuai {_marker(v1['title'] + ' v2.0', v1['id'])}."
    resolve_resp = client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Sitasi versi lama",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )
    assert resolve_resp.status_code == 200, resolve_resp.text

    v2 = client.post(
        "/api/v1/knowledge",
        json={
            "title": "SOP Pengaduan",
            "knowledgeType": "SOP",
            "versionLabel": "2.1",
            "supersedesKnowledgeId": v1["id"],
        },
        headers=admin_header,
    ).json()["data"]
    files = {"file": ("sop21.pdf", io.BytesIO(b"%PDF-1.4 v2.1"), "application/pdf")}
    client.post(
        f"/api/v1/knowledge/{v2['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "PRIMARY"},
    )
    client.put(f"/api/v1/knowledge/{v2['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/knowledge/{v1['id']}/archive", headers=admin_header)

    # Old reference still points at v1's id, never silently repointed to v2.
    current = client.get(
        f"/api/v1/complaints/{complaint_id}/resolution", headers=agent_header
    )
    saved_notes = current.json()["data"]["resolutionNotes"]
    assert v1["id"] in saved_notes
    assert v2["id"] not in saved_notes

    # New @ search offers v2, not the archived v1.
    ref_search = client.get(
        "/api/v1/knowledge", params={"referenceOnly": "true", "q": "SOP Pengaduan"}, headers=agent_header
    ).json()["data"]
    ids = [k["id"] for k in ref_search]
    assert v2["id"] in ids
    assert v1["id"] not in ids


# --- File access through a referenced Knowledge — no new bypass -----------


def test_referenced_knowledge_primary_file_opens_via_existing_mechanism(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    knowledge = _create_active_knowledge(client, admin_header, title="SOP dengan file dirujuk")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = f"Penyelesaian sesuai {_marker(knowledge['title'], knowledge['id'])}."
    client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Buka file rujukan",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )

    primary_file_id = knowledge["files"][0]["id"]
    download = client.get(
        f"/api/v1/attachments/{primary_file_id}/download", headers=agent_header
    )
    assert download.status_code == 200, download.text


def test_referenced_knowledge_file_still_requires_knowledge_read(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    """Referencing a Knowledge in a resolution grants no bypass — a caller
    without knowledge:read still cannot open its file, even by reading the
    id straight out of the resolution text."""
    knowledge = _create_active_knowledge(client, admin_header, title="SOP tanpa akses baca")
    complaint_id = _create_in_progress_complaint(db_session)
    notes = f"Penyelesaian sesuai {_marker(knowledge['title'], knowledge['id'])}."
    client.post(
        f"/api/v1/complaints/{complaint_id}/resolution",
        json={
            "resolutionCategory": "SOLVED",
            "rootCause": "Tanpa izin",
            "resolutionNotes": notes,
        },
        headers=agent_header,
    )

    no_knowledge_read = _header(
        roles=["AGENT"],
        permissions=["complaints:read", "complaints:update", "attachment:read"],
        org_unit_id=_PUSAT_ORG_UNIT_ID,
    )
    primary_file_id = knowledge["files"][0]["id"]
    download = client.get(
        f"/api/v1/attachments/{primary_file_id}/download", headers=no_knowledge_read
    )
    assert download.status_code == 403, download.text

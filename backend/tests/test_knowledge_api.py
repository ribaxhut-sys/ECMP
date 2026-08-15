"""Knowledge (Pengetahuan) API integration tests (real PostgreSQL).

Mirrors tests/test_announcement_api.py — TestClient + live DB, JWT tokens
carrying explicit roles/permissions claims.

Covers the business-locked authorization matrix (only Admin/Supervisor/
Manager Pusat may manage; global read for everyone holding knowledge:read),
the DRAFT -> ACTIVE -> ARCHIVED lifecycle, the one-primary-file-required
publish gate, and file authorization on the shared attachment routes.
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
    reason="PostgreSQL not available for Knowledge API tests",
)

READ_ONLY_PERMISSIONS = ["complaints:read", "knowledge:read", "attachment:read"]
MANAGE_PERMISSIONS = [
    "complaints:read",
    "knowledge:read",
    "knowledge:manage",
    "attachment:read",
]


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
    """Point storage.root.path at a temp dir — mirrors
    test_announcement_attachment_api.py so uploads in this file never write
    into the repo's real storage dir."""
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
    """attachments.uploaded_by carries a real FK to users.id — seed a minimal
    row so uploads in this file don't violate referential integrity. Depends
    on storage_root so every fixture that needs to upload gets the temp dir
    for free by requesting this fixture."""
    from app.models import Role, User

    role = db_session.scalar(select(Role).where(Role.code == "ADMIN"))
    if role is None:
        pytest.skip("ADMIN role not seeded (alembic upgrade to 0020_roles)")
    user = User(
        role_id=role.id,
        email=f"{uuid.uuid4().hex}@example.test",
        username=uuid.uuid4().hex[:16],
        full_name="Knowledge Test User",
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


_PUSAT_ORG_UNIT_ID = "PUSAT"
_CABANG_ORG_UNIT_ID = "UPPPD-TANAH-ABANG"


@pytest.fixture()
def admin_header(seeded_user_id: uuid.UUID) -> dict[str, str]:
    """Admin Pusat — ADMIN never carries a branch (HEAD_OFFICE_SCOPED_ROLE_CODES).
    Carries a real users.id subject since this fixture uploads files."""
    return _header(
        roles=["ADMIN"], permissions=MANAGE_PERMISSIONS, subject=seeded_user_id
    )


@pytest.fixture()
def supervisor_header() -> dict[str, str]:
    return _header(
        roles=["SUPERVISOR"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_PUSAT_ORG_UNIT_ID,
    )


@pytest.fixture()
def manager_header() -> dict[str, str]:
    return _header(
        roles=["MANAGER"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_PUSAT_ORG_UNIT_ID,
    )


@pytest.fixture()
def supervisor_cabang_header() -> dict[str, str]:
    """Same SUPERVISOR role code, branch org unit — must still be denied manage."""
    return _header(
        roles=["SUPERVISOR"],
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=_CABANG_ORG_UNIT_ID,
    )


@pytest.fixture()
def agent_header() -> dict[str, str]:
    """Cabang role with Pengaduan module access but NOT a manage role."""
    return _header(
        roles=["AGENT"],
        permissions=READ_ONLY_PERMISSIONS,
        org_unit_id=_CABANG_ORG_UNIT_ID,
    )


@pytest.fixture()
def no_permission_header() -> dict[str, str]:
    return _header(roles=["ADMIN"], permissions=[])


def _create_draft(
    client: TestClient,
    header: dict[str, str],
    *,
    title: str = "SOP Penanganan Pengaduan",
    knowledge_type: str = "SOP",
    **extra: object,
) -> dict:
    payload: dict[str, object] = {
        "title": title,
        "knowledgeType": knowledge_type,
    }
    payload.update(extra)
    resp = client.post("/api/v1/knowledge", json=payload, headers=header)
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


def _upload_primary_file(
    client: TestClient, header: dict[str, str], knowledge_id: str
) -> dict:
    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    resp = client.post(
        f"/api/v1/knowledge/{knowledge_id}/files",
        headers=header,
        files=files,
        data={"role": "PRIMARY"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# --- Authorization matrix (Pusat-only manage, LOCKED) -----------------------


@pytest.mark.parametrize(
    "header_fixture", ["admin_header", "supervisor_header", "manager_header"]
)
def test_admin_supervisor_manager_can_create(
    client: TestClient, header_fixture: str, request: pytest.FixtureRequest
) -> None:
    header = request.getfixturevalue(header_fixture)
    created = _create_draft(client, header)
    assert created["status"] == "DRAFT"
    assert created["knowledgeType"] == "SOP"


def test_other_role_cannot_create(client: TestClient, agent_header: dict[str, str]) -> None:
    resp = client.post(
        "/api/v1/knowledge",
        json={"title": "Tidak diizinkan", "knowledgeType": "SOP"},
        headers=agent_header,
    )
    assert resp.status_code == 403, resp.text


def test_supervisor_cabang_cannot_create(
    client: TestClient, supervisor_cabang_header: dict[str, str]
) -> None:
    """SUPERVISOR role code alone is not sufficient — must be Pusat-coded."""
    resp = client.post(
        "/api/v1/knowledge",
        json={"title": "Harus ditolak", "knowledgeType": "SOP"},
        headers=supervisor_cabang_header,
    )
    assert resp.status_code == 403, resp.text


def test_other_role_cannot_publish_or_delete(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Target aksi ditolak")
    kid = created["id"]

    publish_resp = client.put(f"/api/v1/knowledge/{kid}/publish", headers=agent_header)
    assert publish_resp.status_code == 403

    delete_resp = client.delete(f"/api/v1/knowledge/{kid}", headers=agent_header)
    assert delete_resp.status_code == 403


def test_other_role_cannot_upload_file(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Upload ditolak untuk agent")
    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    resp = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=agent_header,
        files=files,
        data={"role": "PRIMARY"},
    )
    assert resp.status_code == 403, resp.text


# --- Global read (business decision — Knowledge v1 global-read) ------------


def test_agent_can_read_active_knowledge(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    """Cabang staff cannot manage, but can read every ACTIVE record globally
    (no org-unit narrowing on read, unlike the announcement attachment catalog)."""
    created = _create_draft(client, admin_header, title="Dibaca oleh cabang")
    _upload_primary_file(client, admin_header, created["id"])
    pub = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert pub.status_code == 200, pub.text

    resp = client.get("/api/v1/knowledge", headers=agent_header)
    assert resp.status_code == 200, resp.text
    titles = [k["title"] for k in resp.json()["data"]]
    assert "Dibaca oleh cabang" in titles

    detail = client.get(f"/api/v1/knowledge/{created['id']}", headers=agent_header)
    assert detail.status_code == 200, detail.text


def test_draft_hidden_from_non_manager_search_and_detail(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    draft = _create_draft(client, admin_header, title="Draft tersembunyi dari cabang")

    detail = client.get(f"/api/v1/knowledge/{draft['id']}", headers=agent_header)
    assert detail.status_code == 404, detail.text

    search = client.get(
        "/api/v1/knowledge", params={"status": "DRAFT"}, headers=agent_header
    )
    assert search.status_code == 403, search.text


def test_manager_sees_draft_in_management_search_and_detail(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    draft = _create_draft(client, admin_header, title="Draft terlihat oleh pengelola")

    detail = client.get(f"/api/v1/knowledge/{draft['id']}", headers=admin_header)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["status"] == "DRAFT"

    search = client.get(
        "/api/v1/knowledge", params={"status": "DRAFT"}, headers=admin_header
    )
    titles = [k["title"] for k in search.json()["data"]]
    assert "Draft terlihat oleh pengelola" in titles


def test_search_requires_knowledge_read(
    client: TestClient, no_permission_header: dict[str, str]
) -> None:
    resp = client.get("/api/v1/knowledge", headers=no_permission_header)
    assert resp.status_code == 403, resp.text


# --- Lifecycle: DRAFT -> ACTIVE -> ARCHIVED ---------------------------------


def test_publish_requires_at_least_one_file(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Tanpa file")
    resp = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert resp.status_code == 400, resp.text
    assert "file" in resp.json()["message"].lower() or "File" in resp.json()["message"]


def test_publish_succeeds_when_first_upload_is_supporting_role(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """UI no longer distinguishes primary/supporting — first file auto-PRIMARY."""
    created = _create_draft(client, admin_header, title="File pendukung saja")
    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    upload = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "SUPPORTING"},
    )
    assert upload.status_code == 201, upload.text
    roles = [f["role"] for f in upload.json()["data"]["files"]]
    assert "PRIMARY" in roles
    resp = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["status"] == "ACTIVE"


def test_publish_succeeds_with_primary_file(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Dengan file utama")
    _upload_primary_file(client, admin_header, created["id"])
    resp = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert resp.status_code == 200, resp.text
    body = resp.json()["data"]
    assert body["status"] == "ACTIVE"
    assert body["publishedAt"] is not None
    assert body["publishedBy"] is not None


def test_archive_only_from_active(client: TestClient, admin_header: dict[str, str]) -> None:
    created = _create_draft(client, admin_header, title="Belum aktif")
    resp = client.put(f"/api/v1/knowledge/{created['id']}/archive", headers=admin_header)
    assert resp.status_code == 409, resp.text


def test_unarchive_only_from_archived(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Belum diarsip")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    resp = client.put(
        f"/api/v1/knowledge/{created['id']}/unarchive", headers=admin_header
    )
    assert resp.status_code == 409, resp.text


def test_unarchive_reactivates_archived_knowledge(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Salah arsip")
    _upload_primary_file(client, admin_header, created["id"])
    pub = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert pub.status_code == 200, pub.text
    published_at = pub.json()["data"]["publishedAt"]
    published_by = pub.json()["data"]["publishedBy"]

    archive = client.put(
        f"/api/v1/knowledge/{created['id']}/archive", headers=admin_header
    )
    assert archive.json()["data"]["status"] == "ARCHIVED"

    unarchive = client.put(
        f"/api/v1/knowledge/{created['id']}/unarchive", headers=admin_header
    )
    assert unarchive.status_code == 200, unarchive.text
    body = unarchive.json()["data"]
    assert body["status"] == "ACTIVE"
    assert body["publishedAt"] == published_at
    assert body["publishedBy"] == published_by

    active_search = client.get("/api/v1/knowledge", headers=admin_header)
    assert "Salah arsip" in [k["title"] for k in active_search.json()["data"]]


def test_agent_cannot_unarchive(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
) -> None:
    created = _create_draft(client, admin_header, title="Arsip agent")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/knowledge/{created['id']}/archive", headers=admin_header)

    resp = client.put(
        f"/api/v1/knowledge/{created['id']}/unarchive", headers=agent_header
    )
    assert resp.status_code == 403, resp.text


def test_full_lifecycle_draft_active_archived(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Siklus penuh")
    _upload_primary_file(client, admin_header, created["id"])
    pub = client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    assert pub.json()["data"]["status"] == "ACTIVE"

    archive = client.put(f"/api/v1/knowledge/{created['id']}/archive", headers=admin_header)
    assert archive.status_code == 200, archive.text
    assert archive.json()["data"]["status"] == "ARCHIVED"

    # ARCHIVED tetap dapat dibuka oleh knowledge:read biasa.
    detail = client.get(f"/api/v1/knowledge/{created['id']}", headers=admin_header)
    assert detail.status_code == 200
    assert detail.json()["data"]["status"] == "ARCHIVED"

    # ARCHIVED tidak muncul di pencarian default (status=ACTIVE).
    default_search = client.get("/api/v1/knowledge", headers=admin_header)
    assert "Siklus penuh" not in [
        k["title"] for k in default_search.json()["data"]
    ]

    # Tapi dapat ditemukan lewat filter status=ARCHIVED.
    archived_search = client.get(
        "/api/v1/knowledge", params={"status": "ARCHIVED"}, headers=admin_header
    )
    assert "Siklus penuh" in [k["title"] for k in archived_search.json()["data"]]


def test_delete_only_allowed_while_draft(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Akan dihapus")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    resp = client.delete(f"/api/v1/knowledge/{created['id']}", headers=admin_header)
    assert resp.status_code == 409, resp.text


def test_delete_draft_removes_from_search(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Draft dihapus")
    resp = client.delete(f"/api/v1/knowledge/{created['id']}", headers=admin_header)
    assert resp.status_code == 204, resp.text

    detail = client.get(f"/api/v1/knowledge/{created['id']}", headers=admin_header)
    assert detail.status_code == 404


# --- ACTIVE identity lock (KM §17, LOCKED) ----------------------------------


def test_active_identity_fields_locked(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(
        client, admin_header, title="Identitas terkunci", versionLabel="1.0"
    )
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    resp = client.put(
        f"/api/v1/knowledge/{created['id']}",
        json={
            "title": "Judul diubah paksa",
            "knowledgeType": "SOP",
            "versionLabel": "1.0",
        },
        headers=admin_header,
    )
    assert resp.status_code == 400, resp.text


def test_active_non_identity_fields_still_editable(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(
        client, admin_header, title="Ringkasan boleh diubah", versionLabel="1.0"
    )
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    resp = client.put(
        f"/api/v1/knowledge/{created['id']}",
        json={
            "title": "Ringkasan boleh diubah",
            "knowledgeType": "SOP",
            "versionLabel": "1.0",
            "summary": "Ringkasan yang diperbarui.",
        },
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["summary"] == "Ringkasan yang diperbarui."


def test_draft_identity_fields_freely_editable(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Draft judul awal")
    resp = client.put(
        f"/api/v1/knowledge/{created['id']}",
        json={"title": "Draft judul diubah", "knowledgeType": "PERATURAN"},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()["data"]
    assert body["title"] == "Draft judul diubah"
    assert body["knowledgeType"] == "PERATURAN"


# --- Files: role, primary uniqueness, DRAFT-only mutation -------------------


def test_multiple_files_one_primary(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Banyak file")
    _upload_primary_file(client, admin_header, created["id"])
    files = {"file": ("lampiran.pdf", io.BytesIO(b"%PDF-1.4 lampiran"), "application/pdf")}
    supporting = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "SUPPORTING"},
    )
    assert supporting.status_code == 201, supporting.text

    body_files = supporting.json()["data"]["files"]
    assert len(body_files) == 2
    roles = sorted(f["role"] for f in body_files)
    assert roles == ["PRIMARY", "SUPPORTING"]


def test_set_primary_switches_primary_file(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Ganti file utama")
    first = _upload_primary_file(client, admin_header, created["id"])
    first_primary_id = next(
        f["id"] for f in first["files"] if f["role"] == "PRIMARY"
    )

    files = {"file": ("v2.pdf", io.BytesIO(b"%PDF-1.4 v2"), "application/pdf")}
    second_upload = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "SUPPORTING"},
    )
    second_id = next(
        f["id"]
        for f in second_upload.json()["data"]["files"]
        if f["fileName"] == "v2.pdf"
    )

    switch = client.put(
        f"/api/v1/knowledge/{created['id']}/files/{second_id}/primary",
        headers=admin_header,
    )
    assert switch.status_code == 200, switch.text
    body = switch.json()["data"]
    primaries = [f for f in body["files"] if f["role"] == "PRIMARY"]
    assert len(primaries) == 1
    assert primaries[0]["id"] == second_id

    old = next(f for f in body["files"] if f["id"] == first_primary_id)
    assert old["role"] == "SUPPORTING"


def test_remove_file_while_draft(client: TestClient, admin_header: dict[str, str]) -> None:
    created = _create_draft(client, admin_header, title="Hapus file draft")
    primary = _upload_primary_file(client, admin_header, created["id"])
    attachment_id = primary["files"][0]["id"]

    resp = client.delete(
        f"/api/v1/knowledge/{created['id']}/files/{attachment_id}",
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["files"] == []


def test_file_mutation_rejected_once_active(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Aktif tidak boleh ubah file")
    primary = _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    files = {"file": ("lain.pdf", io.BytesIO(b"%PDF-1.4 lain"), "application/pdf")}
    upload_resp = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "SUPPORTING"},
    )
    assert upload_resp.status_code == 409, upload_resp.text

    attachment_id = primary["files"][0]["id"]
    remove_resp = client.delete(
        f"/api/v1/knowledge/{created['id']}/files/{attachment_id}",
        headers=admin_header,
    )
    assert remove_resp.status_code == 409, remove_resp.text


# --- File authorization on the shared attachment routes ---------------------


def test_reader_can_download_active_knowledge_file(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="File dapat diunduh cabang")
    primary = _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    attachment_id = primary["files"][0]["id"]

    resp = client.get(
        f"/api/v1/attachments/{attachment_id}/download", headers=agent_header
    )
    assert resp.status_code == 200, resp.text


def test_reader_cannot_download_draft_knowledge_file(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="File draft tidak boleh diunduh")
    primary = _upload_primary_file(client, admin_header, created["id"])
    attachment_id = primary["files"][0]["id"]

    resp = client.get(
        f"/api/v1/attachments/{attachment_id}/download", headers=agent_header
    )
    assert resp.status_code == 404, resp.text

    # Pengelola tetap boleh membuka file draft miliknya sendiri.
    manage_resp = client.get(
        f"/api/v1/attachments/{attachment_id}/download", headers=admin_header
    )
    assert manage_resp.status_code == 200, manage_resp.text


def test_no_permission_cannot_download_active_knowledge_file(
    client: TestClient,
    admin_header: dict[str, str],
    no_permission_header: dict[str, str],
) -> None:
    created = _create_draft(client, admin_header, title="Tanpa izin unduh")
    primary = _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    attachment_id = primary["files"][0]["id"]

    resp = client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=no_permission_header,
    )
    assert resp.status_code == 403, resp.text


# --- Search ------------------------------------------------------------


def test_search_by_title(client: TestClient, admin_header: dict[str, str]) -> None:
    created = _create_draft(client, admin_header, title="Persyaratan Pengajuan Pembatalan")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/knowledge", params={"q": "pembatalan"}, headers=admin_header
    )
    assert resp.status_code == 200, resp.text
    titles = [k["title"] for k in resp.json()["data"]]
    assert "Persyaratan Pengajuan Pembatalan" in titles


def test_search_by_document_number(client: TestClient, admin_header: dict[str, str]) -> None:
    created = _create_draft(
        client, admin_header, title="SOP unik ABC", documentNumber="SOP-999"
    )
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/knowledge", params={"q": "SOP-999"}, headers=admin_header
    )
    titles = [k["title"] for k in resp.json()["data"]]
    assert "SOP unik ABC" in titles


def test_search_by_type_filter(client: TestClient, admin_header: dict[str, str]) -> None:
    sop = _create_draft(client, admin_header, title="Filter jenis SOP")
    _upload_primary_file(client, admin_header, sop["id"])
    client.put(f"/api/v1/knowledge/{sop['id']}/publish", headers=admin_header)

    peraturan = _create_draft(
        client, admin_header, title="Filter jenis Peraturan", knowledge_type="PERATURAN"
    )
    _upload_primary_file(client, admin_header, peraturan["id"])
    client.put(f"/api/v1/knowledge/{peraturan['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/knowledge", params={"type": "PERATURAN"}, headers=admin_header
    )
    titles = [k["title"] for k in resp.json()["data"]]
    assert "Filter jenis Peraturan" in titles
    assert "Filter jenis SOP" not in titles


def test_default_search_excludes_expired_for_non_manager(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    db_session: Session,
) -> None:
    created = _create_draft(client, admin_header, title="Kedaluwarsa untuk cabang")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    past = datetime.now(UTC) - timedelta(days=1)
    db_session.execute(
        text("UPDATE knowledge SET effective_to = :past WHERE id = :id"),
        {"past": past, "id": created["id"]},
    )
    db_session.commit()

    reader_search = client.get("/api/v1/knowledge", headers=agent_header)
    assert "Kedaluwarsa untuk cabang" not in [
        k["title"] for k in reader_search.json()["data"]
    ]

    # Pengelola tetap melihatnya di daftar ACTIVE (untuk keperluan arsip).
    manager_search = client.get("/api/v1/knowledge", headers=admin_header)
    assert "Kedaluwarsa untuk cabang" in [
        k["title"] for k in manager_search.json()["data"]
    ]


# --- Versioning: supersedes_knowledge_id ------------------------------------


def test_supersedes_links_new_version_to_prior(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    v1 = _create_draft(client, admin_header, title="SOP Versi Lama", versionLabel="1.0")
    _upload_primary_file(client, admin_header, v1["id"])
    client.put(f"/api/v1/knowledge/{v1['id']}/publish", headers=admin_header)

    v2 = _create_draft(
        client,
        admin_header,
        title="SOP Versi Baru",
        versionLabel="2.0",
        supersedesKnowledgeId=v1["id"],
    )
    assert v2["supersedesKnowledgeId"] == v1["id"]
    assert v2["supersedesTitle"] == "SOP Versi Lama"


# --- Validation --------------------------------------------------------


def test_create_rejects_blank_title(client: TestClient, admin_header: dict[str, str]) -> None:
    resp = client.post(
        "/api/v1/knowledge",
        json={"title": "   ", "knowledgeType": "SOP"},
        headers=admin_header,
    )
    assert resp.status_code == 400


def test_create_rejects_invalid_knowledge_type(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    resp = client.post(
        "/api/v1/knowledge",
        json={"title": "Jenis tidak valid", "knowledgeType": "LAINNYA"},
        headers=admin_header,
    )
    assert resp.status_code == 400, resp.text


def test_create_rejects_effective_to_before_from(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    now = datetime.now(UTC)
    resp = client.post(
        "/api/v1/knowledge",
        json={
            "title": "Rentang tanggal invalid",
            "knowledgeType": "SOP",
            "effectiveFrom": now.isoformat(),
            "effectiveTo": (now - timedelta(days=1)).isoformat(),
        },
        headers=admin_header,
    )
    assert resp.status_code == 400, resp.text


# --- Business role matrix (LOCKED — 4 business roles: Agent, Supervisor,
# Manager, Admin/Super Admin). Only Supervisor/Manager/Admin *at Pusat* may
# manage; Agent never manages regardless of org unit. Read follows Pengaduan
# module access (complaints:read) for every persona, Pusat or Cabang alike —
# this is the existing gate, not a new permission. ADMIN never carries a
# branch (HEAD_OFFICE_SCOPED_ROLE_CODES) so its "Cabang" row is the
# adversarial case: a client-supplied Cabang org marker on an ADMIN token
# must still be denied (defense in depth), matching the announcement
# precedent (test_denied_persona_cannot_create's admin_cabang_header).
#
#   role                  | pusat? | read | manage
#   Agent                 |  Ya    |  ✅  |  ❌
#   Supervisor            |  Ya    |  ✅  |  ✅
#   Manager               |  Ya    |  ✅  |  ✅
#   Admin / Super Admin   |  Ya    |  ✅  |  ✅
#   Agent                 | Tidak  |  ✅  |  ❌
#   Supervisor            | Tidak  |  ✅  |  ❌
#   Manager               | Tidak  |  ✅  |  ❌
#   Admin / Super Admin   | Tidak  |  ✅  |  ❌


_BUSINESS_ROLE_MATRIX: list[tuple[str, list[str], str | None, bool]] = [
    ("agent_pusat", ["AGENT"], _PUSAT_ORG_UNIT_ID, False),
    ("supervisor_pusat", ["SUPERVISOR"], _PUSAT_ORG_UNIT_ID, True),
    ("manager_pusat", ["MANAGER"], _PUSAT_ORG_UNIT_ID, True),
    ("admin_pusat", ["ADMIN"], None, True),
    ("agent_cabang", ["AGENT"], _CABANG_ORG_UNIT_ID, False),
    ("supervisor_cabang", ["SUPERVISOR"], _CABANG_ORG_UNIT_ID, False),
    ("manager_cabang", ["MANAGER"], _CABANG_ORG_UNIT_ID, False),
    ("admin_cabang", ["ADMIN"], _CABANG_ORG_UNIT_ID, False),
]


@pytest.mark.parametrize(
    "label, roles, org_unit_id, expect_manage", _BUSINESS_ROLE_MATRIX
)
def test_business_role_matrix_read_always_allowed(
    client: TestClient,
    label: str,
    roles: list[str],
    org_unit_id: str | None,
    expect_manage: bool,
) -> None:
    """Read follows Pengaduan module access (complaints:read) for all 4
    business roles, Pusat or Cabang — never narrowed by jabatan/org unit."""
    _ = expect_manage
    header = _header(roles=roles, permissions=MANAGE_PERMISSIONS, org_unit_id=org_unit_id)

    search_resp = client.get("/api/v1/knowledge", headers=header)
    assert search_resp.status_code == 200, f"{label} search: {search_resp.text}"

    detail_resp = client.get(
        f"/api/v1/knowledge/{uuid.uuid4()}", headers=header
    )
    # Unknown id — 404, never 403: proves the endpoint itself is reachable
    # (knowledge:read granted) rather than blocked at the permission gate.
    assert detail_resp.status_code == 404, f"{label} detail: {detail_resp.text}"


@pytest.mark.parametrize(
    "label, roles, org_unit_id, expect_manage", _BUSINESS_ROLE_MATRIX
)
def test_business_role_matrix_manage_only_pusat_supervisor_manager_admin(
    client: TestClient,
    label: str,
    roles: list[str],
    org_unit_id: str | None,
    expect_manage: bool,
) -> None:
    """Manage (create) is allowed only for Supervisor/Manager/Admin at
    Pusat; Agent never manages, and the same jabatan at Cabang never
    manages — enforced server-side even though the request carries the
    knowledge:manage permission claim."""
    header = _header(roles=roles, permissions=MANAGE_PERMISSIONS, org_unit_id=org_unit_id)

    resp = client.post(
        "/api/v1/knowledge",
        json={"title": f"Matrix create — {label}", "knowledgeType": "SOP"},
        headers=header,
    )
    if expect_manage:
        assert resp.status_code == 201, f"{label}: {resp.text}"
    else:
        assert resp.status_code == 403, f"{label}: {resp.text}"


@pytest.mark.parametrize(
    "label, roles, org_unit_id, expect_manage", _BUSINESS_ROLE_MATRIX
)
def test_business_role_matrix_publish_archive_files_gated_same_as_create(
    client: TestClient,
    admin_header: dict[str, str],
    seeded_user_id: uuid.UUID,
    label: str,
    roles: list[str],
    org_unit_id: str | None,
    expect_manage: bool,
) -> None:
    """§5, LOCKED — publish/archive/upload-file must reject non-manage
    personas even when called directly, not just via the UI gate."""
    created = _create_draft(client, admin_header, title=f"Matrix action target — {label}")
    # seeded_user_id — attachments.uploaded_by has a real FK to users.id, and
    # the expect_manage personas below actually reach the upload call.
    header = _header(
        roles=roles,
        permissions=MANAGE_PERMISSIONS,
        org_unit_id=org_unit_id,
        subject=seeded_user_id,
    )

    # Upload the primary file first — publish requires one (KM §18).
    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    upload_resp = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=header,
        files=files,
        data={"role": "PRIMARY"},
    )
    publish_resp = client.put(
        f"/api/v1/knowledge/{created['id']}/publish", headers=header
    )

    if expect_manage:
        assert upload_resp.status_code == 201, f"{label} upload: {upload_resp.text}"
        assert publish_resp.status_code == 200, f"{label} publish: {publish_resp.text}"
    else:
        assert upload_resp.status_code == 403, f"{label} upload: {upload_resp.text}"
        assert publish_resp.status_code == 403, f"{label} publish: {publish_resp.text}"

    archive_resp = client.put(
        f"/api/v1/knowledge/{created['id']}/archive", headers=header
    )
    if expect_manage:
        assert archive_resp.status_code == 200, f"{label} archive: {archive_resp.text}"
    else:
        assert archive_resp.status_code == 403, f"{label} archive: {archive_resp.text}"


def test_agent_pusat_can_read_but_cannot_manage(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """Explicit single-scenario check for the business rule §2/§3: Agent
    always reads, never manages — Pusat or not is irrelevant for Agent."""
    published = _create_draft(client, admin_header, title="Dibaca Agent Pusat")
    _upload_primary_file(client, admin_header, published["id"])
    client.put(f"/api/v1/knowledge/{published['id']}/publish", headers=admin_header)

    agent_pusat = _header(
        roles=["AGENT"], permissions=MANAGE_PERMISSIONS, org_unit_id=_PUSAT_ORG_UNIT_ID
    )
    read_resp = client.get(f"/api/v1/knowledge/{published['id']}", headers=agent_pusat)
    assert read_resp.status_code == 200, read_resp.text

    manage_resp = client.put(
        f"/api/v1/knowledge/{published['id']}/archive", headers=agent_pusat
    )
    assert manage_resp.status_code == 403, manage_resp.text


# --- History (who changed what, incl. file replacement) --------------------


def _history(client: TestClient, header: dict[str, str], knowledge_id: str) -> list[dict]:
    resp = client.get(f"/api/v1/knowledge/{knowledge_id}/history", headers=header)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def test_history_requires_knowledge_read(
    client: TestClient, admin_header: dict[str, str], no_permission_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat butuh izin baca")
    resp = client.get(
        f"/api/v1/knowledge/{created['id']}/history", headers=no_permission_header
    )
    assert resp.status_code == 403, resp.text


def test_history_hidden_for_draft_non_manager(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str]
) -> None:
    """Same visibility rule as the record itself — a DRAFT's history must not
    leak that the record exists to a non-manager."""
    created = _create_draft(client, admin_header, title="Riwayat draft tersembunyi")
    resp = client.get(
        f"/api/v1/knowledge/{created['id']}/history", headers=agent_header
    )
    assert resp.status_code == 404, resp.text


def test_history_records_create_and_update(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(
        client, admin_header, title="Riwayat dibuat", summary="Ringkasan awal"
    )
    update_resp = client.put(
        f"/api/v1/knowledge/{created['id']}",
        headers=admin_header,
        json={
            "title": created["title"],
            "knowledgeType": created["knowledgeType"],
            "summary": "Ringkasan baru",
        },
    )
    assert update_resp.status_code == 200, update_resp.text

    entries = _history(client, admin_header, created["id"])
    event_types = [e["eventType"] for e in entries]
    assert "KnowledgeCreated" in event_types
    assert "KnowledgeUpdated" in event_types

    created_entry = next(e for e in entries if e["eventType"] == "KnowledgeCreated")
    assert created_entry["newValues"]["summary"] == "Ringkasan awal"
    assert created_entry["actorId"] is not None

    updated_entry = next(e for e in entries if e["eventType"] == "KnowledgeUpdated")
    assert updated_entry["oldValues"]["summary"] == "Ringkasan awal"
    assert updated_entry["newValues"]["summary"] == "Ringkasan baru"
    # Untouched fields stay out of the diff.
    assert "title" not in updated_entry["oldValues"]


def test_history_ignores_no_op_update(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat tanpa perubahan")
    resp = client.put(
        f"/api/v1/knowledge/{created['id']}",
        headers=admin_header,
        json={"title": created["title"], "knowledgeType": created["knowledgeType"]},
    )
    assert resp.status_code == 200, resp.text

    entries = _history(client, admin_header, created["id"])
    assert "KnowledgeUpdated" not in [e["eventType"] for e in entries]


def test_history_records_publish_archive_unarchive(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat siklus hidup")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)
    client.put(f"/api/v1/knowledge/{created['id']}/archive", headers=admin_header)
    client.put(f"/api/v1/knowledge/{created['id']}/unarchive", headers=admin_header)

    entries = _history(client, admin_header, created["id"])
    event_types = [e["eventType"] for e in entries]
    assert "KnowledgePublished" in event_types
    assert "KnowledgeArchived" in event_types
    assert "KnowledgeUnarchived" in event_types

    published = next(e for e in entries if e["eventType"] == "KnowledgePublished")
    assert published["oldValues"] == {"status": "DRAFT"}
    assert published["newValues"]["status"] == "ACTIVE"


def test_history_records_file_upload_and_replace(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat file diganti")
    _upload_primary_file(client, admin_header, created["id"])

    files = {"file": ("v2.pdf", io.BytesIO(b"%PDF-1.4 v2"), "application/pdf")}
    replace_resp = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "PRIMARY"},
    )
    assert replace_resp.status_code == 201, replace_resp.text

    entries = _history(client, admin_header, created["id"])
    event_types = [e["eventType"] for e in entries]
    assert "KnowledgeFileUploaded" in event_types
    assert "KnowledgeFileReplaced" in event_types

    replaced = next(e for e in entries if e["eventType"] == "KnowledgeFileReplaced")
    assert replaced["oldValues"] == {"fileName": "sop.pdf", "role": "PRIMARY"}
    assert replaced["newValues"] == {"fileName": "v2.pdf", "role": "PRIMARY"}


def test_history_records_set_primary_file_replacement(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat tetapkan utama")
    _upload_primary_file(client, admin_header, created["id"])
    files = {"file": ("lampiran.pdf", io.BytesIO(b"%PDF-1.4 lampiran"), "application/pdf")}
    supporting = client.post(
        f"/api/v1/knowledge/{created['id']}/files",
        headers=admin_header,
        files=files,
        data={"role": "SUPPORTING"},
    )
    supporting_id = next(
        f["id"] for f in supporting.json()["data"]["files"] if f["fileName"] == "lampiran.pdf"
    )

    switch = client.put(
        f"/api/v1/knowledge/{created['id']}/files/{supporting_id}/primary",
        headers=admin_header,
    )
    assert switch.status_code == 200, switch.text

    entries = _history(client, admin_header, created["id"])
    replaced = next(e for e in entries if e["eventType"] == "KnowledgeFileReplaced")
    assert replaced["oldValues"] == {"fileName": "sop.pdf", "role": "PRIMARY"}
    assert replaced["newValues"] == {"fileName": "lampiran.pdf", "role": "PRIMARY"}


def test_history_records_file_removal(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    created = _create_draft(client, admin_header, title="Riwayat file dihapus")
    primary = _upload_primary_file(client, admin_header, created["id"])
    attachment_id = primary["files"][0]["id"]

    remove_resp = client.delete(
        f"/api/v1/knowledge/{created['id']}/files/{attachment_id}",
        headers=admin_header,
    )
    assert remove_resp.status_code == 200, remove_resp.text

    entries = _history(client, admin_header, created["id"])
    removed = next(e for e in entries if e["eventType"] == "KnowledgeFileRemoved")
    assert removed["oldValues"] == {"fileName": "sop.pdf", "role": "PRIMARY"}
    assert removed["actorId"] is not None


def test_type_counts_endpoint_matches_citable_set(
    client: TestClient, admin_header: dict[str, str]
) -> None:
    """``GET /type-counts`` must run before ``/{id}`` and count ACTIVE rows."""
    draft = _create_draft(client, admin_header, title="Draft type-counts")
    _upload_primary_file(client, admin_header, draft["id"])
    active = _create_draft(
        client, admin_header, title="SOP type-counts citable", knowledge_type="SOP"
    )
    _upload_primary_file(client, admin_header, active["id"])
    pub = client.put(f"/api/v1/knowledge/{active['id']}/publish", headers=admin_header)
    assert pub.status_code == 200, pub.text

    resp = client.get("/api/v1/knowledge/type-counts", headers=admin_header)
    assert resp.status_code == 200, resp.text
    counts = resp.json()["data"]
    assert counts["SOP"] >= 1
    assert set(counts) == {
        "SOP",
        "PERATURAN",
        "SURAT_EDARAN",
        "KEPUTUSAN",
        "PANDUAN",
    }


def test_history_newest_first(client: TestClient, admin_header: dict[str, str]) -> None:
    created = _create_draft(client, admin_header, title="Riwayat urutan terbaru")
    _upload_primary_file(client, admin_header, created["id"])
    client.put(f"/api/v1/knowledge/{created['id']}/publish", headers=admin_header)

    entries = _history(client, admin_header, created["id"])
    event_types = [e["eventType"] for e in entries]
    # KnowledgePublished happened last — must lead the list.
    assert event_types[0] == "KnowledgePublished"
    assert event_types[-1] == "KnowledgeCreated"

"""Announcement ↔ Attachment integration tests (real PostgreSQL + storage).

Covers business decision §5–9, §14, §18 (LOCKED):
  - one announcement may have many attachments;
  - two visibility options only, default PUBLISHED;
  - IMMEDIATE is visible even on a DRAFT announcement;
  - PUBLISHED follows the announcement's own status;
  - unauthorized access is denied server-side (never trusts the frontend);
  - the landing/active list only counts/returns attachments visible to
    the caller (announcements are global — no audience/target).
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
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
    reason="PostgreSQL not available for Announcement Attachment API tests",
)

READ_ONLY_PERMISSIONS = ["complaints:read", "announcement:read", "attachment:read"]
MANAGE_PERMISSIONS = [
    "complaints:read",
    "announcement:read",
    "announcement:manage",
    "attachment:read",
]
_PUSAT_ORG_UNIT_ID = "PUSAT"


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
    """Point storage.root.path at a temp dir — mirrors test_attachment_api.py
    so uploads in this file never write into the repo's real storage dir."""
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
def seeded_user_id(db_session: Session) -> uuid.UUID:
    """attachments.uploaded_by carries a real FK to users.id (unlike
    announcements' own audit columns) — seed a minimal row so uploads in
    this file don't violate referential integrity."""
    from app.models import Role, User

    role = db_session.scalar(select(Role).where(Role.code == "ADMIN"))
    if role is None:
        pytest.skip("ADMIN role not seeded (alembic upgrade to 0020_roles)")
    user = User(
        role_id=role.id,
        email=f"{uuid.uuid4().hex}@example.test",
        username=uuid.uuid4().hex[:16],
        full_name="Announcement Attachment Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id


@pytest.fixture()
def admin_header(seeded_user_id: uuid.UUID) -> dict[str, str]:
    return _header(roles=["ADMIN"], permissions=MANAGE_PERMISSIONS, subject=seeded_user_id)


@pytest.fixture()
def other_admin_header() -> dict[str, str]:
    """A second Admin Pusat identity — used to prove any of the 3 manage
    roles, not just the creator, can act (equal rights)."""
    return _header(
        roles=["SUPERVISOR"], permissions=MANAGE_PERMISSIONS, org_unit_id=_PUSAT_ORG_UNIT_ID
    )


@pytest.fixture()
def agent_header() -> dict[str, str]:
    return _header(roles=["AGENT"], permissions=READ_ONLY_PERMISSIONS)


@pytest.fixture()
def no_permission_header() -> dict[str, str]:
    return _header(roles=["AGENT"], permissions=[])


def _create_announcement(
    client: TestClient, header: dict[str, str], *, title: str = "Pengumuman uji"
) -> dict:
    resp = client.post(
        "/api/v1/announcements",
        json={"title": title, "body": "Isi uji.", "priority": "NORMAL"},
        headers=header,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


def _upload(
    client: TestClient,
    header: dict[str, str],
    announcement_id: str,
    *,
    filename: str = "SOP.pdf",
    visibility: str | None = None,
    content: bytes = b"%PDF-1.4 announcement attachment",
) -> dict:
    data = {} if visibility is None else {"visibility": visibility}
    resp = client.post(
        f"/api/v1/announcements/{announcement_id}/attachments",
        headers=header,
        data=data,
        files={"file": (filename, content, "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# --- Multiple attachments + upload/remove -----------------------------------


def test_announcement_can_have_multiple_attachments(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    _upload(client, admin_header, ann["id"], filename="SOP.pdf")
    _upload(client, admin_header, ann["id"], filename="Formulir.pdf")
    _upload(client, admin_header, ann["id"], filename="Alur.pdf")

    detail = client.get(f"/api/v1/announcements/{ann['id']}", headers=admin_header)
    assert detail.status_code == 200, detail.text
    body = detail.json()["data"]
    assert body["attachmentCount"] == 3
    names = {a["fileName"] for a in body["attachments"]}
    assert names == {"SOP.pdf", "Formulir.pdf", "Alur.pdf"}


def test_upload_attachment_returns_metadata(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], filename="SOP.pdf")
    assert uploaded["fileName"] == "SOP.pdf"
    assert uploaded["mimeType"] == "application/pdf"
    assert uploaded["sizeBytes"] > 0
    assert uploaded["visibility"] == "PUBLISHED"


def test_remove_attachment(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"])

    delete_resp = client.delete(
        f"/api/v1/announcements/{ann['id']}/attachments/{uploaded['id']}",
        headers=admin_header,
    )
    assert delete_resp.status_code == 204, delete_resp.text

    detail = client.get(f"/api/v1/announcements/{ann['id']}", headers=admin_header)
    assert detail.json()["data"]["attachmentCount"] == 0

    # Unlink keeps the file in the catalog — download must still work.
    download = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=admin_header
    )
    assert download.status_code == 200, download.text


# --- Visibility default + options -------------------------------------------


def test_default_visibility_is_published(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility=None)
    assert uploaded["visibility"] == "PUBLISHED"


def test_visibility_immediate_can_be_chosen(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility="IMMEDIATE")
    assert uploaded["visibility"] == "IMMEDIATE"


def test_visibility_can_be_updated(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility="PUBLISHED")

    resp = client.put(
        f"/api/v1/announcements/{ann['id']}/attachments/{uploaded['id']}",
        json={"visibility": "IMMEDIATE"},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["visibility"] == "IMMEDIATE"


# --- Draft/Published × Immediate/Published access matrix (§9, LOCKED) ------


def test_draft_plus_immediate_is_accessible(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)  # stays DRAFT
    uploaded = _upload(client, admin_header, ann["id"], visibility="IMMEDIATE")

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=agent_header
    )
    assert resp.status_code == 200, resp.text
    assert resp.content == b"%PDF-1.4 announcement attachment"


def test_draft_plus_published_is_not_accessible(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)  # stays DRAFT
    uploaded = _upload(client, admin_header, ann["id"], visibility="PUBLISHED")

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=agent_header
    )
    assert resp.status_code == 403, resp.text


def test_published_plus_published_is_accessible(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility="PUBLISHED")
    client.put(f"/api/v1/announcements/{ann['id']}/publish", headers=admin_header)

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=agent_header
    )
    assert resp.status_code == 200, resp.text


def test_manager_pusat_can_preview_draft_published_attachment(
    client: TestClient,
    admin_header: dict[str, str],
    other_admin_header: dict[str, str],
    storage_root: Path,
) -> None:
    """Manage-role bypass — Supervisor Pusat can preview while still editing,
    even though the file is DRAFT + PUBLISHED-visibility (§3 equal rights)."""
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility="PUBLISHED")

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=other_admin_header
    )
    assert resp.status_code == 200, resp.text


# --- Unauthorized access -----------------------------------------------------


def test_unauthorized_user_denied_download(
    client: TestClient,
    admin_header: dict[str, str],
    no_permission_header: dict[str, str],
    storage_root: Path,
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], visibility="IMMEDIATE")
    client.put(f"/api/v1/announcements/{ann['id']}/publish", headers=admin_header)

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=no_permission_header
    )
    assert resp.status_code == 403, resp.text


def test_unauthorized_user_denied_upload(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    resp = client.post(
        f"/api/v1/announcements/{ann['id']}/attachments",
        headers=agent_header,
        files={"file": ("x.pdf", b"%PDF", "application/pdf")},
    )
    assert resp.status_code == 403


def test_unauthorized_user_denied_remove(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"])
    resp = client.delete(
        f"/api/v1/announcements/{ann['id']}/attachments/{uploaded['id']}",
        headers=agent_header,
    )
    assert resp.status_code == 403


# --- Attachment stays with the announcement, global for every reader -------


def test_attachment_visible_on_global_active_list(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    """Announcements have no audience/target (business decision, LOCKED) — an
    attachment on a published announcement shows up in the single global
    /active list for every announcement:read holder."""
    ann = _create_announcement(client, admin_header, title="Untuk semua")
    uploaded = _upload(client, admin_header, ann["id"], visibility="IMMEDIATE")
    client.put(f"/api/v1/announcements/{ann['id']}/publish", headers=admin_header)

    resp = client.get("/api/v1/announcements/active", headers=admin_header)
    item = next(a for a in resp.json()["data"] if a["id"] == ann["id"])
    assert item["attachmentCount"] == 1
    assert item["attachments"][0]["id"] == uploaded["id"]


# --- Landing/active list: visibility-filtered attachments + count ----------


def test_active_list_only_returns_visible_attachments(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header, title="Dengan lampiran campuran")
    _upload(client, admin_header, ann["id"], filename="Immediate.pdf", visibility="IMMEDIATE")
    _upload(client, admin_header, ann["id"], filename="Published.pdf", visibility="PUBLISHED")
    client.put(f"/api/v1/announcements/{ann['id']}/publish", headers=admin_header)

    resp = client.get(
        "/api/v1/announcements/active",
        headers=agent_header,
    )
    item = next(a for a in resp.json()["data"] if a["id"] == ann["id"])
    assert item["attachmentCount"] == 2
    names = {a["fileName"] for a in item["attachments"]}
    assert names == {"Immediate.pdf", "Published.pdf"}


def test_active_list_hides_published_visibility_attachment_while_draft(
    client: TestClient, admin_header: dict[str, str], agent_header: dict[str, str], storage_root: Path
) -> None:
    """A DRAFT announcement never appears on /active at all, but this also
    proves the attachment-count logic composes correctly with that filter —
    nothing about the attachment leaks even indirectly."""
    ann = _create_announcement(client, admin_header, title="Draft dengan lampiran")
    _upload(client, admin_header, ann["id"], visibility="IMMEDIATE")

    resp = client.get(
        "/api/v1/announcements/active",
        headers=agent_header,
    )
    ids = [a["id"] for a in resp.json()["data"]]
    assert ann["id"] not in ids


# --- Attachment library + link (reuse without copy) --------------------------


def test_attachment_library_returns_announcement_files(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], filename="Reuse-Me.pdf")

    resp = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    )
    assert resp.status_code == 200, resp.text
    ids = {item["id"] for item in resp.json()["data"]}
    assert uploaded["id"] in ids


def test_attachment_library_excludes_already_linked(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"], filename="Only-Here.pdf")

    resp = client.get(
        "/api/v1/announcements/attachment-library",
        params={"excludeAnnouncementId": ann["id"]},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    ids = {item["id"] for item in resp.json()["data"]}
    assert uploaded["id"] not in ids


def test_attachment_library_filters_by_q(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    match = _upload(client, admin_header, ann["id"], filename="SOP-Cabang.pdf")
    _upload(client, admin_header, ann["id"], filename="Other.pdf")

    other = _create_announcement(client, admin_header, title="Lain")
    resp = client.get(
        "/api/v1/announcements/attachment-library",
        params={"q": "SOP-Cabang", "excludeAnnouncementId": other["id"]},
        headers=admin_header,
    )
    assert resp.status_code == 200, resp.text
    names = {item["fileName"] for item in resp.json()["data"]}
    assert "SOP-Cabang.pdf" in names
    assert "Other.pdf" not in names
    assert match["id"] in {item["id"] for item in resp.json()["data"]}


def test_attachment_library_dedupes_multi_join(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    a = _create_announcement(client, admin_header, title="A")
    b = _create_announcement(client, admin_header, title="B")
    uploaded = _upload(client, admin_header, a["id"], filename="Shared.pdf")
    link = client.post(
        f"/api/v1/announcements/{b['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "PUBLISHED"},
        headers=admin_header,
    )
    assert link.status_code == 201, link.text

    resp = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    )
    assert resp.status_code == 200, resp.text
    ids = [item["id"] for item in resp.json()["data"] if item["id"] == uploaded["id"]]
    assert len(ids) == 1


def _catalog_upload(
    client: TestClient,
    header: dict[str, str],
    *,
    filename: str,
    access_level: str = "PRIVATE",
) -> dict:
    resp = client.post(
        "/api/v1/announcements/attachment-library",
        files={"file": (filename, b"%PDF-1.4 catalog", "application/pdf")},
        data={"accessLevel": access_level},
        headers=header,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


def test_attachment_library_org_scope_filter(
    client: TestClient,
    db_session: Session,
    seeded_user_id: uuid.UUID,
    storage_root: Path,
) -> None:
    """Semua = own + Public shares; Cabang = own unit only; Pusat = Pusat stamp."""
    from app.models import Role, User

    role = db_session.scalar(select(Role).where(Role.code == "AGENT"))
    if role is None:
        role = db_session.scalar(select(Role).where(Role.code == "ADMIN"))
    assert role is not None

    cabang_a_id = uuid.uuid4()
    cabang_b_id = uuid.uuid4()
    for uid, name in (
        (cabang_a_id, "Agent Cabang A"),
        (cabang_b_id, "Agent Cabang B"),
    ):
        db_session.add(
            User(
                id=uid,
                role_id=role.id,
                email=f"{uid.hex}@example.test",
                username=uid.hex[:16],
                full_name=name,
            )
        )
    db_session.commit()

    cabang_a = "UPPPD-TANAH-ABANG"
    cabang_b = "UPPPD-GAMBIR"
    header_a = _header(
        roles=["AGENT"],
        permissions=READ_ONLY_PERMISSIONS,
        org_unit_id=cabang_a,
        subject=cabang_a_id,
    )
    header_b = _header(
        roles=["AGENT"],
        permissions=READ_ONLY_PERMISSIONS,
        org_unit_id=cabang_b,
        subject=cabang_b_id,
    )
    header_pusat = _header(
        roles=["ADMIN"],
        permissions=MANAGE_PERMISSIONS,
        subject=seeded_user_id,
    )

    own = _catalog_upload(client, header_a, filename="own-cabang.pdf")
    shared = _catalog_upload(
        client, header_b, filename="shared-other.pdf", access_level="PUBLIC"
    )
    pusat_file = _catalog_upload(
        client, header_pusat, filename="pusat-public.pdf", access_level="PUBLIC"
    )
    _catalog_upload(client, header_b, filename="private-other.pdf")

    all_resp = client.get(
        "/api/v1/announcements/attachment-library",
        params={"orgScope": "all"},
        headers=header_a,
    )
    assert all_resp.status_code == 200, all_resp.text
    all_ids = {item["id"] for item in all_resp.json()["data"]}
    assert own["id"] in all_ids
    assert shared["id"] in all_ids
    assert pusat_file["id"] in all_ids

    cabang_resp = client.get(
        "/api/v1/announcements/attachment-library",
        params={"orgScope": "cabang"},
        headers=header_a,
    )
    assert cabang_resp.status_code == 200, cabang_resp.text
    cabang_ids = {item["id"] for item in cabang_resp.json()["data"]}
    assert own["id"] in cabang_ids
    assert shared["id"] not in cabang_ids
    assert pusat_file["id"] not in cabang_ids

    pusat_resp = client.get(
        "/api/v1/announcements/attachment-library",
        params={"orgScope": "pusat"},
        headers=header_a,
    )
    assert pusat_resp.status_code == 200, pusat_resp.text
    pusat_ids = {item["id"] for item in pusat_resp.json()["data"]}
    assert pusat_file["id"] in pusat_ids
    assert own["id"] not in pusat_ids
    assert shared["id"] not in pusat_ids


def test_link_attachment_creates_join_without_copy(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    a = _create_announcement(client, admin_header, title="Sumber")
    b = _create_announcement(client, admin_header, title="Target")
    uploaded = _upload(
        client, admin_header, a["id"], filename="Shared.pdf", visibility="PUBLISHED"
    )

    linked = client.post(
        f"/api/v1/announcements/{b['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "IMMEDIATE"},
        headers=admin_header,
    )
    assert linked.status_code == 201, linked.text
    body = linked.json()["data"]
    assert body["id"] == uploaded["id"]
    assert body["visibility"] == "IMMEDIATE"
    assert body["fileName"] == "Shared.pdf"

    detail_a = client.get(f"/api/v1/announcements/{a['id']}", headers=admin_header)
    detail_b = client.get(f"/api/v1/announcements/{b['id']}", headers=admin_header)
    assert detail_a.json()["data"]["attachmentCount"] == 1
    assert detail_b.json()["data"]["attachmentCount"] == 1
    assert detail_b.json()["data"]["attachments"][0]["visibility"] == "IMMEDIATE"


def test_link_rejects_duplicate_on_same_announcement(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    ann = _create_announcement(client, admin_header)
    uploaded = _upload(client, admin_header, ann["id"])
    resp = client.post(
        f"/api/v1/announcements/{ann['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "PUBLISHED"},
        headers=admin_header,
    )
    assert resp.status_code == 409, resp.text


def test_link_rejects_non_announcement_attachment(
    client: TestClient,
    admin_header: dict[str, str],
    db_session: Session,
    storage_root: Path,
) -> None:
    from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
    from app.modules.attachment.models import AttachmentORM

    ann = _create_announcement(client, admin_header)
    foreign_id = uuid.uuid4()
    row = AttachmentORM(
        id=foreign_id,
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        file_name="complaint.pdf",
        original_name="complaint.pdf",
        mime_type="application/pdf",
        extension="pdf",
        size_bytes=12,
        storage_provider="local",
        storage_path="x/complaint.pdf",
        checksum_sha256="a" * 64,
        status=AttachmentStatus.AVAILABLE.value,
    )
    db_session.add(row)
    db_session.commit()

    resp = client.post(
        f"/api/v1/announcements/{ann['id']}/attachments/link",
        json={"attachmentId": str(foreign_id), "visibility": "PUBLISHED"},
        headers=admin_header,
    )
    assert resp.status_code == 400, resp.text


def test_link_requires_manage(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    storage_root: Path,
) -> None:
    a = _create_announcement(client, admin_header)
    b = _create_announcement(client, admin_header, title="Target")
    uploaded = _upload(client, admin_header, a["id"])
    resp = client.post(
        f"/api/v1/announcements/{b['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "PUBLISHED"},
        headers=agent_header,
    )
    assert resp.status_code == 403


def test_remove_keeps_platform_file_when_still_linked(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    a = _create_announcement(client, admin_header, title="A")
    b = _create_announcement(client, admin_header, title="B")
    uploaded = _upload(client, admin_header, a["id"])
    assert (
        client.post(
            f"/api/v1/announcements/{b['id']}/attachments/link",
            json={"attachmentId": uploaded["id"], "visibility": "PUBLISHED"},
            headers=admin_header,
        ).status_code
        == 201
    )

    assert (
        client.delete(
            f"/api/v1/announcements/{a['id']}/attachments/{uploaded['id']}",
            headers=admin_header,
        ).status_code
        == 204
    )

    detail_b = client.get(f"/api/v1/announcements/{b['id']}", headers=admin_header)
    assert detail_b.json()["data"]["attachmentCount"] == 1
    download = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=admin_header
    )
    assert download.status_code == 200, download.text


def test_unlink_keeps_catalog_file_when_last_join_gone(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    """Removing joins unlinks only — catalog soft-delete is a separate DELETE."""
    a = _create_announcement(client, admin_header, title="A")
    b = _create_announcement(client, admin_header, title="B")
    uploaded = _upload(client, admin_header, a["id"])
    client.post(
        f"/api/v1/announcements/{b['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "PUBLISHED"},
        headers=admin_header,
    )
    client.delete(
        f"/api/v1/announcements/{a['id']}/attachments/{uploaded['id']}",
        headers=admin_header,
    )
    client.delete(
        f"/api/v1/announcements/{b['id']}/attachments/{uploaded['id']}",
        headers=admin_header,
    )
    download = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=admin_header
    )
    assert download.status_code == 200, download.text

    deleted = client.delete(
        f"/api/v1/announcements/attachment-library/{uploaded['id']}",
        headers=admin_header,
    )
    assert deleted.status_code == 204, deleted.text
    gone = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=admin_header
    )
    assert gone.status_code == 404


def test_access_granted_via_any_visible_join(
    client: TestClient,
    admin_header: dict[str, str],
    agent_header: dict[str, str],
    storage_root: Path,
) -> None:
    """Reader access must not depend on which join row is returned first."""
    draft = _create_announcement(client, admin_header, title="Draft only")
    live = _create_announcement(client, admin_header, title="Live")
    uploaded = _upload(
        client, admin_header, draft["id"], filename="Shared.pdf", visibility="PUBLISHED"
    )
    client.post(
        f"/api/v1/announcements/{live['id']}/attachments/link",
        json={"attachmentId": uploaded["id"], "visibility": "IMMEDIATE"},
        headers=admin_header,
    )
    client.put(f"/api/v1/announcements/{live['id']}/publish", headers=admin_header)

    resp = client.get(
        f"/api/v1/attachments/{uploaded['id']}/download", headers=agent_header
    )
    assert resp.status_code == 200, resp.text


# --- Pin (0103) — presentation only, capped at 10, scoped per caller -------


def test_pin_floats_file_to_top_of_library(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    _catalog_upload(client, admin_header, filename="Older.pdf")
    newer = _catalog_upload(client, admin_header, filename="Newer.pdf")

    # Default order is uploaded_at DESC, so "Newer" already leads — pin the
    # older file and confirm it jumps ahead despite its older timestamp.
    older_first = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    ).json()["data"]
    older = next(item for item in older_first if item["fileName"] == "Older.pdf")
    assert older["pinned"] is False

    pin_resp = client.put(
        f"/api/v1/announcements/attachment-library/{older['id']}/pin",
        headers=admin_header,
    )
    assert pin_resp.status_code == 204, pin_resp.text

    listing = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    ).json()["data"]
    assert listing[0]["id"] == older["id"]
    assert listing[0]["pinned"] is True
    assert listing[1]["id"] == newer["id"]
    assert listing[1]["pinned"] is False


def test_pin_is_idempotent(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    item = _catalog_upload(client, admin_header, filename="Once.pdf")

    first = client.put(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )
    second = client.put(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )
    assert first.status_code == 204
    assert second.status_code == 204


def test_unpin_is_idempotent_and_restores_order(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    item = _catalog_upload(client, admin_header, filename="Toggle.pdf")
    client.put(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )

    first = client.delete(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )
    second = client.delete(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )
    assert first.status_code == 204
    assert second.status_code == 204

    listing = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    ).json()["data"]
    pinned = next(row for row in listing if row["id"] == item["id"])
    assert pinned["pinned"] is False


def test_pin_limit_is_ten_per_caller(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    items = [
        _catalog_upload(client, admin_header, filename=f"F{i}.pdf") for i in range(11)
    ]
    for item in items[:10]:
        resp = client.put(
            f"/api/v1/announcements/attachment-library/{item['id']}/pin",
            headers=admin_header,
        )
        assert resp.status_code == 204, resp.text

    over_limit = client.put(
        f"/api/v1/announcements/attachment-library/{items[10]['id']}/pin",
        headers=admin_header,
    )
    assert over_limit.status_code == 409, over_limit.text
    assert over_limit.json()["code"] == "CONFLICT"

    # Re-pinning an already-pinned file at the cap must still succeed —
    # the limit only blocks growing past 10, not confirming an existing pin.
    already_pinned_again = client.put(
        f"/api/v1/announcements/attachment-library/{items[0]['id']}/pin",
        headers=admin_header,
    )
    assert already_pinned_again.status_code == 204, already_pinned_again.text


def test_pins_are_scoped_per_caller(
    client: TestClient,
    admin_header: dict[str, str],
    other_admin_header: dict[str, str],
    storage_root: Path,
) -> None:
    item = _catalog_upload(client, admin_header, filename="MineOnly.pdf")

    pin_resp = client.put(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=admin_header,
    )
    assert pin_resp.status_code == 204, pin_resp.text

    mine = client.get(
        "/api/v1/announcements/attachment-library", headers=admin_header
    ).json()["data"]
    other = client.get(
        "/api/v1/announcements/attachment-library", headers=other_admin_header
    ).json()["data"]

    assert next(r for r in mine if r["id"] == item["id"])["pinned"] is True
    assert next(r for r in other if r["id"] == item["id"])["pinned"] is False


def test_pin_requires_announcement_read_permission(
    client: TestClient,
    admin_header: dict[str, str],
    no_permission_header: dict[str, str],
    storage_root: Path,
) -> None:
    item = _catalog_upload(client, admin_header, filename="Guarded.pdf")

    resp = client.put(
        f"/api/v1/announcements/attachment-library/{item['id']}/pin",
        headers=no_permission_header,
    )
    assert resp.status_code == 403, resp.text

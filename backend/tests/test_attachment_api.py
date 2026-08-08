"""CAPABILITY-011 Attachment Management integration tests (API-323–326, 386–387)."""

from __future__ import annotations

import hashlib
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
from app.models import Attachment, User
from app.modules.attachment.domain.enums import AttachmentStatus
from app.modules.attachment.permissions import (
    ATTACHMENT_CREATE,
    ATTACHMENT_DELETE,
    ATTACHMENT_READ,
)


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
    reason="PostgreSQL not available for Attachment API tests",
)


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
def actor(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if user is None:
        pytest.skip("No seed user available")
    return user


@pytest.fixture(autouse=True)
def require_attachment_schema(db_session: Session) -> None:
    try:
        db_session.execute(text("SELECT aggregate_type, status FROM attachments LIMIT 0"))
    except Exception:
        pytest.skip("attachments CAPABILITY-011 schema missing (alembic upgrade to 0035)")


@pytest.fixture()
def storage_root(tmp_path: Path, db_session: Session) -> Path:
    """Point storage.root.path at a temp dir for isolated API tests.

    Always restore the previous value — otherwise a shared lab/dev DB keeps
    writing blobs under /tmp/pytest-* and downloads 404 after the temp dir dies.
    """
    from app.models import Setting

    row = db_session.scalar(
        select(Setting).where(Setting.key == "storage.root.path")
    )
    if row is None:
        pytest.skip("storage settings seed not migrated (0017_attachments)")
    previous = row.value
    row.value = str(tmp_path)
    db_session.commit()
    try:
        yield tmp_path
    finally:
        current = db_session.scalar(
            select(Setting).where(Setting.key == "storage.root.path")
        )
        if current is not None:
            current.value = previous
            db_session.commit()


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def test_upload_get_list_download_delete_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
    storage_root: Path,
) -> None:
    aggregate_id = uuid.uuid4()
    payload = b"%PDF-1.4 ECMP attachment test"
    headers = _auth(actor, ATTACHMENT_CREATE, ATTACHMENT_READ, ATTACHMENT_DELETE)

    upload = client.post(
        "/api/v1/attachments",
        headers=headers,
        data={
            "aggregateType": "Complaint",
            "aggregateId": str(aggregate_id),
        },
        files={"file": ("evidence.pdf", payload, "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    body = upload.json()["data"]
    attachment_id = body["id"]
    assert body["originalName"] == "evidence.pdf"
    assert body["aggregateType"] == "Complaint"
    assert body["aggregateId"] == str(aggregate_id)
    assert body["mimeType"] == "application/pdf"
    assert body["sizeBytes"] == len(payload)
    assert body["checksumSha256"] == hashlib.sha256(payload).hexdigest()
    assert body["storageProvider"] == "local"
    assert body["uploadedBy"] == str(actor.id)
    assert body["status"] == AttachmentStatus.AVAILABLE.value
    assert body["fileName"].endswith(".pdf")

    meta = client.get(
        f"/api/v1/attachments/{attachment_id}",
        headers=_auth(actor, ATTACHMENT_READ),
    )
    assert meta.status_code == 200
    assert meta.json()["data"]["id"] == attachment_id

    listed = client.get(
        "/api/v1/attachments",
        headers=_auth(actor, ATTACHMENT_READ),
        params={
            "aggregateType": "Complaint",
            "aggregateId": str(aggregate_id),
        },
    )
    assert listed.status_code == 200
    assert any(item["id"] == attachment_id for item in listed.json()["data"])

    complaint_list = client.get(
        f"/api/v1/complaints/{aggregate_id}/attachments",
        headers=_auth(actor, ATTACHMENT_READ),
    )
    assert complaint_list.status_code == 200
    assert any(item["id"] == attachment_id for item in complaint_list.json()["data"])

    download = client.get(
        f"/api/v1/attachments/{attachment_id}/download",
        headers=_auth(actor, ATTACHMENT_READ),
    )
    assert download.status_code == 200
    assert download.content == payload
    assert download.headers["content-type"].startswith("application/pdf")
    assert "evidence.pdf" in download.headers.get("content-disposition", "")
    assert download.headers.get("x-checksum-sha256") == hashlib.sha256(payload).hexdigest()

    denied = client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=_auth(actor, ATTACHMENT_READ),
    )
    assert denied.status_code == 403

    deleted = client.delete(
        f"/api/v1/attachments/{attachment_id}",
        headers=_auth(actor, ATTACHMENT_DELETE),
    )
    assert deleted.status_code == 204

    row = db_session.get(Attachment, uuid.UUID(attachment_id))
    assert row is not None
    assert row.status == AttachmentStatus.DELETED.value

    missing = client.get(
        f"/api/v1/attachments/{attachment_id}",
        headers=_auth(actor, ATTACHMENT_READ),
    )
    assert missing.status_code == 404


def test_upload_rejects_disallowed_mime(
    client: TestClient, actor: User, storage_root: Path
) -> None:
    resp = client.post(
        "/api/v1/attachments",
        headers=_auth(actor, ATTACHMENT_CREATE),
        data={
            "aggregateType": "Complaint",
            "aggregateId": str(uuid.uuid4()),
        },
        files={"file": ("malware.exe", b"MZ", "application/x-msdownload")},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_upload_requires_permission(
    client: TestClient, actor: User, storage_root: Path
) -> None:
    resp = client.post(
        "/api/v1/attachments",
        headers=_auth(actor, ATTACHMENT_READ),
        data={
            "aggregateType": "Queue",
            "aggregateId": str(uuid.uuid4()),
        },
        files={"file": ("a.pdf", b"%PDF", "application/pdf")},
    )
    assert resp.status_code == 403

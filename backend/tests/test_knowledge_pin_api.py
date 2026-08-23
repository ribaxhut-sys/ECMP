"""Knowledge pin (0104) API integration tests (real PostgreSQL).

Mirrors tests/test_announcement_attachment_api.py's pin coverage — same
rules apply here: presentation only, capped at 10, scoped per caller.
"""

from __future__ import annotations

import io
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
    reason="PostgreSQL not available for Knowledge Pin API tests",
)

READ_ONLY_PERMISSIONS = ["complaints:read", "knowledge:read", "attachment:read"]
MANAGE_PERMISSIONS = [
    "complaints:read",
    "knowledge:read",
    "knowledge:manage",
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
    from app.models import Role, User

    role = db_session.scalar(select(Role).where(Role.code == "ADMIN"))
    if role is None:
        pytest.skip("ADMIN role not seeded (alembic upgrade to 0020_roles)")
    user = User(
        role_id=role.id,
        email=f"{uuid.uuid4().hex}@example.test",
        username=uuid.uuid4().hex[:16],
        full_name="Knowledge Pin Test User",
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
def other_admin_header() -> dict[str, str]:
    """A second Admin Pusat identity — proves pins are scoped per caller."""
    return _header(
        roles=["SUPERVISOR"], permissions=MANAGE_PERMISSIONS, org_unit_id=_PUSAT_ORG_UNIT_ID
    )


@pytest.fixture()
def no_permission_header() -> dict[str, str]:
    return _header(roles=["AGENT"], permissions=[])


def _create_active(
    client: TestClient, header: dict[str, str], *, title: str
) -> dict:
    created = client.post(
        "/api/v1/knowledge",
        json={"title": title, "knowledgeType": "SOP"},
        headers=header,
    )
    assert created.status_code == 201, created.text
    knowledge_id = created.json()["data"]["id"]

    files = {"file": ("sop.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")}
    uploaded = client.post(
        f"/api/v1/knowledge/{knowledge_id}/files",
        headers=header,
        files=files,
        data={"role": "PRIMARY"},
    )
    assert uploaded.status_code == 201, uploaded.text

    published = client.put(
        f"/api/v1/knowledge/{knowledge_id}/publish", headers=header
    )
    assert published.status_code == 200, published.text
    return published.json()["data"]


def _search(client: TestClient, header: dict[str, str]) -> list[dict]:
    resp = client.get("/api/v1/knowledge", headers=header)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def test_pin_floats_record_to_top_of_search(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    _create_active(client, admin_header, title="Older SOP")
    newer = _create_active(client, admin_header, title="Newer SOP")

    older_first = _search(client, admin_header)
    older = next(row for row in older_first if row["title"] == "Older SOP")
    assert older["pinned"] is False

    pin_resp = client.put(
        f"/api/v1/knowledge/{older['id']}/pin", headers=admin_header
    )
    assert pin_resp.status_code == 204, pin_resp.text

    listing = _search(client, admin_header)
    assert listing[0]["id"] == older["id"]
    assert listing[0]["pinned"] is True
    assert listing[1]["id"] == newer["id"]
    assert listing[1]["pinned"] is False


def test_pin_and_unpin_are_idempotent(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    record = _create_active(client, admin_header, title="Toggle SOP")

    first = client.put(f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header)
    second = client.put(f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header)
    assert first.status_code == 204
    assert second.status_code == 204

    unpin_first = client.delete(
        f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header
    )
    unpin_second = client.delete(
        f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header
    )
    assert unpin_first.status_code == 204
    assert unpin_second.status_code == 204

    listing = _search(client, admin_header)
    row = next(r for r in listing if r["id"] == record["id"])
    assert row["pinned"] is False


def test_pin_limit_is_ten_per_caller(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    records = [
        _create_active(client, admin_header, title=f"SOP {i}") for i in range(11)
    ]
    for record in records[:10]:
        resp = client.put(
            f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header
        )
        assert resp.status_code == 204, resp.text

    over_limit = client.put(
        f"/api/v1/knowledge/{records[10]['id']}/pin", headers=admin_header
    )
    assert over_limit.status_code == 409, over_limit.text
    assert over_limit.json()["code"] == "CONFLICT"

    already_pinned_again = client.put(
        f"/api/v1/knowledge/{records[0]['id']}/pin", headers=admin_header
    )
    assert already_pinned_again.status_code == 204, already_pinned_again.text


def test_pins_are_scoped_per_caller(
    client: TestClient,
    admin_header: dict[str, str],
    other_admin_header: dict[str, str],
    storage_root: Path,
) -> None:
    record = _create_active(client, admin_header, title="Mine Only SOP")

    pin_resp = client.put(
        f"/api/v1/knowledge/{record['id']}/pin", headers=admin_header
    )
    assert pin_resp.status_code == 204, pin_resp.text

    mine = _search(client, admin_header)
    other = _search(client, other_admin_header)

    assert next(r for r in mine if r["id"] == record["id"])["pinned"] is True
    assert next(r for r in other if r["id"] == record["id"])["pinned"] is False


def test_pin_requires_knowledge_read_permission(
    client: TestClient,
    admin_header: dict[str, str],
    no_permission_header: dict[str, str],
    storage_root: Path,
) -> None:
    record = _create_active(client, admin_header, title="Guarded SOP")

    resp = client.put(
        f"/api/v1/knowledge/{record['id']}/pin", headers=no_permission_header
    )
    assert resp.status_code == 403, resp.text


def test_pin_unknown_knowledge_returns_404(
    client: TestClient, admin_header: dict[str, str], storage_root: Path
) -> None:
    resp = client.put(
        f"/api/v1/knowledge/{uuid.uuid4()}/pin", headers=admin_header
    )
    assert resp.status_code == 404, resp.text

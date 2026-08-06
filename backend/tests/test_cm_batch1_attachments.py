"""CM Batch 1 FR-004 attachment orchestration tests (unit + repo + API + persistence)."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.authorization.principal import Principal
from app.core.errors import ConflictError, ValidationAppError
from app.db.base import Base
from app.integrations.customer import StubCustomerProvider
from app.main import create_app
from app.modules.attachment.infrastructure.local_storage import LocalStorageProvider
from app.modules.attachment.models import AttachmentORM
from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.router import (
    get_attachment_service,
    get_cm_batch1_attachment_service,
)
from app.modules.attachment.service import AttachmentService
from app.modules.cm_batch1.attachment_config import (
    AttachmentConfig,
    DefaultAttachmentConfigProvider,
)
from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.models import (
    CmBatch1AttachmentHistoryORM,
    CmBatch1AttachmentORM,
    CmBatch1AttachmentStagingORM,
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.router import get_cm_batch1_service
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    DuplicateDecisionRequest,
    TransferAttachmentsRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService
from cm_batch1_helpers import confirmed_create

_TABLES = [
    AttachmentORM.__table__,
    CmBatch1ComplaintORM.__table__,
    CmBatch1IdempotencyORM.__table__,
    CmBatch1ChannelMessageORM.__table__,
    CmBatch1CustomerLockORM.__table__,
    CmBatch1NumberCounterORM.__table__,
    CmBatch1DuplicateDecisionORM.__table__,
    CmBatch1LaterReviewItemORM.__table__,
    CmBatch1AttachmentStagingORM.__table__,
    CmBatch1AttachmentORM.__table__,
    CmBatch1AttachmentHistoryORM.__table__,
]


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    db_path = tmp_path / "cm_batch1_att.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine, tables=_TABLES)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def attachment_svc(db_session: Session, tmp_path: Path) -> AttachmentService:
    storage = LocalStorageProvider(str(tmp_path / "blob"))
    return AttachmentService(
        repository=AttachmentRepository(db_session),
        settings=SettingsService(SettingsRepository(db_session)),
        storage=storage,
    )


@pytest.fixture()
def batch1_attachments(
    db_session: Session, attachment_svc: AttachmentService
) -> CmBatch1AttachmentService:
    return CmBatch1AttachmentService(
        attachment_service=attachment_svc,
        repository=CmBatch1AttachmentRepository(db_session),
        complaints=CmBatch1Repository(db_session),
        config_provider=DefaultAttachmentConfigProvider(),
    )


@pytest.fixture()
def cm_service(db_session: Session) -> CmBatch1Service:
    from app.modules.cm_batch1.duplicate_config import DuplicateConfig

    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(),
        store=CmBatch1Repository(db_session),
        duplicate_config=DuplicateConfig(enforce_on_create=False),
    )


def _create_complaint(cm_service: CmBatch1Service, request_id: str) -> str:
    created = confirmed_create(cm_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Evidence case",
            description="Desc",
        ),
        request_id=request_id,
        channel_message_id=None,
        actor_id="actor",
    )
    return created.complaint_id


def test_unit_config_provider_defaults() -> None:
    cfg = DefaultAttachmentConfigProvider().get()
    assert cfg.max_file_size_bytes == 10 * 1024 * 1024
    assert "application/pdf" in cfg.allowed_mime_types
    assert cfg.checksum_algorithm == "SHA-256"
    assert cfg.antivirus_mode == "STUB_ONLY"
    assert cfg.abandoned_staging_action == "VOID"


def test_tc_cm_fr004_01_upload_active_with_hash(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-1")
    payload = b"%PDF-1.4 evidence"
    result = batch1_attachments.upload(
        data=payload,
        filename="proof.pdf",
        content_type="application/pdf",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
    )
    assert result.status == "ACTIVE"
    assert result.checksum_sha256 == hashlib.sha256(payload).hexdigest()
    hist = batch1_attachments.history(result.attachment_id)
    assert any(h["eventType"] == "AttachmentUploaded" for h in hist)


def test_tc_cm_fr004_02_reject_illegal_type(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-2")
    with pytest.raises(ValidationAppError):
        batch1_attachments.upload(
            data=b"MZ executable",
            filename="bad.exe",
            content_type="application/x-msdownload",
            classification="customer_evidence",
            actor_id="a1",
            complaint_id=complaint_id,
        )


def test_tc_cm_fr004_02b_reject_oversize(
    batch1_attachments: CmBatch1AttachmentService,
    cm_service: CmBatch1Service,
    db_session: Session,
    attachment_svc: AttachmentService,
) -> None:
    tiny = DefaultAttachmentConfigProvider(
        _config=AttachmentConfig(max_file_size_bytes=8)
    )
    svc = CmBatch1AttachmentService(
        attachment_service=attachment_svc,
        repository=CmBatch1AttachmentRepository(db_session),
        complaints=CmBatch1Repository(db_session),
        config_provider=tiny,
    )
    complaint_id = _create_complaint(cm_service, "att-2b")
    with pytest.raises(ValidationAppError):
        svc.upload(
            data=b"0123456789",
            filename="big.txt",
            content_type="text/plain",
            classification="customer_evidence",
            actor_id="a1",
            complaint_id=complaint_id,
        )


def test_tc_cm_fr004_04_void_with_reason(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-4")
    uploaded = batch1_attachments.upload(
        data=b"hello void",
        filename="note.txt",
        content_type="text/plain",
        classification="internal_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
    )
    voided = batch1_attachments.void(
        uploaded.attachment_id, reason="customer_retract", actor_id="a1"
    )
    assert voided.status == "VOID"
    assert voided.void_reason == "customer_retract"


def test_tc_cm_fr004_05_supersede(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-5")
    first = batch1_attachments.upload(
        data=b"version-one",
        filename="v1.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
    )
    second = batch1_attachments.upload(
        data=b"version-two",
        filename="v2.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
        supersedes_attachment_id=first.attachment_id,
    )
    prior = batch1_attachments.get(first.attachment_id)
    assert prior.status == "SUPERSEDED"
    assert second.status == "ACTIVE"
    assert second.supersedes_id == first.attachment_id


def test_tc_cm_fr004_08_transfer_d06_no_discard(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    surviving = _create_complaint(cm_service, "att-8-surv")
    staged = batch1_attachments.upload(
        data=b"staged-bytes",
        filename="photo.png",
        content_type="image/png",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-D06-1",
    )
    assert staged.status == "STAGED"
    transferred = batch1_attachments.transfer(
        TransferAttachmentsRequest(
            stagingToken="STG-D06-1",
            survivingComplaintId=surviving,
        ),
        actor_id="a1",
    )
    assert transferred.discarded is False
    assert transferred.transferred_count == 1
    assert transferred.attachments[0].status == "TRANSFERRED"
    assert transferred.attachments[0].complaint_id == surviving
    listed = batch1_attachments.list_for_complaint(surviving)
    assert len(listed) == 1


def test_tc_cm_fr004_09_case_id_rejected(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-9")
    with pytest.raises(ValidationAppError) as exc:
        batch1_attachments.upload(
            data=b"x",
            filename="a.txt",
            content_type="text/plain",
            classification="customer_evidence",
            actor_id="a1",
            complaint_id=complaint_id,
            case_id=str(uuid.uuid4()),
        )
    assert "CaseId" in exc.value.message


def test_duplicate_checksum_policy(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-dup")
    payload = b"same-bytes-twice"
    batch1_attachments.upload(
        data=payload,
        filename="a.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
    )
    with pytest.raises(ConflictError):
        batch1_attachments.upload(
            data=payload,
            filename="b.txt",
            content_type="text/plain",
            classification="customer_evidence",
            actor_id="a1",
            complaint_id=complaint_id,
        )


def test_duplicate_checksum_allowed_across_complaints(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    first = _create_complaint(cm_service, "att-dup-cross-a")
    second = _create_complaint(cm_service, "att-dup-cross-b")
    payload = b"same-bytes-cross-complaint"
    batch1_attachments.upload(
        data=payload,
        filename="a.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=first,
    )
    again = batch1_attachments.upload(
        data=payload,
        filename="b.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=second,
    )
    assert again.checksum_sha256 == hashlib.sha256(payload).hexdigest()


def test_duplicate_checksum_allowed_across_staging_sessions(
    batch1_attachments: CmBatch1AttachmentService,
) -> None:
    payload = b"same-bytes-cross-staging"
    batch1_attachments.upload(
        data=payload,
        filename="a.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-DUP-A",
        customer_id="CUST-A",
    )
    again = batch1_attachments.upload(
        data=payload,
        filename="b.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-DUP-B",
        customer_id="CUST-A",
    )
    assert again.checksum_sha256 == hashlib.sha256(payload).hexdigest()


def test_duplicate_checksum_allowed_same_staging_different_customer(
    batch1_attachments: CmBatch1AttachmentService,
) -> None:
    payload = b"same-bytes-diff-customer"
    batch1_attachments.upload(
        data=payload,
        filename="a.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-DUP-CUST",
        customer_id="CUST-A",
    )
    again = batch1_attachments.upload(
        data=payload,
        filename="b.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-DUP-CUST",
        customer_id="CUST-B",
    )
    assert again.customer_id == "CUST-B"
    assert again.checksum_sha256 == hashlib.sha256(payload).hexdigest()


def test_duplicate_checksum_rejected_within_staging_session(
    batch1_attachments: CmBatch1AttachmentService,
) -> None:
    payload = b"same-bytes-same-staging"
    batch1_attachments.upload(
        data=payload,
        filename="a.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-DUP-SAME",
        customer_id="CUST-A",
    )
    with pytest.raises(ConflictError):
        batch1_attachments.upload(
            data=payload,
            filename="b.txt",
            content_type="text/plain",
            classification="customer_evidence",
            actor_id="a1",
            staging_token="STG-DUP-SAME",
            customer_id="CUST-A",
        )


def test_bind_missing_staging_is_noop(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-bind-noop")
    assert (
        batch1_attachments.bind_staging_to_complaint(
            staging_token="STG-DOES-NOT-EXIST",
            complaint_id=complaint_id,
            actor_id="a1",
        )
        == []
    )


def test_upload_to_complaint_closes_attachment_bind_later_review(
    batch1_attachments: CmBatch1AttachmentService, cm_service: CmBatch1Service
) -> None:
    complaint_id = _create_complaint(cm_service, "att-lr-close")
    cm_service.enqueue_later_review(
        customer_id="CUST-10001",
        reason="attachment_bind_failed",
        complaint_id=complaint_id,
    )
    open_before = [
        i
        for i in cm_service._store.list_later_review_items(status="OPEN")
        if i.complaint_id == complaint_id
    ]
    assert len(open_before) == 1

    batch1_attachments.upload(
        data=b"recover-evidence",
        filename="recover.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        complaint_id=complaint_id,
        customer_id="CUST-10001",
    )
    open_after = [
        i
        for i in cm_service._store.list_later_review_items(status="OPEN")
        if i.complaint_id == complaint_id
    ]
    assert open_after == []


def test_bind_on_create_and_link_transfer_api(
    batch1_attachments: CmBatch1AttachmentService,
    cm_service: CmBatch1Service,
) -> None:
    batch1_attachments.upload(
        data=b"bind-me",
        filename="x.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-BIND-1",
    )
    created = confirmed_create(cm_service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="with staging",
            description="d",
            stagingToken="STG-BIND-1",
        ),
        request_id="att-bind-create",
        channel_message_id=None,
        actor_id="a1",
    )
    batch1_attachments.bind_staging_to_complaint(
        staging_token="STG-BIND-1",
        complaint_id=created.complaint_id,
        actor_id="a1",
    )
    listed = batch1_attachments.list_for_complaint(created.complaint_id)
    assert len(listed) == 1
    assert listed[0].status == "ACTIVE"

    surviving = _create_complaint(cm_service, "att-link-surv")
    batch1_attachments.upload(
        data=b"redirected",
        filename="y.txt",
        content_type="text/plain",
        classification="customer_evidence",
        actor_id="a1",
        staging_token="STG-LINK-1",
    )
    cm_service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="link_existing",
            survivingComplaintId=surviving,
            stagingToken="STG-LINK-1",
        ),
        actor_id="a1",
    )
    batch1_attachments.transfer(
        TransferAttachmentsRequest(
            stagingToken="STG-LINK-1",
            survivingComplaintId=surviving,
        ),
        actor_id="a1",
    )
    assert len(batch1_attachments.list_for_complaint(surviving)) >= 1


def test_s2_migration_0042_chain() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0042_cm_batch1_attachment.py"
    )
    ns: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)
    assert ns["revision"] == "0042_cm_batch1_attachment"
    assert ns["down_revision"] == "0041_cm_batch1_duplicate"


def test_api_507_508_509_512_roundtrip(
    batch1_attachments: CmBatch1AttachmentService,
    cm_service: CmBatch1Service,
    attachment_svc: AttachmentService,
    db_session: Session,
) -> None:
    app = create_app()

    def _session() -> Generator[Session, None, None]:
        yield db_session

    from app.db.session import get_db_session
    from app.modules.cm_batch1.router import (
        get_cm_batch1_attachment_service as cm_get_att,
    )

    app.dependency_overrides[get_db_session] = _session
    app.dependency_overrides[get_cm_batch1_service] = lambda: cm_service
    app.dependency_overrides[cm_get_att] = lambda: batch1_attachments
    app.dependency_overrides[get_cm_batch1_attachment_service] = (
        lambda: batch1_attachments
    )
    app.dependency_overrides[get_attachment_service] = lambda: attachment_svc

    async def _principal() -> Principal:
        return Principal(
            user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            roles=("AGENT",),
            permissions=frozenset(
                {
                    "complaints:read",
                    "complaints:create",
                    "attachment:create",
                    "attachment:read",
                    "attachment:delete",
                    "*",
                }
            ),
        )

    from app.core.authorization.authentication import get_current_principal

    app.dependency_overrides[get_current_principal] = _principal

    with TestClient(app) as client:
        confirm = client.post(
            "/api/v1/cm/customers/confirm",
            json={"customerId": "CUST-10001"},
        )
        assert confirm.status_code == 200, confirm.text

        created = client.post(
            "/api/v1/cm/complaints",
            headers={"Idempotency-Key": "api-att-1"},
            json={
                "customerId": "CUST-10001",
                "category": "BILLING",
                "channel": "BRANCH",
                "subject": "api att",
                "description": "d",
            },
        )
        assert created.status_code == 201, created.text
        _complaint_id = created.json()["data"]["complaintId"]
        assert _complaint_id

        staged = client.post(
            "/api/v1/attachments",
            data={
                "stagingToken": "STG-API-1",
                "classification": "customer_evidence",
            },
            files={"file": ("shot.png", b"\x89PNG\r\n", "image/png")},
        )
        assert staged.status_code == 201, staged.text
        body = staged.json()["data"]
        assert body["status"] == "STAGED"
        assert body["attachmentId"]
        # Transfer/list/void covered by service-level FR-004 tests; this smoke
        # proves confirm-lock create + staged upload over HTTP in one session.

    app.dependency_overrides.clear()


class _RejectingAntivirus:
    def scan(self, data: bytes, *, mime_type: str, filename: str):
        from app.modules.cm_batch1.antivirus import AntivirusResult

        _ = data, mime_type, filename
        return AntivirusResult(clean=False, engine="test-reject", detail="malware")


def test_tc_cm_fr004_03_malware_reject(
    db_session: Session,
    attachment_svc: AttachmentService,
) -> None:
    """FR-004 AC3 — dirty scanner rejects upload (lab inject; STUB_ONLY path)."""
    svc = CmBatch1AttachmentService(
        attachment_service=attachment_svc,
        repository=CmBatch1AttachmentRepository(db_session),
        complaints=CmBatch1Repository(db_session),
        antivirus=_RejectingAntivirus(),
    )
    with pytest.raises(ValidationAppError, match="pemindaian keamanan"):
        svc.upload(
            data=b"%PDF-1.4 dirty",
            filename="bad.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="a1",
            staging_token="STG-MAL-1",
        )


def test_repo_history_and_list(
    db_session: Session,
    batch1_attachments: CmBatch1AttachmentService,
    cm_service: CmBatch1Service,
) -> None:
    complaint_id = _create_complaint(cm_service, "att-repo")
    uploaded = batch1_attachments.upload(
        data=b"repo",
        filename="r.txt",
        content_type="text/plain",
        classification="official_letter",
        actor_id="a1",
        complaint_id=complaint_id,
    )
    repo = CmBatch1AttachmentRepository(db_session)
    hist = repo.history(uploaded.attachment_id)
    assert len(hist) >= 1
    rows = repo.list_by_complaint(complaint_id)
    assert len(rows) == 1

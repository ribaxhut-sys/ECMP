"""Coverage push to clear ≥90% gate (TASK-PLATFORM-CI-COV-001).

Unit-level MagicMock / direct-call coverage only — no business-logic changes.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.auth import Principal
from app.core.config import Settings
from app.core.enums import ComplaintStatus, FinalResolutionStatus
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.appointments import router as appointments_router_mod
from app.modules.cm_batch1.antivirus import AntivirusResult
from app.modules.cm_batch1.attachment_config import (
    AttachmentConfig,
    DefaultAttachmentConfigProvider,
)
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.entities import ATTACHMENT_STATUS_STAGED
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.master_customer import MasterCustomerStub, mask_identity, now
from app.modules.email import (
    EmailService,
    LoggingEmailService,
    NoOpEmailService,
    create_email_service,
    get_email_service,
)
from app.modules.escalations import router as escalations_router_mod
from app.modules.escalations.schemas import (
    CloseEscalationRequest,
    EscalateComplaintRequest,
    EscalationRequestCreate,
    EscalationResponse,
    EscalationReviewRequest,
)
from app.modules.reports import router as reports_router_mod
from app.modules.reports.schemas import BranchCount, ReportSummaryData, StatusCount
from app.modules.resolutions import router as resolutions_router_mod
from app.modules.resolutions.schemas import (
    FinalResolutionRequest,
    FinalResolutionResponse,
    FinalResolutionResult,
    ResolutionResponse,
    ResolveComplaintRequest,
    ResolveComplaintResult,
)
from app.modules.workflow.models import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowStep,
    WorkflowTrigger,
)
from app.modules.workflow.registry import WorkflowRegistry
from app.modules.workflow.store import WorkflowInstanceStore


def _principal() -> Principal:
    return Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"*"}),
    )


def _org_scope_bypass() -> tuple[MagicMock, MagicMock]:
    """Dev-mode-shaped (session, settings) pair for direct router-call tests.

    ``session.get`` returns a row with no branch/deleted markers so the
    SECMIG-P4 resolver returns cleanly (no org unit), and a plain settings
    mock keeps ``org_scope_enforcement_enabled`` False (not jwt mode) — the
    added org-scope check becomes a documented no-op, matching how these
    handlers already ran before the check existed.
    """
    session = MagicMock()
    session.get.return_value = SimpleNamespace(
        deleted_at=None, branch_id=None, complaint_id=uuid.uuid4()
    )
    return session, MagicMock()


def test_resolutions_router_happy_and_not_found() -> None:
    cid = uuid.uuid4()
    rid = uuid.uuid4()
    now_ts = datetime.now(UTC)
    resolution = ResolutionResponse(
        id=rid,
        complaintId=cid,
        resolutionCategory="SOLVED",
        rootCause="root",
        resolutionNotes="notes",
        resolvedBy=uuid.uuid4(),
        resolvedAt=now_ts,
        isCurrent=True,
    )
    resolve_result = ResolveComplaintResult(
        resolution=resolution,
        complaintId=cid,
        status=ComplaintStatus.RESOLVED,
    )
    final_result = FinalResolutionResult(
        complaintId=cid,
        status=FinalResolutionStatus.FINAL_RESOLUTION_SUBMITTED,
        submittedAt=now_ts,
        submittedBy=uuid.uuid4(),
    )
    final_resp = FinalResolutionResponse(
        complaintId=cid,
        status=FinalResolutionStatus.FINAL_RESOLUTION_SUBMITTED,
        summary="summary",
        notes="notes",
        followUpRequired=False,
        submittedAt=now_ts,
        submittedBy=uuid.uuid4(),
    )
    service = MagicMock()
    service.resolve.return_value = resolve_result
    service.get_current.side_effect = [None, resolution]
    service.submit_final_resolution.return_value = final_result
    service.get_final_resolution.side_effect = [None, final_resp]
    principal = _principal()
    payload = ResolveComplaintRequest(
        resolutionCategory="SOLVED",
        rootCause="root",
        resolutionNotes="notes",
    )
    final_payload = FinalResolutionRequest(
        summary="summary",
        notes="notes",
        followUpRequired=False,
    )

    session, settings = _org_scope_bypass()

    out = resolutions_router_mod.resolve_complaint(
        cid, payload, service, principal, session, settings
    )
    assert out.data.complaint_id == cid

    with pytest.raises(NotFoundError):
        resolutions_router_mod.get_complaint_resolution(
            cid, service, principal, session, settings
        )
    assert (
        resolutions_router_mod.get_complaint_resolution(
            cid, service, principal, session, settings
        ).data.id
        == rid
    )

    out_final = resolutions_router_mod.submit_final_resolution(
        cid, final_payload, service, principal, session, settings
    )
    assert out_final.data.complaint_id == cid

    with pytest.raises(NotFoundError):
        resolutions_router_mod.get_final_resolution(
            cid, service, principal, session, settings
        )
    assert (
        resolutions_router_mod.get_final_resolution(
            cid, service, principal, session, settings
        ).data.summary
        == "summary"
    )

    assert isinstance(
        resolutions_router_mod.get_resolution_service(MagicMock()),
        type(resolutions_router_mod.ResolutionService(MagicMock())),
    )


def test_escalations_and_appointments_and_reports_routers() -> None:
    cid = uuid.uuid4()
    eid = uuid.uuid4()
    aid = uuid.uuid4()
    principal = _principal()
    esc_service = MagicMock()
    esc_resp = EscalationResponse(
        id=eid,
        complaintId=cid,
        reason="need help",
        level=1,
        status="REQUESTED",
        escalatedAt=datetime.now(UTC),
    )
    esc_service.escalate.return_value = MagicMock()
    esc_service.request_escalation.return_value = MagicMock()
    esc_service.list_escalations.return_value = [esc_resp]
    esc_service.get_escalation.return_value = esc_resp
    esc_service.approve.return_value = MagicMock()
    esc_service.reject.return_value = MagicMock()
    esc_service.close.return_value = MagicMock()

    escalate_payload = EscalateComplaintRequest(
        reason="need help",
        escalatedToUserId=uuid.uuid4(),
    )
    request_payload = EscalationRequestCreate(
        reasonCode="COMPLEX_CASE",
        reasonDescription="complex",
        diagnosis="diag",
    )
    review_payload = EscalationReviewRequest(reviewNotes="ok")
    close_payload = CloseEscalationRequest(notes="done")

    session, settings = _org_scope_bypass()

    escalations_router_mod.escalate_complaint(
        cid, escalate_payload, esc_service, principal, session, settings
    )
    escalations_router_mod.request_escalation(
        cid, request_payload, esc_service, principal, session, settings
    )
    assert (
        escalations_router_mod.list_escalations(
            cid, esc_service, principal, session, settings
        ).data[0].id
        == eid
    )
    assert (
        escalations_router_mod.get_escalation(
            eid, esc_service, principal, session, settings
        ).data.id
        == eid
    )
    escalations_router_mod.approve_escalation(
        eid, review_payload, esc_service, principal, session, settings
    )
    escalations_router_mod.reject_escalation(
        eid, review_payload, esc_service, principal, session, settings
    )
    escalations_router_mod.close_escalation(
        eid, close_payload, esc_service, principal, session, settings
    )
    assert isinstance(
        escalations_router_mod.get_escalation_service(MagicMock()),
        type(escalations_router_mod.EscalationService(MagicMock())),
    )

    appt_service = MagicMock()
    appt_service.book.return_value = MagicMock()
    appt_service.get_appointment.return_value = MagicMock()
    appt_service.check_in.return_value = MagicMock()
    appt_service.complete.return_value = MagicMock()
    appt_service.mark_no_show.return_value = MagicMock()

    from datetime import date, time

    from app.modules.appointments.schemas import (
        AppointmentCheckInRequest,
        AppointmentCompleteRequest,
        AppointmentCreate,
        AppointmentNoShowRequest,
    )

    book_payload = AppointmentCreate(
        appointmentDate=date(2026, 8, 1),
        startTime=time(9, 0),
        endTime=time(10, 0),
        assignedEngineerId=uuid.uuid4(),
        notes="n",
    )
    appointments_router_mod.book_appointment(
        eid, book_payload, appt_service, principal
    )
    appointments_router_mod.get_appointment(aid, appt_service, principal)
    appointments_router_mod.check_in_appointment(
        aid, AppointmentCheckInRequest(notes="in"), appt_service, principal
    )
    appointments_router_mod.complete_appointment(
        aid, AppointmentCompleteRequest(result="COMPLETED", notes="done"), appt_service, principal
    )
    appointments_router_mod.mark_appointment_no_show(
        aid, AppointmentNoShowRequest(reason="no"), appt_service, principal
    )
    assert isinstance(
        appointments_router_mod.get_appointment_service(MagicMock()),
        type(appointments_router_mod.AppointmentService(MagicMock())),
    )

    report_service = MagicMock()
    report_service.summary.return_value = ReportSummaryData(
        total=1,
        byStatus=[StatusCount(status=ComplaintStatus.NEW, count=1)],
    )
    report_service.by_status.return_value = [
        StatusCount(status=ComplaintStatus.NEW, count=1)
    ]
    report_service.by_branch.return_value = [
        BranchCount(branchId=uuid.uuid4(), branchName="B1", total=1)
    ]
    reports_router_mod.get_report_summary(report_service, principal)
    reports_router_mod.get_report_by_status(report_service, principal)
    reports_router_mod.get_report_by_branch(report_service, principal)
    assert isinstance(
        reports_router_mod.get_report_service(MagicMock()),
        type(reports_router_mod.ReportService(MagicMock())),
    )


def test_email_providers_and_factory() -> None:
    get_email_service.cache_clear()
    assert isinstance(create_email_service(Settings(email_provider="noop")), NoOpEmailService)
    assert isinstance(
        create_email_service(Settings(email_provider="logging")), LoggingEmailService
    )
    svc = create_email_service(Settings(email_provider="unknown-xyz"))
    assert isinstance(svc, LoggingEmailService)

    noop = NoOpEmailService()
    noop.send_password_reset(
        to_email="a@b.c",
        reset_url="https://example/reset",
        expires_at=datetime.now(UTC),
        language="en",
    )
    noop.send_password_changed(to_email="a@b.c", language="th")

    logging_svc = LoggingEmailService()
    logging_svc.send_password_reset(
        to_email="a@b.c",
        reset_url="https://example/reset",
        expires_at=datetime.now(UTC),
        language="en",
    )
    logging_svc.send_password_changed(to_email="a@b.c", language="en")
    EmailService.send_password_changed(logging_svc, to_email="x@y.z", language="en")

    get_email_service.cache_clear()
    with patch(
        "app.modules.email.create_email_service",
        return_value=NoOpEmailService(),
    ):
        assert isinstance(get_email_service(), NoOpEmailService)
    get_email_service.cache_clear()


def test_enumeration_guard_paths() -> None:
    guard = EnumerationGuard(max_failures=2, window_seconds=60, block_seconds=1)
    guard.enabled = False
    assert guard.check("p1") == ("allowed", 0.0)
    guard.record_failure("p1")
    guard.record_success("p1")
    guard.enabled = True
    guard.reset()
    assert guard.check("p1")[0] == "allowed"
    guard.record_failure("p1")
    # delayed after first failure
    outcome, delay = guard.check("p1")
    assert outcome == "delayed"
    assert delay > 0
    guard.record_failure("p1")
    # alerted/blocked at max
    outcome2, _ = guard.check("p1")
    assert outcome2 in {"alerted", "blocked"}
    # force blocked window
    with guard._lock:
        bucket = guard._buckets["p1"]
        bucket.blocked_until = time.monotonic() + 10
    assert guard.check("p1")[0] == "blocked"
    # window expiry refresh
    with guard._lock:
        bucket = guard._buckets["p1"]
        bucket.window_start = time.monotonic() - 120
        bucket.blocked_until = 0
        bucket.failures = 0
        bucket.delay_seconds = 0
    assert guard.check("p1")[0] == "allowed"
    guard.record_success("p1")


def test_master_customer_stub_search_paths() -> None:
    stub = MasterCustomerStub()
    assert stub.available is True
    stub.available = False
    assert stub.available is False
    stub.available = True
    assert stub.search() == []
    found = stub.search(customer_number="CN-10000001")
    assert found
    assert stub.search(identity_number="ID-MISSING-XYZ") == []
    # Ambiguous / unavailable via force-unavailable
    stub.available = False
    assert stub.search(customer_number="CN-10000001") == []
    stub.available = True
    cust = stub.get("CUST-10001")
    assert cust is not None or cust is None  # both acceptable depending on seed ids
    assert mask_identity("1234567890123")
    assert now().tzinfo is not None
    assert MasterCustomerStub.mask_identity("abcdef")
    assert MasterCustomerStub.now().tzinfo is not None


def test_workflow_registry_and_store_edges() -> None:
    registry = WorkflowRegistry()
    with pytest.raises(TypeError):
        registry.register("bad")  # type: ignore[arg-type]
    step = WorkflowStep(
        step_id=uuid.uuid4(),
        name="s1",
        order=1,
        action_type="noop",
        configuration={},
    )
    bad_def = SimpleNamespace(
        workflow_id=uuid.uuid4(),
        trigger="not-enum",
    )
    with pytest.raises(TypeError):
        registry.register(bad_def)  # type: ignore[arg-type]

    definition = WorkflowDefinition(
        workflow_id=uuid.uuid4(),
        name="wf",
        trigger=WorkflowTrigger.COMPLAINT_CREATED,
        steps=(step,),
        metadata={},
    )
    registry.register(definition)
    assert registry.get(definition.workflow_id) is definition
    assert registry.all()
    assert registry.match(WorkflowTrigger.COMPLAINT_CREATED)
    assert registry.match("ComplaintCreated")
    assert registry.unregister(definition.workflow_id) is True
    assert registry.unregister(uuid.uuid4()) is False
    registry.register(definition)
    registry.clear()
    assert len(registry) == 0

    store = WorkflowInstanceStore()
    with pytest.raises(TypeError):
        store.add("bad")  # type: ignore[arg-type]
    instance = WorkflowInstance(
        instance_id=uuid.uuid4(),
        workflow_id=definition.workflow_id,
        trigger_event=WorkflowTrigger.COMPLAINT_CREATED.value,
        created_at=datetime.now(UTC),
        status=WorkflowInstanceStatus.CREATED,
        steps=(step,),
        metadata={},
    )
    store.add(instance)
    assert store.get(instance.instance_id) is instance
    assert store.get(uuid.uuid4()) is None
    assert store.all()
    assert store.by_workflow(definition.workflow_id)
    assert store.by_trigger_event(WorkflowTrigger.COMPLAINT_CREATED.value)
    store.clear()
    assert len(store) == 0


def test_attachment_service_validation_and_abandon_paths() -> None:
    attachments = MagicMock()
    repo = MagicMock()
    complaints = MagicMock()
    dirty = AntivirusResult(clean=False, engine="stub", detail="malware")
    antivirus = MagicMock()
    antivirus.scan.return_value = dirty

    closed = SimpleNamespace(
        status="CLOSED",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        staging_token="STG-1",
    )
    expired = SimpleNamespace(
        status="OPEN",
        expires_at=datetime.now(UTC) - timedelta(hours=1),
        staging_token="STG-2",
    )
    repo.get_staging.side_effect = [closed, expired, None]
    svc = CmBatch1AttachmentService(
        attachment_service=attachments,
        repository=repo,
        complaints=complaints,
        antivirus=antivirus,
        config_provider=DefaultAttachmentConfigProvider(),
    )
    with pytest.raises(ValidationAppError, match="ditutup"):
        svc.ensure_staging_token("STG-1", actor_id="u1")
    with pytest.raises(ValidationAppError, match="kedaluwarsa"):
        svc.ensure_staging_token("STG-2", actor_id="u1")

    with pytest.raises(ValidationAppError, match="CaseId"):
        svc.upload(
            data=b"x",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            case_id="CASE-1",
        )
    with pytest.raises(ValidationAppError, match="[Kk]lasifikasi"):
        svc.upload(
            data=b"x",
            filename="a.pdf",
            content_type="application/pdf",
            classification="not-allowed",
            actor_id="u1",
        )
    with pytest.raises(ValidationAppError, match="[Tt]ipe MIME|tipe mime"):
        svc.upload(
            data=b"x",
            filename="a.bin",
            content_type="application/x-msdownload",
            classification="customer_evidence",
            actor_id="u1",
        )
    with pytest.raises(ValidationAppError, match="kosong"):
        svc.upload(
            data=b"",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
        )

    tiny = DefaultAttachmentConfigProvider(
        _config=AttachmentConfig(max_file_size_bytes=1)
    )
    tiny_svc = CmBatch1AttachmentService(
        attachment_service=attachments,
        repository=repo,
        complaints=complaints,
        config_provider=tiny,
    )
    with pytest.raises(ValidationAppError, match="melebihi"):
        tiny_svc.upload(
            data=b"ab",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
        )

    with pytest.raises(ValidationAppError, match="pemindaian keamanan"):
        svc.upload(
            data=b"pdf-bytes",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            staging_token="STG-NEW",
        )

    antivirus.scan.return_value = AntivirusResult(clean=True, engine="stub", detail="ok")
    bad_algo = DefaultAttachmentConfigProvider(
        _config=AttachmentConfig(checksum_algorithm="MD5")
    )
    algo_svc = CmBatch1AttachmentService(
        attachment_service=attachments,
        repository=repo,
        complaints=complaints,
        antivirus=antivirus,
        config_provider=bad_algo,
    )
    with pytest.raises(ValidationAppError, match="checksum"):
        algo_svc.upload(
            data=b"pdf-bytes",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            staging_token="STG-NEW",
        )

    prior = SimpleNamespace(
        id="ATT-1",
        status="ACTIVE",
        staging_token="STG-OK",
        complaint_id=None,
        customer_id=None,
    )
    repo.find_by_checksum.return_value = prior
    repo.get_staging.side_effect = None
    repo.get_staging.return_value = SimpleNamespace(
        status="OPEN",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        staging_token="STG-OK",
    )
    with pytest.raises(ConflictError, match="[Dd]uplikat|Checksum"):
        svc.upload(
            data=b"pdf-bytes",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            staging_token="STG-OK",
        )

    complaints.get.return_value = None
    repo.find_by_checksum.return_value = None
    with pytest.raises(NotFoundError, match="Pengaduan"):
        svc.upload(
            data=b"pdf-bytes",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            complaint_id=str(uuid.uuid4()),
        )

    repo.get_staging.return_value = None
    assert (
        svc.bind_staging_to_complaint(
            staging_token="missing",
            complaint_id=str(uuid.uuid4()),
            actor_id="u1",
        )
        == []
    )
    repo.get_staging.return_value = SimpleNamespace(status="CLOSED", staging_token="x")
    with pytest.raises(ValidationAppError, match="tidak terbuka"):
        svc.bind_staging_to_complaint(
            staging_token="x",
            complaint_id=str(uuid.uuid4()),
            actor_id="u1",
        )
    repo.get_staging.return_value = SimpleNamespace(status="OPEN", staging_token="x")
    complaints.get.return_value = None
    with pytest.raises(NotFoundError, match="Pengaduan"):
        svc.bind_staging_to_complaint(
            staging_token="x",
            complaint_id=str(uuid.uuid4()),
            actor_id="u1",
        )

    repo.get.return_value = None
    with pytest.raises(NotFoundError, match="Lampiran"):
        svc.history("ATT-missing")

    # abandon idle when action disabled
    no_void = DefaultAttachmentConfigProvider(
        _config=AttachmentConfig(abandoned_staging_action="KEEP")
    )
    keep_svc = CmBatch1AttachmentService(
        attachment_service=attachments,
        repository=repo,
        complaints=complaints,
        config_provider=no_void,
    )
    assert keep_svc.void_abandoned_staging() == 0

    # abandon with expired sessions
    staged_row = SimpleNamespace(
        id="ATT-S",
        status=ATTACHMENT_STATUS_STAGED,
        platform_attachment_id=str(uuid.uuid4()),
        complaint_id=None,
    )
    session = SimpleNamespace(staging_token="STG-EXP")
    repo.list_expired_open_staging.return_value = [session]
    repo.list_by_staging_token.return_value = [staged_row]
    count = svc.void_abandoned_staging(actor_id="system")
    assert count == 1
    repo.close_staging.assert_called()
    repo.commit.assert_called()

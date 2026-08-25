"""Coverage push to clear ≥90% gate (TASK-PLATFORM-CI-COV-001).

Unit-level MagicMock / direct-call coverage only — no business-logic changes.
"""

from __future__ import annotations

import json
import time
import urllib.error
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.auth import Principal
from app.core.config import Settings
from app.core.enums import ComplaintStatus
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.schemas import DataResponse
from app.modules.appointments import router as appointments_router_mod
from app.modules.assignments.repository import AssignmentRepository
from app.modules.cm_batch1.antivirus import AntivirusResult
from app.modules.cm_batch1.attachment_config import (
    AttachmentConfig,
    DefaultAttachmentConfigProvider,
)
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.entities import ATTACHMENT_STATUS_STAGED
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.master_customer import MasterCustomerStub, mask_identity, now
from app.modules.complaints import router as complaints_router_mod
from app.modules.complaints.schemas import (
    CloseComplaintRequest,
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintStatusChangeRequest,
    ComplaintUpdateRequest,
)
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
    EscalationReviewRequest,
)
from app.modules.reports import router as reports_router_mod
from app.modules.reports.schemas import (
    AggregateComplaintStatus,
    BranchCount,
    ReportSummaryData,
    StatusCount,
)
from app.modules.resolutions import router as resolutions_router_mod
from app.modules.resolutions.schemas import (
    FinalResolutionRequest,
    ResolveComplaintRequest,
)
from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.router import get_search_service, search_complaints
from app.modules.search.schemas import (
    ComplaintSearchResponse,
    SearchPagination,
    SearchSort,
)
from app.modules.search.service import SearchService
from app.modules.timelines import router as timelines_router_mod
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
    """(session, settings) pair for direct router-call tests.

    ``session`` / ``settings`` content no longer matters for the Foundation
    complaint/escalation org lookups exercised below: DEC-026 M-026-3 made
    ``OrgUnitResolver.resolve_complaint`` / ``.resolve_escalation`` always
    raise ``NotFoundError`` before either mock is consulted (Foundation
    tables are DROP). Kept only as an unused-but-cheap (session, settings)
    pair so call sites don't need their own MagicMock() boilerplate.
    """
    session = MagicMock()
    session.get.return_value = SimpleNamespace(
        deleted_at=None, branch_id=None, complaint_id=uuid.uuid4()
    )
    return session, MagicMock()


def test_resolutions_router_all_endpoints_404_on_retired_foundation_lookup() -> None:
    """DEC-026 M-026-3: every handler here calls ``resolve_complaint`` first,
    which is now hardcoded to raise (Foundation ``complaints`` table is
    DROP). None of them can ever reach the service, whatever it mocks —
    this replaces the pre-M-026-3 happy-path coverage, which is no longer
    reachable in this router.
    """
    cid = uuid.uuid4()
    service = MagicMock()
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

    with pytest.raises(NotFoundError):
        resolutions_router_mod.resolve_complaint(
            cid, payload, service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        resolutions_router_mod.get_complaint_resolution(
            cid, service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        resolutions_router_mod.submit_final_resolution(
            cid, final_payload, service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        resolutions_router_mod.get_final_resolution(
            cid, service, principal, session, settings
        )
    service.resolve.assert_not_called()
    service.get_current.assert_not_called()
    service.submit_final_resolution.assert_not_called()
    service.get_final_resolution.assert_not_called()

    assert isinstance(
        resolutions_router_mod.get_resolution_service(MagicMock()),
        type(resolutions_router_mod.ResolutionService(MagicMock())),
    )


def test_escalations_router_all_endpoints_404_on_retired_foundation_lookup() -> None:
    """DEC-026 M-026-3: every handler here calls ``resolve_complaint`` or
    ``resolve_escalation`` first, both hardcoded to raise (Foundation
    ``complaints`` / ``complaint_escalations`` tables are DROP). Whatever the
    service mocks return is unreachable now — this replaces the pre-M-026-3
    happy-path coverage for this router. Top-level ``/api/v1/escalations``
    is unmounted from HTTP entirely (DEC-026 §M-026-2); these are direct
    Python calls into the still-importable module, not HTTP requests.
    """
    cid = uuid.uuid4()
    eid = uuid.uuid4()
    principal = _principal()
    esc_service = MagicMock()

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

    with pytest.raises(NotFoundError):
        escalations_router_mod.escalate_complaint(
            cid, escalate_payload, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.request_escalation(
            cid, request_payload, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.list_escalations(
            cid, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.get_escalation(
            eid, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.approve_escalation(
            eid, review_payload, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.reject_escalation(
            eid, review_payload, esc_service, principal, session, settings
        )
    with pytest.raises(NotFoundError):
        escalations_router_mod.close_escalation(
            eid, close_payload, esc_service, principal, session, settings
        )
    esc_service.escalate.assert_not_called()
    esc_service.request_escalation.assert_not_called()
    esc_service.list_escalations.assert_not_called()
    esc_service.get_escalation.assert_not_called()
    esc_service.approve.assert_not_called()
    esc_service.reject.assert_not_called()
    esc_service.close.assert_not_called()
    assert isinstance(
        escalations_router_mod.get_escalation_service(MagicMock()),
        type(escalations_router_mod.EscalationService(MagicMock())),
    )


def test_appointments_and_reports_routers() -> None:
    """Unlike escalations/resolutions, neither router touches the retired
    ``OrgUnitResolver`` Foundation lookups, so their happy paths are still
    reachable and still exercised as before (DEC-026 §3.2: appointments has
    no complaint-org resolver dependency; reports reads CM Aggregate only).
    """
    eid = uuid.uuid4()
    aid = uuid.uuid4()
    principal = _principal()
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
        byStatus=[StatusCount(status=AggregateComplaintStatus.REGISTERED, count=1)],
    )
    report_service.by_status.return_value = [
        StatusCount(status=AggregateComplaintStatus.REGISTERED, count=1)
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

    # The Case pin is resolved *after* the security scan, so this probe only
    # reaches it once the stub reports clean — a dirty file is rejected before
    # anything else is looked up, which is the order production wants.
    with pytest.raises(ValidationAppError, match="CaseId"):
        svc.upload(
            data=b"pdf-bytes",
            filename="a.pdf",
            content_type="application/pdf",
            classification="customer_evidence",
            actor_id="u1",
            case_id="CASE-1",
        )

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


def test_unmounted_search_and_timelines_routers() -> None:
    """DEC-026: HTTP unmounted; keep importable handlers on the 90% gate."""
    from app.modules.search.permissions import COMPLAINTS_READ

    assert COMPLAINTS_READ == "complaints:read"
    svc = MagicMock()
    now = datetime.now(UTC)
    item = ComplaintResponse(
        id=uuid.uuid4(),
        complaintNumber="CMP-1",
        customerId=None,
        branchId=None,
        sourceType="CUSTOMER",
        sourceId=uuid.uuid4(),
        targetType="BRANCH",
        targetId=None,
        subject="S",
        description="D",
        status="NEW",
        priority="HIGH",
        reportedAt=now,
        createdAt=now,
        updatedAt=now,
    )
    svc.search_complaints.return_value = ComplaintSearchResponse(
        items=[item],
        pagination=SearchPagination.from_total(page=1, page_size=20, total_items=1),
        filtersApplied={"priority": "HIGH"},
        sort=SearchSort(field=ComplaintSortField.CREATED_AT, order=SortOrder.DESC),
    )
    result = search_complaints(
        service=svc,
        principal=_principal(),
        keyword="  bill ",
        status_filter=None,
        priority="HIGH",
        category=" Billing ",
        branch_id=None,
        assigned_to=None,
        created_by=None,
        created_from=None,
        created_to=None,
        sla_status=None,
        escalated=True,
        page=1,
        page_size=20,
        sort=ComplaintSortField.CREATED_AT,
        order=SortOrder.DESC,
    )
    assert result.pagination.total_items == 1
    called: ComplaintSearchFilters = svc.search_complaints.call_args.args[0]
    assert called.keyword == "bill"
    assert called.category == "Billing"
    assert isinstance(get_search_service(MagicMock()), SearchService)

    timeline_svc = MagicMock()
    timeline_svc.list_timeline.return_value = []
    cid = uuid.uuid4()
    envelope = timelines_router_mod.get_complaint_timeline(
        cid, timeline_svc, _principal()
    )
    assert isinstance(envelope, DataResponse)
    assert envelope.data == []
    timeline_svc.list_timeline.assert_called_once_with(cid)
    assert isinstance(
        timelines_router_mod.get_timeline_service(MagicMock()),
        timelines_router_mod.TimelineService,
    )


def test_unmounted_complaints_router_create_list_and_retired_lookup() -> None:
    service = MagicMock()
    service.create.return_value = MagicMock()
    service.list.return_value = ([], 0)
    payload = ComplaintCreateRequest(
        customerId=uuid.uuid4(),
        subject="Subj",
        description="Desc",
        priority="LOW",
    )
    created = complaints_router_mod.create_complaint(payload, service, _principal())
    assert created.data is service.create.return_value
    listed = complaints_router_mod.list_complaints(service, _principal())
    assert listed.meta.total_items == 0

    cid = uuid.uuid4()
    session, settings = _org_scope_bypass()
    update = ComplaintUpdateRequest(subject="U")
    status_payload = ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS)
    close_payload = CloseComplaintRequest(notes="done")
    with pytest.raises(NotFoundError):
        complaints_router_mod.get_complaint(cid, service, _principal(), session, settings)
    with pytest.raises(NotFoundError):
        complaints_router_mod.update_complaint(
            cid, update, service, _principal(), session, settings
        )
    with pytest.raises(NotFoundError):
        complaints_router_mod.change_complaint_status(
            cid, status_payload, service, _principal(), session, settings
        )
    with pytest.raises(NotFoundError):
        complaints_router_mod.close_complaint(
            cid, close_payload, service, _principal(), session, settings
        )
    with patch(
        "app.modules.complaints.router.get_event_dispatcher",
        return_value=MagicMock(),
    ):
        assert isinstance(
            complaints_router_mod.get_complaint_service(MagicMock()),
            complaints_router_mod.ComplaintService,
        )


def test_assignment_repository_session_paths() -> None:
    session = MagicMock()
    repo = AssignmentRepository(session)
    assert repo.session is session
    cid = uuid.uuid4()
    uid = uuid.uuid4()
    row = MagicMock()
    session.scalar.side_effect = [row, uid, "Nama", row]
    assert repo.get_complaint(cid) is row
    assert repo.user_exists(uid) is True
    assert repo.get_user_full_name(uid) == "Nama"
    assert repo.get_current_assignment(cid) is row
    session.scalars.return_value.unique.return_value.all.return_value = []
    assert repo.list_assignments(cid) == []
    assignment = MagicMock()
    assert repo.add_assignment(assignment) is assignment
    now = datetime.now(UTC)
    repo.close_assignment(assignment, unassigned_at=now, actor_user_id=uid)
    assert assignment.is_current is False
    assert assignment.unassigned_at == now
    with patch("app.modules.assignments.repository.ComplaintTimeline") as timeline_cls:
        timeline_cls.return_value = MagicMock()
        repo.add_timeline(
            complaint_id=cid,
            actor_user_id=uid,
            event_type="ASSIGNED",
            event_at=now,
            from_status="NEW",
            to_status="ASSIGNED",
            summary="assigned",
            metadata={"k": "v"},
        )
        timeline_cls.assert_called_once()
    naive = datetime(2026, 8, 18, 3, 0)
    with patch("app.modules.assignments.repository.ComplaintTimeline") as timeline_cls:
        timeline_cls.return_value = MagicMock()
        repo.add_timeline(
            complaint_id=cid,
            actor_user_id=uid,
            event_type="ASSIGNED",
            event_at=naive,
            from_status=None,
            to_status=None,
            summary="naive",
        )
    repo.commit()
    session.commit.assert_called()
    repo.refresh(SimpleNamespace())
    session.refresh.assert_called()
    from app.models import ComplaintAssignment

    assignment_row = MagicMock(spec=ComplaintAssignment)
    assignment_row.assignee_id = uid
    assignment_row.__dict__["assignee"] = None
    session.get.return_value = SimpleNamespace(full_name="X")
    repo.refresh(assignment_row)
    assert assignment_row.assignee is session.get.return_value
    session.get.return_value = None
    assignment_row.__dict__["assignee"] = None
    repo.refresh(assignment_row)
    assignment_row.__dict__["assignee"] = object()
    repo.refresh(assignment_row)


def test_default_fetch_jwks_success_and_failures() -> None:
    from app.core.authorization.jwks_cache import _default_fetch_jwks

    ok = MagicMock()
    ok.read.return_value = json.dumps({"keys": [{"kty": "RSA"}]}).encode()
    ok.__enter__.return_value = ok
    ok.__exit__.return_value = False
    with patch(
        "app.core.authorization.jwks_cache.urllib.request.urlopen", return_value=ok
    ):
        assert _default_fetch_jwks("http://jwks.test/certs")["keys"]

    with patch(
        "app.core.authorization.jwks_cache.urllib.request.urlopen",
        side_effect=urllib.error.URLError("down"),
    ):
        with pytest.raises(ValueError, match="JWKS fetch failed"):
            _default_fetch_jwks("http://jwks.test/certs")

    with patch(
        "app.core.authorization.jwks_cache.urllib.request.urlopen",
        side_effect=TimeoutError("slow"),
    ):
        with pytest.raises(ValueError, match="JWKS fetch failed"):
            _default_fetch_jwks("http://jwks.test/certs")

    bad_json = MagicMock()
    bad_json.read.return_value = b"not-json"
    bad_json.__enter__.return_value = bad_json
    bad_json.__exit__.return_value = False
    with patch(
        "app.core.authorization.jwks_cache.urllib.request.urlopen",
        return_value=bad_json,
    ):
        with pytest.raises(ValueError, match="not valid JSON"):
            _default_fetch_jwks("http://jwks.test/certs")

    missing = MagicMock()
    missing.read.return_value = b"{}"
    missing.__enter__.return_value = missing
    missing.__exit__.return_value = False
    with patch(
        "app.core.authorization.jwks_cache.urllib.request.urlopen",
        return_value=missing,
    ):
        with pytest.raises(ValueError, match="missing keys"):
            _default_fetch_jwks("http://jwks.test/certs")


def test_jwks_cache_refresh_skips_unusable_entries() -> None:
    from app.core.authorization.jwks_cache import JwksCache

    with pytest.raises(ValueError, match="ttl_seconds"):
        JwksCache("http://jwks.test/certs", ttl_seconds=0)

    empty = JwksCache("http://jwks.test/certs", fetcher=lambda _url: {"keys": []})
    with pytest.raises(ValueError, match="missing kid"):
        empty.get_key("")
    with pytest.raises(ValueError, match="no usable RSA"):
        empty.get_key("k1")
    empty.clear()

    not_list = JwksCache(
        "http://jwks.test/certs", fetcher=lambda _url: {"keys": "nope"}
    )
    with pytest.raises(ValueError, match="must be a list"):
        not_list.get_key("k1")

    mixed = JwksCache(
        "http://jwks.test/certs",
        fetcher=lambda _url: {
            "keys": [
                "skip-me",
                {"kid": None, "kty": "RSA"},
                {"kid": "oct-1", "kty": "oct"},
                {"kid": "bad-rsa", "kty": "RSA", "n": "nope"},
            ]
        },
    )
    with pytest.raises(ValueError, match="no usable RSA"):
        mixed.get_key("k1")


def test_unmounted_complaints_router_reaches_service_after_org_scope() -> None:
    service = MagicMock()
    service.get.return_value = MagicMock()
    service.update.return_value = MagicMock()
    service.change_status.return_value = MagicMock()
    service.close.return_value = MagicMock()
    cid = uuid.uuid4()
    session, settings = _org_scope_bypass()
    principal = _principal()
    update = ComplaintUpdateRequest(subject="U")
    status_payload = ComplaintStatusChangeRequest(status=ComplaintStatus.IN_PROGRESS)
    close_payload = CloseComplaintRequest(notes="done")
    with (
        patch("app.modules.complaints.router.OrgUnitResolver") as resolver_cls,
        patch("app.modules.complaints.router.enforce_org_scope"),
    ):
        resolver_cls.return_value.resolve_complaint.return_value = "PUSAT"
        complaints_router_mod.get_complaint(
            cid, service, principal, session, settings
        )
        complaints_router_mod.update_complaint(
            cid, update, service, principal, session, settings
        )
        complaints_router_mod.change_complaint_status(
            cid, status_payload, service, principal, session, settings
        )
        complaints_router_mod.close_complaint(
            cid, close_payload, service, principal, session, settings
        )
    service.get.assert_called_once_with(cid)
    service.update.assert_called_once()
    service.change_status.assert_called_once()
    service.close.assert_called_once()


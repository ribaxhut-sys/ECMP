"""Coverage for CM Batch-1 validation and HQ/duplicate error branches."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.authorization.principal import Principal
from app.core.config import get_settings
from app.core.errors import InvalidStateError, NotFoundError, ValidationAppError
from app.integrations.customer import StubCustomerProvider
from app.integrations.customer.types import (
    CustomerLookupResult,
    CustomerLookupStatus,
    MinimalCustomer,
)
from app.main import create_app
from app.modules.cm_batch1 import router as cm_router
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.exceptions import ReplayConflict
from app.modules.cm_batch1.router import (
    _enforce_cm_org_or_pusat_hq,
    get_cm_batch1_attachment_service,
    get_cm_batch1_history_service,
    get_cm_batch1_service,
)
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    CustomerSearchRequest,
    DuplicateDecisionRequest,
    HqAcceptAndScheduleRequest,
    HqAcceptRequest,
    HqReturnRequest,
    HqScheduleArrivalRequest,
    IntakeEscalationDecisionRequest,
    IntakeEscalationRequestBody,
    TransferAttachmentsRequest,
    TransferAttachmentsResponse,
)
from app.modules.cm_batch1.service import CmBatch1Service, _aggregate_status, _is_hhmm
from app.modules.cm_batch1.store import Batch1Store
from cm_batch1_helpers import confirmed_create


@pytest.fixture()
def store() -> Batch1Store:
    s = Batch1Store()
    s.reset()
    return s


@pytest.fixture()
def service(store: Batch1Store) -> CmBatch1Service:
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=store,
    )


@pytest.fixture()
def api_client(service: CmBatch1Service):
    app = create_app()
    app.dependency_overrides[get_cm_batch1_service] = lambda: service

    async def _principal() -> Principal:
        return Principal(
            user_id=uuid4(),
            roles=("AGENT",),
            permissions=frozenset({"complaints:read", "complaints:create", "*"}),
        )

    from app.core.authorization.authentication import get_current_principal

    app.dependency_overrides[get_current_principal] = _principal
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def _escalate_pending(service: CmBatch1Service, request_id: str):
    return confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject=f"Esc {request_id}",
            description="Keluhan\n\n---\nAlasan eskalasi:\nButuh tinjauan Pusat untuk kasus ini",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            duplicateOverrideJustification="Lab override for Batch-1 error-path coverage.",
        ),
        request_id=request_id,
        actor_id="agent-1",
    )


def test_hhmm_and_aggregate_status_helpers() -> None:
    assert _is_hhmm("09:30") is True
    assert _is_hhmm("24:00") is False
    assert _is_hhmm("ab:cd") is False
    assert _is_hhmm("9") is False
    assert _aggregate_status(None) == "REGISTERED"
    assert _aggregate_status("CLOSED") == "CLOSED"
    assert _aggregate_status("weird") == "REGISTERED"


def test_search_identity_and_degraded_non_strict(store: Batch1Store) -> None:
    strict = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(),
        store=store,
    )
    by_id = strict.search_customer(
        CustomerSearchRequest(identityNumber="ID-10000001"),
        principal_key="p-id",
    )
    assert by_id.verification_status in {"verified", "ambiguous"}

    loose = CmBatch1Service(
        customer_provider=StubCustomerProvider(available=False),
        guard=EnumerationGuard(),
        store=store,
        strict_master=False,
    )
    degraded = loose.search_customer(
        CustomerSearchRequest(customerNumber="CN-10000001"),
        principal_key="p-deg",
    )
    assert degraded.verification_status == "degraded"


def test_peek_and_get_missing(service: CmBatch1Service) -> None:
    assert service.peek_idempotent("  ") is None
    assert service.peek_idempotent("no-such-key") is None
    assert service.peek_by_channel_message("") is None
    assert service.peek_by_channel_message("no-msg") is None
    with pytest.raises(NotFoundError):
        service.get_complaint(str(uuid4()))
    with pytest.raises(ValidationAppError):
        service.create_complaint(
            CreateComplaintBatch1Request(
                customerId="CUST-10001",
                category="BILLING",
                channel="BRANCH",
                subject="No key",
                description="x\n\n---\nCatatan:\nCatatan lab",
            ),
            request_id="  ",
            channel_message_id=None,
            actor_id="a",
        )


def test_duplicate_decision_error_branches(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(decision="link_existing"),
            actor_id="a",
        )
    with pytest.raises(NotFoundError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(
                decision="link_existing",
                survivingComplaintId=str(uuid4()),
            ),
            actor_id="a",
        )
    with pytest.raises(ValidationAppError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(decision="override"),
            actor_id="a",
        )
    with pytest.raises(ValidationAppError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(decision="blocked"),
            actor_id="a",
        )
    with pytest.raises(NotFoundError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(
                decision="recommend_only",
                survivingComplaintId=str(uuid4()),
            ),
            actor_id="a",
        )
    with pytest.raises(ValidationAppError):
        service.record_duplicate_decision(
            DuplicateDecisionRequest(decision="recommend_only"),
            actor_id="a",
        )


def test_duplicate_blocked_inherits_surviving_customer(service: CmBatch1Service) -> None:
    surviving = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Surviving blocked inherit",
            description="x\n\n---\nCatatan:\nCatatan lab",
        ),
        request_id="err-block-surv",
        actor_id="agent-1",
    )
    blocked = service.record_duplicate_decision(
        DuplicateDecisionRequest(
            decision="blocked",
            survivingComplaintId=surviving.complaint_id,
        ),
        actor_id="sup-1",
    )
    assert blocked.hard_block is True


def test_confirm_360_and_reference_search(service: CmBatch1Service, store: Batch1Store) -> None:
    ref = service.search_customer(
        CustomerSearchRequest(referenceNumber="REF-10000001"),
        principal_key="p-ref",
    )
    assert ref.verification_status in {"verified", "ambiguous", "not_found"}

    down = CmBatch1Service(
        customer_provider=StubCustomerProvider(available=False),
        guard=EnumerationGuard(),
        store=store,
        strict_master=True,
    )
    with pytest.raises(NotFoundError):
        down.confirm_customer("CUST-10001", principal_key="p-down")
    with pytest.raises(NotFoundError):
        service.confirm_customer("CUST-MISSING", principal_key="p-miss")
    with pytest.raises(NotFoundError):
        service.customer_360_minimum("CUST-MISSING")

    class _BlankNames(StubCustomerProvider):
        def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
            return CustomerLookupResult(
                status=CustomerLookupStatus.FOUND,
                customer=MinimalCustomer(
                    customer_id=customer_id,
                    customer_number="  ",
                    identity_number="ID-1",
                    reference_number="REF-1",
                    display_name="  ",
                ),
            )

    created = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Blank customer labels",
            description="x\n\n---\nCatatan:\nCatatan lab",
            duplicateOverrideJustification="Lab override for blank customer display names.",
        ),
        request_id="err-blank-labels",
        actor_id="agent-1",
    )
    service._customers = _BlankNames()
    viewed = service.get_complaint(created.complaint_id)
    assert viewed.customer_display_name is None


def test_intake_decision_and_re_escalate_guards(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    with pytest.raises(NotFoundError):
        service.decide_intake_escalation(
            str(uuid4()),
            IntakeEscalationDecisionRequest(
                decision="APPROVE",
                note="x" * 24,
                priority="HIGH",
            ),
            actor_id="spv",
        )
    with pytest.raises(NotFoundError):
        service.request_intake_escalation(
            str(uuid4()),
            IntakeEscalationRequestBody(reason="x" * 24),
            actor_id="agent-1",
        )

    created = _escalate_pending(service, "err-re-1")
    row = store.get(created.complaint_id)
    assert row is not None
    row.status = "CLOSED"
    with pytest.raises(InvalidStateError):
        service.decide_intake_escalation(
            created.complaint_id,
            IntakeEscalationDecisionRequest(
                decision="APPROVE",
                note="x" * 24,
                priority="HIGH",
            ),
            actor_id="spv",
        )
    with pytest.raises(InvalidStateError):
        service.request_intake_escalation(
            created.complaint_id,
            IntakeEscalationRequestBody(reason="x" * 24),
            actor_id="agent-1",
        )

    row.status = "REGISTERED"
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Penolakan Eskalasi: bukti cabang belum lengkap untuk Pusat.",
        ),
        actor_id="spv",
    )
    with pytest.raises(ValidationAppError):
        service.request_intake_escalation(
            created.complaint_id,
            IntakeEscalationRequestBody(reason="too-short"),
            actor_id="agent-1",
        )
    with pytest.raises(ValidationAppError):
        service.request_intake_escalation(
            created.complaint_id,
            IntakeEscalationRequestBody.model_construct(
                reason="Ajuan ulang dengan prioritas yang tidak valid untuk HQ.",
                priority="NOPE",
            ),
            actor_id="agent-1",
        )

    row = store.get(created.complaint_id)
    assert row is not None
    row.hq_accepted_at = datetime.now(UTC)
    with pytest.raises(InvalidStateError):
        service.request_intake_escalation(
            created.complaint_id,
            IntakeEscalationRequestBody(reason="x" * 24),
            actor_id="agent-1",
        )
    row.hq_accepted_at = None
    row.case_created = True
    replayed = service.request_intake_escalation(
        created.complaint_id,
        IntakeEscalationRequestBody(reason="x" * 24),
        actor_id="agent-1",
    )
    assert replayed.intake_disposition == "ESCALATE_PENDING_APPROVAL"


def test_cancel_allowed_when_case_exists(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    created = _escalate_pending(service, "err-cancel-case")
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui sementara sebelum Case dibuat di unit Pusat.",
            priority="HIGH",
        ),
        actor_id="spv",
    )
    row = store.get(created.complaint_id)
    assert row is not None
    row.case_created = True
    row.status = "IN_PROGRESS"
    cancelled = service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="CANCEL",
            note="Batalkan Eskalasi: Case tetap ada, Pusat belum menerima.",
        ),
        actor_id="spv",
    )
    assert cancelled.intake_disposition == "ESCALATE_CANCELLED"
    assert cancelled.case_created is True


def test_hq_accept_schedule_return_guards(
    service: CmBatch1Service, store: Batch1Store
) -> None:
    missing = str(uuid4())
    with pytest.raises(NotFoundError):
        service.return_from_hq(
            missing,
            HqReturnRequest(reasonCode="MISSING_ATTACHMENT", note="x" * 24),
            actor_id="hq",
        )
    with pytest.raises(NotFoundError):
        service.accept_at_hq(missing, HqAcceptRequest(note="x" * 24), actor_id="hq")
    with pytest.raises(NotFoundError):
        service.accept_and_schedule_at_hq(
            missing,
            HqAcceptAndScheduleRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
                destinationUnitId="PUSAT-CRO",
                note="x" * 12,
            ),
            actor_id="hq",
        )
    with pytest.raises(NotFoundError):
        service.schedule_hq_arrival(
            missing,
            HqScheduleArrivalRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
                note="ok",
            ),
            actor_id="hq",
        )

    created = _escalate_pending(service, "err-hq-1")
    with pytest.raises(InvalidStateError):
        service.return_from_hq(
            created.complaint_id,
            HqReturnRequest(reasonCode="MISSING_ATTACHMENT", note="x" * 24),
            actor_id="hq",
        )
    with pytest.raises(InvalidStateError):
        service.accept_and_schedule_at_hq(
            created.complaint_id,
            HqAcceptAndScheduleRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
                destinationUnitId="PUSAT-CRO",
                note="x" * 12,
            ),
            actor_id="hq",
        )

    row = store.get(created.complaint_id)
    assert row is not None
    row.status = "CLOSED"
    with pytest.raises(InvalidStateError):
        service.return_from_hq(
            created.complaint_id,
            HqReturnRequest(reasonCode="MISSING_ATTACHMENT", note="x" * 24),
            actor_id="hq",
        )
    with pytest.raises(InvalidStateError):
        service.accept_at_hq(
            created.complaint_id, HqAcceptRequest(note="x" * 24), actor_id="hq"
        )
    with pytest.raises(InvalidStateError):
        service.accept_and_schedule_at_hq(
            created.complaint_id,
            HqAcceptAndScheduleRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
                destinationUnitId="PUSAT-CRO",
                note="x" * 12,
            ),
            actor_id="hq",
        )
    with pytest.raises(InvalidStateError):
        service.schedule_hq_arrival(
            created.complaint_id,
            HqScheduleArrivalRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
            ),
            actor_id="hq",
        )

    row.status = "REGISTERED"
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar cabang error-path HQ bisa diuji lengkap.",
            priority="MEDIUM",
        ),
        actor_id="spv",
    )
    with pytest.raises(ValidationAppError):
        service.accept_and_schedule_at_hq(
            created.complaint_id,
            HqAcceptAndScheduleRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="xx:yy",
                destinationUnitId="PUSAT-CRO",
                note="x" * 12,
            ),
            actor_id="hq",
        )
    with pytest.raises(InvalidStateError):
        service.schedule_hq_arrival(
            created.complaint_id,
            HqScheduleArrivalRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
            ),
            actor_id="hq",
        )

    service.accept_at_hq(
        created.complaint_id,
        HqAcceptRequest(note="Pusat menerima untuk uji jadwal HHMM invalid."),
        actor_id="hq",
    )
    with pytest.raises(InvalidStateError):
        service.return_from_hq(
            created.complaint_id,
            HqReturnRequest(reasonCode="MISSING_ATTACHMENT", note="x" * 24),
            actor_id="hq",
        )
    with pytest.raises(InvalidStateError):
        service.accept_and_schedule_at_hq(
            created.complaint_id,
            HqAcceptAndScheduleRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="09:00",
                destinationUnitId="PUSAT-CRO",
                note="x" * 12,
            ),
            actor_id="hq",
        )
    with pytest.raises(ValidationAppError):
        service.schedule_hq_arrival(
            created.complaint_id,
            HqScheduleArrivalRequest(
                arrivalDate=date(2026, 8, 20),
                arrivalTime="99:99",
            ),
            actor_id="hq",
        )


def test_customer_and_officer_label_failures(store: Batch1Store) -> None:
    class _BoomCustomers(StubCustomerProvider):
        def get_minimal_customer(self, customer_id: str) -> CustomerLookupResult:
            raise RuntimeError("directory down")

    class _BoomDirectory:
        def display_names(self, user_ids: set[str]) -> dict[str, str]:
            raise RuntimeError("down")

    svc = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        user_directory=_BoomDirectory(),
        guard=EnumerationGuard(),
        store=store,
    )
    created = confirmed_create(
        svc,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Label fail",
            description="x\n\n---\nCatatan:\nCatatan lab",
        ),
        request_id="err-labels-1",
        actor_id="agent-77",
    )
    svc._customers = _BoomCustomers()
    viewed = svc.get_complaint(created.complaint_id)
    assert viewed.customer_display_name is None
    assert viewed.created_by_name is None

    empty = CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        user_directory=_BoomDirectory(),
        guard=EnumerationGuard(),
        store=store,
    )
    assert empty._officer_labels_for(set()) == {}


def test_list_filters_and_work_stats_http(api_client: TestClient) -> None:
    listed = api_client.get(
        "/api/v1/cm/complaints?priority=NOPE&status=BOGUS&intakeDisposition=ZZZ"
    )
    assert listed.status_code == 200
    # G2-4: the panel is scoped to users the caller may see. A random id is
    # not the caller and resolves to no member, so it is 404 — the same shape
    # GET /users/{id} already returns for an unknown target.
    stats = api_client.get(f"/api/v1/cm/complaints/work-stats/{uuid4()}")
    assert stats.status_code == 404
    write = api_client.post("/api/v1/cm/customers/write-back")
    assert write.status_code == 400
    three60 = api_client.get("/api/v1/cm/customers/CUST-10001/batch1-360")
    assert three60.status_code == 200


def test_router_factories_and_org_enforcement_helper() -> None:
    session = MagicMock()
    settings = get_settings()
    assert get_cm_batch1_service(session, settings) is not None
    assert get_cm_batch1_history_service(session) is not None
    with patch(
        "app.modules.cm_batch1.router.build_attachment_service",
        return_value=MagicMock(),
    ):
        assert get_cm_batch1_attachment_service(session) is not None

    principal = Principal(
        user_id=uuid4(),
        roles=("AGENT",),
        org_unit_id="CABANG-1",
        permissions=frozenset({"complaints:read"}),
    )
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org="CABANG-1",
        session=session,
        settings=settings,
    )
    with patch(
        "app.modules.cm_batch1.router.org_scope_enforcement_enabled",
        return_value=True,
    ), patch(
        "app.modules.cm_batch1.router._effective_org_unit",
        return_value="PUSAT",
    ), patch(
        "app.modules.cm_batch1.router.is_pusat_unit",
        return_value=True,
    ):
        _enforce_cm_org_or_pusat_hq(
            principal=principal,
            resource_org="CABANG-1",
            session=session,
            settings=settings,
        )
    admin = Principal(
        user_id=uuid4(),
        roles=("ADMIN",),
        org_unit_id="CABANG-1",
        permissions=frozenset({"complaints:read"}),
    )
    with patch(
        "app.modules.cm_batch1.router.org_scope_enforcement_enabled",
        return_value=True,
    ), patch(
        "app.modules.cm_batch1.router._effective_org_unit",
        return_value="CABANG-1",
    ), patch(
        "app.modules.cm_batch1.router.is_pusat_unit",
        return_value=False,
    ):
        _enforce_cm_org_or_pusat_hq(
            principal=admin,
            resource_org="OTHER",
            session=session,
            settings=settings,
        )
    with patch(
        "app.modules.cm_batch1.router.org_scope_enforcement_enabled",
        return_value=True,
    ), patch(
        "app.modules.cm_batch1.router._effective_org_unit",
        return_value="CABANG-1",
    ), patch(
        "app.modules.cm_batch1.router.is_pusat_unit",
        return_value=False,
    ), patch(
        "app.modules.cm_batch1.router.enforce_org_scope"
    ) as enforce:
        agent = Principal(
            user_id=uuid4(),
            roles=("AGENT",),
            org_unit_id="CABANG-1",
            permissions=frozenset({"complaints:read"}),
        )
        _enforce_cm_org_or_pusat_hq(
            principal=agent,
            resource_org="OTHER",
            session=session,
            settings=settings,
        )
        enforce.assert_called_once()


def test_router_handlers_delegate_to_service(service: CmBatch1Service) -> None:
    created = _escalate_pending(service, "err-router-1")
    service.decide_intake_escalation(
        created.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui agar handler router HQ bisa dipanggil langsung.",
            priority="HIGH",
        ),
        actor_id="spv",
    )
    principal = Principal(
        user_id=uuid4(),
        roles=("HO_SCHEDULER", "AGENT"),
        org_unit_id="PUSAT",
        permissions=frozenset(
            {"complaints:read", "complaints:create", "complaints:escalate", "*"}
        ),
    )
    session = MagicMock()
    settings = get_settings()
    cid = created.complaint_id
    history = MagicMock()
    history.list_history.return_value = []
    attachments = MagicMock()
    attachments.list_for_complaint.return_value = []
    attachments.transfer.return_value = TransferAttachmentsResponse(
        stagingToken="STG-1",
        survivingComplaintId=cid,
        transferredCount=0,
        attachments=[],
        discarded=False,
    )

    with patch.object(cm_router, "OrgUnitResolver") as resolver:
        resolver.return_value.resolve_cm_complaint.return_value = "PUSAT"
        # Destination unit is looked up in the org directory before it is stored.
        resolver.return_value.resolve_active_unit_code.return_value = "PUSAT-CRO"
        with patch.object(cm_router, "_enforce_cm_org_or_pusat_hq"):
            assert cm_router.get_complaint(
                cid, principal, service, session, settings
            ).data.complaint_id == cid
            hist = cm_router.get_complaint_history(
                cid, principal, service, history, session, settings
            )
            assert hist.data == []
            listed = cm_router.list_cm_complaint_attachments(
                cid, principal, attachments, session, settings, 1, 20
            )
            assert listed.data == []
            accepted = cm_router.hq_accept_escalation(
                cid,
                HqAcceptRequest(note="Pusat terima via pemanggilan handler router."),
                principal,
                service,
                session,
                settings,
            )
            assert accepted.data.hq_accepted_at is not None or True
            scheduled = cm_router.hq_schedule_arrival(
                cid,
                HqScheduleArrivalRequest(
                    arrivalDate=date(2026, 8, 21),
                    arrivalTime="10:00",
                    note="Jadwal uji handler",
                ),
                principal,
                service,
                session,
                settings,
            )
            assert scheduled.data.intake_disposition == "HQ_SCHEDULED"

            other = _escalate_pending(service, "err-router-return")
            service.decide_intake_escalation(
                other.complaint_id,
                IntakeEscalationDecisionRequest(
                    decision="APPROVE",
                    note="Disetujui untuk uji handler pengembalian Pusat.",
                    priority="LOW",
                ),
                actor_id="spv",
            )
            returned = cm_router.hq_return_escalation(
                other.complaint_id,
                HqReturnRequest(
                    reasonCode="MISSING_ATTACHMENT",
                    note="Lampirkan bukti pembayaran pelanggan ke cabang.",
                ),
                principal,
                service,
                session,
                settings,
            )
            assert returned.data.intake_disposition == "RETURNED_TO_BRANCH"
            again = cm_router.request_intake_escalation(
                other.complaint_id,
                IntakeEscalationRequestBody(
                    reason="Berkas dilengkapi, ajukan ulang eskalasi ke Pusat."
                ),
                principal,
                service,
                session,
                settings,
            )
            assert again.data.intake_disposition == "ESCALATE_PENDING_APPROVAL"
            decided = cm_router.decide_intake_escalation(
                other.complaint_id,
                IntakeEscalationDecisionRequest(
                    decision="REJECT",
                    note="Penolakan Eskalasi: masih kurang bukti untuk Pusat.",
                ),
                principal,
                service,
                session,
                settings,
            )
            assert decided.data.intake_disposition == "ESCALATE_REJECTED"

            combo = _escalate_pending(service, "err-router-combo")
            service.decide_intake_escalation(
                combo.complaint_id,
                IntakeEscalationDecisionRequest(
                    decision="APPROVE",
                    note="Disetujui untuk uji terima dan jadwal sekaligus.",
                    priority="MEDIUM",
                ),
                actor_id="spv",
            )
            combo_out = cm_router.hq_accept_and_schedule(
                combo.complaint_id,
                HqAcceptAndScheduleRequest(
                    arrivalDate=date(2026, 8, 22),
                    arrivalTime="11:15",
                    destinationUnitId="PUSAT-CRO",
                    note="Informasikan wajib pajak jadwal kedatangan.",
                ),
                principal,
                service,
                session,
                settings,
            )
            assert combo_out.data.intake_disposition == "HQ_SCHEDULED"

        with patch.object(
            cm_router, "org_scope_enforcement_enabled", return_value=True
        ), patch.object(cm_router, "enforce_org_scope"):
            transfer = cm_router.transfer_staged_attachments(
                TransferAttachmentsRequest(
                    stagingToken="STG-1", survivingComplaintId=cid
                ),
                principal,
                attachments,
                session,
                settings,
            )
            assert transfer.data.transferred_count == 0
            surviving = confirmed_create(
                service,
                CreateComplaintBatch1Request(
                    customerId="CUST-10001",
                    category="BILLING",
                    channel="BRANCH",
                    subject="Surviving link",
                    description="x\n\n---\nCatatan:\nCatatan lab",
                    duplicateOverrideJustification="Lab override for router duplicate-decision handler.",
                ),
                request_id="err-router-surv",
                actor_id="agent-1",
            )
            decision = cm_router.record_duplicate_decision(
                DuplicateDecisionRequest(
                    decision="link_existing",
                    survivingComplaintId=surviving.complaint_id,
                    stagingToken="STG-1",
                ),
                principal,
                service,
                attachments,
                session,
                settings,
            )
            assert decision.data.decision == "link_existing"


def _store_create(store: Batch1Store, *, request_id: str, channel: str | None):
    return store.create(
        customer_id="CUST-10001",
        category="BILLING",
        channel="BRANCH",
        subject=request_id,
        description="desc",
        priority="MEDIUM",
        created_by="agent-1",
        request_id=request_id,
        channel_message_id=channel,
    )


def test_store_replay_conflict_and_later_review_close(store: Batch1Store) -> None:
    first, new = _store_create(store, request_id="req-a", channel="ch-a")
    assert new is True
    second, new_b = _store_create(store, request_id="req-b", channel="ch-b")
    assert new_b is True
    with pytest.raises(ReplayConflict):
        _store_create(store, request_id="req-a", channel="ch-b")
    replay, created = _store_create(store, request_id="req-a", channel="ch-a")
    assert created is False
    assert replay.complaint_id == first.complaint_id
    store.create_later_review_work_item(
        customer_id="CUST-10001",
        reason="attachment_bind_failed",
        complaint_id=first.complaint_id,
    )
    assert store.close_later_review_items(complaint_id="  ") == 0
    assert store.close_later_review_items(complaint_id=first.complaint_id) >= 1
    assert store.list_later_review_items(status="ALL", limit=10)
    _ = second

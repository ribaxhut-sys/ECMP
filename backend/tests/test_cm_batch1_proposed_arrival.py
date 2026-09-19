"""Branch-proposed HQ arrival slot — advisory only, Pusat still decides.

Cabang may propose a date/time when escalating to Pusat (create or
re-escalate). Pusat's own accept/schedule/return decisions always own the
final ``hq_arrival_date``/``hq_arrival_time`` and clear the proposal.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.core.errors import ValidationAppError
from app.integrations.customer import StubCustomerProvider
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    HqAcceptAndScheduleRequest,
    HqReturnRequest,
    IntakeEscalationDecisionRequest,
    IntakeEscalationRequestBody,
)
from app.modules.cm_batch1.service import CmBatch1Service, _validate_proposed_arrival
from app.modules.cm_batch1.store import Batch1Store
from cm_batch1_helpers import confirmed_create

_TOMORROW = date.today() + timedelta(days=1)


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


def _escalate_body(**overrides: object) -> CreateComplaintBatch1Request:
    fields = {
        "customerId": "CUST-10001",
        "category": "Layanan",
        "channel": "WALK_IN",
        "subject": "Subjek",
        "description": "Cerita\n\n---\nAlasan eskalasi:\nPerlu ditinjau Pusat.",
        "intakeDisposition": "ESCALATE_PENDING_APPROVAL",
    }
    fields.update(overrides)
    return CreateComplaintBatch1Request.model_validate(fields)


def test_propose_arrival_on_create_escalate(service: CmBatch1Service) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-1",
    )
    assert resp.proposed_arrival_date == _TOMORROW
    assert resp.proposed_arrival_time == "09:00"
    assert resp.proposed_by == "actor-1"
    assert resp.hq_arrival_date is None


def test_propose_arrival_rejected_without_escalation(service: CmBatch1Service) -> None:
    body = CreateComplaintBatch1Request.model_validate(
        {
            "customerId": "CUST-10002",
            "category": "Layanan",
            "channel": "WALK_IN",
            "subject": "Subjek",
            "description": "Cerita",
            "proposedArrivalDate": _TOMORROW.isoformat(),
            "proposedArrivalTime": "09:00",
        }
    )
    with pytest.raises(ValidationAppError):
        confirmed_create(service, body, request_id="req-2")


def test_propose_arrival_rejects_past_date(service: CmBatch1Service) -> None:
    yesterday = date.today() - timedelta(days=1)
    with pytest.raises(ValidationAppError):
        confirmed_create(
            service,
            _escalate_body(
                proposedArrivalDate=yesterday.isoformat(), proposedArrivalTime="09:00"
            ),
            request_id="req-3",
        )


def test_proposed_arrival_past_check_uses_jakarta_calendar() -> None:
    jakarta_today = datetime.now(ZoneInfo("Asia/Jakarta")).date()
    _validate_proposed_arrival(jakarta_today, "09:00")
    with pytest.raises(ValidationAppError):
        _validate_proposed_arrival(jakarta_today - timedelta(days=1), "09:00")


def test_propose_arrival_rejects_bad_time(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError):
        confirmed_create(
            service,
            _escalate_body(
                proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="25:99"
            ),
            request_id="req-4",
        )


def test_hq_accept_and_schedule_clears_proposal(service: CmBatch1Service) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-5",
    )
    approved = service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui supervisor cabang untuk eskalasi ke Pusat.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    # APPROVE keeps the proposal alive — Pusat has not decided yet.
    assert approved.proposed_arrival_date == _TOMORROW

    scheduled = service.accept_and_schedule_at_hq(
        resp.complaint_id,
        HqAcceptAndScheduleRequest(
            arrivalDate=_TOMORROW.isoformat(),
            arrivalTime="10:00",
            destinationUnitId="PUSAT-CRO",
            note="Jadwal digeser satu jam oleh Pusat.",
        ),
        actor_id="hq-scheduler-1",
    )
    assert scheduled.hq_arrival_date == _TOMORROW
    assert scheduled.hq_arrival_time == "10:00"
    assert scheduled.hq_destination_unit_id == "PUSAT-CRO"
    assert scheduled.proposed_arrival_date is None
    assert scheduled.proposed_arrival_time is None
    # The proposal is cleared, so the shift only survives in the history blob —
    # the branch still gets asked "why 10:00, we proposed 09:00?".
    assert "digeser Pusat ke" in (scheduled.description or "")
    assert "09:00" in (scheduled.hq_arrival_note or "")


def test_hq_accept_and_schedule_rejects_non_pusat_destination(
    service: CmBatch1Service,
) -> None:
    """A taxpayer escalated to Pusat is never directed back to a branch desk."""
    resp = confirmed_create(service, _escalate_body(), request_id="req-dest-1")
    service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui supervisor cabang untuk eskalasi ke Pusat.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    with pytest.raises(ValidationAppError):
        service.accept_and_schedule_at_hq(
            resp.complaint_id,
            HqAcceptAndScheduleRequest(
                arrivalDate=_TOMORROW.isoformat(),
                arrivalTime="10:00",
                destinationUnitId="UPPPD-GAMBIR",
                note="Unit tujuan salah, harus ditolak.",
            ),
            actor_id="hq-scheduler-1",
        )


def test_reject_clears_proposal(service: CmBatch1Service) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-6",
    )
    rejected = service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Data pendukung belum lengkap untuk eskalasi ini.",
        ),
        actor_id="supervisor-1",
    )
    assert rejected.proposed_arrival_date is None
    assert rejected.proposed_arrival_time is None


def test_re_escalate_replaces_stale_proposal(service: CmBatch1Service) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-7",
    )
    service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Data pendukung belum lengkap untuk eskalasi ini.",
        ),
        actor_id="supervisor-1",
    )
    next_day = _TOMORROW + timedelta(days=1)
    re_escalated = service.request_intake_escalation(
        resp.complaint_id,
        IntakeEscalationRequestBody.model_validate(
            {
                "reason": "Melengkapi bukti tambahan sesuai permintaan Pusat sebelumnya.",
                "proposedArrivalDate": next_day.isoformat(),
                "proposedArrivalTime": "11:00",
            }
        ),
        actor_id="agent-1",
    )
    assert re_escalated.proposed_arrival_date == next_day
    assert re_escalated.proposed_arrival_time == "11:00"


def test_re_escalate_without_new_proposal_clears_old_one(
    service: CmBatch1Service,
) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-8",
    )
    service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="REJECT",
            note="Data pendukung belum lengkap untuk eskalasi ini.",
        ),
        actor_id="supervisor-1",
    )
    re_escalated = service.request_intake_escalation(
        resp.complaint_id,
        IntakeEscalationRequestBody.model_validate(
            {"reason": "Melengkapi bukti tambahan sesuai permintaan Pusat sebelumnya."}
        ),
        actor_id="agent-1",
    )
    assert re_escalated.proposed_arrival_date is None
    assert re_escalated.proposed_arrival_time is None


def test_return_from_hq_clears_proposal(service: CmBatch1Service) -> None:
    resp = confirmed_create(
        service,
        _escalate_body(
            proposedArrivalDate=_TOMORROW.isoformat(), proposedArrivalTime="09:00"
        ),
        request_id="req-10",
    )
    approved = service.decide_intake_escalation(
        resp.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Disetujui supervisor cabang untuk eskalasi ke Pusat.",
            priority="MEDIUM",
        ),
        actor_id="supervisor-1",
    )
    assert approved.proposed_arrival_date == _TOMORROW

    returned = service.return_from_hq(
        resp.complaint_id,
        HqReturnRequest(
            reasonCode="INCOMPLETE_CHRONOLOGY",
            note="Data pendukung belum lengkap, mohon dilengkapi.",
        ),
        actor_id="hq-scheduler-1",
    )
    assert returned.proposed_arrival_date is None
    assert returned.proposed_arrival_time is None
    assert returned.intake_disposition == "RETURNED_TO_BRANCH"


def test_proposed_arrival_date_and_time_must_pair(service: CmBatch1Service) -> None:
    with pytest.raises(ValidationAppError):
        confirmed_create(
            service,
            _escalate_body(proposedArrivalDate=_TOMORROW.isoformat()),
            request_id="req-9",
        )

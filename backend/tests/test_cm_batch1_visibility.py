"""CM Batch-1 list visibility (DEC-024 pattern / owning_unit_id)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.authorization.principal import Principal
from app.core.authorization.visibility import (
    VisibilityClass,
    complaint_visible_for_pusat,
    resolve_row_visibility,
)
from app.integrations.customer import StubCustomerProvider
from app.modules.cm_batch1.enumeration import EnumerationGuard
from app.modules.cm_batch1.schemas import (
    CreateComplaintBatch1Request,
    IntakeEscalationDecisionRequest,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.store import Batch1Store
from cm_batch1_helpers import confirmed_create


def _service() -> CmBatch1Service:
    store = Batch1Store()
    store.reset()
    return CmBatch1Service(
        customer_provider=StubCustomerProvider(),
        guard=EnumerationGuard(max_failures=3, window_seconds=60, block_seconds=30),
        store=store,
    )


def test_resolve_ho_scheduler_is_pusat() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_SCHEDULER",),
        permissions=frozenset({"complaints:read", "escalations:review"}),
    )
    assert resolve_row_visibility(principal) == VisibilityClass.PUSAT


def test_complaint_visible_for_pusat_predicates() -> None:
    assert (
        complaint_visible_for_pusat(
            owning_unit_id="PUSAT",
            intake_disposition=None,
            hq_accepted_at=None,
        )
        is True
    )
    assert (
        complaint_visible_for_pusat(
            owning_unit_id="UPPPD-A",
            intake_disposition="ESCALATE_PENDING_APPROVAL",
            hq_accepted_at=None,
        )
        is False
    )
    assert (
        complaint_visible_for_pusat(
            owning_unit_id="UPPPD-A",
            intake_disposition="ESCALATE_APPROVED",
            hq_accepted_at=None,
        )
        is True
    )
    assert (
        complaint_visible_for_pusat(
            owning_unit_id="UPPPD-A",
            intake_disposition="ESCALATE_PENDING_APPROVAL",
            hq_accepted_at=datetime.now(UTC),
        )
        is True
    )


def test_list_visibility_self_unit_pusat() -> None:
    service = _service()
    agent_a = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    agent_b = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    own_a = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="BILLING",
            channel="BRANCH",
            subject="Branch A own",
            description="Keluhan A",
            recordingUnitId="UPPPD-A",
        ),
        request_id="vis-a-1",
        actor_id=str(agent_a),
    )
    assert own_a.owning_unit_id == "UPPPD-A"

    confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="BILLING",
            channel="BRANCH",
            subject="Branch B own",
            description="Keluhan B",
            recordingUnitId="UPPPD-B",
        ),
        request_id="vis-b-1",
        actor_id=str(agent_b),
    )

    pending = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10001",
            category="SERVICE",
            channel="BRANCH",
            subject="Pending esc",
            description="Keluhan lain\n\n---\nAlasan eskalasi:\nButuh pusat segera",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-A",
            duplicateOverrideJustification=(
                "Uji visibility — keluhan kedua pelanggan yang sama diizinkan."
            ),
        ),
        request_id="vis-pending",
        actor_id=str(agent_a),
    )
    approved = confirmed_create(
        service,
        CreateComplaintBatch1Request(
            customerId="CUST-10002",
            category="SERVICE",
            channel="BRANCH",
            subject="Approved esc",
            description="Keluhan lain\n\n---\nAlasan eskalasi:\nButuh pusat segera",
            intakeDisposition="ESCALATE_PENDING_APPROVAL",
            recordingUnitId="UPPPD-B",
            duplicateOverrideJustification=(
                "Uji visibility — keluhan kedua pelanggan yang sama diizinkan."
            ),
        ),
        request_id="vis-approved",
        actor_id=str(agent_b),
    )
    service.decide_intake_escalation(
        approved.complaint_id,
        IntakeEscalationDecisionRequest(
            decision="APPROVE",
            note="Catatan supervisor cukup panjang untuk HQ review.",
            priority="HIGH",
        ),
        actor_id="supervisor-b",
    )

    self_items, self_total = service.list_complaints(
        principal=Principal(
            user_id=agent_a,
            roles=("AGENT",),
            permissions=frozenset({"complaints:read"}),
        ),
    )
    assert self_total == 2
    assert {i.complaint_id for i in self_items} == {
        own_a.complaint_id,
        pending.complaint_id,
    }

    unit_items, unit_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("SUPERVISOR",),
            permissions=frozenset({"complaints:read"}),
            org_unit_id="UPPPD-A",
        ),
        org_unit_id="UPPPD-A",
    )
    assert unit_total == 2
    assert all(i.owning_unit_id == "UPPPD-A" for i in unit_items)
    assert approved.complaint_id not in {i.complaint_id for i in unit_items}

    pusat_items, _pusat_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("HO_SCHEDULER",),
            permissions=frozenset({"complaints:read", "escalations:review"}),
        ),
    )
    pusat_ids = {i.complaint_id for i in pusat_items}
    assert approved.complaint_id in pusat_ids
    assert pending.complaint_id not in pusat_ids
    assert own_a.complaint_id not in pusat_ids

    _admin_items, admin_total = service.list_complaints(
        principal=Principal(
            user_id=uuid.uuid4(),
            roles=("ADMIN",),
            permissions=frozenset({"*"}),
        ),
    )
    assert admin_total == 4

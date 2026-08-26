"""UM-BUG-008 — dashboard 'recent activity' reads CM Batch 1 timeline_entries.

Regression coverage for the dual-SoT bug: the dashboard's Recent Activity
widget used to compose from the legacy complaint_timelines/complaints
tables, which the running system no longer writes to. It must read
timeline_entries (CAPABILITY-010) + cm_batch1_complaints instead.

Unit-level (mocked collaborators) rather than a real session: TimelineEntryORM
uses a Postgres-only JSONB column, so an in-memory sqlite session can't create
the table — this exercises CmBatch1ActivityDashboardProvider's composition
logic (event-type mapping, complaint-number/actor resolution and fallbacks)
directly instead.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.dashboard.providers.cm_batch1_activity_provider import (
    CmBatch1ActivityDashboardProvider,
)


def _entry(
    *,
    aggregate_id: uuid.UUID | None = None,
    event_type: str = "ComplaintRegistered",
    actor_id: str | None = None,
    actor_name: str | None = None,
    metadata: dict | None = None,
    created_at: datetime | None = None,
):
    return SimpleNamespace(
        aggregate_id=aggregate_id or uuid.uuid4(),
        event_type=event_type,
        title=event_type,
        actor_id=actor_id,
        actor_name=actor_name,
        metadata=metadata or {},
        created_at=created_at or datetime.now(UTC),
    )


def _provider() -> tuple[CmBatch1ActivityDashboardProvider, MagicMock, MagicMock, MagicMock]:
    # Constructing with a MagicMock session is safe — TimelineRepository /
    # CmBatch1Repository / LocalUserDirectory only store the session in
    # __init__, no DB calls happen until a method is invoked.
    provider = CmBatch1ActivityDashboardProvider(MagicMock())
    timeline = MagicMock()
    complaints = MagicMock()
    directory = MagicMock()
    provider._timeline = timeline
    provider._complaints = complaints
    provider._directory = directory
    return provider, timeline, complaints, directory


def test_list_recent_empty_when_no_entries() -> None:
    provider, timeline, _complaints, directory = _provider()
    timeline.list_recent.return_value = []

    assert provider.list_recent(limit=10) == []
    directory.display_names.assert_not_called()


def test_list_recent_resolves_complaint_number_and_maps_created_event() -> None:
    provider, timeline, complaints, directory = _provider()
    entry = _entry(event_type="ComplaintRegistered")
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000001': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert len(items) == 1
    assert items[0].complaint_number == "CM-00000001"
    assert items[0].event_type == "complaint.created"
    assert items[0].actor == "SYSTEM"  # no actor_id, no actor_name on this row
    complaints.complaint_numbers_by_ids.assert_called_once_with({entry.aggregate_id})


def test_list_recent_maps_escalation_decisions_by_metadata() -> None:
    provider, timeline, complaints, directory = _provider()
    approved = _entry(
        event_type="IntakeEscalationDecided", metadata={"decision": "APPROVE"}
    )
    rejected = _entry(
        event_type="IntakeEscalationDecided", metadata={"decision": "REJECT"}
    )
    timeline.list_recent.return_value = [approved, rejected]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000002': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.escalation_approved",
        "complaint.escalation_rejected",
    ]


def test_list_recent_maps_intake_disposition_escalation_requested() -> None:
    """Create-with-escalate must show as escalation requested, not generic update."""
    provider, timeline, complaints, directory = _provider()
    entry = _entry(
        event_type="IntakeDispositionRecorded",
        metadata={"intakeDisposition": "ESCALATE_PENDING_APPROVAL"},
    )
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000009': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert len(items) == 1
    assert items[0].event_type == "complaint.escalation_requested"


def test_list_recent_omits_attachment_bind_from_dashboard_feed() -> None:
    provider, timeline, complaints, directory = _provider()
    bound = _entry(event_type="AttachmentBound")
    created = _entry(event_type="ComplaintRegistered")
    timeline.list_recent.return_value = [bound, created]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0002': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == ["complaint.created"]
    timeline.list_recent.assert_called_once()
    assert timeline.list_recent.call_args.kwargs["limit"] >= 10


def test_list_recent_maps_handling_and_case_created() -> None:
    provider, timeline, complaints, directory = _provider()
    created = _entry(event_type="CaseCreated", metadata={"caseNumber": "CASE-9"})
    handling = _entry(event_type="HandlingTakenOver")
    timeline.list_recent.return_value = [created, handling]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000011': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.case_created",
        "complaint.handling_taken_over",
    ]
    assert items[0].case_number == "CASE-9"


def test_list_recent_maps_handling_continued() -> None:
    provider, timeline, complaints, directory = _provider()
    timeline.list_recent.return_value = [_entry(event_type="HandlingContinued")]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000012': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == ["complaint.handling_continued"]


def test_list_recent_maps_hq_and_case_ops_not_generic_update() -> None:
    provider, timeline, complaints, directory = _provider()
    timeline.list_recent.return_value = [
        _entry(event_type="HqAccepted"),
        _entry(event_type="HqReturned"),
        _entry(event_type="HqArrivalScheduled"),
        _entry(event_type="CaseAssigned"),
        _entry(event_type="CaseStatusChanged"),
        _entry(event_type="CaseResolved"),
        _entry(event_type="CaseClosed"),
        _entry(event_type="CaseCancelled"),
        _entry(
            event_type="IntakeEscalationDecided", metadata={"decision": "CANCEL"}
        ),
        _entry(event_type="CaseEscalatedToPusat"),
        _entry(event_type="CaseEscalationToPusatCancelled"),
        _entry(event_type="CaseEscalationReturned"),
        _entry(event_type="DuplicateFound"),
    ]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000013': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=20)

    assert [item.event_type for item in items] == [
        "complaint.hq_accepted",
        "complaint.hq_returned",
        "complaint.hq_arrival_scheduled",
        "complaint.assigned",
        "complaint.case_status_changed",
        "complaint.resolved",
        "complaint.closed",
        "complaint.case_cancelled",
        "complaint.escalation_cancelled",
        "complaint.escalated_to_pusat",
        "complaint.escalation_to_pusat_cancelled",
        "complaint.escalation_returned",
    ]
    assert "complaint.updated" not in {item.event_type for item in items}
    assert "complaint.other" not in {item.event_type for item in items}


def test_list_recent_omits_unmapped_events_instead_of_other() -> None:
    provider, timeline, complaints, directory = _provider()
    created = _entry(event_type="ComplaintRegistered")
    unknown = _entry(event_type="NotADashboardEvent")
    timeline.list_recent.return_value = [unknown, created]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0014': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == ["complaint.created"]
    assert "complaint.other" not in {item.event_type for item in items}


def test_list_recent_maps_case_escalated_to_pusat_after_handling() -> None:
    """Intake escalate-to-Pusat writes CaseEscalatedToPusat last — not 'Lain'."""
    provider, timeline, complaints, directory = _provider()
    timeline.list_recent.return_value = [
        _entry(event_type="HandlingContinued"),
        _entry(event_type="CaseEscalatedToPusat", metadata={"caseNumber": "TAB-2608-0014"}),
    ]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0014': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.handling_continued",
        "complaint.escalated_to_pusat",
    ]
    assert items[1].case_number == "TAB-2608-0014"


def test_list_recent_maps_approved_intake_disposition() -> None:
    provider, timeline, complaints, directory = _provider()
    entry = _entry(
        event_type="IntakeDispositionRecorded",
        metadata={"intakeDisposition": "ESCALATE_APPROVED"},
    )
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0015': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == ["complaint.escalation_approved"]


def test_list_recent_collapses_resolve_accept_into_closed() -> None:
    """Dashboard shows one close outcome; intake history still has the full path."""
    provider, timeline, complaints, directory = _provider()
    aggregate_id = uuid.uuid4()
    when = datetime(2026, 8, 14, 6, 0, tzinfo=UTC)
    timeline.list_recent.return_value = [
        _entry(
            aggregate_id=aggregate_id,
            event_type="CaseClosed",
            created_at=when,
        ),
        _entry(
            aggregate_id=aggregate_id,
            event_type="CaseOwnerAccepted",
            created_at=when,
        ),
        _entry(
            aggregate_id=aggregate_id,
            event_type="CaseResolved",
            created_at=when,
        ),
        _entry(
            aggregate_id=aggregate_id,
            event_type="HandlingContinued",
            created_at=when,
        ),
        _entry(
            aggregate_id=aggregate_id,
            event_type="ComplaintRegistered",
            created_at=when,
        ),
    ]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0008': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.closed",
        "complaint.handling_continued",
        "complaint.created",
    ]


def test_list_recent_keeps_resolved_when_not_yet_closed() -> None:
    provider, timeline, complaints, directory = _provider()
    timeline.list_recent.return_value = [_entry(event_type="CaseResolved")]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-OPEN': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == ["complaint.resolved"]


def test_list_recent_ranks_closed_above_created_when_same_timestamp() -> None:
    provider, timeline, complaints, directory = _provider()
    when = datetime(2026, 8, 15, 6, 55, 54, tzinfo=UTC)
    aggregate_id = uuid.uuid4()
    created = _entry(
        aggregate_id=aggregate_id,
        event_type="ComplaintRegistered",
        created_at=when,
    )
    closed = _entry(
        aggregate_id=aggregate_id,
        event_type="IntakeDispositionRecorded",
        metadata={"intakeDisposition": "BRANCH_CLOSED"},
        created_at=when,
    )
    timeline.list_recent.return_value = [created, closed]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='TAB-2608-0009': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.closed",
        "complaint.created",
    ]


def test_list_recent_ranks_escalation_above_created_when_same_timestamp() -> None:
    provider, timeline, complaints, directory = _provider()
    when = datetime(2026, 8, 8, 7, 30, tzinfo=UTC)
    aggregate_id = uuid.uuid4()
    created = _entry(
        aggregate_id=aggregate_id,
        event_type="ComplaintRegistered",
        created_at=when,
    )
    escalated = _entry(
        aggregate_id=aggregate_id,
        event_type="IntakeDispositionRecorded",
        metadata={"intakeDisposition": "ESCALATE_PENDING_APPROVAL"},
        created_at=when,
    )
    # Deliberately return created first — provider must re-rank.
    timeline.list_recent.return_value = [created, escalated]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-00000006': {i: _n for i in ids}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.escalation_requested",
        "complaint.created",
    ]


def test_list_recent_resolves_actor_via_directory() -> None:
    provider, timeline, complaints, directory = _provider()
    actor_id = "11111111-1111-1111-1111-111111111111"
    entry = _entry(event_type="ComplaintRegistered", actor_id=actor_id)
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n='CM-1': {i: _n for i in ids}
    directory.display_names.return_value = {actor_id: "Galih Firmansyah"}

    items = provider.list_recent(limit=10)

    assert items[0].actor == "Galih Firmansyah"
    directory.display_names.assert_called_once_with({actor_id})


def test_list_recent_falls_back_to_metadata_complaint_number_when_complaint_missing() -> (
    None
):
    provider, timeline, complaints, directory = _provider()
    entry = _entry(
        event_type="ComplaintRegistered", metadata={"complaintNumber": "CM-FALLBACK"}
    )
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.return_value = {}
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)
    assert items[0].complaint_number == "CM-FALLBACK"


def test_list_recent_falls_back_to_cm_cases_when_event_metadata_has_no_case_number() -> (
    None
):
    """HqArrivalScheduled etc. carry no caseNumber of their own — once a Case
    exists for the complaint, the feed must still show it instead of the
    complaint number (UM-BUG-011)."""
    provider, timeline, complaints, directory = _provider()
    entry = _entry(event_type="HqArrivalScheduled")
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n="CMTAB-2608-0006": {
        i: _n for i in ids
    }
    directory.display_names.return_value = {}

    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (str(entry.aggregate_id), "TAB-2608-0007"),
    ]
    provider._session = session

    items = provider.list_recent(limit=10)

    assert items[0].case_number == "TAB-2608-0007"


def test_list_recent_prefers_event_metadata_case_number_over_cm_cases_lookup() -> None:
    provider, timeline, complaints, directory = _provider()
    entry = _entry(event_type="CaseCreated", metadata={"caseNumber": "CASE-META"})
    timeline.list_recent.return_value = [entry]
    complaints.complaint_numbers_by_ids.side_effect = lambda ids, _n="CM-X": {
        i: _n for i in ids
    }
    directory.display_names.return_value = {}

    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (str(entry.aggregate_id), "CASE-STALE"),
    ]
    provider._session = session

    items = provider.list_recent(limit=10)

    assert items[0].case_number == "CASE-META"


def test_complaint_ids_for_branch_returns_matching_ids() -> None:
    provider, *_ = _provider()
    session = provider._session
    branch_id = uuid.uuid4()
    complaint_id = uuid.uuid4()
    session.get.return_value = SimpleNamespace(code="UPPPD-A", deleted_at=None)
    complaint_result = MagicMock()
    complaint_result.all.return_value = [complaint_id]
    session.scalars.return_value = complaint_result

    ids = provider._complaint_ids_for_branch(branch_id)
    assert ids == {complaint_id}
    session.get.assert_called_once()
    session.scalars.assert_called_once()


def test_complaint_ids_for_branch_short_circuits_when_branch_missing() -> None:
    provider, *_ = _provider()
    session = provider._session
    session.get.return_value = None

    ids = provider._complaint_ids_for_branch(uuid.uuid4())
    assert ids == set()
    session.scalars.assert_not_called()


def test_list_recent_with_branch_id_filters_via_complaint_ids() -> None:
    provider, timeline, _complaints, _directory = _provider()
    branch_id = uuid.uuid4()
    complaint_ids = {uuid.uuid4()}
    provider._complaint_ids_for_branch = MagicMock(return_value=complaint_ids)
    timeline.list_recent.return_value = []

    provider.list_recent(limit=10, branch_id=branch_id)

    provider._complaint_ids_for_branch.assert_called_once_with(branch_id)
    timeline.list_recent.assert_called_once_with(
        aggregate_type="Complaint", limit=40, aggregate_ids=complaint_ids
    )


def test_list_recent_with_branch_id_short_circuits_when_no_complaints() -> None:
    provider, timeline, _complaints, _directory = _provider()
    provider._complaint_ids_for_branch = MagicMock(return_value=set())

    items = provider.list_recent(limit=10, branch_id=uuid.uuid4())

    assert items == []
    timeline.list_recent.assert_not_called()


def test_list_recent_forwards_aggregate_type_and_limit() -> None:
    provider, timeline, _complaints, directory = _provider()
    timeline.list_recent.return_value = []
    directory.display_names.return_value = {}

    provider.list_recent(limit=7)

    timeline.list_recent.assert_called_once_with(
        aggregate_type="Complaint", limit=28, aggregate_ids=None
    )


def _kpi_row(**overrides: int) -> SimpleNamespace:
    """One grouped-pass result row (DEC-031 collapsed the 8 COUNTs into one)."""
    base = {
        "total": 16,
        "open_count": 10,
        "closed": 6,
        "escalate_pending": 4,
        "waiting_assignment": 3,
        "escalate_approved": 1,
        "escalate_scheduled": 2,
        "in_progress": 0,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _stub_kpi_execute(provider, row: SimpleNamespace) -> MagicMock:
    execute = MagicMock()
    execute.return_value.one.return_value = row
    provider._session.execute = execute
    return execute


def test_complaint_kpis_unrestricted_counts() -> None:
    provider, *_ = _provider()
    execute = _stub_kpi_execute(provider, _kpi_row())

    kpis = provider.complaint_kpis(branch_id=None)

    assert kpis.total == 16
    assert kpis.open == 10
    assert kpis.closed == 6
    assert kpis.escalate_pending == 4
    assert kpis.waiting_assignment == 3
    assert kpis.escalate_approved == 1
    assert kpis.escalate_scheduled == 2
    assert kpis.in_progress == 0
    # Slices partition the set: 3 + 4 + 1 + 2 + 0 + 6 = 16
    assert (
        kpis.waiting_assignment
        + kpis.escalate_pending
        + kpis.escalate_approved
        + kpis.escalate_scheduled
        + kpis.in_progress
        + kpis.closed
        == kpis.total
    )
    # One statement, not one per slice — this endpoint is polled every 60s.
    assert execute.call_count == 1


def test_complaint_kpis_omits_sla_when_measurement_is_off() -> None:
    provider, *_ = _provider()
    _stub_kpi_execute(provider, _kpi_row())

    kpis = provider.complaint_kpis(branch_id=None, target_days=0)

    assert kpis.sla is None


def test_complaint_kpis_rolls_up_sla_slices() -> None:
    provider, *_ = _provider()
    _stub_kpi_execute(
        provider,
        _kpi_row(
            sla_on_track=7,
            sla_warning=2,
            sla_overdue=1,
            sla_met=4,
            sla_missed=1,
            sla_unknown=1,
        ),
    )

    kpis = provider.complaint_kpis(branch_id=None, target_days=30)

    assert kpis.sla is not None
    assert kpis.sla.target_days == 30
    assert (kpis.sla.on_track, kpis.sla.warning, kpis.sla.overdue) == (7, 2, 1)
    assert (kpis.sla.met, kpis.sla.missed, kpis.sla.unknown) == (4, 1, 1)
    # Compliance counts only settled complaints: 4 of 5, not 4 of 6 — an
    # unstamped closure must not flatter the figure.
    assert kpis.sla.compliance_percentage == 80.0
    # Every complaint lands in exactly one slice.
    assert (
        kpis.sla.on_track
        + kpis.sla.warning
        + kpis.sla.overdue
        + kpis.sla.met
        + kpis.sla.missed
        + kpis.sla.unknown
        == kpis.total
    )


def test_complaint_kpis_compliance_is_none_before_anything_settles() -> None:
    provider, *_ = _provider()
    _stub_kpi_execute(
        provider,
        _kpi_row(
            sla_on_track=16,
            sla_warning=0,
            sla_overdue=0,
            sla_met=0,
            sla_missed=0,
            sla_unknown=0,
        ),
    )

    kpis = provider.complaint_kpis(branch_id=None, target_days=30)

    assert kpis.sla is not None
    # Not 0% — nothing has been judged yet, and 0% would read as total failure.
    assert kpis.sla.compliance_percentage is None


def test_complaint_kpis_branch_with_unknown_unit_is_zero() -> None:
    provider, *_ = _provider()
    provider._owning_unit_for_branch = MagicMock(return_value=None)
    execute = MagicMock()
    provider._session.execute = execute

    kpis = provider.complaint_kpis(branch_id=uuid.uuid4())

    assert kpis.total == 0
    assert kpis.open == 0
    assert kpis.closed == 0
    assert kpis.escalate_pending == 0
    assert kpis.escalate_scheduled == 0
    execute.assert_not_called()


def test_complaint_kpis_branch_passes_owning_unit_scope() -> None:
    provider, *_ = _provider()
    provider._owning_unit_for_branch = MagicMock(return_value="UPPPD-A")
    _stub_kpi_execute(provider, _kpi_row())
    branch_id = uuid.uuid4()

    provider.complaint_kpis(branch_id=branch_id)

    provider._owning_unit_for_branch.assert_called_once_with(branch_id)

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
    complaints.get.return_value = SimpleNamespace(complaint_number="CM-00000001")
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert len(items) == 1
    assert items[0].complaint_number == "CM-00000001"
    assert items[0].event_type == "complaint.created"
    assert items[0].actor == "SYSTEM"  # no actor_id, no actor_name on this row
    complaints.get.assert_called_once_with(str(entry.aggregate_id))


def test_list_recent_maps_escalation_decisions_by_metadata() -> None:
    provider, timeline, complaints, directory = _provider()
    approved = _entry(
        event_type="IntakeEscalationDecided", metadata={"decision": "APPROVE"}
    )
    rejected = _entry(
        event_type="IntakeEscalationDecided", metadata={"decision": "REJECT"}
    )
    timeline.list_recent.return_value = [approved, rejected]
    complaints.get.return_value = SimpleNamespace(complaint_number="CM-00000002")
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)

    assert [item.event_type for item in items] == [
        "complaint.escalation_approved",
        "complaint.escalation_rejected",
    ]


def test_list_recent_resolves_actor_via_directory() -> None:
    provider, timeline, complaints, directory = _provider()
    actor_id = "11111111-1111-1111-1111-111111111111"
    entry = _entry(event_type="ComplaintRegistered", actor_id=actor_id)
    timeline.list_recent.return_value = [entry]
    complaints.get.return_value = SimpleNamespace(complaint_number="CM-1")
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
    complaints.get.return_value = None
    directory.display_names.return_value = {}

    items = provider.list_recent(limit=10)
    assert items[0].complaint_number == "CM-FALLBACK"


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
        aggregate_type="Complaint", limit=10, aggregate_ids=complaint_ids
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
        aggregate_type="Complaint", limit=7, aggregate_ids=None
    )


def test_complaint_kpis_unrestricted_counts() -> None:
    provider, *_ = _provider()
    provider._count_complaints = MagicMock(side_effect=[5, 3, 2, 1])

    kpis = provider.complaint_kpis(branch_id=None)

    assert kpis.total == 5
    assert kpis.open == 3
    assert kpis.closed == 2
    assert kpis.escalate_pending == 1
    assert provider._count_complaints.call_count == 4
    # First call is unrestricted (owning_unit_id=None)
    assert provider._count_complaints.call_args_list[0].args[0] is None


def test_complaint_kpis_branch_with_unknown_unit_is_zero() -> None:
    provider, *_ = _provider()
    provider._owning_unit_for_branch = MagicMock(return_value=None)
    provider._count_complaints = MagicMock()

    kpis = provider.complaint_kpis(branch_id=uuid.uuid4())

    assert kpis.total == 0
    assert kpis.open == 0
    assert kpis.closed == 0
    assert kpis.escalate_pending == 0
    provider._count_complaints.assert_not_called()


def test_complaint_kpis_branch_passes_owning_unit_scope() -> None:
    provider, *_ = _provider()
    provider._owning_unit_for_branch = MagicMock(return_value="UPPPD-A")
    provider._count_complaints = MagicMock(return_value=0)
    branch_id = uuid.uuid4()

    provider.complaint_kpis(branch_id=branch_id)

    provider._owning_unit_for_branch.assert_called_once_with(branch_id)
    for call in provider._count_complaints.call_args_list:
        assert call.args[0] == "UPPPD-A"

"""Repository coverage boost for reports/appointments/resolutions (CI-COV-001)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.modules.appointments import repository as appt_mod
from app.modules.appointments.repository import AppointmentRepository
from app.modules.reports.repository import ReportRepository
from app.modules.resolutions import repository as res_mod
from app.modules.resolutions.repository import ResolutionRepository


def test_report_repository_aggregations() -> None:
    """``_base_filters`` resolves ``branch_id`` (UUID) → ``Branch.code`` via
    ``owning_unit_for_branch`` (DEC-024 pattern, wired into reports as part of
    DEC-026 M-026-3). A bare MagicMock session makes ``session.get(...)``
    return a truthy mock whose ``deleted_at`` is itself a truthy mock, so the
    branch reads as soft-deleted and every aggregate silently comes back
    empty — session.get must return a real not-deleted branch shape.
    """
    session = MagicMock()
    repo = ReportRepository(session)
    bid = uuid.uuid4()
    now = datetime.now(UTC)
    session.get.return_value = SimpleNamespace(deleted_at=None, code="PUSAT")

    session.scalar.return_value = 3
    assert (
        repo.count_total(branch_id=bid, date_from=now, date_to=now) == 3
    )

    session.execute.return_value.all.return_value = [("OPEN", 2), ("CLOSED", 1)]
    assert repo.count_by_status(branch_id=bid) == [("OPEN", 2), ("CLOSED", 1)]

    session.execute.return_value.all.return_value = [
        (bid, "B1", "Branch 1", 5),
        (None, None, None, 1),
    ]
    rows = repo.count_by_branch(date_from=now, date_to=now)
    assert rows[0][0] == bid
    assert rows[0][3] == 5
    assert rows[1][0] is None

    # Unresolvable branch (soft-deleted / unknown) is a known-empty scope —
    # every aggregate returns its empty shape, not an error.
    session.get.return_value = SimpleNamespace(deleted_at=now, code="PUSAT")
    assert repo.count_total(branch_id=bid) == 0
    assert repo.count_by_status(branch_id=bid) == []
    assert repo.count_by_branch(branch_id=bid) == []


def test_appointment_repository_query_paths() -> None:
    session = MagicMock()
    repo = AppointmentRepository(session)
    assert repo.session is session
    eid = uuid.uuid4()
    cid = uuid.uuid4()
    aid = uuid.uuid4()
    uid = uuid.uuid4()
    obj = MagicMock()

    session.scalar.side_effect = [obj, obj, obj, obj, uid, obj, None]
    assert repo.get_escalation(eid) is obj
    assert repo.get_complaint(cid) is obj
    assert repo.get_by_id(aid) is obj
    assert repo.get_active_by_escalation(eid) is obj
    assert repo.user_exists(uid) is True
    assert (
        repo.find_engineer_overlap(
            engineer_id=uid,
            on_date=date.today(),
            start=time(9, 0),
            end=time(10, 0),
            exclude_id=aid,
        )
        is obj
    )
    assert (
        repo.find_engineer_overlap(
            engineer_id=uid,
            on_date=date.today(),
            start=time(9, 0),
            end=time(10, 0),
        )
        is None
    )

    appt = MagicMock()
    assert repo.add(appt) is appt
    session.add.assert_called()
    repo.commit()
    session.commit.assert_called()
    assert repo.refresh(appt) is appt

    timeline = MagicMock()
    with patch.object(appt_mod, "ComplaintTimeline", return_value=timeline):
        entry = repo.add_timeline(
            complaint_id=cid,
            actor_user_id=uid,
            event_type="BOOKED",
            event_at=datetime(2026, 1, 1, 12, 0, 0),  # naive → tz added
            from_status=None,
            to_status="BOOKED",
            summary="booked",
            metadata={"k": "v"},
        )
    assert entry is timeline


def test_resolution_repository_paths() -> None:
    session = MagicMock()
    repo = ResolutionRepository(session)
    assert repo.session is session
    cid = uuid.uuid4()
    uid = uuid.uuid4()
    rid = uuid.uuid4()
    obj = MagicMock()
    session.scalar.side_effect = [obj, obj, obj, obj, obj, obj]
    assert repo.get_complaint(cid) is obj
    assert repo.get_user(uid) is obj
    assert repo.get_current_resolution(cid) is obj
    assert repo.get_final_resolution(cid) is obj
    assert repo.get_latest_appointment_for_complaint(cid) is obj
    assert repo.get_escalation(rid) is obj

    resolution = MagicMock()
    when = datetime.now(UTC)
    repo.close_current_resolution(resolution, actor_user_id=uid, when=when)
    assert resolution.is_current is False
    assert resolution.updated_by == uid

    assert repo.add_resolution(resolution) is resolution
    assert repo.refresh(resolution) is resolution
    repo.commit()
    session.commit.assert_called()

    audit = MagicMock()
    with patch.object(res_mod, "AuditLog", return_value=audit):
        entry = repo.add_audit_log(
            actor_user_id=uid,
            action="resolve",
            entity_id=cid,
            new_value={"a": 1},
            old_value=None,
            occurred_at=datetime(2026, 1, 1, 12, 0, 0),
        )
    assert entry is audit

    timeline = MagicMock()
    with patch.object(res_mod, "ComplaintTimeline", return_value=timeline):
        tl = repo.add_timeline(
            complaint_id=cid,
            actor_user_id=uid,
            event_type="RESOLVED",
            event_at=datetime.now(UTC),
            from_status="OPEN",
            to_status="RESOLVED",
            summary="done",
        )
    assert tl is timeline

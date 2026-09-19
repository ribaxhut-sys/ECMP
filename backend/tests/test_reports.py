"""Report service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.authorization.principal import Principal
from app.core.errors import ValidationAppError
from app.modules.reports.pdf import (
    ReportPrintData,
    _comparison_line,
    _signed,
    _styles,
    _user_activity_table,
    format_count,
    format_period_window,
    format_report_stamp,
    format_unit_label,
    printable_status_rows,
    report_pdf_filename,
)
from app.modules.reports.pdf_copy import copy_for, normalize_report_lang
from app.modules.reports.repository import (
    ReportRepository,
    UserActivityAgg,
    _complaint_unit_filters,
    _is_human_actor,
    _later,
)
from app.modules.reports.router import get_report_summary, print_report
from app.modules.reports.schemas import (
    AggregateComplaintStatus,
    ReportPrintCategory,
    StatusCount,
    UserActivityCount,
)
from app.modules.reports.scope import effective_report_branch_id
from app.modules.reports.service import ReportService


def test_summary_uses_aggregate_status_enum() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 5
    repo.count_by_status.return_value = [("REGISTERED", 3), ("CLOSED", 2)]

    result = ReportService(repo).summary()

    assert result.total == 5
    assert len(result.by_status) == len(AggregateComplaintStatus)
    by_status = {item.status: item.count for item in result.by_status}
    assert by_status[AggregateComplaintStatus.REGISTERED] == 3
    assert by_status[AggregateComplaintStatus.CLOSED] == 2
    assert by_status[AggregateComplaintStatus.IN_PROGRESS] == 0


def test_by_status_fills_missing_statuses() -> None:
    repo = MagicMock()
    repo.count_by_status.return_value = [("REGISTERED", 4)]

    result = ReportService(repo).by_status()

    assert [item.status for item in result] == list(AggregateComplaintStatus)
    assert result[0].status == AggregateComplaintStatus.REGISTERED
    assert result[0].count == 4
    assert result[1].count == 0


def test_by_branch_sorts_by_case_completion_percent() -> None:
    branch_a = uuid.uuid4()
    branch_b = uuid.uuid4()
    repo = MagicMock()
    repo.count_by_branch.return_value = [
        (branch_a, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 10, 9, 1, 2, 8, 2, 6),
        (branch_b, "BR-B", "Beta", 3, 0, 3, 1, 3, 0, 3),
        (None, None, None, 1, 1, 0, 0, 0, 0, 0),
    ]

    result = ReportService(repo).by_branch()

    assert [item.branch_code for item in result] == ["BR-B", "UPPPD-TANAH-ABANG", None]
    assert result[0].closed == 3
    assert result[1].closed == 1
    assert result[0].unit_code == "BRB"
    assert result[1].unit_code == "TAB"
    assert result[2].unit_code is None
    assert result[0].escalated == 1
    assert result[1].escalated == 2


def test_invalid_date_range_rejected() -> None:
    repo = MagicMock()
    service = ReportService(repo)
    date_from = datetime(2026, 7, 20, tzinfo=UTC)
    date_to = datetime(2026, 7, 10, tzinfo=UTC)

    with pytest.raises(ValidationAppError):
        service.summary(date_from=date_from, date_to=date_to)
    repo.count_total.assert_not_called()


def test_combine_case_counts_adds_implied_no_case_complaints() -> None:
    assert ReportRepository._combine_case_counts((5, 3, 2), (4, 1, 3)) == (9, 4, 5)


def test_count_by_branch_branch_resolved_excludes_hq_escalated_closed() -> None:
    """caseClosed = selesai di cabang; escalated = open only (opsi B)."""
    session = MagicMock()
    repo = ReportRepository(session)
    branch_id = uuid.uuid4()
    session.execute.return_value.all.side_effect = [
        # total=4, closed=2, escalated=1 (open-only already applied in SQL mock)
        [(branch_id, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 4, 2, 1)],
        # cases: 3 total, 2 all_closed, 1 branch_resolved (1 CLOSED+escalatedToPusat)
        [("UPPPD-TANAH-ABANG", 3, 2, 1)],
        # implied: 1 CLOSED HQ_CLOSED → all_closed=1, branch_resolved=0
        [("UPPPD-TANAH-ABANG", 1, 1, 0)],
    ]
    rows = repo.count_by_branch()
    row = rows[0]
    assert row[3:7] == (4, 2, 2, 1)  # total, open, closed, escalated
    assert row[7:10] == (4, 1, 1)  # caseTotal, caseOpen, caseClosed (branch)


def test_count_by_branch_keeps_idle_active_branches() -> None:
    """Kesehatan Cabang needs the full unit set, including zeros."""
    session = MagicMock()
    repo = ReportRepository(session)
    idle_id = uuid.uuid4()
    active_id = uuid.uuid4()
    session.execute.return_value.all.side_effect = [
        [
            (idle_id, "UPPPD-GAMBIR", "UPPPD Gambir", 0, 0, 0),
            (active_id, "UPPPD-TANAH-ABANG", "UPPPD Tanah Abang", 12, 5, 2),
        ],
        # (unit, total, all_closed, branch_resolved)
        [("UPPPD-TANAH-ABANG", 10, 2, 2)],
        [],
    ]
    rows = repo.count_by_branch()
    codes = [row[1] for row in rows]
    assert codes[0] == "UPPPD-TANAH-ABANG"
    assert "UPPPD-GAMBIR" in codes
    assert rows[0][3] == 12
    gambir = next(row for row in rows if row[1] == "UPPPD-GAMBIR")
    assert gambir[3:] == (0, 0, 0, 0, 0, 0, 0)


def test_cycle_time_summarizes_closed_case_durations() -> None:
    """Average, median, p90 and the age-band distribution over closed cases."""
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = [0.5, 2.0, 5.0, 9.0, 4.0]

    result = ReportService(repo).cycle_time()

    assert result.closed_cases == 5
    assert result.average_days == 4.1
    assert result.median_days == 4.0
    assert result.p90_days == 7.4
    assert result.fastest_days == 0.5
    assert result.slowest_days == 9.0
    assert {b.key: b.count for b in result.buckets} == {
        "sameDay": 1,
        "upTo3Days": 1,
        "upTo7Days": 2,
        "over7Days": 1,
    }


def test_cycle_time_empty_window_reports_zero_not_none_buckets() -> None:
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = []

    result = ReportService(repo).cycle_time()

    assert result.closed_cases == 0
    assert result.average_days is None
    assert [b.count for b in result.buckets] == [0, 0, 0, 0]


def test_cycle_time_rejects_inverted_window() -> None:
    repo = MagicMock()
    with pytest.raises(ValidationAppError):
        ReportService(repo).cycle_time(
            date_from=datetime(2026, 8, 31, tzinfo=UTC),
            date_to=datetime(2026, 8, 1, tzinfo=UTC),
        )
    repo.closed_case_durations_days.assert_not_called()


def test_cycle_time_forwards_normalized_window_to_repository() -> None:
    repo = MagicMock()
    repo.closed_case_durations_days.return_value = []

    ReportService(repo).cycle_time(date_from=datetime(2026, 8, 1))

    repo.closed_case_durations_days.assert_called_once_with(
        branch_id=None, date_from=datetime(2026, 8, 1, tzinfo=UTC), date_to=None
    )


def test_print_pdf_all_category_queries_every_metric() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 7
    repo.count_resolved.return_value = 4
    repo.count_escalated.return_value = 2
    repo.count_in_progress_at_branch.return_value = 1
    repo.closed_case_durations_days.return_value = [1.0, 3.0]
    repo.activity_by_user.return_value = []

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.ALL, period_label="Bulan ini"
    )

    assert pdf_bytes.startswith(b"%PDF")
    repo.count_total.assert_called_once()
    repo.count_by_status.assert_not_called()
    repo.count_resolved.assert_called_once()
    repo.count_escalated.assert_called_once()
    repo.count_in_progress_at_branch.assert_called_once()
    repo.closed_case_durations_days.assert_called_once()
    repo.activity_by_user.assert_called_once()


def test_print_pdf_escalated_category_skips_unrelated_queries() -> None:
    """A single-category export must not pay for counts it will not print —
    also guards against the PDF silently showing stale/zero data as real."""
    repo = MagicMock()
    repo.count_escalated.return_value = 5

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.ESCALATED, period_label="Minggu ini"
    )

    assert pdf_bytes.startswith(b"%PDF")
    repo.count_escalated.assert_called_once()
    repo.count_total.assert_not_called()
    repo.count_by_status.assert_not_called()
    repo.count_resolved.assert_not_called()
    repo.count_in_progress_at_branch.assert_not_called()
    repo.closed_case_durations_days.assert_not_called()
    repo.activity_by_user.assert_not_called()


def test_print_pdf_other_category_renders_without_any_query() -> None:
    """OTHER has no predicate yet — the PDF must say so, not invent a count."""
    repo = MagicMock()

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.OTHER, period_label="Tahun ini"
    )

    assert pdf_bytes.startswith(b"%PDF")
    repo.count_total.assert_not_called()
    repo.count_by_status.assert_not_called()
    repo.count_resolved.assert_not_called()
    repo.count_escalated.assert_not_called()
    repo.count_in_progress_at_branch.assert_not_called()


def test_report_stamp_converts_utc_to_jakarta() -> None:
    stamp = format_report_stamp(datetime(2026, 8, 27, 17, 30, tzinfo=UTC))
    assert stamp == "28-08-2026, 00:30 WIB"


def test_report_pdf_filename_uses_jakarta_date() -> None:
    name = report_pdf_filename(
        ReportPrintCategory.ALL, datetime(2026, 8, 27, 17, 30, tzinfo=UTC)
    )
    assert name == "laporan-pengaduan-all-2026-08-28.pdf"


def test_printable_status_rows_omits_registered() -> None:
    rows = [
        StatusCount(status=AggregateComplaintStatus.REGISTERED, count=4),
        StatusCount(status=AggregateComplaintStatus.IN_PROGRESS, count=9),
        StatusCount(status=AggregateComplaintStatus.CLOSED, count=30),
    ]
    visible = printable_status_rows(rows)
    assert [row.status for row in visible] == [
        AggregateComplaintStatus.IN_PROGRESS,
        AggregateComplaintStatus.CLOSED,
    ]


def test_format_count_includes_unit() -> None:
    assert format_count(39) == "39 pengaduan"
    assert format_count(10, "kasus") == "10 kasus"
    assert format_count(39, lang="en") == "39 complaints"


def test_format_unit_label_strips_upppd_and_defaults_all_units() -> None:
    assert format_unit_label(None) == "Semua unit"
    assert format_unit_label(None, "en") == "All units"
    assert format_unit_label("UPPPD Tanah Abang") == "Tanah Abang"


def test_format_period_window_uses_jakarta_dates() -> None:
    assert format_period_window(None, None) == "Tidak dibatasi"
    window = format_period_window(
        datetime(2026, 7, 31, 17, 0, tzinfo=UTC),
        datetime(2026, 8, 27, 16, 59, tzinfo=UTC),
    )
    assert window == "01-08-2026 - 27-08-2026"
    assert format_period_window(None, None, "en") == "Not limited"


def test_normalize_report_lang() -> None:
    assert normalize_report_lang(None) == "id"
    assert normalize_report_lang("id") == "id"
    assert normalize_report_lang("en") == "en"
    assert normalize_report_lang("en-US") == "en"


def test_effective_report_branch_id_locks_cabang() -> None:
    own = uuid.uuid4()
    other = uuid.uuid4()
    session = MagicMock()
    session.scalar.side_effect = [own, "UPPPD-TANAH-ABANG"]
    principal = Principal(user_id=uuid.uuid4(), roles=("MANAGER",))

    assert effective_report_branch_id(session, principal, other) == own

    session.scalar.side_effect = [own, "UPPPD-TANAH-ABANG"]
    assert effective_report_branch_id(session, principal, None) == own


def test_effective_report_branch_id_head_office_honors_request() -> None:
    requested = uuid.uuid4()
    session = MagicMock()
    session.scalar.return_value = None
    principal = Principal(user_id=uuid.uuid4(), roles=("ADMIN",))

    assert effective_report_branch_id(session, principal, requested) == requested
    session.scalar.assert_called_once()

    session.scalar.return_value = None
    assert effective_report_branch_id(session, principal, None) is None


def test_effective_report_branch_id_pusat_home_honors_request() -> None:
    own = uuid.uuid4()
    requested = uuid.uuid4()
    session = MagicMock()
    session.scalar.side_effect = [own, "PUSAT"]
    principal = Principal(user_id=uuid.uuid4(), roles=("HO_SCHEDULER",))

    assert effective_report_branch_id(session, principal, requested) == requested

    session.scalar.side_effect = [own, "PUSAT-CRO"]
    assert effective_report_branch_id(session, principal, None) is None


def test_summary_route_uses_effective_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    own = uuid.uuid4()
    other = uuid.uuid4()
    monkeypatch.setattr(
        "app.modules.reports.router.effective_report_branch_id",
        lambda _session, _principal, _requested: own,
    )
    svc = MagicMock()
    svc.summary.return_value = MagicMock()
    principal = Principal(user_id=uuid.uuid4(), roles=("MANAGER",))

    get_report_summary(
        service=svc,
        principal=principal,
        session=MagicMock(),
        branch_id=other,
    )

    svc.summary.assert_called_once()
    assert svc.summary.call_args.kwargs["branch_id"] == own


def test_print_route_loads_label_for_effective_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    effective = uuid.uuid4()
    monkeypatch.setattr(
        "app.modules.reports.router.effective_report_branch_id",
        lambda _session, _principal, _requested: effective,
    )
    svc = MagicMock()
    svc.print_pdf.return_value = b"%PDF-mock"
    session = MagicMock()
    session.scalar.return_value = "UPPPD Tanah Abang"
    principal = Principal(user_id=uuid.uuid4(), roles=("MANAGER",))

    response = print_report(
        service=svc,
        session=session,
        principal=principal,
        branch_id=uuid.uuid4(),
    )

    assert response.media_type == "application/pdf"
    assert svc.print_pdf.call_args.kwargs["branch_id"] == effective
    assert svc.print_pdf.call_args.kwargs["branch_label"] == "UPPPD Tanah Abang"


def test_print_pdf_english_renders() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 7
    repo.count_resolved.return_value = 4
    repo.count_escalated.return_value = 2
    repo.count_in_progress_at_branch.return_value = 1
    repo.closed_case_durations_days.return_value = [1.0, 3.0]
    repo.activity_by_user.return_value = []

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.ALL,
        period_label="This month",
        lang="en-US",
    )

    assert pdf_bytes.startswith(b"%PDF")


def test_print_pdf_comparison_queries_previous_window() -> None:
    repo = MagicMock()
    repo.count_total.return_value = 7
    repo.count_resolved.return_value = 4
    repo.count_escalated.return_value = 2
    repo.count_in_progress_at_branch.return_value = 1
    repo.closed_case_durations_days.return_value = [1.0]
    repo.activity_by_user.return_value = []

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.ALL,
        period_label="Bulan ini",
        date_from=datetime(2026, 8, 1, tzinfo=UTC),
        date_to=datetime(2026, 8, 18, tzinfo=UTC),
        compare_from=datetime(2026, 7, 1, tzinfo=UTC),
        compare_to=datetime(2026, 7, 18, tzinfo=UTC),
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert repo.count_total.call_count == 2
    assert repo.count_resolved.call_count == 2
    assert repo.count_escalated.call_count == 2
    assert repo.count_in_progress_at_branch.call_count == 2
    repo.activity_by_user.assert_called_once()


def test_by_user_maps_repository_rows() -> None:
    actor = uuid.uuid4()
    stamp = datetime(2026, 8, 18, 10, tzinfo=UTC)
    repo = MagicMock()
    repo.activity_by_user.return_value = [
        UserActivityAgg(
            user_id=str(actor),
            display_name="Ani Petugas",
            username="ani",
            branch_id=actor,
            branch_name="UPPPD Tanah Abang",
            created_count=3,
            decided_count=1,
            closed_count=2,
            activity_count=9,
            last_activity_at=stamp,
        )
    ]

    result = ReportService(repo).by_user()

    assert len(result) == 1
    assert result[0].display_name == "Ani Petugas"
    assert result[0].username == "ani"
    assert result[0].created_count == 3
    assert result[0].decided_count == 1
    assert result[0].closed_count == 2
    assert result[0].activity_count == 9
    assert result[0].last_activity_at == stamp
    repo.activity_by_user.assert_called_once()


def test_by_user_rejects_inverted_window() -> None:
    repo = MagicMock()
    with pytest.raises(ValidationAppError):
        ReportService(repo).by_user(
            date_from=datetime(2026, 8, 31, tzinfo=UTC),
            date_to=datetime(2026, 8, 1, tzinfo=UTC),
        )
    repo.activity_by_user.assert_not_called()


def test_activity_by_user_unknown_branch_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    repo = ReportRepository(session)
    monkeypatch.setattr(
        "app.modules.reports.repository.owning_unit_for_branch",
        lambda *_a, **_k: None,
    )
    assert repo.activity_by_user(branch_id=uuid.uuid4()) == []
    session.execute.assert_not_called()


def test_print_pdf_all_renders_when_officer_activity_present() -> None:
    stamp = datetime(2026, 8, 18, 10, tzinfo=UTC)
    repo = MagicMock()
    repo.count_total.return_value = 3
    repo.count_resolved.return_value = 1
    repo.count_escalated.return_value = 0
    repo.count_in_progress_at_branch.return_value = 2
    repo.closed_case_durations_days.return_value = []
    repo.activity_by_user.return_value = [
        UserActivityAgg(
            user_id="u-ani",
            display_name="Ani Petugas",
            username="ani",
            branch_id=None,
            branch_name="UPPPD Tanah Abang",
            created_count=2,
            decided_count=0,
            closed_count=1,
            activity_count=5,
            last_activity_at=stamp,
        )
    ]

    pdf_bytes = ReportService(repo).print_pdf(
        category=ReportPrintCategory.ALL, period_label="Bulan ini"
    )

    assert pdf_bytes.startswith(b"%PDF")
    repo.activity_by_user.assert_called_once()


def test_user_activity_table_lists_officer_name() -> None:
    table = _user_activity_table(
        [
            UserActivityCount(
                userId="u-ani",
                displayName="Ani Petugas",
                username="ani",
                createdCount=2,
                decidedCount=0,
                closedCount=1,
                activityCount=5,
            )
        ],
        _styles(),
        copy_for("id"),
    )
    assert "Ani Petugas" in table._cellvalues[1][0].getPlainText()
    assert "2" in table._cellvalues[1][2].getPlainText()


def test_human_actor_and_later_helpers() -> None:
    assert _is_human_actor(None) is False
    assert _is_human_actor("  ") is False
    assert _is_human_actor("system") is False
    assert _is_human_actor("SYSTEM") is False
    assert _is_human_actor("u-1") is True
    stamp = datetime(2026, 8, 1, tzinfo=UTC)
    later = datetime(2026, 8, 2, tzinfo=UTC)
    assert _later(None, stamp) is stamp
    assert _later(stamp, None) is stamp
    assert _later(stamp, later) is later
    assert _later(later, stamp) is later
    assert _complaint_unit_filters(None) == []
    assert _complaint_unit_filters("TAB")


def test_report_counts_unknown_branch_are_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    repo = ReportRepository(session)
    monkeypatch.setattr(
        "app.modules.reports.repository.owning_unit_for_branch",
        lambda *_a, **_k: None,
    )
    branch_id = uuid.uuid4()
    assert repo.count_total(branch_id=branch_id) == 0
    assert repo.count_resolved(branch_id=branch_id) == 0
    assert repo.count_escalated(branch_id=branch_id) == 0
    assert repo.count_in_progress_at_branch(branch_id=branch_id) == 0
    assert repo.count_by_status(branch_id=branch_id) == []
    assert repo._case_counts_by_unit(branch_id=branch_id, date_from=None, date_to=None) == {}
    assert repo._implied_case_counts_by_unit(
        branch_id=branch_id, date_from=None, date_to=None
    ) == {}
    assert repo.count_by_branch(branch_id=branch_id) == []
    assert repo.closed_case_durations_days(branch_id=branch_id) == []
    session.execute.assert_not_called()


def test_report_count_paths_with_unit_and_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    session.scalar.return_value = 4
    session.execute.return_value.all.return_value = [("IN_PROGRESS", 4)]
    repo = ReportRepository(session)
    monkeypatch.setattr(
        "app.modules.reports.repository.owning_unit_for_branch",
        lambda *_a, **_k: "TAB",
    )
    date_from = datetime(2026, 8, 1, tzinfo=UTC)
    date_to = datetime(2026, 8, 31, tzinfo=UTC)
    branch_id = uuid.uuid4()
    assert repo.count_in_progress_at_branch(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    ) == 4
    assert repo.count_resolved(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    ) == 4
    assert repo.count_escalated(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    ) == 4
    assert repo.count_by_status(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    ) == [("IN_PROGRESS", 4)]


def test_closed_case_durations_skips_null_and_clamps_negative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    created = datetime(2026, 8, 10, tzinfo=UTC)
    closed = datetime(2026, 8, 8, tzinfo=UTC)
    session.execute.return_value.all.return_value = [
        (None, closed),
        (created, None),
        (created, closed),
    ]
    repo = ReportRepository(session)
    monkeypatch.setattr(
        "app.modules.reports.repository.owning_unit_for_branch",
        lambda *_a, **_k: "TAB",
    )
    days = repo.closed_case_durations_days(
        branch_id=uuid.uuid4(),
        date_from=datetime(2026, 8, 1, tzinfo=UTC),
        date_to=datetime(2026, 8, 31, tzinfo=UTC),
    )
    assert days == [0.0]


def test_activity_by_user_merges_actor_buckets() -> None:
    session = MagicMock()
    repo = ReportRepository(session)
    actor = str(uuid.uuid4())
    other = "bukan-uuid"
    early = datetime(2026, 8, 1, tzinfo=UTC)
    late = datetime(2026, 8, 18, tzinfo=UTC)
    repo._actor_counts = MagicMock(  # type: ignore[method-assign]
        side_effect=[
            {actor: (2, early), "system": (9, late)},
            {actor: (1, late)},
        ]
    )
    repo._closed_case_actor_counts = MagicMock(  # type: ignore[method-assign]
        return_value={actor: (3, None)}
    )
    repo._timeline_actor_counts = MagicMock(  # type: ignore[method-assign]
        return_value={actor: (4, late, "Ani"), other: (1, early, None)}
    )
    branch_id = uuid.uuid4()
    repo._directory_rows = MagicMock(  # type: ignore[method-assign]
        return_value={
            actor: ("Ani Petugas", "ani", branch_id, "UPPPD Tanah Abang"),
        }
    )
    rows = repo.activity_by_user(
        date_from=early,
        date_to=late,
    )
    by_id = {row.user_id: row for row in rows}
    assert by_id[actor].created_count == 2
    assert by_id[actor].decided_count == 1
    assert by_id[actor].closed_count == 3
    assert by_id[actor].activity_count == 4
    assert by_id[actor].display_name == "Ani Petugas"
    assert by_id[actor].last_activity_at == late
    assert by_id[other].display_name == other
    assert by_id[other].username is None


def test_actor_and_directory_sql_helpers() -> None:
    from app.modules.cm_batch1.models import CmBatch1ComplaintORM

    session = MagicMock()
    actor = uuid.uuid4()
    stamp = datetime(2026, 8, 18, tzinfo=UTC)
    session.execute.return_value.all.side_effect = [
        [(str(actor), 2, stamp), ("system", 1, stamp), ("", 1, stamp)],
        [(str(actor), 3, stamp, "Ani")],
        [(actor, "Ani Petugas", "ani", uuid.uuid4(), "Cabang")],
        [(str(actor), 1, stamp)],
    ]
    repo = ReportRepository(session)
    counts = repo._actor_counts(
        CmBatch1ComplaintORM.created_by,
        CmBatch1ComplaintORM.created_at,
        extra=[],
        date_from=stamp,
        date_to=stamp,
    )
    assert counts[str(actor)] == (2, stamp)
    assert "system" not in counts
    timeline = repo._timeline_actor_counts(
        "TAB",
        date_from=stamp,
        date_to=stamp,
    )
    assert timeline[str(actor)][0] == 3
    directory = repo._directory_rows({str(actor), "bukan-uuid"})
    assert directory[str(actor)][0] == "Ani Petugas"
    assert repo._directory_rows(set()) == {}
    closed = repo._closed_case_actor_counts("TAB", stamp, stamp)
    assert isinstance(closed, dict)


def test_case_count_helpers_execute_grouped_sql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    session.execute.return_value.all.return_value = [("TAB", 5, 2, 1)]
    repo = ReportRepository(session)
    monkeypatch.setattr(
        "app.modules.reports.repository.owning_unit_for_branch",
        lambda *_a, **_k: "TAB",
    )
    date_from = datetime(2026, 8, 1, tzinfo=UTC)
    date_to = datetime(2026, 8, 31, tzinfo=UTC)
    branch_id = uuid.uuid4()
    actual = repo._case_counts_by_unit(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    )
    implied = repo._implied_case_counts_by_unit(
        branch_id=branch_id, date_from=date_from, date_to=date_to
    )
    assert actual["TAB"] == (5, 3, 1)
    assert implied["TAB"] == (5, 3, 1)


@pytest.mark.parametrize(
    "category",
    [
        ReportPrintCategory.CREATED,
        ReportPrintCategory.RESOLVED,
        ReportPrintCategory.ESCALATED,
    ],
)
def test_print_pdf_category_variants_with_comparison(
    category: ReportPrintCategory,
) -> None:
    repo = MagicMock()
    repo.count_total.return_value = 7
    repo.count_by_status.return_value = [("REGISTERED", 4), ("IN_PROGRESS", 3)]
    repo.count_resolved.return_value = 4
    repo.count_escalated.return_value = 2
    repo.count_in_progress_at_branch.return_value = 1
    repo.closed_case_durations_days.return_value = [1.0, 4.0]
    repo.activity_by_user.return_value = []
    pdf_bytes = ReportService(repo).print_pdf(
        category=category,
        period_label="Agustus 2026",
        lang="id",
        date_from=datetime(2026, 8, 1, tzinfo=UTC),
        date_to=datetime(2026, 8, 31, tzinfo=UTC),
        compare_from=datetime(2026, 7, 1, tzinfo=UTC),
        compare_to=datetime(2026, 7, 31, tzinfo=UTC),
    )
    assert pdf_bytes.startswith(b"%PDF")


def test_comparison_line_per_category() -> None:
    copy = copy_for("id")
    base = dict(
        period_label="Agustus",
        branch_label=None,
        generated_at=datetime(2026, 8, 18, tzinfo=UTC),
        total_created=5,
        resolved=2,
        escalated=1,
        in_progress_at_branch=2,
        previous_total_created=3,
        previous_resolved=4,
        previous_escalated=0,
        previous_in_progress_at_branch=1,
        has_comparison=True,
    )
    created = ReportPrintData(category=ReportPrintCategory.CREATED, **base)
    resolved = ReportPrintData(category=ReportPrintCategory.RESOLVED, **base)
    escalated = ReportPrintData(category=ReportPrintCategory.ESCALATED, **base)
    other = ReportPrintData(category=ReportPrintCategory.OTHER, **base)
    assert _signed(2) == "+2"
    assert _signed(-1) == "-1"
    assert _comparison_line(created, copy)
    assert _comparison_line(resolved, copy)
    assert _comparison_line(escalated, copy)
    assert _comparison_line(other, copy) is None
    assert _comparison_line(
        ReportPrintData(
            category=ReportPrintCategory.ALL,
            period_label="x",
            branch_label=None,
            generated_at=datetime(2026, 8, 18, tzinfo=UTC),
            has_comparison=False,
        ),
        copy,
    ) is None

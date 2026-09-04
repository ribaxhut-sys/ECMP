"""Pengaduan Internal list report PDF (API-553).

The paper form of /internal/reports: the same filtered population the screen
shows, as a status breakdown plus one line per ticket. Operator-only, read-only,
same visibility as the list endpoint. Not a per-ticket snapshot (that is
API-550) and not a WP Case dump (API-539).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.operator_pdf import OPERATOR_PDF_AGENCY, OperatorPdfDoc, dash
from app.modules.cm_case.application.pdf_dates import format_pdf_datetime
from app.modules.internal_complaint.application.dto import (
    InternalComplaintSummaryDTO,
)
from app.modules.internal_complaint.application.pdf_labels import (
    CATEGORY_LABEL,
    PRIORITY_LABEL,
    STATUS_LABEL,
    label,
)
from app.modules.internal_complaint.domain.aggregate import (
    canonicalize_internal_handling_unit,
)

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_REPORT_TITLE = "Laporan Pengaduan Internal"
# Column widths in points; the content box is 495pt wide (A4 minus margins).
_TABLE_WIDTHS = [22.0, 96.0, 158.0, 62.0, 66.0, 50.0, 41.0]
# Headers are sized to fit their column: a truncated header ("Unit Penang...")
# reads as a defect on a printed report.
_TABLE_HEADERS = [
    "No",
    "Nomor",
    "Subjek",
    "Unit",
    "Status",
    "Prioritas",
    "Dibuat",
]
# Status order on the breakdown, so a period with zero CLOSED still says so.
_STATUS_ORDER = (
    "CREATED",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
    "WITHDRAWN",
)


@dataclass(frozen=True)
class InternalReportFilters:
    """What the operator had applied on screen when they pressed export."""

    status: str | None = None
    category: str | None = None
    priority: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    query: str | None = None


@dataclass
class InternalReportSnapshot:
    rows: list[InternalComplaintSummaryDTO] = field(default_factory=list)
    #: Rows matching the filters server-side; larger than ``rows`` when the
    #: export cap trimmed the tail.
    total_matched: int = 0
    filters: InternalReportFilters = field(default_factory=InternalReportFilters)
    exported_by: str = ""
    exported_at: datetime | None = None


def internal_report_pdf_filename(when: datetime | None = None) -> str:
    """`laporan-pengaduan-internal_20260902.pdf` — Jakarta calendar day."""
    stamp = (when or datetime.now(_OPERATOR_TZ)).astimezone(_OPERATOR_TZ).strftime(
        "%Y%m%d"
    )
    return f"laporan-pengaduan-internal_{stamp}.pdf"


def render_internal_report_pdf(snapshot: InternalReportSnapshot) -> bytes:
    exported_at = snapshot.exported_at or datetime.now(_OPERATOR_TZ)
    footer = (
        f"INTERNAL  |  {_REPORT_TITLE}  |  "
        f"diunduh {format_pdf_datetime(exported_at)}  |  "
        f"{snapshot.exported_by or '-'}"
    )
    doc = OperatorPdfDoc(footer=footer)
    _write_report(doc, snapshot, exported_at)
    return doc.build()


def _period_label(filters: InternalReportFilters) -> str:
    start = (filters.date_from or "").strip()
    end = (filters.date_to or "").strip()
    if start and end:
        return f"{start} s.d. {end}"
    if start:
        return f"Sejak {start}"
    if end:
        return f"Sampai {end}"
    return "Semua periode"


def _write_report(
    doc: OperatorPdfDoc, snapshot: InternalReportSnapshot, exported_at: datetime
) -> None:
    filters = snapshot.filters
    rows = snapshot.rows

    doc.letterhead_centered(
        OPERATOR_PDF_AGENCY,
        _REPORT_TITLE,
        subject=_period_label(filters),
    )
    doc.blank()

    doc.heading("Kriteria")
    doc.kv_block(
        [
            ("Periode", _period_label(filters)),
            ("Status", label(STATUS_LABEL, filters.status) if filters.status else "Semua"),
            (
                "Kategori",
                label(CATEGORY_LABEL, filters.category) if filters.category else "Semua",
            ),
            (
                "Prioritas",
                label(PRIORITY_LABEL, filters.priority) if filters.priority else "Semua",
            ),
            ("Pencarian", dash(filters.query)),
            ("Jumlah baris", str(len(rows))),
            ("Total sesuai kriteria", str(snapshot.total_matched or len(rows))),
            ("Diekspor oleh", dash(snapshot.exported_by)),
            ("Waktu ekspor", format_pdf_datetime(exported_at)),
        ]
    )

    if snapshot.total_matched > len(rows):
        doc.blank()
        doc.muted(
            f"Hanya {len(rows)} baris pertama yang dicetak dari "
            f"{snapshot.total_matched} yang sesuai kriteria. Persempit filter "
            "untuk laporan yang utuh."
        )

    doc.blank()
    doc.heading("Distribusi Status")
    counts = Counter((r.status or "").strip().upper() for r in rows)
    breakdown: list[tuple[str, str | None]] = [
        (label(STATUS_LABEL, status), str(counts.get(status, 0)))
        for status in _STATUS_ORDER
    ]
    for status, count in sorted(counts.items()):
        if status and status not in _STATUS_ORDER:
            breakdown.append((label(STATUS_LABEL, status), str(count)))
    doc.kv_block(breakdown)

    doc.blank()
    doc.heading("Daftar Pengaduan")
    if not rows:
        doc.para("Tidak ada pengaduan internal yang sesuai kriteria.")
        return
    doc.table(
        _TABLE_HEADERS,
        [
            [
                str(index),
                dash(row.complaint_number),
                dash(row.subject),
                dash(canonicalize_internal_handling_unit(row.handling_unit_id)),
                label(STATUS_LABEL, row.status),
                label(PRIORITY_LABEL, row.priority),
                _short_date(row.created_at),
            ]
            for index, row in enumerate(rows, start=1)
        ],
        _TABLE_WIDTHS,
    )


def _short_date(value: datetime) -> str:
    return value.astimezone(_OPERATOR_TZ).strftime("%d-%m-%y")

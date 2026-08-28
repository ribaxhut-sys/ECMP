"""Print-friendly PDF rendering for /reports (server-side, no client dependency).

Pure-Python (reportlab) — no system packages, unlike a headless-browser or
WeasyPrint route, so the runtime image needs no changes to grow this feature.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.modules.reports.schemas import (
    AggregateComplaintStatus,
    CycleTimeBucket,
    CycleTimeData,
    ReportPrintCategory,
    StatusCount,
)

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_UNIT_PREFIX = re.compile(r"^(?:UPPPD|UP3D)[\s.\-]+", re.IGNORECASE)
REPORT_PDF_AGENCY = "Unit Pelayanan Pemungutan Pajak Daerah"

_STATUS_LABELS: dict[str, str] = {
    "IN_PROGRESS": "Diproses",
    "CLOSED": "Ditutup",
}

_CATEGORY_TITLES: dict[ReportPrintCategory, str] = {
    ReportPrintCategory.ALL: "Semua Pengaduan",
    ReportPrintCategory.CREATED: "Pengaduan Dibuat",
    ReportPrintCategory.RESOLVED: "Pengaduan Diselesaikan",
    ReportPrintCategory.ESCALATED: "Pengaduan Dieskalasi",
    ReportPrintCategory.OTHER: "Lainnya",
}

_BUCKET_LABELS: dict[str, str] = {
    "sameDay": "Sampai 1 hari",
    "upTo3Days": "Lebih dari 1 sampai 3 hari",
    "upTo7Days": "Lebih dari 3 sampai 7 hari",
    "over7Days": "Lebih dari 7 hari",
}

_INK = colors.HexColor("#111827")
_MUTED = colors.HexColor("#6b7280")
_RULE = colors.HexColor("#d1d5db")
_HEAD_BG = colors.HexColor("#f3f4f6")


@dataclass(frozen=True)
class ReportPrintData:
    """Everything the PDF needs — one shape for every category.

    Fields not relevant to the selected category are simply left unused by
    the renderer instead of branching the caller into five payload types.
    """

    category: ReportPrintCategory
    period_label: str
    branch_label: str | None
    generated_at: datetime
    date_from: datetime | None = None
    date_to: datetime | None = None
    total_created: int = 0
    by_status: list[StatusCount] = field(default_factory=list)
    resolved: int = 0
    escalated: int = 0
    in_progress_at_branch: int = 0
    cycle_time: CycleTimeData | None = None
    #: Always True today — OTHER has no predicate yet (future status/disposition).
    other_pending: bool = True


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "agency": ParagraphStyle(
            "agency",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            alignment=TA_CENTER,
            textColor=_INK,
        ),
        "masthead": ParagraphStyle(
            "masthead",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=_INK,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=_INK,
            spaceBefore=8,
            spaceAfter=2,
        ),
        "heading": ParagraphStyle(
            "heading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=_INK,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=_INK,
        ),
        "muted": ParagraphStyle(
            "muted",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=_MUTED,
        ),
        "value": ParagraphStyle(
            "value",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_RIGHT,
            textColor=_INK,
        ),
        "label": ParagraphStyle(
            "label",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=_INK,
        ),
    }


def _as_jakarta(value: datetime) -> datetime:
    aware = value if value.tzinfo else value.replace(tzinfo=UTC)
    return aware.astimezone(_OPERATOR_TZ)


def format_report_stamp(value: datetime) -> str:
    """Operator-facing download stamp: DD-MM-YYYY, HH:MM WIB (never raw UTC)."""
    local = _as_jakarta(value)
    return f"{local.strftime('%d-%m-%Y')}, {local.strftime('%H:%M')} WIB"


def format_report_date(value: datetime) -> str:
    return _as_jakarta(value).strftime("%d-%m-%Y")


def format_period_window(
    date_from: datetime | None,
    date_to: datetime | None,
) -> str:
    """Inclusive calendar window in Asia/Jakarta, or 'Tidak dibatasi'."""
    if date_from is None and date_to is None:
        return "Tidak dibatasi"
    start = format_report_date(date_from) if date_from is not None else "..."
    end = format_report_date(date_to) if date_to is not None else "..."
    return f"{start} - {end}"


def format_unit_label(branch_label: str | None) -> str:
    """Letterhead / identitas unit. Unscoped report = semua unit."""
    raw = (branch_label or "").strip()
    if not raw:
        return "Semua unit"
    stripped = _UNIT_PREFIX.sub("", raw).strip()
    return stripped or raw


def format_count(value: int, unit: str = "pengaduan") -> str:
    return f"{value} {unit}"


def format_days(value: float | None) -> str:
    return f"{value:.1f} hari" if value is not None else "-"


def report_pdf_filename(category: ReportPrintCategory, generated_at: datetime) -> str:
    day = _as_jakarta(generated_at).strftime("%Y-%m-%d")
    return f"laporan-pengaduan-{category.value}-{day}.pdf"


def printable_status_rows(rows: list[StatusCount]) -> list[StatusCount]:
    """Omit REGISTERED from the operator PDF.

    That label collides with "total created" and with the screen's operational
    slices (waiting / eskalasi / diproses). Intake-without-Case is not a
    report row operators need to reconcile.
    """
    return [row for row in rows if row.status != AggregateComplaintStatus.REGISTERED]


def _kv_table(rows: Sequence[tuple[str, str]], styles: dict[str, ParagraphStyle]) -> Table:
    data = [
        [Paragraph(label, styles["label"]), Paragraph(value, styles["value"])]
        for label, value in rows
    ]
    table = Table(data, colWidths=[95 * mm, 75 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, _RULE),
            ]
        )
    )
    return table


def _status_table(
    rows: list[StatusCount], styles: dict[str, ParagraphStyle]
) -> Table:
    header = [
        Paragraph("Status", styles["label"]),
        Paragraph("Jumlah", styles["value"]),
    ]
    body = [
        [
            Paragraph(
                _STATUS_LABELS.get(row.status.value, row.status.value),
                styles["label"],
            ),
            Paragraph(format_count(row.count), styles["value"]),
        ]
        for row in printable_status_rows(rows)
    ]
    table = Table([header, *body], colWidths=[95 * mm, 75 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _HEAD_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.4, _RULE),
            ]
        )
    )
    return table


def _cycle_time_rows(data: CycleTimeData) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        ("Kasus ditutup pada periode ini", format_count(data.closed_cases, "kasus")),
        ("Rata-rata waktu penyelesaian", format_days(data.average_days)),
        ("Median waktu penyelesaian", format_days(data.median_days)),
        ("Persentil 90", format_days(data.p90_days)),
        ("Tercepat", format_days(data.fastest_days)),
        ("Terlama", format_days(data.slowest_days)),
    ]
    for bucket in data.buckets:
        rows.append(_bucket_row(bucket, data.closed_cases))
    return rows


def _bucket_row(bucket: CycleTimeBucket, closed_cases: int) -> tuple[str, str]:
    label = _BUCKET_LABELS.get(bucket.key, bucket.key)
    if closed_cases <= 0:
        return (label, format_count(bucket.count, "kasus"))
    share = round((bucket.count / closed_cases) * 100)
    return (label, f"{bucket.count} kasus ({share}%)")


def _footer(stamp: str):
    def _draw(canvas, _doc) -> None:  # noqa: ANN001
        canvas.saveState()
        canvas.setStrokeColor(_RULE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_MUTED)
        canvas.drawString(
            20 * mm,
            10 * mm,
            f"INTERNAL  |  Laporan Pengaduan  |  diunduh {stamp}",
        )
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Halaman {_doc.page}")
        canvas.restoreState()

    return _draw


def build_report_pdf(data: ReportPrintData) -> bytes:
    import io

    stamp = format_report_stamp(data.generated_at)
    unit = format_unit_label(data.branch_label)
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=16 * mm,
        bottomMargin=22 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"Laporan Pengaduan — {_CATEGORY_TITLES[data.category]}",
        author=REPORT_PDF_AGENCY,
    )
    story: list[object] = []

    story.append(Paragraph(REPORT_PDF_AGENCY, styles["agency"]))
    story.append(Paragraph(unit, styles["masthead"]))
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=_INK, spaceAfter=2))
    story.append(Paragraph("Laporan Pengaduan", styles["title"]))
    story.append(
        Paragraph(_CATEGORY_TITLES[data.category], styles["masthead"])
    )
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Identitas", styles["heading"]))
    story.append(
        _kv_table(
            [
                ("Kategori", _CATEGORY_TITLES[data.category]),
                ("Periode", data.period_label),
                ("Rentang tanggal", format_period_window(data.date_from, data.date_to)),
                ("Unit", unit),
                ("Diunduh", stamp),
            ],
            styles,
        )
    )

    if data.category == ReportPrintCategory.ALL:
        story.append(Paragraph("Ringkasan", styles["heading"]))
        story.append(
            _kv_table(
                [
                    ("Total pengaduan dibuat", format_count(data.total_created)),
                    ("Diselesaikan", format_count(data.resolved)),
                    ("Dieskalasi ke Pusat", format_count(data.escalated)),
                    ("Masih diproses", format_count(data.in_progress_at_branch)),
                ],
                styles,
            )
        )
        story.append(Spacer(1, 2 * mm))
        story.append(
            Paragraph(
                "Masih diproses termasuk dikembalikan ke cabang — pengaduan "
                "masih berjalan. Dieskalasi hanya yang masih di jalur Pusat. "
                "Diselesaikan memakai tanggal penutupan; yang lain memakai "
                "tanggal pengaduan dibuat.",
                styles["muted"],
            )
        )
        _append_cycle_time(story, data.cycle_time, styles)
    elif data.category == ReportPrintCategory.CREATED:
        story.append(Paragraph("Ringkasan", styles["heading"]))
        story.append(
            _kv_table(
                [("Total pengaduan dibuat", format_count(data.total_created))],
                styles,
            )
        )
        visible = printable_status_rows(data.by_status)
        if visible:
            story.append(Paragraph("Status saat ini", styles["heading"]))
            story.append(_status_table(data.by_status, styles))
    elif data.category == ReportPrintCategory.RESOLVED:
        story.append(Paragraph("Ringkasan", styles["heading"]))
        story.append(
            _kv_table(
                [
                    (
                        "Total pengaduan diselesaikan",
                        format_count(data.resolved),
                    )
                ],
                styles,
            )
        )
        story.append(Spacer(1, 2 * mm))
        story.append(
            Paragraph(
                "Dihitung dari tanggal penutupan, bukan tanggal pengaduan dibuat.",
                styles["muted"],
            )
        )
        _append_cycle_time(story, data.cycle_time, styles)
    elif data.category == ReportPrintCategory.ESCALATED:
        story.append(Paragraph("Ringkasan", styles["heading"]))
        story.append(
            _kv_table(
                [
                    (
                        "Total pengaduan dieskalasi ke Pusat",
                        format_count(data.escalated),
                    )
                ],
                styles,
            )
        )
        story.append(Spacer(1, 2 * mm))
        story.append(
            Paragraph(
                "Hanya pengaduan yang masih di jalur Pusat "
                "(menunggu persetujuan, disetujui, atau terjadwal kunjungan).",
                styles["muted"],
            )
        )
    else:
        story.append(Paragraph("Ringkasan", styles["heading"]))
        story.append(
            Paragraph(
                "Kategori ini menunggu definisi status baru dan belum memiliki "
                "data. Laporan akan terisi begitu status tersebut ditambahkan "
                "ke domain pengaduan.",
                styles["body"],
            )
        )

    footer = _footer(stamp)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def _append_cycle_time(
    story: list[object],
    cycle_time: CycleTimeData | None,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(Paragraph("Umur penyelesaian", styles["heading"]))
    if cycle_time is None or cycle_time.closed_cases <= 0:
        story.append(
            Paragraph(
                "Tidak ada kasus ditutup pada rentang tanggal ini.",
                styles["muted"],
            )
        )
        return
    story.append(_kv_table(_cycle_time_rows(cycle_time), styles))
    story.append(Spacer(1, 2 * mm))
    story.append(
        Paragraph(
            "Diukur dari kasus dibuat sampai ditutup, dalam hari, pada jendela "
            "tanggal penutupan.",
            styles["muted"],
        )
    )

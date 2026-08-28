"""Print-friendly PDF rendering for /reports (server-side, no client dependency).

Pure-Python (reportlab) — no system packages, unlike a headless-browser or
WeasyPrint route, so the runtime image needs no changes to grow this feature.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.modules.reports.schemas import CycleTimeData, ReportPrintCategory, StatusCount

_STATUS_LABELS: dict[str, str] = {
    "REGISTERED": "Terdaftar",
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
    total_created: int = 0
    by_status: list[StatusCount] = field(default_factory=list)
    resolved: int = 0
    escalated: int = 0
    cycle_time: CycleTimeData | None = None
    #: Always True today — OTHER has no predicate yet (future status/disposition).
    other_pending: bool = True


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": base["Title"],
        "heading": base["Heading2"],
        "body": base["BodyText"],
        "muted": ParagraphStyle(
            "muted", parent=base["BodyText"], textColor=colors.HexColor("#6b7280")
        ),
    }


def _headline_table(rows: list[tuple[str, str]]) -> Table:
    table = Table(rows, colWidths=[90 * mm, 60 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#111827")),
            ]
        )
    )
    return table


def _status_table(rows: list[StatusCount]) -> Table:
    header = ["Status", "Jumlah"]
    body = [[_STATUS_LABELS.get(row.status.value, row.status.value), str(row.count)] for row in rows]
    table = Table([header, *body], colWidths=[90 * mm, 60 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
            ]
        )
    )
    return table


def _cycle_time_rows(data: CycleTimeData) -> list[tuple[str, str]]:
    def fmt(value: float | None) -> str:
        return f"{value:.1f} hari" if value is not None else "-"

    return [
        ("Case ditutup pada periode ini", str(data.closed_cases)),
        ("Rata-rata waktu penyelesaian", fmt(data.average_days)),
        ("Median waktu penyelesaian", fmt(data.median_days)),
        ("P90 waktu penyelesaian", fmt(data.p90_days)),
    ]


def build_report_pdf(data: ReportPrintData) -> bytes:
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"Laporan Pengaduan — {_CATEGORY_TITLES[data.category]}",
    )
    styles = _styles()
    story = []

    story.append(Paragraph("Laporan Pengaduan", styles["title"]))
    story.append(Paragraph(_CATEGORY_TITLES[data.category], styles["heading"]))

    meta_bits = [f"Periode: {data.period_label}"]
    if data.branch_label:
        meta_bits.append(f"Cabang: {data.branch_label}")
    meta_bits.append(f"Dicetak: {data.generated_at.strftime('%d %B %Y, %H:%M')} WIB")
    story.append(Paragraph(" · ".join(meta_bits), styles["muted"]))
    story.append(Spacer(1, 10 * mm))

    if data.category == ReportPrintCategory.ALL:
        story.append(
            _headline_table(
                [
                    ("Total pengaduan dibuat", str(data.total_created)),
                    ("Diselesaikan", str(data.resolved)),
                    ("Dieskalasi ke Pusat", str(data.escalated)),
                ]
            )
        )
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph("Rincian per status", styles["heading"]))
        story.append(Spacer(1, 3 * mm))
        story.append(_status_table(data.by_status))
    elif data.category == ReportPrintCategory.CREATED:
        story.append(_headline_table([("Total pengaduan dibuat", str(data.total_created))]))
        if data.by_status:
            story.append(Spacer(1, 8 * mm))
            story.append(Paragraph("Status saat ini", styles["heading"]))
            story.append(Spacer(1, 3 * mm))
            story.append(_status_table(data.by_status))
    elif data.category == ReportPrintCategory.RESOLVED:
        story.append(_headline_table([("Total pengaduan diselesaikan", str(data.resolved))]))
        if data.cycle_time is not None and data.cycle_time.closed_cases > 0:
            story.append(Spacer(1, 8 * mm))
            story.append(Paragraph("Waktu penyelesaian", styles["heading"]))
            story.append(Spacer(1, 3 * mm))
            story.append(_headline_table(_cycle_time_rows(data.cycle_time)))
    elif data.category == ReportPrintCategory.ESCALATED:
        story.append(_headline_table([("Total pengaduan dieskalasi ke Pusat", str(data.escalated))]))
    else:  # OTHER — no predicate defined yet
        story.append(
            Paragraph(
                "Kategori ini menunggu definisi status baru dan belum memiliki data. "
                "Laporan akan terisi begitu status tersebut ditambahkan ke domain pengaduan.",
                styles["body"],
            )
        )

    doc.build(story)
    return buffer.getvalue()

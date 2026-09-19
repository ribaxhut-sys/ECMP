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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.modules.reports.pdf_copy import (
    category_title,
    copy_for,
    normalize_report_lang,
)
from app.modules.reports.schemas import (
    AggregateComplaintStatus,
    CycleTimeBucket,
    CycleTimeData,
    ReportPrintCategory,
    StatusCount,
    UserActivityCount,
)

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_UNIT_PREFIX = re.compile(r"^(?:UPPPD|UP3D)[\s.\-]+", re.IGNORECASE)
REPORT_PDF_AGENCY = "Unit Pelayanan Pemungutan Pajak Daerah"

# Match frontend tokens: --ecmp-color-primary / --ecmp-color-text-primary.
_INK = colors.HexColor("#0f172a")
_MUTED = colors.HexColor("#64748b")
_TEAL = colors.HexColor("#0f766e")
_TEAL_LINE = colors.HexColor("#99f6e4")
_KPI_BG = colors.HexColor("#f0fdfa")
_HEAD_BG = colors.HexColor("#0f766e")
_HEAD_FG = colors.white
_CONTENT_WIDTH = 170 * mm
_PDF_USER_ROWS = 15


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
    lang: str = "id"
    has_comparison: bool = False
    previous_total_created: int = 0
    previous_resolved: int = 0
    previous_escalated: int = 0
    previous_in_progress_at_branch: int = 0
    user_activity: list[UserActivityCount] = field(default_factory=list)


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle(
            "kicker",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
            textColor=_TEAL,
            spaceAfter=1,
        ),
        "agency": ParagraphStyle(
            "agency",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            alignment=TA_LEFT,
            textColor=_INK,
        ),
        "masthead": ParagraphStyle(
            "masthead",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=_MUTED,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=_INK,
            spaceBefore=6,
            spaceAfter=1,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=_TEAL,
            spaceAfter=4,
        ),
        "heading": ParagraphStyle(
            "heading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=_TEAL,
            spaceBefore=12,
            spaceAfter=2,
        ),
        "briefing": ParagraphStyle(
            "briefing",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=_INK,
            spaceAfter=4,
        ),
        "kpiValue": ParagraphStyle(
            "kpiValue",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            alignment=TA_CENTER,
            textColor=_INK,
        ),
        "kpiLabel": ParagraphStyle(
            "kpiLabel",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_CENTER,
            textColor=_MUTED,
        ),
        "th": ParagraphStyle(
            "th",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=_HEAD_FG,
        ),
        "thValue": ParagraphStyle(
            "thValue",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
            textColor=_HEAD_FG,
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
        "cell": ParagraphStyle(
            "cell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=_INK,
        ),
        "cellNum": ParagraphStyle(
            "cellNum",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
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


class _UpppdMark(Flowable):
    """Typographic letterhead lockup — not a government seal or coat of arms."""

    SIZE = 16 * mm

    def wrap(self, *_args: object) -> tuple[float, float]:
        return (self.SIZE, self.SIZE)

    def draw(self) -> None:
        canvas = self.canv
        size = self.SIZE
        canvas.setFillColor(_TEAL)
        canvas.roundRect(0, 0, size, size, 2 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawCentredString(size / 2, size / 2 - 2.4, "UPPPD")


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
    lang: str | None = "id",
) -> str:
    """Inclusive calendar window in Asia/Jakarta, or unbounded."""
    copy = copy_for(lang)
    if date_from is None and date_to is None:
        return copy["unbounded"]
    start = format_report_date(date_from) if date_from is not None else "..."
    end = format_report_date(date_to) if date_to is not None else "..."
    return f"{start} - {end}"


def format_unit_label(branch_label: str | None, lang: str | None = "id") -> str:
    """Letterhead / identitas unit. Unscoped report = semua unit."""
    raw = (branch_label or "").strip()
    if not raw:
        return copy_for(lang)["all_units"]
    stripped = _UNIT_PREFIX.sub("", raw).strip()
    return stripped or raw


def format_count(
    value: int, unit: str = "pengaduan", lang: str | None = "id"
) -> str:
    copy = copy_for(lang)
    label = {
        "pengaduan": copy["unit_complaint"],
        "kasus": copy["unit_case"],
        "hari": copy["unit_day"],
    }.get(unit, unit)
    return f"{value} {label}"


def format_days(value: float | None, lang: str | None = "id") -> str:
    if value is None:
        return "-"
    return f"{value:.1f} {copy_for(lang)['unit_day']}"


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


def _section(title: str, styles: dict[str, ParagraphStyle]) -> list[object]:
    return [
        Paragraph(title, styles["heading"]),
        HRFlowable(
            width="100%",
            thickness=1.1,
            color=_TEAL,
            spaceBefore=0,
            spaceAfter=6,
        ),
    ]


def _kpi_strip(
    items: Sequence[tuple[str, str]], styles: dict[str, ParagraphStyle]
) -> Table:
    count = max(len(items), 1)
    col = _CONTENT_WIDTH / count
    value_row = [Paragraph(value, styles["kpiValue"]) for _, value in items]
    label_row = [Paragraph(label, styles["kpiLabel"]) for label, _ in items]
    table = Table([value_row, label_row], colWidths=[col] * count)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _KPI_BG),
                ("BOX", (0, 0), (-1, -1), 0.8, _TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, _TEAL_LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _kv_table(rows: Sequence[tuple[str, str]], styles: dict[str, ParagraphStyle]) -> Table:
    data = [
        [Paragraph(label, styles["label"]), Paragraph(value, styles["value"])]
        for label, value in rows
    ]
    table = Table(data, colWidths=[95 * mm, 75 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _KPI_BG),
                ("BOX", (0, 0), (-1, -1), 0.6, _TEAL),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -2), 0.3, _TEAL_LINE),
            ]
        )
    )
    return table


def _letterhead(
    unit: str, copy: dict[str, str], styles: dict[str, ParagraphStyle]
) -> Table:
    identity = Table(
        [
            [Paragraph(copy["internal"], styles["kicker"])],
            [Paragraph(REPORT_PDF_AGENCY, styles["agency"])],
            [Paragraph(unit, styles["masthead"])],
        ],
        colWidths=[150 * mm],
    )
    identity.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    table = Table([[_UpppdMark(), identity]], colWidths=[20 * mm, 150 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 4),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _signed(delta: int) -> str:
    return f"+{delta}" if delta > 0 else str(delta)


def _comparison_line(data: ReportPrintData, copy: dict[str, str]) -> str | None:
    if not data.has_comparison:
        return None
    if data.category == ReportPrintCategory.ALL:
        parts = [
            f"{copy['kpi_created']} {_signed(data.total_created - data.previous_total_created)}",
            f"{copy['kpi_resolved']} {_signed(data.resolved - data.previous_resolved)}",
            f"{copy['kpi_escalated']} {_signed(data.escalated - data.previous_escalated)}",
            (
                f"{copy['kpi_in_progress']} "
                f"{_signed(data.in_progress_at_branch - data.previous_in_progress_at_branch)}"
            ),
        ]
    elif data.category == ReportPrintCategory.CREATED:
        parts = [
            f"{copy['kpi_created']} {_signed(data.total_created - data.previous_total_created)}"
        ]
    elif data.category == ReportPrintCategory.RESOLVED:
        parts = [
            f"{copy['kpi_resolved']} {_signed(data.resolved - data.previous_resolved)}"
        ]
    elif data.category == ReportPrintCategory.ESCALATED:
        parts = [
            f"{copy['kpi_escalated']} {_signed(data.escalated - data.previous_escalated)}"
        ]
    else:
        return None
    return f"{copy['vs_previous']}: {' · '.join(parts)}"


def _briefing_line(data: ReportPrintData, copy: dict[str, str]) -> str:
    if data.total_created <= 0 and data.resolved <= 0:
        return copy["briefing_empty"]
    text = copy["briefing"].format(
        closed=data.resolved,
        total=data.total_created,
        open=data.in_progress_at_branch,
    )
    if data.escalated > 0:
        text += copy["briefing_escalated"].format(escalated=data.escalated)
    return text


def _status_table(
    rows: list[StatusCount],
    styles: dict[str, ParagraphStyle],
    copy: dict[str, str],
    lang: str,
) -> Table:
    status_labels = {
        "IN_PROGRESS": copy["status_in_progress"],
        "CLOSED": copy["status_closed"],
    }
    header = [
        Paragraph(copy["status"], styles["th"]),
        Paragraph(copy["count"], styles["thValue"]),
    ]
    body = [
        [
            Paragraph(
                status_labels.get(row.status.value, row.status.value),
                styles["label"],
            ),
            Paragraph(format_count(row.count, lang=lang), styles["value"]),
        ]
        for row in printable_status_rows(rows)
    ]
    table = Table([header, *body], colWidths=[95 * mm, 75 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _HEAD_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), _HEAD_FG),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.6, _TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, _TEAL_LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _KPI_BG]),
            ]
        )
    )
    return table


def _cycle_time_rows(
    data: CycleTimeData, copy: dict[str, str], lang: str
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        (copy["cycle_closed"], format_count(data.closed_cases, "kasus", lang)),
        (copy["cycle_average"], format_days(data.average_days, lang)),
        (copy["cycle_median"], format_days(data.median_days, lang)),
        (copy["cycle_p90"], format_days(data.p90_days, lang)),
        (copy["cycle_fastest"], format_days(data.fastest_days, lang)),
        (copy["cycle_slowest"], format_days(data.slowest_days, lang)),
    ]
    for bucket in data.buckets:
        rows.append(_bucket_row(bucket, data.closed_cases, copy, lang))
    return rows


def _bucket_row(
    bucket: CycleTimeBucket,
    closed_cases: int,
    copy: dict[str, str],
    lang: str,
) -> tuple[str, str]:
    labels = {
        "sameDay": copy["band_same_day"],
        "upTo3Days": copy["band_up_to_3"],
        "upTo7Days": copy["band_up_to_7"],
        "over7Days": copy["band_over_7"],
    }
    label = labels.get(bucket.key, bucket.key)
    if closed_cases <= 0:
        return (label, format_count(bucket.count, "kasus", lang))
    share = round((bucket.count / closed_cases) * 100)
    return (label, copy["cases_share"].format(count=bucket.count, share=share))


def _footer(stamp: str, copy: dict[str, str]):
    def _draw(canvas, _doc) -> None:  # noqa: ANN001
        canvas.saveState()
        canvas.setStrokeColor(_TEAL)
        canvas.setLineWidth(1.1)
        canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_MUTED)
        canvas.drawString(
            20 * mm,
            10 * mm,
            f"INTERNAL  |  {copy['footer_title']}  |  {copy['downloaded']} {stamp}",
        )
        canvas.drawRightString(
            A4[0] - 20 * mm,
            10 * mm,
            f"{copy['page']} {_doc.page}",
        )
        canvas.restoreState()

    return _draw


def build_report_pdf(data: ReportPrintData) -> bytes:
    import io

    lang = normalize_report_lang(data.lang)
    copy = copy_for(lang)
    stamp = format_report_stamp(data.generated_at)
    unit = format_unit_label(data.branch_label, lang)
    cat = category_title(data.category, lang)
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=16 * mm,
        bottomMargin=22 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"{copy['title']} — {cat}",
        author=REPORT_PDF_AGENCY,
    )
    story: list[object] = []

    story.append(_letterhead(unit, copy, styles))
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=2.2, color=_TEAL, spaceAfter=0.8))
    story.append(HRFlowable(width="100%", thickness=0.45, color=_INK, spaceAfter=4))
    story.append(Paragraph(copy["title"], styles["title"]))
    story.append(Paragraph(cat, styles["subtitle"]))
    story.append(Spacer(1, 4 * mm))

    if data.category == ReportPrintCategory.ALL:
        story.append(Paragraph(_briefing_line(data, copy), styles["briefing"]))
        story.append(Spacer(1, 2 * mm))

    story.extend(_section(copy["identity"], styles))
    story.append(
        _kv_table(
            [
                (copy["category"], cat),
                (copy["period"], data.period_label),
                (
                    copy["date_range"],
                    format_period_window(data.date_from, data.date_to, lang),
                ),
                (copy["unit"], unit),
                (copy["downloaded"], stamp),
            ],
            styles,
        )
    )

    comparison = _comparison_line(data, copy)

    if data.category == ReportPrintCategory.ALL:
        story.extend(_section(copy["summary"], styles))
        story.append(
            _kpi_strip(
                [
                    (copy["kpi_created"], format_count(data.total_created, lang=lang)),
                    (copy["kpi_resolved"], format_count(data.resolved, lang=lang)),
                    (copy["kpi_escalated"], format_count(data.escalated, lang=lang)),
                    (
                        copy["kpi_in_progress"],
                        format_count(data.in_progress_at_branch, lang=lang),
                    ),
                ],
                styles,
            )
        )
        if comparison:
            story.append(Spacer(1, 2 * mm))
            story.append(Paragraph(comparison, styles["muted"]))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(copy["note_all"], styles["muted"]))
        _append_cycle_time(story, data.cycle_time, styles, copy, lang)
        _append_user_activity(story, data.user_activity, styles, copy)
    elif data.category == ReportPrintCategory.CREATED:
        story.extend(_section(copy["summary"], styles))
        story.append(
            _kpi_strip(
                [
                    (
                        copy["kpi_created_long"],
                        format_count(data.total_created, lang=lang),
                    )
                ],
                styles,
            )
        )
        if comparison:
            story.append(Spacer(1, 2 * mm))
            story.append(Paragraph(comparison, styles["muted"]))
        visible = printable_status_rows(data.by_status)
        if visible:
            story.extend(_section(copy["status_now"], styles))
            story.append(_status_table(data.by_status, styles, copy, lang))
    elif data.category == ReportPrintCategory.RESOLVED:
        story.extend(_section(copy["summary"], styles))
        story.append(
            _kpi_strip(
                [
                    (
                        copy["kpi_resolved_long"],
                        format_count(data.resolved, lang=lang),
                    )
                ],
                styles,
            )
        )
        if comparison:
            story.append(Spacer(1, 2 * mm))
            story.append(Paragraph(comparison, styles["muted"]))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(copy["note_resolved"], styles["muted"]))
        _append_cycle_time(story, data.cycle_time, styles, copy, lang)
    elif data.category == ReportPrintCategory.ESCALATED:
        story.extend(_section(copy["summary"], styles))
        story.append(
            _kpi_strip(
                [
                    (
                        copy["kpi_escalated_long"],
                        format_count(data.escalated, lang=lang),
                    )
                ],
                styles,
            )
        )
        if comparison:
            story.append(Spacer(1, 2 * mm))
            story.append(Paragraph(comparison, styles["muted"]))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(copy["note_escalated"], styles["muted"]))
    else:
        story.extend(_section(copy["summary"], styles))
        story.append(Paragraph(copy["note_other"], styles["body"]))

    footer = _footer(stamp, copy)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def _append_cycle_time(
    story: list[object],
    cycle_time: CycleTimeData | None,
    styles: dict[str, ParagraphStyle],
    copy: dict[str, str],
    lang: str,
) -> None:
    story.extend(_section(copy["cycle_time"], styles))
    if cycle_time is None or cycle_time.closed_cases <= 0:
        story.append(Paragraph(copy["cycle_empty"], styles["muted"]))
        return
    story.append(_kv_table(_cycle_time_rows(cycle_time, copy, lang), styles))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(copy["cycle_note"], styles["muted"]))


def _append_user_activity(
    story: list[object],
    rows: list[UserActivityCount],
    styles: dict[str, ParagraphStyle],
    copy: dict[str, str],
) -> None:
    story.extend(_section(copy["user_activity"], styles))
    if not rows:
        story.append(Paragraph(copy["user_activity_empty"], styles["muted"]))
        return
    visible = rows[:_PDF_USER_ROWS]
    story.append(_user_activity_table(visible, styles, copy))
    story.append(Spacer(1, 2 * mm))
    if len(rows) > _PDF_USER_ROWS:
        story.append(
            Paragraph(
                copy["user_activity_truncated"].format(
                    shown=_PDF_USER_ROWS, total=len(rows)
                ),
                styles["muted"],
            )
        )
    story.append(Paragraph(copy["user_activity_note"], styles["muted"]))


def _user_activity_table(
    rows: list[UserActivityCount],
    styles: dict[str, ParagraphStyle],
    copy: dict[str, str],
) -> Table:
    header = [
        Paragraph(copy["user_activity_name"], styles["th"]),
        Paragraph(copy["user_activity_unit"], styles["th"]),
        Paragraph(copy["user_activity_created"], styles["thValue"]),
        Paragraph(copy["user_activity_decided"], styles["thValue"]),
        Paragraph(copy["user_activity_closed"], styles["thValue"]),
        Paragraph(copy["user_activity_events"], styles["thValue"]),
    ]
    body = []
    for row in rows:
        unit = row.branch_name or "—"
        body.append(
            [
                Paragraph(row.display_name, styles["cell"]),
                Paragraph(unit, styles["cell"]),
                Paragraph(str(row.created_count), styles["cellNum"]),
                Paragraph(str(row.decided_count), styles["cellNum"]),
                Paragraph(str(row.closed_count), styles["cellNum"]),
                Paragraph(str(row.activity_count), styles["cellNum"]),
            ]
        )
    table = Table(
        [header, *body],
        colWidths=[48 * mm, 38 * mm, 21 * mm, 21 * mm, 21 * mm, 21 * mm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _HEAD_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), _HEAD_FG),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BOX", (0, 0), (-1, -1), 0.6, _TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, _TEAL_LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _KPI_BG]),
            ]
        )
    )
    return table


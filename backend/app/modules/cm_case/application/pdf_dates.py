"""Operator-facing dates for API-539 PDF: DD-MM-YYYY, and comma before the clock."""

from __future__ import annotations

import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

_OPERATOR_TZ = ZoneInfo("Asia/Jakarta")
_ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_CLOCK = re.compile(r"^(\d{1,2}):(\d{2})")
_ISO_IN_TEXT = re.compile(
    r"\b(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{1,2}):(\d{2})(?::\d{2})?)?\b"
)


def format_pdf_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"
    local = value.astimezone(_OPERATOR_TZ) if value.tzinfo else value
    return f"{local.strftime('%d-%m-%Y')}, {local.strftime('%H:%M')}"


def format_pdf_date_and_time(
    date_part: date | str | None,
    time_part: str | None = None,
) -> str:
    """Date only: DD-MM-YYYY. Date + clock: DD-MM-YYYY, HH:MM."""
    day = _date_to_dmy(date_part)
    clock = _normalize_clock(time_part)
    if day and clock:
        return f"{day}, {clock}"
    return day or clock or ""


def rewrite_iso_dates_in_text(text: str) -> str:
    """Turn ISO dates in prose into DD-MM-YYYY[, HH:MM]."""

    def repl(match: re.Match[str]) -> str:
        year, month, day = match.group(1), match.group(2), match.group(3)
        dmy = f"{day}-{month}-{year}"
        hour, minute = match.group(4), match.group(5)
        if hour is None:
            return dmy
        return f"{dmy}, {int(hour):02d}:{minute}"

    return _ISO_IN_TEXT.sub(repl, text or "")


def _date_to_dmy(value: date | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    text = str(value).strip()
    match = _ISO_DATE.match(text[:10] if len(text) >= 10 else text)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    return text


def _normalize_clock(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    match = _CLOCK.match(text)
    if match is None:
        return text
    return f"{int(match.group(1)):02d}:{match.group(2)}"

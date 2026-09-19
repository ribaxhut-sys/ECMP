"""Announcement reference numbers — ``PGM-YYMM-NNNN``.

Example: Aug 2026 seq 1 → ``PGM-2608-0001``.
Sequence width starts at 4 digits and grows past 9999 so create never fails.
Counter key is global per calendar month (Pusat-only manage; no unit suffix).
"""

from __future__ import annotations

from datetime import UTC, datetime

PREFIX = "PGM"


def counter_name(*, year: int, month: int) -> str:
    """Portable counter key — one sequence per calendar month."""
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")
    return f"an:{year:04d}{month:02d}"


def format_reference_number(*, year: int, month: int, sequence: int) -> str:
    """Format: ``PGM-YYMM-NNNN`` (NNNN grows past 4 digits after 9999)."""
    if sequence < 1:
        raise ValueError("sequence must be >= 1")
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")
    yymm = f"{year % 100:02d}{month:02d}"
    width = 4 if sequence <= 9999 else len(str(sequence))
    return f"{PREFIX}-{yymm}-{sequence:0{width}d}"


def next_reference_number(*, sequence: int, at: datetime | None = None) -> str:
    """Build the public number for an allocated sequence value."""
    when = at or datetime.now(UTC)
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return format_reference_number(
        year=when.year, month=when.month, sequence=sequence
    )

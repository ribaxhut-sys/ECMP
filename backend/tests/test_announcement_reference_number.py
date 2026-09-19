"""Unit tests for announcement reference numbers (PGM-YYMM-NNNN)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.announcement.reference_number import (
    counter_name,
    format_reference_number,
    next_reference_number,
)


def test_format_yymm_year_then_month() -> None:
    assert format_reference_number(year=2026, month=8, sequence=1) == "PGM-2608-0001"
    assert format_reference_number(year=2025, month=12, sequence=42) == "PGM-2512-0042"


def test_format_grows_past_9999() -> None:
    assert format_reference_number(year=2026, month=1, sequence=10000) == "PGM-2601-10000"


def test_counter_name_monthly() -> None:
    assert counter_name(year=2026, month=8) == "an:202608"


def test_next_reference_number_uses_at() -> None:
    at = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
    assert next_reference_number(sequence=3, at=at) == "PGM-2608-0003"


@pytest.mark.parametrize("sequence", [0, -1])
def test_format_rejects_non_positive_sequence(sequence: int) -> None:
    with pytest.raises(ValueError):
        format_reference_number(year=2026, month=8, sequence=sequence)

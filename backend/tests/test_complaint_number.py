"""Unit tests for Aggregate complaint number format B."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.cm_batch1.complaint_number import (
    counter_name,
    format_complaint_number,
    next_complaint_number,
    resolve_unit_code,
)


def test_resolve_tanah_abang_to_tab() -> None:
    assert resolve_unit_code("UPPPD-TANAH-ABANG") == "TAB"
    assert resolve_unit_code("upppd_tanah_abang") == "TAB"


def test_resolve_pusat_and_unknown() -> None:
    assert resolve_unit_code("PUSAT") == "PUS"
    assert resolve_unit_code(None) == "UNK"
    assert resolve_unit_code("") == "UNK"
    assert resolve_unit_code("TAB") == "TAB"


def test_counter_name_per_unit_month() -> None:
    assert counter_name("TAB", year=2026, month=8) == "cn:TAB:202608"
    assert counter_name("GAM", year=2026, month=8) == "cn:GAM:202608"
    assert counter_name("TAB", year=2026, month=9) == "cn:TAB:202609"


def test_format_b_padded_four_digits() -> None:
    assert (
        format_complaint_number("TAB", year=2026, month=8, sequence=42)
        == "TAB-2608-0042"
    )


def test_format_b_overflow_grows_width() -> None:
    assert (
        format_complaint_number("TAB", year=2026, month=8, sequence=10000)
        == "TAB-2608-10000"
    )
    assert (
        format_complaint_number("TAB", year=2026, month=8, sequence=100000)
        == "TAB-2608-100000"
    )


def test_next_complaint_number_uses_at() -> None:
    at = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
    assert (
        next_complaint_number(
            owning_unit_id="UPPPD-TANAH-ABANG", sequence=1, at=at
        )
        == "TAB-2608-0001"
    )


@pytest.mark.parametrize("seq", [0, -1])
def test_format_rejects_non_positive_sequence(seq: int) -> None:
    with pytest.raises(ValueError):
        format_complaint_number("TAB", year=2026, month=8, sequence=seq)

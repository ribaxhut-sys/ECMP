"""Vendored national-holiday calendars for HQ schedule import.

Do not fetch third-party APIs at request time — those hosts have already
gone dark. Add a new ``holidays_YYYY.json`` when the next SKB is published.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Literal

HolidayKind = Literal["LIBUR_NASIONAL", "CUTI_BERSAMA"]

_DATA_DIR = Path(__file__).resolve().parent / "data"
_KIND_VALUES = frozenset({"LIBUR_NASIONAL", "CUTI_BERSAMA"})


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    holiday_date: date
    label: str
    kind: HolidayKind
    default_selected: bool


@dataclass(frozen=True, slots=True)
class YearCatalog:
    year: int
    source: str
    source_name: str
    source_url: str | None
    last_updated: str | None
    notes: str | None
    entries: tuple[CatalogEntry, ...]


def available_years() -> list[int]:
    years: list[int] = []
    for path in sorted(_DATA_DIR.glob("holidays_*.json")):
        suffix = path.stem.removeprefix("holidays_")
        if suffix.isdigit():
            years.append(int(suffix))
    return years


@lru_cache(maxsize=8)
def load_year_catalog(year: int) -> YearCatalog | None:
    path = _DATA_DIR / f"holidays_{year}.json"
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries: list[CatalogEntry] = []
    for item in raw.get("entries") or []:
        kind = item.get("kind")
        if kind not in _KIND_VALUES:
            continue
        entries.append(
            CatalogEntry(
                holiday_date=date.fromisoformat(str(item["date"])),
                label=str(item["label"]).strip(),
                kind=kind,
                default_selected=bool(item.get("defaultSelected", True)),
            )
        )
    return YearCatalog(
        year=int(raw["year"]),
        source=str(raw.get("source") or f"skb-3-menteri-{year}"),
        source_name=str(raw.get("sourceName") or raw.get("source") or ""),
        source_url=raw.get("sourceUrl"),
        last_updated=raw.get("lastUpdated"),
        notes=raw.get("notes"),
        entries=tuple(entries),
    )


def catalog_by_date(year: int) -> dict[date, CatalogEntry]:
    catalog = load_year_catalog(year)
    if catalog is None:
        return {}
    return {entry.holiday_date: entry for entry in catalog.entries}

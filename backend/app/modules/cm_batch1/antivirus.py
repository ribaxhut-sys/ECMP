"""Antivirus extension point for FR-004 (stub only — no integration)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AntivirusResult:
    clean: bool
    engine: str
    detail: str | None = None


class AntivirusScanner(Protocol):
    def scan(
        self, data: bytes, *, mime_type: str, filename: str
    ) -> AntivirusResult: ...


class StubAntivirusScanner:
    """STUB_ONLY mode — always clean. Real engine plugs in here later."""

    def scan(
        self, data: bytes, *, mime_type: str, filename: str
    ) -> AntivirusResult:
        _ = data, mime_type, filename
        return AntivirusResult(clean=True, engine="stub", detail="antivirusMode=STUB_ONLY")

"""Indonesian labels for Pengaduan Internal PDF output.

Shared by the per-ticket snapshot (API-550) and the list report (API-553) so a
status never reads one way on the ticket and another way on the report.
"""

from __future__ import annotations

STATUS_LABEL = {
    "CREATED": "Dibuat",
    "ASSIGNED": "Ditugaskan",
    "IN_PROGRESS": "Dalam Penanganan",
    "RESOLVED": "Terselesaikan",
    "CLOSED": "Ditutup",
    "WITHDRAWN": "Dibatalkan",
}
CATEGORY_LABEL = {
    "PERFORMANCE": "Kinerja",
    "PROCESS_SOP": "Proses/SOP",
    "COORDINATION": "Koordinasi",
    "COMPLIANCE": "Kepatuhan",
    "SYSTEM": "Sistem",
    "OPERATIONAL": "Operasional",
    "OTHER": "Lainnya",
}
PRIORITY_LABEL = {
    "LOW": "Rendah",
    "MEDIUM": "Sedang",
    "HIGH": "Tinggi",
    "CRITICAL": "Kritis",
}


def label(table: dict[str, str], raw: str | None) -> str:
    """Localized label, or the raw code when it is not one we know."""
    key = (raw or "").strip()
    if not key:
        return "-"
    return table.get(key.upper(), key)

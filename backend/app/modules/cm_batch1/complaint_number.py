"""Aggregate complaint numbers — format B: ``UNIT-YYMM-NNNN``.

Example: Tanah Abang Aug 2026 seq 42 → ``TAB-2608-0042``.
Sequence width starts at 4 digits and grows automatically past 9999
(``TAB-2608-10000``) so create never fails on overflow.
"""

from __future__ import annotations

from datetime import UTC, datetime

# Branch.code / owning_unit_id → fixed 3-letter unit key for human-readable numbers.
_UNIT_CODES: dict[str, str] = {
    "PUSAT": "PUS",
    "HO": "PUS",
    "HEAD_OFFICE": "PUS",
    "HEAD-OFFICE": "PUS",
    "UPPPD-TANAH-ABANG": "TAB",
    "UPPPD-GAMBIR": "GAM",
    "UPPPD-SAWAH-BESAR": "SWB",
    "UPPPD-KEMAYORAN": "KMY",
    "UPPPD-SENEN": "SEN",
    "UPPPD-CEMPAKA-PUTIH": "CMP",
    "UPPPD-MENTENG": "MTG",
    "UPPPD-JOHAR-BARU": "JHB",
    "UPPPD-PENJARINGAN": "PNJ",
    "UPPPD-PADEMANGAN": "PDM",
    "UPPPD-TANJUNG-PRIOK": "TJP",
    "UPPPD-KOJA": "KOJ",
    "UPPPD-KELAPA-GADING": "KLG",
    "UPPPD-CILINCING": "CLC",
    "UPPPD-GROGOL-PETAMBURAN": "GRP",
    "UPPPD-TAMAN-SARI": "TMS",
    "UPPPD-TAMBORA": "TMB",
    "UPPPD-KEBON-JERUK": "KBJ",
    "UPPPD-PALMERAH": "PLM",
    "UPPPD-KEMBANGAN": "KMB",
    "UPPPD-CENGKARENG": "CGK",
    "UPPPD-KALIDERES": "KLD",
    "UPPPD-KEBAYORAN-BARU": "KBB",
    "UPPPD-KEBAYORAN-LAMA": "KBL",
    "UPPPD-PESANGGRAHAN": "PSG",
    "UPPPD-CILANDAK": "CLD",
    "UPPPD-PASAR-MINGGU": "PSM",
    "UPPPD-JAGAKARSA": "JGK",
    "UPPPD-MAMPANG-PRAPATAN": "MPP",
    "UPPPD-PANCORAN": "PNC",
    "UPPPD-TEBET": "TBT",
    "UPPPD-SETIABUDI": "STB",
    "UPPPD-MATRAMAN": "MTR",
    "UPPPD-PULOGADUNG": "PLG",
    "UPPPD-JATINEGARA": "JTG",
    "UPPPD-DUREN-SAWIT": "DRS",
    "UPPPD-KRAMAT-JATI": "KRJ",
    "UPPPD-MAKASAR": "MKS",
    "UPPPD-PASAR-REBO": "PSR",
    "UPPPD-CIRACAS": "CRC",
    "UPPPD-CIPAYUNG": "CPY",
    "UPPPD-CAKUNG": "CKG",
}


def resolve_unit_code(owning_unit_id: str | None) -> str:
    """Map owning unit / Branch.code to a stable 3-letter unit code."""
    raw = (owning_unit_id or "").strip().upper().replace("_", "-")
    if not raw:
        return "UNK"
    if raw in _UNIT_CODES:
        return _UNIT_CODES[raw]
    # Already a short code (lab / manual).
    if len(raw) == 3 and raw.isalpha():
        return raw
    # Fallback: letters only from slug, pad/trim to 3.
    letters = "".join(ch for ch in raw if ch.isalpha())
    if len(letters) >= 3:
        return letters[:3].upper()
    return (letters.upper() + "XXX")[:3]


def counter_name(unit_code: str, *, year: int, month: int) -> str:
    """Portable counter key — one sequence per unit per calendar month."""
    return f"cn:{unit_code.upper()}:{year:04d}{month:02d}"


def format_complaint_number(
    unit_code: str,
    *,
    year: int,
    month: int,
    sequence: int,
) -> str:
    """Format B: ``UNIT-YYMM-NNNN`` (NNNN grows past 4 digits after 9999)."""
    if sequence < 1:
        raise ValueError("sequence must be >= 1")
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")
    unit = resolve_unit_code(unit_code)
    yymm = f"{year % 100:02d}{month:02d}"
    width = 4 if sequence <= 9999 else len(str(sequence))
    return f"{unit}-{yymm}-{sequence:0{width}d}"


def next_complaint_number(
    *,
    owning_unit_id: str | None,
    sequence: int,
    at: datetime | None = None,
) -> str:
    """Build the next public number for an allocated sequence value."""
    when = at or datetime.now(UTC)
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    unit = resolve_unit_code(owning_unit_id)
    return format_complaint_number(
        unit, year=when.year, month=when.month, sequence=sequence
    )

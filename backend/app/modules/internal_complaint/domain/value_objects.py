"""Value objects for Pengaduan Internal (domain terpisah dari F4)."""

from __future__ import annotations

import re
from enum import StrEnum


class InternalStatus(StrEnum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ResolveAction(StrEnum):
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class ResolutionProposalStatus(StrEnum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class AcceptanceParty(StrEnum):
    OWNER = "OWNER"
    HANDLING_UNIT = "HANDLING_UNIT"


class AcceptanceDecision(StrEnum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class TransferRequestStatus(StrEnum):
    """Agent-family transfer request gate — create stays local until decided."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class HistoryEventType(StrEnum):
    CREATED = "CREATED"
    TRANSFER = "TRANSFER"
    TRANSFER_REQUESTED = "TRANSFER_REQUESTED"
    TRANSFER_REQUEST_APPROVED = "TRANSFER_REQUEST_APPROVED"
    TRANSFER_REQUEST_REJECTED = "TRANSFER_REQUEST_REJECTED"
    RECEIVED = "RECEIVED"
    REVIEW = "REVIEW"
    RESOLUTION = "RESOLUTION"
    HANDLING_UNIT_ACCEPT = "HANDLING_UNIT_ACCEPT"
    HANDLING_UNIT_REJECT = "HANDLING_UNIT_REJECT"
    OWNER_ACCEPT = "OWNER_ACCEPT"
    OWNER_REJECT = "OWNER_REJECT"
    CLOSED = "CLOSED"


# Legacy lab format ``PI-YYYY-NNNNNN`` (global per-year counter — kept
# readable for rows already created before the unit-scoped format existed)
# and the current format ``PI-{UNIT}-{YYMM}-{NNN...}`` (per-unit-per-month,
# width grows past 999). Old numbers are never remapped.
_LEGACY_NUMBER_RE = re.compile(r"^PI-(\d{4})-(\d{6})$")
_UNIT_NUMBER_RE = re.compile(r"^PI-([A-Z]{3})-(\d{4})-(\d{3,})$")


class InternalComplaintNumber:
    """Nomor Pengaduan Internal — ``PI-{UNIT}-{YYMM}-{NNN}`` (current) or legacy."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        text = (value or "").strip().upper()
        if not (_LEGACY_NUMBER_RE.match(text) or _UNIT_NUMBER_RE.match(text)):
            raise ValueError(f"Invalid Internal Complaint Number format: {value!r}")
        self._value = text

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def format(cls, year: int, seq: int) -> InternalComplaintNumber:
        """Legacy per-year format — retained only for rows already on disk."""
        if seq < 1 or seq > 999_999:
            raise ValueError("Internal Complaint Number sequence out of range")
        return cls(f"PI-{year:04d}-{seq:06d}")

    @classmethod
    def format_unit(
        cls, unit_code: str, *, year: int, month: int, sequence: int
    ) -> InternalComplaintNumber:
        """Current format ``PI-{UNIT}-{YYMM}-{NNN}`` — width grows past 999."""
        if sequence < 1:
            raise ValueError("Internal Complaint Number sequence out of range")
        if not (1 <= month <= 12):
            raise ValueError("month must be 1..12")
        unit = (unit_code or "").strip().upper()
        if len(unit) != 3 or not unit.isalpha():
            raise ValueError(
                f"Invalid unit code for Internal Complaint Number: {unit_code!r}"
            )
        yymm = f"{year % 100:02d}{month:02d}"
        width = 3 if sequence <= 999 else len(str(sequence))
        return cls(f"PI-{unit}-{yymm}-{sequence:0{width}d}")

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InternalComplaintNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

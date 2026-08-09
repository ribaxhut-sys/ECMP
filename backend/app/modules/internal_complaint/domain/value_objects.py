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


class HistoryEventType(StrEnum):
    CREATED = "CREATED"
    TRANSFER = "TRANSFER"
    RECEIVED = "RECEIVED"
    REVIEW = "REVIEW"
    RESOLUTION = "RESOLUTION"
    HANDLING_UNIT_ACCEPT = "HANDLING_UNIT_ACCEPT"
    HANDLING_UNIT_REJECT = "HANDLING_UNIT_REJECT"
    OWNER_ACCEPT = "OWNER_ACCEPT"
    OWNER_REJECT = "OWNER_REJECT"
    CLOSED = "CLOSED"


_NUMBER_RE = re.compile(r"^PI-(\d{4})-(\d{6})$")


class InternalComplaintNumber:
    """Nomor Pengaduan Internal ``PI-YYYY-NNNNNN``."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        text = (value or "").strip()
        if not _NUMBER_RE.match(text):
            raise ValueError(f"Invalid Internal Complaint Number format: {value!r}")
        self._value = text

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def format(cls, year: int, seq: int) -> InternalComplaintNumber:
        if seq < 1 or seq > 999_999:
            raise ValueError("Internal Complaint Number sequence out of range")
        return cls(f"PI-{year:04d}-{seq:06d}")

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InternalComplaintNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

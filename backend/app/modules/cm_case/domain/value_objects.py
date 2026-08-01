"""Value objects for CAP-008 Mode A Case Aggregate."""

from __future__ import annotations

import re
from enum import StrEnum


class CaseStatus(StrEnum):
    """Mode A Delivery exposed statuses (BQ-009). PENDING/ESCALATED not exposed."""

    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class CancelReason(StrEnum):
    """Mode A cancel reasons (BQ-014)."""

    DUPLICATE = "DUPLICATE"
    WRONG_INPUT = "WRONG_INPUT"
    CUSTOMER_CANCELLATION = "CUSTOMER_CANCELLATION"


class ResolveAction(StrEnum):
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class ResolutionProposalStatus(StrEnum):
    """Resolution lifecycle — not a Case status (BR-008)."""

    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


_CASE_NUMBER_RE = re.compile(r"^CASE-(\d{4})-(\d{6})$")


class CaseNumber:
    """Case Number ``CASE-YYYY-NNNNNN`` (BQ-004) — independent of Complaint Number."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        text = (value or "").strip()
        if not _CASE_NUMBER_RE.match(text):
            raise ValueError(f"Invalid Case Number format: {value!r}")
        self._value = text

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def format(cls, year: int, seq: int) -> CaseNumber:
        if seq < 1 or seq > 999_999:
            raise ValueError("Case Number sequence out of range")
        return cls(f"CASE-{year:04d}-{seq:06d}")

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CaseNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


MAX_CASES_PER_COMPLAINT = 5  # Mode A default (BQ-003)
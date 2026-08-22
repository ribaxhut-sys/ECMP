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


class AcceptanceParty(StrEnum):
    """F4 closure requires agreement from both parties.

    OWNER = unit that created the Complaint (immutable for its lifetime).
    HANDLING_UNIT = unit currently responsible for working the Case
    (``CaseAggregate.owning_unit_id`` — mutated on transfer/ASSIGNED).
    """

    OWNER = "OWNER"
    HANDLING_UNIT = "HANDLING_UNIT"


class AcceptanceDecision(StrEnum):
    """A party's decision on a proposed resolution (F4 closure rule)."""

    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


_CASE_NUMBER_RE = re.compile(r"^CASE-(\d{4})-(\d{4,6})$")


class CaseNumber:
    """Case Number ``CASE-YYYY-NNNN`` (BQ-004) — independent of Complaint Number.

    Sequence is four digits (e.g. ``CASE-2026-0002``). Six-digit legacy values
    such as ``CASE-2026-000002`` are accepted and canonicalized on parse.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        text = (value or "").strip()
        match = _CASE_NUMBER_RE.match(text)
        if not match:
            raise ValueError(f"Invalid Case Number format: {value!r}")
        seq = int(match.group(2))
        if seq < 1 or seq > 9999:
            raise ValueError("Case Number sequence out of range")
        self._value = f"CASE-{match.group(1)}-{seq:04d}"

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def format(cls, year: int, seq: int) -> CaseNumber:
        if seq < 1 or seq > 9999:
            raise ValueError("Case Number sequence out of range")
        return cls(f"CASE-{year:04d}-{seq:04d}")

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CaseNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


MAX_CASES_PER_COMPLAINT = 5  # Mode A default (BQ-003)

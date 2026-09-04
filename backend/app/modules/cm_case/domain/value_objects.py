"""Value objects for CAP-008 Mode A Case Aggregate."""

from __future__ import annotations

import re
from enum import StrEnum

from app.modules.cm_batch1.complaint_number import format_case_number


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


_CASE_NUMBER_RE = re.compile(r"^([A-Z]{3})-(\d{4})-(\d{4,})$")


class CaseNumber:
    """Case Number ``UNIT-YYMM-NNNN`` (BQ-004) — independent of Complaint Number.

    Example: Tanah Abang Aug 2026 seq 1 → ``TAB-2608-0001``. Complaint numbers
    use the same unit/month shape with a glued ``CM`` prefix (``CMTAB-…``)
    and are rejected here.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        text = (value or "").strip().upper()
        match = _CASE_NUMBER_RE.fullmatch(text)
        if not match:
            raise ValueError(f"Invalid Case Number format: {value!r}")
        yymm = match.group(2)
        month = int(yymm[2:])
        if month < 1 or month > 12:
            raise ValueError(f"Invalid Case Number format: {value!r}")
        seq = int(match.group(3))
        year = 2000 + int(yymm[:2])
        self._value = format_case_number(
            match.group(1), year=year, month=month, sequence=seq
        )

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def format(
        cls,
        unit_code: str,
        *,
        year: int,
        month: int,
        sequence: int,
    ) -> CaseNumber:
        return cls(
            format_case_number(unit_code, year=year, month=month, sequence=sequence)
        )

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CaseNumber):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


MAX_CASES_PER_COMPLAINT = 5  # Mode A default (BQ-003)

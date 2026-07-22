"""Active Workflow Config baseline (DOM-ECMF-003 / ADR-003 configuration-first).

Transitions are data, not if/else chains. Administration will own persistence later
(ADR-008); Sprint-02B loads the FRD-002 in-scope subset as an immutable config.
CLOSED→REOPENED is excluded (FRD-002 §8: reopen flow out of scope; DEC-006 U-1/U-4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Full CaseStatus enum (DOM-ECMF-003 SoT) — values the API may express.
CASE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "REGISTERED",
        "ASSIGNED",
        "IN_PROGRESS",
        "PENDING_REVIEW",
        "CLOSED",
        "REOPENED",
    }
)


@dataclass(frozen=True, slots=True)
class TransitionRule:
    from_status: str
    to_status: str
    # Domain event ids emitted in addition to EVT-003 (always emitted on success).
    extra_events: tuple[str, ...] = ()


# Sprint-02B configured subset (FRD-002 in-scope path).
_BASELINE: Final[tuple[TransitionRule, ...]] = (
    TransitionRule("REGISTERED", "ASSIGNED", extra_events=("EVT-002",)),
    TransitionRule("ASSIGNED", "IN_PROGRESS"),
    TransitionRule("IN_PROGRESS", "PENDING_REVIEW"),
    TransitionRule("PENDING_REVIEW", "CLOSED", extra_events=("EVT-005",)),
    TransitionRule("PENDING_REVIEW", "IN_PROGRESS"),
    # REOPENED→ASSIGNED remains in assignable set for contract parity; unreachable
    # until reopen ships. Kept so assign API stays aligned with case-service.v1.yaml guards.
    TransitionRule("REOPENED", "ASSIGNED", extra_events=("EVT-002",)),
    TransitionRule("REOPENED", "IN_PROGRESS"),
)


def active_transitions() -> frozenset[tuple[str, str]]:
    return frozenset((r.from_status, r.to_status) for r in _BASELINE)


def transition_rule(from_status: str, to_status: str) -> TransitionRule | None:
    for rule in _BASELINE:
        if rule.from_status == from_status and rule.to_status == to_status:
            return rule
    return None


def is_allowed_transition(from_status: str, to_status: str) -> bool:
    return (from_status, to_status) in active_transitions()


def assignable_statuses() -> frozenset[str]:
    """Statuses that have a configured transition to ASSIGNED (API-003 INVALID_STATE)."""
    return frozenset(src for src, dst in active_transitions() if dst == "ASSIGNED")


def requires_resolution_code(to_status: str) -> bool:
    """BR-ECMF-06: resolutionCode mandatory for →CLOSED."""
    return to_status == "CLOSED"


def requires_reason(from_status: str, to_status: str, *, is_admin_override: bool) -> bool:
    """reason mandatory for admin override (BR-ECMF-03) and CLOSED→REOPENED (BR-ECMF-07)."""
    if is_admin_override:
        return True
    return from_status == "CLOSED" and to_status == "REOPENED"

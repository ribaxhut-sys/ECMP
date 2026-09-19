"""Who is holding a Case right now — the work-list handler column.

Escalating to Pusat clears ``handling_claimed_by`` on purpose (Pusat must
claim), which left every Case on the HQ path with an empty handler column.
The officer is not lost though: accepting or scheduling at Pusat stamps the
actor on the parent Complaint. This resolves the first source that applies,
so the list always shows the person the Case is sitting with.

Column-only sources — no timeline replay, no extra per-row query.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.cm_case.domain.repositories import ParentHandoff

BRANCH = "BRANCH"
PUSAT = "PUSAT"

#: Parent dispositions that mean "this Complaint is at/through Pusat".
_HQ_DISPOSITIONS = frozenset({"ESCALATE_APPROVED", "HQ_SCHEDULED", "HQ_CLOSED"})


__all__ = ["BRANCH", "PUSAT", "CurrentHandler", "ParentHandoff", "resolve_current_handler"]


@dataclass(frozen=True)
class CurrentHandler:
    actor_id: str | None = None
    scope: str = BRANCH


def _clean(value: str | None) -> str:
    return (value or "").strip()


def resolve_current_handler(
    *,
    handling_claimed_by: str | None,
    created_by: str | None,
    escalated_to_pusat: bool = False,
    parent: ParentHandoff | None = None,
) -> CurrentHandler:
    """Resolve the current handler, most specific source first.

    1. active handling claim (branch officer, or Pusat once it claims);
    2. Pusat officer who set the arrival/destination, else who accepted;
    3. branch officer who proposed the escalation (awaiting approval);
    4. the Case creator.
    """
    claimed = _clean(handling_claimed_by)
    if claimed:
        return CurrentHandler(claimed, PUSAT if escalated_to_pusat else BRANCH)

    ref = parent or ParentHandoff()
    disposition = _clean(ref.intake_disposition).upper()

    if escalated_to_pusat or disposition in _HQ_DISPOSITIONS:
        for candidate in (ref.hq_destination_set_by, ref.hq_accepted_by):
            actor = _clean(candidate)
            if actor:
                return CurrentHandler(actor, PUSAT)

    if disposition == "ESCALATE_PENDING_APPROVAL":
        proposer = _clean(ref.proposed_by)
        if proposer:
            return CurrentHandler(proposer, BRANCH)

    return CurrentHandler(_clean(created_by) or None, BRANCH)

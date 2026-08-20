"""Canonical read predicates over ``cm_batch1_complaints`` (DEC-025 §3.3).

One definition per predicate so list filter, dashboard summary, KPI, Users
directory counter, recent-activity provider, and report cannot drift apart.
Before this module ``escalated`` was 2 dispositions on the dashboard, 6 on the
list filter, 4 on the Users directory counter, and 1 (mismapped) in the
report donut.

``status`` is the Aggregate lifecycle SoT; ``intake_disposition`` is the intake
path label and never overrides it.

Also here: ``cm_batch1_activity_provider.py``'s aggregate-KPI donut is a
different, mutually-exclusive partition (``waiting_assignment`` /
``escalate_pending`` / ``escalate_approved`` / ``escalate_scheduled`` +
``in_progress`` + ``closed`` sum to total). ``escalate_scheduled`` is the
HQ_SCHEDULED slice: without it the donut reported "0 escalated" while every
row sat on the escalation path, contradicting ``ESCALATION_ACTIVE`` here.
"""

from __future__ import annotations

#: Aggregate lifecycle exposed by DEC-025 §3.3.
AGGREGATE_STATUSES: tuple[str, ...] = ("REGISTERED", "IN_PROGRESS", "CLOSED")

CLOSED_STATUS = "CLOSED"

#: Escalation approved and an HQ visit is on the calendar.
HQ_SCHEDULED = "HQ_SCHEDULED"

#: HQ visit handled; Aggregate CLOSED. Not on the live escalation path.
HQ_CLOSED = "HQ_CLOSED"

#: Still travelling the escalation path — the KPI/dashboard "escalated" count.
ESCALATION_ACTIVE: tuple[str, ...] = (
    "ESCALATE_PENDING_APPROVAL",
    "ESCALATE_APPROVED",
    HQ_SCHEDULED,
)

#: Ever entered escalation — list drill-down pseudo-value ``ESCALATED``.
ESCALATION_FAMILY: tuple[str, ...] = (
    "ESCALATE_PENDING_APPROVAL",
    "ESCALATE_APPROVED",
    "ESCALATE_REJECTED",
    "ESCALATE_CANCELLED",
    "RETURNED_TO_BRANCH",
    HQ_SCHEDULED,
)


def is_closed(status: str | None) -> bool:
    return (status or "").strip().upper() == CLOSED_STATUS


def is_open(status: str | None) -> bool:
    """Open = not CLOSED (DEC-025 M-025-1).

    An out-of-set stored value counts as open too — ``_aggregate_status``
    (cm_batch1/service.py) exposes it as REGISTERED rather than hiding it, so
    ``open + closed == total`` holds for every row.

    Intake HQ actions (approve / cancel / HQ accept) use this predicate so a
    bound Case (``IN_PROGRESS``) does not block Cabang↔Pusat routing.
    """
    return not is_closed(status)


def is_escalation_active(disposition: str | None) -> bool:
    return (disposition or "").strip().upper() in ESCALATION_ACTIVE


def in_escalation_family(disposition: str | None) -> bool:
    return (disposition or "").strip().upper() in ESCALATION_FAMILY

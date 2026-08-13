"""Canonical read predicates over ``cm_batch1_complaints`` (DEC-025 §3.3).

One definition per predicate so list filter, dashboard, KPI, and report cannot
drift apart. Before this module the same words meant three different things:
``escalated`` was 2 dispositions on the dashboard, 6 on the list filter, and 1
in the report donut.

``status`` is the Aggregate lifecycle SoT; ``intake_disposition`` is the intake
path label and never overrides it.
"""

from __future__ import annotations

#: Aggregate lifecycle exposed by DEC-025 §3.3.
AGGREGATE_STATUSES: tuple[str, ...] = ("REGISTERED", "IN_PROGRESS", "CLOSED")

CLOSED_STATUS = "CLOSED"

#: OPEN = anything not CLOSED (DEC-025 M-025-1). Matches ``_aggregate_status``,
#: which exposes an out-of-set stored value as REGISTERED rather than hiding it,
#: so ``open + closed == total`` holds for every row.
OPEN_STATUSES: tuple[str, ...] = ("REGISTERED", "IN_PROGRESS")

#: Still travelling the escalation path — the KPI/dashboard "escalated" count.
ESCALATION_ACTIVE: tuple[str, ...] = (
    "ESCALATE_PENDING_APPROVAL",
    "ESCALATE_APPROVED",
    "HQ_SCHEDULED",
)

#: Ever entered escalation — list drill-down pseudo-value ``ESCALATED``.
ESCALATION_FAMILY: tuple[str, ...] = (
    "ESCALATE_PENDING_APPROVAL",
    "ESCALATE_APPROVED",
    "ESCALATE_REJECTED",
    "ESCALATE_CANCELLED",
    "RETURNED_TO_BRANCH",
    "HQ_SCHEDULED",
)


def is_closed(status: str | None) -> bool:
    return (status or "").strip().upper() == CLOSED_STATUS


def is_open(status: str | None) -> bool:
    """Open = not closed, so no row falls out of both buckets."""
    return not is_closed(status)


def is_escalation_active(disposition: str | None) -> bool:
    return (disposition or "").strip().upper() in ESCALATION_ACTIVE


def in_escalation_family(disposition: str | None) -> bool:
    return (disposition or "").strip().upper() in ESCALATION_FAMILY

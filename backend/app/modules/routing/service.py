"""Complaint Routing Foundation (TASK-043).

Centralizes initial destination resolution for DEC-018 multi-source/target
complaints. Assignment Engine, SLA, KPI, Notification, and Timeline must
consume ``ComplaintRoute`` — they must not embed routing rules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Mapping

from app.core.enums import (
    ComplaintReceiverType,
    ComplaintSourceType,
    ComplaintTargetType,
)
from app.core.errors import ValidationAppError

# Default supported (source_type, target_type) → receiver_type pairs.
# Future routes are added here only — not in Complaint / Assignment services.
_DEFAULT_ROUTES: Mapping[
    tuple[ComplaintSourceType, ComplaintTargetType], ComplaintReceiverType
] = {
    (ComplaintSourceType.CUSTOMER, ComplaintTargetType.BRANCH): (
        ComplaintReceiverType.BRANCH
    ),
    (ComplaintSourceType.BRANCH, ComplaintTargetType.HEAD_OFFICE): (
        ComplaintReceiverType.HEAD_OFFICE
    ),
    (ComplaintSourceType.HEAD_OFFICE, ComplaintTargetType.BRANCH): (
        ComplaintReceiverType.BRANCH
    ),
    (ComplaintSourceType.SYSTEM, ComplaintTargetType.HEAD_OFFICE): (
        ComplaintReceiverType.HEAD_OFFICE
    ),
}


@dataclass(frozen=True, slots=True)
class ComplaintRoute:
    """Immutable routing result for a complaint create."""

    receiver_type: ComplaintReceiverType
    receiver_id: uuid.UUID | None
    assignment_context: Mapping[str, Any]
    routing_reason: str


class ComplaintRoutingService:
    """Single place for complaint destination routing decisions."""

    def validate_route(
        self,
        *,
        source_type: ComplaintSourceType,
        source_id: uuid.UUID,
        target_type: ComplaintTargetType,
        target_id: uuid.UUID | None,
    ) -> None:
        """Reject unsupported source/target combinations.

        Raises:
            ValidationAppError: when the pair is not in the default matrix,
                or required identifiers are missing for the selected route.
        """
        _ = source_id  # reserved for future policy keyed by originator
        key = (source_type, target_type)
        if key not in _DEFAULT_ROUTES:
            raise ValidationAppError(
                "Invalid complaint route.",
                details={
                    "sourceType": source_type.value,
                    "targetType": target_type.value,
                    "reason": "combination not supported",
                    "supported": [
                        f"{s.value}->{t.value}"
                        for (s, t) in _DEFAULT_ROUTES
                    ],
                },
            )

        receiver = _DEFAULT_ROUTES[key]
        # Legacy CUSTOMER→BRANCH may omit branch (target_id null) — allowed.
        if (
            source_type == ComplaintSourceType.CUSTOMER
            and target_type == ComplaintTargetType.BRANCH
            and target_id is None
        ):
            return

        if target_id is None:
            raise ValidationAppError(
                "targetId is required for this route.",
                details={
                    "sourceType": source_type.value,
                    "targetType": target_type.value,
                    "receiverType": receiver.value,
                },
            )

    def resolve_route(
        self,
        *,
        source_type: ComplaintSourceType,
        source_id: uuid.UUID,
        target_type: ComplaintTargetType,
        target_id: uuid.UUID | None,
    ) -> ComplaintRoute:
        """Validate and resolve the immutable initial route."""
        self.validate_route(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
        )
        receiver_type = _DEFAULT_ROUTES[(source_type, target_type)]
        receiver_id = target_id

        if receiver_type == ComplaintReceiverType.BRANCH:
            assignment_context: dict[str, Any] = {
                "branchId": str(receiver_id) if receiver_id else None,
            }
            reason = (
                f"{source_type.value} → {target_type.value}: "
                "initial receiver is Branch (assignment context = branch)"
            )
        else:
            assignment_context = {
                "headOfficeId": str(receiver_id) if receiver_id else None,
                "branchId": None,
            }
            reason = (
                f"{source_type.value} → {target_type.value}: "
                "initial receiver is Head Office (no branch assignment context)"
            )

        return ComplaintRoute(
            receiver_type=receiver_type,
            receiver_id=receiver_id,
            assignment_context=assignment_context,
            routing_reason=reason,
        )

    @staticmethod
    def supported_routes() -> tuple[tuple[str, str, str], ...]:
        """Return (source, target, receiver) triples for docs/diagnostics."""
        return tuple(
            (s.value, t.value, r.value) for (s, t), r in _DEFAULT_ROUTES.items()
        )

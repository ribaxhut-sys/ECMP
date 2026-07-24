"""DashboardProjection — immutable operational read-model snapshot (TASK-050).

Updated only via Complaint events. Not persisted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class DashboardProjection:
    """Immutable dashboard metrics snapshot.

    Single in-process projection; rebuilt/updated only from Complaint events.
    """

    total_complaints: int
    open_complaints: int
    assigned_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    closed_complaints: int
    escalated_complaints: int
    breached_sla: int
    updated_at: datetime

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP API contract)."""
        return MappingProxyType(
            {
                "totalComplaints": self.total_complaints,
                "openComplaints": self.open_complaints,
                "assignedComplaints": self.assigned_complaints,
                "inProgressComplaints": self.in_progress_complaints,
                "resolvedComplaints": self.resolved_complaints,
                "closedComplaints": self.closed_complaints,
                "escalatedComplaints": self.escalated_complaints,
                "breachedSla": self.breached_sla,
                "updatedAt": self.updated_at.isoformat(),
            }
        )

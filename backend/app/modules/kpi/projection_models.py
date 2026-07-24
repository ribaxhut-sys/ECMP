"""KpiProjection — immutable operational KPI read-model snapshot (TASK-051).

Updated only via Complaint events. Not persisted. No HTTP contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class KpiProjection:
    """Immutable KPI metrics snapshot.

    Single in-process projection; rebuilt/updated only from Complaint events.
    """

    total_received: int
    total_closed: int
    total_resolved: int
    total_escalated: int
    current_open: int
    current_in_progress: int
    sla_breached: int
    closure_rate: float
    resolution_rate: float
    updated_at: datetime

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP API contract)."""
        return MappingProxyType(
            {
                "totalReceived": self.total_received,
                "totalClosed": self.total_closed,
                "totalResolved": self.total_resolved,
                "totalEscalated": self.total_escalated,
                "currentOpen": self.current_open,
                "currentInProgress": self.current_in_progress,
                "slaBreached": self.sla_breached,
                "closureRate": self.closure_rate,
                "resolutionRate": self.resolution_rate,
                "updatedAt": self.updated_at.isoformat(),
            }
        )

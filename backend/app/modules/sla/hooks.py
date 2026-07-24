"""Internal hook for domain services to evaluate SLA statuses (TASK-024)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.sla.repository import SlaRepository
from app.modules.sla.service import SlaService


def evaluate_sla_for_complaint(
    session: Session,
    complaint_id: uuid.UUID,
    *,
    now: datetime | None = None,
) -> None:
    """Evaluate SLA statuses in the current transaction (no commit).

    Safe no-op when the complaint has no SLA row.
    """
    SlaService(SlaRepository(session)).evaluate_for_complaint(
        complaint_id,
        now=now,
        commit=False,
    )

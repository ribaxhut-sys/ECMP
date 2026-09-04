"""Map dashboard/report ``branchId`` (UUID) → Aggregate ``owning_unit_id``."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import Branch


def owning_unit_for_branch(session: Session, branch_id: uuid.UUID) -> str | None:
    branch = session.get(Branch, branch_id)
    if branch is None or getattr(branch, "deleted_at", None) is not None:
        return None
    code = (getattr(branch, "code", None) or "").strip()
    return code or None

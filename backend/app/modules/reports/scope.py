"""Who may see which unit on /reports (API-210…212, API-545, API-546).

Cabang principals are locked to their home branch. Pusat / Head Office
(no home branch, or home unit is a Pusat code) may omit branchId for every
unit or pick one. Enforced in the router — the UI picker is not the gate.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authorization.principal import Principal
from app.core.authorization.visibility import is_pusat_unit
from app.models import Branch, User


def effective_report_branch_id(
    session: Session,
    principal: Principal,
    requested: uuid.UUID | None,
) -> uuid.UUID | None:
    """Return the branchId the report queries must use.

    ``None`` means every unit. A cabang user cannot widen or switch away
    from their own branch by sending another ``branchId``.
    """
    own_branch_id = session.scalar(
        select(User.branch_id).where(User.id == principal.user_id)
    )
    if own_branch_id is None:
        return requested
    code = session.scalar(select(Branch.code).where(Branch.id == own_branch_id))
    if is_pusat_unit(code):
        return requested
    return own_branch_id

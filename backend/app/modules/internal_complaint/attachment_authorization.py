"""Authorization for InternalComplaint-owned attachments (CAPABILITY-011).

Used by the shared attachment router when aggregate_type is InternalComplaint.
Visibility matches ticket get: owner unit OR handling unit (enforce_org_scope_any).
Do not bind Internal files to cm_batch1_attachments / FR-004 staging.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.authorization.org_unit_guard import enforce_org_scope_any
from app.core.authorization.principal import Principal
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.modules.internal_complaint.application.services import (
    InternalComplaintApplicationService,
)
from app.modules.internal_complaint.infrastructure.repository import (
    SqlAlchemyInternalComplaintRepository,
)


def assert_can_access_internal_complaint_attachment(
    *,
    principal: Principal,
    session: Session,
    aggregate_id: uuid.UUID,
    settings: Settings,
) -> None:
    """Gate upload / list / metadata / download / delete for a ticket's files."""
    service = InternalComplaintApplicationService(
        SqlAlchemyInternalComplaintRepository(session)
    )
    try:
        dto = service.get(str(aggregate_id))
    except NotFoundError:
        raise NotFoundError(m("attachment.not_found")) from None
    enforce_org_scope_any(
        principal,
        (dto.owner_unit_id, dto.handling_unit_id),
        settings,
    )

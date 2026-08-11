"""Authorization for Knowledge-owned attachments (source files).

Used by the *shared* attachment router (CAPABILITY-011) when an attachment's
aggregate_type is "Knowledge" — see app/modules/attachment/router.py.
Backend-only enforcement; the frontend is never trusted.

Rule (business decision, LOCKED — ECMP Modul Pengetahuan §11): file access
mirrors Knowledge access exactly — one source of truth, never two:
  - Pengelola (knowledge:manage, Pusat-proven) may open any file regardless
    of Knowledge status, same as they may view a DRAFT Knowledge.
  - Any other knowledge:read holder may open a file only when its owning
    Knowledge is ACTIVE or ARCHIVED (never DRAFT) — matching
    KnowledgeService.get (detail read gate). No org-unit narrowing: Knowledge
    v1 is global-read, Pusat-curated.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.authorization.gates import principal_may_manage_knowledge
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.user_messages import m
from app.modules.knowledge.file_repository import KnowledgeFileRepository
from app.modules.knowledge.repository import KnowledgeRepository

_READABLE_STATUSES = ("ACTIVE", "ARCHIVED")


def resolve_caller_org_unit(principal: Principal, session: Session) -> str | None:
    resolver = OrgUnitResolver(session)
    return resolver.normalize(principal.org_unit_id) or resolver.resolve_principal_membership(
        principal.user_id
    )


def assert_can_access_knowledge_attachment(
    *,
    principal: Principal,
    session: Session,
    attachment_id: uuid.UUID,
) -> None:
    """Gate for reading metadata / downloading bytes (GET, GET .../download)."""
    join = KnowledgeFileRepository(session).get_by_attachment_id(attachment_id)
    if join is None:
        raise NotFoundError(m("attachment.not_found"))

    knowledge = KnowledgeRepository(session).get(join.knowledge_id)
    if knowledge is None:
        raise NotFoundError(m("attachment.not_found"))

    org = resolve_caller_org_unit(principal, session)
    if principal_may_manage_knowledge(principal, org_unit_id=org):
        return

    if not principal.has_permission("knowledge:read"):
        raise PermissionDeniedError(m("common.forbidden"))
    if knowledge.status not in _READABLE_STATUSES:
        raise NotFoundError(m("attachment.not_found"))

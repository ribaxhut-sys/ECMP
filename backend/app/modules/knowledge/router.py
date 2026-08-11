"""Knowledge (Pengetahuan) HTTP routes.

Two permission tiers (business decision, LOCKED — ECMP Modul Pengetahuan §3):
  - knowledge:read   — anyone with Pengaduan module access (mirrors whichever
    roles already hold complaints:read; seeded in 0070_knowledge_permissions).
  - knowledge:manage — Admin Pusat / Supervisor Pusat / Manager Pusat only,
    same Pusat-proof rule as announcement:manage (require_knowledge_manage).
"""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.authorization.gates import (
    principal_may_manage_knowledge,
    require_knowledge_manage,
)
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.attachment.registration import build_attachment_service
from app.modules.knowledge.authorization import resolve_caller_org_unit
from app.modules.knowledge.file_repository import KnowledgeFileRepository
from app.modules.knowledge.repository import KnowledgeRepository
from app.modules.knowledge.schemas import (
    KnowledgeCreateRequest,
    KnowledgeResponse,
    KnowledgeUpdateRequest,
)
from app.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge"])

KnowledgeTypeFilter = Literal["SOP", "PERATURAN", "SURAT_EDARAN", "KEPUTUSAN", "PANDUAN"]
KnowledgeStatusFilter = Literal["ACTIVE", "ARCHIVED", "DRAFT"]
KnowledgeFileRoleForm = Literal["PRIMARY", "SUPPORTING"]


def get_knowledge_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> KnowledgeService:
    return KnowledgeService(
        repository=KnowledgeRepository(session),
        files=KnowledgeFileRepository(session),
        attachments=build_attachment_service(session),
    )


def _caller_may_manage(principal: Principal, session: Session) -> bool:
    org = resolve_caller_org_unit(principal, session)
    return principal_may_manage_knowledge(principal, org_unit_id=org)


@router.get(
    "",
    response_model=DataResponse[list[KnowledgeResponse]],
    status_code=status.HTTP_200_OK,
    summary="Search Knowledge (single shared list — reader + manager)",
)
def search_knowledge(
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_permissions("knowledge:read"))],
    session: Annotated[Session, Depends(get_db_session)],
    q: Annotated[str | None, Query(max_length=200)] = None,
    knowledge_type: Annotated[
        KnowledgeTypeFilter | None, Query(alias="type")
    ] = None,
    status_filter: Annotated[
        KnowledgeStatusFilter, Query(alias="status")
    ] = "ACTIVE",
    reference_only: Annotated[bool, Query(alias="referenceOnly")] = False,
) -> DataResponse[list[KnowledgeResponse]]:
    """Default ``status=ACTIVE`` narrows to the effective window for
    non-managers; ``status=DRAFT`` requires knowledge:manage.

    ``referenceOnly=true`` (Complaint Resolution ``@`` mention) always
    forces ACTIVE + effective-window narrowing, even for knowledge:manage
    callers — a Knowledge citable as the basis of a new Penyelesaian must be
    in effect *right now*, regardless of who is typing.
    """
    caller_may_manage = _caller_may_manage(principal, session)
    data = service.search(
        q=q,
        knowledge_type=knowledge_type,
        status=status_filter,
        caller_may_manage=caller_may_manage,
        reference_only=reference_only,
    )
    return DataResponse(data=data)


@router.get(
    "/{id}",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Knowledge detail",
)
def get_knowledge(
    id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_permissions("knowledge:read"))],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[KnowledgeResponse]:
    """DRAFT is never visible outside knowledge:manage — matches the search
    gate so a known UUID cannot bypass the DRAFT restriction."""
    caller_may_manage = _caller_may_manage(principal, session)
    return DataResponse(data=service.get(id, caller_may_manage=caller_may_manage))


@router.post(
    "",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Knowledge (draft)",
)
def create_knowledge(
    payload: KnowledgeCreateRequest,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[KnowledgeResponse]:
    org = resolve_caller_org_unit(principal, session)
    return DataResponse(
        data=service.create(
            payload, actor_id=principal.user_id, owner_org_unit_id=org or "PUSAT"
        )
    )


@router.put(
    "/{id}",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Knowledge metadata",
)
def update_knowledge(
    id: uuid.UUID,
    payload: KnowledgeUpdateRequest,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> DataResponse[KnowledgeResponse]:
    return DataResponse(data=service.update(id, payload, actor_id=principal.user_id))


@router.put(
    "/{id}/publish",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Publish (activate) Knowledge — DRAFT -> ACTIVE",
)
def publish_knowledge(
    id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> DataResponse[KnowledgeResponse]:
    return DataResponse(data=service.publish(id, actor_id=principal.user_id))


@router.put(
    "/{id}/archive",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Archive Knowledge — ACTIVE -> ARCHIVED",
)
def archive_knowledge(
    id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> DataResponse[KnowledgeResponse]:
    return DataResponse(data=service.archive(id, actor_id=principal.user_id))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Knowledge (soft delete — DRAFT only)",
)
def delete_knowledge(
    id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> Response:
    service.delete(id, actor_id=principal.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Files (knowledge:manage, DRAFT only — see KnowledgeService) -----------
#
# Upload reuses the shared AttachmentService for all storage/checksum/mime
# work (no new storage system). Reading (metadata + bytes) goes through the
# *generic* /api/v1/attachments/{id} and .../download routes — see
# app/modules/attachment/router.py's Knowledge branch, gated by
# assert_can_access_knowledge_attachment.


@router.post(
    "/{id}/files",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a source file onto a Knowledge draft",
)
async def upload_knowledge_file(
    id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
    file: Annotated[UploadFile, File()],
    role: Annotated[KnowledgeFileRoleForm, Form()] = "SUPPORTING",
) -> DataResponse[KnowledgeResponse]:
    data = await file.read()
    result = service.upload_file(
        id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        role=role,
        actor_id=principal.user_id,
    )
    return DataResponse(data=result)


@router.put(
    "/{id}/files/{attachment_id}/primary",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Set a file as the primary source document",
)
def set_primary_knowledge_file(
    id: uuid.UUID,
    attachment_id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> DataResponse[KnowledgeResponse]:
    result = service.set_primary_file(id, attachment_id, actor_id=principal.user_id)
    return DataResponse(data=result)


@router.delete(
    "/{id}/files/{attachment_id}",
    response_model=DataResponse[KnowledgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Remove a file from a Knowledge draft",
)
def remove_knowledge_file(
    id: uuid.UUID,
    attachment_id: uuid.UUID,
    service: Annotated[KnowledgeService, Depends(get_knowledge_service)],
    principal: Annotated[Principal, Depends(require_knowledge_manage)],
) -> DataResponse[KnowledgeResponse]:
    _ = principal
    result = service.remove_file(id, attachment_id)
    return DataResponse(data=result)

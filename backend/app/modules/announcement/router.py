"""Announcement HTTP routes.

Two permission tiers (business decision, LOCKED):
  - announcement:read   — anyone with Pengaduan module access (mirrors
    whichever roles already hold complaints:read; seeded in
    0063_announcement_permissions).
  - announcement:manage — Admin Pusat / Supervisor Pusat / Manager Pusat only.
    ADMIN is always head-office (never carries a branch — see
    HEAD_OFFICE_SCOPED_ROLE_CODES). SUPERVISOR/MANAGER are branch-scoped role
    codes shared with Cabang staff, so the announcement:manage permission
    grant alone is not sufficient to prove "Pusat" — require_announcement_manage
    additionally checks the caller's own org unit resolves to a Pusat-coded
    branch (is_pusat_unit), the same mechanism already used for "Agent Pusat"
    (require_hq_intake_action). Enforced server-side — never trusts a
    client-supplied role.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.authorization.gates import (
    principal_may_manage_announcements,
    require_announcement_manage,
)
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.announcement.attachment_repository import AnnouncementAttachmentRepository
from app.modules.announcement.attachment_service import AnnouncementAttachmentService
from app.modules.announcement.catalog_access import (
    caller_is_pusat,
    resolve_caller_org_unit,
)
from app.modules.announcement.repository import AnnouncementRepository
from app.modules.announcement.schemas import (
    AnnouncementAttachmentAccessUpdateRequest,
    AnnouncementAttachmentLibraryItem,
    AnnouncementAttachmentLinkRequest,
    AnnouncementAttachmentResponse,
    AnnouncementAttachmentVisibilityUpdateRequest,
    AnnouncementCreateRequest,
    AnnouncementPublishRequest,
    AnnouncementResponse,
    AnnouncementUpdateRequest,
)
from app.modules.announcement.service import AnnouncementService
from app.modules.attachment.registration import build_attachment_service

router = APIRouter(prefix="/api/v1/announcements", tags=["Announcements"])


def get_announcement_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AnnouncementAttachmentService:
    return AnnouncementAttachmentService(
        announcements=AnnouncementRepository(session),
        join_repo=AnnouncementAttachmentRepository(session),
        attachments=build_attachment_service(session),
        session=session,
    )


def get_announcement_service(
    session: Annotated[Session, Depends(get_db_session)],
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
) -> AnnouncementService:
    return AnnouncementService(AnnouncementRepository(session), attachments=attachments)


def _caller_may_manage(principal: Principal, session: Session) -> bool:
    """Same predicate as require_announcement_manage, used where a route is
    reachable by any announcement:read holder but should show unfiltered
    attachments to the 3 manage roles (e.g. the detail view while editing)."""
    resolver = OrgUnitResolver(session)
    org = resolver.normalize(principal.org_unit_id) or resolver.resolve_principal_membership(
        principal.user_id
    )
    return principal_may_manage_announcements(principal, org_unit_id=org)


@router.get(
    "",
    response_model=DataResponse[list[AnnouncementResponse]],
    status_code=status.HTTP_200_OK,
    summary="List announcements (management — all statuses)",
)
def list_announcements(
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[list[AnnouncementResponse]]:
    _ = principal
    return DataResponse(data=service.list_for_management())


@router.get(
    "/active",
    response_model=DataResponse[list[AnnouncementResponse]],
    status_code=status.HTTP_200_OK,
    summary="List active announcements for the Pengaduan landing page",
)
def list_active_announcements(
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> DataResponse[list[AnnouncementResponse]]:
    """PUBLISHED + in-window — global for every announcement:read holder."""
    _ = principal
    return DataResponse(data=service.list_active())


@router.get(
    "/history",
    response_model=DataResponse[list[AnnouncementResponse]],
    status_code=status.HTTP_200_OK,
    summary="Archive — every PUBLISHED/ARCHIVED announcement",
)
def list_announcement_history(
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> DataResponse[list[AnnouncementResponse]]:
    """Reader archive (§4, LOCKED) — same auth pattern as /active
    (announcement:read, no manage requirement). DRAFT and SCHEDULED never
    appear; expired (past end_at) stays visible. See list_history.
    ``isRead`` is per authenticated caller.
    """
    return DataResponse(data=service.list_history(user_id=principal.user_id))


@router.get(
    "/unread",
    response_model=DataResponse[int],
    status_code=status.HTTP_200_OK,
    summary="Count of unread active announcements for the caller",
)
def get_unread_active_count(
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> DataResponse[int]:
    """Post-login gate + sidebar badge — COUNT, never the full /active list.
    Same active-window predicate as /active, plus "no read record for this
    user yet". ``0`` → Dashboard; ``> 0`` → /announcements then the bell
    number. Expired and archived items are excluded."""
    return DataResponse(data=service.count_unread_active(user_id=principal.user_id))


@router.get(
    "/attachment-library",
    response_model=DataResponse[list[AnnouncementAttachmentLibraryItem]],
    status_code=status.HTTP_200_OK,
    summary="Announcement attachment catalog / link picker (access-filtered)",
)
def list_announcement_attachment_library(
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
    q: Annotated[str | None, Query()] = None,
    exclude_announcement_id: Annotated[
        uuid.UUID | None, Query(alias="excludeAnnouncementId")
    ] = None,
    org_scope: Annotated[
        Literal["all", "pusat", "cabang"],
        Query(alias="orgScope"),
    ] = "all",
) -> DataResponse[list[AnnouncementAttachmentLibraryItem]]:
    """PUBLIC/PRIVATE filtered catalog. Must be registered before ``/{id}``."""
    return DataResponse(
        data=attachments.list_library(
            principal=principal,
            q=q,
            exclude_announcement_id=exclude_announcement_id,
            include_orphans=True,
            org_scope=org_scope,
        )
    )


@router.put(
    "/attachment-library/{attachment_id}/access",
    response_model=DataResponse[AnnouncementAttachmentLibraryItem],
    status_code=status.HTTP_200_OK,
    summary="Set PUBLIC/PRIVATE access for an announcement catalog file",
)
def update_announcement_attachment_access(
    attachment_id: uuid.UUID,
    payload: AnnouncementAttachmentAccessUpdateRequest,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> DataResponse[AnnouncementAttachmentLibraryItem]:
    return DataResponse(
        data=attachments.update_access_level(
            attachment_id,
            access_level=payload.access_level,
            principal=principal,
        )
    )


@router.delete(
    "/attachment-library/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an announcement attachment from the catalog",
)
def delete_announcement_attachment_from_catalog(
    attachment_id: uuid.UUID,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> Response:
    attachments.delete_from_catalog(attachment_id, principal=principal)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/attachment-library",
    response_model=DataResponse[AnnouncementAttachmentLibraryItem],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file into the announcement attachment catalog",
)
async def upload_announcement_attachment_to_catalog(
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
    session: Annotated[Session, Depends(get_db_session)],
    file: Annotated[UploadFile, File()],
    access_level: Annotated[
        Literal["PUBLIC", "PRIVATE"], Form(alias="accessLevel")
    ] = "PRIVATE",
) -> DataResponse[AnnouncementAttachmentLibraryItem]:
    """Catalog upload — no announcement join. Default PRIVATE + caller org unit.

    Must be registered before ``/{id}``. Cabang callers see all files of their
    own org unit via catalog access rules.
    """
    data = await file.read()
    org = resolve_caller_org_unit(principal, session)
    # Unscoped Pusat/Admin has no branch membership — stamp PUSAT so the row
    # is discoverable in catalog filters and UI (not a blank Private · —).
    if org is None and caller_is_pusat(principal, session):
        org = "PUSAT"
    result = attachments.upload_to_catalog(
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        actor_id=principal.user_id,
        uploaded_org_unit_id=org,
        access_level=access_level,
    )
    return DataResponse(data=result)


@router.get(
    "/{id}",
    response_model=DataResponse[AnnouncementResponse],
    status_code=status.HTTP_200_OK,
    summary="Get announcement detail",
)
def get_announcement(
    id: uuid.UUID,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[AnnouncementResponse]:
    """Attachments are visibility-filtered unless the caller is one of the
    3 manage roles (Admin/Supervisor/Manager Pusat), who see every attachment
    regardless of status — same as the management list."""
    if _caller_may_manage(principal, session):
        return DataResponse(data=service.get_for_management(id))
    return DataResponse(data=service.get_for_reader(id))


@router.post(
    "",
    response_model=DataResponse[AnnouncementResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create announcement (draft)",
)
def create_announcement(
    payload: AnnouncementCreateRequest,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[AnnouncementResponse]:
    return DataResponse(data=service.create(payload, actor_id=principal.user_id))


@router.put(
    "/{id}",
    response_model=DataResponse[AnnouncementResponse],
    status_code=status.HTTP_200_OK,
    summary="Update announcement",
)
def update_announcement(
    id: uuid.UUID,
    payload: AnnouncementUpdateRequest,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[AnnouncementResponse]:
    return DataResponse(
        data=service.update(id, payload, actor_id=principal.user_id)
    )


@router.put(
    "/{id}/publish",
    response_model=DataResponse[AnnouncementResponse],
    status_code=status.HTTP_200_OK,
    summary="Publish announcement (optional startAt — no approval / no scheduler)",
)
def publish_announcement(
    id: uuid.UUID,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
    payload: Annotated[AnnouncementPublishRequest | None, Body()] = None,
) -> DataResponse[AnnouncementResponse]:
    """Omit body / startAt for publish-now. Future startAt schedules visibility
    via read-time evaluation (DB status stays PUBLISHED; DEC: no scheduler)."""
    start_at = payload.start_at if payload is not None else None
    return DataResponse(
        data=service.publish(id, actor_id=principal.user_id, start_at=start_at)
    )


@router.put(
    "/{id}/unpublish",
    response_model=DataResponse[AnnouncementResponse],
    status_code=status.HTTP_200_OK,
    summary="Unpublish (archive) announcement",
)
def unpublish_announcement(
    id: uuid.UUID,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[AnnouncementResponse]:
    return DataResponse(data=service.unpublish(id, actor_id=principal.user_id))


@router.put(
    "/{id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark an announcement as read by the caller (idempotent)",
)
def mark_announcement_read(
    id: uuid.UUID,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_permissions("announcement:read"))],
) -> Response:
    """Read-state milestone (§4/§15, LOCKED) — considered read only when the
    reader opens the detail (not the list). ``user_id`` is always the
    authenticated principal, never a client-supplied value."""
    service.mark_read(id, user_id=principal.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete announcement (soft delete)",
)
def delete_announcement(
    id: uuid.UUID,
    service: Annotated[AnnouncementService, Depends(get_announcement_service)],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> Response:
    service.delete(id, actor_id=principal.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Attachments (§5–8, LOCKED) --------------------------------------------
#
# Creation/removal/visibility changes are manage-only — reuses the shared
# AttachmentService for all storage/upload/checksum/mime work (no new
# storage system). Reading (metadata + bytes) goes through the *generic*
# /api/v1/attachments/{id} and .../download routes — see
# app/modules/attachment/router.py's Announcement branch, gated by
# assert_can_access_announcement_attachment (visibility rule).


@router.post(
    "/{id}/attachments",
    response_model=DataResponse[AnnouncementAttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload an attachment onto an announcement",
)
async def upload_announcement_attachment(
    id: uuid.UUID,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
    session: Annotated[Session, Depends(get_db_session)],
    file: Annotated[UploadFile, File()],
    visibility: Annotated[
        Literal["IMMEDIATE", "PUBLISHED"], Form()
    ] = "PUBLISHED",
) -> DataResponse[AnnouncementAttachmentResponse]:
    data = await file.read()
    org = resolve_caller_org_unit(principal, session)
    if org is None and caller_is_pusat(principal, session):
        org = "PUSAT"
    result = attachments.upload(
        id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        visibility=visibility,
        actor_id=principal.user_id,
        uploaded_org_unit_id=org,
        access_level="PRIVATE",
    )
    return DataResponse(data=result)


@router.post(
    "/{id}/attachments/link",
    response_model=DataResponse[AnnouncementAttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Link an existing announcement attachment (no file copy)",
)
def link_announcement_attachment(
    id: uuid.UUID,
    payload: AnnouncementAttachmentLinkRequest,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[AnnouncementAttachmentResponse]:
    result = attachments.link(
        id,
        attachment_id=payload.attachment_id,
        visibility=payload.visibility,
        actor_id=principal.user_id,
        principal=principal,
    )
    return DataResponse(data=result)


@router.put(
    "/{id}/attachments/{attachment_id}",
    response_model=DataResponse[AnnouncementAttachmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Change an attachment's visibility",
)
def update_announcement_attachment_visibility(
    id: uuid.UUID,
    attachment_id: uuid.UUID,
    payload: AnnouncementAttachmentVisibilityUpdateRequest,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> DataResponse[AnnouncementAttachmentResponse]:
    result = attachments.update_visibility(
        id, attachment_id, visibility=payload.visibility, actor_id=principal.user_id
    )
    return DataResponse(data=result)


@router.delete(
    "/{id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an attachment from an announcement",
)
def remove_announcement_attachment(
    id: uuid.UUID,
    attachment_id: uuid.UUID,
    attachments: Annotated[
        AnnouncementAttachmentService, Depends(get_announcement_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_announcement_manage)],
) -> Response:
    _ = principal
    attachments.remove(id, attachment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

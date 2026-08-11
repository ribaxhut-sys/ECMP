"""Knowledge application service (no FastAPI imports).

Permission gating (knowledge:read / knowledge:manage) happens at the router
via ``require_permissions`` / ``require_knowledge_manage`` — this service
only handles the one *record-level* visibility rule that depends on the
result of that gate: DRAFT is invisible to non-managers (mirrors
AnnouncementService.get_for_reader / get_for_management).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.core.errors import (
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ValidationAppError,
)
from app.core.user_messages import m
from app.modules.attachment.domain.enums import AggregateType
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.service import AttachmentService
from app.modules.knowledge.file_repository import KnowledgeFileRepository, KnowledgeFileRow
from app.modules.knowledge.models import KnowledgeORM
from app.modules.knowledge.repository import KnowledgeRepository, within_effective_window
from app.modules.knowledge.schemas import (
    KnowledgeCreateRequest,
    KnowledgeFileResponse,
    KnowledgeResponse,
    KnowledgeUpdateRequest,
)

KNOWLEDGE_NOT_FOUND_MESSAGE = m("knowledge.not_found")


def _file_response(row: KnowledgeFileRow) -> KnowledgeFileResponse:
    return KnowledgeFileResponse(
        id=row.attachment_id,
        fileName=row.original_name,
        mimeType=row.mime_type,
        sizeBytes=row.size_bytes,
        role=row.role,  # type: ignore[arg-type]
        createdAt=row.created_at,
    )


class KnowledgeService:
    def __init__(
        self,
        repository: KnowledgeRepository,
        files: KnowledgeFileRepository,
        attachments: AttachmentService,
    ) -> None:
        self._repo = repository
        self._files = files
        self._attachments = attachments

    def _to_response(
        self, row: KnowledgeORM, file_rows: list[KnowledgeFileRow]
    ) -> KnowledgeResponse:
        supersedes_title: str | None = None
        if row.supersedes_knowledge_id is not None:
            prior = self._repo.get(row.supersedes_knowledge_id)
            supersedes_title = prior.title if prior is not None else None
        return KnowledgeResponse(
            id=row.id,
            title=row.title,
            knowledgeType=row.knowledge_type,  # type: ignore[arg-type]
            status=row.status,  # type: ignore[arg-type]
            documentNumber=row.document_number,
            summary=row.summary,
            versionLabel=row.version_label,
            effectiveFrom=row.effective_from,
            effectiveTo=row.effective_to,
            ownerOrgUnitId=row.owner_org_unit_id,
            publishedAt=row.published_at,
            publishedBy=row.published_by,
            supersedesKnowledgeId=row.supersedes_knowledge_id,
            supersedesTitle=supersedes_title,
            createdBy=row.created_by,
            createdAt=row.created_at,
            updatedBy=row.updated_by,
            updatedAt=row.updated_at,
            files=[_file_response(f) for f in file_rows],
        )

    # --- Read ---------------------------------------------------------

    # Cap for Complaint Resolution ``@`` mention dropdown (product UX).
    REFERENCE_SEARCH_DEFAULT_LIMIT = 10
    REFERENCE_SEARCH_MAX_LIMIT = 10

    def search(
        self,
        *,
        q: str | None,
        knowledge_type: str | None,
        status: str,
        caller_may_manage: bool,
        reference_only: bool = False,
        limit: int | None = None,
    ) -> list[KnowledgeResponse]:
        """``reference_only`` — Complaint Resolution ``@`` mention search
        (KM Reference §3, LOCKED): always ACTIVE + within the effective
        window, unconditionally — the ``caller_may_manage`` window bypass
        below exists for the *management* list (so a manager can find a
        lapsed-but-ACTIVE record to archive it) and must never leak into
        what a new Penyelesaian may cite.

        Reference search returns at most 10 rows (default and hard cap) so
        the ``@`` popover stays scannable; the management list is uncapped
        unless the caller passes an explicit ``limit``.
        """
        effective_status = "ACTIVE" if reference_only else status
        if effective_status == "DRAFT" and not caller_may_manage:
            raise PermissionDeniedError(m("knowledge.only_admin_supervisor_manager_pusat"))
        rows = self._repo.search(q=q, knowledge_type=knowledge_type, status=effective_status)
        if effective_status == "ACTIVE" and (reference_only or not caller_may_manage):
            now = datetime.now(UTC)
            rows = [r for r in rows if within_effective_window(r, now=now)]
        if reference_only:
            cap = self.REFERENCE_SEARCH_DEFAULT_LIMIT
            if limit is not None:
                cap = min(limit, self.REFERENCE_SEARCH_MAX_LIMIT)
            rows = rows[:cap]
        elif limit is not None:
            rows = rows[:limit]
        files_by_id = self._files.list_for_knowledge_ids([r.id for r in rows])
        return [self._to_response(r, files_by_id.get(r.id, [])) for r in rows]

    def get(self, knowledge_id: uuid.UUID, *, caller_may_manage: bool) -> KnowledgeResponse:
        row = self._repo.get(knowledge_id)
        if row is None or (row.status == "DRAFT" and not caller_may_manage):
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        files = self._files.list_for_knowledge(knowledge_id)
        return self._to_response(row, files)

    # --- Management (knowledge:manage) ---------------------------------

    def create(
        self,
        payload: KnowledgeCreateRequest,
        *,
        actor_id: uuid.UUID,
        owner_org_unit_id: str | None,
        commit: bool = True,
    ) -> KnowledgeResponse:
        """Always creates DRAFT — publishing is a separate, explicit action."""
        row = self._repo.create(
            title=payload.title,
            knowledge_type=payload.knowledge_type,
            document_number=payload.document_number,
            summary=payload.summary,
            version_label=payload.version_label,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            owner_org_unit_id=owner_org_unit_id,
            created_by=actor_id,
        )
        if payload.supersedes_knowledge_id is not None:
            row.supersedes_knowledge_id = payload.supersedes_knowledge_id
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        return self._to_response(row, [])

    def update(
        self,
        knowledge_id: uuid.UUID,
        payload: KnowledgeUpdateRequest,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> KnowledgeResponse:
        """DRAFT — fully editable. ACTIVE/ARCHIVED — identity fields (title,
        knowledgeType, versionLabel) are locked (KM §17, LOCKED): a
        substantive change must instead create a new Knowledge record with
        ``supersedesKnowledgeId``."""
        row = self._repo.get(knowledge_id)
        if row is None:
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        if row.status != "DRAFT" and (
            payload.title != row.title
            or payload.knowledge_type != row.knowledge_type
            or payload.version_label != row.version_label
        ):
            raise ValidationAppError(m("knowledge.active_identity_locked"))
        row = self._repo.update_fields(
            row,
            title=payload.title,
            knowledge_type=payload.knowledge_type,
            document_number=payload.document_number,
            summary=payload.summary,
            version_label=payload.version_label,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            updated_by=actor_id,
        )
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        files = self._files.list_for_knowledge(knowledge_id)
        return self._to_response(row, files)

    def publish(
        self,
        knowledge_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> KnowledgeResponse:
        row = self._repo.get(knowledge_id)
        if row is None:
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        if row.status != "DRAFT":
            raise InvalidStateError(m("knowledge.not_draft"))
        primary = self._files.get_primary(knowledge_id)
        if primary is None:
            raise ValidationAppError(m("knowledge.primary_file_required"))
        if (
            row.effective_from is not None
            and row.effective_to is not None
            and row.effective_from >= row.effective_to
        ):
            raise ValidationAppError(m("knowledge.effective_to_before_from"))
        row = self._repo.publish(row, published_by=actor_id)
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        files = self._files.list_for_knowledge(knowledge_id)
        return self._to_response(row, files)

    def archive(
        self,
        knowledge_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> KnowledgeResponse:
        row = self._repo.get(knowledge_id)
        if row is None:
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        if row.status != "ACTIVE":
            raise InvalidStateError(m("knowledge.not_active"))
        row = self._repo.archive(row, updated_by=actor_id)
        if commit:
            self._repo.commit()
            self._repo.refresh(row)
        files = self._files.list_for_knowledge(knowledge_id)
        return self._to_response(row, files)

    def delete(
        self,
        knowledge_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        commit: bool = True,
    ) -> None:
        """Soft delete — DRAFT only (KM §23, LOCKED). ACTIVE/ARCHIVED are
        never deletable, hard or soft."""
        row = self._repo.get(knowledge_id)
        if row is None:
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        if row.status != "DRAFT":
            raise InvalidStateError(m("knowledge.delete_draft_only"))
        self._repo.soft_delete(row, deleted_by=actor_id)
        if commit:
            self._repo.commit()

    # --- Files (knowledge:manage, DRAFT only) ---------------------------

    def _require_draft(self, knowledge_id: uuid.UUID) -> KnowledgeORM:
        row = self._repo.get(knowledge_id)
        if row is None:
            raise NotFoundError(KNOWLEDGE_NOT_FOUND_MESSAGE)
        if row.status != "DRAFT":
            raise InvalidStateError(m("knowledge.files_draft_only"))
        return row

    def upload_file(
        self,
        knowledge_id: uuid.UUID,
        *,
        filename: str | None,
        content_type: str | None,
        data: bytes,
        role: str,
        actor_id: uuid.UUID,
    ) -> KnowledgeResponse:
        self._require_draft(knowledge_id)
        uploaded: AttachmentResponse = self._attachments.upload(
            aggregate_type=AggregateType.KNOWLEDGE.value,
            aggregate_id=knowledge_id,
            filename=filename,
            content_type=content_type,
            data=data,
            uploaded_by=actor_id,
            commit=False,
        )
        join = self._files.create(
            knowledge_id=knowledge_id,
            attachment_id=uploaded.id,
            role="SUPPORTING",
            created_by=actor_id,
        )
        if role == "PRIMARY":
            self._files.set_primary(join, updated_by=actor_id)
        self._files.commit()
        return self.get(knowledge_id, caller_may_manage=True)

    def set_primary_file(
        self,
        knowledge_id: uuid.UUID,
        attachment_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
    ) -> KnowledgeResponse:
        self._require_draft(knowledge_id)
        join = self._files.get(knowledge_id, attachment_id)
        if join is None:
            raise NotFoundError(m("attachment.not_found"))
        self._files.set_primary(join, updated_by=actor_id)
        self._files.commit()
        return self.get(knowledge_id, caller_may_manage=True)

    def remove_file(
        self,
        knowledge_id: uuid.UUID,
        attachment_id: uuid.UUID,
    ) -> KnowledgeResponse:
        self._require_draft(knowledge_id)
        join = self._files.get(knowledge_id, attachment_id)
        if join is None:
            raise NotFoundError(m("attachment.not_found"))
        self._files.delete(join)
        self._attachments.soft_delete(attachment_id, commit=False)
        self._files.commit()
        return self.get(knowledge_id, caller_may_manage=True)

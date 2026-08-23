"""CM Batch 1 attachment orchestration over CAP-011 AttachmentService (FR-004)."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from app.core.errors import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationAppError,
)
from app.core.logging import get_logger
from app.core.user_messages import m
from app.modules.attachment.domain.enums import AggregateType
from app.modules.attachment.service import (
    AttachmentService,
    normalize_upload_mime,
    sanitize_filename,
)
from app.modules.cm_batch1 import event_factory as events
from app.modules.cm_batch1.antivirus import AntivirusScanner, StubAntivirusScanner
from app.modules.cm_batch1.attachment_config import (
    DEFAULT_ATTACHMENT_CONFIG_PROVIDER,
    AttachmentConfig,
    AttachmentConfigProvider,
)
from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
from app.modules.cm_batch1.entities import (
    ATTACHMENT_STATUS_ACTIVE,
    ATTACHMENT_STATUS_STAGED,
    ATTACHMENT_STATUS_SUPERSEDED,
    ATTACHMENT_STATUS_TRANSFERRED,
    ATTACHMENT_STATUS_VOID,
    Batch1AttachmentRecord,
)
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import (
    Batch1AttachmentResponse,
    TransferAttachmentsRequest,
    TransferAttachmentsResponse,
)
from app.modules.cm_batch1.side_effects import (
    NoOpSideEffectRecorder,
    SideEffectRecorder,
)

logger = get_logger("app.modules.cm_batch1.attachment")


class CmBatch1AttachmentService:
    """Orchestrates staging / bind / transfer / void; binaries via CAP-011."""

    def __init__(
        self,
        *,
        attachment_service: AttachmentService,
        repository: CmBatch1AttachmentRepository,
        complaints: CmBatch1Repository,
        config_provider: AttachmentConfigProvider | None = None,
        antivirus: AntivirusScanner | None = None,
        side_effects: SideEffectRecorder | None = None,
    ) -> None:
        self._attachments = attachment_service
        self._repo = repository
        self._complaints = complaints
        self._config_provider = config_provider or DEFAULT_ATTACHMENT_CONFIG_PROVIDER
        self._antivirus = antivirus or StubAntivirusScanner()
        self._side_effects: SideEffectRecorder = (
            side_effects or NoOpSideEffectRecorder()
        )
        # When a real recorder is present, share one TX with CAP-011 (commit=False until end).
        self._share_tx = side_effects is not None and not isinstance(
            side_effects, NoOpSideEffectRecorder
        )

    def _cfg(self) -> AttachmentConfig:
        return self._config_provider.get()

    def ensure_staging_token(
        self, staging_token: str | None, *, actor_id: str | None
    ) -> str:
        cfg = self._cfg()
        token = (staging_token or "").strip() or f"STG-{uuid.uuid4().hex}"
        existing = self._repo.get_staging(token)
        if existing is None:
            self._repo.create_staging_session(
                staging_token=token,
                expires_at=datetime.now(UTC)
                + timedelta(hours=cfg.staging_ttl_hours),
                created_by=actor_id,
            )
            self._repo.commit()
            return token
        if existing.status != "OPEN":
            raise ValidationAppError(
                m("staging.token_closed"),
                details={"stagingToken": token, "status": existing.status},
            )
        expires_at = existing.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            raise ValidationAppError(
                m("staging.token_expired"),
                details={"stagingToken": token},
            )
        return token

    def _require_open_complaint(self, complaint_id: str):
        complaint = self._complaints.get(complaint_id.strip())
        if complaint is None:
            raise NotFoundError(m("complaint.not_found"))
        status = (complaint.status or "").strip().upper()
        if status in {"CLOSED", "CANCELLED"}:
            raise ConflictError(
                m("complaint.already_closed"),
                details={"complaintId": complaint.complaint_id, "status": status},
            )
        return complaint

    def _resolve_case_pin(
        self,
        *,
        case_id: str | None,
        complaint_id: str | None,
    ) -> uuid.UUID | None:
        """Optional FR-004 Case pin — Case MUST belong to the bound Complaint."""
        raw = (case_id or "").strip()
        if not raw:
            return None
        complaint = (complaint_id or "").strip()
        if not complaint:
            raise ValidationAppError(
                m("attachment.case_pin_requires_complaint"),
                details={"caseId": raw},
            )
        try:
            case_uuid = uuid.UUID(raw)
        except ValueError:
            raise ValidationAppError(
                m("attachment.case_not_found"),
                details={"caseId": raw},
            ) from None
        case_complaint_id = self._repo.complaint_id_for_case(case_uuid)
        if case_complaint_id is None:
            raise ValidationAppError(
                m("attachment.case_not_found"),
                details={"caseId": raw},
            )
        if case_complaint_id.strip().lower() != complaint.lower():
            raise ValidationAppError(
                m("attachment.case_not_in_complaint"),
                details={"caseId": raw, "complaintId": complaint},
            )
        return case_uuid

    def upload(
        self,
        *,
        data: bytes,
        filename: str | None,
        content_type: str | None,
        classification: str,
        actor_id: str | None,
        staging_token: str | None = None,
        complaint_id: str | None = None,
        customer_id: str | None = None,
        case_id: str | None = None,
        supersedes_attachment_id: str | None = None,
        uploaded_by: uuid.UUID | None = None,
    ) -> Batch1AttachmentResponse:
        cfg = self._cfg()
        classification_clean = (classification or "").strip()
        if classification_clean not in cfg.allowed_classifications:
            raise ValidationAppError(
                m("complaint.classification_not_allowed"),
                details={
                    "classification": classification,
                    "allowed": sorted(cfg.allowed_classifications),
                },
            )

        if not data:
            raise ValidationAppError(m("storage.file_empty"), details={"sizeBytes": 0})
        mime_type = normalize_upload_mime(
            content_type=content_type, filename=filename, data=data
        )
        if mime_type not in cfg.allowed_mime_types:
            raise ValidationAppError(
                m("storage.mime_not_allowed"),
                details={
                    "mimeType": mime_type,
                    "allowed": sorted(cfg.allowed_mime_types),
                },
            )
        if len(data) > cfg.max_file_size_bytes:
            raise ValidationAppError(
                m("storage.file_exceeds_max_size"),
                details={
                    "sizeBytes": len(data),
                    "maxBytes": cfg.max_file_size_bytes,
                },
            )

        safe_name = sanitize_filename(filename)
        if cfg.antivirus_mode == "STUB_ONLY":
            scan = self._antivirus.scan(
                data, mime_type=mime_type, filename=safe_name
            )
            if not scan.clean:
                raise ValidationAppError(
                    m("attachment.security_scan_rejected"),
                    details={"engine": scan.engine, "detail": scan.detail},
                )

        if cfg.checksum_algorithm.upper() != "SHA-256":
            raise ValidationAppError(
                m("attachment.unsupported_checksum_algorithm"),
                details={"checksumAlgorithm": cfg.checksum_algorithm},
            )

        complaint_uuid: uuid.UUID | None = None
        complaint_customer_id: str | None = (customer_id or "").strip() or None
        status = ATTACHMENT_STATUS_STAGED
        token: str | None = None

        if complaint_id and complaint_id.strip():
            complaint = self._require_open_complaint(complaint_id.strip())
            complaint_uuid = uuid.UUID(complaint.complaint_id)
            complaint_customer_id = complaint.customer_id
            status = ATTACHMENT_STATUS_ACTIVE
            aggregate_type = AggregateType.COMPLAINT.value
            aggregate_id = complaint_uuid
        else:
            token = self.ensure_staging_token(staging_token, actor_id=actor_id)
            status = ATTACHMENT_STATUS_STAGED
            aggregate_type = cfg.staging_aggregate_type
            aggregate_id = uuid.uuid5(
                uuid.NAMESPACE_URL, f"cm-batch1-staging:{token}"
            )

        resolved_case_id = self._resolve_case_pin(
            case_id=case_id,
            complaint_id=str(complaint_uuid) if complaint_uuid else None,
        )

        checksum = hashlib.sha256(data).hexdigest()
        if cfg.duplicate_checksum_policy == "REJECT_WITH_EXISTING_REFERENCE":
            # Integrity hash is mandatory (FR-004). Duplicate rejection is scoped
            # to the same customer within the same complaint or staging session —
            # identical bytes for a different customer MUST be allowed.
            prior = self._repo.find_by_checksum(checksum)
            superseding = bool(
                supersedes_attachment_id and supersedes_attachment_id.strip()
            )
            if prior is not None and not superseding:
                complaint_key = (complaint_id or "").strip() or None
                staging_key = (token or staging_token or "").strip() or None
                same_complaint = bool(
                    complaint_key
                    and prior.complaint_id
                    and prior.complaint_id == complaint_key
                )
                same_staging = bool(
                    staging_key
                    and prior.staging_token
                    and prior.staging_token == staging_key
                )
                prior_customer = self._customer_for_attachment(prior)
                same_customer = bool(
                    complaint_customer_id
                    and prior_customer
                    and complaint_customer_id == prior_customer
                )
                reject = False
                if same_complaint:
                    reject = True
                elif same_staging and same_customer:
                    reject = True
                elif (
                    same_staging
                    and not complaint_customer_id
                    and not prior_customer
                ):
                    reject = True
                if reject:
                    raise ConflictError(
                        m("attachment.duplicate_checksum"),
                        details={
                            "checksumSha256": checksum,
                            "existingAttachmentId": prior.id,
                            "existingStatus": prior.status,
                            "customerId": complaint_customer_id,
                        },
                    )

        supersedes_uuid: uuid.UUID | None = None
        prior_batch: Batch1AttachmentRecord | None = None
        if supersedes_attachment_id:
            prior_batch = self._repo.get(supersedes_attachment_id.strip())
            if prior_batch is None:
                raise NotFoundError(m("attachment.superseded_not_found"))
            if prior_batch.status in {ATTACHMENT_STATUS_VOID, ATTACHMENT_STATUS_SUPERSEDED}:
                raise ValidationAppError(
                    m("attachment.cannot_supersede_void"),
                    details={"status": prior_batch.status},
                )
            supersedes_uuid = uuid.UUID(prior_batch.id)

        try:
            platform = self._attachments.upload(
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                filename=safe_name,
                content_type=mime_type,
                data=data,
                uploaded_by=uploaded_by,
                allowed_mime_types=set(cfg.allowed_mime_types),
                max_bytes=cfg.max_file_size_bytes,
                commit=not self._share_tx,
            )
        except Exception:
            raise

        try:
            record = self._repo.upload(
                platform_attachment_id=platform.id,
                status=status,
                classification=classification_clean,
                staging_token=token,
                complaint_id=complaint_uuid,
                customer_id=complaint_customer_id,
                case_id=resolved_case_id,
                original_name=safe_name,
                mime_type=mime_type,
                size_bytes=len(data),
                checksum_sha256=checksum,
                supersedes_id=supersedes_uuid,
                uploaded_by=actor_id,
            )
            self._repo.append_history(
                attachment_id=record.id,
                event_type="AttachmentUploaded",
                from_status=None,
                to_status=status,
                reason=None,
                actor_id=actor_id,
                details=f"platformAttachmentId={platform.id}",
            )
            self._side_effects.record(
                events.attachment_uploaded(
                    attachment_id=record.id,
                    complaint_id=str(complaint_uuid) if complaint_uuid else None,
                    checksum=checksum,
                    actor_id=actor_id,
                    status=status,
                )
            )
            if prior_batch is not None:
                self._repo.supersede(prior_batch.id, successor_id=record.id)
                self._repo.append_history(
                    attachment_id=prior_batch.id,
                    event_type="AttachmentSuperseded",
                    from_status=prior_batch.status,
                    to_status=ATTACHMENT_STATUS_SUPERSEDED,
                    reason="superseded_by_upload",
                    actor_id=actor_id,
                    details=f"successorId={record.id}",
                )
                self._side_effects.record(
                    events.attachment_superseded(
                        attachment_id=record.id,
                        superseded_attachment_id=prior_batch.id,
                        complaint_id=str(complaint_uuid) if complaint_uuid else None,
                        actor_id=actor_id,
                    )
                )
            self._repo.commit()
        except Exception as exc:
            # Failed bind compensation: soft-delete platform row; keep no ACTIVE Batch1.
            try:
                self._attachments.soft_delete(
                    platform.id, commit=not self._share_tx
                )
                if self._share_tx:
                    self._repo.commit()
            except Exception:
                pass
            if complaint_uuid is not None:
                self._complaints.create_later_review_work_item(
                    customer_id=complaint_customer_id or "ATTACHMENT_BIND",
                    reason="attachment_bind_failed",
                    complaint_id=str(complaint_uuid),
                )
                self._complaints.commit()
            raise ValidationAppError(
                m("attachment.metadata_bind_failed"),
                details={"platformAttachmentId": str(platform.id), "error": str(exc)},
            ) from exc

        if complaint_uuid is not None:
            closed = self._complaints.close_later_review_items(
                complaint_id=str(complaint_uuid),
                reason="attachment_bind_failed",
            )
            if closed:
                self._complaints.commit()

        return self._to_response(record)

    def _customer_for_attachment(
        self, row: Batch1AttachmentRecord
    ) -> str | None:
        if row.customer_id and row.customer_id.strip():
            return row.customer_id.strip()
        if row.complaint_id:
            complaint = self._complaints.get(row.complaint_id)
            if complaint is not None and complaint.customer_id:
                return complaint.customer_id
        return None

    def bind_staging_to_complaint(
        self,
        *,
        staging_token: str,
        complaint_id: str,
        actor_id: str | None,
    ) -> list[Batch1AttachmentResponse]:
        """Bind staged evidence to Complaint.

        Missing staging session or zero STAGED rows is a successful no-op —
        attachments are optional at create (FR-004). Later-review E8 applies
        only when staged bytes exist and bind fails.
        """
        session = self._repo.get_staging(staging_token)
        if session is None:
            return []
        if session.status != "OPEN":
            raise ValidationAppError(
                m("staging.token_not_open"),
                details={"status": session.status},
            )
        complaint = self._require_open_complaint(complaint_id)

        rows = self._repo.list_by_staging_token(staging_token)
        staged = [row for row in rows if row.status == ATTACHMENT_STATUS_STAGED]
        if not staged:
            self._repo.close_staging(staging_token, status="BOUND")
            self._repo.commit()
            return []

        results: list[Batch1AttachmentResponse] = []
        for row in staged:
            self._attachments.rebind(
                uuid.UUID(row.platform_attachment_id),
                aggregate_type=AggregateType.COMPLAINT.value,
                aggregate_id=uuid.UUID(complaint_id),
                commit=not self._share_tx,
            )
            updated = self._repo.bind(
                row.id,
                complaint_id=complaint_id,
                status=ATTACHMENT_STATUS_ACTIVE,
                customer_id=complaint.customer_id,
            )
            self._repo.append_history(
                attachment_id=row.id,
                event_type="AttachmentBound",
                from_status=ATTACHMENT_STATUS_STAGED,
                to_status=ATTACHMENT_STATUS_ACTIVE,
                reason="create_commit_bind",
                actor_id=actor_id,
                details=f"complaintId={complaint_id}",
            )
            self._side_effects.record(
                events.attachment_bound(
                    attachment_id=row.id,
                    complaint_id=complaint_id,
                    actor_id=actor_id,
                )
            )
            results.append(self._to_response(updated))
        self._repo.close_staging(staging_token, status="BOUND")
        self._repo.commit()
        if results:
            closed = self._complaints.close_later_review_items(
                complaint_id=complaint_id,
                reason="attachment_bind_failed",
            )
            if closed:
                self._complaints.commit()
        return results

    def transfer(
        self,
        body: TransferAttachmentsRequest,
        *,
        actor_id: str | None,
    ) -> TransferAttachmentsResponse:
        """D-06 — transfer staged evidence to surviving Complaint; never discard.

        Missing staging session is a successful no-op (parity with
        ``bind_staging_to_complaint``): the create/intake FE always mints a
        client-side ``STG-*`` token even when no file was uploaded, so a hard
        404 here broke ``link_existing`` for the common no-attachment path.
        """
        token = body.staging_token.strip()
        surviving = body.surviving_complaint_id.strip()
        session = self._repo.get_staging(token)
        if session is None:
            return TransferAttachmentsResponse(
                stagingToken=token,
                survivingComplaintId=surviving,
                transferredCount=0,
                attachments=[],
                discarded=False,
            )
        complaint = self._complaints.get(surviving)
        if complaint is None:
            raise NotFoundError(m("duplicate.surviving_complaint_not_found"))

        rows = self._repo.list_by_staging_token(token)
        transferred: list[Batch1AttachmentResponse] = []
        for row in rows:
            if row.status in {ATTACHMENT_STATUS_VOID, ATTACHMENT_STATUS_SUPERSEDED}:
                continue
            self._attachments.rebind(
                uuid.UUID(row.platform_attachment_id),
                aggregate_type=AggregateType.COMPLAINT.value,
                aggregate_id=uuid.UUID(surviving),
                commit=not self._share_tx,
            )
            updated = self._repo.transfer(
                row.id,
                complaint_id=surviving,
                status=ATTACHMENT_STATUS_TRANSFERRED,
                customer_id=complaint.customer_id,
            )
            self._repo.append_history(
                attachment_id=row.id,
                event_type="AttachmentTransferred",
                from_status=row.status,
                to_status=ATTACHMENT_STATUS_TRANSFERRED,
                reason="duplicate_redirect_d06",
                actor_id=actor_id,
                details=f"survivingComplaintId={surviving}",
            )
            self._side_effects.record(
                events.attachment_transferred(
                    attachment_id=row.id,
                    staging_token=token,
                    surviving_complaint_id=surviving,
                    actor_id=actor_id,
                )
            )
            transferred.append(self._to_response(updated))

        self._repo.close_staging(token, status="TRANSFERRED")
        self._repo.commit()
        return TransferAttachmentsResponse(
            stagingToken=token,
            survivingComplaintId=surviving,
            transferredCount=len(transferred),
            attachments=transferred,
            discarded=False,
        )

    def list_for_complaint(
        self, complaint_id: str
    ) -> list[Batch1AttachmentResponse]:
        if self._complaints.get(complaint_id) is None:
            raise NotFoundError(m("complaint.not_found"))
        return [self._to_response(r) for r in self._repo.list_by_complaint(complaint_id)]

    def get(self, attachment_id: str) -> Batch1AttachmentResponse:
        row = self._repo.get(attachment_id)
        if row is None:
            raise NotFoundError(m("attachment.not_found"))
        return self._to_response(row)

    def try_get(
        self, attachment_id: str
    ) -> Batch1AttachmentResponse | None:
        row = self._repo.get(attachment_id)
        return self._to_response(row) if row is not None else None

    def try_get_by_platform_id(
        self, platform_attachment_id: uuid.UUID
    ) -> Batch1AttachmentResponse | None:
        row = self._repo.get_by_platform_id(platform_attachment_id)
        return self._to_response(row) if row is not None else None

    def resolve_platform_attachment_id(
        self, attachment_id: uuid.UUID
    ) -> uuid.UUID:
        """Map Batch 1 id or platform id to CAP-011 attachment id."""
        by_platform = self._repo.get_by_platform_id(attachment_id)
        if by_platform is not None:
            return attachment_id
        by_batch = self._repo.get(str(attachment_id))
        if by_batch is not None:
            return uuid.UUID(by_batch.platform_attachment_id)
        return attachment_id

    def void(
        self,
        attachment_id: str,
        *,
        reason: str,
        actor_id: str | None,
        is_admin: bool = False,
    ) -> Batch1AttachmentResponse:
        reason_clean = (reason or "").strip()
        if not reason_clean:
            raise ValidationAppError(
                m("attachment.void_reason_required"),
                details={"attachmentId": attachment_id},
            )
        row = self._repo.get(attachment_id)
        if row is None:
            raise NotFoundError(m("attachment.not_found"))
        if row.status == ATTACHMENT_STATUS_VOID:
            raise ConflictError(
                m("attachment.already_void"),
                details={"attachmentId": attachment_id},
            )
        if row.complaint_id:
            self._require_open_complaint(str(row.complaint_id))
        self._assert_can_void(row, actor_id=actor_id, is_admin=is_admin)
        self._attachments.soft_delete(
            uuid.UUID(row.platform_attachment_id), commit=not self._share_tx
        )
        updated = self._repo.void(attachment_id, reason=reason_clean)
        self._repo.append_history(
            attachment_id=attachment_id,
            event_type="AttachmentVoided",
            from_status=row.status,
            to_status=ATTACHMENT_STATUS_VOID,
            reason=reason_clean,
            actor_id=actor_id,
        )
        self._side_effects.record(
            events.attachment_voided(
                attachment_id=attachment_id,
                reason=reason_clean,
                complaint_id=row.complaint_id,
                actor_id=actor_id,
            )
        )
        self._repo.commit()
        return self._to_response(updated)

    def _assert_can_void(
        self,
        row: Batch1AttachmentRecord,
        *,
        actor_id: str | None,
        is_admin: bool,
    ) -> None:
        """Uploader, complaint creator, or admin may void; others are denied."""
        if is_admin:
            return
        actor = (actor_id or "").strip()
        if not actor:
            raise PermissionDeniedError(
                m("attachment.void_forbidden"),
                details={"attachmentId": row.id},
            )
        if (row.uploaded_by or "").strip() == actor:
            return
        if row.complaint_id:
            complaint = self._complaints.get(str(row.complaint_id))
            if complaint is not None and (complaint.created_by or "").strip() == actor:
                return
        if row.staging_token:
            staging = self._repo.get_staging(row.staging_token)
            if staging is not None and (staging.created_by or "").strip() == actor:
                return
        raise PermissionDeniedError(
            m("attachment.void_forbidden"),
            details={"attachmentId": row.id},
        )

    def void_abandoned_staging(self, *, actor_id: str | None = "system") -> int:
        cfg = self._cfg()
        if cfg.abandoned_staging_action != "VOID":
            logger.info(
                "abandoned staging cleanup skipped action=%s",
                cfg.abandoned_staging_action,
            )
            return 0
        expired = self._repo.list_expired_open_staging(now=datetime.now(UTC))
        count = 0
        for session in expired:
            for row in self._repo.list_by_staging_token(session.staging_token):
                if row.status == ATTACHMENT_STATUS_STAGED:
                    self._attachments.soft_delete(
                        uuid.UUID(row.platform_attachment_id),
                        commit=not self._share_tx,
                    )
                    self._repo.void(row.id, reason="abandoned_staging_ttl")
                    self._repo.append_history(
                        attachment_id=row.id,
                        event_type="AttachmentVoided",
                        from_status=ATTACHMENT_STATUS_STAGED,
                        to_status=ATTACHMENT_STATUS_VOID,
                        reason="abandoned_staging_ttl",
                        actor_id=actor_id,
                    )
                    self._side_effects.record(
                        events.attachment_voided(
                            attachment_id=row.id,
                            reason="abandoned_staging_ttl",
                            complaint_id=None,
                            actor_id=actor_id,
                        )
                    )
                    count += 1
            self._repo.close_staging(session.staging_token, status="ABANDONED")
        if expired:
            self._repo.commit()
        logger.info(
            "abandoned staging cleanup complete "
            "expiredSessions=%s voidedAttachments=%s actorId=%s ttlHours=%s",
            len(expired),
            count,
            actor_id,
            cfg.staging_ttl_hours,
        )
        return count

    def history(self, attachment_id: str) -> list[dict]:
        if self._repo.get(attachment_id) is None:
            raise NotFoundError(m("attachment.not_found"))
        return [
            {
                "id": h.id,
                "eventType": h.event_type,
                "fromStatus": h.from_status,
                "toStatus": h.to_status,
                "reason": h.reason,
                "actorId": h.actor_id,
                "createdAt": h.created_at.isoformat(),
            }
            for h in self._repo.history(attachment_id)
        ]

    @staticmethod
    def _to_response(row: Batch1AttachmentRecord) -> Batch1AttachmentResponse:
        return Batch1AttachmentResponse(
            attachmentId=row.id,
            platformAttachmentId=row.platform_attachment_id,
            status=row.status,  # type: ignore[arg-type]
            classification=row.classification,
            stagingToken=row.staging_token,
            complaintId=row.complaint_id,
            customerId=row.customer_id,
            caseId=row.case_id,
            originalName=row.original_name or "",
            mimeType=row.mime_type or "",
            sizeBytes=row.size_bytes or 0,
            checksumSha256=row.checksum_sha256 or "",
            supersedesId=row.supersedes_id,
            voidReason=row.void_reason,
            createdAt=row.created_at,
        )

"""OrgUnitResolver — single resource → organization-unit lookup (SECMIG-P4).

Endpoints must not implement ad-hoc org lookup. All G1 org binding goes through
this component. No database schema redesign: Complaint uses ``Branch.code``;
CM Batch 1 uses ``recordingUnitId`` recorded on ``ComplaintCreated`` outbox
payload (JSON), or a declared unit supplied at create time.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.models import Branch, Complaint
from app.modules.cm_batch1.models import CmBatch1ComplaintORM, CmBatch1OutboxORM


class OrgUnitResolver:
    """Resolve the organization unit id for a protected resource."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def normalize(value: str | None) -> str | None:
        cleaned = (value or "").strip()
        return cleaned or None

    def resolve_declared(self, org_unit_id: str | None) -> str | None:
        """Normalize a caller-/body-declared organization unit (create path)."""
        return self.normalize(org_unit_id)

    def resolve_complaint(self, complaint_id: uuid.UUID) -> str | None:
        """Map legacy Complaint → Branch.code (org unit key)."""
        row = self._session.get(Complaint, complaint_id)
        if row is None or row.deleted_at is not None:
            raise NotFoundError(m("complaint.not_found"))
        if row.branch_id is None:
            return None
        branch = self._session.get(Branch, row.branch_id)
        if branch is None or branch.deleted_at is not None:
            return None
        return self.normalize(branch.code)

    def resolve_cm_complaint(self, complaint_id: str | uuid.UUID) -> str | None:
        """Map CM Batch 1 complaint → recordingUnitId from ComplaintCreated outbox."""
        aggregate_id = str(complaint_id).strip()
        if not aggregate_id:
            raise NotFoundError(m("complaint.not_found"))

        row: CmBatch1ComplaintORM | None = None
        try:
            row = self._session.get(CmBatch1ComplaintORM, uuid.UUID(aggregate_id))
        except ValueError:
            row = None
        if row is None:
            raise NotFoundError(m("complaint.not_found"))

        stmt = (
            select(CmBatch1OutboxORM.payload_json)
            .where(
                CmBatch1OutboxORM.aggregate_type == "Complaint",
                CmBatch1OutboxORM.aggregate_id == str(row.id),
                CmBatch1OutboxORM.event_name == "ComplaintCreated",
            )
            .order_by(CmBatch1OutboxORM.created_at.desc())
            .limit(1)
        )
        payload_json = self._session.scalar(stmt)
        if not payload_json:
            return None
        try:
            payload: dict[str, Any] = json.loads(payload_json)
        except (TypeError, json.JSONDecodeError):
            return None
        return self.normalize(
            _as_optional_str(payload.get("recordingUnitId"))
            or _as_optional_str(payload.get("recording_unit_id"))
            or _as_optional_str(payload.get("orgUnitId"))
            or _as_optional_str(payload.get("org_unit_id"))
        )


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

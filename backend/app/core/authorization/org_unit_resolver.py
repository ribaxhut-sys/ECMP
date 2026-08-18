"""OrgUnitResolver — single resource → organization-unit lookup (SECMIG-P4).

Endpoints must not implement ad-hoc org lookup. All G1 org binding goes through
this component. Complaint uses ``Branch.code``; CM Batch 1 prefers column
``owning_unit_id``, falling back to ``recordingUnitId`` on ``ComplaintCreated``
outbox payload (JSON) for rows created before the column existed.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.models import Branch, User
from app.modules.cm_batch1.models import CmBatch1ComplaintORM, CmBatch1OutboxORM

if TYPE_CHECKING:
    from app.core.authorization.principal import Principal
from app.modules.cm_case.infrastructure.orm import CmCaseORM


@dataclass(frozen=True, slots=True)
class CaseOrgUnits:
    """CAP-008 Case org binding: immutable Owner vs mutable Handling Unit."""

    handling_unit_id: str | None
    owner_unit_id: str | None
    complaint_id: str | None = None


class OrgUnitResolver:
    """Resolve the organization unit id for a protected resource."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def normalize(value: str | None) -> str | None:
        cleaned = (value or "").strip()
        return cleaned or None

    def resolve_declared(self, org_unit_id: str | None) -> str | None:
        """Normalize a caller-/body-declared organization unit (create path).

        Lab FE historically sent ``Branch.id`` (UUID) as ``recordingUnitId``.
        Canonical org key is ``Branch.code`` (e.g. ``PUSAT``, ``UPPPD-…``) —
        resolve UUID → code when the id matches an active branch.
        """
        cleaned = self.normalize(org_unit_id)
        if not cleaned:
            return None
        try:
            branch_uuid = uuid.UUID(cleaned)
        except ValueError:
            return cleaned
        branch = self._session.get(Branch, branch_uuid)
        if branch is None or branch.deleted_at is not None:
            return cleaned
        return self.normalize(branch.code)

    def resolve_complaint(self, complaint_id: uuid.UUID) -> str | None:
        """Legacy Foundation Complaint org lookup (DEC-026 / Alembic 0072).

        Tables ``complaints`` / ``complaint_escalations`` are DROP. Callers
        (attachment download, unmounted routers) must treat this as not-found
        — do not query the retired models (UndefinedTable).
        """
        _ = complaint_id
        raise NotFoundError(m("complaint.not_found"))

    def resolve_user(self, user_id: uuid.UUID) -> str | None:
        """Map ECMP User membership → Branch.code (org unit key, UM-SEC-001)."""
        row = self._session.get(User, user_id)
        if row is None or row.deleted_at is not None:
            raise NotFoundError(m("user.not_found"))
        if row.branch_id is None:
            return None
        branch = self._session.get(Branch, row.branch_id)
        if branch is None or branch.deleted_at is not None:
            return None
        return self.normalize(branch.code)

    def resolve_principal_membership(self, principal_user_id: uuid.UUID) -> str | None:
        """Map the *acting* principal's own User row → Branch.code (UM-BUG-005).

        Dev mode (``ECMP_AUTH_MODE=dev``) issues no ``orgUnitId`` claim — there
        is no Enterprise SSO token to carry one — so ``Principal.org_unit_id``
        is always empty there. This falls back to the ECMP-owned membership
        record so branch-scoped roles still see only their own unit locally,
        the same domain rule Mode B enforces via the claim. Fails open (None)
        rather than raising, matching the existing head-office/no-branch gap
        handling — this is a fallback lookup, not a resource guard.
        """
        try:
            return self.resolve_user(principal_user_id)
        except NotFoundError:
            return None

    def resolve_principal(self, principal: Principal) -> str | None:
        """Effective org unit for the acting principal — claim first, membership
        fallback (see ``resolve_principal_membership``). Every endpoint that
        needs "what unit is this caller in" (not "what unit owns this
        resource") should go through this, not read ``principal.org_unit_id``
        directly — that claim is empty in Mode A dev auth.
        """
        claimed = self.normalize(principal.org_unit_id)
        if claimed:
            return claimed
        try:
            return self.resolve_principal_membership(principal.user_id)
        except Exception:
            return None

    def resolve_cm_complaint(self, complaint_id: str | uuid.UUID) -> str | None:
        """Map CM Batch 1 complaint → owning_unit_id (column), else outbox JSON."""
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

        from_column = self.normalize(row.owning_unit_id)
        if from_column:
            return from_column

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

    def _load_case_row(self, case_id: str) -> CmCaseORM:
        """Load Case ORM by id or case_number (repository get parity)."""
        key = (case_id or "").strip()
        if not key:
            raise NotFoundError("Case does not exist.")
        row: CmCaseORM | None = None
        try:
            row = self._session.get(CmCaseORM, uuid.UUID(key))
        except ValueError:
            row = None
        if row is None:
            row = self._session.scalar(
                select(CmCaseORM).where(CmCaseORM.case_number == key)
            )
        if row is None:
            raise NotFoundError("Case does not exist.")
        return row

    def resolve_case(self, case_id: str) -> str | None:
        """Map CAP-008 Case (Aggregate) → current handling unit (owning_unit_id).

        Handling mutations (status / resolve / transfer) still bind to this
        unit. For Owner+Handling read access use ``resolve_case_units``.
        """
        row = self._load_case_row(case_id)
        return self.normalize(row.owning_unit_id)

    def resolve_case_units(self, case_id: str) -> CaseOrgUnits:
        """Map CAP-008 Case → Owner unit + current Handling unit (F4)."""
        row = self._load_case_row(case_id)
        return CaseOrgUnits(
            handling_unit_id=self.normalize(row.owning_unit_id),
            owner_unit_id=self.normalize(row.owner_unit_id),
            complaint_id=(row.complaint_id or "").strip() or None,
        )

    def resolve_escalation(self, escalation_id: uuid.UUID) -> str | None:
        """Legacy Foundation escalation org lookup (DEC-026 / Alembic 0072)."""
        _ = escalation_id
        raise NotFoundError(m("escalation.not_found"))


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

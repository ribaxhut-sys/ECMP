"""Persistent repository for CM Batch 1 Aggregate (S2 Task 01)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.cm_batch1.entities import ComplaintAggregate, DuplicateDecisionRecord
from app.modules.cm_batch1.models import (
    CmBatch1ChannelMessageORM,
    CmBatch1ComplaintORM,
    CmBatch1CustomerLockORM,
    CmBatch1DuplicateDecisionORM,
    CmBatch1IdempotencyORM,
    CmBatch1LaterReviewItemORM,
    CmBatch1NumberCounterORM,
)

_COUNTER_NAME = "complaint_number"


def _to_entity(row: CmBatch1ComplaintORM) -> ComplaintAggregate:
    return ComplaintAggregate(
        complaint_id=str(row.id),
        complaint_number=row.complaint_number,
        customer_id=row.customer_id,
        category=row.category,
        channel=row.channel,
        subject=row.subject,
        description=row.description,
        priority=row.priority,
        status=row.status,
        created_at=row.created_at,
        created_by=row.created_by,
        case_created=False,
    )


class CmBatch1Repository:
    """SQLAlchemy-backed Aggregate + idempotency store."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def confirm(self, principal_key: str, customer_id: str) -> None:
        row = self._session.scalar(
            select(CmBatch1CustomerLockORM).where(
                CmBatch1CustomerLockORM.principal_key == principal_key
            )
        )
        if row is None:
            self._session.add(
                CmBatch1CustomerLockORM(
                    principal_key=principal_key,
                    customer_id=customer_id,
                    locked_at=datetime.now(UTC),
                )
            )
        else:
            row.customer_id = customer_id
            row.locked_at = datetime.now(UTC)
        self._session.flush()

    def get_confirmed(self, principal_key: str) -> str | None:
        row = self._session.scalar(
            select(CmBatch1CustomerLockORM).where(
                CmBatch1CustomerLockORM.principal_key == principal_key
            )
        )
        return row.customer_id if row is not None else None

    def get_idempotent(self, request_id: str) -> ComplaintAggregate | None:
        rec = self._session.scalar(
            select(CmBatch1IdempotencyORM).where(
                CmBatch1IdempotencyORM.request_id == request_id
            )
        )
        if rec is None:
            return None
        return self.get(str(rec.complaint_id))

    def get_by_channel_message(self, message_id: str) -> ComplaintAggregate | None:
        rec = self._session.scalar(
            select(CmBatch1ChannelMessageORM).where(
                CmBatch1ChannelMessageORM.channel_message_id == message_id
            )
        )
        if rec is None:
            return None
        return self.get(str(rec.complaint_id))

    def get(self, complaint_id: str) -> ComplaintAggregate | None:
        try:
            cid = uuid.UUID(complaint_id)
        except ValueError:
            return None
        row = self._session.get(CmBatch1ComplaintORM, cid)
        return _to_entity(row) if row is not None else None

    def list_active_for_customer(self, customer_id: str) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .where(CmBatch1ComplaintORM.status != "CLOSED")
            .order_by(CmBatch1ComplaintORM.created_at.asc())
        ).all()
        return [_to_entity(r) for r in rows]

    def _next_complaint_number(self) -> str:
        row = self._session.scalar(
            select(CmBatch1NumberCounterORM)
            .where(CmBatch1NumberCounterORM.name == _COUNTER_NAME)
            .with_for_update()
        )
        if row is None:
            row = CmBatch1NumberCounterORM(name=_COUNTER_NAME, value=0)
            self._session.add(row)
            self._session.flush()
            row = self._session.scalar(
                select(CmBatch1NumberCounterORM)
                .where(CmBatch1NumberCounterORM.name == _COUNTER_NAME)
                .with_for_update()
            )
            assert row is not None
        row.value += 1
        self._session.flush()
        return f"CM-{row.value:08d}"

    def create(
        self,
        *,
        customer_id: str,
        category: str,
        channel: str,
        subject: str,
        description: str,
        priority: str,
        created_by: str | None,
        request_id: str,
        channel_message_id: str | None,
    ) -> tuple[ComplaintAggregate, bool]:
        """Return ``(aggregate, created)`` — ``created=False`` on idempotent replay."""
        existing = self.get_idempotent(request_id)
        if existing is not None:
            return existing, False
        if channel_message_id:
            existing_ch = self.get_by_channel_message(channel_message_id)
            if existing_ch is not None:
                return existing_ch, False

        complaint_id = uuid.uuid4()
        complaint_number = self._next_complaint_number()
        orm = CmBatch1ComplaintORM(
            id=complaint_id,
            complaint_number=complaint_number,
            customer_id=customer_id,
            category=category,
            channel=channel,
            subject=subject,
            description=description,
            priority=priority,
            status="REGISTERED",
            case_created=False,
            created_by=created_by,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self._session.add(orm)
        self._session.add(
            CmBatch1IdempotencyORM(
                request_id=request_id,
                complaint_id=complaint_id,
                created_at=datetime.now(UTC),
            )
        )
        if channel_message_id:
            self._session.add(
                CmBatch1ChannelMessageORM(
                    channel_message_id=channel_message_id,
                    complaint_id=complaint_id,
                    created_at=datetime.now(UTC),
                )
            )
        try:
            self._session.flush()
        except IntegrityError:
            self._session.rollback()
            replay = self.get_idempotent(request_id)
            if replay is not None:
                return replay, False
            if channel_message_id:
                replay_ch = self.get_by_channel_message(channel_message_id)
                if replay_ch is not None:
                    return replay_ch, False
            raise

        return _to_entity(orm), True

    def find_duplicate_candidates(
        self,
        *,
        customer_id: str,
        since: datetime,
        limit: int,
    ) -> list[ComplaintAggregate]:
        rows = self._session.scalars(
            select(CmBatch1ComplaintORM)
            .where(CmBatch1ComplaintORM.customer_id == customer_id)
            .where(CmBatch1ComplaintORM.created_at >= since)
            .order_by(CmBatch1ComplaintORM.created_at.desc())
            .limit(limit)
        ).all()
        return [_to_entity(r) for r in rows]

    def save_duplicate_decision(
        self,
        *,
        customer_id: str,
        decision: str,
        surviving_complaint_id: str | None,
        source_complaint_id: str | None,
        justification: str | None,
        staging_token: str | None,
        warning: bool,
        hard_block: bool,
        policy_version: str,
        candidate_snapshot: str | None,
        actor_id: str | None,
        later_review_work_item_id: str | None,
    ) -> DuplicateDecisionRecord:
        decision_id = uuid.uuid4()
        surviving_uuid = (
            uuid.UUID(surviving_complaint_id) if surviving_complaint_id else None
        )
        source_uuid = uuid.UUID(source_complaint_id) if source_complaint_id else None
        created_at = datetime.now(UTC)
        orm = CmBatch1DuplicateDecisionORM(
            id=decision_id,
            customer_id=customer_id,
            decision=decision,
            surviving_complaint_id=surviving_uuid,
            source_complaint_id=source_uuid,
            justification=justification,
            staging_token=staging_token,
            warning=warning,
            hard_block=hard_block,
            policy_version=policy_version,
            candidate_snapshot=candidate_snapshot,
            actor_id=actor_id,
            later_review_work_item_id=later_review_work_item_id,
            case_created=False,
            created_at=created_at,
        )
        self._session.add(orm)
        self._session.flush()
        return DuplicateDecisionRecord(
            decision_id=str(decision_id),
            customer_id=customer_id,
            decision=decision,
            surviving_complaint_id=surviving_complaint_id,
            source_complaint_id=source_complaint_id,
            justification=justification,
            staging_token=staging_token,
            warning=warning,
            hard_block=hard_block,
            policy_version=policy_version,
            candidate_snapshot=candidate_snapshot,
            actor_id=actor_id,
            later_review_work_item_id=later_review_work_item_id,
            created_at=created_at,
            case_created=False,
        )

    def get_duplicate_history(
        self, *, customer_id: str, limit: int = 50
    ) -> list[DuplicateDecisionRecord]:
        rows = self._session.scalars(
            select(CmBatch1DuplicateDecisionORM)
            .where(CmBatch1DuplicateDecisionORM.customer_id == customer_id)
            .order_by(CmBatch1DuplicateDecisionORM.created_at.desc())
            .limit(limit)
        ).all()
        return [
            DuplicateDecisionRecord(
                decision_id=str(r.id),
                customer_id=r.customer_id,
                decision=r.decision,
                surviving_complaint_id=(
                    str(r.surviving_complaint_id)
                    if r.surviving_complaint_id is not None
                    else None
                ),
                source_complaint_id=(
                    str(r.source_complaint_id)
                    if r.source_complaint_id is not None
                    else None
                ),
                justification=r.justification,
                staging_token=r.staging_token,
                warning=r.warning,
                hard_block=r.hard_block,
                policy_version=r.policy_version,
                candidate_snapshot=r.candidate_snapshot,
                actor_id=r.actor_id,
                later_review_work_item_id=r.later_review_work_item_id,
                created_at=r.created_at,
                case_created=False,
            )
            for r in rows
        ]

    def create_later_review_work_item(
        self, *, customer_id: str, reason: str
    ) -> str:
        work_item_id = f"LR-{uuid.uuid4().hex[:12].upper()}"
        self._session.add(
            CmBatch1LaterReviewItemORM(
                id=uuid.uuid4(),
                work_item_id=work_item_id,
                customer_id=customer_id,
                reason=reason,
                status="OPEN",
                created_at=datetime.now(UTC),
            )
        )
        self._session.flush()
        return work_item_id

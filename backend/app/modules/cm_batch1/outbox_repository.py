"""Outbox repository for CM Batch 1 (persist-only EVT-CM-*)."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.cm_batch1.models import CmBatch1OutboxORM


@dataclass
class OutboxRecord:
    id: str
    event_id: str
    event_name: str
    aggregate_type: str
    aggregate_id: str | None
    idempotency_key: str
    payload: dict[str, Any]
    status: str
    occurred_at: datetime


class OutboxRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def exists_idempotency_key(self, key: str) -> bool:
        row = self._session.scalar(
            select(CmBatch1OutboxORM.id).where(
                CmBatch1OutboxORM.idempotency_key == key
            )
        )
        return row is not None

    def enqueue(
        self,
        *,
        event_id: str,
        event_name: str,
        aggregate_type: str,
        aggregate_id: str | None,
        idempotency_key: str,
        payload: dict[str, Any],
        occurred_at: datetime | None = None,
    ) -> OutboxRecord | None:
        """Insert unpublished outbox row. Returns None when idempotent duplicate."""
        if self.exists_idempotency_key(idempotency_key):
            return None
        now = occurred_at or datetime.now(UTC)
        row_id = uuid.uuid4()
        orm = CmBatch1OutboxORM(
            id=row_id,
            event_id=event_id,
            event_name=event_name,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            idempotency_key=idempotency_key,
            payload_json=json.dumps(payload, default=str),
            status="UNPUBLISHED",
            occurred_at=now,
            created_at=datetime.now(UTC),
            published_at=None,
        )
        try:
            with self._session.begin_nested():
                self._session.add(orm)
                self._session.flush()
        except IntegrityError:
            return None
        return OutboxRecord(
            id=str(row_id),
            event_id=event_id,
            event_name=event_name,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            idempotency_key=idempotency_key,
            payload=payload,
            status="UNPUBLISHED",
            occurred_at=now,
        )

    def list_unpublished(self, *, limit: int = 100) -> list[OutboxRecord]:
        rows = self._session.scalars(
            select(CmBatch1OutboxORM)
            .where(CmBatch1OutboxORM.status == "UNPUBLISHED")
            .where(CmBatch1OutboxORM.event_id.like("EVT-%"))
            .order_by(CmBatch1OutboxORM.occurred_at.asc())
            .limit(limit)
        ).all()
        return [
            OutboxRecord(
                id=str(r.id),
                event_id=r.event_id,
                event_name=r.event_name,
                aggregate_type=r.aggregate_type,
                aggregate_id=r.aggregate_id,
                idempotency_key=r.idempotency_key,
                payload=json.loads(r.payload_json),
                status=r.status,
                occurred_at=r.occurred_at,
            )
            for r in rows
        ]

    def list_by_aggregate(
        self, *, aggregate_type: str, aggregate_id: str
    ) -> list[OutboxRecord]:
        rows = self._session.scalars(
            select(CmBatch1OutboxORM)
            .where(CmBatch1OutboxORM.aggregate_type == aggregate_type)
            .where(CmBatch1OutboxORM.aggregate_id == aggregate_id)
            .order_by(CmBatch1OutboxORM.occurred_at.asc())
        ).all()
        return [
            OutboxRecord(
                id=str(r.id),
                event_id=r.event_id,
                event_name=r.event_name,
                aggregate_type=r.aggregate_type,
                aggregate_id=r.aggregate_id,
                idempotency_key=r.idempotency_key,
                payload=json.loads(r.payload_json),
                status=r.status,
                occurred_at=r.occurred_at,
            )
            for r in rows
        ]

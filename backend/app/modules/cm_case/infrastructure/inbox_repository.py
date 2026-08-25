"""Case inbox receipts (Cabang unread) + Pusat queue read receipts.

Both sidebar badges live here. Cabang counts unread Cases from receipt rows;
Pusat counts queue rows it has not opened yet (see ``cm_pusat_queue_seen``).
Fail-open: writers never raise into the domain transaction. Badge readers
return 0 on error so navigation stays up.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cm_case.infrastructure.orm import CmCaseInboxReceiptORM, CmCaseORM

logger = logging.getLogger(__name__)

REASON_RETURNED = "RETURNED"
REASON_HQ_SCHEDULED = "HQ_SCHEDULED"
ALLOWED_REASONS = frozenset({REASON_RETURNED, REASON_HQ_SCHEDULED})

_TERMINAL_CASE = frozenset({"CLOSED", "CANCELLED", "RESOLVED"})
_CLOSED_COMPLAINT = "CLOSED"
_ESCALATE_APPROVED = "ESCALATE_APPROVED"
_HQ_SCHEDULED = "HQ_SCHEDULED"


def _norm(value: str | None) -> str:
    return (value or "").strip()


def _ids_match(left: str | None, right: str | None) -> bool:
    a = _norm(left)
    b = _norm(right)
    if not a or not b:
        return False
    if a.casefold() == b.casefold():
        return True
    try:
        return str(UUID(a)) == str(UUID(b))
    except ValueError:
        return False


def _parse_case_id(case_id: str) -> UUID | None:
    try:
        return UUID(str(case_id).strip())
    except ValueError:
        return None


class CaseInboxRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def mark_unread(self, case_id: str, user_id: str, reason: str) -> None:
        cid = _parse_case_id(case_id)
        uid = _norm(user_id)
        why = _norm(reason).upper()
        if cid is None or not uid or why not in ALLOWED_REASONS:
            return
        now = datetime.now(UTC)
        row = self._session.scalar(
            select(CmCaseInboxReceiptORM).where(
                CmCaseInboxReceiptORM.case_id == cid,
                CmCaseInboxReceiptORM.user_id == uid,
            )
        )
        if row is None:
            self._session.add(
                CmCaseInboxReceiptORM(
                    case_id=cid,
                    user_id=uid,
                    reason=why,
                    event_at=now,
                    read_at=None,
                )
            )
        else:
            row.reason = why
            row.event_at = now
            row.read_at = None
        self._session.flush()

    def mark_read(self, case_id: str, user_id: str) -> None:
        cid = _parse_case_id(case_id)
        uid = _norm(user_id)
        if cid is None or not uid:
            return
        row = self._session.scalar(
            select(CmCaseInboxReceiptORM).where(
                CmCaseInboxReceiptORM.case_id == cid,
                CmCaseInboxReceiptORM.user_id == uid,
            )
        )
        if row is None or row.read_at is not None:
            return
        row.read_at = datetime.now(UTC)
        self._session.flush()

    def mark_read_all_under_complaint(self, complaint_id: str, user_id: str) -> None:
        """Cabang opened the parent — every Case receipt for this user is read."""
        uid = _norm(user_id)
        cid = _norm(complaint_id)
        if not uid or not cid:
            return
        rows = list(
            self._session.scalars(
                select(CmCaseORM).where(CmCaseORM.complaint_id == cid)
            )
        )
        for row in rows:
            self.mark_read(str(row.id), uid)

    def count_unread(self, user_id: str) -> int:
        uid = _norm(user_id)
        if not uid:
            return 0
        rows = list(
            self._session.scalars(
                select(CmCaseInboxReceiptORM).where(
                    CmCaseInboxReceiptORM.user_id == uid,
                    CmCaseInboxReceiptORM.read_at.is_(None),
                )
            )
        )
        return len(rows)

    def unread_map(
        self, user_id: str, case_ids: list[str]
    ) -> dict[str, str]:
        """case_id -> unread reason for this user."""
        uid = _norm(user_id)
        ids = [_parse_case_id(i) for i in case_ids]
        parsed = [i for i in ids if i is not None]
        if not uid or not parsed:
            return {}
        rows = list(
            self._session.scalars(
                select(CmCaseInboxReceiptORM).where(
                    CmCaseInboxReceiptORM.user_id == uid,
                    CmCaseInboxReceiptORM.case_id.in_(parsed),
                    CmCaseInboxReceiptORM.read_at.is_(None),
                )
            )
        )
        return {str(row.case_id): row.reason for row in rows}

    def list_case_creators(self, complaint_id: str) -> list[tuple[str, str]]:
        cid = _norm(complaint_id)
        if not cid:
            return []
        rows = list(
            self._session.scalars(
                select(CmCaseORM).where(CmCaseORM.complaint_id == cid)
            )
        )
        out: list[tuple[str, str]] = []
        for row in rows:
            creator = _norm(row.created_by)
            if creator:
                out.append((str(row.id), creator))
        return out

    def count_pusat_queue_unread(self, user_id: str) -> int:
        """Queue rows this Pusat user has not opened yet.

        Delegates to the complaint repository so the badge and the
        ``?needsPusatHandling=1`` list share one definition of the queue —
        counting them separately is exactly how they drifted apart before.
        """
        from app.modules.cm_batch1.repository import CmBatch1Repository

        return CmBatch1Repository(self._session).count_pusat_queue_unread(user_id)

    def count_pusat_follow_up_unread(self, user_id: str) -> int:
        from app.modules.cm_batch1.repository import CmBatch1Repository

        return CmBatch1Repository(self._session).count_pusat_follow_up_unread(
            user_id
        )

    def mark_pusat_queue_seen(self, complaint_id: str, user_id: str) -> None:
        """Record that this Pusat user opened the parent (badge read receipt)."""
        from app.modules.cm_batch1.repository import CmBatch1Repository

        CmBatch1Repository(self._session).mark_pusat_queue_seen(
            complaint_id, user_id
        )


def safe_mark_unread(
    session: Session | None,
    *,
    case_id: str,
    user_id: str,
    reason: str,
    actor_id: str | None,
) -> None:
    if session is None:
        return
    if _ids_match(user_id, actor_id):
        return
    try:
        with session.begin_nested():
            CaseInboxRepository(session).mark_unread(case_id, user_id, reason)
    except Exception:
        logger.exception("case inbox unread write failed")


def safe_mark_read(session: Session | None, *, case_id: str, user_id: str) -> None:
    if session is None:
        return
    try:
        with session.begin_nested():
            CaseInboxRepository(session).mark_read(case_id, user_id)
    except Exception:
        logger.exception("case inbox mark-read failed")


def safe_mark_cases_read_for_complaint(
    session: Session | None,
    *,
    complaint_id: str,
    user_id: str,
    actor_is_pusat: bool,
) -> None:
    """Cabang opened the parent complaint — Case inbox receipts clear."""
    if session is None or actor_is_pusat:
        return
    try:
        with session.begin_nested():
            CaseInboxRepository(session).mark_read_all_under_complaint(
                complaint_id, user_id
            )
    except Exception:
        logger.exception("case inbox parent mark-read failed")


def notify_complaint_case_creators(
    session: Session | None,
    *,
    complaint_id: str,
    actor_id: str | None,
    reason: str,
) -> None:
    if session is None:
        return
    try:
        with session.begin_nested():
            repo = CaseInboxRepository(session)
            for case_id, creator in repo.list_case_creators(complaint_id):
                if _ids_match(creator, actor_id):
                    continue
                repo.mark_unread(case_id, creator, reason)
    except Exception:
        logger.exception("case inbox notify-creators failed")


def safe_mark_pusat_queue_seen(
    session: Session | None,
    *,
    complaint_id: str,
    user_id: str,
    actor_is_pusat: bool,
) -> None:
    """Pusat opened this parent — its badge row stops counting for that user."""
    if session is None or not actor_is_pusat:
        return
    try:
        with session.begin_nested():
            CaseInboxRepository(session).mark_pusat_queue_seen(
                complaint_id, user_id
            )
    except Exception:
        logger.exception("pusat queue seen write failed")


def safe_work_badge_counts(
    session: Session | None,
    *,
    actor_id: str,
    actor_is_pusat: bool,
) -> tuple[int, int, int]:
    if session is None:
        return 0, 0, 0
    try:
        repo = CaseInboxRepository(session)
        unread = 0 if actor_is_pusat else repo.count_unread(actor_id)
        queue = repo.count_pusat_queue_unread(actor_id) if actor_is_pusat else 0
        follow_up = (
            repo.count_pusat_follow_up_unread(actor_id) if actor_is_pusat else 0
        )
        return unread, queue, follow_up
    except Exception:
        logger.exception("case inbox badge count failed")
        return 0, 0, 0


def complaint_needs_pusat_handling(
    *,
    status: str | None,
    intake_disposition: str | None,
    hq_accepted_at: object | None,
    cases: list[object],
) -> bool:
    if _norm(status).upper() == _CLOSED_COMPLAINT:
        return False
    if hq_accepted_at is not None:
        return False
    if _norm(intake_disposition).upper() == _HQ_SCHEDULED:
        return False
    for raw in cases:
        escalated = bool(getattr(raw, "escalated_to_pusat", False))
        claimed = _norm(getattr(raw, "handling_claimed_by", None))
        case_status = _norm(getattr(raw, "status", None)).upper()
        if escalated and not claimed and case_status not in _TERMINAL_CASE:
            return True
        if isinstance(raw, dict):
            escalated = bool(raw.get("escalatedToPusat") or raw.get("escalated_to_pusat"))
            claimed = _norm(
                str(raw.get("handlingClaimedBy") or raw.get("handling_claimed_by") or "")
            )
            case_status = _norm(str(raw.get("status") or "")).upper()
            if escalated and not claimed and case_status not in _TERMINAL_CASE:
                return True
    if _norm(intake_disposition).upper() == _ESCALATE_APPROVED and hq_accepted_at is None:
        return True
    return False

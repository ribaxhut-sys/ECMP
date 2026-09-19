"""BR-005 E4 — double-claim race, proven against a real Postgres row lock.

``test_cm_case_mode_a.py`` proves the claim guard for *sequential* calls
(claim, then a second claim in the same thread is rejected). It runs on an
in-memory SQLite connection, which cannot demonstrate that two concurrent
transactions actually block on the same row — SQLite has no ``FOR UPDATE``
and the fixture shares a single connection.

This test opens two independent Postgres connections and drives them from
separate threads: Thread A locks the Case row (``SELECT ... FOR UPDATE``,
matching ``SqlAlchemyCaseRepository.get(for_update=True)``) and holds the
transaction open; Thread B — going through the real
``CaseApplicationService.update_status`` claim path on its own connection —
must block until A commits, then lose with ``HANDLING_ALREADY_CLAIMED``.
That proves the fix closes the race at the database level, not just in
single-threaded application order.
"""

from __future__ import annotations

import threading
import time
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.errors import ApiError
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.application.dto import CreateCaseCommand, UpdateStatusCommand
from app.modules.cm_case.application.services import CaseApplicationService, NoOpSideEffects
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository

HOLD_SECONDS = 1.0


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for the real-lock claim race test",
)


def _new_session() -> Session:
    """A dedicated connection — never shared across threads."""
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    factory = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    return factory()


def _close(session: Session) -> None:
    session.close()
    session.bind.dispose()  # type: ignore[union-attr]


def _seed_unclaimed_case() -> str:
    """Create a Case, then clear the auto-claim so it starts open (queue state)."""
    setup = _new_session()
    try:
        complaint = CmBatch1ComplaintORM(
            id=uuid.uuid4(),
            complaint_number=f"CMP-{uuid.uuid4().hex[:8].upper()}",
            customer_id="CUST-RACE",
            category="BILLING",
            channel="WALK_IN",
            subject="Race seed complaint",
            description="Seed",
            priority="MEDIUM",
            status="REGISTERED",
            case_created=False,
            created_by="seed",
        )
        setup.add(complaint)
        setup.commit()
        service = CaseApplicationService(
            SqlAlchemyCaseRepository(setup), side_effects=NoOpSideEffects()
        )
        dto = service.create_case(
            CreateCaseCommand(
                complaint_id=str(complaint.id),
                case_type="BILLING",
                subject="Race case",
                description="desc",
                priority="MEDIUM",
                actor_id="seed",
            )
        )
        setup.execute(
            text("UPDATE cm_cases SET handling_claimed_by = NULL WHERE id = :id"),
            {"id": dto.case_id},
        )
        setup.commit()
        return dto.case_id
    finally:
        _close(setup)


def _officer_a_locks_then_holds(
    case_id: str,
    *,
    lock_acquired: threading.Event,
    errors: list[BaseException],
) -> None:
    """Take the FOR UPDATE lock, signal acquisition, hold it, then commit."""
    session = _new_session()
    try:
        repo = SqlAlchemyCaseRepository(session)
        case = repo.get(case_id, for_update=True)
        assert case is not None
        case.claim_handling("officer-1")
        repo.save(case)
        lock_acquired.set()
        time.sleep(HOLD_SECONDS)
        repo.commit()
    except BaseException as exc:  # noqa: BLE001 - surfaced to the main thread
        errors.append(exc)
        session.rollback()
    finally:
        _close(session)


def _officer_b_claims_after_a_has_lock(
    case_id: str,
    *,
    lock_acquired: threading.Event,
    result: dict,
    errors: list[BaseException],
) -> None:
    """Only start once A provably holds the lock, so B's read must block on it."""
    if not lock_acquired.wait(timeout=5):
        errors.append(RuntimeError("Officer A never signalled lock acquisition"))
        return
    session = _new_session()
    try:
        service = CaseApplicationService(
            SqlAlchemyCaseRepository(session), side_effects=NoOpSideEffects()
        )
        started = time.monotonic()
        try:
            service.update_status(
                UpdateStatusCommand(
                    case_id=case_id,
                    to_status="CREATED",
                    actor_id="officer-2",
                    reason="HANDLE_CLAIM",
                )
            )
        except ApiError as exc:
            result["blocked_seconds"] = time.monotonic() - started
            result["error"] = exc
        else:
            result["blocked_seconds"] = time.monotonic() - started
            result["error"] = None
    except BaseException as exc:  # noqa: BLE001
        errors.append(exc)
        session.rollback()
    finally:
        _close(session)


def test_concurrent_claim_blocks_on_row_lock_and_only_one_wins() -> None:
    case_id = _seed_unclaimed_case()

    lock_acquired = threading.Event()
    errors: list[BaseException] = []
    result: dict = {}

    thread_a = threading.Thread(
        target=_officer_a_locks_then_holds,
        args=(case_id,),
        kwargs={"lock_acquired": lock_acquired, "errors": errors},
    )
    thread_b = threading.Thread(
        target=_officer_b_claims_after_a_has_lock,
        args=(case_id,),
        kwargs={"lock_acquired": lock_acquired, "result": result, "errors": errors},
    )

    thread_a.start()
    thread_b.start()
    thread_a.join(timeout=10)
    thread_b.join(timeout=10)

    assert not errors, f"unexpected errors in worker threads: {errors}"
    assert not thread_a.is_alive() and not thread_b.is_alive(), "worker thread hung"

    # Proof #1 — B's claim attempt actually blocked on Postgres' row lock for
    # (most of) the duration A held it. A sequential/app-level check would
    # return near-instantly instead.
    assert result.get("blocked_seconds", 0.0) >= HOLD_SECONDS * 0.8, (
        "Officer B's claim did not block on the FOR UPDATE lock — "
        f"took {result.get('blocked_seconds')!r}s, expected >= {HOLD_SECONDS * 0.8}s"
    )

    # Proof #2 — after unblocking, B loses: only one claim wins (BR-005 E4).
    error = result.get("error")
    assert isinstance(error, ApiError), f"expected officer B to be rejected, got {error!r}"
    assert error.code == "HANDLING_ALREADY_CLAIMED"
    assert error.details == {"handlingClaimedBy": "officer-1"}

    verify = _new_session()
    try:
        claimed_by = verify.execute(
            text("SELECT handling_claimed_by FROM cm_cases WHERE id = :id"),
            {"id": case_id},
        ).scalar_one()
        assert claimed_by == "officer-1"
    finally:
        _close(verify)

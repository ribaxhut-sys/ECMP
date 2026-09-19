#!/usr/bin/env python3
"""Mode A ops hygiene for Complaint Batch-1 (FR-004 + FR-030).

Commands (run from ``backend/`` with app env loaded)::

    python scripts/cm_batch1_ops_hygiene.py probe-storage
    python scripts/cm_batch1_ops_hygiene.py void-abandoned-staging
    python scripts/cm_batch1_ops_hygiene.py sweep-sla-thresholds
    python scripts/cm_batch1_ops_hygiene.py drain-outbox
    python scripts/cm_batch1_ops_hygiene.py all

Does **not** invent OpenAPI routes. Does **not** unlock Mode B / CAP-005.
TD-OPS-002 (password drift) remains deferred — out of this script.

Prefer wrapping sweep/drain with host ``flock -n`` (OPS-CM-B1-SLA-001); this
script also takes an internal non-blocking flock so a double schedule is safe.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow ``python scripts/...`` from backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

logger = logging.getLogger("cm_batch1_ops_hygiene")


def _configure() -> None:
    from app.core.config import get_settings
    from app.core.logging import configure_logging

    settings = get_settings()
    configure_logging(settings.log_level, log_format=settings.log_format)


def cmd_probe_storage() -> int:
    from app.db.session import get_session_factory
    from app.modules.attachment.registration import build_attachment_service
    from app.modules.attachment.service import SETTING_STORAGE_ROOT_PATH
    from app.modules.cm_batch1.ops_hygiene import probe_local_attachment_storage
    from app.modules.settings.repository import SettingsRepository
    from app.modules.settings.service import SettingsService

    session = get_session_factory()()
    try:
        settings_svc = SettingsService(SettingsRepository(session))
        root = settings_svc.get_string(
            SETTING_STORAGE_ROOT_PATH, default="storage/attachments"
        ).strip()
        result = probe_local_attachment_storage(root)
        print(
            f"storageProbe ok={result.ok} root={result.root} "
            f"exists={result.exists} writable={result.writable} detail={result.detail}"
        )
        # Touch service construction to prove CAP-011 wiring still loads.
        _ = build_attachment_service(session)
        return 0 if result.ok else 2
    finally:
        session.close()


def cmd_void_abandoned() -> int:
    from app.db.session import get_session_factory
    from app.modules.attachment.registration import build_attachment_service
    from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
    from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
    from app.modules.cm_batch1.repository import CmBatch1Repository

    session = get_session_factory()()
    try:
        svc = CmBatch1AttachmentService(
            attachment_service=build_attachment_service(session),
            repository=CmBatch1AttachmentRepository(session),
            complaints=CmBatch1Repository(session),
        )
        count = svc.void_abandoned_staging(actor_id="ops-hygiene")
        print(f"voidAbandonedStaging voidedAttachments={count}")
        return 0
    finally:
        session.close()


def cmd_sweep_sla_thresholds(
    *,
    lock_path: Path | None = None,
    marker_path: Path | None = None,
) -> int:
    from app.core.config import get_settings
    from app.db.session import get_session_factory
    from app.modules.cm_batch1.ops_hygiene import (
        DEFAULT_SLA_SWEEP_LOCK,
        DEFAULT_SLA_SWEEP_MARKER,
        exclusive_lock,
        write_heartbeat_marker,
    )
    from app.modules.cm_batch1.sla_sweep import CmBatch1SlaSweepService

    settings = get_settings()
    lock = lock_path or DEFAULT_SLA_SWEEP_LOCK
    marker = marker_path or DEFAULT_SLA_SWEEP_MARKER
    try:
        with exclusive_lock(lock):
            session = get_session_factory()()
            try:
                result = CmBatch1SlaSweepService(
                    session,
                    target_days=settings.complaint_resolution_target_days,
                    warning_percent=settings.complaint_sla_warning_percent,
                    batch_limit=settings.complaint_sla_sweep_batch_limit,
                ).sweep()
                write_heartbeat_marker(marker)
                print(
                    f"sweepSlaThresholds scanned={result.scanned} "
                    f"emitted={result.emitted} "
                    f"skippedIdempotent={result.skipped_idempotent}"
                )
                logger.info(
                    "sweep-sla-thresholds ok scanned=%s emitted=%s skipped=%s",
                    result.scanned,
                    result.emitted,
                    result.skipped_idempotent,
                )
                return 0
            finally:
                session.close()
    except BlockingIOError:
        print(f"sweepSlaThresholds skipped=lock_held lock={lock}")
        logger.info("sweep-sla-thresholds skipped=lock_held lock=%s", lock)
        return 0
    except Exception:
        logger.exception("sweep-sla-thresholds failed")
        print("sweepSlaThresholds failed=1", file=sys.stderr)
        return 2


def cmd_drain_outbox(
    *,
    lock_path: Path | None = None,
    marker_path: Path | None = None,
) -> int:
    from app.core.config import get_settings
    from app.db.session import get_session_factory
    from app.modules.cm_batch1.ops_hygiene import (
        DEFAULT_OUTBOX_DRAIN_LOCK,
        DEFAULT_OUTBOX_DRAIN_MARKER,
        exclusive_lock,
        write_heartbeat_marker,
    )
    from app.modules.cm_batch1.sla_sweep import CmBatch1OutboxDrainService

    settings = get_settings()
    lock = lock_path or DEFAULT_OUTBOX_DRAIN_LOCK
    marker = marker_path or DEFAULT_OUTBOX_DRAIN_MARKER
    try:
        with exclusive_lock(lock):
            session = get_session_factory()()
            try:
                result = CmBatch1OutboxDrainService(
                    session,
                    batch_limit=settings.complaint_sla_sweep_batch_limit,
                ).drain()
                write_heartbeat_marker(marker)
                print(f"drainOutbox published={result.published}")
                logger.info("drain-outbox ok published=%s", result.published)
                return 0
            finally:
                session.close()
    except BlockingIOError:
        print(f"drainOutbox skipped=lock_held lock={lock}")
        logger.info("drain-outbox skipped=lock_held lock=%s", lock)
        return 0
    except Exception:
        logger.exception("drain-outbox failed")
        print("drainOutbox failed=1", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CM Batch-1 Mode A ops hygiene (FR-004 staging / FR-030 SLA)"
    )
    parser.add_argument(
        "command",
        choices=(
            "probe-storage",
            "void-abandoned-staging",
            "sweep-sla-thresholds",
            "drain-outbox",
            "all",
        ),
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=None,
        help="Override flock path (tests / non-standard hosts)",
    )
    parser.add_argument(
        "--marker-path",
        type=Path,
        default=None,
        help="Override heartbeat marker path (C-1)",
    )
    args = parser.parse_args(argv)
    _configure()

    if args.command == "probe-storage":
        return cmd_probe_storage()
    if args.command == "void-abandoned-staging":
        return cmd_void_abandoned()
    if args.command == "sweep-sla-thresholds":
        return cmd_sweep_sla_thresholds(
            lock_path=args.lock_path, marker_path=args.marker_path
        )
    if args.command == "drain-outbox":
        return cmd_drain_outbox(
            lock_path=args.lock_path, marker_path=args.marker_path
        )

    # ``all`` stays FR-004-only so existing staging cron does not start SLA
    # sweeps without an explicit crontab line (OPS-CM-B1-SLA-001).
    probe_rc = cmd_probe_storage()
    void_rc = cmd_void_abandoned()
    return probe_rc if probe_rc != 0 else void_rc


if __name__ == "__main__":
    raise SystemExit(main())

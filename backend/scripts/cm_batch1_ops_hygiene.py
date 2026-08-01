#!/usr/bin/env python3
"""Mode A ops hygiene for Complaint Batch-1 attachments (FR-004).

Commands (run from ``backend/`` with app env loaded)::

    python scripts/cm_batch1_ops_hygiene.py probe-storage
    python scripts/cm_batch1_ops_hygiene.py void-abandoned-staging
    python scripts/cm_batch1_ops_hygiene.py all

Does **not** invent OpenAPI routes. Does **not** unlock Mode B.
TD-OPS-002 (password drift) remains deferred — out of this script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow ``python scripts/...`` from backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CM Batch-1 Mode A ops hygiene (FR-004 staging / storage)"
    )
    parser.add_argument(
        "command",
        choices=("probe-storage", "void-abandoned-staging", "all"),
    )
    args = parser.parse_args(argv)
    _configure()

    if args.command == "probe-storage":
        return cmd_probe_storage()
    if args.command == "void-abandoned-staging":
        return cmd_void_abandoned()

    probe_rc = cmd_probe_storage()
    void_rc = cmd_void_abandoned()
    return probe_rc if probe_rc != 0 else void_rc


if __name__ == "__main__":
    raise SystemExit(main())

"""Mode A ops hygiene helpers for Batch-1 Complaint attachments + SLA (FR-004 / FR-030).

No new HTTP API — operators run ``backend/scripts/cm_batch1_ops_hygiene.py``.
Does not unlock Mode B / TD-OPS-002 password drift / CAP-005 transport.
"""

from __future__ import annotations

import fcntl
import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)

DEFAULT_SLA_SWEEP_LOCK = Path("/var/lock/ecmp-cm-sla-sweep.lock")
DEFAULT_OUTBOX_DRAIN_LOCK = Path("/var/lock/ecmp-cm-outbox-drain.lock")
DEFAULT_SLA_SWEEP_MARKER = Path("/var/log/ecmp/cm-sla-sweep.last_ok")
DEFAULT_OUTBOX_DRAIN_MARKER = Path("/var/log/ecmp/cm-outbox-drain.last_ok")


@dataclass(frozen=True)
class AttachmentStorageProbe:
    ok: bool
    root: str
    exists: bool
    writable: bool
    detail: str


def probe_local_attachment_storage(root: Path | str) -> AttachmentStorageProbe:
    """Check that the attachment blob root exists and is writable (Complaint evidence)."""
    path = Path(root).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()

    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return AttachmentStorageProbe(
            ok=False,
            root=str(path),
            exists=path.exists(),
            writable=False,
            detail=f"mkdir failed: {exc}",
        )

    probe = path / ".ecmp_write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        return AttachmentStorageProbe(
            ok=False,
            root=str(path),
            exists=True,
            writable=False,
            detail=f"write probe failed: {exc}",
        )

    return AttachmentStorageProbe(
        ok=True,
        root=str(path),
        exists=True,
        writable=True,
        detail="writable",
    )


def write_heartbeat_marker(path: Path | str, *, when: datetime | None = None) -> None:
    """C-1 — stamp last successful run (UTC ISO-8601)."""
    stamp = (when or datetime.now(UTC)).astimezone(UTC).isoformat().replace("+00:00", "Z")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(stamp + "\n", encoding="utf-8")


@contextmanager
def exclusive_lock(path: Path | str) -> Iterator[None]:
    """Non-blocking exclusive flock. Raises ``BlockingIOError`` if held."""
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

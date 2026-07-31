"""Mode A ops hygiene helpers for Batch-1 Complaint attachments (FR-004).

No new HTTP API — operators run ``backend/scripts/cm_batch1_ops_hygiene.py``.
Does not unlock Mode B / TD-OPS-002 password drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

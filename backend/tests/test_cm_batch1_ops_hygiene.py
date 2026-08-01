"""Unit tests for Mode A Batch-1 ops hygiene helpers (no DB)."""

from __future__ import annotations

from pathlib import Path

from app.modules.cm_batch1.ops_hygiene import probe_local_attachment_storage


def test_probe_local_attachment_storage_writable(tmp_path: Path) -> None:
    root = tmp_path / "attachments"
    result = probe_local_attachment_storage(root)
    assert result.ok is True
    assert result.writable is True
    assert result.exists is True
    assert Path(result.root).exists()


def test_probe_local_attachment_storage_rejects_file_as_root(tmp_path: Path) -> None:
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x", encoding="utf-8")
    result = probe_local_attachment_storage(blocker)
    assert result.ok is False
    assert result.writable is False

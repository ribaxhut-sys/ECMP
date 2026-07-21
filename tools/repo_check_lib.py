#!/usr/bin/env python3
"""Shared repository governance helpers used by ear_repo_check.py and repo_metrics.py."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

SKIP_DIR_NAMES = {".git", ".cursor", "node_modules", "__pycache__", "archive", "site", ".venv", ".pytest_cache"}
SKIP_FILE_NAMES = {"GENERATED_INVENTORY.md", "REPO_HEALTH_REPORT.md", "ADR_INDEX.generated.md"}

META_FIELDS = ("ID", "Version", "Owner", "Reviewer", "Approver", "Status", "Last Review", "Next Review")


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.name in SKIP_FILE_NAMES:
            continue
        yield path


def numbered_folders(root: Path):
    return sorted([p for p in root.iterdir() if p.is_dir() and re.match(r"^\d{2} ", p.name)])


def parse_metadata(text: str) -> dict[str, str]:
    """Parse only EAR metadata tables that start with | Field | Value |."""
    meta = {}
    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        if not re.search(r"\|\s*Field\s*\|\s*Value\s*\|", block, flags=re.IGNORECASE):
            continue
        for field in META_FIELDS:
            m = re.search(
                rf"\|\s*{re.escape(field)}\s*\|\s*([^|]+)\|",
                block,
                flags=re.IGNORECASE,
            )
            if m:
                meta[field] = m.group(1).strip()
        if meta:
            break
    return meta


def extract_md_links(text: str):
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def check_links(path: Path, text: str):
    broken = []
    for link in extract_md_links(text):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        if link.startswith("#"):
            continue
        raw = unquote(link.split("#")[0]).strip()
        if not raw:
            continue
        candidate = (path.parent / raw).resolve()
        if not candidate.exists():
            broken.append(link)
    return broken


def build_inventory(root: Path):
    rows = []
    for folder in numbered_folders(root):
        md_files = [p for p in folder.rglob("*.md") if p.name not in SKIP_FILE_NAMES]
        rows.append((folder.name, len(md_files), (folder / "README.md").exists()))
    return rows


def score_health(stats: dict) -> int:
    # Weighted health: metadata completeness, links, readme presence, review freshness
    total = max(stats["total_md"], 1)
    meta_ok = 1 - (stats["missing_metadata"] / total)
    fields_ok = 1 - (stats["incomplete_metadata"] / total)
    link_ok = 1.0 if stats["broken_links"] == 0 else max(0.0, 1 - (stats["broken_links"] / max(total, 1)))
    readme_ok = 1 - (stats["missing_readme"] / max(stats["folders"], 1))
    review_ok = 1 - (stats["review_due"] / total)
    owner_ok = 1.0 if stats["missing_owner"] == 0 else max(0.0, 1 - stats["missing_owner"] / total)

    health = (
        meta_ok * 0.25
        + fields_ok * 0.20
        + link_ok * 0.20
        + readme_ok * 0.10
        + review_ok * 0.15
        + owner_ok * 0.10
    )
    return int(round(health * 100))

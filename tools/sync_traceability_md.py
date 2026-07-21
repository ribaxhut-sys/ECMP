#!/usr/bin/env python3
"""Sync TRACEABILITY_MATRIX.md from traceability.yaml."""

from __future__ import annotations

from eos_lib import ROOT, load_traceability, meta_block

OUT = ROOT / "26 Traceability" / "TRACEABILITY_MATRIX.md"


def main():
    links, artifacts = load_traceability()
    lines = [
        "# ECMP Traceability Matrix",
        "",
        *meta_block("TRC-001", "BA Lead / QA Lead"),
        "> Synced from `traceability.yaml` by `tools/sync_traceability_md.py`.",
        "",
        "| Link | Domain | BP | BR | FR | API | Event | Test | Sprint | Status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for link in links:
        lines.append(
            "| {id} | {domain} | {bp} | {br} | {fr} | {api} | {evt} | {tc} | {sprint} | {status} |".format(
                id=link.get("id", ""),
                domain=link.get("domain", ""),
                bp=link.get("bp", ""),
                br=link.get("br", ""),
                fr=link.get("fr", ""),
                api=", ".join(link.get("api") or []) or "—",
                evt=", ".join(link.get("events") or []) or "—",
                tc=", ".join(link.get("tests") or []) or "—",
                sprint=link.get("sprint") or "—",
                status=link.get("status") or "",
            )
        )
    lines += ["", "## Artifact Dictionary", ""]
    for kind in ["bp", "br", "fr", "api", "events", "tests"]:
        lines.append(f"### {kind.upper()}")
        for key, val in (artifacts.get(kind) or {}).items():
            lines.append(f"- `{key}`: {val}")
        lines.append("")
    lines += [
        "## Maintenance Rule",
        "",
        "Update `traceability.yaml` first, then run `python tools/sync_traceability_md.py` (or `run_engineering_os.py`).",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

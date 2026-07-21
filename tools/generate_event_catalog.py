#!/usr/bin/env python3
"""Generate markdown Event Catalog page from events/events.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "08 Event Catalog" / "events" / "events.yaml"
OUT = ROOT / "08 Event Catalog" / "EVENT_CATALOG.generated.md"

# Badge per status text; see "00 Repository Guide/STATUS_BADGES.md".
STATUS_BADGES = {
    "approved": "🟢",
    "draft": "🟡",
    "under review": "🔵",
    "deprecated": "🔴",
}


def status_badge(status: str) -> str:
    return STATUS_BADGES.get(str(status).strip().lower(), "🟡")


def main():
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    events = data.get("events", [])
    status = data.get("status", "Draft")
    lines = [
        "# Event Catalog (Generated)",
        "",
        "| Field | Value |",
        "|---|---|",
        "| ID | EVT-CAT-001 |",
        f"| Version | {data.get('version', '0.1')} |",
        f"| Owner | {data.get('owner', 'Integration Lead')} |",
        "| Reviewer | Solution Architect |",
        "| Approver | Architecture Board |",
        f"| Status | {status_badge(status)} {status} |",
        "| Last Review | auto |",
        "| Next Review | auto |",
        "",
        f"> Generated from `{SOURCE.relative_to(ROOT).as_posix()}`.",
        "",
        "| Event ID | Name | Producer | Status | Description |",
        "|---|---|---|---|---|",
    ]
    for evt in events:
        evt_status = evt.get("status") or "Planned"
        lines.append(
            f"| {evt.get('id','')} | {evt.get('name','')} | {evt.get('producer','')} "
            f"| {evt_status} | {evt.get('description','')} |"
        )
    lines += ["", "## Payload Summary", ""]
    for evt in events:
        lines.append(f"### {evt.get('id')} — {evt.get('name')}")
        payload = evt.get("payload") or {}
        if not payload:
            lines.append("- (no payload defined)")
        else:
            for key, typ in payload.items():
                lines.append(f"- `{key}`: {typ}")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

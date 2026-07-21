#!/usr/bin/env python3
"""Repository Observability — trends over time + change activity."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import date, datetime

from eos_lib import ROOT, meta_block

HISTORY_DIR = ROOT / "metrics" / "history"
OUT = ROOT / "00 Repository Guide" / "REPO_TRENDS.generated.md"
PORTAL = ROOT / "docs" / "governance" / "repo-trends.md"


def load_history() -> list[dict]:
    rows = []
    if not HISTORY_DIR.exists():
        return rows
    for path in sorted(HISTORY_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_file"] = path.name
            rows.append(data)
        except Exception:
            continue
    rows.sort(key=lambda r: r.get("date", ""))
    return rows


def delta(curr, prev, key):
    if prev is None:
        return "n/a"
    try:
        return int(curr.get(key, 0)) - int(prev.get(key, 0))
    except Exception:
        return "n/a"


def git_available() -> bool:
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def git_change_stats(max_commits: int = 200):
    """Return file change counts and domain activity from git history."""
    if not git_available():
        return [], {}, {}
    try:
        log = subprocess.check_output(
            ["git", "log", f"-n{max_commits}", "--name-only", "--pretty=format:---%H|%ad|%s", "--date=short"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return [], {}, {}

    file_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()
    monthly_commits: Counter[str] = Counter()
    current_date = None

    domain_map = {
        "01 ": "Business",
        "02 ": "Business Rules",
        "03 ": "FRD",
        "04 ": "Solution Architecture",
        "05 ": "ADR",
        "07 ": "API",
        "08 ": "Event",
        "20 ": "Domain Architecture",
        "ai/domain/crm": "CRM",
        "ai/domain/ecmf": "ECMF",
        "ai/domain/kpi": "KPI",
        "ai/domain/dashboard": "Dashboard",
        "ai/domain/notification": "Notification",
        "ai/domain/core-platform": "Core Platform",
        "implementation/": "Implementation",
        "20 Domain Architecture/CRM": "CRM",
        "20 Domain Architecture/ECMF": "ECMF",
        "20 Domain Architecture/KPI": "KPI",
        "20 Domain Architecture/Dashboard": "Dashboard",
        "20 Domain Architecture/Notification": "Notification",
        "20 Domain Architecture/Core Platform": "Core Platform",
    }

    for line in log.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("---"):
            # ---hash|date|subject
            parts = line[3:].split("|", 2)
            if len(parts) >= 2:
                current_date = parts[1]
                monthly_commits[current_date[:7]] += 1
            continue
        file_counts[line] += 1
        for prefix, domain in domain_map.items():
            if line.startswith(prefix) or prefix in line:
                domain_counts[domain] += 1
                break
        else:
            if line.startswith("ai/"):
                domain_counts["AI Context"] += 1
            elif line.startswith("docs/"):
                domain_counts["Portal Docs"] += 1
            elif line.startswith("tools/"):
                domain_counts["Tooling"] += 1

    top_files = file_counts.most_common(15)
    return top_files, dict(domain_counts.most_common(15)), dict(sorted(monthly_commits.items()))


def avg_review_lag_days() -> str:
    """Heuristic: days between Last Review and Next Review on approved/draft docs."""
    lags = []
    for path in ROOT.rglob("*.md"):
        if any(p in path.parts for p in {".git", "site", ".venv", "__pycache__"}):
            continue
        if "generated" in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "| Field | Value |" not in text:
            continue
        last = re.search(r"\|\s*Last Review\s*\|\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*\|", text)
        nxt = re.search(r"\|\s*Next Review\s*\|\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*\|", text)
        if not last or not nxt:
            continue
        try:
            d1 = datetime.strptime(last.group(1), "%Y-%m-%d").date()
            d2 = datetime.strptime(nxt.group(1), "%Y-%m-%d").date()
            lag = (d2 - d1).days
            if 0 < lag < 800:
                lags.append(lag)
        except Exception:
            continue
    if not lags:
        return "n/a (insufficient dated reviews)"
    return f"{sum(lags) / len(lags):.0f} days (from {len(lags)} docs with dated review window)"


def render(history: list[dict], top_files, domain_counts, monthly_commits) -> str:
    latest = history[-1] if history else {}
    prev = history[-2] if len(history) >= 2 else None
    lines = [
        "# Repository Trends & Observability",
        "",
        *meta_block("EOS-TRENDS-001"),
        "> Generated by `tools/repo_trends.py`.",
        "",
        f"## Latest Snapshot ({latest.get('date', 'n/a')})",
        "",
        "| Metric | Value | Δ vs previous snapshot |",
        "|---|---|---|",
    ]
    keys = [
        ("health", "Health %"),
        ("adr_count", "ADR count"),
        ("api_spec_count", "API specs"),
        ("event_count", "Events"),
        ("business_rules_referenced", "Business Rules (ref)"),
        ("fr_referenced", "FR (ref)"),
        ("traceability_links", "Traceability links"),
        ("domains_in_traceability", "Domains in traceability"),
        ("metadata_complete_pct", "Metadata completeness %"),
        ("reviewed_pct", "Reviewed/Approved %"),
        ("markdown_files", "Markdown files"),
    ]
    for key, label in keys:
        val = latest.get(key, "n/a")
        d = delta(latest, prev, key)
        d_txt = d if d == "n/a" else (f"+{d}" if isinstance(d, int) and d > 0 else str(d))
        lines.append(f"| {label} | {val} | {d_txt} |")

    lines += [
        "",
        "## History Table",
        "",
        "| Date | Health | ADR | API | Event | BR | FR | Links | Reviewed % |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    if not history:
        lines.append("| — | — | — | — | — | — | — | — | — |")
    else:
        for row in history[-12:]:
            lines.append(
                "| {date} | {health} | {adr} | {api} | {evt} | {br} | {fr} | {links} | {rev} |".format(
                    date=row.get("date", ""),
                    health=row.get("health", ""),
                    adr=row.get("adr_count", ""),
                    api=row.get("api_spec_count", ""),
                    evt=row.get("event_count", ""),
                    br=row.get("business_rules_referenced", ""),
                    fr=row.get("fr_referenced", ""),
                    links=row.get("traceability_links", ""),
                    rev=row.get("reviewed_pct", ""),
                )
            )

    lines += ["", "## ADR / Artifact Growth (text)", "", "```text"]
    if len(history) == 1:
        lines.append("Only one metrics snapshot available. Re-run repo_metrics over time to build trends.")
    else:
        for row in history:
            bar = "█" * max(1, int(row.get("adr_count", 0)))
            lines.append(f"{row.get('date')}: ADR {row.get('adr_count', 0):>3} {bar}")
    lines += ["```", ""]

    lines += [
        "## Average Review Window",
        "",
        f"- {avg_review_lag_days()}",
        "",
        "## Most Changed Documents (git)",
        "",
    ]
    if not top_files:
        lines.append("_Git history not available or empty in this environment._")
    else:
        lines.append("| File | Changes (recent commits) |")
        lines.append("|---|---|")
        for path, count in top_files:
            lines.append(f"| `{path}` | {count} |")

    lines += ["", "## Most Active Areas (git)", ""]
    if not domain_counts:
        lines.append("_No domain activity derived from git yet._")
    else:
        lines.append("| Area | File-change events |")
        lines.append("|---|---|")
        for area, count in sorted(domain_counts.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| {area} | {count} |")

    lines += ["", "## Commit Volume by Month (git)", ""]
    if not monthly_commits:
        lines.append("_No monthly commit data._")
    else:
        lines.append("| Month | Commits |")
        lines.append("|---|---|")
        for month, count in monthly_commits.items():
            lines.append(f"| {month} | {count} |")

    lines += [
        "",
        "## How to Grow Trend History",
        "",
        "1. Run `python tools/repo_metrics.py` regularly (CI on main is enough)",
        "2. Keep `metrics/history/*.json` committed",
        "3. Re-run `python tools/repo_trends.py` (or `python tools/eos.py` → Trends)",
        "",
    ]
    return "\n".join(lines)


def main():
    history = load_history()
    top_files, domain_counts, monthly_commits = git_change_stats()
    text = render(history, top_files, domain_counts, monthly_commits)
    OUT.write_text(text, encoding="utf-8")
    PORTAL.parent.mkdir(parents=True, exist_ok=True)
    PORTAL.write_text(text, encoding="utf-8")
    # also stamp a trends pointer into today's metrics if present
    today = date.today().isoformat()
    snap = HISTORY_DIR / f"{today}.json"
    if snap.exists():
        data = json.loads(snap.read_text(encoding="utf-8"))
        data["trends_generated"] = True
        data["top_changed_files"] = [{"path": p, "count": c} for p, c in top_files[:10]]
        data["active_areas"] = domain_counts
        snap.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {PORTAL}")


if __name__ == "__main__":
    main()

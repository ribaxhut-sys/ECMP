#!/usr/bin/env python3
"""Shared helpers for Engineering OS capability tools."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRACEABILITY = ROOT / "26 Traceability" / "traceability.yaml"
EVENTS = ROOT / "08 Event Catalog" / "events" / "events.yaml"
OPENAPI_DIR = ROOT / "07 API Catalog" / "openapi"
ADR_DIR = ROOT / "05 Architecture Decision Records"
DOMAIN_ARCH = ROOT / "20 Domain Architecture"
AI_DOMAIN = ROOT / "ai" / "domain"
SPRINT_DIR = ROOT / "ai" / "sprint"
BR_DIR = ROOT / "02 Business Rules"
FRD_DIR = ROOT / "03 Functional Requirements"

DOMAINS = ["CRM", "ECMF", "KPI", "Dashboard", "Notification", "Core Platform", "Administration", "Channel"]


def load_yaml(path: Path):
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_traceability():
    data = load_yaml(TRACEABILITY)
    return data.get("links", []), data.get("artifacts", {})


def meta_block(doc_id: str, title_owner: str = "Automation") -> list[str]:
    return [
        "| Field | Value |",
        "|---|---|",
        f"| ID | {doc_id} |",
        "| Version | 0.1 |",
        f"| Owner | {title_owner} |",
        "| Reviewer | PMO / Enterprise Architecture |",
        "| Approver | Architecture Board |",
        "| Status | 🟡 Draft |",
        "| Last Review | auto |",
        "| Next Review | auto |",
        "",
    ]


def list_openapi_ops():
    ops = {}
    if not OPENAPI_DIR.exists():
        return ops
    for path in list(OPENAPI_DIR.glob("*.yaml")) + list(OPENAPI_DIR.glob("*.yml")):
        data = load_yaml(path)
        info = data.get("info") or {}
        ear_id = info.get("x-ear-id")
        title = info.get("title", path.stem)
        paths = data.get("paths") or {}
        count = sum(len(v) for v in paths.values() if isinstance(v, dict))
        key = ear_id or path.stem
        ops[key] = {"file": path.name, "title": title, "operations": count, "path": path}
    return ops


def list_events():
    data = load_yaml(EVENTS)
    out = {}
    for evt in data.get("events") or []:
        out[evt.get("id", evt.get("name"))] = evt
    return out


def list_adrs():
    rows = []
    if not ADR_DIR.exists():
        return rows
    for path in sorted(ADR_DIR.glob("*.md")):
        if path.name in {"README.md", "ADR_INDEX.generated.md"} or "template" in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"\|\s*ID\s*\|\s*(ADR-\d+)\s*\|", text, flags=re.I)
        if m:
            rows.append({"id": m.group(1), "path": path})
    return rows


def domain_folder_name(domain: str) -> str:
    mapping = {
        "CRM": "CRM",
        "ECMF": "ECMF",
        "KPI": "KPI",
        "Dashboard": "Dashboard",
        "Notification": "Notification",
        "Core Platform": "Core Platform",
        "Administration": "Administration",
        "Channel": "Channel",
    }
    return mapping.get(domain, domain)


def file_exists_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


# Manual coverage estimates, NOT derived from repository data. These floors
# represent documentation known to exist outside machine-detectable locations
# (e.g. FRD content still living in source workbooks). Remove entries as the
# real docs land; a domain whose scores were lifted here reports basis=manual.
MANUAL_BASELINES: dict[str, dict[str, int]] = {
    "ECMF": {"frd_score": 60},
    "CRM": {"frd_score": 40},
    "Notification": {"frd_score": 40},
    "KPI": {"frd_score": 10},
}


def domain_signals(domain: str) -> dict:
    """Heuristic coverage signals for a domain."""
    dfold = domain_folder_name(domain)
    links, _ = load_traceability()
    domain_links = [ln for ln in links if ln.get("domain") == domain]

    ai_domain = AI_DOMAIN / f"{dfold.lower().replace(' ', '-')}.md"
    if domain == "Core Platform":
        ai_domain = AI_DOMAIN / "core-platform.md"
    if domain == "Administration":
        ai_domain = AI_DOMAIN / "administration.md"

    arch = DOMAIN_ARCH / dfold / "README.md"
    frd_files = list(FRD_DIR.glob(f"*{domain}*")) + list(FRD_DIR.glob(f"*{dfold}*"))

    has_business = file_exists_nonempty(ai_domain) or file_exists_nonempty(arch)

    frd_score = 0
    if frd_files:
        frd_score = 100
    elif domain_links:
        # No FRD documents yet: links referencing FR IDs are a partial signal,
        # so credit is capped at 50%.
        with_fr = sum(1 for ln in domain_links if ln.get("fr"))
        frd_score = int(round(50 * with_fr / len(domain_links)))

    apis = {a for ln in domain_links for a in (ln.get("api") or [])}
    evts = {e for ln in domain_links for e in (ln.get("events") or [])}
    tests = {t for ln in domain_links for t in (ln.get("tests") or [])}

    openapi = list_openapi_ops()
    events_cat = list_events()

    api_score = 0
    if apis:
        matched = sum(1 for a in apis if a in openapi or any(a in key for key in openapi))
        with_api = sum(1 for ln in domain_links if ln.get("api"))
        link_ratio = with_api / max(len(domain_links), 1)
        match_ratio = matched / len(apis)
        # Half weight: links carrying an API artifact; half: APIs found in the catalog.
        api_score = int(round(100 * (0.5 * link_ratio + 0.5 * match_ratio)))

    event_score = 0
    if evts:
        present = sum(1 for e in evts if e in events_cat)
        event_score = int(100 * present / len(evts))

    test_score = int(100 * len(tests) / max(len(domain_links), 1)) if domain_links else 0
    if domain_links and not tests:
        test_score = 0
    elif tests and not domain_links:
        test_score = 40

    scores = {
        "frd_score": frd_score,
        "api_score": api_score,
        "event_score": event_score,
        "test_score": test_score,
    }
    basis = "computed"
    for key, floor in MANUAL_BASELINES.get(domain, {}).items():
        if scores[key] < floor:
            scores[key] = floor
            basis = "manual"

    return {
        "domain": domain,
        "business": has_business,
        "basis": basis,
        **scores,
        "links": domain_links,
        "apis": sorted(apis),
        "events": sorted(evts),
        "tests": sorted(tests),
        "frs": sorted({ln.get("fr") for ln in domain_links if ln.get("fr")}),
        "brs": sorted({ln.get("br") for ln in domain_links if ln.get("br")}),
        "sprints": sorted({ln.get("sprint") for ln in domain_links if ln.get("sprint")}),
        "ai_domain": ai_domain,
        "arch": arch,
    }

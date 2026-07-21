#!/usr/bin/env python3
"""AI Platform helpers: registries, prompt/memory resolution, packs."""

from __future__ import annotations

from pathlib import Path

import yaml

from eos_lib import ROOT

AIP = ROOT / "ai-platform"


def load_yaml(path: Path):
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def list_agents() -> dict[str, dict]:
    agents = {}
    for path in sorted((AIP / "agents").glob("*.yaml")):
        data = load_yaml(path)
        if data.get("id"):
            agents[data["id"]] = data
    return agents


def load_capabilities() -> dict[str, dict]:
    reg = load_yaml(AIP / "capabilities" / "registry.yaml")
    out = {}
    for cap in reg.get("capabilities", []) or []:
        out[cap["id"]] = cap
    return out


def current_memory_version() -> str:
    text = (AIP / "memory" / "MANIFEST.md").read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if "current =" in line.lower():
            # **current = v1**
            part = line.split("=")[-1].strip().strip("*").strip()
            if part.startswith("v"):
                return part
    return "v1"


def resolve_prompt(ref: str) -> Path:
    """Resolve prompt ref like 'implement-feature@v1' or 'implement-feature'."""
    name, _, ver = ref.partition("@")
    if not ver:
        # parse MANIFEST current table lightly; default v1
        ver = "v1"
        manifest = (AIP / "prompts" / "MANIFEST.md").read_text(encoding="utf-8", errors="ignore")
        for line in manifest.splitlines():
            if line.strip().startswith(f"| {name} "):
                cols = [c.strip() for c in line.split("|") if c.strip()]
                if len(cols) >= 2:
                    ver = cols[1]
                break
    path = AIP / "prompts" / name / ver / "prompt.md"
    return path


def detect_domain(task: str) -> str | None:
    t = task.lower()
    mapping = {
        "ecmf": "ecmf",
        "complaint": "ecmf",
        "case": "ecmf",
        "crm": "crm",
        "customer 360": "crm",
        "kpi": "kpi",
        "sla": "kpi",
        "dashboard": "dashboard",
        "notification": "notification",
        "core platform": "core-platform",
        "auth": "core-platform",
    }
    for key, dom in mapping.items():
        if key in t:
            return dom
    return None


def pack_path(domain: str) -> Path:
    return AIP / "packs" / domain.lower().replace(" ", "-") / "pack.md"

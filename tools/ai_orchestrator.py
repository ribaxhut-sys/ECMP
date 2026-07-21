#!/usr/bin/env python3
"""Registry-driven AI Orchestrator (AI Platform)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import yaml

from aip_lib import (
    AIP,
    current_memory_version,
    detect_domain,
    list_agents,
    load_capabilities,
    pack_path,
    resolve_prompt,
)
from eos_lib import ROOT, meta_block
from rag_lib import search

ROUTER = AIP / "orchestrator" / "router.yaml"
OUT = AIP / "orchestrator" / "last_route.md"
TELEMETRY_DIR = AIP / "telemetry" / "runs"


def load_router():
    return yaml.safe_load(ROUTER.read_text(encoding="utf-8")) or {}


def choose_capability(task: str, router: dict, capabilities: dict) -> str:
    task_l = task.lower()
    for rule in router.get("routes", []) or []:
        keys = [k.lower() for k in rule.get("any", [])]
        if any(k in task_l for k in keys):
            return rule["capability"]
    return router.get("default_capability") or next(iter(capabilities))


def route_task(task: str) -> dict:
    router = load_router()
    agents = list_agents()
    capabilities = load_capabilities()
    cap_id = choose_capability(task, router, capabilities)
    cap = capabilities.get(cap_id, {})
    agent_id = cap.get("agent") or router.get("default_agent")
    agent = agents.get(agent_id, {})
    domain = detect_domain(task)
    mem_ver = router.get("memory_version") or current_memory_version()
    prompt_ref = cap.get("prompt") or agent.get("default_prompt")
    prompt_path = resolve_prompt(prompt_ref) if prompt_ref else None
    hits = search(task, top_k=5) if router.get("rag_enabled", True) else []

    context = []
    for item in (agent.get("context") or {}).get("required", []) or []:
        context.append(item.replace("{domain}", domain or "ecmf"))
    if router.get("pack_preferred") and domain:
        p = pack_path(domain)
        if p.exists():
            context.append(p.relative_to(ROOT).as_posix())
    for item in (agent.get("context") or {}).get("optional", []) or []:
        resolved = item.replace("{domain}", domain or "ecmf")
        context.append(resolved)

    # ensure memory versioned path preferred
    context = [
        c.replace("ai-platform/memory/v1/", f"ai-platform/memory/{mem_ver}/")
        for c in context
    ]

    return {
        "task": task,
        "capability_id": cap_id,
        "capability": cap,
        "agent_id": agent_id,
        "agent": agent,
        "domain": domain,
        "memory_version": mem_ver,
        "prompt_ref": prompt_ref,
        "prompt_path": str(prompt_path.relative_to(ROOT)) if prompt_path and prompt_path.exists() else None,
        "context": context,
        "rag_hits": hits,
        "routed_at": datetime.now(timezone.utc).isoformat(),
    }


def write_telemetry(result: dict):
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = TELEMETRY_DIR / f"route_{ts}.json"
    payload = {
        "type": "orchestrator_route",
        "timestamp": result["routed_at"],
        "task": result["task"],
        "capability_id": result["capability_id"],
        "agent_id": result["agent_id"],
        "domain": result["domain"],
        "memory_version": result["memory_version"],
        "prompt_ref": result["prompt_ref"],
        "rag_hit_count": len(result["rag_hits"]),
        "rag_top_score": (result["rag_hits"][0]["score"] if result["rag_hits"] else 0),
        "context_count": len(result["context"]),
        "success": True,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def render(result: dict) -> str:
    agent = result["agent"]
    cap = result["capability"]
    lines = [
        "# AI Orchestrator Route (Registry-driven)",
        "",
        *meta_block("ORCH-ROUTE-002"),
        f"> Task: {result['task']}",
        "",
        f"## Capability: {cap.get('name', result['capability_id'])}",
        f"- ID: `{result['capability_id']}`",
        f"- Owner: {cap.get('owner', 'n/a')}",
        f"- Status: {cap.get('status', 'n/a')}",
        f"- Input: {cap.get('input', 'n/a')}",
        f"- Output: {cap.get('output', 'n/a')}",
        "",
        f"## Agent: {agent.get('name', result['agent_id'])}",
        f"- ID: `{result['agent_id']}`",
        f"- Tool role: {agent.get('tool_role', 'n/a')}",
        f"- Memory: `{result['memory_version']}`",
        f"- Domain pack: `{result['domain'] or 'n/a'}`",
        "",
        "## Prompt",
        f"- Ref: `{result['prompt_ref']}`",
        f"- Path: `{result['prompt_path']}`",
        "",
        "## Context Pack",
        "",
    ]
    for c in result["context"]:
        lines.append(f"- `{c}`")
    lines += ["", "## RAG Top Hits", ""]
    if not result["rag_hits"]:
        lines.append("- (no hits — run rag-index)")
    else:
        for hit in result["rag_hits"]:
            lines.append(f"- `{hit['path']}` (score={hit['score']})")
    lines += [
        "",
        "## Next",
        "1. Load prompt + context in the selected tool role",
        "2. Prefer Domain Pack over whole-repo context",
        "3. After run, capture outcome via telemetry/eval gates for prompt changes",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    result = route_task(args.task)
    text = render(result)
    print(f"Capability: {result['capability_id']}")
    print(f"Agent: {result['agent'].get('name', result['agent_id'])}")
    print(f"Prompt: {result['prompt_ref']} -> {result['prompt_path']}")
    print(f"Domain pack: {result['domain'] or 'n/a'}")
    print(f"Memory: {result['memory_version']}")
    for hit in result["rag_hits"][:5]:
        print(f"- RAG [{hit['score']}] {hit['path']}")

    tel = write_telemetry(result)
    print(f"Telemetry: {tel}")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
        # Legacy mirror for ai/ compatibility layer — remove when ai/ is retired (review at Sprint-03 planning)
        legacy = ROOT / "ai" / "orchestrator" / "last_route.md"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text(text, encoding="utf-8")
        print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

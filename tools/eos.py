#!/usr/bin/env python3
"""ECMP Engineering OS — developer experience launcher (Wave A/B/C aware)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")


def run_script(args: list[str]) -> int:
    script = TOOLS / args[0]
    cmd = [sys.executable, str(script), *args[1:]]
    print("==>", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def cmd_impact(artifact_id: str | None = None, write: bool = True) -> int:
    artifact_id = artifact_id or input("Artifact ID (e.g. BR-001, API-001, EVT-002): ").strip()
    if not artifact_id:
        print("ID is required.")
        return 2
    args = ["impact_analysis.py", "--id", artifact_id]
    if write:
        args.append("--write")
    return run_script(args)


def cmd_domain(name: str | None = None) -> int:
    name = (name or input("Domain name (CRM/ECMF/KPI/Dashboard/Notification/Core Platform): ").strip() or "ECMF")
    slug = name.lower().replace(" ", "-")
    target = ROOT / "20 Domain Architecture" / "navigator" / f"{slug}.md"
    rc = 0
    # Preview the existing navigator file; only regenerate when it is missing.
    if not target.exists():
        rc = run_script(["domain_navigator.py"])
    print()
    if target.exists():
        print(f"Domain pack: {target}")
        preview = "\n".join(target.read_text(encoding="utf-8", errors="ignore").splitlines()[:35])
        try:
            print("\n--- preview ---\n" + preview + "\n---------------\n")
        except UnicodeEncodeError:
            pass
    else:
        print(f"Navigator file not found for domain '{name}'.")
        rc = max(rc, 1)
    return rc


def cmd_rag_search(query: str | None = None, write: bool = True) -> int:
    query = query or input("RAG query: ").strip()
    if not query:
        print("Query is required.")
        return 2
    args = ["rag_search.py", "--query", query]
    if write:
        args.append("--write")
    return run_script(args)


def cmd_orchestrate(task: str | None = None, write: bool = True) -> int:
    task = task or input("Task to orchestrate: ").strip()
    if not task:
        print("Task is required.")
        return 2
    args = ["ai_orchestrator.py", "--task", task]
    if write:
        args.append("--write")
    return run_script(args)


def cmd_packs(domain: str | None = None, write: bool = True) -> int:
    domain = domain or input("Domain pack (ECMF/CRM/KPI/...): ").strip() or "ECMF"
    args = ["domain_pack.py", "--domain", domain]
    if write:
        args.append("--write")
    return run_script(args)


# Single registry driving the interactive menu, argparse subparsers, and dispatch.
# Entry keys:
#   menu_key: interactive menu number (None = CLI-only)
#   command:  CLI subcommand name (None = menu-only)
#   script:   tool script + args to run via run_script
#   options:  argparse options for the subparser [(names, kwargs), ...]
#   cli:      handler for CLI invocation, receives parsed args
#   menu:     handler for interactive invocation (prompts for input)
COMMANDS: list[dict] = [
    {
        "menu_key": "1", "label": "Build AI Memory", "command": "memory",
        "help": "Build AI memory files", "script": ["build_ai_memory.py"],
    },
    {
        "menu_key": "2", "label": "Impact Analysis", "command": "impact",
        "help": "Impact analysis for an artifact ID",
        "options": [
            (("--id",), {"required": True}),
            (("--no-write",), {"action": "store_true"}),
        ],
        "cli": lambda a: cmd_impact(a.id, write=not a.no_write),
        "menu": cmd_impact,
    },
    {
        "menu_key": "3", "label": "Open Domain (Navigator)", "command": "domain",
        "help": "Preview a domain navigator page",
        "options": [(("--name",), {"default": "ECMF"})],
        "cli": lambda a: cmd_domain(a.name),
        "menu": cmd_domain,
    },
    {
        "menu_key": "4", "label": "Generate Knowledge Graph", "command": "graph",
        "help": "Generate knowledge graph", "script": ["generate_knowledge_graph.py"],
    },
    {
        "menu_key": "5", "label": "Generate API Catalog", "command": "api",
        "help": "Generate API catalog", "script": ["generate_api_catalog.py"],
    },
    {
        "menu_key": "6", "label": "Generate Event Catalog", "command": "events",
        "help": "Generate event catalog", "script": ["generate_event_catalog.py"],
    },
    {
        "menu_key": "7", "label": "Repository Health", "command": "health",
        "help": "Repository health check + reports", "script": ["ear_repo_check.py", "--write-all"],
    },
    {
        "menu_key": "8", "label": "Documentation Coverage", "command": "coverage",
        "help": "Documentation coverage dashboard", "script": ["doc_coverage.py"],
    },
    {
        "menu_key": "9", "label": "AI Review", "command": "review",
        "help": "Generate AI review pack", "script": ["ai_reviewer.py"],
    },
    {
        "menu_key": "10", "label": "Repository Metrics", "command": "metrics",
        "help": "Repository metrics snapshot", "script": ["repo_metrics.py"],
    },
    {
        "menu_key": "11", "label": "Repository Trends", "command": "trends",
        "help": "Repository trends report", "script": ["repo_trends.py"],
    },
    {
        "menu_key": "12", "label": "Build RAG Index", "command": "rag-index",
        "help": "Build the local RAG index", "script": ["rag_index.py"],
    },
    {
        "menu_key": "13", "label": "RAG Search", "command": "rag",
        "help": "Search the RAG index",
        "options": [
            (("--query",), {"required": True}),
            (("--no-write",), {"action": "store_true"}),
        ],
        "cli": lambda a: cmd_rag_search(a.query, write=not a.no_write),
        "menu": cmd_rag_search,
    },
    {
        "menu_key": "14", "label": "AI Orchestrator", "command": "orchestrate",
        "help": "Route a task via the AI orchestrator",
        "options": [
            (("--task",), {"required": True}),
            (("--no-write",), {"action": "store_true"}),
        ],
        "cli": lambda a: cmd_orchestrate(a.task, write=not a.no_write),
        "menu": cmd_orchestrate,
    },
    {
        "menu_key": "15", "label": "Domain Knowledge Pack", "command": "packs",
        "help": "Build a domain knowledge pack",
        "options": [
            (("--domain",), {"required": True}),
            (("--no-write",), {"action": "store_true"}),
        ],
        "cli": lambda a: cmd_packs(a.domain, write=not a.no_write),
        "menu": cmd_packs,
    },
    {
        "menu_key": "16", "label": "AI Evaluation", "command": "eval",
        "help": "Run AI evaluation benchmark", "script": ["eval_benchmark.py"],
    },
    {
        "menu_key": "17", "label": "AI Telemetry Report", "command": "telemetry",
        "help": "Generate AI telemetry report", "script": ["telemetry_report.py"],
    },
    {
        "menu_key": "18", "label": "Feedback Metrics", "command": "feedback",
        "help": "Generate feedback metrics", "script": ["feedback_metrics.py"],
    },
    {
        "menu_key": "19", "label": "Sync Traceability Markdown", "command": "sync-traceability",
        "help": "Sync traceability markdown from YAML", "script": ["sync_traceability_md.py"],
    },
    {
        "menu_key": "20", "label": "Run ALL generators", "command": None,
        "script": ["run_engineering_os.py"],
    },
    {
        "menu_key": None, "label": "Domain Navigator (regenerate)", "command": "navigator",
        "help": "Regenerate domain navigator pages", "script": ["domain_navigator.py"],
    },
    {
        "menu_key": None, "label": "Interactive Menu", "command": "menu",
        "help": "Show the interactive menu",
        "cli": lambda a: interactive(),
    },
]


def run_entry_interactive(entry: dict) -> int:
    if "menu" in entry:
        return entry["menu"]()
    return run_script(entry["script"])


def interactive() -> int:
    print()
    print("ECMP Engineering OS / Platform")
    print("==============================")
    menu_entries = {e["menu_key"]: e for e in COMMANDS if e["menu_key"]}
    for key, entry in menu_entries.items():
        print(f" {key:>2}. {entry['label']}")
    print("  0. Exit")
    print()
    choice = input("Select option: ").strip()
    if choice in {"0", "q", "quit", "exit"}:
        return 0
    entry = menu_entries.get(choice)
    if entry is None:
        print("Invalid option.")
        return 2
    print(f"\nRunning: {entry['label']}\n")
    return run_entry_interactive(entry)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ECMP Engineering OS launcher")
    p.add_argument("--all", action="store_true", help="Run full generator pipeline")
    sub = p.add_subparsers(dest="command")
    for entry in COMMANDS:
        if not entry["command"]:
            continue
        sp = sub.add_parser(entry["command"], help=entry.get("help"))
        for names, kwargs in entry.get("options", []):
            sp.add_argument(*names, **kwargs)
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.all:
        return run_script(["run_engineering_os.py"])

    cmd = args.command
    if cmd is None:
        return interactive()

    for entry in COMMANDS:
        if entry["command"] != cmd:
            continue
        if "cli" in entry:
            return entry["cli"](args)
        return run_script(entry["script"])

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run all Engineering OS v4 capability generators."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

# Avoid Windows console encoding failures on emoji/status glyphs
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

STEPS = [
    ["sync_traceability_md.py"],
    ["generate_api_catalog.py"],
    ["generate_event_catalog.py"],
    ["generate_knowledge_graph.py"],
    ["doc_coverage.py"],
    ["repo_metrics.py"],
    ["repo_trends.py"],
    ["domain_navigator.py"],
    ["build_ai_memory.py"],
    ["rag_index.py"],
    ["feedback_metrics.py"],
    ["impact_analysis.py", "--id", "BR-001", "--write"],
    ["ai_orchestrator.py", "--task", "implement FR-001 create case", "--write"],
    ["domain_pack.py", "--domain", "ECMF", "--write"],
    ["eval_benchmark.py"],
    ["telemetry_report.py"],
    ["ai_reviewer.py"],
    ["ear_repo_check.py", "--write-all"],
]


def main():
    print("Running Engineering OS generators...")
    for step in STEPS:
        script = TOOLS / step[0]
        cmd = [sys.executable, str(script), *step[1:]]
        print("\n==>", " ".join(cmd))
        subprocess.check_call(cmd, cwd=ROOT)
    print("\nEngineering OS generation complete.")


if __name__ == "__main__":
    main()

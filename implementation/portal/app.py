from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from rag_lib import search  # noqa: E402
from ai_orchestrator import route_task, write_telemetry  # noqa: E402

# Local-only developer tooling, unauthenticated by design. Serve it bound to
# 127.0.0.1 only (see README). Optionally set ECMP_PORTAL_TOKEN to require a
# token on POST /tools/run.
app = FastAPI(title="ECMP Developer Portal", version="0.2.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def read_text(rel: str, limit: int = 12000) -> str:
    path = ROOT / rel
    if not path.exists():
        return f"_Missing: {rel}_"
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:limit]


def run_eos(args: list[str]) -> str:
    cmd = [sys.executable, str(TOOLS / "eos.py"), *args]
    try:
        out = subprocess.check_output(cmd, cwd=ROOT, stderr=subprocess.STDOUT, text=True)
        return out[-4000:]
    except subprocess.CalledProcessError as exc:
        return (exc.output or str(exc))[-4000:]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "ECMP Developer Portal",
        },
    )


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str = "", collection: str = ""):
    hits = search(q, top_k=8, collection=collection or None) if q else []
    return templates.TemplateResponse(
        "search.html",
        {"request": request, "q": q, "collection": collection, "hits": hits},
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "coverage": read_text("00 Repository Guide/DOC_COVERAGE.generated.md"),
            "metrics": read_text("00 Repository Guide/REPO_METRICS.generated.md"),
            "trends": read_text("00 Repository Guide/REPO_TRENDS.generated.md"),
            "feedback": read_text("00 Repository Guide/FEEDBACK_METRICS.generated.md"),
            "evaluation": read_text("ai-platform/evaluation/EVAL_REPORT.generated.md"),
            "telemetry": read_text("ai-platform/telemetry/reports/TELEMETRY_REPORT.generated.md"),
        },
    )


@app.get("/impact", response_class=HTMLResponse)
def impact_page(request: Request, id: str = "BR-001"):
    output = ""
    report = ""
    if id:
        output = run_eos(["impact", "--id", id])
        report = read_text("26 Traceability/IMPACT_ANALYSIS.generated.md")
    return templates.TemplateResponse(
        "impact.html",
        {"request": request, "artifact_id": id, "output": output, "report": report},
    )


@app.get("/orchestrate", response_class=HTMLResponse)
def orchestrate_page(request: Request, task: str = ""):
    result = None
    if task:
        result = route_task(task)
        write_telemetry(result)
    return templates.TemplateResponse(
        "orchestrate.html",
        {"request": request, "task": task, "result": result},
    )


@app.post("/tools/run")
def tools_run(
    action: str = Form(...),
    token: str = Form(""),
    x_portal_token: str | None = Header(None),
):
    expected = os.environ.get("ECMP_PORTAL_TOKEN")
    if expected and token != expected and x_portal_token != expected:
        raise HTTPException(
            status_code=403,
            detail="Missing or invalid portal token (set 'token' form field or 'X-Portal-Token' header).",
        )
    mapping = {
        "all": ["--all"],
        "memory": ["memory"],
        "coverage": ["coverage"],
        "metrics": ["metrics"],
        "trends": ["trends"],
        "graph": ["graph"],
        "rag-index": ["rag-index"],
        "eval": ["eval"],
        "telemetry": ["telemetry"],
        "feedback": ["feedback"],
        "health": ["health"],
        "navigator": ["navigator"],
        "packs": ["packs", "--domain", "ECMF"],
    }
    if action not in mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action '{action}'. Valid actions: {', '.join(sorted(mapping))}.",
        )
    run_eos(mapping[action])
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/docs-link", response_class=HTMLResponse)
def docs_link(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

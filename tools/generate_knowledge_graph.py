#!/usr/bin/env python3
"""Generate enriched knowledge graph from ontology + traceability + catalogs + ADR/FRD."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from eos_lib import ROOT, list_adrs, list_events, list_openapi_ops, load_traceability, meta_block

OUT_YAML = ROOT / "ai" / "knowledge-graph" / "graph.generated.yaml"
OUT_MD = ROOT / "ai" / "knowledge-graph" / "graph.generated.md"
PORTAL = ROOT / "docs" / "architecture" / "knowledge-graph.md"
ONTOLOGY = ROOT / "ai" / "ontology" / "ontology.yaml"


def load_ontology():
    if ONTOLOGY.exists():
        return yaml.safe_load(ONTOLOGY.read_text(encoding="utf-8")) or {}
    return {}


def add_node(nodes, node_id, ntype, label, **extra):
    nodes[node_id] = {"id": node_id, "type": ntype, "label": label, **extra}


def add_edge(edges, seen, frm, to, relation):
    key = (frm, to, relation)
    if key in seen or not frm or not to:
        return
    seen.add(key)
    edges.append({"from": frm, "to": to, "relation": relation})


def _as_id_list(value):
    """Normalize OpenAPI extension ids (scalar or list) to a flat id list.

    Specs may set ``x-event`` / ``x-fr`` as a string or a YAML list when an
    operation emits/implements multiple artifacts (see case-service.v1.yaml).
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        out = []
        for item in value:
            out.extend(_as_id_list(item))
        return out
    text = str(value).strip()
    return [text] if text else []


def enrich_from_openapi(nodes, edges, seen):
    for key, spec in list_openapi_ops().items():
        path = spec.get("path")
        if not path or not path.exists():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for route, methods in (data.get("paths") or {}).items():
            if not isinstance(methods, dict):
                continue
            for method, op in methods.items():
                if method.startswith("x-") or not isinstance(op, dict):
                    continue
                api_id = op.get("x-ear-id") or f"API-{method.upper()}-{route}"
                label = op.get("summary") or f"{method.upper()} {route}"
                add_node(nodes, api_id, "API", label, path=route, method=method.upper())
                for fr in _as_id_list(op.get("x-fr")):
                    add_node(nodes, fr, "FRD", fr)
                    add_edge(edges, seen, fr, api_id, "implemented_by")
                for evt in _as_id_list(op.get("x-event")):
                    add_node(nodes, evt, "Event", evt)
                    add_edge(edges, seen, api_id, evt, "emits")


def enrich_from_adrs(nodes, edges, seen):
    for adr in list_adrs():
        title = Path(adr["path"]).stem
        add_node(nodes, adr["id"], "ADR", title, path=str(adr["path"]))
        text = adr["path"].read_text(encoding="utf-8", errors="ignore")
        for dom in re.findall(r"\b(ECMF|CRM|KPI|Dashboard|Notification|Core Platform)\b", text):
            dom_id = f"DOM-{dom.upper().replace(' ', '-')}"
            add_node(nodes, dom_id, "Domain", dom)
            add_edge(edges, seen, adr["id"], dom_id, "decided_by")


def enrich_from_frd_files(nodes, edges, seen):
    frd_dir = ROOT / "03 Functional Requirements"
    for path in frd_dir.glob("ECMP_FRD_*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        doc_id = f"DOC-{path.stem}"
        add_node(nodes, doc_id, "Document", path.name, path=str(path.relative_to(ROOT)))
        frs = set(re.findall(r"\bFR-\d+\b", text))
        brs = set(re.findall(r"\bBR-\d+\b", text))
        for fr in frs:
            add_node(nodes, fr, "FRD", fr)
            add_edge(edges, seen, doc_id, fr, "documented_in")
        for br in brs:
            add_node(nodes, br, "BusinessRule", br)
            for fr in frs:
                add_edge(edges, seen, br, fr, "constrains")
        if "ECMF" in path.name.upper():
            add_node(nodes, "DOM-ECMF", "Domain", "ECMF")
            add_edge(edges, seen, doc_id, "DOM-ECMF", "documented_in")


def main():
    ontology = load_ontology()
    links, artifacts = load_traceability()
    events = list_events()

    nodes = {}
    edges = []
    seen = set()

    add_node(
        nodes,
        "BG-001",
        "BusinessGoal",
        "Orchestrate customer service with centralized customer data",
    )
    add_node(nodes, "CAP-001", "Capability", "Complaint Management")
    add_node(nodes, "CAP-002", "Capability", "Customer Inquiry")
    add_edge(edges, seen, "BG-001", "CAP-001", "enables")
    add_edge(edges, seen, "BG-001", "CAP-002", "enables")

    for link in links:
        domain = link.get("domain")
        dom_id = f"DOM-{str(domain).upper().replace(' ', '-')}"
        add_node(nodes, dom_id, "Domain", domain)
        add_edge(edges, seen, "BG-001", dom_id, "enables")
        if domain == "ECMF":
            add_edge(edges, seen, "CAP-001", dom_id, "realized_in")
        if domain == "CRM":
            add_edge(edges, seen, "CAP-002", dom_id, "realized_in")

        bp = link.get("bp")
        br = link.get("br")
        fr = link.get("fr")
        if bp:
            add_node(nodes, bp, "Capability", artifacts.get("bp", {}).get(bp, bp))
            add_edge(edges, seen, bp, dom_id, "realized_in")
        if br:
            add_node(nodes, br, "BusinessRule", artifacts.get("br", {}).get(br, br))
        if fr:
            add_node(nodes, fr, "FRD", artifacts.get("fr", {}).get(fr, fr))
            add_edge(edges, seen, dom_id, fr, "specified_by")
            if br:
                add_edge(edges, seen, br, fr, "implemented_via")
                add_edge(edges, seen, br, fr, "constrains")
        for api in link.get("api") or []:
            add_node(nodes, api, "API", artifacts.get("api", {}).get(api, api))
            if fr:
                add_edge(edges, seen, fr, api, "implemented_by")
        for evt in link.get("events") or []:
            label = artifacts.get("events", {}).get(evt) or (events.get(evt) or {}).get("name", evt)
            add_node(nodes, evt, "Event", label)
            if fr:
                add_edge(edges, seen, fr, evt, "emits")
            for api in link.get("api") or []:
                add_edge(edges, seen, api, evt, "emits")
        for tc in link.get("tests") or []:
            add_node(nodes, tc, "Test", artifacts.get("tests", {}).get(tc, tc))
            if fr:
                add_edge(edges, seen, fr, tc, "verified_by")
        sprint = link.get("sprint")
        if sprint:
            add_node(nodes, sprint, "Sprint", sprint)
            if fr:
                add_edge(edges, seen, sprint, fr, "delivers")

    enrich_from_openapi(nodes, edges, seen)
    enrich_from_adrs(nodes, edges, seen)
    enrich_from_frd_files(nodes, edges, seen)

    # validate relation names against ontology if present
    allowed = set((ontology.get("relations") or {}).keys()) or None

    graph = {
        "version": "1.0",
        "id": "AI-KG-GEN-001",
        "ontology": "ONT-001",
        "generated_by": "tools/generate_knowledge_graph.py",
        "nodes": sorted(nodes.values(), key=lambda n: n["id"]),
        "edges": [
            e
            for e in edges
            if allowed is None or e["relation"] in allowed
        ],
    }
    OUT_YAML.write_text(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True), encoding="utf-8")

    md = [
        "# Knowledge Graph (Generated)",
        "",
        *meta_block("AI-KG-GEN-001"),
        "> Enriched from ontology + traceability + OpenAPI + FRD + ADR.",
        "",
        f"- Ontology: `{ONTOLOGY.relative_to(ROOT).as_posix()}`",
        f"- Nodes: {len(graph['nodes'])}",
        f"- Edges: {len(graph['edges'])}",
        "",
        "Machine source: `ai/knowledge-graph/graph.generated.yaml`",
        "",
        "```mermaid",
        "flowchart TD",
    ]
    for link in links[:8]:
        fr = link.get("fr")
        if not fr:
            continue
        domain = str(link.get("domain")).replace(" ", "_")
        md.append(f"  {domain}[{link.get('domain')}] --> {fr}[{fr}]")
        for api in link.get("api") or []:
            md.append(f"  {fr} --> {api}[{api}]")
        for evt in link.get("events") or []:
            md.append(f"  {fr} --> {evt}[{evt}]")
        for tc in link.get("tests") or []:
            md.append(f"  {fr} --> {tc}[{tc}]")
    md += [
        "```",
        "",
        "## Query tips",
        "",
        "- Impact: `python tools/eos.py impact --id BR-001`",
        "- Semantic search: `python tools/eos.py rag --query \"create case\"`",
        "- Orchestrate: `python tools/eos.py orchestrate --task \"implement FR-001\"`",
        "",
    ]
    text = "\n".join(md)
    OUT_MD.write_text(text, encoding="utf-8")
    PORTAL.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_YAML}")
    print(f"Wrote {OUT_MD}")
    print(f"nodes={len(graph['nodes'])} edges={len(graph['edges'])}")


if __name__ == "__main__":
    main()

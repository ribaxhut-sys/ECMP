#!/usr/bin/env python3
"""Generate markdown API Catalog index from OpenAPI YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "07 API Catalog" / "openapi"
OUT = ROOT / "07 API Catalog" / "API_CATALOG.generated.md"

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def base_prefix(data: dict) -> str:
    """Derive display prefix (e.g. /v1) from the first server URL path."""
    servers = data.get("servers") or []
    if servers and isinstance(servers[0], dict):
        url = str(servers[0].get("url", ""))
        # Strip scheme+host, keep path portion.
        if "://" in url:
            rest = url.split("://", 1)[1]
            slash = rest.find("/")
            return rest[slash:] if slash >= 0 else ""
        return url
    return ""


def load_specs():
    specs = []
    for path in sorted(SOURCE_DIR.glob("*.yaml")) + sorted(SOURCE_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        info = data.get("info") or {}
        paths = data.get("paths") or {}
        prefix = base_prefix(data)
        operations = []
        for raw_path, item in paths.items():
            if not isinstance(item, dict):
                continue
            # Path-level `servers` overrides the root prefix (e.g. /health at root).
            item_prefix = base_prefix(item) if item.get("servers") else prefix
            for method, op in item.items():
                if method not in HTTP_METHODS or not isinstance(op, dict):
                    continue
                operations.append(
                    {
                        "method": method.upper(),
                        "path": f"{item_prefix}{raw_path}",
                        "summary": op.get("summary", ""),
                        "ear_id": op.get("x-ear-id", ""),
                    }
                )
        specs.append(
            {
                "file": path.name,
                "title": info.get("title", path.stem),
                "version": info.get("version", "n/a"),
                "operations": operations,
            }
        )
    return specs


def main():
    specs = load_specs()
    lines = [
        "# API Catalog (Generated)",
        "",
        "| Field | Value |",
        "|---|---|",
        "| ID | API-CAT-001 |",
        "| Version | 0.2 |",
        "| Owner | Backend Lead |",
        "| Reviewer | Solution Architect |",
        "| Approver | Architecture Board |",
        "| Status | 🟡 Draft |",
        "| Last Review | auto |",
        "| Next Review | auto |",
        "",
        f"> Generated from OpenAPI files in `{SOURCE_DIR.relative_to(ROOT).as_posix()}`.",
        "",
        "| Spec | Title | Version | Operations |",
        "|---|---|---|---|",
    ]
    if not specs:
        lines.append("| — | No OpenAPI specs yet | — | 0 |")
        lines.append("")
        lines.append("Add files like `openapi/case-service.v1.yaml`.")
    else:
        for spec in specs:
            lines.append(
                f"| `{spec['file']}` | {spec['title']} | {spec['version']} "
                f"| {len(spec['operations'])} |"
            )
        for spec in specs:
            lines.append("")
            lines.append(f"## `{spec['file']}`")
            lines.append("")
            lines.append("| ID | Operation | Summary |")
            lines.append("|---|---|---|")
            for op in spec["operations"]:
                lines.append(
                    f"| {op['ear_id'] or '—'} | `{op['method']} {op['path']}` "
                    f"| {op['summary']} |"
                )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

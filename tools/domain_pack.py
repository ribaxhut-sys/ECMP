#!/usr/bin/env python3
"""Open/build domain knowledge pack summary for AI context loading."""

from __future__ import annotations

import argparse

from aip_lib import AIP, pack_path
from eos_lib import ROOT, meta_block

OUT_DIR = AIP / "packs" / "_active"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, help="ECMF/CRM/KPI/...")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    domain = args.domain.lower().replace(" ", "-")
    path = pack_path(domain)
    if not path.exists():
        print(f"Pack not found: {path}")
        raise SystemExit(2)

    text = path.read_text(encoding="utf-8", errors="ignore")
    print(f"Domain pack: {path}")
    preview = "\n".join(text.splitlines()[:60])
    try:
        print(preview)
    except UnicodeEncodeError:
        print(preview.encode("ascii", "replace").decode("ascii"))

    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        active = OUT_DIR / "ACTIVE_PACK.md"
        content = [
            f"# Active Domain Pack — {domain}",
            "",
            *meta_block("AIP-PACK-ACTIVE"),
            f"> Selected pack: `{path.relative_to(ROOT).as_posix()}`",
            "",
            text,
            "",
        ]
        active.write_text("\n".join(content), encoding="utf-8")
        print(f"Wrote {active}")


if __name__ == "__main__":
    main()

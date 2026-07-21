#!/usr/bin/env python3
"""Lightweight local RAG helpers (chunking + TF-IDF retrieval)."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from eos_lib import ROOT

INDEX_PATH = ROOT / "ai-platform" / "rag" / "index.json"
LEGACY_INDEX_PATH = ROOT / "ai" / "rag" / "index.json"

SOURCE_GLOBS = [
    ("ai_context", ["ai/*.md", "ai/domain/*.md", "ai/sprint/*.md", "ai/generated/*.md", "ai/rules.md"]),
    ("ai_platform_policies", ["ai-platform/policies/*.md"]),
    ("ai_platform_memory", ["ai-platform/memory/v*/memory_*.md"]),
    ("ai_platform_packs", ["ai-platform/packs/*/pack.md"]),
    ("ai_platform_prompts", ["ai-platform/prompts/*/v*/prompt.md"]),
    ("ai_platform_ontology", ["ai-platform/ontology/*.yaml", "ai-platform/ontology/*.md"]),
    ("ai_platform_eval", ["ai-platform/evaluation/facts.md"]),
    ("frd", ["03 Functional Requirements/*.md"]),
    ("traceability", ["26 Traceability/TRACEABILITY_MATRIX.md", "26 Traceability/README.md"]),
    ("adr_stack", ["05 Architecture Decision Records/ECMP_ADR_004*.md"]),
    ("implementation_docs", ["implementation/README.md", "implementation/backend/README.md"]),
    ("adr", ["05 Architecture Decision Records/ECMP_ADR_*.md"]),
    ("business_rules", ["02 Business Rules/*.md"]),
    ("catalogs", ["07 API Catalog/*.md", "08 Event Catalog/*.md", "08 Event Catalog/events/*.yaml"]),
    ("navigator", ["20 Domain Architecture/navigator/*.md"]),
    ("sprint", ["ai/sprint/Sprint-*.md"]),
    ("implementation", ["implementation/backend/README.md", "implementation/README.md"]),
]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_\-/]{2,}", text.lower())


def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    parts = re.split(r"\n(?=#{1,3} )", text)
    chunks: list[str] = []
    buf = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(buf) + len(part) + 1 <= max_chars:
            buf = f"{buf}\n\n{part}".strip()
        else:
            if buf:
                chunks.append(buf)
            if len(part) <= max_chars:
                buf = part
            else:
                for i in range(0, len(part), max_chars):
                    chunks.append(part[i : i + max_chars])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks or ([text[:max_chars]] if text.strip() else [])


def iter_source_files():
    # Globs overlap between collections; dedupe by resolved path so no file is
    # indexed twice. The first collection listed in SOURCE_GLOBS wins.
    seen: set[Path] = set()
    for collection, patterns in SOURCE_GLOBS:
        for pattern in patterns:
            for path in ROOT.glob(pattern):
                if not path.is_file():
                    continue
                resolved = path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                yield collection, path


def build_index() -> dict:
    docs = []
    doc_id = 0
    for collection, path in iter_source_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for idx, chunk in enumerate(chunk_text(text)):
            tokens = tokenize(chunk)
            if len(tokens) < 5:
                continue
            docs.append(
                {
                    "id": f"RAG-{doc_id:05d}",
                    "collection": collection,
                    "path": rel,
                    "chunk_index": idx,
                    "text": chunk,
                    "tokens": tokens,
                    "tf": dict(Counter(tokens)),
                }
            )
            doc_id += 1

    df: Counter[str] = Counter()
    for d in docs:
        for term in d["tf"].keys():
            df[term] += 1
    n = max(len(docs), 1)
    idf = {t: math.log((n + 1) / (df_t + 1)) + 1.0 for t, df_t in df.items()}

    for d in docs:
        weights = {}
        norm = 0.0
        for term, tf in d["tf"].items():
            w = (tf) * idf.get(term, 0.0)
            weights[term] = w
            norm += w * w
        d["tfidf"] = weights
        d["norm"] = math.sqrt(norm) or 1.0
        del d["tokens"]

    index = {
        "version": 1,
        "document_count": len(docs),
        "idf": idf,
        "documents": docs,
    }
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(index)
    INDEX_PATH.write_text(payload, encoding="utf-8")
    # Legacy mirror for ai/ compatibility layer — remove when ai/ is retired (review at Sprint-03 planning)
    LEGACY_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEGACY_INDEX_PATH.write_text(payload, encoding="utf-8")
    return index


def load_index() -> dict:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if LEGACY_INDEX_PATH.exists():
        return json.loads(LEGACY_INDEX_PATH.read_text(encoding="utf-8"))
    return build_index()


def search(query: str, top_k: int = 5, collection: str | None = None) -> list[dict]:
    index = load_index()
    q_terms = tokenize(query)
    if not q_terms:
        return []
    q_tf = Counter(q_terms)
    idf = index.get("idf", {})
    q_weights = {}
    q_norm = 0.0
    for term, tf in q_tf.items():
        w = tf * idf.get(term, 0.0)
        q_weights[term] = w
        q_norm += w * w
    q_norm = math.sqrt(q_norm) or 1.0

    scored = []
    for doc in index.get("documents", []):
        if collection and doc.get("collection") != collection:
            continue
        denom = doc.get("norm", 1.0) * q_norm
        if denom == 0:
            continue
        score = 0.0
        tfidf = doc.get("tfidf", {})
        for term, qw in q_weights.items():
            score += qw * tfidf.get(term, 0.0)
        score /= denom
        if score <= 0:
            continue
        scored.append(
            {
                "id": doc["id"],
                "score": round(score, 4),
                "collection": doc["collection"],
                "path": doc["path"],
                "chunk_index": doc["chunk_index"],
                "text": doc["text"][:1000],
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

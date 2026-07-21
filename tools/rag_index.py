#!/usr/bin/env python3
"""Build local RAG index for ECMP knowledge artifacts."""

from __future__ import annotations

from rag_lib import INDEX_PATH, build_index


def main():
    index = build_index()
    print(f"Indexed {index['document_count']} chunks -> {INDEX_PATH}")


if __name__ == "__main__":
    main()

# RAG / Vector Search MVP

| Field | Value |
|---|---|
| ID | RAG-000 |
| Version | 0.1 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Retrieve relevant context chunks instead of loading the whole repository into AI prompts.

## Commands
```bash
python tools/eos.py rag-index
python tools/eos.py rag --query "create case linked to customer"
```

## Outputs
- `index.json` — local TF-IDF index
- `last_context.md` — latest retrieved context pack

## Notes
This MVP uses local lexical/TF-IDF retrieval (no external vector DB).  
Upgrade path: embeddings + Chroma/Qdrant while keeping the same collections.

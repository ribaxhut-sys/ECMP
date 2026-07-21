# AI Evaluation

| Field | Value |
|---|---|
| ID | AIP-EVAL-000 |
| Version | 1.0 |
| Owner | Enterprise Architecture / QA |
| Reviewer | Agent Owners |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Regression-test prompt/agent quality using golden questions.

## Run
```bash
python tools/eos.py eval
```

## Notes
MVP scores retrieval+policy knowledge from RAG/memory/packs (deterministic checker).
Future: call live LLM answers and compare semantically.

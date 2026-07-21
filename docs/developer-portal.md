# Developer Portal

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DEV-001 |
| Version | 0.1 |
| Owner | Engineering Manager |
| Reviewer | EA / Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Run
```bash
python tools/eos.py rag-index
python tools/eos.py feedback
cd implementation/portal
pip install -r requirements.txt
uvicorn app:app --reload --port 8030
```

Open http://127.0.0.1:8030

Combines: RAG search, dashboards, impact analysis, orchestrator, EOS actions.

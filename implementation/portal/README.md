# ECMP Developer Portal

| Field | Value |
|---|---|
| ID | IMP-PORTAL-001 |
| Version | 0.1 |
| Owner | Engineering Manager / EA |
| Reviewer | Tech Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## What it combines
- RAG semantic search over EKR
- Coverage / metrics / trends / feedback dashboards
- Impact analysis
- AI Orchestrator routing
- Engineering OS actions

## Run
```bash
# from repo root, ensure indexes/reports exist
python tools/eos.py rag-index
python tools/eos.py feedback

cd implementation/portal
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8030
```

Open: http://127.0.0.1:8030

## Security posture
- The portal is **local-only developer tooling, unauthenticated by design**.
  Always bind it to `127.0.0.1` (as in the command above) — never expose it on
  a network interface.
- Optional cheap guard: set the `ECMP_PORTAL_TOKEN` environment variable before
  starting the portal to require that token on `POST /tools/run` (send it as
  the `token` form field or the `X-Portal-Token` header). When unset, no token
  is required (local dev default).

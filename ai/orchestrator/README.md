# Legacy Orchestrator (Shim)

| Field | Value |
|---|---|
| ID | AI-ORCH-SHIM-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Canonical router and route outputs live in:

- `ai-platform/orchestrator/router.yaml`
- `ai-platform/orchestrator/last_route.md`

Use:

```bash
python tools/eos.py orchestrate --task "..."
```

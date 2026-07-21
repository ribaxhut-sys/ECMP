# AI Orchestrator

| Field | Value |
|---|---|
| ID | EAR-PORTAL-ORCH-002 |
| Version | 2.0 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Registry-driven orchestrator (Wave C):

```bash
python tools/eos.py orchestrate --task "implement FR-001 create case endpoint"
```

Reads:
- `ai-platform/orchestrator/router.yaml`
- `ai-platform/agents/*.yaml`
- `ai-platform/capabilities/registry.yaml`

Portal UI: `/orchestrate`

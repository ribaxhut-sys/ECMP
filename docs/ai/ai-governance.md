# AI Governance

| Field | Value |
|---|---|
| ID | EAR-PORTAL-AIP-GOV-001 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

Source: `ai-platform/policies/ai-governance.md` and `ai-platform/policies/ai-rules.md`.

## Gates
- Prompt/agent changes should pass evaluation threshold (`python tools/eos.py eval --strict` in CI gates).
- Orchestrator routes emit telemetry under `ai-platform/telemetry/runs/`.
- Capabilities and agents are registry-owned (no ad-hoc hardcoded agent logic in tools).

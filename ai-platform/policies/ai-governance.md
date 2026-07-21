# AI Governance Policy

| Field | Value |
|---|---|
| ID | AIP-GOV-001 |
| Version | 1.0 |
| Owner | Architecture Board |
| Reviewer | EA / Eng Manager / Security |
| Approver | CIO / Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Decision Rights

| Change type | Proposed by | Reviewed by | Approved by |
|---|---|---|---|
| AI Rules (`policies/ai-rules.md`) | EA / Tech Lead | Architecture Board | Architecture Board |
| Prompt (experimental → candidate) | Any engineer | Agent Owner | Agent Owner |
| Prompt (candidate → stable) | Agent Owner | EA + Eval evidence | Architecture Board |
| New Agent | EA / Domain Lead | Architecture Board | Architecture Board |
| New Capability | Agent Owner | EA | Architecture Board |
| Memory major version | EA / BA | Domain POs | Architecture Board |
| Rollback prompt/memory | Agent Owner or EA | — | Agent Owner (emergency) / Board (stable) |

## Stability States
- `experimental` — may change freely; not for production workflows
- `candidate` — under evaluation; needs golden-set score
- `stable` — approved for default routing; changes require eval + approval
- `deprecated` — replaced; keep for rollback history

## Evaluation Gate
Sebelum prompt/agent `stable`:
1. Jalankan `python tools/eos.py eval`
2. Skor suite terkait >= threshold (default 0.80)
3. Tidak ada regression > 5 poin vs versi sebelumnya
4. Catat hasil di `telemetry/reports/`

## Rollback
1. Set `current` pointer ke versi sebelumnya di prompt/memory manifest
2. Catat alasan di `27 Project Decisions` atau ADR bila arsitektural
3. Re-run eval untuk konfirmasi recovery

## Adding a New Agent
1. Buat `agents/<name>.yaml`
2. Daftarkan capability di `capabilities/registry.yaml`
3. Sediakan prompt v1 + evaluation suite
4. Lulus eval gate
5. Update orchestrator routes bila perlu

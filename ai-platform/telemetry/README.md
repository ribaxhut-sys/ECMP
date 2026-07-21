# AI Telemetry

| Field | Value |
|---|---|
| ID | AIP-TEL-000 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Eng Manager |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Layout
- `runs/` — per-route JSON logs from orchestrator
- `reports/` — aggregated reports (`TELEMETRY_REPORT.generated.md`, `eval_latest.json`)

## Commands
```bash
python tools/eos.py orchestrate --task "..."
python tools/eos.py telemetry
```

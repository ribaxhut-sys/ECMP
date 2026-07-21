# 06 — Events Context

| Field | Value |
|---|---|
| ID | AI-CTX-006 |
| Version | 1.0 |
| Owner | Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Source of Truth
`08 Event Catalog/events/events.yaml`

## Baseline Events
| ID | Name |
|---|---|
| EVT-001 | CaseCreated |
| EVT-002 | CaseAssigned |
| EVT-003 | StatusChanged |
| EVT-004 | SLABreached |
| EVT-005 | CaseClosed |
| EVT-006 | ConfigChanged |
| EVT-007 | CaseReopened (Proposed) |

## Rules
- No new event outside Event Catalog (`events/events.yaml` — satu-satunya SoT; duplikat v1.0 sudah dihapus per ARB 2026-07-21).
- Producers/consumers must be explicit (kini tercantum per event di SoT).
- Consumers MUST be idempotent (delivery at-least-once, ADR-001).
- Emisi event via transactional outbox (ADR-009) — dilarang emit di luar transaksi write.
- Payload camelCase (naming standard `21 Technical Standards`).
- Regenerate catalog markdown after edits:
  `python tools/generate_event_catalog.py`

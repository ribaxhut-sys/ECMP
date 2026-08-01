# Decision Record — G2 Mini-Gate (Mode A)

| Field | Value |
|---|---|
| ID | DEC-021 |
| Version | 1.0 |
| Owner | Solution Architect / Tech Lead |
| Reviewer | ECMF PO / QA Lead |
| Approver | Lab Architecture (W-SOD-1 disclosed) |
| Status | 🟢 Accepted (Mode A lab) |
| Last Review | 2026-08-01 |
| Next Review | 2026-10-01 |
| Type | Project Decision (non-ADR) — G2 exit for Mode A path |
| Related | ADR-009, DEC-006, DEC-020, ACR-002, TS-OBS-001, PROGRAM-BOARD-004 C-7 |

## Context

G1 exited (DEC-006; `deploy/evidence/G1_Exit_Verified_20260801.md`). Roadmap G2-S1…S4 were still OPEN/PARTIAL. Mode B / Batch-2 / enterprise customer remain **CLOSED** (C-7). This DEC closes the **Mode A** mini-gate so Sprint-03 residual and SIT can proceed without inventing broker/IdP.

## Decisions

### G2-S1 — Broker revisit → **extend in-process outbox**

1. **No physical broker** for Mode A SIT/UAT wave-1.  
2. Official transport remains **transactional outbox + in-process drain** (ADR-009 §2).  
3. First multi-process KPI/SLA consumer (Sprint FR-030 event clock) **re-triggers** broker evaluation; until then do not build generic multi-broker frameworks.  
4. Recorded as ADR-009 Addendum G2 (`ECMP_ADR_009_Addendum_G2_InProcess_Extension_v1.0.md`).

### G2-S2 — Customer Master → **remain stub; API-010 stays deferred**

1. Affirm ACR-002: **do not** implement Customer 360 with fabricated profile fields.  
2. INT-001A RFI may continue offline; Mode A DoD **does not** require API-010.  
3. Real CM mode is a future G2 re-open when sandbox exists — not a Mode A blocker.

### G2-S3 — Observability → **Mode A floor accepted**

1. Binding for Mode A: JSON logs + `X-Request-ID` on both `implementation/backend` and `backend/` (see `Observability_Minimum_20260801.md` + `deploy/smoke-lab.sh`).  
2. TS-OBS-001 document remains Draft for full metrics/APM; Mode A claims only the floor in §1–§3 of that standard.  
3. Prometheus/Grafana/Sentry **out of scope** for this DEC.

### G2-S4 — Regression pack & runbook → **adopted**

1. Named pack: `implementation/backend/REGRESSION_PACK_G2.md`.  
2. Operator path: `implementation/backend/DEV_RUNBOOK.md`.  
3. Exit command: `implementation/backend/scripts/run_g2_regression.sh` (pytest subset).

### DEC-006 U-1 — Reopen subset → **out of Mode A DoD**

1. Configured workflow subset **excludes** `CLOSED→REOPENED` (already in `workflow.py`).  
2. EVT-007 remains Proposed; no reopen implementation until separate freeze + U-4.  
3. This closes U-1 for Mode A planning; does not delete reopen from long-term DOM.

### Dual-tree SIT SoT (under DEC-020)

| Use | SoT |
|---|---|
| Contract / lifecycle conformance (API-003/004/005, FR-020, 409 semantics) | `implementation/backend` + `case-service.v1.yaml` |
| Lab edge / VPS operator surface (today’s live host) | `backend/` + `/api/v1/complaints` (+ cm_batch1 as applicable) |

No forced merge. Future Retirement DEC still required to collapse trees.

## Explicit non-decisions

- Mode B / OIDC production issuer  
- Inventing Customer Master profile stub  
- Claiming Production Enterprise Ready  
- Selecting RabbitMQ/Kafka now  

## Exit declaration

**G2 mini-gate EXITED for Mode A lab** under W-SOD-1. Evidence: `deploy/evidence/G2_Mini_Gate_Mode_A_20260801.md`.

## Links

- `ai/sprint/IMPLEMENTATION_ROADMAP_v0.1.md` §G2  
- DEC-006, DEC-020, ACR-002, Board C-7  

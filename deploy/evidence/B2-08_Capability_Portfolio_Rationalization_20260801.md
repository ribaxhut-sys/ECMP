# B2-08 — Capability Portfolio Rationalization

| Field | Value |
|---|---|
| Document ID | GOV-B2-08-PORTFOLIO-001 |
| Sprint | B2-08 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board / Portfolio Governance / Chief Product Architect |
| Scope | Portfolio review + roadmap recommendation **only** (no BE/FE/BR/FRD/OpenAPI edits) |
| Prerequisite | B2-07 ENGINEERING ALIGNMENT COMPLETE |
| CAP-008 | **Out of re-open** — Program CLOSED (lab); disposition Remain (closed) |
| Verdict | **PORTFOLIO RATIONALIZATION COMPLETE** |

## 1. Non-goals

No feature implementation · no Backend/Frontend/OpenAPI/BR/FRD content changes · no CAP-008 redesign · no Mode B · no invented artifacts beyond this governance record + register disposition metadata.

## 2. Portfolio scope

Remaining capabilities after CAP-008 Program Closure: **CAP-001 … CAP-007**.  
CAP-008 recorded for completeness as **CLOSED / Remain (no follow-up delivery)**.

## 3. Dispositions (repository evidence)

| CAP | Disposition | Rationale (evidence-only) |
|---|---|---|
| CAP-001 | **Remain** | Implemented Sprint slice; dual-SoT with Aggregate (DEC-020) — merge only via future Retirement DEC |
| CAP-002 | **Remain** | Implemented Sprint slice; Aggregate Mode A assignment is unit-level under CAP-008 — soft overlap, not retire |
| CAP-003 | **Remain** | Implemented Sprint slice; status matrix coexistence with CAP-008 — soft overlap |
| CAP-004 | **Stay Deferred** | TRC-L-005 Planned; ACR-002 deferred; API-010 draft; no FR-010 engine |
| CAP-005 | **Remain (stub) · Stay Deferred (prod)** | TRC-L-006 Approved stub only; production delivery not evidenced |
| CAP-006 | **Stay Deferred** | TRC-L-007 Planned; SLA foundation ≠ FR-030/EVT-004 |
| CAP-007 | **Stay Deferred · Merge candidate** | TRC-L-008 Planned; foundation `/api/v1/dashboard/queue` + API-513 ≠ API-040 — rationalize before build |
| CAP-008 | **Remain (CLOSED)** | Program Closure — no delivery reopen |

## 4. Ranked next engineering (open work)

1. CAP-007 contract rationalization (docs/governance → then eng)  
2. CAP-006 SLA breach engine (after CAP-003 event surface clarity)  
3. CAP-004 Customer 360 (after ACR-002 / FRD DoR)  
4. CAP-005 notification productionize (after catalog/engine gate)  
5. CAP-001/002/003 — keep-green / dual-SoT hygiene only (not new feature)

Adjacent (not CAP-00x register IDs): FRD-CM-002 Escalation/Resolution Board LOCK path; Production `v1.2.0` (external IdP).

## 5. Recommended sprints

| Sprint | Focus | Why |
|---|---|---|
| B2-09 | Dual-SoT coexistence inventory + keep-green Batch-1/CAP-008 | Protect CLOSED delivery; DEC-020 hygiene before new CAP builds |
| B2-10 | CAP-007 API-040 vs foundation queue vs API-513 disposition | Highest repo drift + supervisor value; avoid third queue surface |
| B2-11 | CAP-006 FRD DoR + SLA breach design freeze | Core complaint KPI; depends soft on status/close events |
| B2-12 | CAP-004 unlock package (ACR-002 revisit + FRD DoR) | High agent value; external CRM dependency |
| B2-13 | CAP-005 stub → governed delivery (or explicit DEFER) | Lowest urgency among open CAPs |

## 6. Related

- Capability Register: `01 Business Blueprint/ECMP_Capability_Register_v0.1.md`  
- B2-07: `deploy/evidence/B2-07_Repository_Capability_Alignment_20260801.md`  
- CAP-008 reset: `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md`

---

*End of GOV-B2-08-PORTFOLIO-001.*

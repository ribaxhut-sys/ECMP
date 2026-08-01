# CAP-008 Governance Baseline

| Field | Value |
|---|---|
| Document ID | GOV-CAP008-CLOSE-007 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 **Frozen** |
| Authority | Architecture Review Board |

## 1. Governing instruments (locked / recorded)

| Instrument | ID / Path | Status |
|---|---|---|
| Constitution | ECMP-CONSTITUTION-001 v1.1 | LOCKED |
| Master Prompt | ECMP-MASTER-PROMPT-001 v1.1 | LOCKED |
| Board Mode B gate | PROGRAM-BOARD-004 C-7 · BOARD-006 C-B6-1 | Mode B **CLOSED** |
| BQ Lock Pack | DEC-MODEA-B2-001 | APPROVED · Residual BQ ZERO |
| Case state dual SoT | DEC-BQ001 O3 | APPROVED |
| Namespace coexistence | DEC-020 | Approved |
| Canonical trees | DEC-019 | Approved |
| Implementation posture | PROGRAM-IMPLEMENTATION-001 / BR-008 | AUTHORIZED WITH CONDITIONS (historical) |
| ADR module posture | ADR-014 / ADR-015 | Accepted with Conditions |

## 2. CAP-008 control gates (closed)

| Gate | Result |
|---|---|
| Business Lock | READY |
| Board Unlock (Mode A delivery baseline) | READY |
| FRD Lock | LOCKED |
| Lab RC | PASS |
| SoT Closure | COMPLETE |
| Program Closure | **CLOSED** (this pack) |

## 3. Change control after closure

| Change type | Required |
|---|---|
| CAP-008 FRD / BCS / BQ reopen | New DEC + Board / BO approval |
| OpenAPI API-530…535 breaking change | Impact Analysis + catalog CR; not silent |
| Production promote `v1.2.0` | REL-SEC-001 GO + REL-APR-001 + real IdP contract |
| Mode B enablement | Explicit Board Unlock Resolution + org-gap + IdP contract |

## 4. Follow-up = NONE (for closed program)

No open CAP-008 Mode A delivery actions remain under this program.  
External Production / Mode B items are **not** CAP-008 program backlog.

---

*End of GOV-CAP008-CLOSE-007.*

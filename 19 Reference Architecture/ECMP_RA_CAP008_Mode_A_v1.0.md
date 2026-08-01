# CAP-008 Mode A — Reference Architecture (As-Built)

| Field | Value |
|---|---|
| Document ID | REF-CAP008-001 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Status | 🔒 **Baseline** (describes closed Mode A delivery) |
| Authority | Architecture Review Board |
| Capability | CAP-008 |
| Normative parents | ADR-005 · ADR-014 · DEC-019 · DEC-020 · DEC-BQ001 O3 · DEC-MODEA-B2-001 |
| Does not | Redesign CAP-008 · Change BR · Change OpenAPI · Unlock Mode B |

## 1. Purpose

Record the **as-built** reference shape of CAP-008 Mode A so future work integrates without rewriting the domain.

## 2. Context

```text
[ Frontend Mode A UI ]
        |  HTTPS
[ Backend FastAPI — root backend/ ]
        |
   +----+----+------------------+
   |         |                  |
 cm_case  cm_batch1         foundation
 /api/v1/cm/cases*   /api/v1/cm/*intake   /api/v1/complaints*
   |         |                  |
   +----+----+------------------+
        |
   PostgreSQL (Alembic incl. 0046_cm_case_management)
```

Canonical trees: DEC-019 — root `backend/`, `frontend/`.  
Dual SoT: DEC-020 — Aggregate CM vs foundation complaints — coexistence until Retirement DEC.

## 3. Aggregate Case (CAP-008)

| Concern | Mode A baseline |
|---|---|
| API | API-530…535 — `cm-case-management.v1.yaml` v1.0.0 |
| Module | `backend/app/modules/cm_case/` |
| Status SoT | BR-CM-CAT Definition B (DEC-BQ001 O3) |
| Exposed statuses | CREATED · ASSIGNED · IN_PROGRESS · RESOLVED · CLOSED · CANCELLED |
| Not exposed | PENDING · ESCALATED (BQ-009) |
| Assignment | Unit only (BQ-006) |
| Close Case | MUST NOT auto-close Complaint (BQ-007) |
| AuthN | Mode A lab credential / local — Mode B CLOSED |

## 4. Layering

Follows ADR-005 backend layering inside `cm_case` (router → service → repository/domain).  
No message broker required for Mode A CAP-008 (ADR-009 deferral; in-process side effects for audit/timeline per RC evidence).

## 5. Integration boundaries (unchanged)

| Boundary | Posture |
|---|---|
| Customer Master | Not SoR (ADR-002); Batch-1 stubs / EX exceptions |
| Identity / IdP | Mode B blocked pending bilateral contract |
| Notification / SLA / Assignment engines | Out of CAP-008 Mode A |

## 6. Related patterns

- `19 Reference Architecture/PATTERNS.md` (REF-001)
- Constitution ECMP-CONSTITUTION-001 LOCKED

---

*End of REF-CAP008-001.*

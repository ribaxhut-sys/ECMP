# Glossary

| Field | Value |
|---|---|
| ID | EAR-PORTAL-MIRROR |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The controlled ECMP glossary (GLS-001, 🟢 Approved baseline) defines the business and technical vocabulary used across the repository:

- Core business terms: ECMP, Case, Complaint, Inquiry, Customer, Assignment, Escalation, Priority vs Severity, SLA, KPI, Root Cause, Resolution, Reopen.
- Case status enum baseline: `REGISTERED`, `ASSIGNED`, `IN_PROGRESS`, `PENDING_REVIEW`, `CLOSED`, `REOPENED`.
- Closed enums: Case Type (`COMPLAINT` | `INQUIRY`) and Priority (`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`).
- All seven domain events EVT-001..EVT-007 with producers.
- Architecture/DDD terms: Bounded Context, Aggregate, Transactional Outbox, Write-Audit, Error Envelope, Configuration First.
- Explicit out-of-scope terms per DEC-001 (Branch / Head Office / Work Order / Schedule Slot).

**Canonical source:** `25 Glossary/GLOSSARY.md` — open it in the repository for the full controlled document.

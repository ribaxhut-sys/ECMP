# Repository Dashboard

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

The repository dashboard (EAR-IDX-002) steers the documentation roadmap by combining:

- A pointer to the generated health report (`REPO_HEALTH_REPORT.md`) as machine truth, refreshed via `python tools/ear_repo_check.py --write-all`.
- A manually maintained **product maturity** table per area (Blueprint 85% approved, Glossary, Templates, Traceability, Solution/Reference/Domain Architecture, catalogs, ADR, Security, Test, Deployment, Operations, Portal).
- A **domain maturity** table for the seven ECMP domains with progress bars.

Use it to see at a glance which knowledge areas are baseline-approved versus still starter/draft.

**Canonical source:** `00 Repository Guide/REPO_DASHBOARD.md`.

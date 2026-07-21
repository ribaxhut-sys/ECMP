# Health Report

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

The generated repository health report (machine truth, produced by `tools/ear_repo_check.py` — do not edit manually) tracks:

- Overall health score (currently 100%) across ~300 markdown files.
- Metadata completeness: missing/incomplete metadata tables, missing owners.
- Broken internal links and overdue reviews.
- README coverage for every numbered folder (00–27) and an inventory of markdown files per folder.
- ADR count (11 records found).

Regenerate with `python tools/ear_repo_check.py --write-all` (or `python tools/eos.py --all`).

**Canonical source:** `00 Repository Guide/REPO_HEALTH_REPORT.md`.

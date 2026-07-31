# Split Plans — VPS Mixed Commits (E-05 / C-01…C-04)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | **DRAFT — awaiting Tech Lead (+ BE/FE) approval** |
| Source paths | Phase 0 §3.1 |
| Rule | Do not cherry-pick until this document is approved |

---

## C-01 — `96f52eb` (Risk High) — SPLIT

**Subject:** Add HTTPS edge cutover for pengaduan.layanankami.tech.

| Unit | Target pick content | Paths |
|---|---|---|
| A — Infra / edge | Cherry-pick candidate (after Security+Deploy review) | `deploy/Caddyfile`, `docker-compose.prod.yml`, `deploy/backup-postgres.sh`, `.env.prod.example`, `.gitignore` |
| B — Docs / DEC | Separate pick or defer | `27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md`, `deploy/README.md`, `deploy/SMOKE_UAT_2026-07-31.md` |

**Notes:** High flags (Phase 0 §7 / Phase 1): `ENVIRONMENT=production`, secret key templates, edge `/docs*` `/openapi.json`. Unit B may land after Unit A; do not recombine into one Mixed commit on release branch.

---

## C-02 — `2f1348a` (Risk Medium) — SPLIT

**Subject:** Fix user provisioning so new accounts get IAM permissions.

| Unit | Target pick content | Paths |
|---|---|---|
| A — IAM app | Cherry-pick candidate | `backend/app/modules/users/repository.py`, `backend/app/modules/users/service.py`, `backend/tests/test_users.py` |
| B — Lab seed / deploy docs | Separate or defer | `deploy/seed-lab-master-data.sql`, `deploy/README.md`, `deploy/SMOKE_UAT_2026-07-31.md` |

**Notes:** `deploy/README.md` / `SMOKE_UAT_*` also touched by `96f52eb` (textual overlap A→M). Resolve on release branch per C-08. Seed is lab-data sensitive (D-04).

---

## C-03 — `a476ebf` (Risk Medium) — SPLIT

**Subject:** Add Users and Reports admin screens for the live lab.

| Unit | Target pick content | Paths |
|---|---|---|
| A — Users/Reports UI+API | Cherry-pick candidate | `frontend/src/app/(app)/reports/page.tsx`, `frontend/src/app/(app)/users/page.tsx`, `frontend/src/features/reports/ReportsView.tsx`, `frontend/src/features/reports/index.ts`, `frontend/src/features/users/UsersManagement.tsx`, `frontend/src/features/users/index.ts`, `frontend/src/lib/api/index.ts`, `frontend/src/lib/api/roles.ts`, `frontend/src/lib/api/users.ts` |
| B — Ops evidence | Separate KEEP-style pick | `deploy/evidence/backup-verify-20260731.md` |

**Notes:** Behavioral overlap with `2f1348a` (users lifecycle). Promote Unit A only with IAM Unit A from C-02 unless Product scopes UI-only.

---

## C-04 — `41a0f48` (Risk Medium) — SPLIT

**Subject:** Add login rate limiting and tighten SSH with UFW limit.

| Unit | Target pick content | Paths |
|---|---|---|
| A — Rate-limit app | Cherry-pick candidate | `backend/app/core/errors.py`, `backend/app/core/rate_limit.py`, `backend/app/modules/auth/router.py`, `backend/tests/test_rate_limit.py` |
| B — Evidence | Separate | `deploy/evidence/hardening-20260731.md` |

**Out of Git:** UFW SSH host hardening mentioned in commit message — **not** in tree; do not assume it travels with cherry-pick (D-06).

**Notes:** Behavioral/deploy dependency on Caddy / `X-Forwarded-For` from `96f52eb` Unit A. Pick after edge infra if rate-limit IP keying is in scope.

---

## C-05 — `ad4a373` — KEEP (no split)

| Unit | Paths |
|---|---|
| Whole | `deploy/evidence/restore-drill-20260731.md` |

---

## Recommended pick sequence (after approvals)

1. `96f52eb` Unit A (infra)  
2. `96f52eb` Unit B (docs) — optional / ordered after A  
3. `2f1348a` Unit A (IAM)  
4. `2f1348a` Unit B (seed/docs) — optional  
5. `a476ebf` Unit A (UI)  
6. `a476ebf` Unit B + `ad4a373` + `41a0f48` Unit B (evidence chain)  
7. `41a0f48` Unit A (rate-limit)

Exact sequence may collapse evidence units; **must not** re-merge Mixed boundaries.

---

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Tech Lead | _pending_ | | Approve / Reject |
| Backend Lead | _pending_ | | Approve / Reject (C-02, C-04) |
| Frontend Lead | _pending_ | | Approve / Reject (C-03) |

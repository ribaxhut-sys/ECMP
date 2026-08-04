# Evidence Pack — EBS-001: Organization Location + Complaint Module Authorization

| Field | Value |
|---|---|
| Date | 2026-08-04 |
| Mode | A (`ECMP_AUTH_MODE=dev`) |
| Status | **Commits 1–7 implemented, reviewed per-commit; PR not yet opened** |
| Batch | EBS-001 / IP-001 (approved), gated by DG-001 (PASS) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Prior baseline | `deploy/evidence/User_Branch_Required_BranchScopedRoles_20260804.md` — the branch-**required** direction (branch-scoped roles) predates this batch and is not re-documented here |

This pack documents what Commits 1–7 actually implemented, with the evidence gathered while implementing each. It is written for PR review, not for a production deployment gate — the heavier `ECMP_Release_Evidence_Template_v1.0.md` (DB backup/restore, OIDC confirmation, recovery drill) does not apply here: this batch has no migration, no deployment, and no identity-contract change.

---

## 1. Scope

What this batch implemented, in the order it was built:

1. **Backend — organization-location enforcement, second direction.** The existing rule (branch-scoped roles require a branch — see prior baseline above) is now paired with its mirror: head-office scoped roles (`ADMIN`, `ADMINISTRATOR`, `HO_SCHEDULER`, `HEAD_OFFICE_SCHEDULER`, `SCHEDULER`, `HO_ENGINEER`, `HEAD_OFFICE_ENGINEER`) must **not** carry a `branchId`. `SUPER_ADMIN` is explicitly exempted from both directions, evaluated first.
2. **OpenAPI** — `UserCreateRequest.branchId` / `UserUpdateRequest.branchId` descriptions updated to state both directions and the exception, matching the code exactly.
3. **Frontend — location-aware Create User.** The branch selector now has three states driven by the selected role: required (branch-scoped), disabled + forced null (head-office scoped), optional (SUPER_ADMIN / unclassified — unchanged). `BRANCH_SUPERVISOR` displays as "Manager Cabang" in the role picker (presentation only).
4. **Frontend — Pusat/Cabang directory badge.** User directory list and preview panel show a badge derived from `branchId` presence.
5. **Frontend — Complaint navigation gate.** The sidebar's Complaints item is now hidden unless the signed-in user holds at least one of the canonical complaint permissions.
6. **Frontend — Complaint layout gate.** Direct URL access to `/complaints` and every descendant route is now blocked for users without a complaint permission, reusing the exact same permission metadata as the navigation gate.

## 2. Files

16 files touched across 7 commits. High-level only — see each commit's own report for line-level detail.

| Area | Files | Commits |
|---|---|---|
| Backend | `backend/app/modules/users/service.py`, `backend/app/core/user_messages.py` | 1, 2 |
| Backend tests | `backend/tests/test_users.py` (+24 test cases, 19→43) | 3 |
| OpenAPI | `07 API Catalog/openapi/complaint-service.v1.yaml` (2 description blocks only) | 4 |
| Frontend — Create User / Directory | `CreateUserModal.tsx`, `directoryHelpers.ts`, `directoryHelpers.test.ts`, `DirectoryPeopleList.tsx`, `DirectoryPreviewPanel.tsx`, `DirectoryLocationBadge.tsx` (new) | 5 |
| Frontend — Navigation gate | `shared/layouts/app-layout/nav.ts`, `Sidebar.tsx`, `nav.test.ts` | 6 |
| Frontend — Layout gate | `src/app/(app)/complaints/layout.tsx` (new) | 7 |
| i18n | `frontend/messages/en.json`, `frontend/messages/id.json` | 5, 7 |

**Working-tree caveat (carried from every commit report):** several of these files — `user_messages.py`, `service.py`, `test_users.py`, `nav.ts`, `Sidebar.tsx`, `en.json`, `id.json` — already contained substantial **unrelated, pre-existing uncommitted work** before this batch started (a parallel UI redesign effort visible across `dashboard/`, `settings/`, `cwx/`, `auth/`, etc.). Every commit report in this batch traced and disclosed the exact lines this batch is responsible for versus what predates it. `git diff` against `HEAD` on these files will show more than this batch's own change — see §9 (Rollback) for the practical consequence.

## 3. Architecture

**Organization-location enforcement.** One method, `UserService._ensure_branch_for_role`, is the single point of enforcement for both `create()` and `update()`. Evaluation order: (1) unknown role → skip; (2) `SUPER_ADMIN` → branch optional, validated if present, **evaluated before both scoped sets**; (3) branch-scoped → required; (4) head-office scoped → forbidden; (5) fallback → optional. No new table, no new column — `branchId` and role code are the only inputs, exactly as before this batch.

**Complaint module authorization (frontend).** Two independent enforcement points now exist, both reading the same data:
- **Navigation gate** (Commit 6) — `Sidebar.tsx` hides the Complaints item when `isNavItemVisible(complaintsNavItem, hasPermission)` is false. Presentation only; does not stop a direct URL hit.
- **Layout gate** (Commit 7) — `frontend/src/app/(app)/complaints/layout.tsx` calls the identical `isNavItemVisible` with the identical `APP_NAV_ITEMS` entry, and renders the existing `Empty`/"Access Denied" pattern instead of `children` when it returns false. This is what actually stops direct URL access — Next.js executes a route's `layout.tsx` on every render of that subtree, including a fresh browser navigation straight to `/complaints/123`.

**Single source of truth.** `nav.ts` declares exactly one permission list, on exactly one `NavItem` (`complaints`), sourced from `backend/app/core/rbac.py`'s existing complaint permission family (`complaints:read/create/update/assign/escalate/close` — verified by `grep`, not guessed). The layout gate does not declare a second list; it looks up the same `NavItem` by `id` from the same `APP_NAV_ITEMS` array and calls the same pure function. Wildcard (`*`) handling lives in exactly one place, `AuthProvider.hasPermission`, and is never reimplemented — both gates receive `hasPermission` as a parameter and never inspect `"*"` themselves.

## 4. Out of Scope

Explicitly not touched by this batch, per EBS-001 §1 and this batch's own constraints, reaffirmed here:

- **Mode B**, **Enterprise** entitlement, **OIDC**, **Identity Adapter** — no identity-contract file touched; `ECMP_AUTH_MODE` behavior unchanged.
- **CAP-006**, **CAP-005**, **DEC-F4**, **M4** — none referenced or modified by any commit in this batch.
- Permission catalog / role catalog — zero new permission strings, zero new role codes (confirmed: every code referenced already existed in the `roles` table per DG-001's query).
- Assignment policy (`role_assignment_policy.py`) — not touched.
- Database schema / migrations — none created; `alembic_version` unchanged.
- Router files — no `router.py` touched in any commit.
- CI workflow files — not touched by this evidence commit either.
- No feature beyond the six items in §1.

## 5. Acceptance Criteria Summary

All AC from EBS-001 §4 and each commit's own AC section are satisfied; consolidated by area:

**Backend (AC-B1–B11, EBS-001 §4.1):** branch-scoped roles unchanged (required); all 7 head-office codes reject a present `branchId` and accept null; `SUPER_ADMIN` accepts both, still validated for branch existence when present; update-path re-validation fires on role or branch change and stays silent otherwise; unclassified roles (`VIEWER`) unaffected; message resolved via `m("user.branch_forbidden_for_role")`, no literal strings.

**OpenAPI (AC-O1–O5):** both `branchId` descriptions name the full role sets and the `SUPER_ADMIN` exception; diff limited to two `description` fields; all 11 specs (incl. drafts) pass `openapi_spec_validator`.

**Frontend — Create User / Directory (AC-F1–F6 equivalents, Commit 5):** role switch immediately updates the branch selector (enabled+required / disabled+cleared / optional) with no page refresh; head-office submission always sends `branchId: null`; `BRANCH_SUPERVISOR` displays as "Manager Cabang" without touching `role.code`/`role.name`; directory list and preview panel both show the Pusat/Cabang badge derived from `branchId`.

**Frontend — Navigation gate (Commit 6):** users holding at least one of the six canonical complaint permissions see the Complaints nav item; users holding none do not; wildcard (`*`) continues to grant visibility through `AuthProvider.hasPermission`, not a reimplementation.

**Frontend — Layout gate (Commit 7):** Navigation and Layout consume the identical `APP_NAV_ITEMS` entry and the identical `isNavItemVisible` function (verified: zero permission-string literals in `layout.tsx`); users with a complaint permission can reach `/complaints` and descendants; users without one are blocked and shown the existing `Empty`/"Access Denied" pattern already used elsewhere in the app; direct URL access is now protected (the mechanism is the Next.js layout itself, which runs on every render of the subtree); wildcard continues to work.

## 6. Tests

**Backend** — `cd backend && pytest -q tests/test_users.py`: **43/43 passed** (19 pre-existing + 24 added in Commit 3, covering every AC in §5). Adjacent suites `test_secmig_p4_org_scope.py`, `test_users_repository_coverage.py`, `test_users_schema_coverage.py`: **45/45 passed**. `ruff check app tests`: clean at every commit.

**Known pre-existing failures (not caused by this batch):** 9 failures across `test_force_password_change.py` (1), `test_primary_role_sync.py` (3), `test_role_assignment_policy.py` (5) — all traced in Commit 1 by reconstructing the exact pre-Commit-1 file state and re-running: identical 9 failures occurred with none of this batch's code present. Root cause: those fixtures create an `AGENT` user without a `branchId`, tripping the **pre-existing** branch-required rule (see prior baseline, §0) that predates this entire batch. Re-verified identical in Commits 2 and 3. Not fixed — out of scope, "do not attempt unrelated fixes" was explicit at every commit.

**Frontend** — `npm run typecheck` and `npm run lint` (`eslint . --max-warnings 0`, full repo): clean at every commit, no exceptions. `directoryHelpers.test.ts`: **11/11 passed** (6 pre-existing + 5 added in Commit 5). `nav.test.ts`: **11/11 passed** (5 pre-existing + 6 added in Commit 6), re-confirmed unchanged in Commit 7.

**Smoke verification (Commit 7, manual, not part of the committed suite):**
- Module-level check against the real `nav.ts` (via `npx tsx`, real import): AGENT-shaped permissions → nav=true/layout=true; VIEWER-like (no `complaints:*`) → nav=false/layout=false; wildcard → nav=true/layout=true. Nav and Layout agreed in all three cases.
- Component-level check against the real `ComplaintsLayout` (React Testing Library, mocking `next-intl`/`next/navigation`/`AuthProvider` per the repo's existing pattern from `CmBatch1SupervisorQueueView.test.tsx`): all 3 scenarios (with-permission / without-permission / wildcard) passed. This was a throwaway file, run once and deleted — not part of the repo.
- **Not performed:** a live browser session against the running `ecmp-frontend` container. That container is a production build from an earlier image; it does not reflect this batch's uncommitted source, and rebuilding/redeploying it was judged out of scope for an engineering-execution commit (see Commit 7 report for the full reasoning).

## 7. Risks

Only risks already surfaced during implementation — none invented for this pack:

| Risk | Status |
|---|---|
| `ADMIN`/`ADMINISTRATOR` retroactively rejected if existing users held a branch | **Cleared** — DG-001 queried the lab database directly: zero users hold any of the 7 head-office role codes today (only `AGENT`×5, `SUPERVISOR`×1, `SUPER_ADMIN`×1 exist), so the new rule has no existing record to break. |
| Pre-existing uncommitted content mixed into several touched files | **Open, documented** — see §2 caveat and §9 Rollback. Does not affect correctness of this batch's logic (each commit traced its own lines precisely), but affects how cleanly this batch can be isolated into its own commit/PR. |
| 9 pre-existing backend test failures | **Open, pre-existing, unrelated** — traced to a rule that predates this batch (§6). Will still show red in a full `pytest --cov-fail-under=90` run until fixed separately; not this batch's responsibility. |
| No live browser/E2E verification of the frontend gates | **Open, documented** — smoke verification (§6) exercised the real modules/components directly; a full browser session against a rebuilt container was not performed this batch, for the reasons stated. |

## 8. Rollback (commit level, no database rollback)

No migration exists in this batch — rollback is code-only.

**If this batch is committed as isolated commits/PR:** `git revert` on the relevant commit(s), then rebuild. Verify post-revert: head-office `branchId` restriction gone (`POST /users` with `ADMIN` + `branchId` succeeds again); Complaints nav item visible to all authenticated users again; `/complaints` reachable without a permission check again.

**Caveat from §2:** because several touched files already carry unrelated pre-existing uncommitted work, a plain `git add <file>` on those files will bundle this batch's hunks together with that other work in the same commit. A reviewer who wants this batch isolated should stage with `git add -p` and select only this batch's hunks (each commit's own report identifies exactly which lines are this batch's). A straightforward single-commit `git revert` remains available regardless of how it was staged, since revert operates on whatever the commit actually contains — the caveat affects *how cleanly this batch can be separated from other work*, not whether a revert is possible.

## 9. Traceability

No entry added to `26 Traceability/traceability.yaml` or the generated `TRACEABILITY_MATRIX.md`. Reasoning: this batch tightens enforcement of an **existing** Mode A business rule (organization-location validation, already partially enforced per the prior baseline in §0) and hardens **existing** complaint-module authorization on the frontend — it does not introduce a new functional requirement, business rule, or API contract that would warrant a new `TRC-L-xxx` link. `TRACEABILITY_MATRIX.md` is auto-generated (`tools/sync_traceability_md.py`) and must not be hand-edited. No existing `TRC-L-xxx` link, FR, BR, or CAP was reopened, reclassified, or touched.

---

## 10. Final Quality Gate

| Dimension | Status |
|---|---|
| **Scope** | 16 files, 7 commits, exactly the areas EBS-001 §2 assigned (backend validation, OpenAPI docs, Create User UX, directory badge, nav gate, layout gate). No scope expansion at any commit. |
| **Architecture** | Single enforcement method backend-side (`_ensure_branch_for_role`); single permission-metadata source frontend-side (`APP_NAV_ITEMS` + `isNavItemVisible`), consumed identically by nav and layout. No second authorization system introduced anywhere. |
| **Tests** | Backend: 43/43 `test_users.py`, 45/45 adjacent — all green. Frontend: 11/11 `directoryHelpers.test.ts`, 11/11 `nav.test.ts` — all green. 9 pre-existing, unrelated backend failures documented, not introduced by this batch. |
| **Typecheck** | `npm run typecheck` clean at every frontend commit (5, 6, 7). |
| **Lint** | `ruff check app tests` clean at every backend commit (1–4). `npm run lint` (`--max-warnings 0`, full repo) clean at every frontend commit (5–7). |
| **OpenAPI impact** | One file, two `description` fields only. Zero `type`/`required`/`path`/schema changes. Validated: all 11 specs pass. |
| **Backend impact** | Two files (`service.py`, `user_messages.py`) + one test file. Zero router, permission-catalog, role-catalog, schema, or migration changes. |
| **Frontend impact** | 13 files across Create User/Directory/Navigation/Layout. Zero backend/API calls changed — `createUser` payload shape unchanged (`branchId: string \| null`, same as before). |
| **Rollback** | Code-only, no migration. Isolation caveat documented (§8/§2) — does not block revert, affects staging cleanliness. |
| **Governance** | No CLAUDE.md filter violated (§1 three-filter test: closer to COMPLETE, domain stable, integration mechanism untouched). No Mode B, no Enterprise Platform artifact touched. |
| **PR readiness** | **Ready**, with the isolation caveat (§8) disclosed for the PR author to decide how to stage. |

---

*This pack documents Commits 1–7 as implemented. It does not authorize merge, push, or deployment — those remain separate, human decisions per this repo's review process.*

---

## 11. Release Isolation Note (2026-08-04)

Isolated onto branch `release/ebs-001-org-location-authorization` from `main` without touching the dirty development worktree.

**Included as approved EBS surfaces:** backend organization-location validation + tests, OpenAPI `branchId` documentation, Create User modal (location-aware), `DirectoryLocationBadge` on the baseline user directory table, Complaints navigation gate, Complaints layout gate, this evidence pack, and ECMP-EBS-001.

**Intentionally excluded from this PR branch (parallel dirty-tree work, not EBS-001):** CWX M1–M4, UI redesign (dashboard/settings/auth/shell), `DirectoryPeopleList` / `DirectoryPreviewPanel` rewrite and their unfinished i18n/UI-primitive co-requisites, `org_unit_resolver` / CAP / Mode B / DEC-F4 / M4, deploy/Caddy/compose churn, and other unstaged files on `feature/cm-batch1-s2-persistence`.

Badge AC is delivered via `DirectoryLocationBadge` on the existing user table rather than the unfinished directory rewrite panels.


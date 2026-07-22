# ECMP Sprint-07 — Platform Stabilization: Implementation Plan

Engineering plan only — no code. Every finding below is from reading the actual current source
(not the plan documents that preceded it) and, where noted, running real commands. Milestone 2
(Timeline/Notes/Audit) has already been built since the last plan was written — this review starts
from that reality, not from the earlier plan's assumptions.

## Objective Status (read first)

| # | Objective | Status |
|---|---|---|
| 1 | Standardize AsyncPanel usage | **PARTIALLY IMPLEMENTED** — new panels (Timeline, Notes, Audit History) use it correctly; Case Detail/Queue workspaces deliberately don't yet (explicit code comment: "Do not retrofit shipped Case Detail / Case Queue screens onto this yet"). Real work remains — see §2. |
| 2 | Standardize API client patterns | **MOSTLY IMPLEMENTED** — `api/cases.ts` is already fully consistent. One concrete gap found: a React Query config inconsistency, not an API-client one. See §2. |
| 3 | Expand automated testing to 100+ tests | **NOT IMPLEMENTED** for frontend — zero test files, no test framework installed. Backend has 76 tests (counted just now), thin on the newest endpoints. |
| 4 | Remove dead code and placeholders | **NOT IMPLEMENTED** — one confirmed dead component found (`ActivityTimelinePlaceholder`, zero imports anywhere). Scope of this finding is bounded — see caveat in §2. |
| 5 | Add CI quality gates | **NOT IMPLEMENTED** for frontend — no frontend CI workflow exists at all. Backend has a strong model to mirror (`backend-ci.yml`). |

No objective is fully implemented and excludable. All five have real, verified remaining work.

---

## 1. Architecture Review

**What's actually in the repo now** (verified by reading source, not assumed from prior plans):

- `implementation/frontend/src` has grown to ~70 files across `case-detail`, `case-queue`, and
  `case-notes` features, plus shared `components/`, `api/`, `auth/`, `lib/`.
- Milestone 2 was built **faithfully to contract-first discipline**: `07 API Catalog/openapi/
  case-service.v1.yaml` has API-006 (`GET .../timeline`) and API-007 (`GET .../notes`) properly
  cataloged with `x-ear-id`; `26 Traceability/traceability.yaml` has FR-006/FR-007 and API-006/API-007
  rows. This is real governance discipline being followed correctly, not just claimed — good sign for
  the codebase's health.
- **Gap found in that same governance chain:** no FRD document backs FR-006/FR-007 — they exist in
  the traceability index and in code comments, but not in `03 Functional Requirements/`. Not this
  sprint's job to write one (out of scope — no new business functionality), but worth flagging since
  it's a documentation-completeness gap in already-shipped work.
- **Gap found in the conformance suite specifically:** `tests/test_contract_conformance.py` (the
  "catalog == runtime" enforcer that's been this repo's contract-integrity backbone since Sprint-01,
  reinforced in Sprint-03A) does **not** cover API-006 or API-007 at all. The exact kind of drift the
  Sprint-03A governance sync sprint existed to eliminate has quietly reappeared for the two newest
  endpoints. This is a concrete, high-value target for objective 5 (CI gates) and objective 3
  (testing) — not a new problem to design around, an existing one to close.
- `AsyncPanel` (`src/components/AsyncPanel.tsx`) is well-designed and does what it says: renders
  exactly one of `LoadingSkeleton`/`ErrorBanner`/`EmptyState`/`children` from a flat prop contract.
  It is *not*, as written, a drop-in replacement for either workspace's existing logic — see §2 for
  why.
- `AuthContext`'s `DEV_FIXTURES` were correctly extended with `cases:notes:create` for the principals
  that should have it (dev/supervisor/handler/foreign-supervisor tokens), correctly omitted from
  readonly/noperm tokens — consistent with the backend's permission model as far as I checked.

## 2. Refactoring Plan

### 2a. AsyncPanel retrofit (objective 1)

**Not a mechanical find-and-replace.** Both workspaces have states `AsyncPanel` doesn't model:

- `CaseDetailWorkspace`: the error branch needs *different actions per error code* — `NOT_FOUND`/
  `FORBIDDEN` show "Back to queue", everything else shows "Retry". `AsyncPanel.onRetry` is a single
  fixed action. **Required change:** extend `AsyncPanel` to accept a generic `errorAction: {label,
  onClick}` instead of (or alongside) `onRetry`, so callers decide the action per error code
  themselves — a small, additive prop change, not a rewrite.
- `CaseQueueWorkspace`: uses `keepPreviousData` and renders the *previous* table dimmed while
  refetching (`CaseQueueTable dimmed={isFetching}`), plus a `VALIDATION_ERROR` branch that keeps the
  filter bar visible while showing a recovery hint — states `AsyncPanel`'s binary
  loading/error/empty/content model has no slot for. **Required change:** either (a) add an
  `isRefreshing` mode to `AsyncPanel` that renders `children` dimmed instead of a full skeleton, or
  (b) accept that Case Queue's pagination-refresh UX is a deliberate, documented exception and only
  migrate its *initial-load* and *hard-error* branches to `AsyncPanel`, leaving the dimmed-refetch
  behavior as workspace-local code. **Recommend (b)** — inventing a generic "refreshing" mode inside a
  shared primitive to serve one caller's specific UX is how shared components accrete unused
  complexity; simpler to document the exception.
- Both retrofits are **behavior-preserving refactors** (same visual output, same states, same copy) —
  this is why they're in scope despite "do not redesign completed features": the design doesn't
  change, only which code renders it. If a retrofit would change visible behavior, stop and treat that
  as a new design decision, not a refactor.

### 2b. React Query config standardization (objective 2)

`useCase.ts` is missing `retry: false`, which every other query/mutation hook in the codebase
(`useCaseQueue`, `useCaseTimeline`, `useCaseNotes`, `useAssignCase`, `useChangeStatus`) already sets.
This was flagged as a risk back in the Sprint-06 report and confirmed still true. **This is the one
concrete "API client pattern" fix** — everything in `api/cases.ts` itself (the actual HTTP client
layer) is already consistent: one `apiRequest<T>` wrapper, uniform `encodeURIComponent` usage, uniform
JSDoc citing the API ID. Objective 2's real remaining work is this one-line hook config fix, not a
client-layer rewrite.

### 2c. Dead code removal (objective 4)

**Confirmed:** `src/features/case-detail/components/ActivityTimelinePlaceholder.tsx` and its
`.module.css` — zero imports anywhere in `src/` (verified by grep across the whole tree). It was
superseded by `CaseActivityTimeline` when Milestone 2 shipped and never deleted.

**Caveat on scope:** I verified this one file precisely because the "placeholder" naming made it an
obvious candidate and its Screen Spec history made it easy to trace. I have **not** exhaustively swept
every file in the frontend or backend for unused exports, orphaned CSS classes, or unreachable code
paths — that's a mechanical task better suited to a real tool (`ts-prune`, `eslint
no-unused-vars`/`no-unused-imports` once lint is working again, or `vulture`/`ruff --select F401` on
the Python side) than manual file-by-file reading. Recommending that tooling pass as part of this
sprint's CI work (§4), which will surface anything beyond this one confirmed file rather than me
guessing at a complete list.

## 3. File Impact Analysis

| File | Change | Reason |
|---|---|---|
| `src/components/AsyncPanel.tsx` | Add `errorAction` prop (additive) | §2a |
| `src/features/case-detail/CaseDetailWorkspace.tsx` | Replace hand-rolled loading/error branches with `AsyncPanel` | §2a |
| `src/features/case-queue/CaseQueueWorkspace.tsx` | Replace *initial-load and hard-error* branches only with `AsyncPanel`; leave dimmed-refetch/validation-recovery logic as-is | §2a |
| `src/features/case-detail/hooks/useCase.ts` | Add `retry: false` | §2b |
| `src/features/case-detail/components/ActivityTimelinePlaceholder.tsx` (+ `.module.css`) | **Delete** | §2c |
| `implementation/backend/tests/test_contract_conformance.py` | Extend to cover API-006/API-007 operations, response codes, schemas | §1 finding — closes a real conformance gap |
| `implementation/frontend/package.json` | Add test tooling (Vitest, React Testing Library, `@testing-library/jest-dom`) | §5 |
| `implementation/frontend/vite.config.ts` | Add `test` config block for Vitest | §5 |
| New: `implementation/frontend/src/**/*.test.{ts,tsx}` | New test files (see §5 for scope) | §5 |
| New: `.github/workflows/frontend-ci.yml` | New CI workflow | §4 |
| `implementation/backend/tests/test_timeline_notes.py` | Backfill additional test cases (currently only 4 for 2 new endpoints + new table + new permission) | §5 |

No file outside `implementation/frontend/`, `implementation/backend/tests/`, and `.github/workflows/`
is touched. No OpenAPI file changes. No new endpoint. No ADR changes.

## 4. CI Proposal

Backend CI (`backend-ci.yml`) is a solid model — mirror its shape for frontend rather than inventing a
different one:

```
name: Frontend CI
on: push/PR, paths: implementation/frontend/**, .github/workflows/frontend-ci.yml
jobs:
  test:
    - checkout, setup-node (version pinned to match local dev, e.g. 20.x LTS — not 22, see Risks)
    - npm ci
    - npm run typecheck        # tsc --noEmit
    - npm run lint             # eslint — must be fixed first, see Risks
    - npm run test -- --coverage   # vitest, coverage gate TBD (backend uses 90% — propose same
                                     # target for consistency, confirm with team before enforcing)
    - npm run build            # vite build — production bundle must succeed
```

Additionally, extend the **existing** `backend-ci.yml` test step (not a new job) so
`test_contract_conformance.py`'s expansion (§2/§3) is exercised — this closes the API-006/API-007
conformance gap as a CI-enforced gate, not just a one-time manual fix.

**Do not** add a combined "platform CI" workflow that runs both frontend and backend in one job —
`backend-ci.yml` already scopes itself by `paths:` to avoid running on unrelated changes; a new
`frontend-ci.yml` should do the same, independently, matching the existing pattern rather than
introducing a new one.

## 5. Testing Strategy

**Frontend (currently zero):**
- Tooling: Vitest (pairs naturally with Vite, per ADR-013's existing stack — no new ADR needed, this
  is a dev-dependency addition, not an architecture decision) + React Testing Library.
- Priority order (highest-value first, not file-alphabetical):
  1. `permissions.ts` — pure functions, highest logic density, zero rendering needed, cheapest tests to write and most valuable (this is exactly the kind of function where a silent regression would be a real security-visibility bug).
  2. `api/errors.ts` (`isApiError`, `getErrorCopy`) — pure functions, same rationale.
  3. Hook tests for `useAssignCase`/`useChangeStatus`/`useCaseTimeline`/`useCaseNotes` — verify the `setQueryData`-on-success / `invalidateQueries`-on-409 cache behavior actually happens, since that's the single most architecturally important behavior in the whole frontend (Screen Spec §5/§6) and currently has zero automated coverage.
  4. Component tests for `AsyncPanel` itself (all four render branches) — becomes load-bearing once §2a lands.
  5. Component tests for the four action components (`AssignActionForm`, `StatusActionControls`, `ApproveCloseForm`, `RejectButton`) covering the error-code branches from Screen Spec §7.
- **Not proposing:** full end-to-end/browser tests (Playwright/Cypress) this sprint — that's a bigger
  tooling decision (new CI runtime requirements, possibly worth its own ADR-style discussion) and
  wasn't asked for. Vitest + RTL covers "automated testing," not full E2E.

**Backend (76 existing, real gap is distribution not total):**
- `test_timeline_notes.py` has 4 tests for 2 new endpoints + a new table + a new permission — thin
  compared to assign/status's coverage (dozens of tests across three files for a comparable-sized
  surface). Backfill: empty-timeline case, forbidden (missing `cases:read`), forbidden (missing
  `cases:notes:create` on POST), 404 on unknown caseId for both endpoints, ordering guarantee for
  notes (chronological), and the contract-conformance additions from §2/§4.

**On "100+ tests":** ambiguous whether this means combined platform total (76 backend + 24+ new
frontend would already clear it) or 100+ *per side*. Recommend clarifying with the CTO rather than
guessing — I've sized the frontend priority list above to comfortably produce 40-60 meaningful tests
on its own merits (not padded to hit a number), which combined with backend backfill clears 100+
either way, but the interpretation affects whether backend also needs a larger push.

## 6. Risks

| Risk | Notes |
|---|---|
| ESLint hangs in this sandbox (`npm run lint` timed out with zero output, reproduced twice, 30s hard timeout) | Root cause not diagnosed — could be sandbox-specific or a real config issue (ESLint 8.57.1 legacy config on Node 22). **Must be resolved before CI can enforce lint as a gate** — an always-timing-out CI step is worse than no lint gate (blocks all merges). Flagging as a blocker for §4, not guessing at a fix. |
| `vite build` failed in the verification sandbox (missing native Rollup optional dependency, read-only filesystem prevented repair) | Reported in the Sprint-06 review as an environment artifact (`dist/` evidence showed a prior successful build). Still unresolved as of this sprint — CI must prove this works in a clean, real environment before objective 5 can be called done. |
| AsyncPanel retrofit scope creep | §2a's `errorAction` extension is intentionally minimal; resist the temptation to also add the "isRefreshing" mode for Case Queue (§2a explicitly recommends against it) — that's exactly how a stabilization sprint quietly becomes a redesign sprint. |
| Coverage gate number picked without team input | Backend's 90% is an existing precedent; proposing the same for frontend by default, but this should be confirmed, not assumed, before it becomes a hard CI gate that blocks merges. |
| "100+ tests" interpretation ambiguity | See §5 — could change scope materially depending on answer. |

## 7. Acceptance Criteria

1. `CaseDetailWorkspace` and `CaseQueueWorkspace` use `AsyncPanel` for their loading/hard-error states; Case Queue's dimmed-refetch and validation-recovery UX remains workspace-local by deliberate documented decision, not by oversight.
2. `useCase.ts` sets `retry: false`, matching every other query/mutation hook.
3. `ActivityTimelinePlaceholder.tsx` and its CSS module no longer exist in the repo; `npm run build` and `tsc --noEmit` both still pass after removal (proves it was truly unreferenced).
4. `test_contract_conformance.py` asserts API-006 and API-007 exist in the catalog, match runtime response codes, and match runtime schemas — same rigor already applied to API-001..005.
5. Frontend has a working `npm run test` command backed by Vitest, producing a coverage report; the priority-ordered test list in §5 exists and passes.
6. `.github/workflows/frontend-ci.yml` exists, runs typecheck/lint/test/build on PRs touching `implementation/frontend/**`, and is green on a real PR (not just locally) — the ESLint and Rollup issues in §6 must be resolved for this criterion to be met, not worked around.
7. `implementation/backend/tests/test_timeline_notes.py` covers the gap cases listed in §5.
8. No visible UI behavior changed anywhere — verified by comparing rendered output before/after for both retrofitted workspaces (manual check, since no E2E/visual-regression tooling exists yet).
9. No new backend endpoint, no OpenAPI change beyond the conformance test extension (which touches only the test file, not the contract itself), no ADR created or modified.

## 8. Technical Debt

- **Case Queue's refresh UX stays outside `AsyncPanel`** — an accepted, documented exception (§2a), not a gap to silently close later by force-fitting it. Revisit only if a second screen needs the same "dimmed content while refetching" pattern, at which point it's worth generalizing.
- **No FRD backs FR-006/FR-007** — traceability and code reference requirements that exist nowhere as prose. Not this sprint's job to write (no new business functionality), but a real documentation-completeness gap inherited from Milestone 2, now explicitly on record rather than silently carried.
- **Dead-code sweep was manual and partial** (§2c caveat) — only `ActivityTimelinePlaceholder` was confirmed. A tooling-based sweep (`ts-prune`, unused-import lint rules once lint works, `ruff --select F401` on backend) is recommended as follow-up, not claimed as done here.
- **Lint and production-build tooling issues (§6) are pre-existing, not introduced by this sprint** — but they block this sprint's own CI objective until fixed, so they've effectively become this sprint's dependency whether or not they were "supposed to" be in scope.
- **No E2E/visual-regression testing** — Vitest + RTL covers unit/integration level; full user-journey verification (Screen Spec §1 J-1..J-5) still requires manual testing, same limitation noted in every prior sprint's report.

---

## Related
- `implementation/frontend/IMPLEMENTATION_PLAN.md`, `IMPLEMENTATION_PLAN_CASE_QUEUE.md`, `IMPLEMENTATION_PLAN_MILESTONE2.md` — prior plans this one verifies against actual code, not just extends on paper
- `07 API Catalog/openapi/case-service.v1.yaml` (API-006/API-007 — contract already correct, conformance test coverage is the gap)
- `.github/workflows/backend-ci.yml` (model for the new frontend workflow)
- `implementation/backend/tests/test_contract_conformance.py` (extension target)

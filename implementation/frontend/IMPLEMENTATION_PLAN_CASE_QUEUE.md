# ECMP Frontend — Implementation Plan (Case Queue)

Sprint-05. Implementation plan only — no code, no new backend endpoint, no OpenAPI/contract change.
Builds entirely on `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 API-005 (`GET /v1/cases`),
already implemented and tested server-side since Sprint-03B (TC-006).

**Risk flagged up front (not a blocker, per Lead Engineer duty to surface before coding):** unlike
Case Detail Workspace, there is **no formal UX-SCR Screen Spec for Case Queue** — `12 UI UX Spec/
ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` §1 explicitly named the queue as "out of scope for
this spec, referenced only as navigation source." The layout/filter/pagination decisions below are
derived directly from FR-005's acceptance criteria (`03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`
v0.4) and the journey references already approved in the Case Detail spec (J-2: "filtered
status=REGISTERED"; J-3: "filtered assigneeId=self&status=ASSIGNED"), not from an independent UX
design pass. Recommend a lightweight UX-SCR-002 sign-off in parallel if the team wants one, but
producing it is outside this Lead Engineer plan and is not requested for Sprint-05.

This plan assumes the Case Detail Workspace implementation (`IMPLEMENTATION_PLAN.md`) exists or is
in progress — it reuses that plan's stack (ADR-013), API client layer, and shared components
(`StatusBadge`, `PriorityBadge`, `ErrorBanner`, `LoadingSkeleton`, `ToastContainer`) rather than
rebuilding them. One new shared component (`EmptyState`) is introduced here because Case Detail never
needed a full-panel empty state.

---

## 1. Component Hierarchy

```
CaseQueuePage                              (route: "/" — replaces the placeholder text
                                             from IMPLEMENTATION_PLAN.md §2; CaseHeader's
                                             BackToQueueLink now has a real destination)
└── CaseQueueWorkspace                      (root — owns filter/pagination state + query)
    ├── QueueFilterBar
    │   ├── StatusFilterSelect              (CaseStatus enum, incl. "All")
    │   ├── PriorityFilterSelect            (Priority enum, incl. "All")
    │   ├── CaseTypeFilterSelect            (CaseType enum, incl. "All")
    │   ├── AssigneeIdFilterInput           (free text — no directory API exists, same
    │   │                                    constraint noted for AssignActionForm in
    │   │                                    IMPLEMENTATION_PLAN.md §5)
    │   └── ClearFiltersButton
    ├── LoadingSkeleton (variant="table")   (initial load only, reused shared component)
    ├── ErrorBanner                         (full-page 403/500, reused shared component)
    ├── EmptyState                          (NEW shared component — see §7)
    ├── CaseQueueTable
    │   ├── CaseQueueTableHeader            (column labels, no client-side sort — see §3)
    │   └── CaseQueueRow (×N)
    │       ├── StatusBadge                 (reused)
    │       ├── PriorityBadge               (reused)
    │       └── (row click → navigate to /cases/:caseId, existing route, unchanged)
    └── PaginationControls
        ├── PageInfo                        ("Showing 21–40 of 137")
        └── PrevNextButtons
```

`ToastContainer` is not duplicated — it already exists at the app-shell level per
`IMPLEMENTATION_PLAN.md` §7 (`main.tsx`), available to this screen without re-mounting.

---

## 2. State Management

- **Filter + pagination state lives in the URL**, via `useSearchParams` (React Router), not local
  component state alone: `?status=REGISTERED&priority=HIGH&caseType=COMPLAINT&assigneeId=USR-2001&page=2`.
  Rationale: makes filtered views shareable/bookmarkable and satisfies the journey pattern already
  implied by the approved Case Detail spec ("opens the queue filtered status=X") — a link to a
  pre-filtered queue is a real requirement, not a nice-to-have. `CaseQueueWorkspace` reads/writes
  search params; individual filter components are controlled from that single source, not each
  owning their own state.
- `pageSize` also lives in the URL (`?pageSize=20`, default 20) so a reload preserves it, but there is
  no UI control to change it in this version (page-size selection isn't in FR-005 AC or any journey —
  not adding a control that isn't requested; default only).
- **Server state:** TanStack Query holds the `CasePage` result, keyed on the full filter+page tuple
  (§4). No separate cache for individual cases — this screen doesn't reuse or seed the `['case',
  caseId]` query key from Case Detail Workspace; they're independent (list items are not automatically
  treated as fresh single-case data, since `Case` objects returned in a list page carry the same shape
  but staleness assumptions differ per screen).
- No global store, no optimistic updates — this is a read-only screen, consistent with the "no
  optimistic updates" principle already established for Case Detail (mutations don't exist here at all).

---

## 3. API Contract

Reused exactly as implemented — **no change, no new endpoint.**

`GET /v1/cases` (API-005, `case-service.v1.yaml` v1.5.0), permission `cases:read`:

| Query param | Type | Sent when |
|---|---|---|
| `page` | integer ≥1, default 1 | Always (from URL state) |
| `pageSize` | integer 1–100, default 20 | Always (from URL state, no UI control this version) |
| `status` | `CaseStatus` | Only if filter set (omit param entirely for "All" — do not send an empty string) |
| `priority` | `Priority` | Only if filter set |
| `caseType` | `CaseType` | Only if filter set |
| `assigneeId` | string | Only if filter set (trimmed; omit if empty) |

Response: `CasePage { items: Case[], page: number, pageSize: number, totalItems: number }` — same
`Case` shape already typed in `IMPLEMENTATION_PLAN.md` §5 `api/types.ts`; add `CasePage` interface
there (one addition, not a new file) plus one function in `api/cases.ts`:

```ts
listCases(params: { page: number; pageSize: number; status?: CaseStatus; priority?: Priority;
                     caseType?: CaseType; assigneeId?: string }): Promise<CasePage>   // GET /v1/cases
```

Sort is **fixed `createdAt` descending** (CTO decision, Sprint-03B) — there is no `sortBy`/`sortDir`
parameter in the contract. `CaseQueueTableHeader` must not imply sortable columns (no clickable sort
affordance on any column) since that would promise behavior the API doesn't support.

---

## 4. Query Strategy

- Query key: `['cases', { page, pageSize, status, priority, caseType, assigneeId }]` — the full
  filter/page object as part of the key, so each distinct combination is cached independently and a
  filter change is naturally a new query, not a manual refetch.
- `useCaseQueue(filters)`: `useQuery(key, () => listCases(filters), { placeholderData: keepPreviousData })`.
  `keepPreviousData` (TanStack Query) is the one deliberate deviation from Case Detail's "always show a
  skeleton" approach: paging/filtering should show the *previous* table with a subtle updating
  indicator (§5) rather than blanking to a skeleton on every click — a table that disappears on every
  filter tweak is a worse experience for a screen whose entire purpose is fast browsing.
- `staleTime: 0`, no polling/auto-refresh — consistent with Case Detail; this screen doesn't need
  live updates for this sprint (not in FR-005 AC).
- `retry: false` on this query, same as Case Detail's mutations — **note:** `IMPLEMENTATION_PLAN.md`
  §6 did not explicitly set a retry policy on `useCase`; this plan sets `retry: false` for
  `useCaseQueue` for consistency and recommends (not requires, out of this plan's scope) the same be
  confirmed for `useCase` during Case Detail implementation so the two screens don't diverge silently.
- Filter/page changes update the URL (§2), which changes the query key, which triggers the fetch —
  there is no separate "Apply filters" button; filters apply immediately on change (matches typical
  queue/table UX and avoids a redundant confirm step for a read-only, side-effect-free action).

---

## 5. Loading State

| Moment | Treatment |
|---|---|
| Initial load (no cached data for this key yet) | `LoadingSkeleton variant="table"` — rows of placeholder blocks matching `CaseQueueTable` column widths |
| Filter/page change with `keepPreviousData` active | Previous table stays visible, reduced opacity (e.g. `0.6`) + small inline spinner near `QueueFilterBar` or `PaginationControls`; **not** a full skeleton (§4 rationale) |
| Pagination button clicked | The clicked Prev/Next button shows a spinner and both buttons disable until the new page's data arrives (prevents double-clicks compounding page state) |

No skeleton or spinner exists outside these three states — no per-row loading indicators.

---

## 6. Error State

| Code | Where | Treatment |
|---|---|---|
| `UNAUTHENTICATED` (401) | Not handled here | App-shell concern, same as Case Detail (`IMPLEMENTATION_PLAN.md` §9) — out of scope for this screen |
| `FORBIDDEN` (403) | `ErrorBanner`, full page (replaces the whole workspace, not just the table) | "You don't have access to view cases" — should be rare (`cases:read` is broad) but the contract allows it, must be handled, not assumed away |
| `VALIDATION_ERROR` (400) | `ErrorBanner`, inline near `PaginationControls` | Defensive only — should not occur if pagination controls respect the `pageSize` ≤100 cap client-side (§3); if it somehow does, reset `page`/`pageSize` to defaults in the URL and show a brief message, do not leave the screen in a broken state |
| `INTERNAL_ERROR` (500) / network failure | `ErrorBanner` with Retry button, replacing the table area only (filters stay visible/usable so the user isn't forced to re-enter them) | Retry re-runs the current query key exactly as-is |

`404` and `409` are not possible responses for this endpoint (list, no target resource, no state
mutation) — no handling needed for them, and none should be added defensively (that would imply a
contract behavior that doesn't exist).

---

## 7. Empty State

New shared component `EmptyState` (`src/components/EmptyState.tsx`, added to the shared set from
`IMPLEMENTATION_PLAN.md` §4 — Case Detail never needed a full-panel empty state, only field-level
"—"/"Unassigned" treatments). Props: `title, message, action?`.

Two distinct conditions, both render `EmptyState` but with different copy — must be distinguished, not
collapsed into one generic message:

| Condition | Copy | Action |
|---|---|---|
| `totalItems === 0` and **no filters active** | "No cases yet." | None |
| `totalItems === 0` and **any filter active** | "No cases match your filters." | "Clear filters" button (resets URL params to defaults) |

"Filters active" is derived from the URL state, not from re-deriving it from the response — the
distinction is about what the *user asked for*, not about the response shape (both cases return the
same empty `items: []`, `totalItems: 0`).

---

## 8. Acceptance Criteria

1. Default load (`/` with no query params) shows page 1, up to 20 items, sorted `createdAt` descending — matches FR-005 AC default behavior exactly.
2. Each filter (`status`, `priority`, `caseType`, `assigneeId`) narrows results correctly individually and in combination (AND semantics) — matches backend behavior already verified by `TC-006` (`tests/test_case_list.py`); this is a UI wiring check, not new logic to test independently.
3. Filter and page state round-trip through the URL: reloading the page, or opening a filtered URL directly, reproduces the same filtered/paginated view.
4. Browser back/forward navigates between previous filter/page states correctly (standard `useSearchParams` behavior — no custom history handling needed).
5. Pagination controls correctly compute and display `page`/`totalItems`; last page with a partial row count renders correctly (no phantom empty rows); Next is disabled on the last page, Prev disabled on page 1.
6. Clicking a row navigates to `/cases/:caseId` for that case — the existing Case Detail Workspace route, unmodified.
7. `pageSize` sent to the API never exceeds 100 under any UI interaction (no control exists to set it above the default in this version, so this is inherently satisfied — verify no hidden path, e.g. malformed URL param, bypasses it: if a URL manually sets `pageSize=500`, clamp client-side to 100 before calling the API rather than sending an invalid value that would 400).
8. 403 on load renders the full-page `ErrorBanner`, not a broken/empty table.
9. Empty state correctly distinguishes "no cases" vs "no matches," including the "Clear filters" action only in the latter case.
10. No new backend endpoint, no `07 API Catalog/` change — verified via `git diff` showing zero changes outside `implementation/frontend/` before merge.
11. `StatusBadge`, `PriorityBadge`, `ErrorBanner`, `LoadingSkeleton` are imported from the existing shared component set (`src/components/`), not re-implemented for this screen.
12. No column/control implies a capability the API doesn't have — no sort-by-column affordance, no page-size selector, no bulk actions.

---

## Related
- `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 (API-005) — unchanged
- `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` v0.4 §10 FR-005 AC
- `13 Test Strategy/ECMP_Test_Case_Catalog_v0.1.md` TC-006 (backend coverage this screen's filters build on)
- `implementation/frontend/IMPLEMENTATION_PLAN.md` (Case Detail Workspace — shared stack/components reused here)
- `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` §1 (queue referenced as out of scope there; this plan fills that gap at the implementation-planning level only, not with a formal Screen Spec)

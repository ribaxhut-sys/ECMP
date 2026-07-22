# ECMP Frontend — Implementation Plan (Case Detail Workspace)

Sprint-04. Not an architecture document — no new ADR, no new Screen Spec, no new endpoint.
This plan operationalizes what is already Approved:

- Stack: `05 Architecture Decision Records/ECMP_ADR_013_Frontend_Technology_Stack_v1.0.md` (Accepted)
- Design: `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` (UX-SCR-001, Approved)
- Contract: `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 (unchanged — read-only source of truth here)

`implementation/frontend` currently contains only `.gitkeep` — this is a from-scratch bootstrap.

**Blocker check: none found.** One infrastructure gap was found (no CORS middleware on the backend)
but it has a frontend-only mitigation (Vite dev proxy, §13) that requires no backend change — not a
stop condition per the rules ("jangan mengubah backend").

---

## 1. Struktur Folder Frontend

```
implementation/frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .env.example                    # VITE_API_BASE_URL, VITE_DEV_TOKEN (dev-mode only, see §8/§13)
├── .eslintrc.cjs
├── .gitignore
├── README.md                       # how to run, env setup
└── src/
    ├── main.tsx                    # ReactDOM root, providers
    ├── App.tsx                     # router outlet only
    ├── routes/
    │   └── router.tsx              # route table
    ├── pages/
    │   └── CaseDetailPage.tsx      # route-level component for /cases/:caseId
    ├── features/
    │   └── case-detail/
    │       ├── CaseDetailWorkspace.tsx    # root component per Screen Spec §11
    │       ├── components/
    │       │   ├── CaseHeader.tsx
    │       │   ├── CaseInfoPanel.tsx
    │       │   ├── ActivityTimelinePlaceholder.tsx
    │       │   ├── CustomerReferencePanel.tsx
    │       │   ├── CaseMetaPanel.tsx
    │       │   ├── ActionPanel.tsx         # decides which action UI (if any) renders
    │       │   ├── AssignActionForm.tsx
    │       │   ├── StatusActionControls.tsx
    │       │   ├── ApproveCloseForm.tsx
    │       │   └── RejectButton.tsx
    │       ├── hooks/
    │       │   ├── useCase.ts              # useQuery wrapper
    │       │   ├── useAssignCase.ts        # useMutation wrapper
    │       │   └── useChangeStatus.ts      # useMutation wrapper
    │       └── permissions.ts              # pure functions per Screen Spec §6
    ├── components/                  # shared, cross-feature (Screen Spec §3)
    │   ├── StatusBadge.tsx
    │   ├── PriorityBadge.tsx
    │   ├── ErrorBanner.tsx
    │   ├── InlineFieldError.tsx
    │   ├── LoadingSkeleton.tsx
    │   ├── ConfirmDialog.tsx
    │   └── Toast/
    │       ├── Toast.tsx
    │       └── ToastContainer.tsx
    ├── api/
    │   ├── client.ts                # fetch wrapper: base URL, auth header, envelope parsing
    │   ├── types.ts                 # hand-written types mirroring case-service.v1.yaml v1.5.0
    │   ├── cases.ts                 # getCase, assignCase, changeStatus (only what this screen uses)
    │   └── errors.ts                # ApiError class
    ├── auth/
    │   └── AuthContext.tsx          # interim token/claims provider (ADR-013 item 7 — dev-mode only)
    ├── lib/
    │   └── queryClient.ts           # TanStack Query client instance + config
    └── styles/
        ├── tokens.css               # StatusBadge/PriorityBadge color mapping (Screen Spec §3)
        └── *.module.css             # one per component, co-located naming
```

No `implementation/frontend/src/pages/CaseListPage.tsx` and no queue/list route — the queue screen is
explicitly out of scope for `UX-SCR-001` and must not be built here (see §3 and §13).

---

## 2. Daftar Halaman (Pages/Routes)

| Route | Component | Notes |
|---|---|---|
| `/cases/:caseId` | `CaseDetailPage` → `CaseDetailWorkspace` | The only real screen in this plan, per Screen Spec scope |
| `*` (catch-all) | Minimal "not found" text, no design needed | Standard SPA fallback for direct bad URLs — not a designed screen, just prevents a blank page |
| `/` | Redirect to nothing meaningful yet — render a one-line placeholder ("Open a case from its URL") | The queue screen that would normally live at `/` doesn't exist yet (out of scope). Do not build a queue/list screen to fill this gap. |

This is intentionally a one-screen app for this sprint. `BackToQueueLink` in `CaseHeader` (Screen Spec
§2/§11) has no real destination yet — point it at `/` (the placeholder), not a fabricated queue page.

---

## 3. Component Hierarchy

Reused verbatim from Screen Spec §11 — do not alter this tree:

```
CaseDetailWorkspace
├── LoadingSkeleton                      (initial fetch in flight)
├── ErrorBanner                          (full-page 403/404/500 on load)
└── (once loaded)
    ├── CaseHeader
    │   ├── BackToQueueLink              (→ "/", see §2)
    │   ├── StatusBadge
    │   └── PriorityBadge
    ├── CaseDetailLayout
    │   ├── MainColumn
    │   │   ├── CaseInfoPanel
    │   │   ├── ActivityTimelinePlaceholder
    │   │   └── ActionPanel              (renders 0 or 1 of:)
    │   │       ├── AssignActionForm
    │   │       │   └── InlineFieldError (×N)
    │   │       └── StatusActionControls
    │   │           ├── StartHandlingButton
    │   │           ├── SubmitForReviewButton
    │   │           ├── ApproveCloseForm
    │   │           │   ├── InlineFieldError
    │   │           │   └── ConfirmDialog
    │   │           └── RejectButton
    │   │               └── ConfirmDialog
    │   └── SideColumn
    │       ├── CustomerReferencePanel
    │       └── CaseMetaPanel
    └── ToastContainer                    (portal, outside layout flow)
```

`StartHandlingButton`/`SubmitForReviewButton` are small enough to live as internal sub-components
inside `StatusActionControls.tsx` rather than separate files — only `ApproveCloseForm` and
`RejectButton` warrant their own files (they carry form state / confirm dialogs).

---

## 4. Shared Components

From Screen Spec §3 — build these first (§12 step 1), they have no case-specific logic:

| Component | Props (essential) | Notes |
|---|---|---|
| `StatusBadge` | `status: CaseStatus` | Fixed color map per Screen Spec §3 — REGISTERED gray, ASSIGNED blue, IN_PROGRESS amber, PENDING_REVIEW purple, CLOSED green, REOPENED red |
| `PriorityBadge` | `priority: Priority` | No color spec given beyond "renders the enum" — use a neutral consistent scheme, do not invent semantic meaning beyond what's specified |
| `ErrorBanner` | `title, message, action?` | Full-width, used for page-level 401/403/404/500 |
| `InlineFieldError` | `message` | Field-level, used under form inputs for 400 `VALIDATION_ERROR.details` |
| `LoadingSkeleton` | `variant: 'header' \| 'panel'` | Shape-matched placeholders per Screen Spec §8 |
| `ConfirmDialog` | `title, message, onConfirm, onCancel, isPending` | Wraps Approve & Close and Reject per Screen Spec §11 |
| `Toast` / `ToastContainer` | `type: 'success' \| 'error', message` | Transient feedback, portal-rendered |

These are the entire shared component set. Do not add a design-system library or additional shared
components beyond this list — ADR-013 explicitly deferred that decision.

---

## 5. API Client Structure

Only the three operations this screen actually calls. `listCases` (API-005) exists on the backend but
is **not** wired here — the queue screen that would use it is out of scope; do not add an unused
client function for it.

**`api/types.ts`** — mirrors `implementation/backend/app/schemas.py` / `case-service.v1.yaml` v1.5.0 exactly:

```ts
export type CaseType = 'COMPLAINT' | 'INQUIRY';
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type CaseStatus =
  | 'REGISTERED' | 'ASSIGNED' | 'IN_PROGRESS' | 'PENDING_REVIEW' | 'CLOSED' | 'REOPENED';

export interface Case {
  caseId: string;
  customerId: string;
  caseType: CaseType;
  priority: Priority;
  subject: string;
  description: string;
  status: CaseStatus;
  channel: string | null;
  customerVerified: boolean;
  assigneeId: string | null;
  unitId: string | null;
  createdAt: string;   // ISO-8601 UTC
  createdBy: string;
  updatedAt: string;   // ISO-8601 UTC
}

export interface AssignRequest { assigneeId: string; unitId: string }
export interface StatusChangeRequest {
  toStatus: CaseStatus;
  resolutionCode?: string | null;
  reason?: string | null;
}
export interface ApiErrorBody { code: string; message: string; details?: Record<string, string> }
```

Header comment in this file must point at `case-service.v1.yaml` v1.5.0 as source of truth — if the
contract ever changes, this file changes by hand (no codegen tool decided in ADR-013; not this
sprint's decision to add one).

**`api/errors.ts`**:
```ts
export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public details?: Record<string, string>) {
    super(message);
  }
}
```

**`api/client.ts`** — thin fetch wrapper:
- Reads base URL from `import.meta.env.VITE_API_BASE_URL`.
- Injects `Authorization: Bearer <token>` from `AuthContext` (see §8).
- On non-2xx: parse body as `ApiErrorBody`, throw `ApiError(status, code, message, details)`.
- On network failure (no response): throw `ApiError(0, 'NETWORK_ERROR', ...)` so callers can branch
  on `.status === 0` for the "connection problem" copy from Screen Spec §7.

**`api/cases.ts`**:
```ts
getCase(caseId: string): Promise<Case>                                    // GET /v1/cases/{caseId}
assignCase(caseId: string, body: AssignRequest): Promise<Case>            // POST /v1/cases/{caseId}/assign
changeStatus(caseId: string, body: StatusChangeRequest): Promise<Case>    // POST /v1/cases/{caseId}/status
```

No other functions in this file for this sprint.

---

## 6. React Query Strategy

- Query key: `['case', caseId]` — single convention, used by both the query and both mutations' cache writes.
- `useCase(caseId)`: `useQuery(['case', caseId], () => getCase(caseId))`. Default `staleTime: 0` — always
  refetch on mount/navigation; no background polling (Screen Spec §8 confirms no live-update requirement).
- `useAssignCase(caseId)` / `useChangeStatus(caseId)`: `useMutation`, **no retry** (avoid duplicate
  side-effecting submissions on transient failure — user must re-trigger manually).
  - `onSuccess(updatedCase)`: `queryClient.setQueryData(['case', caseId], updatedCase)` — **direct
    cache write, not `invalidateQueries`.** This is the exact mechanism behind Screen Spec §5's "response
    body replaces state directly, no refetch."
  - `onError(error)`: if `error.code === 'INVALID_STATE' || error.code === 'INVALID_TRANSITION'`
    (409s), call `queryClient.invalidateQueries(['case', caseId])` to trigger the auto-resync described
    in Screen Spec §5/§7. For all other error codes, do not invalidate — the form stays open with the
    error shown (400) or the panel stays as-is (403/404/500).
- No global query for a case list — out of scope (§2).

---

## 7. Layout Structure

```
main.tsx
  <QueryClientProvider client={queryClient}>
    <AuthProvider>                    (§8 — supplies token + claims via context)
      <RouterProvider router={router}>
        App.tsx → <Outlet />
          CaseDetailPage → CaseDetailWorkspace
```

`CaseDetailWorkspace` owns:
- The `useCase(caseId)` query result (case data, loading, error).
- The currently-open action panel state, derived from `permissions.ts` (§6/pure functions) — not
  stored as separate boolean flags per action, computed from `(case, userClaims)` each render.

Two-column layout (Screen Spec §2) implemented via CSS Grid in `CaseDetailWorkspace.module.css`:
`grid-template-columns: 1fr; @media (min-width: 1024px) { grid-template-columns: 2fr 1fr; }` — mirrors
Screen Spec §10 breakpoints (desktop ≥1024px two-column, tablet/mobile single-column with the
side-panel content becoming an accordion / the action bar becoming sticky, per §10).

---

## 8. State Management

- **Server state:** TanStack Query only, holding the single `Case` object per §6. No Redux/Zustand/Jotai
  — single-screen scope does not justify a global store (ADR-013 did not select one).
- **Local UI state:** `useState` inside individual components — form field values, dialog open/closed,
  which action form is expanded. Not lifted higher than needed.
- **Auth/claims:** `AuthContext` (React Context, not a state library) providing `{ token, userId,
  permissions: string[], supervisedUnitIds: string[] }`. Per ADR-013 item 7, **how this context gets
  populated is unresolved** — for this sprint, implement it reading from `import.meta.env.VITE_DEV_TOKEN`
  and a matching hardcoded claims object per token, mirroring the backend's dev fixtures
  (`app/auth.py` — `cs.agent.1`, `supervisor.1`, `USR-2001`, `viewer.1`, `noperm.1`). This is
  explicitly a dev-mode stand-in, not a login flow — do not build a login screen (not in Screen Spec).
- **No optimistic updates anywhere.** This is a deliberate design decision from Screen Spec §5, not an
  oversight — do not "improve" it during implementation.

---

## 9. Error Handling

Central mapping, one place only (`api/errors.ts` types + a single `getErrorCopy(error, context)`
helper used by `ErrorBanner`/inline error renderers), implementing Screen Spec §7 exactly:

| `ApiError.code` | Where | Copy source |
|---|---|---|
| `UNAUTHENTICATED` (401) | Not handled by this screen | App-shell concern per Screen Spec §7 — out of scope here; `AuthContext` may expose an `onUnauthenticated` callback for the shell to wire later, but this screen does not redirect itself |
| `FORBIDDEN` (403) on load | `ErrorBanner`, full page | "You don't have access to this case" |
| `FORBIDDEN` (403) on action | Inline on the action panel | "You don't have permission to do this" — panel stays visible |
| `NOT_FOUND` (404) | `ErrorBanner`, full page | "Case not found" |
| `VALIDATION_ERROR` (400) | `InlineFieldError` per field from `.details` | Form stays open, values preserved |
| `INVALID_STATE` (409, assign) | Inline on Assign panel | "This case is no longer assignable" + auto-resync (§6) |
| `INVALID_TRANSITION` (409, status) | Inline on Status controls | "This action is no longer available" + auto-resync (§6) |
| `INTERNAL_ERROR` (500) | Inline (action) or `ErrorBanner` (load) | Generic message + manual Retry button |
| `status === 0` (network) | Same slots as 500 | "Connection problem" — distinct copy, same retry affordance |

`error.message` from the backend is never shown verbatim as primary copy for the codes above that have
purpose-written messages (409s especially) — it's a fallback only for genuinely unexpected codes.

---

## 10. Loading Strategy

| React Query flag | UI treatment |
|---|---|
| `useCase(...).isLoading` (no data yet) | `LoadingSkeleton variant="header"` + `variant="panel"` in place of `CaseHeader`/panels |
| `useCase(...).isFetching && !isLoading` (background resync after 409) | Small inline "Refreshing case…" text near the affected panel — not a full skeleton, avoid layout jump |
| `useAssignCase/useChangeStatus.isPending` | Submit button shows spinner + disabled; form fields disabled; rest of page stays fully visible/interactive (no overlay) |

No skeleton or spinner state exists outside these three — do not add a global route-level loading
spinner, the page-level skeleton already covers first load.

---

## 11. File yang Harus Dibuat

Checklist, grouped to match §12's implementation order:

**Bootstrap (step 0)**
- [ ] `package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `.env.example`, `.eslintrc.cjs`, `.gitignore`, `README.md`
- [ ] `src/main.tsx`, `src/App.tsx`, `src/routes/router.tsx`
- [ ] `src/lib/queryClient.ts`
- [ ] `src/api/types.ts`, `src/api/errors.ts`, `src/api/client.ts`, `src/api/cases.ts`
- [ ] `src/auth/AuthContext.tsx`

**Shared primitives (step 1)**
- [ ] `src/components/StatusBadge.tsx` (+ `.module.css`)
- [ ] `src/components/PriorityBadge.tsx` (+ `.module.css`)
- [ ] `src/components/ErrorBanner.tsx` (+ `.module.css`)
- [ ] `src/components/InlineFieldError.tsx`
- [ ] `src/components/LoadingSkeleton.tsx` (+ `.module.css`)
- [ ] `src/components/Toast/Toast.tsx`, `Toast/ToastContainer.tsx` (+ `.module.css`)
- [ ] `src/styles/tokens.css`

**Read-only workspace (step 2)**
- [ ] `src/pages/CaseDetailPage.tsx`
- [ ] `src/features/case-detail/CaseDetailWorkspace.tsx` (+ `.module.css`)
- [ ] `src/features/case-detail/hooks/useCase.ts`
- [ ] `src/features/case-detail/components/CaseHeader.tsx`
- [ ] `src/features/case-detail/components/CaseInfoPanel.tsx`
- [ ] `src/features/case-detail/components/CaseMetaPanel.tsx`

**Degraded/placeholder panels (step 3)**
- [ ] `src/features/case-detail/components/CustomerReferencePanel.tsx`
- [ ] `src/features/case-detail/components/ActivityTimelinePlaceholder.tsx`

**Permission gating (step 4)**
- [ ] `src/features/case-detail/permissions.ts`
- [ ] `src/features/case-detail/components/ActionPanel.tsx`

**Assign action (step 5)**
- [ ] `src/features/case-detail/hooks/useAssignCase.ts`
- [ ] `src/features/case-detail/components/AssignActionForm.tsx`
- [ ] `src/components/ConfirmDialog.tsx` (first needed here or step 7 — build once, shared)

**Status actions, simple transitions (step 6)**
- [ ] `src/features/case-detail/hooks/useChangeStatus.ts`
- [ ] `src/features/case-detail/components/StatusActionControls.tsx`

**Status actions, close/reject (step 7)**
- [ ] `src/features/case-detail/components/ApproveCloseForm.tsx`
- [ ] `src/features/case-detail/components/RejectButton.tsx`

No other files. ~30 files total, matching the folder tree in §1 exactly.

---

## 12. Urutan Implementasi (Paling Efisien)

Same sequencing logic as Screen Spec §12, expressed as concrete build steps:

0. **Bootstrap** — Vite + React + TS project scaffold, API client layer, auth context stub, query client. Nothing renders yet; this just makes the project buildable.
1. **Shared primitives** — badges, banners, skeletons, toasts. No case-specific logic; unblocks everything downstream and is independently visually testable (e.g. in isolation via a temporary route or Storybook-less manual render).
2. **Read-only workspace** — wire `useCase`, render `CaseHeader`/`CaseInfoPanel`/`CaseMetaPanel`, full-page error states. **This alone is a shippable, usable screen** for Viewer/Manager/CS Agent personas (J-1, J-5).
3. **Degraded panels** — Customer panel, Activity Timeline placeholder. Pure presentational, no new API calls.
4. **Permission gating scaffold** — `permissions.ts` + `ActionPanel` deciding what (if anything) renders. No submit logic yet, just visibility, so it's testable against the claims stub from step 0 alone.
5. **Assign flow** — covers J-2 end to end (200/400/403/404/409/500).
6. **Simple status transitions** — Start Handling, Submit for Review — covers most of J-3.
7. **Close/Reject flow** — covers J-4 end to end, completes the permission matrix.
8. **Responsive pass** — CSS breakpoints per §10, once all content/components exist to lay out.
9. **Polish** — 409 resync UX timing, toast dismissal, focus management, ARIA labels, empty-state copy pass.

Each step after step 2 adds one journey's worth of working functionality — nothing is left half-wired
across steps.

---

## 13. Risiko Implementasi

| Risk | Mitigation | Blocking? |
|---|---|---|
| **CORS**: backend (`app/main.py`) has no `CORSMiddleware`. A Vite dev server (default port 5173) calling the backend (port 8000) directly would be blocked by the browser as cross-origin. | **Frontend-only fix:** configure a Vite dev proxy (`vite.config.ts` → `server.proxy: { '/v1': 'http://localhost:8000' }`) so browser requests are same-origin against the Vite dev server, which forwards them server-side. No backend change needed — complies with "jangan mengubah backend." | No — solved in `vite.config.ts` |
| **Auth token acquisition undecided** (ADR-013 item 7) — no login flow exists. | Dev-mode `AuthContext` reads a token from `VITE_DEV_TOKEN` env var, matching one of the backend's static dev tokens. Explicitly not production-ready; documented in `README.md` as a known limitation, not silently treated as "done." | No — documented limitation, not invented as if solved |
| **`BackToQueueLink` has no real destination** — queue screen out of scope. | Points at `/` placeholder (§2). Do not build a queue screen to "complete" the link — that would be scope creep beyond this Sprint's approved Screen Spec. | No |
| **Manual type sync** — `api/types.ts` is hand-written, not generated from `case-service.v1.yaml`. Future contract changes could silently drift. | Header comment pins the exact spec file + version as source of truth; any contract change must update this file by hand as part of that change's PR. No codegen tool introduced this sprint (not ADR-013's decision to make). | No |
| **Backend PENDING_REVIEW guard gap** (Screen Spec Gap #5: no unit-scoping on close/reject) — frontend cannot add a security boundary the API doesn't enforce. | UI shows the action whenever `cases:status` is present, matching backend behavior exactly, per Screen Spec's explicit instruction not to fake a client-side restriction. | No — already resolved in Screen Spec, restated here for implementer awareness |
| **No live updates** — another actor's changes aren't reflected until next load or a 409 forces resync. | Accepted per Screen Spec §8 (no polling/event-stream API exists). Not to be "fixed" by adding polling unprompted — that would be a UX behavior change beyond the approved spec. | No |

No item above blocks starting implementation. All have either a frontend-only fix or are explicitly
accepted, documented limitations inherited from the approved Screen Spec.

---

## 14. Definition of Done

- [ ] Every file in §11 exists; `npm run build` (Vite) and `tsc --noEmit` both succeed with zero errors.
- [ ] All five journeys (Screen Spec §1, J-1 through J-5) manually verified against a running
      `implementation/backend` (dev mode, seeded dev tokens) using the corresponding `AuthContext` stub value for each persona.
- [ ] All nine error-code/status combinations in §9 reproduced against the real backend and rendered
      per the specified copy/placement (not just happy-path tested).
- [ ] All three loading states in §10 visually verified (skeleton, mutation spinner, background resync indicator).
- [ ] Responsive behavior verified at desktop (≥1024px), tablet (768–1023px), and mobile (<768px) per Screen Spec §10.
- [ ] `git diff` confirms **zero changes** to `07 API Catalog/`, `08 Event Catalog/`, `26 Traceability/`, or `implementation/backend/` — frontend-only PR.
- [ ] No component exists beyond what's listed in Screen Spec §3/§11 and this plan's §1/§11 — no
      unrequested design-system adoption, no invented screens/routes.
- [ ] Keyboard focus management on dialog open/error appearance; ARIA labels present on
      badges/buttons/dialogs (Screen Spec §12 step 9).
- [ ] `README.md` documents: how to run (`npm install && npm run dev`), required env vars
      (`VITE_API_BASE_URL`, `VITE_DEV_TOKEN`), and the known limitations from §13 (auth stub, no
      queue screen, no live updates) so the next engineer doesn't mistake them for bugs.
- [ ] Peer review confirms implementation matches `UX-SCR-001` and `ADR-013` with no undocumented
      deviation — any deviation found during review goes back to a Screen Spec amendment, not a
      silent code-level decision.

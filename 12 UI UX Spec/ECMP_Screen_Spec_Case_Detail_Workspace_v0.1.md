# ECMP Screen Spec — Case Detail Workspace v0.1

| Field | Value |
|---|---|
| ID | UX-SCR-001 |
| Version | 0.1 |
| Owner | UX Lead / Frontend Lead |
| Reviewer | ECMF PO / Tech Lead |
| Approver | Business Owner |
| Status | 🟢 Approved — ready for implementation |
| Last Review | 2026-07-22 |
| Next Review | 2026-08-22 |

> **Sprint-04.** Product-UI screen spec under `ADR-011` (Frontend Deferral). Trigger conditions:
> (a) slice stable + gate G1 passed — **met** (Sprint-02B/03B implemented, DEC-006 frozen); (b) UI need
> validated by Business Owner — assumed satisfied by the Sprint-04 directive, not independently
> verified in-repo; formal Business Owner sign-off still recommended but not blocking. (c) scope
> grounded in personas P-01..P-05 (`UX-001`) — met, see §1.
>
> **Stack: locked by `ADR-013`** (Frontend Technology Stack, Accepted 2026-07-22) — React 18 +
> TypeScript SPA, Vite, React Router, TanStack Query, CSS Modules. Every reference to "React + TS SPA
> assumption" below is now a decision, not an assumption. `ADR-011`'s "ADR stack frontend" compliance
> item is closed.
>
> **CTO decision (2026-07-22): design approved, ADR-013 complete, no new backend endpoints or contract
> changes made. Sprint-04 is ready for frontend implementation by Cursor.**

## Known Gaps / Assumptions (read before implementing)

1. **No login/session API exists.** `app/auth.py` only recognizes static dev/CI bearer tokens (`ECMP_DEV_TOKEN` etc., ADR-007 slice phase). This screen assumes an out-of-band mechanism supplies the bearer token and decoded claims (`userId`, `permissions[]`, `supervisedUnitIds`) to the app shell — **this screen does not implement login,** and no login API should be invented to satisfy it.
2. **No activity/audit-log read API exists.** `audit_log` is persisted server-side (BR-008) but nothing exposes it over HTTP (`/_dev/events` is dev-only, gated, not for product UI). The workspace includes an Activity Timeline **placeholder**, not a live timeline. Do not invent an endpoint to fill it — flag as a future API-006 candidate for a later sprint.
3. **API-010 (Customer 360) is deferred** (Sprint-03B CTO decision, `ACR-002`). The Customer panel therefore shows only fields already present on `Case` (`customerId`, `customerVerified`) — no separate customer profile call.
4. **CLOSED → REOPENED is not implemented** in the active workflow config (`app/domain/workflow.py`; DEC-006 U-1/U-4 still open). No Reopen control exists in this version of the screen.
5. **Per-transition guard gap:** the backend enforces `cases:status` generically for PENDING_REVIEW→CLOSED/IN_PROGRESS with no additional org-unit/reviewer-role check (unlike the explicit assignee-or-supervisor guard on ASSIGNED→IN_PROGRESS). This screen reflects backend behavior as-is — it does **not** add a client-side-only restriction that the API doesn't enforce, since that would be false security. Noted here as a backend follow-up candidate, not something the frontend should paper over.

---

## 1. User Journey

Entry point for all journeys is a **Case List / Queue** screen (built on the already-shipped `GET /v1/cases`, API-005) — out of scope for this spec, referenced only as the navigation source. Selecting a row opens the Case Detail Workspace at route `/cases/:caseId`.

### J-1 — CS Agent (P-01), post-create verification
1. Just created a case (separate "New Case" screen, out of scope here) → redirected to `/cases/:caseId`.
2. Workspace loads via `GET /v1/cases/{caseId}` → shows `REGISTERED`, no assignee.
3. No action controls visible (P-01 has `cases:create`/`cases:read` only) — read-only view.
4. Can return later (manual navigation/refresh — no push/live update exists) to check status.

### J-2 — Supervisor (P-02), assignment
1. From the queue, filtered `status=REGISTERED`, opens a case.
2. Workspace shows **Assign** panel (visible: `cases:assign` + case status ∈ assignable statuses).
3. Selects `assigneeId` + `unitId`, submits → `POST /v1/cases/{caseId}/assign`.
4. On success, response `Case` (now `status=ASSIGNED`, `assigneeId`/`unitId` populated) replaces local state in place — no refetch. Assign panel is replaced by the read-only assignment summary.
5. On 409 `INVALID_STATE` (case was assigned by someone else between page load and submit), inline error + automatic re-fetch of the case to resync the UI with the real state.

### J-3 — Handler (P-04), working the case
1. Opens an assigned case from queue filtered `assigneeId=<self>&status=ASSIGNED`.
2. Sees **Start Handling** button (visible: `cases:status` + transition `ASSIGNED→IN_PROGRESS` configured + caller is assignee or unit supervisor).
3. Clicks → `POST /v1/cases/{caseId}/status {toStatus: IN_PROGRESS}` → state updates in place.
4. When done, clicks **Submit for Review** → `POST .../status {toStatus: PENDING_REVIEW}`.

### J-4 — Supervisor/Reviewer (P-02), closing
1. Opens a `PENDING_REVIEW` case.
2. Sees **Approve & Close** (requires `resolutionCode`, opens a small form/modal — mandatory field enforced client-side to avoid a round-trip, but server remains the source of truth) and **Reject** (returns to `IN_PROGRESS`, optional `reason`).
3. Approve & Close → `POST .../status {toStatus: CLOSED, resolutionCode}` → on success, case becomes read-only terminal state (no further actions in this version — reopen not implemented, see Gap #4).
4. Reject → `POST .../status {toStatus: IN_PROGRESS, reason?}` → case returns to Handler's queue.

### J-5 — Manager/Executive (P-05) or Viewer
1. Opens any case via `cases:read`.
2. Entirely read-only — no action panel rendered at all (no `cases:assign`/`cases:status`).

---

## 2. Screen Layout

Two-column workspace layout (desktop reference — see §10 for smaller breakpoints):

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to queue        CASE-00AB12CD34   [STATUS] [PRIORITY]     │  Header
├─────────────────────────────────────────────┬───────────────────┤
│ MAIN COLUMN (≈68%)                           │ SIDE COLUMN (≈32%)│
│                                               │                   │
│  Subject / Description                       │  Customer          │
│  (caseType, channel, createdAt/By)           │  reference panel   │
│                                               │  (degraded)        │
│  Activity Timeline (placeholder)             │                   │
│                                               │  Case meta panel   │
│  Action Panel                                │  (assignee, unit,  │
│   - Assign form  OR                          │   updatedAt)       │
│   - Status controls                          │                   │
│   (exactly one renders, or none)             │                   │
└───────────────────────────────────────────────┴───────────────────┘
```

- Header is sticky on scroll; always shows caseId + current status/priority badges regardless of scroll position, so the user never loses status context while reading a long description.
- Main column is the task surface (read + act). Side column is reference-only context, never contains primary actions.

---

## 3. UI Components

Reusable, screen-agnostic components (usable by future screens, e.g. the queue list):

| Component | Purpose |
|---|---|
| `StatusBadge` | Renders `CaseStatus` enum value with a fixed color mapping (see below) |
| `PriorityBadge` | Renders `Priority` enum value |
| `CaseHeader` | Sticky header: back link, caseId, StatusBadge, PriorityBadge |
| `CaseInfoPanel` | subject, description, caseType, channel, createdAt, createdBy |
| `ActivityTimelinePlaceholder` | Empty-state component explaining history isn't available yet (Gap #2) |
| `CustomerReferencePanel` | Degraded customer info: customerId + customerVerified (Gap #3) |
| `CaseMetaPanel` | assigneeId, unitId, updatedAt |
| `AssignActionForm` | assigneeId + unitId inputs, submit button, inline validation/error |
| `StatusActionControls` | Renders the correct button(s)/form for the case's current status per the configured transition set |
| `ApproveCloseForm` | resolutionCode input (required) + confirm |
| `ConfirmDialog` | Generic confirm-before-submit wrapper (used for Approve & Close, Reject) |
| `ErrorBanner` | Full-width banner for page-level errors (404, 500, 401) |
| `InlineFieldError` | Field-level error rendering from `Error.details` (400 VALIDATION_ERROR) |
| `LoadingSkeleton` | Placeholder blocks matching CaseHeader/CaseInfoPanel shape |
| `Toast` / `ToastContainer` | Transient success/error feedback for actions |

Status → color mapping (for `StatusBadge`, consistent across the product going forward):
`REGISTERED`=neutral gray, `ASSIGNED`=blue, `IN_PROGRESS`=amber, `PENDING_REVIEW`=purple, `CLOSED`=green, `REOPENED`=red.

---

## 4. Backend APIs Used

All from `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 — **no new endpoint required.**

| Action | API | Permission | Notes |
|---|---|---|---|
| Load case | `GET /v1/cases/{caseId}` (API-002) | `cases:read` | On mount, and after any error requiring resync |
| Assign/reassign | `POST /v1/cases/{caseId}/assign` (API-003) | `cases:assign` | Body: `AssignRequest{assigneeId, unitId}` |
| Change status | `POST /v1/cases/{caseId}/status` (API-004) | `cases:status` | Body: `StatusChangeRequest{toStatus, resolutionCode?, reason?}`; used for Start Handling, Submit for Review, Approve & Close, Reject |

**Explicitly not used / not available:** API-010 (Customer 360, deferred), any audit/activity endpoint (doesn't exist), any notification endpoint (doesn't exist — Notification is a backend-only consumer, FR-020). API-005 (list) is used by the *queue* screen that navigates into this one, not by this screen itself.

`assigneeId`/`unitId` input on `AssignActionForm` are free-text in this version (no user/unit directory API exists to populate a picker) — validated only for non-empty per the contract's `minLength: 1`. Flag as a follow-up: a directory lookup API would improve this, but is out of scope — **do not invent one for this sprint.**

---

## 5. Data Flow

```
mount
  └─ GET /v1/cases/{caseId}
       ├─ 200 → set case state, render workspace
       ├─ 404 → render full-page "case not found" (ErrorBanner + back-to-queue CTA)
       ├─ 401 → redirect to session-expired handling (app-shell concern, not this screen)
       └─ 403 → render full-page "you don't have access" (distinct from 404 — case exists, caller lacks cases:read)

user submits Assign / Status action
  └─ disable form, show inline spinner (pessimistic — no optimistic update; state transitions
     are business-significant and must reflect server truth)
  └─ POST .../assign or .../status
       ├─ 2xx → replace case state with response body directly (no refetch needed — response
       │        IS the updated Case); show success Toast; re-render action panel for new status
       ├─ 400 VALIDATION_ERROR → keep form open, map `details` to InlineFieldError per field
       ├─ 403 FORBIDDEN → inline error on the action panel only (rest of page stays interactive);
       │                   do not hide the control that just failed — the user needs to see why
       ├─ 404 NOT_FOUND → full-page error (case was deleted/never existed — edge case)
       ├─ 409 INVALID_STATE / INVALID_TRANSITION → inline error + automatically re-fetch
       │                   GET /v1/cases/{caseId} to resync (another actor changed the case)
       └─ 500 INTERNAL_ERROR → inline error with a manual Retry button (no auto-retry)
```

State is held at the `CaseDetailWorkspace` root (single source of truth for the current `Case` object) and passed down; child components are presentational and receive the case + callbacks, they do not fetch independently.

---

## 6. Permissions

Client-side visibility is a **UX convenience**, not a security boundary — the API is the enforcement point (401/403 above). Controls are hidden when clearly inapplicable, but every submit path still handles 403 gracefully in case claims are stale.

| Control | Requires | Additional condition |
|---|---|---|
| View workspace at all | `cases:read` | — |
| Assign panel | `cases:assign` | `case.status` ∈ assignable set (currently `REGISTERED`; `REOPENED` configured but unreachable, Gap #4) |
| Start Handling button | `cases:status` | `case.status == ASSIGNED`; **and** (`user.userId == case.assigneeId` OR `case.unitId ∈ user.supervisedUnitIds`) — mirrors the one explicit backend guard |
| Submit for Review button | `cases:status` | `case.status == IN_PROGRESS` |
| Approve & Close form | `cases:status` | `case.status == PENDING_REVIEW` (no additional backend guard today — see Gap #5) |
| Reject button | `cases:status` | `case.status == PENDING_REVIEW` (same caveat) |

Roles → controls (per `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` v0.3):

| Role | Permissions | Sees |
|---|---|---|
| CS Agent (P-01) | `cases:create`, `cases:read` | Read-only workspace |
| Supervisor (P-02) | `cases:assign`, `cases:read`, `cases:create` | Assign panel; status controls only if also unit supervisor of an in-progress case |
| Handler (P-04) | `cases:status`, `cases:read` | Status controls (subject to assignee/supervisor guard) |
| Viewer / Manager (P-05) | `cases:read` only | Read-only workspace |

---

## 7. Error States

| HTTP / code | Where shown | Treatment |
|---|---|---|
| 401 `UNAUTHENTICATED` | Global | App-shell responsibility (not this screen) — redirect to re-auth |
| 403 `FORBIDDEN` on load | Full page | "You don't have access to this case" + back-to-queue CTA (distinct copy from 404) |
| 403 `FORBIDDEN` on action | Inline, on the action panel | "You don't have permission to do this" — panel stays visible, not removed |
| 404 `NOT_FOUND` | Full page | "Case not found" + back-to-queue CTA |
| 400 `VALIDATION_ERROR` | Inline, per field via `details` | Field-level messages; form stays open with entered values preserved |
| 409 `INVALID_STATE` (assign) | Inline, on Assign panel | "This case is no longer assignable" + auto-resync |
| 409 `INVALID_TRANSITION` (status) | Inline, on Status controls | "This action is no longer available" + auto-resync |
| 500 `INTERNAL_ERROR` | Inline (action) or full page (load) | Generic message + manual Retry |
| Network/timeout (no HTTP response) | Same as 500 | Distinguish copy ("connection problem") but same retry affordance |

All error rendering reads the `Error{code, message, details?}` envelope — `code` drives behavior, `message` is a fallback display string only (not to be shown as the primary UX copy verbatim for expected cases like 409, which get purpose-written messages above).

---

## 8. Loading States

| Moment | Treatment |
|---|---|
| Initial page load | `LoadingSkeleton` matching CaseHeader + CaseInfoPanel + side panel shapes (avoid layout shift on data arrival) |
| Assign/Status submit | Inline spinner on the submit button; form fields disabled; **rest of the page remains fully visible and interactive** (no full-page overlay — user must still be able to read case details while deciding) |
| Post-error resync (409 auto-refetch) | Small inline "Refreshing case…" indicator near the affected panel, not a full skeleton (avoid jarring reflow for what is effectively a background correction) |

No polling/auto-refresh exists in this version — the case only updates on user-triggered load or after a successful/409 action. This is a known limitation (no event stream API for the frontend to subscribe to); acceptable for this sprint, worth flagging as a future enhancement (not to be solved by inventing an endpoint now).

---

## 9. Empty States

| Area | Condition | Copy/treatment |
|---|---|---|
| Activity Timeline | Always (no API) | "Activity history isn't available yet" — explicit placeholder, not silently omitted (Gap #2) |
| Customer panel | Always (API-010 deferred) | Shows `customerId` + an "Unverified" or "Reference only — full profile not yet available" badge depending on `customerVerified`; never fabricates name/contact fields (Gap #3) |
| Assignee (Case meta) | `assigneeId == null` | "Unassigned" label instead of blank |
| Channel | `channel == null` | "—" (dash), not blank, not "null" |
| Action panel | User has no applicable permission/state combination | Panel section omitted entirely (not an empty box) — read-only view has no dangling "no actions available" clutter |

---

## 10. Responsive Behavior

| Breakpoint | Layout |
|---|---|
| Desktop (≥1024px) | Two-column as in §2 (≈68/32 split) |
| Tablet (768–1023px) | Single column; side panel content (Customer, Meta) collapses into an expandable "Details" accordion below the main content, collapsed by default |
| Mobile (<768px) | Single column; header becomes two-line (caseId+back on line 1, badges on line 2) to fit width; primary action (whichever single action applies) becomes a **sticky bottom action bar**; secondary actions (e.g. Reject) available via an overflow/kebab menu next to the sticky button to avoid crowding |

Sticky header and sticky bottom action bar must not overlap — bottom bar only appears on mobile where the two-column layout has already collapsed.

---

## 11. Component Hierarchy

```
CaseDetailWorkspace                      (route: /cases/:caseId; owns Case state + fetch/mutate logic)
├── LoadingSkeleton                      (shown while initial fetch in flight)
├── ErrorBanner                          (shown for full-page 403/404/500 on load; replaces everything below)
└── (once loaded, mutually exclusive with ErrorBanner)
    ├── CaseHeader
    │   ├── BackToQueueLink
    │   ├── StatusBadge
    │   └── PriorityBadge
    ├── CaseDetailLayout
    │   ├── MainColumn
    │   │   ├── CaseInfoPanel
    │   │   ├── ActivityTimelinePlaceholder
    │   │   └── ActionPanel                        (renders 0 or 1 of the following, per §6)
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
    └── ToastContainer                    (portal-rendered, outside layout flow)
```

---

## 12. Implementation Order

Sequenced so each step is independently testable and the screen is usable (read-only) as early as possible:

1. **Shared primitives** — `StatusBadge`, `PriorityBadge`, `LoadingSkeleton`, `ErrorBanner`, `InlineFieldError`, `Toast`/`ToastContainer`. No case-specific logic; unblock everything else.
2. **Read-only workspace** — `CaseDetailWorkspace` root with `GET /v1/cases/{caseId}` fetch, `CaseHeader`, `CaseInfoPanel`, `CaseMetaPanel`, full-page error handling (401/403/404/500 per §7/§9). Ships a usable screen for Viewer/Manager/CS Agent personas immediately.
3. **Degraded/placeholder panels** — `CustomerReferencePanel` (degraded per Gap #3), `ActivityTimelinePlaceholder` (per Gap #2). No new API calls; purely presentational against data already in `Case`.
4. **Permission-aware action gating** — utility/hook that reads current user claims + case state to decide which action panel (if any) renders, per §6. No submit logic yet — just visibility.
5. **AssignActionForm** — wire to `POST .../assign`; cover 200/400/403/404/409/500 per §5/§7.
6. **StatusActionControls, simple transitions** — Start Handling, Submit for Review (no extra form fields); wire to `POST .../status`.
7. **ApproveCloseForm + RejectButton** — resolutionCode requirement, `ConfirmDialog` wrapper, reason field for reject.
8. **Responsive pass** — tablet accordion, mobile sticky action bar, per §10.
9. **Polish & edge cases** — 409 auto-resync behavior, toast timing/dismissal, accessibility (focus management on error, ARIA labels for badges/buttons), empty-state copy review with UX Lead.

---

## Related
- `07 API Catalog/openapi/case-service.v1.yaml` v1.5.0 (API-002/003/004/005) — unchanged by this design
- `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003)
- `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` v0.3
- `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (UX-001)
- `05 Architecture Decision Records/ECMP_ADR_011_Frontend_Deferral_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_013_Frontend_Technology_Stack_v1.0.md` — stack decision this spec is now built against
- `implementation/backend/ACR_SPRINT02B.md` (ACR-002 — API-010 deferral)

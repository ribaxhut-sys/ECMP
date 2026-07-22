# ECMP Milestone 2 — Case Management Experience: Implementation Plan

Engineering plan only — no code. Covers: Case Timeline, Internal Notes/Comments, Attachments,
Audit History, Unified Empty/Loading/Error UX.

## Headline Finding (read this before the per-feature sections)

**Four of the five requested items have zero backend support today.** Only "Unified Empty/Loading/
Error UX" is pure frontend. This is not a framing choice — it's what's actually in the repo:

| Feature | Backend today | Verdict |
|---|---|---|
| Case Timeline | Nothing exposed. `audit_log` table exists (populated on every write, BR-008) but no API reads it. `ActivityTimelinePlaceholder.tsx` already says so explicitly ("No audit-log read API exists — do not invent one"). | **NOT IMPLEMENTED** — needs one new, small, read-only endpoint |
| Audit History | Same gap as Timeline — same underlying data. | **NOT IMPLEMENTED** — can share Timeline's endpoint (see §4) |
| Internal Notes/Comments | No table, no API, no FR/BR, no mention anywhere in `03 Functional Requirements` beyond one incidental Gherkin example unrelated to case notes. | **NOT IMPLEMENTED** — new domain concept, not just a missing endpoint |
| Attachments | No table, no API, no storage integration, no ADR. Directly overlaps `DEC-006` open item **U-3** ("Evidence untuk COMPLAINT closure... mekanisme evidence menunggu FRD revisi") — already known-open, not new. | **NOT IMPLEMENTED** — largest gap, likely needs its own ADR |
| Unified Empty/Loading/Error UX | `ErrorBanner`, `LoadingSkeleton`, `EmptyState`, `InlineFieldError`, `Toast`, `ConfirmDialog` already exist and are already reused across Case Detail and Case Queue. | **PARTIALLY IMPLEMENTED** — primitives done; only a shared *consumption pattern* for future panels is missing |

"Minimize backend changes" is achievable, but not "zero." I've sized each gap below and picked the
smallest change that satisfies it, and I'm flagging Attachments as likely too large for this
milestone rather than force-fitting it.

**On governance:** three of these features need a contract-first gate (FRD delta + OpenAPI draft +
freeze decision) before any code, per this repo's own established pattern (`DEC-006` did exactly this
for assign/status). I'm identifying what each gate needs to cover, not writing the FRD/OpenAPI content
myself — that's a Business Analyst / Architecture Board artifact, not something to produce inside an
"implementation plan, no code" deliverable. Where I propose a contract shape below, it's marked
**(proposed, unfrozen)** and is a starting point for that gate, not a decision.

---

## 1. Case Timeline

**Status: NOT IMPLEMENTED.**

### Backend Gate (prerequisite, not part of this plan's frontend work)
- New FR needed (e.g. FR-006 "View case activity timeline") — small AC: read-only, `cases:read`
  permission (reuse, no new permission), sourced from `audit_log`.
- New OpenAPI operation, **(proposed, unfrozen)**:
  `GET /v1/cases/{caseId}/timeline` → `{ entries: [{ actionCode, actorUserId, occurredAt, summary }] }`.
  No new table. No new write path. This is the smallest possible backend footprint for this feature —
  it's a projection over data the system already writes on every case mutation.
- Must go through the same freeze discipline as `DEC-006`: FRD delta → OpenAPI draft → review → merge
  into `case-service.v1.yaml` (next minor version) → **then** frontend work starts.

### Reusable Components (once contract exists)
- `LoadingSkeleton`, `ErrorBanner`, `EmptyState` — all already exist, reused as-is.
- New: `CaseActivityTimeline` (replaces `ActivityTimelinePlaceholder`), `TimelineEntryRow`,
  `useCaseTimeline(caseId)` (TanStack Query, same conventions as `useCase`).

### Component Changes
- `CaseDetailWorkspace.tsx`: swap `<ActivityTimelinePlaceholder />` for `<CaseActivityTimeline
  caseId={caseId} />`. This is the **only** touch to an already-shipped file, and it's a one-line
  swap, not a redesign of the workspace.

### Acceptance Criteria
1. Opening a case with at least one status/assignment change shows a chronologically ordered list of entries.
2. A freshly created case (no transitions yet) shows an empty state ("No activity yet"), not an error.
3. 403/500 on the timeline call render inline within the Activity panel only — do not take down the rest of the workspace (same isolation principle as the existing Action Panel error handling).
4. No new permission required — verified against `cases:read`.

---

## 2. Internal Notes / Comments

**Status: NOT IMPLEMENTED** — this is a new domain capability, not a missing endpoint over existing data.

### Backend Gate (prerequisite)
Genuinely new, and the business rules aren't decided yet — these need a real FRD, not an assumption:
- Is a note editable or deletable after posting, or append-only (mirrors the audit-log philosophy
  already used elsewhere, BR-008)? **Recommend append-only for v1** — smallest contract, smallest
  permission surface, consistent with this codebase's existing bias (no case field is ever mutated
  outside the defined transitions; notes shouldn't be the first mutable-after-write entity).
- Who can post a note — everyone with `cases:read`, or a new permission? **Recommend a new
  permission** (e.g. `cases:notes:create`) rather than overloading `cases:read` — read and write
  should stay separable, matching the existing `cases:read`/`cases:create` split pattern.
- Visible to which roles — same visibility as the case itself, or restricted? Assume same as case
  read access unless BA says otherwise.
- New table: `case_notes(note_id, case_id, author_user_id, body, created_at)`.
- New OpenAPI operations **(proposed, unfrozen)**:
  `POST /v1/cases/{caseId}/notes` (permission `cases:notes:create`) →  returns the created note.
  `GET /v1/cases/{caseId}/notes` (permission `cases:read`) → `{ items: [{noteId, authorUserId, body, createdAt}] }`.
- Role Access Matrix delta needed (new permission) — same weight as the `cases:assign`/`cases:status`
  additions in `DEC-006`, so expect a comparable review cycle, not a quick add.

### Reusable Components
- `ErrorBanner`, `LoadingSkeleton`, `EmptyState`, `InlineFieldError`, `Toast` — all reused.
- Pattern reused: `AssignActionForm`'s form/validation/submit structure is the closest existing
  analog (client-side required-field check, server error mapping, toast on success) — new
  `NoteComposer` should follow the same shape, not invent a new form pattern.

### Component Changes
- New feature folder `src/features/case-notes/` (components: `NotesPanel`, `NoteComposer`,
  `NoteListItem`; hooks: `useCaseNotes`, `useAddNote`).
- `CaseDetailWorkspace.tsx`: add `<NotesPanel caseId={caseId} />` to the main column, below Timeline.
  Additive only — no existing panel logic changes.

### Cache Strategy
- `useAddNote`: on success, don't `setQueryData` a single note into a list optimistically — **append
  via `invalidateQueries(['case-notes', caseId])`** instead. Unlike Assign/Status (single-resource
  mutation, response IS the new state), a note *create* returns one note but the panel needs the
  *list* — invalidate-and-refetch is the correct, simpler choice here, not a deviation from the
  established "no optimistic updates" principle.

### Acceptance Criteria
1. Posting a note with `cases:notes:create` appends it to the list, newest last (or first — BA to confirm ordering; default to chronological ascending like a comment thread).
2. Posting without the permission → 403, matches the existing inline-error-on-action-panel pattern.
3. Empty case (no notes yet) shows "No notes yet," not an error.
4. Notes are never editable or deletable in v1 UI — no edit/delete affordance exists (matches the append-only backend decision above).

---

## 3. Attachments

**Status: NOT IMPLEMENTED — recommend excluding from this milestone's build scope.**

This is the one item where I'm not proposing a contract, because the prerequisite decision is
architectural, not just a new endpoint:

- **No file storage backend exists or is decided** (local disk vs. S3-compatible object storage vs.
  something else) — this is genuinely an ADR-level decision (storage choice, retention, encryption
  at rest), not something that fits inside "minimize backend changes."
- **Directly overlaps an already-open item**: `DEC-006` U-3 explicitly deferred "Evidence untuk
  COMPLAINT closure" (BR-ECMF-06) pending an FRD revision — that's this feature. It's not a new gap
  I'm discovering; it's a known one the project already chose not to solve yet.
- Security surface (upload size limits, allowed content types, scanning) is real and untouched —
  `10 Security and Access Standards` has no attachment-handling policy today.

**Recommendation:** treat Attachments as its own gated initiative (new ADR for storage + FRD +
OpenAPI, resolving DEC-006 U-3 explicitly), not as a Milestone 2 deliverable. If the CTO wants it in
this milestone anyway, the first deliverable is the storage ADR, not any code or UI — flagging this
now rather than silently scoping a feature I can't respect "minimize backend changes" for.

*(No component/acceptance-criteria/cache sections below, since this item isn't scoped for build yet.)*

---

## 4. Audit History

**Status: NOT IMPLEMENTED** — same underlying gap as Timeline.

### Backend Gate (prerequisite)
**Reuse Timeline's endpoint rather than adding a second one** — this is the concrete way to honor
"minimize backend changes" for this pair: one `GET /v1/cases/{caseId}/timeline` (or a more neutral
name like `/audit-trail` if the BA prefers, decided at the same gate as §1) serves both:
- **Timeline** renders a curated, human-readable narrative (e.g. "Assigned to USR-2001" instead of
  raw payload).
- **Audit History** renders the same entries with full technical detail (raw `action`, full
  `new_value` diff, `actorUserId`) — a denser, unfiltered view of the same data.

Two frontend components, one backend contract. **Decision point for the gate, not decided here:**
should Audit History require a *different* permission than Timeline (e.g. only Administrators see
raw payloads, everyone with `cases:read` sees the curated narrative)? If so, the endpoint needs a
`detail=full|summary` param or two permission-gated fields in the same response — either is a minor
contract addition, not a second endpoint. Flagging for the BA/Architecture Board to decide at the
same gate as Timeline, not deciding it unilaterally here.

### Reusable Components
Same primitives as Timeline. New: `AuditHistoryPanel`, `AuditEntryRow` (denser rendering of the same
`useCaseTimeline` data — likely shares the hook, not a separate query).

### Acceptance Criteria
1. Every entry visible in Timeline is also visible in Audit History (same source, different rendering) — no data present in one and missing from the other.
2. If a permission split is adopted, a user without the elevated permission sees Timeline but not Audit History (or a redacted version) — exact behavior depends on the gate decision above.

---

## 5. Unified Empty / Loading / Error UX

**Status: PARTIALLY IMPLEMENTED.** No backend dependency at all.

### What already exists (do not rebuild)
`ErrorBanner`, `LoadingSkeleton`, `EmptyState`, `InlineFieldError`, `Toast`/`ToastContainer`,
`ConfirmDialog` — all shipped, all already reused correctly by Case Detail and Case Queue.

### What's actually missing
Not the primitives — a **consistent pattern for consuming them.** Right now, `CaseDetailWorkspace.tsx`
hand-rolls its own `if (query.isLoading) {...} if (caseGone) {...} if (query.isError) {...}` chain.
That's fine for one screen, but Timeline, Notes, and (eventually) Audit History are three more panels
that will each need the same loading/error/empty branching — without a shared pattern, each one
reimplements it slightly differently, which is exactly how UX inconsistency creeps in.

**Proposal:** a small shared `<AsyncPanel>` wrapper (or equivalent hook, e.g. `useAsyncPanelState`)
taking `{ isLoading, isError, error, isEmpty, emptyMessage }` and rendering the correct one of
`LoadingSkeleton` / `ErrorBanner` / `EmptyState` / `children` — one place that encodes "this is what
a loading/error/empty panel looks like everywhere in ECMP."

### Explicit scope boundary (per "do not redesign completed modules")
**`AsyncPanel` is used by the *new* panels (Timeline, Notes, Audit History) only.** `CaseDetailWorkspace.tsx`
and the Case Queue workspace are **not** retrofitted to use it in this milestone — that would be
redesigning already-shipped, already-verified code for stylistic consistency, which is explicitly out
of scope. The inconsistency between old (hand-rolled) and new (`AsyncPanel`-based) screens is accepted
as technical debt (see §Technical Debt), not fixed now.

### Component Changes
- New: `src/components/AsyncPanel.tsx` (+ `.module.css`), used only by `CaseActivityTimeline`,
  `NotesPanel`, `AuditHistoryPanel` as they're built.

### Acceptance Criteria
1. All three new panels (Timeline, Notes, Audit History) use `AsyncPanel` — verified by code review, not just visually.
2. No existing file outside the three new panels imports `AsyncPanel` in this milestone.
3. Loading/error/empty visual treatment is identical across the three new panels (same skeleton shape family, same error banner style, same empty-state copy tone).

---

## Implementation Order

1. **`AsyncPanel` shared pattern** (§5) — pure frontend, no dependency, de-risks everything after it. Build first.
2. **Timeline + Audit History backend gate** (§1/§4) — smallest backend lift (one read endpoint, no new table, no new permission, reuses `audit_log`). Run the FRD/OpenAPI freeze cycle, then build both frontend panels together since they share one query hook.
3. **Notes backend gate** (§2) — medium backend lift (new table, new permission, real BA decisions on edit/visibility). Run its own freeze cycle after Timeline's is done (don't parallelize two contract gates through the same review capacity). Then build `NotesPanel`.
4. **Attachments** — not sequenced in this milestone. First deliverable if pursued is a storage ADR, separate from this plan.

Rationale for this order: cheapest-and-most-derisking first (§5), then smallest real backend addition
(§1/§4, reuses existing data), then the medium one with open business questions (§2), leaving the
largest and most architecturally unresolved one (§3 Attachments) explicitly out rather than jamming it
in at the end under time pressure.

---

## Risks

| Risk | Notes |
|---|---|
| Notes scope creep | Edit/delete/visibility rules aren't decided. Mitigated by recommending append-only + reuse-existing-visibility as the v1 default — if the BA wants more, that's a scope change to flag then, not assume now. |
| Timeline/Audit History coupling | Sharing one endpoint for two features risks one's future needs constraining the other's. Mitigated by keeping the payload raw/generic (§4) rather than baking presentation choices into the API. |
| Attachments pressure to compress the storage decision | Rushing an ADR-level decision (storage backend, security policy) to hit a milestone date is how bad architecture happens. Recommend explicit descope, not a rushed ADR. |
| Two contract-first gates in one milestone (§1/§4 and §2) | Each gate is real review capacity (FRD, OpenAPI, Role Matrix delta, sign-off) — sequencing them (not parallel) is deliberate to avoid both stalling on the same reviewers. |
| `AsyncPanel` adopted inconsistently | If a future engineer "helpfully" retrofits it into Case Detail/Queue mid-milestone, that's an unplanned redesign of shipped code — explicitly called out in §5 as out of scope, worth restating in code review. |

## Technical Debt

- **Old vs. new loading/error/empty pattern coexist** — `CaseDetailWorkspace`'s hand-rolled branching
  is not migrated to `AsyncPanel` this milestone (deliberate, see §5). Revisit in a future milestone
  if the duplication becomes costly to maintain.
- **Timeline/Audit History share one backend endpoint** — efficient now, but if their data needs
  diverge significantly later (e.g. Audit History needs pagination for long-lived cases, Timeline
  doesn't), they'll need to split. Not a problem today; flagged for future awareness.
- **DEC-006 U-3 remains open** — Attachments' descope means the case-closure "evidence" gap identified
  back in Sprint-02A is still unresolved. Not new debt, just not paid down this milestone either.
- **Notes has no edit/delete path by design** — if the business later wants correction/retraction,
  that's a new decision (probably "supersede with a new note" rather than mutate, to preserve the
  append-only property), not an oversight to silently fix later.

---

## Related
- `implementation/frontend/IMPLEMENTATION_PLAN.md` (Case Detail Workspace — `AsyncPanel` sits alongside, not inside, this)
- `implementation/frontend/IMPLEMENTATION_PLAN_CASE_QUEUE.md` (Case Queue — same non-retrofit boundary applies)
- `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` Gap #2 (Activity Timeline placeholder, resolved by §1 here)
- `27 Project Decisions/DEC-006_Contract_Freeze_G1_Sprint02A_v1.0.md` U-3 (Attachments/evidence, still open)
- `implementation/backend/app/models.py` (`AuditLogModel` — the data source for §1/§4)

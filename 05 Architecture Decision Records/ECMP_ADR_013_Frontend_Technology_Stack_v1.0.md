# ECMP_ADR_013_Frontend_Technology_Stack_v1.0

| Field | Value |
|---|---|
| ID | ADR-013 |
| Version | 1.0 |
| Owner | Solution Architect / Tech Lead |
| Reviewer | UX Lead / Frontend Lead |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-22 |

- ADR Status: Accepted (CTO decision, Sprint-04, 2026-07-22)
- Repository strategy: Remain active (PROGRAM-ADR-002 BR-007). Future change requires a separate ADR. Do not supersede via FE documentation.
- Date: 2026-07-22
- Decision Owners: CTO, Solution Architect
- Related Domains: All (product UI)

> **Numbering note:** the CTO decision that commissioned this ADR referred to it as "ADR-012," but
> `ADR-012` is already taken by `ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md` (**Accepted**).
> This decision is filed as **ADR-013**, the next free slot, to avoid overwriting or renumbering an
> existing ADR. No content conflict exists between the two — ADR-012 is about auth architecture,
> this one is about frontend stack.

## Context
`ADR-011` (Frontend Deferral) named React + TypeScript SPA as the *default candidate* but explicitly
deferred the actual stack decision to a dedicated ADR, to be written once ADR-011's trigger conditions
were met and real screen-spec data existed. Sprint-04 produced the first screen spec (`UX-SCR-001`,
Case Detail Workspace) against that candidate. The CTO has now approved the design and directed that
this ADR be written before Cursor starts frontend implementation, satisfying ADR-011's compliance
checklist item "ADR stack frontend — saat trigger butir 2 tersentuh."

This ADR is intentionally narrow: it locks the stack needed to implement `UX-SCR-001` as specified,
not a general-purpose frontend platform strategy. It does not add, remove, or modify any backend
endpoint or contract (`07 API Catalog/openapi/case-service.v1.yaml` is unaffected).

## Decision Drivers
- Match the default candidate already named in ADR-004/ADR-011 — no re-litigation needed
- Fit `UX-SCR-001`'s data flow (pessimistic mutation, inline error/validation states, client-side
  permission-aware rendering) without inventing new backend capability
- Minimize new operational surface for a single-screen first slice
- Compatibility with AI-assisted implementation (Cursor) — mainstream, well-documented choices

## Decision
1. **Framework:** React 18+ with TypeScript, as a client-rendered SPA.
2. **Build tool:** Vite (dev server + build). No SSR/meta-framework (Next.js etc.) — not needed for
   an authenticated, behind-login internal tool; adds complexity `UX-SCR-001` does not require.
3. **Routing:** React Router — `/cases/:caseId` per `UX-SCR-001` §11, plus whatever route the
   (out-of-scope) queue screen uses later.
4. **Server-state / data fetching:** TanStack Query (React Query) for the `GET`/`POST` calls to
   `case-service.v1.yaml`. Matches the spec's pessimistic-update pattern (§5) directly — mutation
   hooks, no manual cache invalidation logic to hand-roll.
5. **Styling:** CSS Modules, no component/design-system library adopted yet. `UX-SCR-001` defines
   its own component set (`StatusBadge`, `ErrorBanner`, etc.) at a level of detail implementable
   without a UI kit; adopting one now would be a second, unrequested decision.
6. **HTTP client:** native `fetch`, wrapped in a thin typed client generated/hand-written from
   `case-service.v1.yaml` (source of truth for request/response shapes — no separate schema).
7. **Auth token handling:** **not decided here.** `UX-SCR-001` §"Known Gaps" already flags that no
   login/session API exists (`ADR-007` is still slice-phase static tokens). This ADR locks the
   *rendering/data* stack only; how the SPA acquires and stores a bearer token is an explicit
   follow-up, not blocking `UX-SCR-001` implementation in a dev/pilot context (token can be
   injected via env/config for now, same as backend CI does today).
8. **Code location:** `implementation/frontend` (currently an empty placeholder — see
   `implementation/frontend/.gitkeep`).

## Options Considered
### Option A — React + TypeScript SPA (chosen)
- Pros: matches ADR-004/ADR-011 default candidate; large ecosystem; TanStack Query fits the
  pessimistic-mutation pattern in `UX-SCR-001` directly; good Cursor/AI-assist support.
- Cons: introduces a client build pipeline (`21 Technical Standards` TypeScript/React standard was
  Planned pending exactly this ADR).

### Option B — Server-rendered (FastAPI + Jinja, matching `implementation/portal`)
- Pros: reuses an already-proven pattern in this repo; no separate JS build pipeline.
- Cons: weaker fit for `UX-SCR-001`'s inline, non-page-reload state transitions (Assign/Status
  actions with optimistic-vs-pessimistic handling, per-field validation errors, toasts) — would
  require hand-rolled JS on top of server templates anyway, without the ecosystem support of A.
- CTO decision (Sprint-04 design review): rejected in favor of Option A.

## Consequences
### Positive
- `UX-SCR-001` can move to implementation without a second design pass — component hierarchy (§11)
  and data flow (§5) map directly onto React components + TanStack Query hooks.
- `21 Technical Standards` TypeScript/React standard can now be activated (was Planned pending this
  ADR, per ADR-011 compliance checklist).

### Negative / Trade-offs
- New build/deploy surface (`implementation/frontend`) — CI, deployment pipeline for the SPA are
  follow-up work, not covered by this ADR.
- Auth token acquisition remains unresolved (item 7) — must be revisited before any non-dev
  environment exposes this screen to real users.

### Follow-up Actions
- [ ] Bootstrap Vite + React + TypeScript project under `implementation/frontend`
- [ ] Activate TypeScript/React Standard in `21 Technical Standards` (ADR-011 compliance item)
- [ ] Decide token acquisition mechanism before any non-dev deployment (separate ADR or Project
      Decision — not blocking `UX-SCR-001` dev-mode implementation)
- [ ] Update `ADR-011` compliance checklist to check off "ADR stack frontend" and reference this ADR

## Related
- `05 Architecture Decision Records/ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0.md` (backend stack; named React+TS as default candidate)
- `05 Architecture Decision Records/ECMP_ADR_011_Frontend_Deferral_v1.0.md` (trigger conditions this ADR satisfies)
- `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` (UX-SCR-001 — first screen built against this stack)
- `07 API Catalog/openapi/case-service.v1.yaml` (unchanged by this ADR)

# ECMP Frontend Development Standards v1.0

| Field | Value |
|---|---|
| ID | FE-STD-001 |
| Program | PROGRAM-FRONTEND-002 |
| Phase | PHASE-0 (Documentation / governance only) |
| Version | 1.0 |
| Owner | Frontend Lead / Tech Lead |
| Reviewer | Solution Architect / Security Architect / UX Lead |
| Approver | Architecture Board |
| Lifecycle | BASELINE |
| Status | 🟢 BASELINE |
| Last Review | 2026-07-30 |
| Next Review | 2026-08-30 |
| Architecture SoT | [`FRONTEND_ARCHITECTURE_v1.2.md`](./FRONTEND_ARCHITECTURE_v1.2.md) (FE-ARCH-001) |
| Canonical tree | `frontend/` (DEC-019) |

## Document control

| Item | Value |
|---|---|
| Purpose | Define **how** frontend code must be implemented in the canonical product UI |
| Non-goals | Redesign architecture; invent APIs/events; choose new libraries; implement application code; decide mount/topology technology |
| Applies to | All new and changed code under `frontend/` |
| Does not apply as product SoT | `implementation/frontend/` (legacy ADR-013 track) |
| Relationship | Implements coding discipline for FE-ARCH-001; does not supersede ADRs |

> **Constraint:** Architecture SoT is FE-ARCH-001 v1.2 (**BASELINE**; Implementation Authorization **AUTHORIZED WITH CONDITIONS** per PROGRAM-ADR-002 BR-008). This document may only refine **implementation standards**. If a standard would contradict FE-ARCH / Accepted ADRs, stop and raise an Open Decision or ADR — do not silently diverge.

---

## SECTION-1 — Project Structure

### 1.1 Canonical layout

```text
frontend/
  Dockerfile
  package.json
  next.config.ts
  messages/                 # Operator copy (id.json, en.json)
  public/                   # Static assets served as-is
  docs/                     # FE delivery notes (sprint, i18n, local)
  src/
    app/                    # Next.js App Router — routes only
    auth/                   # Identity / session consumption (not AuthN ownership)
    features/               # ECMP business feature modules
    lib/
      api/                  # HTTP client + resource API modules + DTO types
    i18n/                   # Locale resolution helpers
    shared/
      ui/                   # Shared Design System primitives
      layouts/              # Module shell layouts
      theme/                # Design tokens
      providers/            # Cross-cutting providers
      hooks/                # Shared hooks (non-domain)
      utils/                # Shared pure helpers
      icons/                # Shared icons
```

### 1.2 Folder responsibilities

| Folder | Responsibility | Must not contain |
|---|---|---|
| `src/app/` | Thin route entries; compose feature views; route-level loading/error boundaries | Business rules, heavy data logic, duplicated UI primitives |
| `src/features/<domain>/` | Domain UI (views, feature components, feature-local helpers/forms) | Shared design-system forks; direct Axios setup; hardcoded infra URLs |
| `src/shared/ui/` | Reusable presentational primitives (Button, Modal, Table patterns, …) | Domain complaint logic; API calls |
| `src/shared/layouts/` | Module-local shells (sidebar/header for ECMP capabilities) | Enterprise Platform chrome ownership; IdP UI |
| `src/shared/theme/` | Tokens mirroring CSS variables | One-off magic colors/spacing for a single screen |
| `src/shared/providers/` | App-wide providers (toast, loading, locale wiring) | Feature-specific state |
| `src/shared/hooks/` | Cross-feature hooks | Feature-only hooks (those stay under `features/`) |
| `src/shared/utils/` | Pure helpers (`cn`, formatters shared across modules) | Side-effectful API calls |
| `src/shared/icons/` | Shared icon assets/components | Feature-only illustrations unless promoted |
| `src/lib/api/` | Single HTTP client, resource wrappers, shared API types/`ApiError` | React components; feature UI |
| `src/auth/` | Session/identity consumption, permission helpers for UX | Platform IdP ownership; Role-Permission SoT admin |
| `src/i18n/` + `messages/` | Locale config and message catalogs | Hardcoded operator strings in components when a key exists |
| `public/` | Favicon and truly static public files | Secrets; environment-specific host configs |
| `docs/` | Local FE documentation | Competing architecture SoT (architecture lives in `docs/frontend/`) |

### 1.3 Feature organization

Each feature module under `src/features/<domain>/` SHOULD group:

| Artifact | Typical name | Notes |
|---|---|---|
| View / screen composition | `*View.tsx` | Smart container for a route |
| Feature components | descriptive PascalCase | Prefer presentational when reusable |
| Feature-local form/filter helpers | `*Form.ts`, `*Filters.ts` | UX helpers only; server remains SoT |
| Feature barrel | `index.ts` | Export public feature surface only |

Suggested domains (non-exhaustive; expand with FRD/catalog only): `complaints`, `queue`, `assignments`, `resolutions`, `attachments`, `dashboard`, `settings`, `sla`, `kpi`, `reports`.

### 1.4 Dependency direction (mandatory)

```text
app → features → shared / lib / auth
features ↛ app
shared ↛ features
lib/api ↛ features / app
```

Violations require Architecture review (or short ADR) before merge (FE-ARCH AEN-01).

### 1.5 Assets

| Asset type | Location | Rule |
|---|---|---|
| Design tokens | `shared/theme` + CSS variables | Prefer tokens over hardcoded visual values |
| Icons | `shared/icons` | Reuse; do not paste ad-hoc SVGs per screen without cause |
| Static public files | `public/` | No secrets; no environment hostnames as “architecture” |
| Message catalogs | `messages/` | `id` default, `en` secondary |

---

## SECTION-2 — Naming Convention

| Kind | Convention | Examples |
|---|---|---|
| Folders | `kebab-case` or short lowercase domain names | `app-layout`, `complaints`, `page-fallback` |
| Files (components) | `PascalCase.tsx` | `ComplaintListView.tsx`, `ErrorState.tsx` |
| Files (non-component TS) | `camelCase.ts` or descriptive camelCase | `createComplaintForm.ts`, `client.ts` |
| Route segments | Next.js file conventions | `page.tsx`, `layout.tsx`, `error.tsx` |
| Components | `PascalCase` | `AssignmentRowActions` |
| Hooks | `use` + `PascalCase` | `useSidebar`, `useMediaQuery` |
| Contexts / Providers | `PascalCase` + `Provider` / `Context` | `AuthProvider`, `ToastProvider` |
| API modules | lowercase resource name | `complaints.ts`, `auth.ts` |
| API functions | verb + noun, camelCase | `listComplaints`, `getComplaint` |
| Interfaces / types | `PascalCase`; prefer `type` or `interface` consistently per file | `ComplaintDto`, `ApiErrorBody` |
| Enums | `PascalCase` enum; `SCREAMING_SNAKE` or domain-aligned members | Prefer backend/catalog enums; do not invent status enums |
| Constants | `SCREAMING_SNAKE` for true constants; `camelCase` for config objects | `PASSWORD_CHANGE_ROUTE` |
| CSS / tokens | Prefer `ecmp-` Tailwind/token prefix where established | `bg-ecmp-primary` |

### 2.1 Naming rules

1. Names describe **role**, not temporary ticket IDs.
2. Do not prefix shared UI with `ECMP` unless disambiguation is required.
3. Do not name Mode A auth screens as if they were Mode B product architecture.
4. Permission checks: name helpers after capability (`canAssignComplaint`), not raw role labels alone.

---

## SECTION-3 — Component Standards

### 3.1 Smart vs presentational

| Kind | Owns | Lives in |
|---|---|---|
| **Smart (container)** | Data fetch via `lib/api`, feature state, permission UX gates, wiring | `features/*`, thin `app/*` pages |
| **Presentational** | Rendering from props; minimal/no API calls | `shared/ui/*`, feature subcomponents |

Rules:

1. `app/**/page.tsx` stays thin: import a feature view; avoid large inline business UI.
2. Presentational components must not invent backend endpoints.
3. Prefer composition (`children`, slots via props) over deep inheritance.

### 3.2 Props & children

- Prefer explicit props over opaque `any`.
- Use `children` for layout composition; document required structure briefly when non-obvious.
- Boolean props should be affirmative (`disabled`, `isLoading`).
- Do not pass secrets or raw tokens into presentational props for display.

### 3.3 Memoization guideline

- Default: write clear components; **do not** add `useMemo` / `useCallback` / `React.memo` by habit.
- Add memoization only when measuring or when a child is demonstrably expensive **and** referential stability matters.
- Prefer fixing unnecessary state/prop churn before memoizing.

### 3.4 Accessibility (component-level)

- Interactive elements must be keyboard reachable.
- Icon-only buttons need accessible names (`aria-label` or visually associated text).
- Do not use color as the sole status signal.
- Modals/dialogs: focus management and Esc dismiss where pattern applies.
- Follow Shared Design System baselines in FE-ARCH §10.

### 3.5 Reusability

- If a primitive is used by two+ features, promote to `shared/ui` (or shared hook/util).
- Domain-specific complaint cards stay in `features/complaints` unless truly generic.
- Do not fork Button/Input/Modal per feature.

---

## SECTION-4 — State Management Standards

**Do not introduce new state libraries** in this standards phase. Optional platform libraries remain OD-FE-006.

| State class | Principle | Guidance |
|---|---|---|
| **Local state** | UI-only concerns | `useState` / local refs for toggles, ephemeral UI |
| **Shared module state** | Cross-route session/identity/locale/toasts | Existing providers (`auth`, toast, loading, i18n). Do not add global Redux/Zustand by default |
| **Server state** | Backend is SoT after successful mutations | Fetch via `lib/api`; prefer pessimistic UI for assign/status/close/escalate; re-fetch or replace entity after conflicts |
| **Form state** | Controlled inputs; client checks are UX only | Map server `VALIDATION_ERROR.details` to fields; preserve input on 400 |

### 4.1 Rules

1. Do not cache “canAct” permission decisions across sessions without refresh.
2. Do not duplicate Role-Permission SoT in client stores (ADR-008).
3. URL state (`searchParams` / path params) for shareable filters/ids when appropriate.
4. Derived UI state should be computed, not mirrored into redundant stores.

---

## SECTION-5 — API Standards

### 5.1 Client usage

- All HTTP goes through the shared client in `src/lib/api` (Axios instance + interceptors as shipped).
- Feature code calls **resource modules** (`lib/api/<resource>.ts`), not ad-hoc `fetch`/`axios.create` per feature.
- Paths and fields must mirror OpenAPI catalog (`07 API Catalog/openapi/`). **No invented endpoints.**

### 5.2 Request flow (mandatory)

```text
Browser → ECMP Frontend → ECMP Backend → Enterprise Services (when required, server-side only)
```

Frontend **MUST NOT**:

- call Enterprise Services directly
- access databases
- bypass ECMP Backend

### 5.3 Response handling

- Success: map to typed DTOs aligned with catalog.
- Errors: normalize to `ApiError` with `status`, `code`, `message`, `details`.
- Prefer message-catalog keys for known `code` values; fall back to sanitized `message`.

### 5.4 Error handling (transport)

| Case | Standard |
|---|---|
| 401 | Mode-appropriate session recovery (Mode A local vs Mode B platform). Not a “permission denied” page |
| 403 | UX denial; keep context when action-scoped |
| 404 | Entity/page not found treatment |
| 400 | Field errors from `details` |
| 409 | Inline conflict + resync entity |
| 5xx / network | Toast and/or inline retry; **no silent infinite auto-retry** |

### 5.5 Retry policy

- **Default:** no automatic infinite retries.
- Safe idempotent GETs may use a **single** bounded retry only if explicitly justified in code comments / review.
- Mutations (POST/PATCH/PUT/DELETE): **no automatic retry** unless backend contract and idempotency are proven.
- User-initiated retry controls are preferred.

### 5.6 Timeout policy

- Use the shared client timeout configuration.
- Do not set per-call infinite timeouts.
- If a longer timeout is required for a specific operation (e.g. large upload), document why at the call site and keep it bounded.
- Exact numeric defaults may evolve via delivery config; do not hardcode environment hostnames to “fix” timeouts.

---

## SECTION-6 — Error Handling

Align with FE-ARCH error placement matrix.

| Error class | User treatment | Implementation rule |
|---|---|---|
| **User / business errors** | Clear, actionable copy near the action or page | Prefer catalog keys; no stack traces |
| **Validation errors** | Field-level messages; preserve input | Map `details`; client-side checks are accelerators only |
| **Permission errors (403)** | Hide clearly inapplicable actions; explain denial without losing context | UX gate ≠ security boundary |
| **Network errors** | Retry affordance; avoid blaming the user | Distinguish offline/timeout when detectable |
| **Unexpected errors** | Route/error boundary safe fallback | Log without tokens/PII; never render raw exception strings in production |

### 6.1 Rules

1. Expected AuthZ denials are UX, not incidents.
2. Correlate with backend request id when exposed.
3. Do not log tokens, passwords, or unnecessary PII to the browser console in production builds.

---

## SECTION-7 — Security Standards

| Topic | Standard |
|---|---|
| **Token handling** | Prefer in-memory access credentials where used; follow Security Standards for cookies/session. Do not put bearer tokens in `localStorage` without Security Architect approval. Never log tokens |
| **Secrets** | No secrets in source, committed `.env`, or image layers. Deployment supplies secrets/config |
| **XSS prevention** | Prefer React text rendering; avoid `dangerouslySetInnerHTML` unless sanitized and justified. Treat API strings as untrusted for HTML interpretation |
| **CSRF awareness** | Cookie-based session flows must respect backend CSRF/SameSite guidance; do not disable protections locally as a “permanent” pattern |
| **Input validation** | Client validation is UX only; server/OpenAPI remain authoritative |
| **AuthZ** | Hide/disable via permissions for UX; **never** rely on FE as the security boundary (Core Platform / backend enforces) |
| **Mode B** | Do not ship Login/Register/Forgot/Change Password as production AuthN ownership. Mode A may exist for local development only |
| **Role-Permission SoT** | Do not build competing SoT admin UI (ADR-008) |
| **Logging restrictions** | No tokens, passwords, recovery codes, or full identity payloads in client logs |

---

## SECTION-8 — Environment Standards

### 8.1 Configuration usage

- Infrastructure values **must** come from deployment-supplied configuration (FE-ARCH LAP-06).
- Read config through the project’s established env/config access patterns.
- As-built names (e.g. `NEXT_PUBLIC_API_BASE_URL`) are illustrative; do not treat hostnames inside them as architecture SoT.

### 8.2 Forbidden hardcoded values

Do **not** hardcode in source:

- API base URLs / absolute backend hosts
- Identity Provider endpoints
- Authentication endpoints as topology assumptions
- Environment URLs / deployment hostnames
- Secrets and private keys

### 8.3 Environment variable rules

| Rule | Detail |
|---|---|
| Commit | Commit `.env.example` (or equivalent) with placeholders only — never real secrets |
| Naming | Prefer clear, documented names; document new vars in FE `docs/` or README |
| Mode switches | Mode A convenience flags must never be required for Mode B production |
| Topology | No assumptions about subdomain/subpath/gateway products (LAP-04) |

---

## SECTION-9 — Performance Standards

| Topic | Standard |
|---|---|
| **Rendering** | Keep `app` pages thin; avoid unnecessary re-renders from unstable props; prefer server SoT over duplicate client caches |
| **Lazy loading** | Lazy-load heavy feature routes/components when it measurably helps initial interaction for operator workflows |
| **Code splitting** | Prefer route-level splitting via App Router structure; avoid monolithic feature barrels that eagerly pull unrelated domains |
| **Bundle awareness** | Do not add large dependencies without Architecture/Tech Lead review; prefer Shared Design System over new UI kits |
| **Images** | Optimize images (appropriate format/size); avoid huge assets in critical path; use Next image guidance where applicable |
| **API chattiness** | Do not issue N+1 browser calls to invent aggregation; use documented backend APIs |

Performance objectives remain those in FE-ARCH Non-Functional Architecture — this section defines coding discipline only.

---

## SECTION-10 — Accessibility Standards

**Baseline (mandatory for product UI work):**

1. Semantic HTML for structure and controls.
2. Visible focus styles (`focus-visible` patterns from design system).
3. Keyboard operability for primary operator flows (navigate, open dialogs, submit, dismiss).
4. Accessible names for controls.
5. Status/priority not by color alone.
6. Dialogs: focus trap / restore patterns consistent with shared Modal.
7. Touch targets reasonable for tablet use where actions appear.
8. i18n: do not embed locale-specific grammar into non-translatable strings when a catalog key is required.

**Formal WCAG level / audit cadence:** **WCAG 2.2 Level AA** adopted as **working target** (FE-CI-POL-001 v1.0 / OD-FE-009). Do **not** claim “WCAG AA conformant” in releases without UX audit evidence (FE-CI-POL-CS-001 C-3). FE-STD §10 baseline remains mandatory. CI a11y smoke is warn-mode.

---

## SECTION-11 — Testing Standards

**Do not choose new test frameworks in this document.** Use the project’s currently approved toolchain when present; framework selection/expansion remains a delivery decision (related OD-FE-003 / OD-FE-004).

| Layer | Expectation |
|---|---|
| **Unit** | Pure helpers (filters, form mappers, permission UX helpers, status transition display helpers) have focused tests when logic is non-trivial |
| **Component** | Shared UI primitives critical to a11y/behavior (Modal, ErrorState, permission-sensitive controls) should have component tests when changing behavior |
| **Integration** | Feature flows that call `lib/api` should cover success + representative error mapping (403/400/409) with mocked HTTP — not against production |
| **E2E / happy path** | Core complaint operator paths are candidates for automated gates as OD-FE-003 Phase C — see FE-CI-POL-001; not mandatory tooling choice in this standards doc |

### 11.2 Quantitative gates (**Accepted** — FE-CI-POL-001 v1.0)

Numeric fail/warn thresholds: see `docs/frontend/FRONTEND_CI_QUALITY_POLICY_v1.0.md` (OD-FE-010). Phase B warn for audit/a11y; **Phase C coverage hard-fail is live** in Root Frontend CI.

### 11.1 Testing rules

1. Tests must not require real secrets or production IdP.
2. Do not assert against hardcoded environment hostnames.
3. Prefer testing behavior over implementation details.
4. Flaky network-dependent tests are not acceptable gates.

---

## SECTION-12 — Documentation Standards

| Artifact | Requirement |
|---|---|
| **Code comments** | Explain non-obvious intent, security constraints, Mode A vs Mode B boundaries — not narrate obvious code |
| **Feature / shared README** | Update when folder responsibility or public exports change materially (`shared/README.md`, feature docs as needed) |
| **ADR / DEC references** | Cite enterprise IDs in PRs and significant design notes (`ADR-008`, `DEC-019`, `FE-ARCH-001`, …) |
| **API documentation** | OpenAPI catalog is SoT; FE wrappers must not become a second undocumented contract. If UI needs a new field/endpoint, update catalog/FRD first |
| **Architecture docs** | Do not fork FE-ARCH inside `frontend/docs/`; link to `docs/frontend/` |
| **i18n docs** | Follow `frontend/docs/I18N.md` for locale rules |

---

## SECTION-13 — Code Review Checklist

Reviewers SHOULD verify:

### Architecture & ownership

- [ ] Change targets `frontend/` (not legacy `implementation/frontend/` as product SoT)
- [ ] Dependency direction respected (`app → features → shared/lib/auth`)
- [ ] No Mode B AuthN ownership UI introduced (Login/Register/Forgot/Change Password as production architecture)
- [ ] No competing Role-Permission SoT UI (ADR-008)
- [ ] No direct Enterprise Service / DB access from browser

### API & contracts

- [ ] Endpoints/fields exist in OpenAPI catalog (or catalog updated in same change)
- [ ] Uses shared `lib/api` client/modules
- [ ] Errors mapped to `ApiError` / placement matrix
- [ ] No invented status transitions / business rules

### Security & config

- [ ] No hardcoded API/IdP/host secrets
- [ ] Tokens/secrets not logged or committed
- [ ] XSS-safe rendering; no unjustified raw HTML
- [ ] Permission UX is non-authoritative

### UX / a11y / i18n

- [ ] Uses Shared Design System where applicable
- [ ] Keyboard/focus/name basics covered for new interactive UI
- [ ] Operator strings via message catalogs when required
- [ ] Loading / empty / error states handled

### Quality

- [ ] Types are sound; no needless `any`
- [ ] Memoization not cargo-culted
- [ ] Tests added/updated when logic warrants
- [ ] Docs/ADR references updated when contracts or ownership touch points change

---

## SECTION-14 — Definition of Done

A frontend task is **Done** only when all applicable items hold:

1. **Scope:** Implements an approved FR/UX/sprint item; no out-of-scope Blueprint inventions.
2. **Tree:** Lands in canonical `frontend/` unless explicitly legacy-track work.
3. **Architecture compliance:** Satisfies SECTION-15 checklist for the change.
4. **Contracts:** Any API usage matches OpenAPI; catalog/traceability updated if contracts changed.
5. **Standards:** Naming, structure, API, error, security, and env rules in this document followed.
6. **UX states:** Loading, empty, validation, 403/404/5xx treated per standards.
7. **i18n:** Operator-facing copy in catalogs for `id`/`en` as required.
8. **Quality gates:** Existing Root Frontend CI green for the change (`typecheck` + production build at minimum).
9. **Review:** Code review checklist completed; Security consulted when auth/token/session behavior changes.
10. **Docs:** Comments/README/ADR references updated when ownership, public APIs, or env vars change.
11. **No secrets:** No credentials in git or images.
12. **Mode honesty:** Mode A-only surfaces not documented or shipped as Mode B requirements.

---

## SECTION-15 — Architecture Compliance

Implementation **MUST** remain compliant with FE-ARCH-001 v1.2 as follows.

| FE-ARCH control | Implementation obligation |
|---|---|
| LAP-01..03 (Locked — ADR-014/015 Accepted with Conditions) | Design Mode B as Enterprise Business Module consuming platform identity; do **not** claim Mode B runtime unlocked (C-7 CLOSED) |
| LAP-04 | No topology assumptions (host/domain/subpath/proxy/gateway products) in code architecture |
| LAP-05 / ADR-008 | No competing Role-Permission SoT; UX permission checks only |
| LAP-06 | Deployment-supplied configuration; no hardcoded infra endpoints |
| LAP-07 | `Browser → FE → ECMP BE` only |
| Mode A / Mode B | Mode A allowed for local dev only; production must not depend on Mode A auth mechanisms |
| Shared Design System | Reuse `shared/*`; do not fork visual language without cause |
| Module Integration Boundary | Do not select Module Federation / iframe / Web Component / reverse proxy as “the” standard here |
| AEN-01..07 | Treat as mandatory engineering rules; CI automation tracked under OD-FE-003 |
| DEC-019 | Product work targets `frontend/` |
| ADR-003 | Configuration-first for business-configurable values; do not hardcode workflow states inventively |

### 15.1 Stop-the-line

Stop and escalate (Open Decision / ADR / Architecture Board) if a task would:

- redesign FE-ARCH ownership boundaries
- invent backend APIs or events
- move Role-Permission SoT
- mandate a new global state library
- mandate mount/topology technology
- flip ADR-014/015 lifecycle without Board action
- claim Mode B / Batch-2 / enterprise customer unlocked without Board unlock beyond PROGRAM-BOARD-004 C-7

---

## Traceability

| Artifact | Role |
|---|---|
| FE-ARCH-001 v1.2 | Architecture SoT |
| DEC-019 | Canonical `frontend/` tree |
| ADR-008 | Role-Permission SoT |
| ADR-003 | Configuration-first |
| ADR-014 / ADR-015 | Enterprise Mode / identity — **Accepted with Conditions** (PROGRAM-BOARD-004 BR-009 / BR-010); Mode B runtime **CLOSED** (C-7); OD-FE-008 CLOSED |
| FE-CI-POL-001 v1.0 | Root Frontend CI / a11y working target / coverage — **Accepted with Conditions** (FE-CI-POL-CS-001); OD-FE-003/009/010 CLOSED |
| OD-FE-001..002, 004..007 | Remaining open architecture/delivery decisions |
| `07 API Catalog/openapi/` | API contract SoT |
| `10 Security and Access Standards/` | Security baseline |
| `21 Technical Standards/` | Platform technical standards hub (FE activation via OD-FE-004) |

---

## New Open Decisions raised by this standards phase

| ID | Topic | Owner | Reason | Expected resolution phase |
|---|---|---|---|---|
| OD-FE-009 | Formal accessibility conformance target | UX Lead, Frontend Lead | **CLOSED** — WCAG 2.2 AA working target (FE-CI-POL-CS-001); no conformance claim without audit | — |
| OD-FE-010 | Quantitative test coverage / gate thresholds | Frontend Lead, Tech Lead | **CLOSED** — Phase B warn / Phase C planned numbers Accepted | Phase C fail activation PR |

Existing OD-FE-001..008 remain in force; this document does not close them.

---

## Document history

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | PROGRAM-FRONTEND-002 PHASE-0 — initial Frontend Development Standards |
| 1.0 | 2026-07-30 | PROGRAM-ADR-002 PHASE-0 Board Resolution: Lifecycle → BASELINE (BR-004) |
| 1.0 | 2026-07-30 | PROGRAM-BOARD-004 F-3 sync: ADR-014/015 Accepted with Conditions cited; LAP-01..03 Pending Upstream retired; Mode B remains CLOSED; OD-FE-008 CLOSED |
| 1.0 | 2026-07-30 | FE-CI-POL-001 v0.1 proposed — OD-FE-003/009/010 draft pointers |
| 1.0 | 2026-07-30 | FE-CI-POL-001 v1.0 Accepted with Conditions (FE-CI-POL-CS-001); OD-FE-003/009/010 CLOSED |

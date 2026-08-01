# Frontend CI Quality Policy (Root `frontend/`)

| Field | Value |
|---|---|
| ID | FE-CI-POL-001 |
| Version | 1.0 |
| Program | PROGRAM-FRONTEND-002 delivery quality (Mode A) |
| Owner | Frontend Lead / Tech Lead |
| Reviewer | UX Lead (a11y target), Architecture Board (AEN alignment) |
| Status | 🟢 **Accepted with Conditions** — see `FRONTEND_CI_QUALITY_POLICY_COUNTERSIGN_v1.0.md` (FE-CI-POL-CS-001) |
| Last Review | 2026-07-30 |
| Related | OD-FE-003 (**CLOSED**), OD-FE-009 (**CLOSED** as working target), OD-FE-010 (**CLOSED**); FE-ARCH-001 §16 AEN-01..07; FE-STD-001 §10–§11; `root-frontend-ci.yml` |
| Non-goals | Mode B AuthN; OpenAPI enterprise `securitySchemes`; Batch-2 unlock; superseding ADR-013; WCAG marketing conformance claim without UX audit |

## Purpose

Define Root Frontend CI quality gates, accessibility **working target**, and coverage thresholds for the canonical product tree `frontend/` (DEC-019).

Legacy `implementation/frontend/` remains on `frontend-ci.yml` and is **not** the product SoT.

## Current as-built (evidence)

| Surface | Today |
|---|---|
| `root-frontend-ci.yml` | install → audit(warn) → typecheck → lint → **auth-route inventory + enterprise-guard self-test + auth-route unit (K-3 hard)** → test:coverage(hard) → test:a11y(warn) → build |
| `frontend/package.json` | Scripts: `dev`, `build`, `start`, `typecheck`, `lint`, `check:auth-routes`, `check:auth-routes:enterprise-guard`, `check:auth-routes:unit`, `test`, `test:coverage`, `test:a11y` |
| Runner | Vitest (unit/coverage) + axe-core (a11y smoke, separate config) + Node test for credential-route guard |

### Implementation progress

| Item | Status |
|---|---|
| Phase A typecheck + build | **Live** (hard) |
| Phase B lint hard-fail | **Live** |
| Phase B npm audit high+ | **Live (warn)** |
| Phase B unit/coverage | **Live (warn)** — scoped helper thresholds |
| Phase B a11y smoke | **Live (warn)** |
| Countersign | **Recorded** — FE-CI-POL-CS-001 (2026-07-30) |
| Phase C coverage hard-fail | **Live** — thresholds lines/statements ≥40%, functions ≥30%, branches ≥25%; CI hard-fail (C-2 activated 2026-07-30); helper scope includes `cmBatch1Attachments.ts` (FR-004 Mode A, 2026-07-31) |
| Phase C e2e / bundle | **Planned** |
| AEN-03 / audit K-3 credential-route guard | **Live** — `check:auth-routes` (standalone inventory) + `check:auth-routes:enterprise-guard` (proves enterprise hard-fail while Mode A routes remain) + `check:auth-routes:unit`. Mode B unlock still **CLOSED** (C-7 / C-B6-1). |

---

## OD-FE-003 — Platform CI Quality Gates (**Accepted**)

### Decision

Adopt a **three-phase** Root Frontend CI plan. Gates map to FE-ARCH AEN-01..07 as **engineering obligations**.

| Phase | Hard-fail (blocks PR) | Warn / continue-on-error | Notes |
|---|---|---|---|
| **A — Floor** | `typecheck`, `build` | — | Live |
| **B — Hygiene** | Phase A + `lint` (max-warnings 0) | `npm audit --audit-level=high`; unit/coverage; a11y smoke | Live |
| **C — Quality bar** | Phase B + unit/coverage **fail** thresholds (OD-FE-010 Phase C) | Playwright/e2e happy-paths; bundle budget; a11y remains warn | Coverage hard-fail **live**; e2e planned |

### AEN → gate mapping

| AEN | Phase A | Phase B | Phase C |
|---|---|---|---|
| AEN-01 dependency direction | Review checklist | Lint/import rule when available | Same |
| AEN-02 forbidden imports | Review checklist | Lint boundary rule when available | Same |
| AEN-03 Mode B vs Mode A auth | Review checklist | **Credential-route guard live** (standalone inventory + enterprise self-test hard); Mode B still **CLOSED** | Enterprise production builds must set `ECMP_FRONTEND_DEPLOY_MODE=enterprise` (hard-fail if Mode A login routes remain) |
| AEN-04 hardcoded infra endpoints | Review checklist | Warn grep/lint | Hard fail |
| AEN-05 API allowlist | Review checklist | Contract/wrapper review | Automated check when ready |
| AEN-06 secrets | Existing secret scanning / review | Same | Same |
| AEN-07 OpenAPI drift | Process / review | Same | Contract check when ready |

### Explicit non-actions

- Do not require Playwright/Cypress in Phase A/B.
- Do not treat this policy as Mode B AuthN authorization.
- Do not unlock Batch-2.

---

## OD-FE-010 — Quantitative coverage / gate thresholds (**Accepted**)

| Phase | Gate mode | Thresholds (product `frontend/`) | Scope |
|---|---|---|---|
| **A** | N/A | — | — |
| **B** | **Warn** (`continue-on-error: true`) | lines ≥ **20%**, statements ≥ **20%**, functions ≥ **15%**, branches ≥ **10%** | Pure helpers under features (+ `cn`, `nav`); expand to `src/lib/**` + `src/shared/**` as suite grows |
| **C** | **Fail** (**live** in CI) | lines ≥ **40%**, statements ≥ **40%**, functions ≥ **30%**, branches ≥ **25%** | Helper scope expanded (fileTypes, quickActionConfig, passwordPolicy, …); grow toward `src/lib/**` + `src/shared/**` over time |

**Tooling (Accepted delivery choice):** Vitest + `@vitest/coverage-v8`. Do not add a second unit-test framework.

---

## OD-FE-009 — Accessibility working target (**Accepted as working target**)

| Item | Decision |
|---|---|
| Target | **WCAG 2.2 Level AA** for primary operator flows (Option A) |
| Conformance claim | **Forbidden** until UX audit evidence (countersign condition C-3) |
| CI | a11y smoke (axe) **Warn** in Phase B; evaluate Hard for shared components in Phase C |
| Audit cadence | Manual keyboard/focus pass before each production release and after material UX redesign |
| Out of scope | Enterprise Platform chrome; Mode B IdP pages (Mode B **CLOSED**) |

FE-STD §10 baseline remains mandatory regardless of WCAG level.

---

## Conditions (from FE-CI-POL-CS-001)

1. **C-1** — Mode B / Batch-2 / enterprise customer remain **CLOSED**.
2. **C-2** — Phase B audit/a11y remain warn; **coverage Phase C hard-fail activated** 2026-07-30.
3. **C-3** — No WCAG AA conformance claim without UX audit evidence.
4. **C-4** — Named role holders may supersede this delivery Accept with a later note.

## Document history

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-30 | Proposed draft (OD-FE-003 / 009 / 010) |
| 0.1a–0.1c | 2026-07-30 | Phase B implementation progress notes |
| 1.0 | 2026-07-30 | **Accepted with Conditions** via FE-CI-POL-CS-001 (Project Owner chat instruction) |
| 1.0a | 2026-07-30 | Phase C coverage hard-fail activated in `root-frontend-ci.yml`; expanded helper tests (fileTypes, quickActionConfig, passwordPolicy) |

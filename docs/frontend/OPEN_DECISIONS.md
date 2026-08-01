# Frontend Architecture — Open Decisions

| Field | Value |
|---|---|
| ID | FE-OD-001 |
| Program | PROGRAM-FRONTEND-001 / PROGRAM-FRONTEND-002 |
| Phase | PHASE-0B + FE-STD PHASE-0 |
| Version | 1.6 |
| Owner | Solution Architect |
| Reviewer | Architecture Board |
| Status | 🟡 Open (post FE-CI-POL-001 Accept; OD-FE-003/008/009/010 closed) |
| Last Review | 2026-07-30 |
| Parent | `FRONTEND_ARCHITECTURE_v1.2.md` (FE-ARCH-001 **BASELINE**); standards: `FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md` (FE-STD-001 **BASELINE**); CI policy: `FRONTEND_CI_QUALITY_POLICY_v1.0.md` (**Accepted with Conditions**) |

Keep **only** decisions that are truly unresolved. LAP-01..03 are **Locked** (ADR-014/015 **Accepted with Conditions** — PROGRAM-BOARD-004); LAP-04..07 remain Locked. Mode B / Batch-2 / enterprise customer remain **CLOSED** (C-7). OD-FE-003/008/009/010 closed. Role/Permission SoT correction is **resolved** in FE-ARCH §2.2.

---

## Disposition summary (PHASE-0B TASK-9)

| ID | Disposition | Owner | Expected resolution phase |
|---|---|---|---|
| OD-FE-001 | **Move to ADR** (keep OPEN until ADR filed/accepted) | Architecture Board, CTO, Frontend Lead | Architecture / stack ADR before claiming frozen FE standard |
| OD-FE-002 | **Keep OPEN** | Security Architect, Frontend Lead, Platform | Security / identity protocol workstream (Mode B runtime still CLOSED per C-7; gated on protocol ADR + Board unlock) |
| OD-FE-003 | **CLOSED** | Frontend Lead, Tech Lead | FE-CI-POL-001 v1.0; Phase C coverage hard-fail **live** |
| OD-FE-004 | **Keep OPEN** | Tech Lead | After OD-FE-001 ADR; Technical Standards activation |
| OD-FE-005 | **Keep OPEN** | UX Lead, ECMF/Complaint PO | UX specification consolidation (parallel; before broad UI build-out) |
| OD-FE-006 | **Keep OPEN** | Frontend Lead | When multi-feature cache pain appears, or confirm “no platform library” |
| OD-FE-007 | **Move to ADR** (keep OPEN until Infra ADR) | Infrastructure Architecture, Platform Architecture, Solution Architect | Infrastructure Architecture / module deployment ADR |
| OD-FE-008 | **CLOSED** | Architecture Board | Upstream ADR acceptance done — ADR-014 v1.4 / ADR-015 v1.3 **Accepted with Conditions** (PROGRAM-BOARD-004 BR-009 / BR-010); Mode B remains **CLOSED** (C-7) |
| OD-FE-009 | **CLOSED** (working target) | UX Lead, Frontend Lead | WCAG 2.2 AA working target Accepted; **no** conformance claim without UX audit (C-3) |
| OD-FE-010 | **CLOSED** | Frontend Lead, Tech Lead | Phase B/C thresholds Accepted; Phase C coverage hard-fail **live** |

Nothing removed as spurious. OD-FE-008 closed only after recorded PROGRAM-BOARD-004 Accept With Conditions (not invented from FE docs). Mode B remains CLOSED.

---

## OD-FE-001 — Technology migration alignment

| Field | Value |
|---|---|
| Priority | High |
| Status | OPEN |
| Disposition | **Move to ADR** |
| Owners | Architecture Board, CTO, Frontend Lead |
| Reason | Accepted ADR-013 (Vite stack) conflicts with DEC-019 production tree (`frontend/` Next.js). FE-ARCH cannot silently supersede an Accepted ADR. PROGRAM-ADR-002 BR-007: ADR-013 remains active; future change requires a separate ADR. |
| Expected resolution phase | Separate ADR required before frozen platform FE standard (PROGRAM-ADR-002 BR-007: ADR-013 remains active; do **not** supersede via FE docs) |
| Blocking? | Blocks declaring a single “frontend stack standard” in `21 Technical Standards` |

### Problem

- **ADR-013** (Accepted — **remain active** per BR-007): React 18 + TypeScript SPA, Vite, React Router, TanStack Query, CSS Modules → `implementation/frontend`
- **DEC-019** (Accepted): `frontend/` is **production canonical**; `implementation/frontend/` is **legacy**
- Production path ships **Next.js 15 + React 19 + Tailwind + Axios** from `frontend/`

### Options

| Option | Description |
|---|---|
| A | File a **separate** stack ADR that amends product-stack guidance while ADR-013 remains historically active / scoped (Board forbids silent supersession via FE-ARCH) |
| B | Revert product tree to Vite SPA (high cost; contradicts Go-Live Compose) |
| C | Dual-stack forever with strict domain split — not recommended |

### Recommendation

**Option A** (separate ADR; do not supersede ADR-013 from FE documentation alone).

### Exit criteria

- Architecture Board records a **separate ADR** for any product-stack change (ADR-013 remain active until that ADR decides otherwise)
- `21 Technical Standards` activated against the chosen SoT (feeds OD-FE-004)

---

## OD-FE-002 — Enterprise authentication protocol

| Field | Value |
|---|---|
| Priority | High (shared env / SIT gate) |
| Status | OPEN |
| Disposition | **Keep OPEN** |
| Owners | Security Architect, Frontend Lead, Platform |
| Reason | Mode B AuthN **ownership** is locked by Accepted ADR-014 (with Conditions); browser **protocol/bridge** is still undecided and must remain subordinate to ADR-015 claims. Mode B implementation remains **CLOSED** (C-7) until a future Board unlock + protocol ADR. |
| Expected resolution phase | Security / identity protocol workstream (ADR-016 / future Board unlock; after F-5 protocol binding); OpenAPI securitySchemes only when Mode B implementation is authorized |
| Related | ADR-012, ADR-014, ADR-015, ADR-016 (Accepted with Conditions — PROGRAM-BOARD-006 BR-011; Mode B still CLOSED C-B6-1), SEC-AUTH-001, SEC-MIG-001, PROGRAM-BOARD-004 C-7 |

### Problem

Mode B locks **ownership** (Enterprise Platform owns AuthN; ECMP consumes identity). The **protocol/bridge** for the browser module is still unresolved, for example:

- Session cookie / BFF brokered by platform or ECMP backend, **vs**
- OIDC Authorization Code + PKCE (or future corporate IdP surface)

### Constraint

- Do not invent a second permission SoT (ADR-008)
- Do not reintroduce ECMP-owned Login/Register/Forgot/Change Password as Mode B product UI
- Do not hardcode IdP endpoints in the frontend (FE-ARCH §12)
- Do not invent ADR-014/015 acceptance

### Exit criteria

- Written protocol choice in SEC-MIG / Security + Platform approval
- OpenAPI `securitySchemes` updated when implementation starts
- FE-ARCH §6 amended to mark protocol as Accepted current (ownership stays Mode B)

---

## OD-FE-003 — Platform CI Quality Gates

| Field | Value |
|---|---|
| Priority | Medium |
| Status | **CLOSED** (2026-07-30) |
| Disposition | **CLOSED** — FE-CI-POL-001 v1.0 Accepted with Conditions (FE-CI-POL-CS-001) |
| Owners | Frontend Lead, Tech Lead |
| Related | `root-frontend-ci.yml`, FE-ARCH AEN-01..07, FE-CI-POL-001 v1.0, OD-FE-009, OD-FE-010 |
| Policy | `docs/frontend/FRONTEND_CI_QUALITY_POLICY_v1.0.md` |

### Accepted decision

Three-phase Root Frontend CI plan (Phase A+B+C coverage **live**; e2e planned):

| Phase | Hard-fail | Warn |
|---|---|---|
| A | typecheck, build | — |
| B | + lint | audit, unit/coverage, a11y |
| C | + coverage fail thresholds (**live**) | e2e / bundle (planned); a11y still warn |

### Exit criteria

- [x] Fail/warn policy recorded and CI updated for Phase A+B
- [x] FE-CI-POL-001 countersigned (FE-CI-POL-CS-001)
- [x] Cited from FE-ARCH / FE-STD delivery notes

---

## OD-FE-004 — Platform Technical Standards

| Field | Value |
|---|---|
| Priority | Medium |
| Status | OPEN |
| Disposition | **Keep OPEN** |
| Owners | Tech Lead |
| Reason | TypeScript/React/Next standards remain Planned pending stack ADR clarity. |
| Expected resolution phase | After OD-FE-001 ADR acceptance; publish under `21/` |
| Related | ADR-011 checklist, `21 Technical Standards/README.md` |
| Blocked by | OD-FE-001 |

### Problem

TypeScript/React (and Next) standards remain Planned pending stack ADR clarity.

### Exit criteria

- Standards docs published under `21/`
- Referenced from `ai/08_standards.md` and FE-ARCH §3

---

## OD-FE-005 — UI Specification Consolidation

| Field | Value |
|---|---|
| Priority | Medium |
| Status | OPEN |
| Disposition | **Keep OPEN** |
| Owners | UX Lead, ECMF/Complaint PO |
| Reason | Formal screen inventory under `12 UI UX Spec/` incomplete vs product routes; needed before broad implementation. |
| Expected resolution phase | UX specification consolidation (can run parallel to infra/auth open items) |
| Related | UX-001, UX-SCR-001, `frontend/SPRINT_F*.md` |

### Problem

Product UI screens are documented mainly in sprint notes under `frontend/`; formal UX inventory under `12 UI UX Spec/` is incomplete.

### Exit criteria

- Screen specs for in-production ECMP capability routes exist under `12 UI UX Spec/` or an Architecture-approved index
- Traceability links where FR/UI apply
- Specs must not reintroduce Mode B AuthN UI ownership contradictions or Role-Permission SoT ownership contradictions

---

## OD-FE-006 — TanStack Query as Platform Standard

| Field | Value |
|---|---|
| Priority | Low |
| Status | OPEN |
| Disposition | **Keep OPEN** |
| Owners | Frontend Lead |
| Reason | No current evidence that platform-wide data-fetching library is required; premature ADR avoided. |
| Expected resolution phase | When two+ features (or a second enterprise module) show duplicated cache/invalidation pain — then short ADR |

### Problem

Legacy Vite UI mandates TanStack Query (ADR-013). Product UI uses feature hooks + Axios. A platform data-fetching standard may be needed as caching/invalidation complexity grows across modules.

### Recommendation

Keep hooks baseline until pain appears; then decide via short ADR.

### Exit criteria

- Explicit “no platform library” confirmation **or** accepted ADR with adoption guide reusable by future modules

---

## OD-FE-007 — Enterprise Module Deployment Strategy

| Field | Value |
|---|---|
| Priority | High (platform integration) |
| Status | OPEN |
| Disposition | **Move to ADR** |
| Owners | Infrastructure Architecture, Platform Architecture, Solution Architect |
| Reason | FE must remain topology-agnostic (LAP-04); mount technology and deployment topology are infra decisions, not FE-ARCH ownership. |
| Expected resolution phase | Infrastructure Architecture / module deployment ADR |
| Related | FE-ARCH §11, §11A, LAP-04 |

### Problem

ECMP must be deployable behind any Enterprise Platform entry point without frontend business-architecture refactoring. **Deployment topology and mount technology are intentionally undefined** in FE architecture.

### Explicitly deferred (do not decide in FE-ARCH)

- subdomain / subpath / hostname / domain
- gateway / ingress / reverse proxy
- Module Federation / iframe / Web Component / other concrete mounting mechanisms

### Exit criteria

- Infrastructure Architecture decision recorded as ADR (or DEC if non-architectural)
- FE config contract updated only as needed (still no hardcoded topology in source)
- FE-ARCH §11 / §11A reference the infra decision without absorbing infra ownership

---

## OD-FE-008 — Upstream Enterprise Mode ADR acceptance

| Field | Value |
|---|---|
| Priority | High (governance) |
| Status | **CLOSED** (2026-07-30) |
| Disposition | **CLOSED** — exit criteria met by PROGRAM-BOARD-004 |
| Owners | Architecture Board |
| Reason | ADR-014 v1.4 and ADR-015 v1.3 are **Accepted with Conditions** (BR-009 / BR-010). FE LAP-01..03 are **Locked** (no longer Pending Upstream). This close is **documentation sync only** (PROGRAM-BOARD-004 F-3). |
| Related | ADR-014, ADR-015, FE-ARCH LAP-01..03, PROGRAM-BOARD-004 C-7 |
| Does **not** unlock | Mode B AuthN / SSO / OpenAPI enterprise `securitySchemes` / OD-FE-002 implementation / Batch-2 / enterprise customer (C-7 remains **CLOSED**) |

### Exit criteria (met)

- [x] ADR-014 revised and Status → **Accepted with Conditions** (BR-009)
- [x] ADR-015 revised and Status → **Accepted with Conditions** (BR-010)
- [x] FE-ARCH / FE-STD / this register amended to remove “Pending Upstream” from LAP-01..03 (F-3 sync)

### Non-actions (still binding)

- Do not treat this OD close as Mode B implementation authorization
- Do not rewrite ADR-014/015 normative bodies from FE documentation
- Do not weaken ADR-008 Role-Permission SoT
- Do not start OD-FE-002 browser/protocol bridge as unlocked delivery until Board unlock + protocol ADR

---

## OD-FE-009 — Formal accessibility conformance target

| Field | Value |
|---|---|
| Priority | Medium |
| Status | **CLOSED** (2026-07-30) — working target only |
| Disposition | **CLOSED** — WCAG **2.2 Level AA** adopted as **working target** (FE-CI-POL-CS-001); conformance claim **not** granted |
| Owners | UX Lead, Frontend Lead |
| Related | FE-STD-001 §10, FE-ARCH §15.3, FE-CI-POL-001 v1.0 |
| Policy | `docs/frontend/FRONTEND_CI_QUALITY_POLICY_v1.0.md` |

### Accepted decision

| Item | Decision |
|---|---|
| Target | **WCAG 2.2 Level AA** (Option A) as working target |
| CI | a11y smoke warn (live) |
| Conformance claim | **Forbidden** until UX audit evidence (condition C-3) |

### Exit criteria

- [x] Written WCAG working target + audit cadence recorded
- [x] Referenced from FE-STD / FE-ARCH / CI policy
- [x] Explicit non-claim for release/marketing conformance

---

## OD-FE-010 — Quantitative test coverage / gate thresholds

| Field | Value |
|---|---|
| Priority | Medium |
| Status | **CLOSED** (2026-07-30) |
| Disposition | **CLOSED** — Phase B warn + Phase C coverage hard-fail **Accepted and live** (FE-CI-POL-CS-001 / C-2) |
| Owners | Frontend Lead, Tech Lead |
| Related | FE-STD-001 §11, OD-FE-003, FE-CI-POL-001 v1.0 |
| Policy | `docs/frontend/FRONTEND_CI_QUALITY_POLICY_v1.0.md` |

### Accepted thresholds

| Phase | Mode | lines / statements | functions | branches |
|---|---|---|---|---|
| B | **Warn** | ≥ 20% | ≥ 15% | ≥ 10% |
| C | **Fail** (**live**) | ≥ 40% | ≥ 30% | ≥ 25% |

### Exit criteria

- [x] Fail/warn thresholds countersigned
- [x] Documented in FE-CI-POL-001 v1.0 and Root Frontend CI
- [x] Phase B applied in CI (warn for audit/a11y); Phase C coverage hard-fail **live** (2026-07-30)

---

## Resolved by PHASE-0A / PHASE-0B (not open)

| Topic | Resolution |
|---|---|
| ECMP standalone vs enterprise module | **Module** (LAP-01 — Locked; ADR-014 Accepted with Conditions) |
| AuthN ownership | **Enterprise Platform**; ECMP consumes identity (LAP-02 — Locked; ADR-014/015 Accepted with Conditions; Mode B runtime **CLOSED**) |
| ECMP capability ownership | Complaint, Ticket, Escalation, Assignment, SLA, Resolution, KPI, Audit (complaint-domain) |
| Role / Permission SoT | **Core Platform** (ADR-008 Accepted). FE v1.1 “Enterprise Platform owns Role/Permission” **corrected** in v1.2 §2.2 |
| Complaint Roles / AuthZ mapping | **ECMP** (ADR-014/015 Accepted with Conditions); FE UX-gates only |
| Enterprise Platform ownership | Authentication, Identity directory, User (enterprise), Organization, Department, Branch, Session, Enterprise Navigation — **not** Role-Permission SoT |
| FE ↔ topology coupling | **Forbidden** (LAP-04) |
| Auth modes | **Mode A** Standalone Development + **Mode B** Enterprise Production |
| API request flow | Browser → ECMP FE → ECMP BE → Enterprise Services (when required) |
| Shared Design System | Required; reusable by future modules |
| Configuration | No hardcoded API URLs, IdP, auth endpoints, env URLs, deployment hostnames; deployment-supplied config required (mechanism TBD) |
| Module integration seam | Ownership/responsibilities/extension points documented; **no** mount technology chosen |
| Future modules | Same architecture; add modules without modifying ECMP business architecture |
| ADR-019 | **N/A** — artifact does not exist |

---

## Closed / informational

| ID | Note |
|---|---|
| DEC-019 | Canonical trees already decided — FE-ARCH treats this as binding |
| ADR-011 deferral triggers | Product UI past deferral for production tree; remaining work is standards + auth protocol (gated) + infra entry; upstream ADR-014/015 acceptance **done** (OD-FE-008 CLOSED) |
| OD-FE-008 | **CLOSED** — PROGRAM-BOARD-004 Accept With Conditions; Mode B remains CLOSED |
| OD-FE-003 / 009 / 010 | **CLOSED** — FE-CI-POL-001 v1.0; Phase C coverage hard-fail live; WCAG claim still conditional |
| Portal vs product UI | `implementation/portal` remains non-product developer portal (ADR-011 exception) |

---

## Review ask

Architecture Board (PROGRAM-ADR-002 PHASE-0): FE-ARCH-001 v1.2 and FE-STD-001 v1.0 are **BASELINE**. Implementation Authorization: **AUTHORIZED WITH CONDITIONS**.

Still required before claiming frozen platform FE standard:

1. **OD-FE-001** (separate stack ADR — ADR-013 remains active)
2. **OD-FE-002** (auth protocol — Mode B runtime still **CLOSED** per C-7)
3. **OD-FE-007** (infra deployment ADR)

**Done (governance):** OD-FE-008 CLOSED — ADR-014/015 Accepted with Conditions; LAP-01..03 no longer Pending Upstream.

**Done (Mode A quality):** OD-FE-003 / 009 / 010 CLOSED via FE-CI-POL-001 v1.0 (FE-CI-POL-CS-001). Phase C coverage hard-fail **live**; a11y/audit remain warn; WCAG conformance claims still conditional.

**Done (audit K-3 / AEN-03):** Mode A credential-route CI guard live (`check:auth-routes` + enterprise self-test). Backend `ECMP_LOCAL_CREDENTIAL_AUTH` / `ECMP_ENTERPRISE_MODE` fail-fast for staging/production + enterprise. Mode B remains **CLOSED** (C-7).

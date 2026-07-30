# ECMP Implementation Readiness Roadmap

| Field | Value |
|---|---|
| ID | IR-RM-001 |
| Version | 2.1 |
| Owner | Enterprise Technical Lead |
| Reviewer | CTO / Architecture Board / PMO |
| Approver | Engineering Manager / Business Owner |
| Status | ⚫ Historical (planning artifact — see body banner) |
| Last Review | 2026-07-21 |
| Next Review | 2026-08-04 |

## Purpose
Gate and sequence work so a funded delivery team can implement the **frozen** architecture without inventing contracts — and without burning calendar on ceremony that does not reduce delivery risk.

> **Status update (ARB, 2026-07-21):** Konflik GO vs G0 diselesaikan lewat `27 Project Decisions/DEC-002` — GO = slice + G0 floor. Deliverable G0 telah landas: Alembic rev0 (`cases`/`audit_log`/`outbox`), docker-compose Postgres, backend CI (ruff → OpenAPI validate → migrate → pytest), error envelope runtime, Role matrix minimal, write-audit transaksional. Sisa G0: sign-off manusia (Tech Lead + SA). Baseline bisnis dibekukan via `DEC-001`; BR ID via `DEC-003`; Event SoT tunggal (`events/events.yaml`).
>
> **⚠️ Dokumen ini adalah artefak perencanaan historis.** Bila isi badan dokumen bertentangan dengan `27 Project Decisions/DEC-001..005`, ADR-009..011, atau status dokumen terkini (badge di tabel metadata masing-masing dokumen), maka **DEC/ADR/status terkini yang berlaku** — bukan narasi di dokumen ini. Klaim yang sudah terlewati ditandai inline dengan tag `[superseded — see DEC-xxx]`.

---

# Part A — CTO Gate Review of Roadmap v1.0

**Verdict on v1.0: Rejected as sequencing model.**  
Useful as a gap inventory. Unsafe as an execution plan for a multi-million-dollar program.

## Challenge by sprint (v1.0)

### RS-1 — Traceability & SoT Freeze
| Lens | Finding |
|---|---|
| Hidden risks | Declaring “mapping tables” creates a **permanent dual-ID regime**. Teams will keep citing both IDs. Mapping ≠ single SoT. |
| Missing dependencies | Needs **named Decision Authority** (who can kill a BR ID scheme). Architecture Board “acknowledgment” is vague — no SLA for sign-off. |
| Wrong priority | SA editorial cleanup is hygiene, not a sprint objective. Event payload alignment matters; ADR index sync does not warrant serial blocking. |
| Doc gaps | No rule for **which ID appears in code, PR titles, and tests**. Without that, mapping docs are unread. |
| Tech debt | Paper SoT while bootstrap code remains non-compliant teaches the team that catalogs are optional. |

**CTO call:** Collapse. Pick **one** BR ID scheme for delivery (recommend keep Sprint `BR-00x` for active slice; enterprise catalog stays Draft until Accepted **[superseded — see DEC-003/DEC-004: BR ID scheme decided; enterprise catalog now 🟢 Approved v1.2]**). Deprecate the other for implementation references. Event SoT = `events/events.yaml` only — delete or generate-away the duplicate, do not “banner” it forever.

### RS-2 — Security, Integration, Data & API Freeze
| Lens | Finding |
|---|---|
| Hidden risks | **Audit on every GET** (FRD §9 / BR-ECMF-01 style) will explode storage and latency; v1 accepted it unchallenged. **Idempotency undecided** mid-freeze invites half-baked keys. Schema-as-markdown without a runnable migration is fiction. |
| Missing dependencies | Customer Master **owner + environment + auth to call stub**; legal/data-use for storing `customerId`; **caseId generation strategy**; timezone/UTC rule; PII handling for `description`; principal/claims JSON shape for Bearer token. |
| Wrong priority | Bundling Role matrix + CM + DDL + error model + audit + idempotency into one “freeze” maximizes wait time on the slowest approver. |
| Doc gaps | No OpenAPI **contract-test** requirement; no enum validation rules beyond Pydantic luck; no concurrency/ETag/version field decision (even if “none for S1”). |
| Tech debt | Annotating Data Dictionary as “conceptual” while developers still open it first guarantees schema drift. |

**CTO call:** Split decisions by **critical path**. Runnable DDL + compose beats another PDF. Challenge audit-on-read before coding it.

### RS-3 — Engineering Baseline & Coding Gate
| Lens | Finding |
|---|---|
| Hidden risks | CI job that **“may fail until IS-1”** is greenwashing. A gate that allows red CI trains failure. |
| Missing dependencies | Dev container/compose ownership; secrets pattern for local DB; CODEOWNERS / who merges contract PRs. |
| Wrong priority | A whole sprint for checklist sign-off + thin CI is **process inflation**. Should be exit criteria of G0, not a calendar sprint. |
| Doc gaps | No definition of “contract change PR” vs “code PR”; no branch protection requirements. |
| Tech debt | Separating RS-3 from RS-2 adds 1–2 weeks of idle team cost with near-zero risk reduction. |

**CTO call:** Kill RS-3 as a sprint. Merge into G0 exit criteria. CI must be green on **current** tests before Build-1 starts.

### IS-1 — Create/Get coding
| Lens | Finding |
|---|---|
| Hidden risks | First coding sprint loads **PostgreSQL + Alembic + audit + error rewrite + authz + events + optional idempotency**. That is a platform sprint disguised as a feature sprint. Failure mode: partial persistence, fake audit, events lost on crash. |
| Missing dependencies | `requirements.txt` today has **no DB drivers/ORM/Alembic**; docker-compose absent; no seed/dev user story for token issuance. |
| Wrong priority | v1 forbids useful code until after three RS sprints, then dumps all hard engineering into IS-1. Inverse of good risk burn-down. |
| Doc gaps | No migration rollback expectation; no “what happens to in-memory demo data”; no observability minimum (request id). |
| Tech debt | In-process event list without outbox in IS-1, then “outbox in IS-3”, **guarantees rewrite** of the emit path after assign/status exist. |

**CTO call:** Burn risk earlier: G0 may include **readiness engineering** (error shape, CI, compose, skeleton migration). Build-1 implements create/get on PG with **write-audit + transactional outbox table** (broker still stub). Drop or defer idempotency and audit-on-read unless Business Owner explicitly funds them.

### IS-2 — Docs-then-code in one sprint
| Lens | Finding |
|---|---|
| Hidden risks | Classic **phase compression**: Phase A slips, Phase B is coded from Slack. Notification stub inside assign sprint violates catalog-first for a second domain. |
| Missing dependencies | Workflow Config ownership (Admin vs Core) is a **governance decision**, not a side note. Status enum complete set; who may assign across units (BR-ECMF-02 TBD) — even a subset needs an explicit “same unit only” or “any CS” rule. |
| Wrong priority | Mixing Notification into assign/status delays the lifecycle vertical and creates fake “done” for Notification. |
| Doc gaps | No FRD for Notification; no API if stub is in-process only — must say so. |
| Tech debt | Hard-coded transition `if` statements labeled “config-first later” become the permanent workflow engine. |

**CTO call:** Hard gate **G1** (docs Accepted) before any assign/status code. Notification is **not** in Build-2.

### IS-3 — Hardening & Notification
| Lens | Finding |
|---|---|
| Hidden risks | Parking outbox, retention, and notification “later” is how programs ship a demo and call it MVP. Retention after audit rows exist is backwards. |
| Missing dependencies | Notification channel reality (email gateway?) even for stub; BR-NOTIF-04 retry still TBD — stub will invent numbers. |
| Wrong priority | Hardening after two feature sprints means S1–S2 already accrued the debt. |
| Doc gaps | No non-prod environment definition; “second developer can run” is not an environment strategy. |
| Tech debt | Highest: dual-write events, audit-on-read volume, stub auth forever with no expiry plan. |

**CTO call:** Pull **outbox + write-audit + request-id** left into Build-1. Notification gets its own mini-gate. Retention interim rule decided in G0 (even if “retain indefinitely until Compliance sprint”).

## Systemic failures in v1.0
1. **Ceremony over risk burn-down** — three serial readiness sprints.
2. **No readiness engineering** — false purity (“docs only”) while non-compliant code sits in repo.
3. **Dual-ID preservation** — mapping tables institutionalize ambiguity.
4. **Late durability** — events/audit designed to be rewritten.
5. **IS-2 as two sprints pretending to be one.**
6. **Silent product decisions** treated as documentation tasks (audit-on-read, workflow ownership, CM owner).
7. **No funded parallel track** for Security/Compliance beyond the slice — will ambush UAT.

---

# Part B — Improved Roadmap v2.0

## Binding rules
1. Architecture frozen (ADR-001..004 intent). No new frameworks. No broker selection required for Build-1/2 local stub.
2. **Single SoT per concern** — no permanent mapping dualism for delivery.
3. **Readiness engineering allowed** in gate sprints when it removes inventable behavior (compose, CI, error envelope, skeleton migration, outbox table).
4. **Catalog-first for new APIs/events** — OpenAPI/Event/FRD Accepted before feature code.
5. **Gates are evidence-based** (artifacts green, artifacts merged), not signature theater.
6. Existing `Sprint-01.md` / `Sprint-02.md` are **product scope references**; this roadmap controls **authorization to build**.

## Sprint model (v2)

| ID | Name | Calendar intent | Coding? |
|---|---|---|---|
| **G0** | Slice Freeze & Platform Floor | One readiness sprint (timeboxed) | Readiness engineering only |
| **B1** | Build — Case Create/Get | First product coding sprint | **Yes** |
| **G1** | Lifecycle Contract Gate | Docs/decisions only | No feature code |
| **B2** | Build — Assign/Status | Second product coding sprint | Yes |
| **G2** | Cross-cutting mini-gate | Notification + CM deepening docs | No feature code |
| **B3** | Build — Notification stub & quality bar | Third product coding sprint | Yes |

```text
G0 ──► B1 ──► G1 ──► B2 ──► G2 ──► B3
         ▲
         └── FIRST PRODUCT FEATURE CODING
```

---

## G0 — Slice Freeze & Platform Floor

### Objectives
- Resolve every decision that would force a Build-1 developer to invent behavior.
- Install the **minimum runnable platform floor** (DB, CI, contract envelope) so Build-1 is feature work, not archaeology.
- Kill dual SoT for the active slice.

### Deliverables
**A. Decisions (must be written, owned, dated)**
1. **BR SoT for delivery:** Sprint-01 IDs (`BR-001`…) are normative in FRD/traceability/code comments for the active slice. Enterprise `BR-<Domain>-NN` remains Draft catalog until separately Accepted **[superseded — see DEC-004: enterprise catalog is now 🟢 Approved v1.2]** — **no mandatory mapping sprint**. Optional one-way index later.
2. **Event SoT:** only `08 Event Catalog/events/events.yaml`. Duplicate catalog reconciled or marked non-normative / generated.
3. **Idempotency:** **Out of B1** unless BO insists in writing; remove “recommended” from FRD or move to B3+.
4. **Audit:** **Write-path audit required** (create). **Read-path audit deferred** unless BO signs cost acceptance; update FRD §9 accordingly (architecture unchanged; slice interpretation clarified).
5. **caseId strategy:** UUID (or approved format) documented.
6. **UTC timestamps** mandatory in API/DB.
7. **Principal claims shape** for Bearer (userId, permissions[]); local `dev-token` mapped to one CS principal.
8. **Workflow ownership:** record Project Decision — which domain owns Workflow Config data (Administration vs Core). Decision only; no engine build.
9. **Retention interim:** Case + Audit retained indefinitely until Compliance defines otherwise (explicit interim).
10. **OQ-001 / OQ-003:** Channel out of B1–B2; CQRS deferred — written.

**B. Contracts**
11. OpenAPI: normative `Error {code,message}`; validation error mapping table; enum constraints aligned to FRD.
12. FRD-001 patched for audit/idempotency decisions above.
13. CM Integration Stub Contract in `09` (timeout, fallback, `customerVerified`, no real CM dependency for B1).
14. Minimal Role matrix: which role has `cases:create` / `cases:read` (even if one role “CS Agent”).
15. Case + AuditLog + Outbox **physical schema** + Alembic revision **0** (runnable).
16. Data Dictionary Case section: banner “B1 attributes = FRD/OpenAPI; samples elsewhere non-normative.”

**C. Readiness engineering (allowed)**
17. `docker-compose` (or equiv) for PostgreSQL used by backend.
18. Dependencies added: DB driver, SQLAlchemy/Alembic (or chosen ADR-004-consistent libs) — **stack not redesigned**.
19. CI: install deps, migrate, `pytest` — **must be green** on current tests (fix bootstrap as needed for error envelope / health).
20. Request ID / correlation ID header convention documented and stubbed in middleware.
21. SA/ADR index **editorial** sync (ADR-004 = stack). Not a separate sprint.

### Required Documents
| Artifact | Outcome |
|---|---|
| FRD-001 | Patched decisions |
| `case-service.v1.yaml` | Error + enums; no silent fields |
| `events/events.yaml` | Sole SoT; EVT-001 stable |
| `09` CM stub | Accepted for B1 |
| `10` Role matrix v0.1 | Accepted for B1 |
| `27` Project Decisions | Workflow ownership + interim retention + OQs |
| `06` DD | Non-normative banner for conflicting Case sample |
| `21` | Local run, env vars, error convention (minimal) |
| Alembic rev 0 | Case, audit_log, outbox |
| Compose + CI | Runnable |

### Dependencies
- Business Owner: audit-on-read deferral; idempotency deferral; CM stub acceptance.
- SA: Event SoT + workflow ownership decision record.
- Eng Manager: CI required on backend PRs.
- **Named CM liaison** (even if stub-only) — if none, BO accepts perpetual stub risk in writing.

### Risks
| Risk | Mitigation |
|---|---|
| G0 becomes endless analysis | Timebox; anything not in Deliverables list → backlog, not gate |
| BO rejects audit deferral | Then fund storage/NFR note in same sprint; do not silently implement |
| Duplicate event file politics | SA owns delete/generate decision in 48h |

### Acceptance Criteria
- [ ] Developer cannot find two normative event schemas.
- [ ] `docker compose up` + migrate + pytest green in CI.
- [ ] OpenAPI Error schema matches what the running app returns for 401/404/422 (or documented 400 mapping).
- [ ] Schema rev 0 applies cleanly on empty DB.
- [ ] FRD, OpenAPI, EVT-001, Role matrix, CM stub agree on create/get behavior.
- [ ] Dual BR IDs: delivery SoT declared in writing.

### Definition of Done
- G0 checklist green; Tech Lead + SA + ECMF PO + Eng Manager sign **Build Authorization for B1**.
- No assign/status/notification feature work.

---

## B1 — Build: Case Create/Get (first product coding)

### Objectives
- Deliver the only Approved product slice (FR-001/FR-002) on the platform floor from G0.
- Prove persistence, write-audit, and **durable emit intent** (outbox rows) without selecting a broker.

### Deliverables
1. `POST /v1/cases`, `GET /v1/cases/{caseId}` per OpenAPI.
2. PostgreSQL persistence (in-memory **not** primary).
3. Write audit on create (and other writes if any); read audit only if G0 forced it.
4. On create: persist Case + Audit + **Outbox row for EVT-001** in one transaction; in-process publisher may drain outbox (at-least-once locally).
5. AuthZ per Role matrix / claims shape.
6. CM stub behavior per Integration Catalog.
7. Tests: happy path, 401/403, validation, 404, CM fallback flag, outbox row present; CI green.
8. Traceability current.

### Required Documents
Consume G0 outputs; update catalogs only via contract-first PR if defects found.

### Dependencies
- **G0 Build Authorization.**
- PostgreSQL via compose (or approved shared dev DB).

### Risks
| Risk | Mitigation |
|---|---|
| Scope creep (list, assign, UI) | PR checklist rejects |
| Treating outbox drain as “messaging done” | README: broker ADR still follow-up; no multi-service claim |
| Partial migration in shared DB | Fresh DB in CI always |

### Acceptance Criteria
- [ ] FRD §10 AC met (as patched in G0).
- [ ] Restart process: data intact.
- [ ] Kill process mid-drain: outbox row remains until published (no silent loss of intent).
- [ ] Error bodies match OpenAPI.
- [ ] No idempotency code unless G0 included it.

### Definition of Done
- Product `Sprint-01.md` DoD met under **G0 contract interpretation**.
- Build Authorization closed; known limitations list published (no SSO, no broker, stub CM, no read-audit if deferred).

---

## G1 — Lifecycle Contract Gate (assign/status)

### Objectives
- Freeze assign/status **before** any lifecycle code.
- Prevent IS-2-style phase collapse.

### Deliverables
1. Status enum + **allowed transition matrix** (subset for next build only).
2. Assignment rules for subset (e.g. any user with `cases:assign` in same org unit — **must pick one rule**; cannot leave BR-ECMF-02 TBD if assign ships).
3. FRD for assign + status (AC, errors, authz).
4. OpenAPI API-003/API-004 **merged before code**.
5. EVT-002/EVT-003 payloads finalized in Event SoT.
6. Role matrix delta (`cases:assign`, `cases:transition` or equivalent).
7. Workflow Config: storage note consistent with G0 ownership decision (config table stub OK; full admin UI out).
8. `Sprint-02.md` → Approved only when above Accepted.

### Required Documents
FRD (new/delta), OpenAPI, events.yaml, Role matrix delta, Project Decision confirmation, Sprint-02.

### Dependencies
- B1 Done.
- ECMF PO + SA for transition subset.
- Security delegate for new permissions.

### Risks
| Risk | Mitigation |
|---|---|
| “Just hardcode transitions” | Matrix is the config; code loads matrix structure even if seeded in migration |
| Cross-unit assign politics | If undecided, **do not start B2** |

### Acceptance Criteria
- [ ] Every transition in scope has from/to/role.
- [ ] OpenAPI published; no code in same PR that implements handlers (contract PR first).
- [ ] Traceability Planned → ready for B2 links.

### Definition of Done
- **Build Authorization for B2** signed. Notification explicitly excluded.

---

## B2 — Build: Assign/Status

### Objectives
- Implement lifecycle subset against G1 contracts only.

### Deliverables
1. Assign/reassign + status transition APIs.
2. Guards reject illegal transitions with normative errors.
3. Outbox events EVT-002/EVT-003.
4. Write audit on assign/status.
5. Tests for legal/illegal transitions and authz; CI green.
6. Traceability updated.

### Required Documents
G1 outputs only.

### Dependencies
- G1 Build Authorization.
- Seeded transition matrix in DB or config file loaded at runtime.

### Risks
| Risk | Mitigation |
|---|---|
| Notification “quick hook” | Reject; belongs in B3 after G2 |
| Expanding status set mid-sprint | Change = return to G1 |

### Acceptance Criteria
- [ ] Illegal transition never mutates state.
- [ ] Events/audit/outbox consistent with create path patterns from B1.
- [ ] Sprint-02 technical DoD (minus notification if it was in old draft — notification not required here).

### Definition of Done
- Assign/status in production-shaped local stack; limitations list updated.

---

## G2 — Cross-cutting Mini-Gate (Notification + CM)

### Objectives
- Catalog-first entry for Notification stub and any CM deepening — without redesigning architecture.

### Deliverables
1. Thin Notification FRD: which events consumed; success/fail logging; **retry counts explicit or “no retry in B3”**.
2. Consumer contract notes on Event SoT (consumer group name optional).
3. Decision: in-process drain vs separate worker module (still no broker ADR required).
4. CM: remain stub **or** define real validate endpoint fields if environment exists (no fantasy URLs).
5. Test inventory for consumer + authz regressions.

### Required Documents
Notification FRD thin; events.yaml consumer notes; `09` update if CM changes; test inventory.

### Dependencies
- B2 Done (events exist to consume).
- Integration owner if leaving stub.

### Risks
| Risk | Mitigation |
|---|---|
| Retry policy debate | Default for B3: log failure, no retry; record TBD for later |
| Fake email gateway | Stub interface only |

### Acceptance Criteria
- [ ] B3 developer has no unanswered “what do I emit/consume” questions for the stub.
- [ ] BR-NOTIF conflicts resolved by explicit B3 subset.

### Definition of Done
- **Build Authorization for B3**.

---

## B3 — Build: Notification Stub & Quality Bar

### Objectives
- Deliver Notification stub against G2.
- Raise quality bar so a second squad can join ECMF without rediscovering tribal knowledge.

### Deliverables
1. Consumer stub for agreed events (e.g. CaseAssigned; CaseCreated if configured).
2. Failure logging per G2 (no silent drop).
3. Regression pack: authz matrix cases, transition negatives, CM fallback, outbox re-drain.
4. Dev runbook: compose, migrate, seed matrix, token, drain outbox (`15` minimal).
5. Known-limitations register (SSO, broker, SLA, read-audit, DR) with owners.

### Required Documents
G2 outputs; minimal runbook; limitations register in `27` or `15`.

### Dependencies
- G2 Build Authorization.

### Risks
| Risk | Mitigation |
|---|---|
| Expanding into full Notification product | Stub only; no templates engine |
| Calling B3 “ops ready” | Limitations register must say otherwise |

### Acceptance Criteria
- [ ] Stub tests green; at least one failure-path test.
- [ ] New developer setup < documented time target (set in G2, e.g. 30–60 minutes).
- [ ] No open P0/P1 contract defects on ECMF slice.

### Definition of Done
- Cross-domain stub exists; program may plan SLA/CRM FRDs under the same **G then B** pattern.

---

## Explicitly deferred (do not pull into G0–B3)
| Item | Rule |
|---|---|
| Message broker product ADR | Before multi-service async or non-prod integration claim |
| SSO / enterprise IdP | Before shared UAT with real users |
| SLA matrix / clocks | Own G-gate before any SLA coding |
| CRM/KPI/Dashboard APIs | Own G-gate (FRD+OpenAPI) each |
| DR/backup/alerting | Before production |
| Frontend | Separate ADR when UI funded |
| Enterprise BR catalog Acceptance | Parallel; not blocking if Sprint BR SoT holds |
| Audit-on-read | Only if BO funded in G0 |

---

## Wrong priorities corrected (v1 → v2)

| v1.0 | v2.0 |
|---|---|
| 3 readiness sprints | **1 gate sprint (G0)** |
| Mapping dual BR IDs | **Single delivery SoT** |
| Docs-only purity | **Readiness engineering in G0** |
| CI may be red | **CI green before B1** |
| Outbox in last sprint | **Outbox table in G0/B1** |
| Audit-on-read assumed | **Challenged; default defer** |
| Notification inside assign sprint | **Own G2 → B3** |
| Docs+code same sprint (IS-2) | **Hard G1 before B2** |
| SA edit as sprint goal | **Hygiene task inside G0** |

---

## Final Answer (v2)

### At which sprint can developers start coding?

| Activity | Sprint |
|---|---|
| Readiness engineering (compose, CI, error envelope, Alembic 0) | **G0** (allowed; not product features) |
| **First product feature coding** (create/get) | **B1**, only after G0 Build Authorization |
| Assign/status coding | **B2**, only after **G1** |
| Notification stub coding | **B3**, only after **G2** |

**Conservative CTO position:** Do **not** treat the legacy “Sprint-01 APPROVED — GO” as build authorization **[superseded — see DEC-002: GO = slice + G0 platform floor is the governing decision]**. **B1** is the first authorized product coding sprint. G0 is mandatory and timeboxed; it replaces RS-1+RS-2+RS-3.

**Why this survives a gate review:** It burns the real risks (SoT, schema, CI, error contract, write-audit, outbox, CM stub, authz claims) before features — without three sprints of paperwork — and refuses to start lifecycle/notification code without separate contract gates.

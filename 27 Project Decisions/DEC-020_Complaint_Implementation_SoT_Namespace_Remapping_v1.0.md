# Decision Record — Complaint Implementation SoT & Namespace Remapping (OQ-CM-B1-001)

| Field | Value |
|---|---|
| ID | DEC-020 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Architecture Board / Business Owner |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Related | OQ-CM-B1-001; FRD-CM-001 v1.1 LOCKED; PROGRAM-IMPLEMENTATION-001; BMR-001; PROGRAM-ADR-002; PROGRAM-DOC-001 |
| Type | Project Decision (non-ADR) — remapping / SoT sequencing |

- Decision Status: **Accepted**
- Resolves: **OQ-CM-B1-001** (*When does BR-CM-CAT-001 replace Sprint delivery SoT for implementation?*)
- Does **not** Accept ADR-014/015, unlock Mode B, Batch-2, or real-customer production

---

## Context

OQ-CM-B1-001 asked for a DEC remapping date: when BR-CM-CAT-001 / Complaint Aggregate becomes the implementation SoT in place of Sprint delivery IDs and paths.

The foundation backend intentionally contains three complaint-related implementations and two HTTP namespaces:

| Implementation | Primary persistence | Production HTTP |
|---|---|---|
| Legacy ECMF complaints | `complaints` (+ related) | `/api/v1/complaints` (full lifecycle surface) |
| Complaint CA BC (CAPABILITY-004…008) | `complaint_cases*` | Ticket-nested only; full foundation router **unmounted** |
| CM Batch 1 Aggregate | `cm_batch1_*` | `/api/v1/cm/*` (FR-001…FR-004) |

Prior approved policy (PROGRAM-IMPLEMENTATION-001 / Board posture):

- No forced merge of implementations
- Controlled coexistence
- Cutover only by Decision
- Governance gates remain active (Mode B, Batch-2, real-customer, EX-A…H)

FRD-CM-001 v1.1 is LOCKED as Batch 1 Aggregate SoT but explicitly does **not** upgrade BR-CM-CAT-001 (Draft), ADR-014/015, or silently overwrite Sprint delivery IDs until remapping is decided.

---

## Decision

**OQ-CM-B1-001 is resolved as follows:**

1. **There is no single “replacement date” that retires Sprint delivery SoT now.**  
   BR-CM-CAT-001 / FRD-CM-001 Aggregate model **does not** wholesale replace Sprint delivery SoT for all complaint implementation.

2. **Dual SoT under controlled coexistence (binding until a future Retirement DEC):**

| Concern | Authoritative SoT | Canonical namespace / code |
|---|---|---|
| Batch 1 Complaint Aggregate intake (FR-001…FR-004) | FRD-CM-001 v1.1 LOCKED (+ BR-CM-CAT-001 rule IDs as cited by that FRD) | `/api/v1/cm` · `backend/app/modules/cm_batch1/` |
| Foundation / Sprint delivery lifecycle (assign, escalate, resolve, close, search, SLA-on-legacy, IAM-coupled complaint ops) | Sprint/foundation catalogs & FRDs already governing those paths | `/api/v1/complaints` · `backend/app/modules/complaints/` (+ related legacy modules) |
| Visit-linked Complaint BC (QueueTicket → Complaint) | `complaint-domain-service.v1.yaml` / DOM-COMPLAINT-001 | Tables `complaint_cases*`; **production** = ticket-nested routes only; full router remains unmounted pending a separate Cutover DEC |

3. **Long-term roles (no merge):**

| Stack | Long-term role |
|---|---|
| `cm_batch1` | Target Aggregate intake path for Complaint Management Module Batch 1; future Batch-2 Case work attaches here **only after** Board unlock (out of scope of this DEC) |
| Legacy `complaints` | Production foundation lifecycle path until an explicit **Retirement DEC**; defect-driven maintenance only (BMR EPIC-ECMF-LEGACY) |
| `complaint_cases` | Separate bounded context for visit/complaint linkage; **not** an evolutionary stage of `cm_batch1`; not a silent replacement for legacy `/api/v1/complaints` |

4. **Canonical ownership of namespaces:**

| Namespace | Owner capability | Consumers MUST treat as |
|---|---|---|
| `/api/v1/cm` | CM Batch 1 Aggregate APIs (API-500…512) | Canonical for FRD-CM-001 Batch 1 |
| `/api/v1/complaints` | Foundation/legacy lifecycle (+ shared attachment listing where catalogued) | Canonical for foundation lifecycle; **not** interchangeable with Aggregate create semantics |
| Shared `/api/v1/attachments*` | Platform attachment CAP (used by Batch 1 and foundation) | Shared; Batch 1 transfer remains under `/api/v1/cm/attachments/transfer` |

5. **ID remapping policy:**  
   Tooling and documents MUST qualify IDs (FRD-CM-001 / BR-CM-CAT vs Sprint FR/BR/API). Catalog collisions (e.g. API-390) MUST be resolved in `07 API Catalog` before those IDs are treated as stable automation anchors. This DEC does **not** renumber historical Sprint IDs.

6. **Cutover / retirement:**  
   Mounting `complaint_foundation_router`, retiring `/api/v1/complaints`, or collapsing namespaces requires a **new Board Decision** that meets the prerequisites in Acceptance Criteria. This DEC **authorizes coexistence**, not retirement.

7. **Explicit non-goals (binding):**  
   This DEC does **not**: merge stacks; rewrite history; redesign BCs; unlock Mode B; unlock Batch-2; unlock real-customer production; Accept ADR-014/015; change OpenAPI path contracts; enable outbox publisher; or exit EX-A…H.

---

## Consequences

### Positive
- OQ-CM-B1-001 closed with a clear dual-SoT rule (no ambiguous “which FR-001?”).
- Implementers and FE consumers have canonical namespace ownership without forced merge.
- Governance gates (Mode B, Batch-2, real-customer, EX pack) remain intact.
- Aligns with FRD-CM-001 D-01 / LOCK caveat and PROGRAM-IMPLEMENTATION-001.

### Trade-offs
- Dual namespaces and dual ID spaces persist until a Retirement DEC.
- CA BC full surface remains documented but mostly unavailable in production.
- Catalog hygiene (status flags, ID collisions) still needs follow-up work under OpenAPI/RTM impact (below)—without changing contracts in this DEC.

### Follow-up (documentation only; not authorized as feature work by this DEC)
- After Board **Accept**: mark OQ-CM-B1-001 **Closed** in FRD/open-question trackers; reference DEC-020.
- Sync narrative in BMR / API catalog README to “Implemented (lab) coexistence” vs metadata `Planned` **without** altering path contracts unless a separate catalog change is approved.
- Keep RTM-CM-B1-001 mapped to `/api/v1/cm` and foundation RTMs mapped to `/api/v1/complaints`.

---

## Alternatives Considered

### A — Immediate wholesale remapping (BR-CM-CAT replaces Sprint SoT on a fixed date)
- Rejected: forces merge/retirement; violates coexistence policy; unlocks uncontrolled cutover; conflicts with FRD LOCK caveat and EX pack.

### B — Declare `/api/v1/complaints` the only canonical namespace; treat `/api/v1/cm` as temporary
- Rejected: contradicts FRD-CM-001 Aggregate SoT and shipped Batch 1 Aggregate APIs.

### C — Merge `cm_batch1` + legacy + `complaint_cases` into one module/table
- Rejected: redesign / forced merge; different aggregates and lifecycles; out of constraint.

### D — Controlled dual SoT + coexistence until explicit Retirement DEC (**selected**)
- Pros: resolves OQ without unlocking gates; preserves baseline; clear ownership.
- Cons: temporary complexity remains visible.

---

## Migration Strategy

**Phase 0 — Now (this DEC, on Accept)**  
- Adopt dual-SoT ownership table above.  
- No code moves. No path retirement. No router mount changes.

**Phase 1 — Consumer alignment (no contract change)**  
- Batch 1 UI/API clients → `/api/v1/cm` for FR-001…004.  
- Foundation lifecycle clients → `/api/v1/complaints`.  
- Do not call legacy create as a substitute for Aggregate registration.

**Phase 2 — Catalog / RTM hygiene (separate approved doc tasks)**  
- Disambiguate API IDs; align OpenAPI `info`/`x-ecmp-status` with coexistence reality.  
- RTM rows cite path+method until IDs stable.

**Phase 3 — Optional cutovers (require new DEC each)**  
- CA BC full mount **or** retire unmounted surface.  
- Legacy path retirement / Aggregate takeover of lifecycle.  
- Batch-2 Case create on Aggregate.  
Each Phase 3 item is **out of scope** of DEC-020 and remains Board-gated.

---

## Risks

| Risk | Mitigation |
|---|---|
| Teams treat this DEC as retirement authorization | Explicit non-goals + Acceptance Criteria |
| FE binds Batch 1 to `/api/v1/complaints` create | Namespace ownership table; consumer impact section |
| Silent mount of `complaint_foundation_router` | Forbidden without Cutover DEC |
| Tooling confuses Sprint FR-001 with FRD-CM-001 FR-001 | Qualified IDs until catalog remediates collisions |
| Scope creep into Mode B / Batch-2 / real-customer | Non-goals; gates unchanged |

---

## Acceptance Criteria

This Decision is **Accepted** only when Architecture Board confirms all of the following:

1. Dual-SoT coexistence table is binding project policy.  
2. No implementation merge or namespace collapse is authorized by DEC-020.  
3. OQ-CM-B1-001 is marked **Closed — remapped by dual SoT (DEC-020)** (not “Sprint SoT retired”).  
4. Prerequisites for **any future retirement** remain all of:
   - Dedicated Retirement/Cutover DEC  
   - Consumer migration complete for affected paths  
   - OpenAPI + RTM updated under catalog governance  
   - CA BC mount-or-retire decided explicitly  
   - No reliance on this DEC for Mode B, Batch-2, or real-customer production  
5. ADR-014/015 status and SEC-MIG Phase 2+ gates are **unchanged** by Accept of DEC-020.

---

## Impact on OpenAPI

- **No path/contract changes** authorized by this DEC.  
- `complaint-management-batch1.v1.yaml` remains Aggregate catalog for `/api/v1/cm`.  
- `complaint-service.v1.yaml` remains foundation catalog for `/api/v1/complaints`.  
- `complaint-domain-service.v1.yaml` remains CA BC catalog; production availability limited to mounted ticket-nested ops until Cutover DEC.  
- Metadata/status/ID-collision remediation may proceed as catalog hygiene **without** inventing new product paths.

## Impact on RTM

- RTM-CM-B1-001 continues to trace FR-001…004 → `/api/v1/cm` (API-500…512).  
- Foundation/Sprint RTMs continue to trace lifecycle → `/api/v1/complaints` and related foundation APIs.  
- Until catalog ID collisions are fixed, traceability MUST prefer **path + method** anchors.

## Impact on Consumers

- Batch 1 consumers: **must** use `/api/v1/cm` for Aggregate intake.  
- Lifecycle consumers: **must** continue `/api/v1/complaints` until Retirement DEC.  
- No consumer is required to migrate off legacy by this DEC.  
- Shared attachment endpoints remain valid where already catalogued.

---

## Open Questions Remaining

| ID | Status after DEC-020 | Note |
|---|---|---|
| **OQ-CM-B1-001** | **Closed — remapped by dual SoT (DEC-020)** | Dual SoT; no wholesale replacement date |
| OQ-CM-B1-002…014 | **Open** (unchanged) | Outside this DEC |
| Future Retirement DEC | **Not opened** | Required before legacy/`complaint_cases` full-surface cutover |
| ADR-014 / ADR-015 | **Proposed — Revised — Pending Board Review** (PROGRAM-ADR-004; not Accepted) | Mode B still gated |
| EPIC-CM-F4 / Batch-2 | **Not unlocked** | Unchanged |

---

## Links

- FRD: `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md`
- OpenAPI Aggregate: `07 API Catalog/openapi/complaint-management-batch1.v1.yaml`
- OpenAPI Foundation: `07 API Catalog/openapi/complaint-service.v1.yaml`
- OpenAPI CA BC: `07 API Catalog/openapi/complaint-domain-service.v1.yaml`
- RTM: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md`
- Open Questions: `27 Project Decisions/OPEN_QUESTIONS.md`

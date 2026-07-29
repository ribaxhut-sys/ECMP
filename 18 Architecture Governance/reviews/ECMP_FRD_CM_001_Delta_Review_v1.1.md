# FRD-CM-001 — Delta Architecture Review (v1.0 → v1.1)

| Field | Value |
|---|---|
| ID | GOV-DELTA-FRD-CM-001 |
| Version | 1.0 |
| Subject | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (v1.1 LOCKED) |
| Baseline | FRD-CM-001 Draft v1.0 |
| Inputs | GOV-REV-FRD-CM-001; GOV-RP-FRD-CM-001 (Revision Plan v1.1); CTO Decisions D-01…D-08 |
| Review Type | Delta review — modified content only |
| Reviewer Role | Principal Enterprise Architect |
| Status | 🟢 Complete — CTO Approval D-08 applied; FRD LOCKED |
| Date | 2026-07-29 |

Scope: changes made for `C-01`…`C-06` and Majors dispositioned **Accept**. Deferred findings and backlog items excluded.

---

## Executive Summary

All six Critical findings are resolved, and every Major marked **Accept** in the Revision Plan is addressed in the FRD text — not merely acknowledged in the Revision Summary. Verification was performed against the FRD body rather than §20, and the two matched in every case checked.

The three highest-value corrections landed cleanly: Case creation is removed from Batch 1 at all fourteen locations where it previously appeared (`C-03`); idempotency is now a first-class Batch 1 capability with its own exceptions, validation rules, DM entity, and acceptance criteria rather than a deferred enhancement (`C-05`); and enumeration protection is a normative five-control table with declared owners and a fail-closed rule (`C-06`).

Scope did not expand. Batch 1 remains FR-001…FR-004, and the only scope movement is **subtractive** (Case create removed, full Customer 360 narrowed to the D-05 subset). Locked architecture is untouched. No governance regression: ADR-014 and ADR-015 remain 🟡 Proposed, BR-CM-CAT-001 remains 🟡 Draft, and the FRD does not claim otherwise.

Three minor ambiguities were introduced alongside the new idempotency and evidence-transfer capability. None is blocking.

---

## Resolved Critical Findings

| Finding | Status | Notes |
|---|---|---|
| C-01 | ✅ Resolved | D-01 applied. §2.1 and §1.1 now read "Architecture Baseline Pending Governance Approval"; namespace table qualified to "intended normative … after approval"; Status = Draft v1.1; Architecture Review Checklist leaves *Claude Delta Review* and *CTO Approval → LOCKED* unchecked. No ADR/BR status was upgraded to manufacture readiness. |
| C-02 | ✅ Resolved | Authorization removed from the §4 external dependency table. New **§4.1** declares authorization ECMP-internal per ADR-008 / ADR-014 / ADR-015 and explicitly prohibits an outbound Authorization API. Reinforced at §13 integration constraint 4, FR-001 §16.1, FR-002 §7.2 / §16.4, FR-004 §7.2. |
| C-03 | ✅ Resolved | D-02 applied consistently: §2.3, §3 note, §6 (BR-004 deferred), FR-001 §3 / A4 / §15.3 / validation invariants, FR-003 §3 / §4 / Normal Flow 6 / **E5** / §15.3 / AC-8, SCR-CM-003 ("no Add Case"), UC-CM-003 and UC-CM-007 reworded, §15 reverse mapping, DM-CM-009 marked Deferred, §17 Out of Scope. Audit event `ResolvedAsCaseOnExisting` removed and replaced by `DuplicateRecommendedExisting` / `DuplicateRedirectedToExisting`. |
| C-04 | ✅ Resolved | **Exactly one** now used uniformly: FR-001 §9.2, E1, §12, §13; FR-002 §3, §9.1, §12, §13, AC-7. FR-002 E5 correctly inverted from "conflicting keys → manual resolution" to "**more than one key type supplied → MUST reject as invalid input**", which removes the structural contradiction rather than papering over it. |
| C-05 | ✅ Resolved | D-03 applied. Request Id MUST (E8), Channel Message Id MUST for channel-sourced creates (E9), replay and double-submit handling in **A6**, idempotency enforced pre-persist (§9.9), `DM-CM-010 Idempotency Record` added to §14 and the RTM, outcome exposed in §14 Output Data, AC-10 and AC-11 added. Critically, the contradictory Future Enhancement item ("per-message-id idempotency") is **deleted** from FR-001 §21 — the deferral that conflicted with in-scope auto-register is gone, not just overridden. |
| C-06 | ✅ Resolved | D-04 applied. **§16.1** is a normative table of five MUST controls (rate limiting, progressive delay, abuse detection, security audit, alerting) with named owners; "Enterprise Security Controls (Anti-Enumeration)" added to §4 with an owner; **fail-closed** stated if the dependency is unavailable; FR-002 §7.5 precondition; E6 threshold breach; AC-8. The circular masking rule is replaced with an unconditional ban — *"cleartext identity numbers MUST NOT be stored in audit"* (§16.1, §17). |

---

## Remaining Critical Findings

**No remaining Critical Findings.**

---

## Remaining Major Findings

Unresolved items among those dispositioned **Accept**:

*None.* All eleven Accept-marked Majors (`M-01`, `M-03`, `M-04`, `M-06`, `M-07`, `M-09`, `M-10`, `M-12`, `M-13`, `M-15`, `M-16`) are present in the FRD body — verified at FR-001 E3/§15.10, FR-003 E1 work item, FR-002 §14 `asOf` + §15.2, FR-004 §9.4/E7/§12 anchor membership, FR-003 §9.3/§12 CLOSED qualification, FR-004 §12/§14 integrity hash MUST + §16.5/§17 sensitive access MUST, FR-003 E4/A3 uniform-empty MUST, FR-001 §18 ECMP outbox + DM-CM-012, FR-003 §9.2/§12 candidate cap and timeout, §13 catalog collision caveat, and §6.1 KPI table + FR-001 A4.4 supervisor aging flag.

For completeness, the following remain open but were **not** Accept-dispositioned and are therefore out of delta scope:

- `M-02` — parked as **OQ-CM-B1-011** (sync vs async index visibility). Note that the `C-05` idempotency controls materially mitigate the duplicate-creation risk that made `M-02` urgent; the residual is candidate-completeness, not Aggregate duplication.
- `M-14` — audit retention values parked as **OQ-CM-B1-009**; structure referenced in §14.
- `M-11` — logical transaction boundary now stated in §14 and E8; the architecture decision itself remains with the Solution Architect.
- `M-17` / `m-12` — deferred to v1.2 per D-07.

---

## Regression Check

**YES** — three new issues, all minor and none blocking.

1. **`TRANSFERRED` status semantics (FR-004 §14 vs A4.3).** §14 Output Data adds `TRANSFERRED` to the attachment status enum, while A4.3 describes the mechanism as *"void of staging token + bind/transfer events"* — implying the artifact ends `ACTIVE` on the surviving Complaint. It is unclear whether `TRANSFERRED` is a terminal status on a source record or a transient state. Introduced with D-06.

2. **Idempotency key lifetime unspecified (FR-001 §12, DM-CM-010).** Request Id and Channel Message Id are mandatory and an idempotency record is persisted, but no retention window or TTL is stated. A replay arriving long after the original create has no defined outcome — replay response or new Aggregate. Not captured as an Open Question. Introduced with D-03.

3. **Request Id generation authority (FR-001 §12, SCR-CM-001).** §12 reads *"MUST be unique per successful create semantics"* — circular — and SCR-CM-001 notes the Request Id is *"handled by client/gateway"* without stating which. A client-generated idempotency key is trust-sensitive; FR-001 §22 names channel replay forgery as a threat but does not address human-path key provenance. Introduced with D-03.

Also noted, not a defect: FR-001 §9.10 lists staged-attachment binding inside the create `SHALL` sequence while §14 places binding **outside** the atomic set with compensable failure via E8. The two are reconcilable (sequence vs atomicity), but a literal reader could implement the bind inside the transaction — the precise ambiguity `M-11` was raised against.

---

## Security Assessment

**PASS.**

Every mandated control is present and normative:

| Control | Location | Level |
|---|---|---|
| Idempotency | FR-001 §9.9, §12, E8/E9 | MUST |
| Replay protection | FR-001 A6, E10, AC-10/11 | MUST |
| Double submit protection | FR-001 A6.4 | MUST |
| Enumeration protection | FR-002 §16.1 | MUST |
| Rate limiting | FR-002 §16.1 | MUST |
| Abuse detection | FR-002 §16.1 | MUST |
| Security audit | FR-001 §17, FR-002 §17, FR-003 §17, FR-004 §17 | MUST |
| Alerting | FR-002 §16.1, §18 | MUST |
| Threats / Mitigations / Residual Risk | **§22 on all four FRs** | Present |

Three prior weaknesses are closed at the level that matters: the enumeration oracle now fails closed rather than degrading open; the audit masking rule is unconditional rather than self-referential; and anti-inference uniform-empty behaviour moved from `SHOULD` to `MUST` (FR-003 E4).

No new security weakness of substance. The idempotency key is new attack surface, and its residual — compromised channel credentials submitting valid first-seen Message Ids — is correctly named in FR-001 §22 rather than assumed away. Regression items 2 and 3 are hardening gaps in that new surface, not exploitable weaknesses.

The residual-risk statements are credible rather than decorative: FR-002 §22 concedes that a distributed low-and-slow attacker across many authorized principals can stay under per-principal thresholds, accepted only with SOC alerting. That is the correct residual to name.

---

## Architecture Assessment

**PASS.**

| Invariant | Verdict | Evidence |
|---|---|---|
| Aggregate Root preserved | ✅ | §3 unchanged; FR-001 §15.2, validation invariants; FR-004 anchor membership invariant (§9.4, §12, E7) **strengthens** the boundary |
| CustomerId-only preserved | ✅ | FR-001 §15.1; FR-002 §15.1–15.2 with `asOf` and ADR-002 retention/PII; UNVERIFIED state now bounded by a reconciliation MUST + aging + max pending duration (FR-001 E3, §15.10) |
| API First preserved | ✅ | §13 integration constraints 1–4; per-FR Backend-only requirements |
| No Direct Database Access preserved | ✅ | §4 preamble, §13 constraint 3 |
| Customer 360 minimal scope only | ✅ | D-05 subset (Profile + Active Complaints + Complaint Count) as MUST at FR-001 §9.4 and FR-002 §9.8; full 360 explicitly out of scope (§2.3, §17, FR-002 §15.6) |
| No Information Lost preserved | ✅ | FR-004 §15.1–15.2, §15.7; strengthened by integrity hash MUST, sensitive-access audit MUST, and D-06 transfer |

**Scope containment verified.** Batch 1 contains only Complaint Registration, Customer Search, Duplicate Detection, and Attachment Upload. No Case creation (checked at fourteen locations, including the removal of the `ResolvedAsCaseOnExisting` audit event and the DM-CM-009 deferral). No Assignment. No SLA execution — FR-001 A4.3 retains the prohibition and Calendar remains a later dependency.

**Evidence handling verified.** Staged evidence MUST transfer on duplicate redirect (FR-001 A2.4, FR-003 A2.4, FR-004 A4.3, AC-7/AC-8); physical discard prohibited; non-redirect cancellation is void-with-reason; abandoned sessions auto-void after TTL with binaries retained under legal hold; `AttachmentTransferred` audit event added; History remains append-only and reconstructable.

**Open Questions verified.** Customer Merge appears **only** as `OQ-CM-B1-007`, marked v1.2 with the instruction *"do not design in Batch 1"*, cross-referenced from §17 Out of Scope, FR-002 §15.7, and FR-002 §21.4. No design content was added.

**Governance verified.** D-01 applied without regression: ADR-014 🟡 Proposed, ADR-015 🟡 Proposed, BR-CM-CAT-001 🟡 Draft — none altered to clear the path. OQ-CM-B1-001 retained. The gate sequence in the checklist is intact and the correct boxes remain unchecked.

---

## Recommendation

**APPROVE FOR CTO** — **Applied (D-08).** FRD-CM-001 v1.1 is **LOCKED**.

All six Critical findings and all Accept-dispositioned Majors are resolved in the document body. Locked architecture is unchanged, scope moved only subtractively, and no governance status was manipulated. The three new minor ambiguities (`TRANSFERRED` semantics, idempotency key lifetime, Request Id provenance) are folded into LOCK as **OQ-CM-B1-012…014 / Architecture Decision candidates** — they do not warrant another revision cycle.

See: `18 Architecture Governance/reviews/ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md`

---

## Related

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (subject — **LOCKED**)
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (baseline)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Architecture_Review_v1.0.md` (GOV-REV-FRD-CM-001)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Revision_Plan_v1.1.md` (GOV-RP-FRD-CM-001)
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md` (GOV-RN-FRD-CM-001)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001)
- ADR-002, ADR-008, ADR-009, ADR-014, ADR-015

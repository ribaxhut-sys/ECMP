# ECMP Repository Lifecycle Policy

| Field | Value |
|---|---|
| ID | LIFECYCLE-01 |
| Document | ECMP Repository Lifecycle Policy |
| Version | 1.0 |
| Type | Repository Governance Policy |
| Mode | Read-only · Declarative only |
| Date | 2026-08-01 |
| Status | 🟢 Active |
| Owner | Enterprise Architecture / PMO |
| Anchors | BASELINE-01 · CERT-01 · MANIFEST-01 · CLS-01 · Capability Register · CHANGELOG · `deploy/evidence/` |
| Scope | Define when the current repository baseline remains valid, and when a new baseline must be created |

> This policy does **not** introduce new governance.  
> It explains **lifecycle transitions** already implied by BASELINE-01 and CERT-01.

---

## Repository Files Audited (read set)

| Source | Path / locus |
|---|---|
| BASELINE-01 | `00 Repository Guide/ECMP_Repository_Baseline_Freeze_BASELINE-01_v1.0.md` |
| CERT-01 | `00 Repository Guide/ECMP_Repository_Certification_CERT-01_v1.0.md` |
| MANIFEST-01 | `00 Repository Guide/ECMP_Repository_Handover_Manifest_MANIFEST-01_v1.0.md` |
| CLS-01 | session canvas `cls-01-project-closure.canvas.tsx` |
| Capability Register | `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` |
| CHANGELOG | `CHANGELOG.md` |
| Evidence | `deploy/evidence/` |

---

## 1. Current Baseline

| Item | Value |
|---|---|
| Baseline ID | BASELINE-01 v1.0 |
| Certification ID | CERT-01 v1.0 |
| Candidate | `v1.2.0-rc.1` |
| Repository SHA | `6890f50` (`6890f50d8243ba30589a3d88f0c0efcef791ce01`) |
| Freeze / certification date | 2026-08-01 |
| Navigation SoT | MANIFEST-01 |
| Capability SoT | Capability Register BP-CAP-001 |
| Lifecycle state | **Frozen · Certified** |

---

## 2. Repository Lifecycle State

| State | Meaning |
|---|---|
| **Frozen** | Documentation baseline identity is fixed per BASELINE-01 |
| **Certified** | Governed repository state attested per CERT-01 (repository baseline only) |
| **Valid** | Current baseline remains in force until a baseline-triggering event occurs |
| **Superseded** | A new baseline (and, as applicable, new certification) has been declared with new repository evidence |

Current official state: **Frozen · Certified · Valid**.

---

## 3. Events That Preserve Baseline

The following classes of change **do not** by themselves invalidate BASELINE-01 or CERT-01, provided they do **not** alter baseline identity, capability disposition, deferred set, contracts of record, release posture, or ownership boundaries (BASELINE-01 §8).

| Preserve-baseline event (examples) | Notes |
|---|---|
| Documentation typo / formatting correction | Editorial only |
| Evidence addition under `deploy/evidence/` | New dated evidence may be appended; does not rewrite baseline identity |
| Release note or CHANGELOG correction of fact already recorded | Correction without new version baseline |
| README or navigation clarity update | Does not change architecture position or ownership boundary |
| Index / cross-link updates consistent with MANIFEST-01 | Navigation hygiene |
| Session package regeneration that restates existing evidence | Does not replace Register / BASELINE / CERT |

Preserving events may still be recorded as evidence; they do not require BASELINE-02 (or successor) unless a trigger in §4 occurs.

---

## 4. Events That Require New Baseline

A **new repository baseline** must be created when repository evidence records a change already implied as baseline-affecting by BASELINE-01 §8 (baseline identity, capability disposition, deferred set, contracts, release posture, or ownership boundaries).

| Require-new-baseline event (examples already implied) | Implied by |
|---|---|
| New capability officially opened / registered beyond current Register set | Capability Register · BASELINE-01 (new evidence required) |
| Capability disposition changes (e.g. Stay Deferred → Remain / Implemented / CLOSED, or reopen) | Capability Register · B2-08 disposition model · BASELINE-01 |
| Production release officially authorized (final release posture change) | Release evidence · CERT-01 non-certification of production · BASELINE-01 release posture |
| New repository version baseline (new candidate / release identity replacing `v1.2.0-rc.1` @ `6890f50` as baseline anchor) | CHANGELOG · tagging · BASELINE-01 version identity |
| Architecture SoT changes affecting module position, Mode A/B boundary, or ownership | ADR / README / BASELINE-01 ownership boundaries |
| Deferred set changes (items enter or leave official deferred baseline) | BASELINE-01 §6 · CLS-01 · Register |
| Contract-of-record changes (API / Event / Data Dictionary normative SoT material change tied to baseline) | BASELINE-01 §8 “contracts” |
| Enterprise identity / Mode B unlock recorded as implementation no longer deferred | ADR-014/015 conditions · EP evidence · BASELINE-01 deferred / external |

When such an event is evidenced, the succession path implied by existing freeze/cert documents is:

1. New repository evidence  
2. New baseline declaration (successor to BASELINE-01)  
3. Re-certification as applicable (successor to CERT-01)  
4. Manifest / navigation update as needed (successor to MANIFEST-01)

This policy does not authorize those events; it only states when a new baseline is required **if** they occur with evidence.

---

## 5. Repository Freeze Policy

| Rule | Statement |
|---|---|
| Freeze in force | BASELINE-01 freeze remains in force while lifecycle state is Valid |
| Mutation of baseline content | Baseline identity and certified areas are not rewritten in place |
| Evidence accumulation | Allowed under preserve-baseline rules (§3) |
| Baseline-affecting change | Requires new baseline (§4); does not silently amend BASELINE-01 or CERT-01 |
| Authorization | Freeze does not authorize engineering, architecture invention, capability reopen, or release (BASELINE-01 §8) |

---

## 6. Certification Validity

| Rule | Statement |
|---|---|
| Validity scope | CERT-01 remains valid **only** for the repository documentation baseline frozen by BASELINE-01 |
| Remains valid while | Baseline identity (`v1.2.0-rc.1` @ `6890f50`) and BASELINE-01 freeze remain unsuperseded |
| Becomes invalid / superseded when | A new baseline is declared for a §4 event, or CERT-01 is expressly superseded by a successor certification |
| Never implied by CERT-01 | Production · Enterprise Platform · Enterprise SSO · deferred capabilities (CERT-01 §5) |
| Companion authority | Capability Register, MANIFEST-01, CLS-01, evidence packs, and ADRs remain authoritative in their roles (CERT-01 §4 · BASELINE-01 §9) |

---

## 7. Lifecycle Statement

The ECMP repository documentation baseline is currently **frozen and certified** (BASELINE-01 · CERT-01). It remains **valid** for editorial, evidence-append, and non-identity documentation changes. Any evidenced change to baseline identity, capability disposition, deferred set, contracts of record, release posture, or ownership boundaries requires a **new baseline** (and re-certification as applicable). This lifecycle policy introduces no new governance bodies, gates, or requirements; it restates the transition rules already declared by the freeze and certification documents.

---

## 8. Final Verdict

**ECMP REPOSITORY LIFECYCLE DEFINED**

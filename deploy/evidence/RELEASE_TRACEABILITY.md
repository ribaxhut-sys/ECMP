# RELEASE_TRACEABILITY.md — Mode A Batch-1 RC

| Field | Value |
|---|---|
| Document ID | REL-TRC-MA-B1-001 |
| Date | 2026-08-01 |
| SHA | `1608245` |
| Scope | Mode A Batch-1 release governance chain |
| Approvals | **None in this file** |

---

## Chain overview

```text
Requirement (FRD / FR)
    ↓
Decision (DEC) — cite file path if ID collides
    ↓
ADR (architecture constraints)
    ↓
Implementation (dual SoT trees)
    ↓
Testing (packs / CI / RTM)
    ↓
Evidence (deploy/evidence)
    ↓
Release (REL-RC-001 → tag)  ← OPEN / NOT READY
```

---

## Matrix (primary Mode A paths)

| Requirement | Decision | ADR | Implementation | Testing | Evidence | Release |
|---|---|---|---|---|---|---|
| FRD-002 / lifecycle assign-status (API-003/004/005, FR-020) | DEC-006 (G1 freeze); U-5 **open** | ADR-005/006/008/009 | `implementation/backend` case-service | G2 pack — 103 recorded | `G1_Exit_Verified_*`, `G2_Mini_Gate_*`, `REGRESSION_PACK_G2.md` | REL-RC-001 **not passed** |
| G2 broker / obs / CM stub stance | DEC-021 **G2 file** (Accepted Mode A) | ADR-009 + Addendum G2 | In-process outbox; no physical broker | G2 pack includes outbox/notif | `G2_Mini_Gate_Mode_A_20260801.md`, `Observability_Minimum_*` | Same — RC cut open |
| Dual SoT / namespace | DEC-020 **SoT remapping** (Accepted) | ADR-014 conditions (module boundary) | `/api/v1/cm` Aggregate in `backend/` + case-service coexist | SIT SoT choice binding; dual tests | `Mode_A_SIT_SoT_Choice_*`, DEC-020 SoT file | RC must not force merge |
| Lab auth Mode A | DEC-020 **Lab auth** file (Accepted ops) — **ID collision** | ADR-007/012; ADR-015 deferred impl | Local JWT / Mode A; Mode B blocked | Security lab review | `Mode_B_Blocked_*`, Security sign-off CONDITIONAL | No Mode B in RC |
| FR-001…004 Batch-1 Aggregate | FRD-CM-001 / DEC-020 coexistence | ADR-014 module | `backend/` cm_batch1 + FE | RTM planned 100%; **executed 0%** (summary) | RTM Batch-1 docs; M3c lab pack (gov) | Do not claim executed RTM = G2 103 |
| FR-030 / FR-040 | Sprint03 residual **DEFER** under G2 DEC | ADR-009 re-eval on multi-process | Not Mode A DoD now | Out of G2 pack | `Sprint03_Residual_Mode_A_DoD_*` | Not RC invent |
| O-06 descendant AuthZ | DEC-021 **O-06** Proposed — **ID collision** | ADR-018 | Interim: no silent expansion | N/A Mode A RC | Collision register | Board before renumber |
| Ops probes `/live` `/ready` `/version` | DEC-021 G2 / catalog align | ADR-010 context | case-service + foundation | `test_prod_readiness` in G2 pack | G2 evidence note | Document in RC notes when SemVer chosen |
| Limited VPS ABSENT port | RAB GO WITH WAIVERS | — | Selective evidence/infra | Smoke post-P5 | Phase5 + Post_P5 + Approval Matrix | **Not** equal to Mode A Batch-1 RC tag |
| Production / Mode B | Board C-7 CLOSED | ADR-014/015 Accepted w/ Conditions | Gates in `config.py`; no invented IdP | — | `Mode_B_Blocked_*` | Out of scope |

---

## Broken / open links in the chain

| Break | Where | Impact |
|---|---|---|
| U-5 unsigned | DEC-006 → governance complete | Blocks “governance complete”; listed in MISSING_APPROVALS |
| DEC ID collision | Decision layer ambiguous | Board Decision required |
| REL-RC-001 §5 blank | Testing/Evidence → Release | Blocks RC cut |
| REL-TAG-001 vs feature tip | Release tagging | Board/RM path decision |
| SemVer / CHANGELOG absent | Release identity | RM/PMO decision |
| IMS-001 / SEC Baseline missing on tip | Standards layer | Optional ABSENT port |
| Batch-1 executed TC gap | Testing (Aggregate) | Disclose in RC notes; do not forge PASS |

---

## Dual-tree rule (binding)

| Concern | SoT for SIT | Do not |
|---|---|---|
| Frozen lifecycle contract | `implementation/backend` + `case-service.v1.yaml` | Claim VPS routes = case-service without Cutover DEC |
| Lab edge / operator UX | `backend/` on VPS | “Fix” by copying sprint routes without DEC |
| CM Batch-1 Aggregate | `/api/v1/cm` when in Batch-1 stories | Conflate with case-service IDs |

Source: `Mode_A_SIT_SoT_Choice_20260801.md`, DEC-020 SoT remapping file.

---

## Release terminus (target state — not achieved)

```text
Human approvals complete
  → Board DEC collision + tag path resolved
  → Clean commit + CHANGELOG [X.Y.Z-rc.N]
  → REL-RC-001 §5 Go
  → Annotated tag on authorized ref (per REL-TAG-001)
  → RC_GATE_REPORT flipped to READY FOR RC
```

Current terminus: cut mechanics open (`RC_GATE_REPORT.md` re-gated 2026-08-01; `v1.1.0-rc.1` synced).

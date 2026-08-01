# B2-07 — ECMP Repository & Capability Alignment

| Field | Value |
|---|---|
| Document ID | GOV-B2-07-ALIGN-001 |
| Sprint | B2-07 |
| Date | 2026-08-01 |
| Authority | Architecture Review Board (ARB) / Repository Auditor |
| Scope | Governance + repository metadata synchronization **only** |
| Verdict | **ENGINEERING ALIGNMENT COMPLETE** |

## 1. Non-goals (enforced)

No new features · no Business Rules rewrite · no capability redesign · no CAP-008 functional change · no Backend/Frontend/OpenAPI/FRD business-content edits · no Mode B · no Enterprise Platform · no invented OIDC · no new git tags.

## 2. Capability Register sync (evidence-based)

| CAP | Prior Register | Evidence | Post B2-07 |
|---|---|---|---|
| CAP-001 | Implemented | TRC-L-001/002/009 Approved + `implementation/backend/` | Unchanged — Implemented |
| CAP-002 | Planned (stale) | TRC-L-003 Approved + assign route/tests | **Implemented (Sprint-02B slice)** |
| CAP-003 | Planned (stale) | TRC-L-004 Approved + status route/tests | **Implemented (Sprint-02B slice)** |
| CAP-004 | Planned | TRC-L-005 Planned; API-010 draft deferred | Unchanged — Planned |
| CAP-005 | Planned (stale) | TRC-L-006 Approved + notification stub | **Implemented stub (Sprint-02B)** |
| CAP-006 | Planned | TRC-L-007 Planned; no FR-030 engine | Unchanged — Planned |
| CAP-007 | Planned | TRC-L-008 Planned; foundation queue ≠ API-040 | Unchanged — Planned |
| CAP-008 | Program CLOSED (lab) | TRC-L-011…016; tag `v1.2.0-rc.1`; REL-RC-001 PASS | Unchanged — Program CLOSED (lab) |

## 3. FRD classification (metadata only)

See `03 Functional Requirements/README.md` § FRD Classification (B2-07).

## 4. Traceability actions

- Re-ran `python3 tools/sync_traceability_md.py` → `TRACEABILITY_MATRIX.md` includes TRC-L-011…016
- `traceability.yaml` → v0.12 (comment + `artifacts.br` BR-017 dictionary entry for TRC-L-013)
- Dual BR namespace (Sprint vs CM Aggregate) **reported**, not collapsed

## 5. Release provenance (report only)

| Release | Proven? | Evidence |
|---|---|---|
| `v1.0.0` | **Tag ABSENT** in this clone | Notes `docs/releases/v1.0.0.md`; remote branch `origin/release/v1.0.0` @ `6cb12fe`; tag **not** created by B2-07 |
| `v1.0.0-rc4` | Yes | Annotated/lightweight tag @ `bd0072c` |
| `v1.1.0-rc.1` | Yes (tag + CHANGELOG) | Tag @ `b079079`; **no** `docs/releases/v1.1*` file |
| `v1.2.0-rc.1` | Yes | Annotated tag @ `6890f50`; REL-RC-001 PASS; CHANGELOG `[1.2.0-rc.1]` |
| `v1.2.0` final | **Not authorized** | REL-SEC-001 NO-GO |

## 6. Files touched by B2-07

Listed in sprint output § Repository Files Updated.

---

*End of GOV-B2-07-ALIGN-001.*

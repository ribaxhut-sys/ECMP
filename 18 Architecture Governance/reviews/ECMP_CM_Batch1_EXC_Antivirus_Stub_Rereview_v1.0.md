# ECMP CM Batch 1 — EX-C Antivirus Stub Re-review

| Field | Value |
|---|---|
| Document ID | GOV-EX-CM-B1-EXC-RR-001 |
| Re-review ID | EX-20260826-01 |
| Parent exception | GOV-EX-CM-B1-S3-001 / EX-20260729-01 **EX-C** |
| Date | 2026-08-26 |
| Prepared by | Tech Lead / Engineering Assistant (Mode A) |
| Audience | Architecture (same channel as EX-20260729-01); Security Architect; PMO |
| Status | 🟡 **Ready for countersign** — not Board Resolution; not EX-C exit |
| Related | FR-004 / BR-012; TD-CM-003; EA-TARGET-CM-001 O11 / capability 27 |

---

## Ask

**Extend EX-C** (antivirus `STUB_ONLY`, always clean) for **lab / synthetic / non-real-customer** use.

Do **not** exit EX-C. Do **not** authorize a real AV engine, ClamAV-in-repo, Mode B, or high-trust attachment production.

## Why now

Parent pack calendar re-review was **2026-08-29** or first real-customer cutover. No Enterprise AV contract exists. Mode A lab COMPLETE (GOV-MODEA-M3C-001) still depends on documented stub, not a silent “scan is real” claim.

## Facts (unchanged)

| Item | State |
|---|---|
| Owner of AV engine | **Enterprise** (O11). ECMP owns attachment **policy** only (type, size, classification, clean-before-`ACTIVE`). |
| Runtime | `antivirus_mode=STUB_ONLY`; `StubAntivirusScanner` always `clean=True`. |
| Domain gate | FR-004 E2 / AC3 reject path exists; lab proof is mock-inject (`test_tc_cm_fr004_03_malware_reject`), not a live engine. |
| Complementary controls | MIME allowlist, 50 MB cap, filename sanitize, SHA-256, backend-only storage access. **Not** a substitute for AV. |
| Residual risk | Malware via stub AV — **elevated**; accepted for lab; **blocked** for high-trust / real-customer attachment prod until EX-C exits. |

## Recommended decision

1. EX-C **remains in force** with the same environment bound as EX-20260729-01: local Docker / Compose lab and synthetic customers only.
2. **Forbidden claims** until EX-C exit: Production Ready for real-customer evidence upload; “malware scanning enforced in this environment.”
3. **Forbidden work in this re-review:** implement AV product in ECMP; bind a lab-only ClamAV as if it were the Enterprise contract; Mode B / SSO / Identity Adapter; OpenAPI / FRD / Event Catalog change.
4. **Next engineering (only after Architecture-approved AV adapter epic + named scan contract):** thin adapter behind `AntivirusScanner`; policy-on → always scan; fail-closed on error/timeout; E2 security audit. Optional gate-hygiene (invert `STUB_ONLY` branch; AC3 audit assertion) is a **separate** small harden — not this pack.

## Explicit non-impacts

- Board Resolution, ADR-014/015/016/017/018, Target Architecture — **unchanged**
- FRD-CM-001 v1.1 LOCKED, OpenAPI, Event Catalog — **unchanged**
- EX-A, EX-B, EX-E…EX-H — **unchanged** (this pack is EX-C calendar re-review only)
- Mode B / C-B6-1 — **CLOSED**; this pack does not unlock it

## EX-C exit (unchanged from parent pack)

Real AV **adapter** + config, against an **Enterprise-named** scan contract (protocol, timeout, fail-closed), **before** high-trust attachment production. Exit is an Architecture-approved integration epic — not this document.

## Proposed next expiry

Whichever first:

1. First **real-customer** production cutover, or
2. Architecture-approved AV adapter epic that exits EX-C, or
3. Calendar re-review **2027-01-21**

Until this pack is countersigned, parent recorded expiry **2026-08-29** still stands.

---

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Architecture (mission authority) | | | ☐ Extend EX-C lab-only / ☐ Reject / ☐ Extend with conditions |
| Security Architect | | | ☐ |
| Domain PO ECMF | | | ☐ |
| Architecture Board Chair | | | ☐ (optional; not required to invent a Board Resolution) |

**Approved environment scope (if extended):** Local Docker / Compose lab and synthetic Customer Master only. **Not** unrestricted real-customer production.

**Conditions (if any):** _________________________________

**Proposed decision text:** Re-review EX-C (EX-20260826-01): remain `STUB_ONLY` for lab/synthetic; no AV engine in ECMP; high-trust attachment prod still blocked until EX-C exit.

---

## Related paths

- `18 Architecture Governance/reviews/ECMP_CM_Batch1_S3_Release_Exception_Pack_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md`
- `backend/app/modules/cm_batch1/antivirus.py`

---

*End of GOV-EX-CM-B1-EXC-RR-001 / EX-20260826-01.*

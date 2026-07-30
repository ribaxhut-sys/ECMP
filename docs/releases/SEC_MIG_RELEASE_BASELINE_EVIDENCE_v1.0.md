# ECMP SEC-MIG Release Baseline Evidence v1.0

| Field | Value |
|---|---|
| ID | SEC-MIG-EVID-BASELINE-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Task | TASK-PLATFORM-SECMIG-P7-003A |
| Owner | Release Manager |
| Status | 🟢 Issued |
| Template basis | REL-EVID-001 (identity + integrity only — not a shared/prod Go pack) |

Documentation / baseline freeze evidence. Does **not** record REL-SEC-001 GO.
Cutover remains **NO-GO** until shared recovery and full REL-SEC scorecard PASS (see PRR / CERT).

---

## 0. Release identity

| Field | Value |
|---|---|
| Product / line | ECMP foundation — SEC-MIG program package |
| Version / tag | `secmig-p6-baseline` |
| Git commit SHA | `PLACEHOLDER_BASELINE_SHA` |
| Target environment | **N/A (baseline freeze)** — not a shared/prod cutover |
| Compose file | `docker-compose.prod.yml` / `docker-compose.prod.nginx.yml` (documented) |
| Change ticket / release id | TASK-PLATFORM-SECMIG-P7-003A |
| Operator | Release Manager (baseline freeze) |
| UTC window | 2026-07-30 (documentation freeze) |

## 1. Baseline contents (committed SoT)

| Track | Included |
|---|---|
| P6-001 | ENV-REF-001 + secure config / validator / prod Compose AuthN injection |
| P6-002 | OPS-SEC-RB-001 / OPS-SEC-SEC-001 / OPS-SEC-AUD-001 |
| P6-003 | OPS-BAK / OPS-RST / OPS-DR / OPS-RCV + DEV restore evidence notes |
| P6-004 | REL-SEC-001 / REL-APR-001 / REL-EVID-001 |
| P6-005 | Hub precedence REL-SEC-001 → DEP-CHK-V1 → START-CHK-001 |
| P6-006 / P7-001 / P7-002 | PRR + Final Certification records |
| P7-003A | This baseline freeze commit + tag |

## 2. Integrity statement

| Check | Result |
|---|---|
| Working tree clean at tag | Required after freeze commit |
| Evidence SHA == tagged commit | **Yes** — SHA above must match `git rev-parse secmig-p6-baseline^{commit}` |
| REL-SEC-001 overall for shared/prod | **NO-GO** (not executed as cutover; recovery shared still open) |

## 3. Related

- `docs/releases/SEC_MIG_FINAL_CERTIFICATION_v1.0.md` (SEC-MIG-CERT-001)
- `docs/releases/PRODUCTION_READINESS_REVIEW_v1.0.md` (SEC-MIG-PRR-001)
- `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` (REL-SEC-001)
- `16 Release Management/ECMP_Git_Tag_Convention_v0.1.md` (REL-TAG-001) — product SemVer tags remain separate; this tag follows the SEC-MIG milestone pattern (`secmig-phase-5`)

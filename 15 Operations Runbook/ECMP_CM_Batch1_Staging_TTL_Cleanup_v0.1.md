# ECMP — CM Batch-1 Staging TTL Cleanup (Mode A ops)

| Field | Value |
|---|---|
| Document ID | OPS-CM-B1-STG-001 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Status | 🟢 Active (Mode A) |
| Related | FR-004 / BR-012; `AttachmentConfig.staging_ttl_hours` (default 24); M6 Mode A |
| Mode B | **CLOSED** — this procedure does not unlock Enterprise integration |

---

## Purpose

Menjaga evidence staging Complaint Batch-1 tetap sehat:

1. **Probe** writable attachment storage (blob root) — tanpa storage writable, FR-004 create staging gagal.
2. **Void abandoned staging** setelah TTL — logical void (`abandoned_staging_ttl`), bukan physical delete.

Tidak menambah OpenAPI route. Operator memakai script lokal/CI ops.

---

## Prerequisites

- Working directory: `backend/`
- Env DB + settings yang sama dengan runtime Mode A (`.env` / Compose)
- `LOG_FORMAT=json` disarankan di shared/staging agar cleanup muncul di log shipping

---

## Commands

```bash
cd backend
python scripts/cm_batch1_ops_hygiene.py probe-storage
python scripts/cm_batch1_ops_hygiene.py void-abandoned-staging
# atau keduanya:
python scripts/cm_batch1_ops_hygiene.py all
```

Exit codes: `0` OK; `2` storage probe failed.

Structured log (JSON) dari `void_abandoned_staging` memuat `expiredSessions`, `voidedAttachments`, `ttlHours`.

---

## Cadence (suggested)

| Environment | Cadence |
|---|---|
| Local lab | On demand after long create-session tests |
| Shared / SIT | Daily or via ops cron when host capacity allows |
| Production cutover | Only under REL-SEC + ops schedule — not authorized by this doc alone |

Remote shared-env **re-drill** (C-K4-4) tetap terpisah — bukan bagian script ini.

---

## Explicitly out of scope

| Item | Why |
|---|---|
| TD-OPS-002 agent/viewer password drift | Deferred by Architecture / BMR — not Complaint FR-004 |
| Mode B Identity Adapter / SSO | C-B6-1 CLOSED |
| New public HTTP maintenance API | Catalog-first; use script until Board/API pack adds one |
| Force-merge dual-SoT | DEC-020 — Retirement DEC required |

---

## Related

- Script: `backend/scripts/cm_batch1_ops_hygiene.py`
- Helper: `backend/app/modules/cm_batch1/ops_hygiene.py`
- Service: `CmBatch1AttachmentService.void_abandoned_staging`
- Mode A priority: `18 Architecture Governance/ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md`

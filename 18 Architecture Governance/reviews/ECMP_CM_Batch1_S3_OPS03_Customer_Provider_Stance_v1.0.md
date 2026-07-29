# ECMP CM Batch 1 — CUSTOMER_PROVIDER Environment Stance

| Field | Value |
|---|---|
| Document ID | GOV-S3-CM-B1-OPS03-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete |
| Epic | EPIC-CM-B1-OPS |
| Task | TASK-OPS-03 |
| Related | EX-A / EX-B in `ECMP_CM_Batch1_S3_Release_Exception_Pack_v1.0.md` |

## Binding stance

| Environment class | `CUSTOMER_PROVIDER` | Allowed? |
|---|---|---|
| Local Compose / lab / synthetic UAT | **`stub`** | **Yes** — default |
| Staging with synthetic customers | **`stub`** | **Yes** |
| Any environment claiming real Customer Master data | `stub` | **No** for that claim |
| Any environment | **`enterprise`** | **No** until Enterprise HTTP adapter epic is Architecture-approved |

## Runtime behaviour (unchanged)

- `stub` — in-memory synthetic seed (`CUST-10001`, …); ADR-002 read-only
- `enterprise` — skeleton adapter; lookups return **UNAVAILABLE**; create/search fail closed when `strict_master=True`

ECMP remains **not** Customer Master SoR.

## Changes delivered

| Artifact | Change |
|---|---|
| `docker-compose.yml` | Explicit `CUSTOMER_PROVIDER=${CUSTOMER_PROVIDER:-stub}` |
| `docker-compose.prod.yml` | Same default + EX-A comment |
| `.env.example` | Documented required stance |
| `.env.production.example` | Documented stub default; enterprise URL commented |

No FRD / OpenAPI / Event Catalog / migration changes. No Enterprise HTTP invented.

---

*End of GOV-S3-CM-B1-OPS03-001.*

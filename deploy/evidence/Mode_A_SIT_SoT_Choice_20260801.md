# Mode A SIT — SoT Choice (under DEC-020)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Status | Binding for Mode A lab SIT planning |
| Parent | DEC-020, DEC-021 |

## Choice (no merge)

| Concern | Exercise in SIT | Why |
|---|---|---|
| Frozen lifecycle contract (API-003/004/005, 409, FR-020, outbox) | `implementation/backend` | Matches `case-service.v1.yaml` + DEC-006 |
| Live lab operator UX / edge | `backend/` on VPS (`/api/v1/complaints`, health, Caddy) | What users hit today; dual coexistence |
| CM Batch-1 aggregate | `/api/v1/cm` when in scope of Batch-1 stories | FRD-CM-001 — separate from case-service IDs |
| Customer 360 | **Skip** | ACR-002 deferred |
| Mode B SSO | **Skip** | Board C-7 |

## Rule

Defects filed against the wrong tree are **invalid** until remapped. Do not “fix” VPS by copying sprint routes without a Cutover DEC.

## Next when collapsing trees

Requires future Retirement / Cutover DEC — out of this memo.

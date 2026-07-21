# 23 Assets


| Field | Value |
|---|---|
| ID | AST-000 |
| Version | 0.2 |
| Owner | Solution Architect |
| Reviewer | UX Lead |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Menyimpan source aset visual dan diagram. Jangan hanya menyimpan hasil export.

## Owner
- Document Owner: Solution Architect / UX Lead

## Status
Draft

## Structure
- `mermaid/` — Mermaid sources (`.mmd` / `.md`) — **aktif** (satu-satunya folder berisi aset saat ini; lihat Asset Index)
- `drawio/` — Draw.io sources (`.drawio`) — *reserved, belum ada aset; folder disiapkan*
- `plantuml/` — PlantUML sources (`.puml`) — *reserved, belum ada aset; folder disiapkan*
- `icons/` — icon packs used by docs/UI references — *reserved, belum ada aset; folder disiapkan*
- `logo/` — brand/logo assets — *reserved, belum ada aset; folder disiapkan*
- `exports/` — PNG/SVG/PDF generated from sources — *reserved, belum ada aset; folder disiapkan*

## Rules
1. Source of truth = file di folder source (drawio/plantuml/mermaid).
2. Export boleh ada, tapi harus bisa di-regenerate dari source.
3. Link diagram dari Domain/Solution Architecture ke file source di sini.

## Asset Index
| Asset | Type | Description | Used by |
|---|---|---|---|
| `mermaid/ecmp-lifecycle.mmd` | Mermaid flowchart | Lifecycle dokumen/delivery ECMP | `../ai/09_workflow.md` |
| `mermaid/case-state-machine.mmd` | Mermaid stateDiagram | Baseline Case state machine (Workflow Config awal) | `../20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003) |
| `mermaid/ecmp-context.mmd` | Mermaid flowchart (C4-style context) | Context ECMP: internal users, 7 domain, Customer Master read-only, Email Gateway opsional, event backbone/outbox | `../20 Domain Architecture/README.md`, SA §3 (`../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`) |
| `mermaid/ecmp-container.mmd` | Mermaid flowchart (container view) | Container view 7 domain + event backbone (outbox, ADR-009) + Customer Master eksternal + gateway opsional; arah dependensi per tabel SA §4 | SA §4 (`../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`) |
| `mermaid/create-case-sequence.mmd` | Mermaid sequenceDiagram | Sequence create case Sprint-01 nyata: CS → `POST /v1/cases` → validasi → stub CM → transaksi tunggal (cases + audit_log + outbox EVT-001) → 201; FR-001c/ADR-009 | SA §5 (`../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`) |
| `mermaid/deployment-dev-ci.mmd` | Mermaid flowchart (deployment view) | Deployment DEV (developer + compose Postgres + uvicorn) dan CI GitHub Actions (ruff → contract → alembic → pytest + Postgres service) per `backend-ci.yml` | SA §9 (`../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`), `../14 Deployment Standards` |

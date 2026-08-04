# CWX-M4 — Operational History

| Field | Value |
|---|---|
| Document ID | CWX-M4 |
| Status | 🔒 LOCKED (specification) · READY slices DELIVERED (FE Mode A) · Audit BLOCKED |
| Epic | EPIC-CW-001 |
| Parent | CWX-M3 / CWX-M2 / CWX-M1 / CWX-000 |
| Category | GOV-001 Category B — Specification |
| Date | 2026-08-03 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → GOV-001 → CWX-000 → M1 → M2 → M3 → **CWX-M4** |
| Implementation | DELIVERED (READY) — History Shell · Navigation · Foundation Activity Feed · Decision History (Foundation + Aggregate). Audit Summary **BLOCKED** (not implemented). Aggregate Activity Feed **BLOCKED** (not composed). |

---

## Objective

Menjawab *"Apa yang sudah terjadi?"* di Case Workspace melalui **Operational History** — presentasi baca saja di atas capability native existing. Extend M1–M3; bukan redesign Timeline, bukan SoR audit baru, bukan Mode B.

## Dual-SoT

```
Operational History (CWX-M4)
        │
   ┌────┴────┐
   ▼         ▼
Foundation           Aggregate
/api/v1/complaints   /api/v1/cm
Activity: TimelineCard   Activity Feed: BLOCKED
Decision: resolution     Decision: resolutionHistory
Audit: BLOCKED           Audit: BLOCKED
```

No silent merge. No API-209 dari Case Aggregate. No rewrite Timeline storage.

## In Scope

- Operational History Shell (presentation)
- History Navigation (controlled tabs: Activity · Decisions · Audit)
- Activity Feed Surface — **Foundation only** (compose `TimelineCard`)
- Decision History Surface — Foundation resolution fields + Aggregate `resolution` / `resolutionHistory`
- Dokumentasi capability **BLOCKED** (Aggregate Activity Feed · Audit Summary) sebagai larangan implementasi

## Out Of Scope

- Audit Summary UI / client baru  
- Aggregate Activity Feed / pemanggilan timeline Foundation dari Aggregate  
- CAP-010 timeline merge  
- Timeline redesign / storage redesign  
- Conversation · Internal Notes · Decision Notes  
- Backend / OpenAPI / DB / Auth changes  
- Mode B / SSO / Identity Adapter  
- Routing History / query persistence  

## Capability Matrix

| Capability | Canonical source | Status | Notes |
|---|---|---|---|
| History Shell | CWX-000 · CWX-R | READY | `CwxOperationalHistoryShell` |
| History Navigation | CWX-M4 UX | READY | `CwxHistoryNavigation`; Audit tab hideable |
| Foundation Activity Feed | API-209 / `TimelineCard` | READY | Compose via `CwxActivityFeedSurface` children |
| Aggregate Activity Feed | — | **BLOCKED** | Tidak ada timeline API Mode A pada `/api/v1/cm` |
| Decision History (Foundation) | Existing resolution payload | READY | Presentation only; bukan Decision Notes |
| Decision History (Aggregate) | `resolution` / `resolutionHistory` | READY | Parent owns data |
| Audit Summary | API-336/337 (katalog) | **BLOCKED** | Gate: no new API calls; FE Mode A belum punya client/payload audit di parent |

## Components (FE)

| Component | Role |
|---|---|
| `CwxOperationalHistoryShell` | Landmark + framing + children |
| `CwxHistoryNavigation` | Controlled tabs; `audit.visible: false` hides Audit |
| `CwxActivityFeedSurface` | Presentation shell; children = native timeline |
| `CwxDecisionHistorySurface` | Presentation shell; children = resolution presentation |

**Parent Owns SoT:** `ComplaintDetailView` (Foundation) · `CaseDetailView` (Aggregate). Shells never fetch / mutate / branch SoT.

## Wiring (implemented reality)

| Surface | Foundation | Aggregate |
|---|---|---|
| History Shell + Nav | Wired; `audit={{ visible: false }}` | Wired; `audit={{ visible: false }}` |
| Activity | `TimelineCard` inside Activity Feed Surface | **Not composed** (BLOCKED) |
| Decisions | Resolution fields existing | `resolutionHistory` / resolution cards |
| Audit | Tab hidden | Tab hidden |

## Acceptance Criteria (READY only)

1. History menjawab *What has already happened?* tanpa meninggalkan Workspace.  
2. Foundation Activity memakai `TimelineCard` existing — tidak fork.  
3. Decision History hanya dari data resolution existing — bukan Decision Notes.  
4. Aggregate Activity Feed tidak diisi palsu dari API Foundation.  
5. Audit tab tidak ditampilkan selama Audit BLOCKED.  
6. Tidak ada endpoint OpenAPI baru; tidak ada perubahan backend/DB.  
7. Dual-SoT intact (DEC-020). Mode B tidak disentuh.  

## Definition of Done (READY)

1. Shell + Nav + Foundation Feed + Decision History (kedua SoT) ter-compose.  
2. Panel BLOCKED tidak diimplementasikan.  
3. Parent Owns SoT · Child Owns Lifecycle · Compose Never Fork.  
4. CWX-R relevan dapat dievaluasi (Activity penuh hanya Foundation).  

## Explicitly Deferred (not debt)

Aggregate Activity Feed · Audit Summary · CAP-010 merge · Timeline redesign · Mode B — lihat `ECMP-EPIC-CW-001-CLOSURE.md` §7 / §11.

## References

| Artefak | Path / ID |
|---|---|
| CWX-000 … M3 · R | `docs/governance/ECMP-CWX-*.md` |
| Closure | `docs/governance/ECMP-EPIC-CW-001-CLOSURE.md` |
| GOV-001 | `docs/governance/ECMP-GOV-001.md` |
| DEC-020 | Dual-SoT coexistence |
| Mirror | `18 Architecture Governance/ECMP_CWX_M4_Operational_History_v1.0.md` |

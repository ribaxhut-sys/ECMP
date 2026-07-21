# Domain Architecture — Channel

| Field | Value |
|---|---|
| ID | DOM-CH-001 |
| Version | 1.0 |
| Owner | Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline — boundary only) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Status
Boundary / Future — **out of scope** untuk ECMP core build (lihat OQ-001 di `../../27 Project Decisions/OPEN_QUESTIONS.md`: fase Channel app belum diputuskan).

## Bounded Context
Folder ini hanya menangkap **integration boundary**: bagaimana channel eksternal (di masa depan) submit/consume case interactions. Tidak ada komponen, data ownership, atau flow internal yang dimodelkan sampai OQ-001 diputuskan.

## Boundary Notes
- Intake dari channel eksternal akan masuk via API resmi ECMF (katalog `../../07 API Catalog`) — tidak ada jalur tulis langsung ke data case.
- Field `channel` pada Case (CALL, EMAIL, BRANCH — FRD-001 §7) adalah atribut pencatatan asal, bukan bukti adanya domain Channel aktif.

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- OQ-001: apakah Channel app masuk fase 1 atau hanya integration boundary? (Open, owner: Business Owner)

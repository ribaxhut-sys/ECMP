# Domain Architecture — CRM

| Field | Value |
|---|---|
| ID | DOM-CRM-001 |
| Version | 1.0 |
| Owner | CRM PO / Solution Architect |
| Reviewer | BA Lead |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Customer 360 view: menggabungkan data master pelanggan (read-only dari Customer Master eksternal) dengan konteks interaksi dan case dari ECMP.

## Bounded Context
- **Konteks:** Customer 360 & Interaction. CRM adalah *downstream context* dari Customer Master eksternal dengan pola **anti-corruption layer + cache read-only** (ADR-002, INT-001 di `../../09 Integration Catalog/`).
- **ECMP BUKAN Customer Master System of Record** (ADR-002, BR-CRM-01 → delivery BR-003). Cache read-only untuk performa diperbolehkan; write-back dilarang. Perubahan data master hanya via integrasi resmi ke sistem master (BR-CRM-04).
- **Ubiquitous language:** Customer Reference, Contact Channel, Interaction History, Related Cases, Customer Notes.

## In Scope
- Customer search & verification
- Profile view (Customer 360)
- Interaction history — interaksi penting wajib tertaut Customer ID (BR-CRM-03)
- Related cases linkage (referensi ke Case Header milik ECMF)
- Customer notes

## Out of Scope
- Menjadi customer master system of record (ADR-002)
- Write-back ke Customer Master
- Edit data master pelanggan dari ECMP

## Key Components
| Komponen | Tanggung jawab |
|---|---|
| Customer Master Adapter (ACL) | Anti-corruption layer: translasi model eksternal → Customer Reference internal; INT-001 |
| Customer Reference Cache | Cache read-only + `last_synced_at` wajib ditampilkan ke user (ADR-002) |
| Interaction Service | Catat interaksi tertaut Customer ID (BR-CRM-03) |
| Customer 360 View | Komposisi profil + interaction history + related cases |

## Key Flows
1. **Search → Verify → View 360 → Open/Link Case → Add Interaction Note** (alur utama CS).
2. **Customer lookup untuk ECMF (Sprint-01):** validasi keberadaan `customerId` bila integrasi tersedia; **stub mode** menerima customerId non-kosong dan menandai `customerVerified=false` (FRD-001 §8).
3. **Sync Customer Reference:** mekanisme (event vs scheduled pull) diputuskan saat integrasi Customer Master nyata — lihat Open Questions.

## Data Ownership
| Entity | Ownership | Catatan |
|---|---|---|
| Customer Reference, Contact Channel | Customer Master (eksternal) — ECMP hanya cache read-only | ADR-002; wajib tampilkan `last_synced_at` |
| Interaction History, Customer Notes | CRM (ECMP native) | PII — akses need-to-know (BR-CRM-02) |
| Related Cases | Referensi ke ECMF (Case Header) | CRM tidak memiliki data case |

## Integrations
- **Customer Master (read-only):** INT-001 — Sprint-01 stub read-only; sinkronisasi nyata dibatasi sampai integrasi CM tersedia (SA "Open Decisions" #3).
- **ECMF:** menyediakan customer reference untuk case create; menerima linkage related cases.
- **Events produced:** tidak ada (baseline).
- **Events consumed:** tidak ada (baseline) — Related Cases dibaca via query/projection, bukan subscription formal di events.yaml.

## NFR Considerations
- Akses data pelanggan mengikuti role + need-to-know (BR-CRM-02); baseline DEC-004: phone/email dimask untuk role non-CS.
- Data PII: masking rule menunggu review Compliance (lihat `../../06 Data Dictionary`).

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Mekanisme sinkronisasi Customer Reference (event push vs scheduled pull) — diputuskan saat integrasi Customer Master nyata (SA "Open Decisions" #3).
- Definisi ambang interaksi "penting" vs ringan (BR-CRM-03) — **ditutup** baseline DEC-004: interaksi tertaut case wajib dicatat; interaksi ringan tanpa case tidak wajib.
- Daftar field yang dibatasi per role (BR-CRM-02) — **ditutup** baseline DEC-004: kontak pelanggan (phone/email) dimask untuk role non-CS.

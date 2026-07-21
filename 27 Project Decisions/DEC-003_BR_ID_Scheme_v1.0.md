# Decision Record — Single Business Rule ID Scheme for Delivery

| Field | Value |
|---|---|
| ID | DEC-003 |
| Version | 1.0 |
| Owner | BA Lead |
| Reviewer | Solution Architect / PMO |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- Type: Project Decision (non-ARB)
- Status: Accepted
- Date: 2026-07-21
- Owner: BA Lead
- Participants: Architecture Review Board, PMO

## Context
Dua skema ID Business Rule hidup berdampingan:
- **Skema delivery** `BR-001…BR-007` — dipakai FRD-001, Sprint-01, traceability, dan kode.
- **Skema enterprise** `BR-<Domain>-NN` (mis. `BR-ECMF-01`) — dipakai `ECMP_Business_Rules_v1.0.md` (Draft).

Header dokumen enterprise juga memakai `ID | BR-001` yang bentrok dengan rule delivery BR-001.

## Decision
1. **SoT untuk implementasi/tes/traceability = skema delivery `BR-0xx`** (`02 Business Rules/ECMP_Business_Rules_Sprint01_v0.1.md` dan penerusnya). Kode, PR, tes, dan traceability hanya boleh mengutip `BR-0xx`.
2. Katalog enterprise `BR-<Domain>-NN` tetap sebagai katalog referensi kebijakan; ID dokumennya diganti `BR-CAT-001` untuk menghilangkan bentrok.
3. Tabel pemetaan alias dipelihara di `ECMP_Business_Rules_v1.0.md` (bagian "Pemetaan ke ID Delivery"). Saat rule enterprise diangkat ke delivery, ia menerima `BR-0xx` baru.

## Mapping (baseline 2026-07-21)
| Delivery | Enterprise | Catatan |
|---|---|---|
| BR-001 | BR-ECMF-03 | Status via workflow config; initial REGISTERED |
| BR-002 | BR-ECMF-02 | Assignment role/unit (Planned) |
| BR-003 | BR-CRM-01 / BR-CRM-04 | Customer master read-only |
| BR-004 | BR-NOTIF-01 | Event/notification opt-in |
| BR-005 | BR-ECMF-05 | SLA otomatis (Planned) |
| BR-006 | BR-DASH-01 / BR-DASH-04 | Dashboard role+org scoped (Planned) |
| BR-007 | BR-CP-01 / BR-CP-02 | AuthN + permission `cases:*` |
| BR-008 | BR-CP-03 / BR-ECMF-01 | Write-audit wajib (diangkat oleh keputusan ini) |

## Impact
- Impact analysis dan routing AI memakai satu skema.
- `BR-008` (write-audit) ditambahkan ke katalog delivery Sprint-01 karena diwajibkan FRD §9 dan diimplementasikan di G0.

## Follow-up
- [x] Update header + bagian pemetaan `ECMP_Business_Rules_v1.0.md`
- [x] Tambah BR-008 di `ECMP_Business_Rules_Sprint01_v0.1.md` dan traceability
- [x] Tambah OQ-006 Resolved

## Links
- Related: `26 Traceability/traceability.yaml`, FRD-001

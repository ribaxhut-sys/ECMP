# Status Badge Standard

| Field | Value |
|---|---|
| ID | EAR-STD-003 |
| Version | 1.1 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Status Values

| Badge | Status Text | Meaning |
|---|---|---|
| 🟢 | Approved | Baselined / boleh dijadikan acuan implementasi |
| 🟡 | Draft | Masih dikembangkan |
| 🔵 | Under Review | Sedang direview stakeholder |
| 🔴 | Deprecated | Digantikan; disimpan untuk sejarah |

## Item-level Markers

Selain badge status dokumen, ada marker level-item untuk baris/butir **di dalam** dokumen (mis. Test Case Catalog, CASE_AGGREGATE):

| Marker | Arti |
|---|---|
| ✅ Implemented | Item sudah diimplementasikan/diverifikasi di kode atau tes |
| 🕓 Planned | Item direncanakan; belum diimplementasikan |

Marker ini berlaku pada baris/item di dalam dokumen, **bukan** pada status dokumen — status dokumen tetap dibatasi pada empat badge di atas. Status free-text komposit (mis. "🟢 ECMF slice Approved; multi-domain Draft") wajib merujuk kosakata standar ini.

## Usage Rules
1. Selalu tulis **badge + teks status** (`🟢 Approved`), jangan hanya emoji.
2. Folder README menampilkan status agregat folder.
3. Perubahan `Draft → Under Review → Approved` mengikuti approval path.
4. Deprecated wajib menunjuk dokumen pengganti (ID + link).
5. **Lifecycle ADR vs badge:** ADR memiliki lifecycle resmi (PROGRAM-ADR-002 BR-001): `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, `DEPRECATED`, `REJECTED` — ditulis di **badan dokumen** (baris `ADR Status:`). Tabel metadata tetap memakai empat nilai badge di atas; lifecycle `ACCEPTED` dipetakan ke badge `🟢 Approved`. Badan dokumen = otoritatif untuk lifecycle; tabel metadata = otoritatif untuk badge repo.
6. **Lifecycle Architecture Documents vs badge:** dokumen arsitektur non-ADR (PROGRAM-ADR-002 BR-002): `DRAFT`, `REVIEW`, `BASELINE`, `ARCHIVED`. Pemetaan: `DRAFT`→`🟡 Draft`; `REVIEW`→`🔵 Under Review`; `BASELINE`→`🟢 Approved` / `🟢 BASELINE`; `ARCHIVED`→`🔴 Deprecated` (atau pointer archived). Board disposition di luar lifecycle ADR (mis. *Needs Revision*) dicatat di index/metadata referensi — **bukan** status lifecycle ADR baru.

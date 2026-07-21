# ECMP Integration: Customer Master Real Mode — Requirement Sheet / RFI (INT-001A)

| Field | Value |
|---|---|
| ID | INT-001A |
| Version | 0.1 |
| Owner | Integration Lead |
| Reviewer | Solution Architect, CRM Domain PO, Security |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

> **Sifat dokumen: input negosiasi (requirement sheet / RFI), BUKAN kontrak final.** Pihak eksternal (tim Customer Master) belum tersedia untuk menegosiasikan kontrak. Dokumen ini menutup Open Items INT-001 dari sisi kebutuhan ECMP, agar begitu akses ke tim Customer Master terbuka, negosiasi bisa langsung dimulai. Hasil negosiasi yang disepakati akan dibakukan sebagai **INT-001 v0.2** (kontrak mode real); dokumen ini kemudian ditandai selesai/deprecated.

## Purpose
Mendefinisikan apa yang ECMP **butuhkan** dari Customer Master agar INT-001 dapat naik dari mode stub ke mode real: field minimum, non-fungsional, auth, error semantics, environment uji, checklist onboarding, dan daftar pertanyaan terbuka.

Konteks tetap: ECMP bukan SoR pelanggan (ADR-002); akses **read-only**, tanpa write-back (BR-003).

## 1. Field Minimum yang ECMP Butuhkan
Kebutuhan konsumen: validasi existence saat `POST /v1/cases` (API-001) dan Customer 360 read-only (API-010, planned — FRD-003).

| Field (nama ECMP) | Tipe | Wajib | Kegunaan di ECMP |
|---|---|---|---|
| `customerId` | string | Ya | Kunci referensi; validasi existence saat create case; identifier di Customer Reference cache |
| `fullName` | string | Ya | Konteks penanganan case; tampilan Customer 360 |
| `contactChannels[]` | array of {type, value} | Ya | Kontak pelanggan (phone/email/dll.) untuk Customer 360; di-mask untuk role non-CS (BR-CRM-02) |
| status aktif (mis. `isActive` / `status`) | boolean/enum | Ya | Membedakan pelanggan aktif vs nonaktif saat registrasi case dan tampilan 360 |

Catatan:
- Nama field di atas adalah kebutuhan ECMP; **penamaan/skema aktual mengikuti kontrak Customer Master** — mapping didefinisikan saat negosiasi (INT-001 v0.2) dan dicatat di `06 Data Dictionary` (Customer Reference).
- Field tambahan (segmen, alamat, dsb.) tidak diminta pada fase ini — prinsip minim-PII: ECMP tidak menyimpan PII melebihi kebutuhan cache (`10 Security and Access Standards`).

## 2. Kebutuhan Non-Fungsional

| Aspek | Kebutuhan ECMP | Dasar |
|---|---|---|
| Response time / timeout | ECMP memutus panggilan pada **3 detik**; respons yang diharapkan jauh di bawah itu (indikatif p95 < 500 ms — dikonfirmasi saat negosiasi) | INT-001 (SLA timeout 3s per call) |
| Availability yang diharapkan | Cukup untuk jam operasional CS; ECMP **tetap beroperasi saat CM down** via fallback unverified (availability > verification), sehingga tidak menuntut HA ekstrem — angka target dikonfirmasi dengan tim CM | INT-001 (fallback mode real) |
| Rate limit | ECMP butuh kuota untuk pola on-demand per create case + retrieval Customer 360; volume aktual belum terukur (belum ada beban produksi) — ECMP meminta info limit CM dan akan menyesuaikan (cache read-only mengurangi frekuensi call) | ADR-002 (cache), INT-001 (frequency/trigger) |
| Konsistensi data | Data boleh eventual (cache + `last_synced_at`); ECMP tidak butuh strong consistency | ADR-002 |

## 3. Kebutuhan Autentikasi (kandidat — belum diputuskan)
Kredensial harus **read-only** dan machine-to-machine. Kandidat yang bisa ECMP dukung (urutan preferensi):

1. **OAuth2 client-credentials** — preferensi bila CM punya authorization server; scope read-only khusus.
2. **Service account + API key/mTLS** — alternatif bila OAuth2 tidak tersedia.

Keputusan final mengikuti kapabilitas Customer Master; apapun pilihannya: kredensial per environment (sandbox vs produksi terpisah), rotasi kredensial terdefinisi, dan tidak ada kredensial di source repo (env/secret store — selaras praktik ADR-007 untuk token dari environment).

## 4. Error Semantics yang Diharapkan
ECMP membutuhkan pembedaan minimal berikut agar fallback INT-001 bekerja benar:

| Kondisi | Semantik yang diharapkan dari CM | Perilaku ECMP (per INT-001) |
|---|---|---|
| Customer ditemukan | 200 + payload field §1 | `customerVerified=true` |
| Customer tidak ditemukan | Terbedakan secara eksplisit (mis. 404) — **bukan** error generik | Diputuskan saat negosiasi: tolak create vs terima unverified (pertanyaan terbuka Q3) |
| Auth gagal | 401/403 terbedakan dari not-found | Alert operasional; fallback unverified agar create tidak terblokir |
| Error server / timeout | 5xx / tidak ada respons ≤ 3s | Fallback stub-like: terima `customerId` non-empty, `customerVerified=false`, create lanjut; tanpa retry synchronous |
| Rate limit terlampaui | Terbedakan (mis. 429 + `Retry-After`) | Diperlakukan seperti unavailable (fallback unverified); masukan tuning cache |

Format body error tidak harus mengikuti envelope ECMP; yang wajib adalah **status code yang terbedakan** dan terdokumentasi.

## 5. Kebutuhan Lingkungan Uji (Sandbox CM)
- Sandbox/staging Customer Master yang bisa diakses dari environment SIT/UAT ECMP (keputusan platform: ADR menyusul — lihat `14 Deployment Standards`).
- Dataset uji **sintetis** yang stabil: minimal beberapa `customerId` valid (aktif + nonaktif) dan pola id yang pasti tidak ada (untuk jalur not-found) — dilarang data pelanggan nyata (selaras Test Strategy §5).
- Kredensial sandbox terpisah dari produksi.
- Kemampuan simulasi kegagalan (timeout/5xx) atau setidaknya dokumentasi perilaku error — dibutuhkan untuk menguji fallback INT-001 dan TC-010.

## 6. Checklist Onboarding Integrasi
- [ ] Kontak/PIC tim Customer Master teridentifikasi
- [ ] RFI ini dikirim dan dijawab (lihat §7)
- [ ] Spesifikasi API CM diterima (endpoint, skema, error codes, rate limit)
- [ ] Mapping field CM → Customer Reference disepakati; update `06 Data Dictionary`
- [ ] Skema auth disepakati; kredensial sandbox diterbitkan (secret store, bukan repo)
- [ ] Akses network sandbox CM dari environment ECMP terverifikasi
- [ ] Review Security (PII, retensi cache, masking BR-CRM-02) lulus
- [ ] Kebijakan cache TTL / `last_synced_at` diputuskan (open item INT-001)
- [ ] **INT-001 v0.2 (kontrak mode real) ditulis dan di-approve Architecture Board**
- [ ] Uji integrasi terhadap sandbox lulus (happy path + not-found + timeout fallback)
- [ ] Toggle mode stub → real terdefinisi per environment; rollback plan jelas

## 7. Pertanyaan Terbuka ke Tim Customer Master
1. **Q1 — Kontrak:** Apa endpoint, format id, dan skema respons lookup pelanggan by id? Adakah API pencarian (by name/phone) yang boleh dipakai untuk Customer 360 (FR-010)?
2. **Q2 — Sinkronisasi:** Apakah CM menyediakan event/feed perubahan data pelanggan (untuk sinkron cache), atau ECMP harus scheduled pull? (Open Decision SA #3.)
3. **Q3 — Semantik not-found:** Bila `customerId` tidak ditemukan (bukan sistem down), apakah bisnis ingin create case ditolak atau tetap diterima sebagai unverified? (Butuh keputusan bersama BA/Business Owner — berdampak ke FRD-001 §8.)
4. **Q4 — Auth:** Skema auth apa yang didukung untuk konsumen M2M read-only (OAuth2 client-credentials / API key / mTLS)? Bagaimana proses penerbitan & rotasi kredensial?
5. **Q5 — NFR:** Berapa SLA availability & latency resmi CM? Berapa rate limit per client dan bagaimana perilaku saat terlampaui (429? throttle?)?
6. **Q6 — Sandbox:** Apakah tersedia sandbox dengan data sintetis stabil dan simulasi error? Bagaimana proses permintaan akses?
7. **Q7 — PII & compliance:** Adakah pembatasan penyimpanan/caching field kontak di sisi konsumen (retensi, masking, audit akses)?
8. **Q8 — Versioning:** Bagaimana kebijakan versioning/breaking-change API CM, dan berapa lead time notifikasi perubahan?

## Related
- `ECMP_INT_001_Customer_Master_Read_v0.1.md` (INT-001) — kontrak berlaku (mode stub); Open Items yang ditutup requirement sheet ini
- `../05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md`
- `../03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` (§8), `ECMP_FRD_CRM_Customer360_v0.1.md` (FR-010)
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` (Customer Reference)
- `../10 Security and Access Standards` (PII, masking BR-CRM-02)
- `../13 Test Strategy/ECMP_Test_Case_Catalog_v0.1.md` (TC-010)

# ECMP Data Retention Policy v0.1

| Field | Value |
|---|---|
| ID | CMP-002 |
| Version | 0.1 |
| Owner | Compliance Officer |
| Reviewer | Security Architect / Data Architect / Legal |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

## 1. Purpose & Status
Baseline retensi data ECMP untuk menutup open item Data Dictionary ("Retention policy untuk Attachment, Customer Notes, Report Snapshot belum ditentukan"). Semua angka di bawah adalah **baseline — konfirmasi Legal/Compliance via DEC**; belum ada mekanisme purging yang diimplementasikan.

## 2. Prinsip
1. **Minimalisasi PII** — data pribadi disimpan hanya selama diperlukan untuk tujuan layanan/audit; klasifikasi PII mengikuti kolom PII `06 Data Dictionary`.
2. **ECMP bukan SoR pelanggan (ADR-002)** — Customer Reference adalah cache read-only; retensi/penghapusannya **mengikuti Customer Master** (master dihapus → cache tidak boleh bertahan melebihi kebutuhan; detail TTL cache menyusul bersama API-010, INT-001 Open Items).
3. **Audit tidak boleh dihapus dalam masa retensi** — `audit_log` append-only (BR-CP-03); retensi panjang, pemusnahan hanya setelah masa retensi habis dan disetujui via DEC.
4. **Retensi dihitung dari titik akhir siklus hidup** (mis. case closed), bukan dari tanggal pembuatan, kecuali dinyatakan lain.

## 3. Baseline Retensi
Semua baris bertanda **(baseline — konfirmasi Legal/Compliance via DEC)**:

| Data | Retensi baseline | Titik mulai hitung | Catatan |
|---|---|---|---|
| Audit Log (`audit_log`) | **7 tahun**; arsip dingin (cold storage) setelah **2 tahun** | Sejak `occurred_at` | Append-only, tidak boleh dihapus selama masa retensi (BR-CP-03); arsip dingin tetap immutable |
| Case (Case Header) + Case Activity | **5 tahun** | Setelah case **closed** | Case belum-closed tidak pernah dipurge |
| Attachment | **2 tahun** | Setelah case **closed** | Menutup [TBD] DD; storage terpisah dari DB |
| Customer Notes | **2 tahun** | Sejak dibuat | Menutup [TBD] DD; PII — kandidat review Legal prioritas |
| Report Snapshot | **1 tahun** | Sejak snapshot dibuat | Menutup [TBD] DD; bisa memuat data pelanggan |
| Outbox (record `published_at` terisi) | **90 hari** | Sejak `published_at` | Record belum-published tidak dipurge (event belum terkirim) |
| Delivery Log (Notification) | **1 tahun** | Sejak pengiriman | Wajib disimpan per BR-NOTIF-03; memuat kontak penerima (PII) |

## 4. Mekanisme
**Status: Planned — belum diimplementasikan.** Tidak ada job purging/arsip di kode Sprint-01.

- Dibutuhkan **job purging/arsip terjadwal** pada fase berikut (pasca Sprint-02), setelah baseline dikonfirmasi via DEC.
- Purging entitas bisnis wajib meninggalkan jejak (aksi purge sendiri tercatat di `audit_log`).
- Arsip dingin `audit_log`: media/platform ditentukan bersama keputusan deployment (`14 Deployment Standards`).
- Sampai mekanisme ada, risiko pertumbuhan data tercatat sebagai gap di `ECMP_Compliance_Control_Matrix_v0.1.md` §5 dan threat model SEC-TM-001 (§2.2 DoS).

## 5. Keterkaitan Data Dictionary Open Items
- Baris DD "Retention policy untuk Attachment, Customer Notes, Report Snapshot belum ditentukan" → **ditunjuk ke baseline dokumen ini** (tetap menunggu konfirmasi Legal).
- Notes entity Attachment ("Perlu kebijakan retensi & scanning"): retensi ditutup baseline ini; **scanning tetap open** (di luar scope dokumen retensi).
- Review Compliance atas klasifikasi PII (DD Open Items) tetap berjalan terpisah.

## Related
- `ECMP_Compliance_Control_Matrix_v0.1.md` (CMP-001)
- `../06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` (Open Items)
- `../05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md`
- `../10 Security and Access Standards/ECMP_Threat_Model_v0.1.md`

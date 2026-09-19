# DEC-030 — Jendela ubah 24 jam pasca-terbit untuk Pengetahuan

| Field | Value |
|---|---|
| ID | DEC-030 |
| Version | 0.1 |
| Owner | Product Owner |
| Status | 🟢 Accepted |
| Date | 2026-08-22 |
| Related | Modul Pengetahuan §17/§23 (LOCKED, disupersede sebagian) · `app/modules/knowledge/service.py` |
| Type | Project Decision (Complaint Module — Pengetahuan) |

---

## 1. Intent

Sebelumnya, begitu Pengetahuan berstatus ACTIVE, `title`/`knowledgeType`/`versionLabel` terkunci permanen (KM §17), sedangkan `documentNumber`/`summary`/`effectiveFrom`/`effectiveTo` tetap bisa diubah **tanpa batas waktu** oleh siapa pun yang memegang `knowledge:manage`. Aturan ini janggal dua arah: koreksi cepat atas identitas (salah ketik judul, salah pilih jenis) tidak bisa diperbaiki tanpa membuat versi baru, sementara field lain bisa diam-diam berubah kapan saja setelah terbit — termasuk berhari-hari kemudian — tanpa pembatasan apa pun.

DEC-030 mengganti aturan itu dengan satu jendela waktu tunggal: **24 jam sejak terbit**, berlaku untuk **semua field** (identitas maupun non-identitas) dan **semua berkas**. Begitu jendela lewat, Pengetahuan terkunci total — perubahan substantif berikutnya wajib lewat versi pengganti (`supersedesKnowledgeId`), bukan edit di tempat.

## 2. Decision

1. Tambah kolom konfigurasi `KNOWLEDGE_EDIT_GRACE_HOURS` (default **24**), dibaca lewat `Settings.knowledge_edit_grace_hours`. Tidak di-hardcode — perubahan durasi bisnis tidak boleh perlu deploy kode.
2. **DRAFT**: tidak berubah — bebas diedit dan berkas bebas diubah, tanpa batas waktu, seperti sebelumnya.
3. **ACTIVE**: bebas diedit dan berkas bebas diubah selama `now < published_at + grace_hours`. Ini mencakup **semua field** — `title`, `knowledgeType`, `versionLabel` termasuk (KM §17 disupersede sebagian: identitas tidak lagi terkunci sejak detik pertama ACTIVE, tapi tetap terkunci begitu jendela lewat).
4. Begitu jendela lewat, ACTIVE terkunci total: update ditolak (`knowledge.edit_window_expired`, 400) dan mutasi berkas ditolak (`knowledge.files_locked`, 409).
5. **ARCHIVED terkunci penuh, tanpa syarat umur.** Mengarsipkan mengakhiri masa edit seketika — tidak relevan apakah baru diarsipkan semenit lalu. `unarchive()` tetap mempertahankan `published_at` asli, jadi unarchive **tidak** membuka jendela baru.
6. **Hapus tetap DRAFT-only**, tidak berubah. Jendela ini melonggarkan *edit*, bukan *unpublish* — Pengetahuan yang salah terbit total diarsipkan, lalu diganti dengan versi baru; tidak pernah dihapus.
7. **Jendela berlaku sama untuk semua pemegang `knowledge:manage`** — Admin Pusat, KaSatPel (MANAGER) Pusat, dan Staff KaSatPel (SUPERVISOR/BRANCH_SUPERVISOR) Pusat. Tidak ada predikat otorisasi baru; ini murni berbasis waktu, bukan peran. Konsekuensi: KaSatPel/Staff KaSatPel yang sebelumnya bisa mengubah `summary`/`documentNumber`/tanggal berlaku tanpa batas waktu, sekarang **ikut terkunci** di jam ke-24 seperti Admin.
8. **Riwayat**: setiap perubahan pasca-terbit (dalam jendela) ditandai `metadata={"postPublish": true, "statusAtChange": ..., "editableUntil": ...}` pada entri audit `KnowledgeUpdated`. FE menampilkan badge "Setelah terbit" pada entri bertanda ini, supaya audit trail membedakan koreksi pasca-terbit dari pengeditan biasa saat DRAFT.
9. **Dua celah jejak berkas ditutup**: (a) menetapkan file PRIMARY pertama kali (tanpa ada primary sebelumnya) kini tercatat sebagai `KnowledgeFilePrimaryChanged`; (b) promosi otomatis file lain menjadi PRIMARY setelah PRIMARY dihapus kini tercatat dengan event yang sama (`reason: "AUTO"`). Sebelumnya kedua perubahan ini terjadi tanpa jejak di riwayat.
10. Response API menambah dua field turunan **dihitung di server**: `editable: boolean` dan `editableUntil: string | null`. FE tidak pernah menghitung ulang dari jam klien.

## 3. Conditions

- North Star tetap: perubahan ini domain Pengetahuan murni, tidak menyentuh integrasi Enterprise.
- Tidak ada migrasi Alembic — `published_at` sudah ada dan sudah ter-index.
- Tidak ada perubahan skema otorisasi (`_KNOWLEDGE_ADMIN_ROLES`/`_KNOWLEDGE_UNIT_ROLES` tetap seperti sebelumnya).

## 4. Acceptance

1. Pengetahuan ACTIVE dapat diubah penuh (termasuk judul/jenis/versi dan berkas) dalam 24 jam sejak `publishedAt`.
2. Setelah 24 jam, PUT apa pun ke Pengetahuan ACTIVE ditolak 400; upload/ganti/hapus berkas ditolak 409.
3. KaSatPel/Staff KaSatPel Pusat dan Admin Pusat diperlakukan identik oleh jendela ini.
4. ARCHIVED selalu ditolak, berapa pun umurnya.
5. Hapus tetap hanya untuk DRAFT.
6. Setiap perubahan pasca-terbit (termasuk perubahan primary file) tercatat di Riwayat dengan penanda "Setelah terbit".
7. `editable`/`editableUntil` di response API dipakai FE untuk menonaktifkan tombol Edit dan menampilkan sisa waktu — tidak ada logika jam dihitung ulang di klien.

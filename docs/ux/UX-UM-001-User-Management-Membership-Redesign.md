# UX-UM-001 — Redesign "User Management" sebagai ECMP Membership List

| Field | Value |
|---|---|
| Document ID | UX-UM-001 |
| Status | Draft — for review by CTO, Product Owner, UI/UX Team, Security Team |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Scope | Layar daftar pengguna ECMP (`UserManagement.tsx` + `DirectoryPeopleList.tsx` + `DirectoryPreviewPanel.tsx`) |
| Reference | [UX-CU-003](UX-CU-003-Create-User-Application-Authorization-Redesign.md) — **LOCKED BASELINE**. Batas domain (§2 di sana) tidak diulang di sini; dokumen ini hanya merujuk. |
| Catatan penulisan dokumen | Tidak ditemukan dokumen desain "User Management" sebelumnya di `docs/ux/` — dicek lewat pencarian menyeluruh nama file dan isi. Dokumen ini karena itu **ditulis baru**, bukan "update" atas dokumen yang sudah ada, meski judul tugas menyebut "Update the existing... design". Tidak ada dokumen kedua yang dibuat sebagai akibatnya — ini satu-satunya artefak baru. |
| Out of scope | Kode. Kapabilitas Enterprise pada batas terkunci UX-CU-003 §2 — tidak dibahas ulang. |

---

## 1. Executive Summary

Layar ini hari ini bernama "Users" dan deskripsinya secara harfiah berbunyi *"Daftarkan anggota
modul, kelola peran, dan **atur ulang kata sandi**"* (`messages/id.json`, kunci
`users.description`). Satu-satunya aksi yang benar-benar tersambung ke UI adalah **Reset
Password** — yang menampilkan password sementara dalam bentuk plaintext, dengan tombol
**Print** (membuka jendela baru dan mencetak password) dan **Copy to clipboard**. Ini adalah
kebalikan tepat dari batas yang sudah dikunci di UX-CU-003: Password adalah milik Enterprise,
bukan ECMP.

Redesign ini menetapkan ulang layar sebagai **daftar keanggotaan ECMP** (siapa yang punya akses
ke modul ini, dengan peran dan unit apa) — bukan direktori kredensial. Temuan yang paling
penting bukan soal penamaan, tapi soal keamanan: **`GET /api/v1/users` tidak membatasi hasil
pada Unit administrator yang memanggilnya** — setiap administrator dengan `users:read` melihat
seluruh anggota lintas unit, tanpa terkecuali. Ini dilaporkan di §8 sebagai gap yang belum
tertutup, sejenis dengan T-1 yang sudah ditutup untuk `users:create`, tapi belum ditutup untuk
jalur baca.

---

## 2. Business Definition

> **Layar ini menampilkan hanya Enterprise User yang sudah diberi akses ECMP — bukan seluruh
> pegawai Enterprise.**

Ini sudah **benar** di kode hari ini, terverifikasi dari sumber datanya: `UserManagement.tsx`
memanggil `fetchUsers()` → `GET /api/v1/users`, yang membaca tabel `users` milik ECMP
(`backend/app/modules/users/repository.py`) — **bukan** `moduleUserCandidates.json` (Mock
Enterprise Directory yang dipakai `CreateUserModal`, UX-CU-003 §5.1). Dua sumber data ini
sudah terpisah dengan benar; tidak ada perbaikan yang dibutuhkan pada titik ini. Yang perlu
diperbaiki adalah **framing dan field yang ditampilkan**, bukan sumber datanya.

---

## 3. Repository Findings (ringkas — bukti untuk §4–§8)

| Temuan | Bukti |
|---|---|
| Deskripsi layar masih menyebut "atur ulang kata sandi" | `messages/id.json` kunci `users.description` |
| Satu-satunya aksi yang tersambung ke UI adalah Reset Password | `UserManagement.tsx:216-263`, dipanggil dari `DirectoryPeopleList.tsx:147-163` dan `DirectoryPreviewPanel.tsx:149-164` |
| Reset Password menampilkan plaintext + Print + Copy | `UserManagement.tsx:49-98` (`printTemporaryPassword`), `254-263` (`copyTemporaryPassword`), modal `495-560` |
| Kolom Unit menampilkan **UUID mentah terpotong**, bukan nama Unit | `directoryHelpers.ts:68-75` (`formatBranch`) — hanya memotong string `branchId`, tidak pernah me-resolve ke `Branch.code`/`name` |
| Tidak ada aksi Edit Membership di UI | Tidak ada `EditUserModal` atau setara di `frontend/src/features/users/` |
| Backend **punya** endpoint Activate/Deactivate, UI tidak memanggilnya | `PATCH /users/{id}/status` ada (`users/router.py:170-183`); tidak dipanggil dari `UserManagement.tsx`/`DirectoryPeopleList.tsx`/`DirectoryPreviewPanel.tsx` |
| `GET /api/v1/users` tidak menegakkan scope Unit administrator | `users/router.py:116-140` — `principal` diterima lalu dibuang (`_ = principal`); tidak ada `enforce_org_scope`/`require_data_scope` |
| `PATCH /users/{id}/status` juga tidak menegakkan scope Unit, dan tidak mencegah self-deactivation | `users/service.py:341-360` (`update_status`) |
| Pencarian & filter beroperasi murni di atas hasil `GET /users` (keanggotaan ECMP) | `directoryHelpers.ts:142-174` (`matchesDirectoryFilter`, `matchesDirectorySearch`) — tidak menyentuh `moduleUserCandidates.json` |
| Tidak ada fitur "Unlock Account" atau "Email User" di repo mana pun | Dicek menyeluruh — tidak ditemukan, tidak ada yang perlu dihapus |

---

## 4. Display — Field Analysis

### 4.1 Field yang ditampilkan hari ini

| Field (kode saat ini) | Ada di repo? | Keputusan | Justifikasi bisnis |
|---|---|---|---|
| `username` (ditampilkan sebagai "@username") | Ya | **RENAME** → Employee ID | Ini **bukan** dua field terpisah (Username vs Employee ID) — keduanya kolom `User.username` yang sama, hanya label yang salah. UX-CU-003 §3.2 sudah menetapkan `username` = Enterprise User Reference (ID Pegawai 16 digit). Instruksi "Remove Username (if not business-relevant)" tidak berlaku di sini karena field ini **sangat** business-relevant — ia bukan kredensial, ia adalah kunci rujukan ke Enterprise User. |
| `fullName` | Ya | **KEEP** | Identitas yang perlu dikenali administrator saat memindai daftar |
| `email` | Ya (opsional toggle) | **REMOVE** | Sesuai instruksi eksplisit. Konsekuensi yang harus dinyatakan: `matchesDirectorySearch` hari ini juga mencocokkan `email` — menghapus kolom email dari tampilan sebaiknya diikuti menghapusnya dari pencocokan pencarian juga (§7), atau cakupan pencarian mengecil secara diam-diam. |
| `roleCode`/`roleName` (badge kategori) | Ya | **KEEP** | Inti dari "siapa boleh apa" — data otorisasi ECMP |
| `branchId` (badge "Branch"/"Head Office" + UUID terpotong) | Ya (nilainya) | **KEEP, tapi perbaiki**: nilainya ada di repo (`User.branch_id`), namun render-nya rusak — `formatBranch` memotong UUID mentah, tidak pernah me-resolve ke nama Unit. Administrator hari ini **tidak bisa** membedakan Unit satu dari Unit lain hanya dari melihat daftar ini. | Field "Unit" yang diminta KEEP hanya terpenuhi setengah: datanya ada, tampilannya tidak berguna. |
| `isActive` (badge Aktif/Nonaktif) | Ya | **KEEP** | Status keanggotaan ECMP — persis field yang diminta |
| `createdAt` | Ya (hanya di Preview Panel, sebagai "Created") | **KEEP** | Diminta eksplisit; sudah ada, hanya perlu konsisten ditampilkan (hari ini hanya di panel detail, tidak di daftar) |
| `updatedAt` | Ya | **KEEP** | Diminta eksplisit; sudah ditampilkan di kedua tempat |
| `lastLoginAt` ("Last login") | Ya | **Tidak termasuk KEEP yang diminta** | Ini sinyal aktivitas autentikasi (kapan pengguna login), bukan data keanggotaan. Direkomendasikan dipindah keluar dari tampilan utama — lihat §4.2. Bukan "Authentication field" yang menyimpan kredensial, jadi tidak seketat Password; tetap direkomendasikan dihapus karena tidak ada di daftar KEEP yang disetujui dan bukan data yang ECMP putuskan. |
| `password` / `temporaryPassword` (hasil Reset Password) | Ya (di respons `admin_reset_password`) | **REMOVE dari UI** — field ini sendiri tetap ada di backend (di luar cakupan dokumen ini untuk diubah), tetapi **tidak boleh ditampilkan** di layar ECMP manapun | Kredensial — milik Enterprise per batas terkunci |

### 4.2 Field yang direkomendasikan TIDAK ditambahkan

Tidak ada field baru yang diciptakan. `Organization`, `Department`, `Position` sudah
ditetapkan tidak ada di repo (UX-CU-003 §5.1, §10.1) — kesimpulan yang sama berlaku di sini,
tidak diulang.

---

## 5. Actions

| Aksi | Status hari ini | Keputusan |
|---|---|---|
| **View Membership** | Ada — klik baris membuka Preview Panel | **KEEP**, rename judul panel dari "User details" (`t("previewTitle")`) menjadi bahasa keanggotaan bila diperlukan (perubahan teks, bukan struktur) |
| **Edit Membership** | **Tidak ada** — tidak ditemukan `EditUserModal` atau setara | **Gap** — direkomendasikan dibangun (ubah Peran/Unit/Status pengguna yang sudah terdaftar), tapi ini **implementasi baru**, bukan yang bisa "di-keep/remove" dari yang sudah ada. Dilaporkan di §9, tidak dirancang detailnya di sini (di luar cakupan "review layar yang ada") |
| **Activate** | Backend ada, **UI tidak memanggilnya** | **KEEP secara desain** — sambungkan UI ke endpoint yang sudah ada. Reuse murni, bukan fitur baru (§9) |
| **Deactivate** | Backend ada, **UI tidak memanggilnya** | Sama seperti Activate |
| **Reset Password** | Ada dan aktif — plaintext + Print + Copy | **REMOVE total**: tombol di `DirectoryPeopleList.tsx`, tombol di `DirectoryPreviewPanel.tsx`, dua modal konfirmasi di `UserManagement.tsx`, fungsi `printTemporaryPassword`, `copyTemporaryPassword` |
| **Forgot Password / Change Password** | Tidak ada di layar ini (ada di layar terpisah) | Tidak ada yang perlu dihapus dari layar ini |
| **Unlock Account** | Tidak ada di repo mana pun | Tidak ada yang perlu dihapus — dicatat agar tidak diasumsikan pernah ada |
| **Email User** | Tidak ada di repo mana pun | Tidak ada yang perlu dihapus |

---

## 6. Filters

| Filter | Status hari ini | Rekomendasi |
|---|---|---|
| Status (Aktif/Nonaktif) | Ada — quick filter chip | **KEEP** |
| Role | Ada, tapi hanya **kategori fuzzy** (Administrator/Supervisor/Agent via regex pada `roleCode`/`roleName`, `directoryHelpers.ts:105-115`), bukan pilihan Role yang literal | **KEEP kategori yang ada**; opsional tambahkan filter Role literal bila daftar peran bertambah — bukan perubahan wajib |
| Unit | **Tidak ada sama sekali** — tidak ada chip, tidak ada dropdown | **Gap** — backend `GET /users` **sudah** menerima query param `branchId` (`users/router.py:114,123`), tapi frontend tidak pernah mengirimkannya. Filter Unit yang diminta task **didukung backend, belum dibangun frontend** |
| Employee ID / Full Name | Tercakup lewat kotak pencarian bebas (§7), bukan filter chip terpisah | **KEEP sebagai pencarian**, bukan chip — sudah sesuai pola |

Tidak ada filter yang diminta task yang tidak didukung repository — filter Unit adalah satu-satunya yang perlu ditambahkan, dan itu pun backend sudah siap.

---

## 7. Search

**Sudah benar sesuai definisi bisnis §2.** `matchesDirectorySearch` (`directoryHelpers.ts:164-174`)
mencocokkan `username`, `fullName`, `email`, `roleName`, `roleCode` — seluruhnya dari baris
`UserRef` hasil `GET /users` (keanggotaan ECMP), tidak pernah menyentuh
`moduleUserCandidates.json` (Mock Enterprise Directory). Pemisahan "cari untuk mendaftarkan"
(Enterprise Directory, di `CreateUserModal`) vs "cari yang sudah terdaftar" (ECMP membership,
di layar ini) sudah berjalan benar secara arsitektural.

Satu penyesuaian mengikuti §4.1: bila `email` dihapus dari field yang ditampilkan, `email`
sebaiknya juga dihapus dari `matchesDirectorySearch` — mempertahankannya di pencarian tapi
tidak di tampilan akan membuat hasil pencarian terasa "ajaib" (cocok tapi tidak terlihat
kenapa).

---

## 8. Security Review

### 8.1 Temuan utama — scope Unit tidak ditegakkan pada jalur baca

**`GET /api/v1/users` mengembalikan seluruh anggota ECMP lintas Unit kepada siapa pun yang
punya permission `users:read`.** Dibuktikan langsung dari kode: `list_users`
(`users/router.py:120-140`) menerima `principal` tapi membuangnya (`_ = principal`) sebelum
memanggil `service.list()`; parameter `branch_id` yang tersedia adalah filter **opsional**
yang dikendalikan pemanggil, bukan batas yang dipaksakan dari identitas administrator.
Frontend mengonfirmasi ini: `UserManagement.tsx:136` memanggil `fetchUsers({ pageSize: 100 })`
tanpa filter unit sama sekali.

Ini sejenis dengan T-1 (privilege escalation lintas unit) yang sudah ditutup untuk
`users:create` (milestone UX-CU-002) — **tapi belum ditutup untuk membaca daftar**.
Administrator Regional Jawa Barat hari ini dapat melihat seluruh anggota Regional Sumatera,
Regional Jawa Timur, dan seterusnya, hanya dengan membuka layar ini.

**Rekomendasi mekanisme (bukan implementasi):** `OrgUnitGuard`/`OrgUnitResolver` yang dipakai
di `users:create` adalah pembanding **satu lawan satu** (principal vs satu resource) — cocok
untuk endpoint create/update satu baris, kurang cocok untuk memfilter **daftar** hasil. Yang
lebih sesuai untuk kasus ini adalah `DataScopeResolver`/`EffectiveScope`
(`app/modules/iam/data_scope_resolver.py`, TASK-039/040) — dirancang untuk memberi *Authorization
Layer* batas scope yang lalu dipakai memfilter query list. Ini **sudah ada di repo**, belum
disambungkan ke `list_users` mana pun. Menyambungkannya membutuhkan satu keputusan produk yang
sama seperti dicatat UX-CU-002/003: pemetaan peran administrator → `ScopeType`, yang belum
ditetapkan (lihat §9).

### 8.2 Temuan kedua — Activate/Deactivate, bila disambungkan, mewarisi gap yang sama

`PATCH /users/{id}/status` (`users/service.py:341-360`) juga tidak memeriksa scope Unit
administrator, dan tidak mencegah administrator menonaktifkan akunnya sendiri. Bila Activate/
Deactivate disambungkan ke UI (§5), kedua celah ini harus ditutup **bersamaan**, bukan
diwariskan diam-diam ke fitur yang baru terlihat.

### 8.3 Temuan ketiga — Reset Password adalah permukaan kredensial yang paling terbuka di ECMP

Password sementara dikirim ke klien, dirender sebagai plaintext dalam DOM
(`data-testid="temporary-password"`), dapat di-print (yang berarti tersimpan di riwayat
printer/PDF di luar kendali ECMP), dan dapat disalin ke clipboard sistem. Ini bukan sekadar
"belum sesuai batas baru" — ini permukaan yang lebih besar dari yang sudah ditutup di
Create User (yang hanya *meminta* password, tidak pernah menampilkannya kembali). Prioritas
penghapusan tertinggi di antara seluruh temuan dokumen ini.

### 8.4 Yang tidak bermasalah

Permission gate (`users:read`, `users:update`) sudah benar sebagai lapisan pertama. Tidak ada
temuan privilege-escalation pada dimensi Role di layar ini (layar ini tidak mengubah Role
siapa pun — itu ranah "Edit Membership" yang belum dibangun, lihat §9).

---

## 9. Repository Gaps

Dilaporkan, bukan diselesaikan dengan mengarang solusi — sesuai instruksi "STOP... Report
repository gaps instead of inventing solutions."

1. **Scope Unit tidak ditegakkan di `GET /api/v1/users` maupun `PATCH /users/{id}/status`**
   (§8.1, §8.2). Mekanisme yang tepat (`DataScopeResolver`) sudah ada di repo tapi
   memerlukan keputusan produk yang sama dengan yang dicatat UX-CU-002 §16.1 dan UX-CU-003
   §16.1: pemetaan resmi peran administrator → `ScopeType`. Belum ditetapkan di ADR maupun
   `02 Business Rules` mana pun yang diperiksa.
2. **Edit Membership tidak ada** — bila disetujui sebagai kebutuhan, ini adalah pekerjaan
   desain dan implementasi baru (form + endpoint `PUT /users/{id}` sudah ada di backend
   sebagai `update_user`, tapi belum ada UI yang memanggilnya untuk mengubah Peran/Unit/Status
   pengguna yang sudah terdaftar — hanya `change_password`/`admin_reset_password` dan status
   toggle yang punya jalur backend siap pakai hari ini).
3. **Resolusi nama Unit** (`branchId` → `Branch.code`/`name`) tidak ada di komponen manapun
   di fitur ini — `CreateUserModal` sudah melakukannya sendiri (mengambil `fetchBranches` dan
   mencocokkan `id`), tapi `DirectoryPeopleList`/`DirectoryPreviewPanel` tidak. Pola yang
   sudah terbukti di `CreateUserModal` dapat dipakai ulang, tapi menyambungkannya adalah
   pekerjaan implementasi, bukan sesuatu yang bisa "diaktifkan" dari desain saat ini.

---

## 10. Final Recommendation

**Prioritas keamanan (kerjakan lebih dulu, terlepas dari rename apa pun):**
1. Tutup §8.1 — scope Unit pada `list_users`, sejalan dengan keputusan produk yang sama yang
   sudah menunggu di UX-CU-002/003.
2. Hapus total permukaan Reset Password (§8.3, §5) — ini bukan soal gaya, ini kredensial
   plaintext yang aktif hari ini.

**Perbaikan tampilan yang murah dan tidak berisiko:**
3. Rename "@username" → Employee ID (label saja, field sama — §4.1).
4. Perbaiki resolusi nama Unit (§9.3) — data sudah ada, hanya butuh pola yang sama seperti
   `CreateUserModal`.
5. Hapus kolom Email dari tampilan dan pencarian (§4.1, §7); pindahkan/hapus "Last Login"
   dari tampilan utama (§4.1).
6. Perbarui `users.description` — hilangkan kalimat "atur ulang kata sandi".

**Gap yang menunggu keputusan produk, bukan keputusan desain layar ini:**
7. Edit Membership belum ada — perlu disetujui sebagai kebutuhan sebelum dirancang.
8. Activate/Deactivate: sambungkan ke backend yang sudah ada, **tapi** setelah §8.2 ditutup,
   bukan sebelum — menyambungkan aksi baru ke endpoint yang belum ter-scope memperbesar
   permukaan gap yang sama, bukan menutupnya.

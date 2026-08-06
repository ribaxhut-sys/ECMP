# UX-CU-001 — Redesign "Create User" → **Grant Module Access**

| Field | Value |
|---|---|
| Document ID | UX-CU-001 |
| Status | Draft — for review by CTO, Product Owner, Security, UI/UX |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Scope | Layar administrasi pengguna modul ECMP (saat ini `CreateUserModal`) |
| Parent | ECMP-CONSTITUTION-001 → ADR-014 → ADR-015 → ADR-017 → ADR-018 |
| Related | IA-001, PDS-001, PWDM-001, SEC-PWD-001, ECMP_RBAC_Flow_v1.0 |
| Out of scope | Kode, kontrak API, skema basis data, protokol identitas |

---

## 0. Executive Summary & Architectural Ruling

Enam requirement diajukan. Setelah diperiksa terhadap kode berjalan dan ADR yang mengikat,
requirement tersebut **tidak berada pada satu bidang kepemilikan yang sama**. Ini harus
disampaikan lebih dulu, karena menentukan requirement mana yang boleh dibangun penuh dan
mana yang akan menjadi utang teknis yang dibongkar saat Mode B menyala.

| Req | Ringkas | Pemilik kapabilitas | Putusan |
|---|---|---|---|
| 1 | Rename "Cabang (Optional)" → "Unit" | **ECMP** (presentation + AuthZ scope) | **BANGUN SEKARANG** |
| 2 | Unit terkunci pada scope administrator | **ECMP** (Authorization adalah milik ECMP) | **BANGUN SEKARANG — prioritas keamanan tertinggi** |
| 3 | Temporary password otomatis | Enterprise Platform (Password Management) | **Mode A saja — bangun sebagai penghapusan permukaan risiko** |
| 4 | Kirim kredensial via email | Enterprise Global Notification | **Mode A saja — dibatasi, adapter-local** |
| 5 | Force change password | Enterprise Platform | **Sudah ada sebagian; lengkapi kontrolnya di Mode A** |
| 6 | Activation link + secure token | **Enterprise Platform sepenuhnya** | **Rekomendasi arah yang benar, TAPI bukan untuk dibangun ECMP** |

### 0.1 Dasar putusan

ADR-014 (`05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md`)
menyatakan secara normatif untuk Enterprise Mode (Mode B):

- Forgot Password **disabled**
- Reset Password **disabled**
- Change Password **disabled**
- Local Password Storage **prohibited**
- "Mode B + local credential routes enabled → **Invalid** — must fail-fast"
- Tabel kepemilikan: Enterprise Platform memiliki *Authentication, SSO, User Directory,
  Password/MFA, Session, Organization/Department/Branch, Enterprise Global Notification*.
  ECMP memiliki *complaint lifecycle*, *Complaint Roles*, dan *ECMP Business Notification*.

Artinya: **Requirement 3, 4, 5, dan 6 seluruhnya berada di kolom Enterprise Platform.**
Membangunnya penuh di ECMP berarti membangun sesuatu yang, menurut ADR yang sudah disetujui,
wajib dimatikan pada saat cutover. ADR-014 sudah mencatat permukaan ini sebagai utang
(SEC-PWD-001: local password change, forgot/reset, admin reset).

**Peringatan kontrak (CLAUDE.md §2):** repo ini belum memuat satu pun artefak identitas dari
aplikasi utama. Semua asumsi tentang siapa yang mengirim email aktivasi, format token, dan
masa berlaku token **belum diverifikasi** ke pemilik Enterprise Platform. Requirement 6 tidak
boleh masuk backlog implementasi sebelum kontrak nyata diperoleh.

### 0.2 Konsekuensi framing terpenting — layar ini salah nama

Kode yang berjalan hari ini sudah **tidak membuat identitas**. `CreateUserModal` memaksa
administrator memilih orang dari direktori pusat lebih dulu (`moduleUserCandidates`); nama,
username, dan email dibaca **read-only** dari kandidat itu dan tidak dapat diketik. Yang
benar-benar ditentukan administrator hanyalah **Peran** dan **Unit**.

> **Layar ini bukan "Create User". Layar ini adalah "Grant Module Access".**

Reframing ini bukan kosmetik — ia menyelesaikan empat dari enam requirement secara struktural:
kalau ECMP tidak membuat identitas, ECMP juga tidak seharusnya membuat, mengirim, atau
mengelola kredensial identitas tersebut.

---

## 1. Current Problems

Temuan berikut diambil dari pembacaan berkas, bukan asumsi.

### P-1 — Label "Cabang" mengunci produk pada satu model organisasi
`frontend/messages/id.json:1833` memuat `"branchOptional": "Cabang (opsional)"`. Setiap
organisasi pengguna yang tidak memakai istilah "Cabang" (Region, Area, Divisi, Departemen,
Kantor, Unit Operasional) menghadapi kosakata yang salah sejak layar administrasi pertama.

### P-2 — Label "(opsional)" berbohong tentang aturan bisnis
Label berubah menjadi "opsional" / "wajib" / "kantor pusat" bergantung peran
(`CreateUserModal.tsx:428–435`). Tidak pernah ada keadaan di mana unit benar-benar opsional:
ia wajib untuk peran ber-scope unit, dan **terlarang** untuk peran kantor pusat. Kata
"opsional" menyembunyikan aturan yang sebenarnya biner dan ditegakkan server
(`backend/app/modules/users/service.py:150–163`).

### P-3 — **Privilege escalation lintas unit (severity: High)**
`CreateUserModal.tsx:427–461` menampilkan **seluruh** cabang hasil `fetchBranches(100)` kepada
setiap administrator. Sisi server, `POST /users` hanya menuntut permission `users:create`
(`backend/app/modules/users/router.py:90`), dan validasi `_ensure_branch_for_role` hanya
memeriksa kecocokan *kategori* peran↔cabang — **bukan** apakah cabang tersebut berada dalam
scope administrator yang sedang login. Akibatnya seorang Regional Admin Jawa Barat dapat
menempatkan pengguna di Regional Sumatera. Ini bukan masalah UI; ini lubang otorisasi yang
kebetulan terlihat di UI.

### P-4 — Administrator mengarang password
Field `password` diketik manual, `minLength={8}` (`CreateUserModal.tsx:390–401`). Password
melewati mata dan papan ketik manusia, lalu harus disampaikan ke pengguna melalui kanal yang
tidak ditentukan sistem — praktiknya WhatsApp, lisan, atau catatan.

### P-5 — Sistem berhenti di titik penciptaan, tidak sampai onboarding
Setelah sukses, modal ditutup dan hanya menampilkan toast (`onCreated` →
`CreateUserModal.tsx:242`). Tidak ada penyampaian kredensial, tidak ada bukti penyampaian,
tidak ada status "belum pernah login". Pekerjaan penyampaian didorong keluar sistem.

### P-6 — Force-change ada tapi tidak terlihat oleh administrator
Backend sudah menetapkan `force_password_change=True` pada setiap pembuatan
(`backend/app/modules/users/service.py:211`, catatan UAT-022). Di UI hal ini hanya muncul
sebagai *hint* kecil di bawah field password. Kontrol yang benar tidak dikomunikasikan,
sehingga tidak menghasilkan rasa aman maupun perubahan perilaku administrator.

### P-7 — Password sementara tidak punya masa berlaku dan tidak sekali pakai
`force_password_change` memaksa penggantian pada login pertama, tetapi tidak ada kedaluwarsa.
Password yang dikirim lewat WhatsApp tetap sah tiga bulan kemudian selama korban belum login.

### P-8 — Beban kognitif form tidak sebanding dengan keputusan yang diambil
Tujuh field ditampilkan; empat di antaranya read-only atau tidak dapat diubah. Administrator
hanya mengambil **dua** keputusan nyata (Peran, Unit), tetapi form tidak mencerminkan itu.

### P-9 — Permukaan kredensial lokal yang dilarang Mode B masih tumbuh
Endpoint `users:reset_password` (`router.py:197`, `service.py:460`) adalah bagian dari
SEC-PWD-001 yang ADR-014 catat sebagai permukaan yang tidak boleh bertahan di Mode B.
Menambah generator password + pengiriman email + activation link akan **memperbesar** permukaan
yang sudah dijadwalkan dibongkar.

---

## 2. Design Goals

| ID | Goal | Ukuran keberhasilan |
|---|---|---|
| G-1 | Kosakata organisasi netral dan dapat dikonfigurasi | Tidak ada string "Cabang"/"Branch" ter-hardcode di layar administrasi pengguna |
| G-2 | Scope unit tidak dapat dilanggar, di UI maupun server | 100% percobaan lintas unit ditolak server, bukan hanya disembunyikan UI |
| G-3 | Administrator tidak pernah menyentuh kredensial | Tidak ada field password di layar; tidak ada plaintext di klipboard, log, atau layar |
| G-4 | Setiap pemberian akses menghasilkan jejak audit yang lengkap | Aktor, subjek, peran, unit, waktu, kanal penyampaian tercatat |
| G-5 | Form mencerminkan keputusan sebenarnya | Administrator mengambil ≤ 2 keputusan; sisanya diturunkan sistem |
| G-6 | Semua mekanisme identitas dapat dilepas tanpa menyentuh domain | Penghapusan Mode A credential surface tidak mengubah satu pun aturan komplain |
| G-7 | Onboarding selesai di dalam sistem | Status pengguna dapat dilacak: Diundang → Aktif |

---

## 3. UX Improvements

### 3.1 Rename layar dan aksi

| Sekarang | Menjadi |
|---|---|
| Create User | **Grant Module Access** / **Beri Akses Modul** |
| Tombol "Create User" | **Grant Access** / **Beri Akses** |
| Deskripsi modal | "Berikan akses Complaint Module kepada karyawan yang sudah terdaftar di direktori perusahaan. ECMP tidak membuat akun baru." |

Alasan: menghapus ekspektasi bahwa ECMP adalah tempat lahir identitas. Ini juga menjadi
pertahanan pertama terhadap permintaan fitur di masa depan yang akan menarik ECMP kembali ke
wilayah Enterprise Platform.

### 3.2 Requirement 1 — "Cabang (Optional)" → **"Unit"**

**Alasan UX.** "Cabang" adalah *jawaban*, bukan *pertanyaan*. Pertanyaan yang sebenarnya
diajukan form adalah "pengguna ini bekerja pada bagian organisasi yang mana?". "Unit" adalah
istilah paling netral yang masih konkret bagi administrator non-teknis. Ia tidak memaksa
model geografis (Cabang, Area, Region), tidak memaksa model fungsional (Divisi, Departemen),
dan tidak memaksa model administratif (Kantor).

**Alasan bisnis.** Produk ditujukan untuk banyak organisasi. Kosakata yang salah pada layar
administrasi menimbulkan biaya nyata: pelatihan yang harus mengoreksi istilah, dokumen SOP
pelanggan yang tidak cocok dengan layar, dan permintaan kustomisasi per pelanggan. Satu
istilah netral menghapus kelas permintaan tersebut.

**Kata "(Optional)" dihapus.** Diganti label kondisional yang jujur:

| Konteks peran | Label | Bantuan |
|---|---|---|
| Peran ber-scope unit | **Unit** | "Ditentukan dari cakupan Anda." |
| Peran ber-scope kantor pusat | **Unit — Tidak berlaku** | "Peran kantor pusat beroperasi lintas seluruh unit." |

**Dampak Information Architecture.** Ini adalah rename **lapisan presentasi**, bukan rename
referensi identitas. ADR-015 menetapkan klaim `organization_id`, `branch_id`, `department_id`
sebagai kosakata kontrak dan ADR-018 menegaskan ECMP hanya menyimpan **referensi**, bukan
master. Karena itu:

- Kunci referensi tetap `branch_id` di lapisan kontrak identitas — **tidak diubah**.
- "Unit" hidup sebagai **label yang dapat dikonfigurasi organisasi** (`unit_label`), dengan
  default "Unit" dan bentuk jamak "Unit".
- IA-001 perlu memuat satu entri glosarium: *Unit = label tampilan untuk Organization
  Reference yang menjadi scope pengguna modul.*

**Future scalability.** ADR-018 §14 mencatat fondasi ECMP saat ini **branch-centric**, padahal
ADR-015 mensyaratkan tiga level (organization / branch / department), dan penutupan celah itu
adalah **prasyarat Mode B**. Label "Unit" adalah satu-satunya kosakata dari tiga kandidat yang
tetap benar ketika pemilih berubah dari daftar datar menjadi pemilih hierarki:

```
Unit
 └── PT Contoh (organization)
      └── Regional Jawa Barat (branch)
           └── Layanan Pelanggan (department)
```

Kalau hari ini dinamai "Cabang", penambahan level ketiga besok memaksa rename kedua — dan
rename kedua jauh lebih mahal karena SOP pelanggan sudah terbentuk.

### 3.3 Requirement 2 — Unit terkunci pada cakupan administrator

**Perilaku baru.** Unit diturunkan dari cakupan administrator yang login, ditampilkan sebagai
**bidang read-only bergaya "derived value"** — bukan `<select>` yang di-disable.

```
Unit
┌──────────────────────────────────────────────┐
│  Regional Jawa Barat                    🔒   │
└──────────────────────────────────────────────┘
Diturunkan dari cakupan Anda sebagai Regional Admin.
```

Perbedaan antara *read-only derived* dan *disabled select* penting secara UX: `select` yang
di-disable mengomunikasikan "Anda tidak boleh memilih sekarang" dan mengundang percobaan;
bidang turunan mengomunikasikan "ini bukan keputusan Anda" dan menutup percobaan.

**Bukan aturan tunggal — ada tiga kelas aktor.** Mengunci total akan mematahkan administrator
tingkat organisasi. Aturan yang benar:

| Kelas aktor | Perilaku field Unit |
|---|---|
| Administrator ber-scope satu unit (mis. Regional Admin) | **Terkunci.** Nilai = unit aktor. |
| Administrator ber-scope banyak unit (mis. HO Admin) | **Dapat dipilih, tetapi hanya dari subtree cakupannya.** Bukan seluruh daftar. |
| Peran target adalah peran kantor pusat | **Tidak berlaku.** Field disembunyikan/dinonaktifkan, nilai kosong. |

**Keamanan.** P-3 adalah temuan keamanan aktif. Aturan yang mengikat: **UI tidak menegakkan
apa pun.** Penyembunyian pilihan adalah *ergonomi*; penegakan harus terjadi di server, dengan
menurunkan unit dari principal, bukan menerimanya dari payload. Prinsipnya:

> Nilai yang tidak boleh diubah pengguna tidak boleh berasal dari klien.

**Integritas data.** Unit menentukan routing komplain, agregasi KPI, dan visibilitas antrean.
Satu pengguna yang salah unit merusak tiga hal sekaligus: pekerjaan mengalir ke unit yang
salah, KPI unit terkontaminasi, dan pengguna melihat data yang bukan haknya. Menurunkan unit
dari cakupan aktor menjadikan seluruh kelas kesalahan ini tidak mungkin, bukan sekadar jarang.

**Dampak RBAC.** Model otorisasi ECMP hari ini adalah *permission-based* (`users:create`) tanpa
dimensi *scope*. Perubahan ini memperkenalkan pasangan wajib: **permission × scope**. Untuk
setiap tindakan administrasi pengguna, pertanyaannya menjadi dua: *"boleh melakukan apa?"* dan
*"terhadap unit mana?"*. Ini juga menutup ADR-018 §Fail-Closed: bila cakupan aktor **tidak
dapat diresolusi**, tindakan ditolak — tidak jatuh ke default apa pun.

**Mengapa mengurangi kesalahan manusia.** Daftar cabang bisa memuat puluhan entri dengan nama
yang mirip. Memilih dari daftar panjang adalah tugas pencocokan visual, dan pencocokan visual
gagal secara diam-diam: administrator yang salah pilih tidak mendapat sinyal error. Turunan
sistem menghapus tugas itu sepenuhnya.

### 3.4 Requirement 3 — Password sementara otomatis (Mode A)

**Perubahan UX yang paling penting bukan menambahkan generator — melainkan menghapus field
password dari layar.** Administrator tidak melihat, tidak mengetik, dan tidak menyalin
kredensial apa pun.

**Mengapa password buatan manusia berbahaya.**

1. **Entropi rendah dan terprediksi.** Password yang diketik administrator konvergen ke pola:
   `Welcome@2026`, nama organisasi + tahun, atau satu password yang sama untuk seluruh batch.
   Pola batch adalah yang terburuk: satu kebocoran mengungkap semua.
2. **Ambang `minLength={8}` tidak lagi memadai** terhadap kemampuan cracking saat ini.
3. **Password melewati manusia.** Ia ada di papan ketik, klipboard, riwayat chat, dan ingatan
   administrator. Setiap tempat itu adalah lokasi kebocoran.
4. **Administrator mengetahui kredensial pengguna lain**, sehingga **non-repudiation runtuh**.
   Setiap tindakan pengguna dapat dibantah dengan "administrator tahu password saya".
5. **Reuse.** Administrator cenderung memakai ulang password yang mudah diingat lintas
   pengguna dan lintas sistem.

**Persyaratan teknis (Mode A).** Dibangkitkan dengan CSPRNG; 16 karakter; wajib memuat huruf
besar, huruf kecil, angka, dan simbol; tidak pernah dicatat ke log; tidak pernah ditampilkan
kecuali pada jalur break-glass eksplisit (§3.6).

**Manfaat UX.** Satu field hilang, satu kelas error validasi hilang, satu kelas kecemasan
administrator hilang ("apakah password ini cukup kuat?"). Waktu penyelesaian form turun.

**Manfaat administratif.** Administrator tidak lagi menjadi kustodian rahasia. Ketika pengguna
lupa password, jawaban administrator berubah dari "saya kirim ulang yang tadi" menjadi "sistem
mengirim ulang undangan" — administrator keluar dari jalur kredensial secara permanen.

### 3.5 Requirement 4 — Penyampaian via email

**Mengapa email lebih baik dari WhatsApp, lisan, dan catatan tangan.**

| Kanal | Terverifikasi milik subjek | Terkontrol organisasi | Meninggalkan bukti | Dapat dicabut | Dapat kedaluwarsa |
|---|---|---|---|---|---|
| **Email korporat** | Ya | Ya | Ya | Ya | Ya |
| WhatsApp | Tidak — terikat nomor pribadi | Tidak — perangkat & akun pribadi | Tidak dalam sistem | Tidak | Tidak |
| Lisan | Tidak | Tidak | Tidak | Tidak | Tidak |
| Catatan tangan | Tidak | Tidak | Bukti fisik yang hilang kendali | Tidak | Tidak |
| Pesan manual lain | Bergantung | Tidak | Tidak | Tidak | Tidak |

Poin yang menentukan bukan "email lebih aman" secara absolut — email juga bukan kanal rahasia.
Yang menentukan adalah: **email korporat adalah satu-satunya kanal yang identitasnya sudah
diverifikasi organisasi dan kendalinya berakhir bersama hubungan kerja.** Ketika karyawan
keluar, akun email dicabut; nomor WhatsApp pribadi tidak. Ingatan orang yang pernah mendengar
password secara lisan juga tidak.

Selain itu email memberi **atomisitas proses**: pemberian akses dan penyampaian menjadi satu
transaksi yang bisa gagal bersama-sama, bukan dua langkah terpisah yang salah satunya bisa
terlupa.

**Keunggulan onboarding.** Email dapat membawa lebih dari sekadar kredensial: nama modul,
peran yang diberikan, unit, siapa yang memberikan akses, tautan panduan pengguna, dan kontak
eskalasi bila pengguna tidak mengenali undangan ini — yang terakhir sekaligus berfungsi sebagai
deteksi pemberian akses yang tidak sah.

**Batas arsitektural.** ADR-014 menempatkan *Enterprise Global Notification* di kolom Enterprise
Platform dan *ECMP Business Notification* di kolom ECMP. Email kredensial adalah notifikasi
**identitas**, bukan notifikasi **bisnis**. Karena itu di Mode B, ECMP tidak mengirim email ini.
Implementasi Mode A wajib berhenti di balik boundary Identity Adapter agar dapat dilepas utuh.

### 3.6 Requirement 5 — Force change password

Backend **sudah** menetapkan `force_password_change=True` pada setiap pembuatan pengguna
(`backend/app/modules/users/service.py:211`). Yang belum ada adalah tiga kontrol pendamping
yang membuat kredensial sementara benar-benar sementara:

| Kontrol | Aturan |
|---|---|
| **Sekali pakai** | Kredensial sementara batal segera setelah login pertama berhasil. |
| **Kedaluwarsa** | Berlaku maksimum 24–72 jam sejak pemberian; setelah itu tidak dapat dipakai. |
| **Jalur terkunci** | Sebelum password diganti, seluruh navigasi selain layar ganti password ditolak — termasuk akses langsung via URL. |

**Manfaat keamanan.** Jendela paparan berubah dari "sampai pengguna kebetulan login" menjadi
"maksimum 72 jam". Kredensial yang bocor di riwayat chat menjadi tidak bernilai setelah
kedaluwarsa. Setelah penggantian, **tidak ada satu pun manusia selain pemilik akun yang tahu
kredensialnya** — inilah yang memulihkan non-repudiation.

**Kepatuhan.** Prinsip ini muncul konsisten di ISO/IEC 27001 Annex A (manajemen informasi
autentikasi rahasia), NIST SP 800-63B (kredensial yang diterbitkan pihak lain harus berumur
pendek dan sekali pakai), dan kerangka audit umum yang menuntut pemisahan tugas antara
pemberi akses dan pemilik kredensial. Kalimat yang diminta auditor: *"tunjukkan bahwa
administrator tidak dapat mengakses akun pengguna."* Force-change + sekali pakai + kedaluwarsa
adalah jawaban atas kalimat itu.

**Break-glass.** Jika email gagal terkirim, kredensial **tidak** ditampilkan secara default.
Administrator dapat memicu "tampilkan sekali" hanya bila memiliki permission terpisah,
tindakan tersebut tercatat sebagai peristiwa audit tersendiri, dan nilai ditampilkan satu kali
tanpa dapat ditampilkan ulang.

### 3.7 Requirement 6 — Activation link (rekomendasi arah)

**Model yang direkomendasikan.**

```
Admin memberi akses
        ↓
Sistem menerbitkan token aktivasi (opaque, acak, hash tersimpan)
        ↓
Email berisi TAUTAN — bukan password
        ↓
Pengguna membuka tautan (token divalidasi: belum dipakai, belum kedaluwarsa)
        ↓
Pengguna MEMBUAT password sendiri
        ↓
Token dibakar (single-use)
        ↓
Akun aktif → Login
```

**Mengapa lebih aman.**

1. **Password tidak pernah melintas kanal apa pun.** Ia lahir di peramban pemilik akun dan
   tidak pernah ada dalam bentuk yang dapat dibaca di email, log, atau layar administrator.
2. **Token bukan kredensial.** Ia adalah izin sekali pakai untuk *menetapkan* kredensial.
   Token yang dicuri setelah dipakai bernilai nol.
3. **Kedaluwarsa alami.** 24–72 jam; kadaluwarsa tidak merusak akun, hanya menuntut undangan
   ulang — biaya kegagalan rendah, sehingga masa berlaku boleh dibuat pendek.
4. **Tidak ada kustodian.** Tidak ada satu titik pun dalam proses di mana manusia selain
   pemilik akun mengetahui kredensial.
5. **Enumerasi tertutup.** Respons layar aktivasi harus seragam untuk token tidak valid,
   sudah dipakai, dan kedaluwarsa.

**Mengapa mayoritas produk SaaS memakainya.** Bukan karena lebih mudah — justru lebih banyak
komponen. Alasannya operasional: model ini menghilangkan tiket dukungan "saya tidak menerima
password", menghilangkan tanggung jawab hukum atas kredensial yang disimpan administrator, dan
merupakan satu-satunya model yang lolos audit dengan jawaban sederhana pada pertanyaan "siapa
saja yang pernah tahu password pengguna ini?" — jawabannya: tidak ada.

**Putusan untuk ECMP.** Ini adalah arah yang benar untuk **Enterprise Platform**, bukan
pekerjaan ECMP. Membangun sistem token aktivasi lengkap di dalam ECMP berarti membangun
penerbitan token, penyimpanan hash, kedaluwarsa, single-use, rate limiting, halaman aktivasi
publik, dan alur kirim-ulang — seluruhnya di kolom yang ADR-014 tetapkan milik Enterprise
Platform, dan seluruhnya wajib dimatikan saat Mode B menyala.

> **Rekomendasi:** ajukan model ini sebagai **requirement ECMP kepada Enterprise Platform**
> pada saat negosiasi kontrak identitas (CLAUDE.md §2). Di ECMP, dokumentasikan sebagai target
> dan jangan implementasikan. Untuk Mode A (lab/standalone), model password sementara di §3.4–3.6
> sudah memadai dan jauh lebih murah untuk dibongkar.

---

## 4. Security Improvements

| ID | Kontrol | Menutup |
|---|---|---|
| S-1 | Unit diturunkan dari principal server-side; nilai unit dari klien diabaikan | P-3 privilege escalation lintas unit |
| S-2 | Daftar unit yang dapat dipilih dibatasi pada subtree cakupan aktor | P-3 (ergonomi) |
| S-3 | Fail-closed: cakupan aktor tidak dapat diresolusi → tindakan ditolak | ADR-018 §Fail-Closed |
| S-4 | Field password dihapus dari UI; kredensial dibangkitkan CSPRNG | P-4 |
| S-5 | Kredensial tidak pernah dicatat ke log aplikasi maupun log audit | P-4 |
| S-6 | Penyampaian hanya ke alamat email dari direktori — tidak dapat diketik ulang administrator | Redirect kredensial ke alamat penyerang |
| S-7 | Kredensial sementara sekali pakai + kedaluwarsa 24–72 jam | P-7 |
| S-8 | Break-glass "tampilkan sekali" memerlukan permission terpisah dan menghasilkan peristiwa audit sendiri | Penyalahgunaan jalur fallback |
| S-9 | Peristiwa audit lengkap: aktor, subjek, peran, unit, waktu, kanal, hasil pengiriman | G-4 |
| S-10 | Rate limiting pada pemberian akses dan kirim-ulang undangan | Penyalahgunaan massal & enumerasi |
| S-11 | Larangan tegas: tidak ada penambahan permukaan kredensial baru di luar boundary Identity Adapter | P-9 |

---

## 5. Business Rules

Ditulis dalam format yang siap diangkat ke `02 Business Rules`.

| ID | Aturan | Penegakan |
|---|---|---|
| **BR-CU-01** | ECMP tidak membuat identitas. Akses modul hanya dapat diberikan kepada orang yang sudah ada di direktori perusahaan. | Server |
| **BR-CU-02** | Nama, username, dan email berasal dari direktori dan tidak dapat diubah dari layar ini. | Server + UI |
| **BR-CU-03** | Unit pengguna baru ditentukan sistem dari cakupan administrator yang memberikan akses. | **Server** |
| **BR-CU-04** | Administrator yang bercakupan satu unit tidak dapat memberikan akses ke unit lain. | **Server** |
| **BR-CU-05** | Administrator yang bercakupan banyak unit hanya dapat memilih unit di dalam subtree cakupannya. | **Server** |
| **BR-CU-06** | Peran ber-scope unit wajib memiliki Unit. Peran kantor pusat wajib tidak memiliki Unit. | Server (sudah ada) |
| **BR-CU-07** | Administrator tidak dapat memberikan peran yang setara atau lebih tinggi dari perannya sendiri. | Server (sudah ada sebagian) |
| **BR-CU-08** | Administrator tidak pernah menentukan, melihat, atau menyimpan kredensial pengguna. | Server + UI |
| **BR-CU-09** | Kredensial sementara berlaku sekali pakai dan kedaluwarsa maksimum 72 jam. | Server |
| **BR-CU-10** | Pengguna dengan kredensial sementara tidak dapat mengakses fungsi apa pun sebelum mengganti password. | Server |
| **BR-CU-11** | Penyampaian kredensial hanya melalui email direktori pengguna. | Server |
| **BR-CU-12** | Bila cakupan organisasi administrator tidak dapat diresolusi, pemberian akses ditolak. | Server |
| **BR-CU-13** | Setiap pemberian, pengiriman ulang, dan pencabutan akses menghasilkan peristiwa audit. | Server |
| **BR-CU-14** | **Mode B:** BR-CU-08 s.d. BR-CU-11 tidak berlaku — seluruh siklus kredensial dimiliki Enterprise Platform, dan jalur kredensial lokal wajib mati (ADR-014). | Konfigurasi fail-fast |

---

## 6. Information Architecture Changes

### 6.1 Kosakata

| Istilah lama | Istilah baru | Catatan |
|---|---|---|
| Cabang / Branch (label UI) | **Unit** | Label tampilan, dapat dikonfigurasi per organisasi |
| Cabang (Optional) | **Unit** + label kondisional | Kata "opsional" dihapus — tidak pernah benar |
| Create User | **Grant Module Access** | Menghapus klaim kepemilikan identitas |
| Password | *(dihapus dari layar)* | Digantikan blok status "Akses & Kredensial" |
| — | **Delivery Status** | Objek informasi baru: hasil penyampaian undangan |
| — | **Access Status** | Objek informasi baru: Diundang / Aktif / Kedaluwarsa / Nonaktif |

Kunci referensi identitas (`organization_id`, `branch_id`, `department_id`) **tidak berubah** —
ADR-015 memilikinya. Rename ini murni lapisan tampilan.

### 6.2 Struktur informasi layar

Form disusun ulang dari daftar tujuh field datar menjadi **tiga blok bermakna**:

| Blok | Isi | Sifat |
|---|---|---|
| **1 · Orang** | Pencarian direktori → Nama, Username, Email | Turunan direktori — read-only |
| **2 · Akses** | **Peran**, **Unit** | Peran = satu-satunya keputusan administrator; Unit = turunan cakupan |
| **3 · Aktivasi** | Kanal penyampaian, ringkasan apa yang akan terjadi | Informasional |

Hierarki ini menyampaikan pesan yang benar dalam satu tatapan: *siapa* (diberikan),
*apa haknya* (diputuskan), *lalu apa* (dijelaskan).

### 6.3 Dampak ke dokumen IA lain

- **IA-001** — tambahkan Information Object *Unit Scope* dan *Access Status*.
- **NAV-001** — layar berpindah label menjadi "Akses Modul" di bawah Administrasi.
- **PDS-001 / PWDM-001** — persona Administrator memperoleh keputusan baru yang eksplisit:
  *"peran mana yang tepat"*, dan kehilangan dua keputusan lama: *"unit mana"* dan
  *"password apa"*.

---

## 7. User Journey

### 7.1 Administrator — memberikan akses

| # | Langkah | Yang dilihat | Yang diputuskan | Beban kognitif |
|---|---|---|---|---|
| 1 | Buka Administrasi → Akses Modul | Daftar pengguna modul + status akses | — | Rendah |
| 2 | Klik "Beri Akses" | Panel dengan satu field aktif: pencarian direktori | — | Rendah |
| 3 | Ketik nama/ID karyawan | Hasil direktori dengan penyorotan kecocokan | Orang yang benar | Sedang |
| 4 | Pilih orang | Identitas terisi read-only; **Unit langsung terisi terkunci** | — | Rendah |
| 5 | Pilih Peran | Daftar peran yang boleh diberikan aktor | **Keputusan tunggal** | Sedang |
| 6 | Baca ringkasan aktivasi | "Undangan dikirim ke nama@perusahaan.co.id" | — | Rendah |
| 7 | Konfirmasi | Status "Diundang" + waktu kirim + bukti pengiriman | — | Rendah |

Perbandingan: 2 keputusan (dulu 4 — termasuk unit dan password), 0 kredensial yang disentuh
administrator, 0 langkah di luar sistem.

### 7.2 Pengguna baru — Mode A (password sementara)

Terima email → Login → **Layar wajib ganti password** (tidak ada jalan lain) → Dashboard.

### 7.3 Pengguna baru — target (activation link)

Terima email → Buka tautan → Buat password sendiri → Akun aktif → Login → Dashboard.
Tidak ada kredensial yang pernah dikirim.

### 7.4 Jalur kegagalan yang wajib dirancang

| Kegagalan | Perilaku |
|---|---|
| Email gagal terkirim | Akses tetap tercipta, status **"Undangan gagal terkirim"**, aksi "Kirim ulang" tersedia |
| Undangan kedaluwarsa | Pengguna melihat pesan netral; administrator melihat status "Kedaluwarsa" + "Kirim ulang" |
| Token/kredensial sudah dipakai | Pesan **identik** dengan token tidak valid (anti-enumerasi) |
| Cakupan aktor tidak dapat diresolusi | Form diblokir dengan pesan yang jelas — **bukan** jatuh ke unit default |
| Orang sudah punya akses modul | Tersaring dari hasil pencarian (perilaku ini sudah ada hari ini) |

---

## 8. Process Flow Diagram (ASCII)

### 8.1 Alur target — Grant Module Access

```
┌──────────────────────────────────────────────────────────────────────┐
│ ADMINISTRATOR (sudah terautentikasi, cakupan = Regional Jawa Barat)  │
└─────────────────────────────┬────────────────────────────────────────┘
                              │  buka "Beri Akses"
                              ▼
                 ┌────────────────────────────┐
                 │  Resolusi cakupan aktor    │
                 └────────────┬───────────────┘
                              │
                  dapat diresolusi?
                    │                │
                 TIDAK              YA
                    │                │
                    ▼                ▼
        ┌───────────────────┐   ┌──────────────────────────────┐
        │ TOLAK (fail-      │   │ Cari orang di direktori      │
        │ closed, BR-CU-12) │   │ perusahaan                   │
        └───────────────────┘   └──────────────┬───────────────┘
                                               │ pilih orang
                                               ▼
                         ┌──────────────────────────────────────┐
                         │ Identitas terisi READ-ONLY           │
                         │ Nama · Username · Email              │
                         └──────────────┬───────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────────┐
                         │ UNIT = cakupan aktor  🔒 TERKUNCI    │
                         │ "Regional Jawa Barat"                │
                         └──────────────┬───────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────────┐
                         │ Administrator memilih PERAN          │
                         │ (hanya peran yang boleh ia berikan)  │
                         └──────────────┬───────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────────┐
                         │ SERVER — penegakan sebenarnya        │
                         │  · unit DITURUNKAN, bukan diterima   │
                         │  · peran ≤ peran aktor               │
                         │  · peran×unit konsisten (BR-CU-06)   │
                         └──────────────┬───────────────────────┘
                                        │
                                 valid? ─── TIDAK ──▶ TOLAK + audit
                                        │
                                       YA
                                        ▼
                         ┌──────────────────────────────────────┐
                         │ Akses modul dibuat                   │
                         │ status = DIUNDANG                    │
                         │ kredensial DIBANGKITKAN sistem       │
                         │ (tidak pernah ditampilkan)           │
                         └──────────────┬───────────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────────┐
                         │ Kirim undangan ke email direktori    │
                         └──────┬───────────────────┬───────────┘
                            SUKSES              GAGAL
                                │                   │
                                ▼                   ▼
                    ┌────────────────────┐  ┌────────────────────────┐
                    │ Status: DIUNDANG   │  │ Status: PENGIRIMAN     │
                    │ + waktu kirim      │  │ GAGAL → "Kirim ulang"  │
                    └────────────────────┘  └────────────────────────┘
                                │
                                ▼
                    ┌────────────────────────────────────────┐
                    │ AUDIT: aktor · subjek · peran · unit · │
                    │ waktu · kanal · hasil                  │
                    └────────────────────────────────────────┘
```

### 8.2 Mode A — siklus kredensial sementara

```
 Undangan terkirim
        │
        ▼
 ┌──────────────────┐   lewat 72 jam    ┌──────────────────┐
 │ Kredensial       │──────────────────▶│ KEDALUWARSA      │
 │ sementara aktif  │                   │ (harus diundang  │
 └────────┬─────────┘                   │  ulang)          │
          │ login pertama               └──────────────────┘
          ▼
 ┌──────────────────────────────┐
 │ WAJIB GANTI PASSWORD         │
 │ semua rute lain DITOLAK      │◀── akses URL langsung juga ditolak
 └────────┬─────────────────────┘
          │ password baru diterima
          ▼
 ┌──────────────────────────────┐
 │ Kredensial sementara DIBAKAR │
 │ Status akses = AKTIF         │
 │ Tidak ada manusia lain yang  │
 │ mengetahui kredensial        │
 └────────┬─────────────────────┘
          ▼
      Dashboard
```

### 8.3 Target — activation link (milik Enterprise Platform)

```
Grant Access ──▶ Terbitkan token ──▶ Email berisi TAUTAN (bukan password)
                        │
                        ▼
              Pengguna membuka tautan
                        │
        ┌───────────────┼────────────────┐
        │               │                │
   token valid    sudah dipakai     kedaluwarsa
        │               │                │
        ▼               └───────┬────────┘
 Buat password sendiri          ▼
        │                Pesan SERAGAM (anti-enumerasi)
        ▼                       │
  Token DIBAKAR                 ▼
        │                 Minta undangan ulang
        ▼
  Akun AKTIF ──▶ Login ──▶ Dashboard

  Password TIDAK PERNAH melintas email, log, atau layar administrator.
```

### 8.4 Perbandingan kepemilikan Mode A vs Mode B

```
                       MODE A (standalone/lab)      MODE B (enterprise)
Identitas              Direktori lokal ECMP    │    Enterprise Platform
Kredensial             ECMP (sementara)        │    Enterprise Platform
Email undangan         ECMP Identity Adapter   │    Enterprise Notification
Ganti password         ECMP                    │    DIMATIKAN (ADR-014)
Reset password         ECMP (SEC-PWD-001)      │    DIMATIKAN (ADR-014)
─────────────────────────────────────────────────────────────────────────
Unit / scope           ECMP                    │    ECMP  ◀── TIDAK BERUBAH
Peran & permission     ECMP                    │    ECMP  ◀── TIDAK BERUBAH
Aturan komplain        ECMP                    │    ECMP  ◀── TIDAK BERUBAH
```

Diagram terakhir ini adalah alasan mengapa Requirement 1 dan 2 aman dibangun sekarang dan
Requirement 3–6 harus dibatasi: yang berada di atas garis akan dibongkar; yang di bawah garis
adalah milik ECMP secara permanen.

---

## 9. Security Considerations

### 9.1 Model ancaman ringkas

| ID | Ancaman | Vektor | Mitigasi |
|---|---|---|---|
| T-1 | Administrator nakal menanam akun di unit lain | Field unit yang dapat dipilih bebas (P-3) | S-1, S-2, BR-CU-03/04/05 |
| T-2 | Pemalsuan nilai unit langsung ke server | Manipulasi payload melewati UI | S-1 — unit tidak diterima dari klien |
| T-3 | Kredensial bocor di WhatsApp/chat | Penyampaian manual | S-6, S-7 |
| T-4 | Kredensial bocor di log | Pencatatan payload | S-5 |
| T-5 | Administrator memakai akun pengguna | Administrator tahu password | S-4, S-7, force-change |
| T-6 | Undangan diarahkan ke alamat penyerang | Email dapat diketik administrator | S-6 — email hanya dari direktori |
| T-7 | Enumerasi pengguna melalui layar aktivasi | Pesan error berbeda per kondisi | Pesan seragam |
| T-8 | Undangan massal / spam | Tidak ada rate limiting | S-10 |
| T-9 | Eskalasi via pemberian peran tinggi | Administrator memberi peran ≥ dirinya | BR-CU-07 |
| T-10 | Keputusan otorisasi dengan data organisasi basi | Projeksi organisasi tidak sinkron (ADR-018 §Eventual Consistency) | Fail-closed pada referensi yang tidak dapat diresolusi |

### 9.2 Prinsip yang tidak boleh dilanggar

1. **UI bukan kontrol keamanan.** Setiap penyembunyian di UI wajib memiliki penegakan server
   yang setara. Field terkunci tanpa penegakan server adalah teater keamanan.
2. **Nilai turunan tidak berasal dari klien.** Unit diturunkan dari principal.
3. **Fail-closed.** Referensi organisasi yang tidak dapat diresolusi menolak tindakan; tidak
   ada nilai default.
4. **Pemisahan tugas.** Pemberi akses ≠ pemilik kredensial. Ini yang membuat jejak audit
   bermakna.
5. **Minimalkan permukaan yang akan dibongkar.** Setiap kapabilitas kredensial baru di ECMP
   adalah utang yang jatuh tempo pada hari cutover Mode B.

### 9.3 Persyaratan audit

Setiap peristiwa merekam: identitas aktor, cakupan aktor pada saat tindakan, subjek, peran
yang diberikan, unit yang ditetapkan, stempel waktu, kanal penyampaian, hasil pengiriman, dan
korelasi permintaan. Peristiwa audit **tidak pernah** memuat kredensial dalam bentuk apa pun.

---

## 10. Future Scalability

| Dimensi | Hari ini | Berikutnya | Disiapkan oleh |
|---|---|---|---|
| Kosakata organisasi | "Cabang" ter-hardcode | Label `unit_label` per organisasi | Req 1 |
| Kedalaman organisasi | Satu level (branch) | Tiga level ADR-015 (org/branch/dept) — **prasyarat Mode B** per ADR-018 §14 | Req 1 (label netral) + Req 2 (model scope) |
| Model scope | Permission tanpa scope | Permission × scope, dengan subtree | Req 2 |
| Multi-tenant | Implisit | Isolasi tenant di atas resolusi cakupan yang sama | Req 2 |
| Sumber identitas | Seed direktori lokal | Enterprise User Directory melalui Identity Adapter | Reframing "Grant Module Access" |
| Siklus kredensial | Password sementara lokal | Sepenuhnya Enterprise Platform | Req 3–6 dibatasi ke adapter |
| Penyampaian undangan | Email dari ECMP | Enterprise Global Notification | Req 4 dibatasi ke adapter |
| Onboarding massal | Satu per satu | Impor batch memakai aturan scope yang **sama persis** | BR-CU-03/04/05 |

Poin penting: pekerjaan yang bertahan lintas semua kolom "Berikutnya" adalah **model scope**
(Req 2) dan **kosakata netral** (Req 1). Sisanya bersifat sementara menurut desain.

---

## 11. Risks

| ID | Risiko | Dampak | Kemungkinan | Mitigasi |
|---|---|---|---|---|
| R-1 | Unit dikunci hanya di UI, server tetap menerima nilai klien | **Kritis** — P-3 tetap terbuka sambil terlihat sudah beres | Sedang | Penegakan server adalah *definition of done*; uji negatif wajib |
| R-2 | Penguncian total mematahkan administrator lintas unit | Tinggi — operasi terhenti | Tinggi bila aturan tunggal dipakai | Tiga kelas aktor (§3.3) |
| R-3 | Membangun activation link penuh di ECMP | Tinggi — utang besar yang wajib dibongkar | **Tinggi** bila Req 6 dieksekusi apa adanya | Batasi ke Mode A; ajukan sebagai requirement ke Enterprise Platform |
| R-4 | Email tidak terkirim, pengguna terjebak | Sedang | Sedang | Status "Pengiriman gagal" + kirim ulang + break-glass terkendali |
| R-5 | Break-glass "tampilkan sekali" menjadi jalur normal | Tinggi — meniadakan seluruh Req 3 | Sedang | Permission terpisah, audit tersendiri, laporan penggunaan berkala |
| R-6 | Rename "Unit" merembet ke penggantian klaim `branch_id` | Tinggi — melanggar ADR-015 | Rendah | Dinyatakan tegas: rename lapisan presentasi saja (§3.2) |
| R-7 | Rename parsial — sebagian layar "Cabang", sebagian "Unit" | Sedang — kebingungan pengguna | **Tinggi** | Inventaris string menyeluruh sebelum rilis; satu istilah per rilis |
| R-8 | Kontrak identitas enterprise ternyata berbeda dari asumsi | Tinggi | **Tinggi** — kontrak belum diperoleh (CLAUDE.md §2) | Jangan implementasikan Req 6; tandai seluruh asumsi identitas sebagai belum terverifikasi |
| R-9 | Projeksi organisasi basi menyebabkan penolakan yang membingungkan | Sedang | Sedang | Pesan yang menjelaskan *mengapa* + jalur eskalasi; ADR-018 §Eventual Consistency |
| R-10 | Penghapusan field password dianggap kehilangan fitur oleh pengguna lama | Rendah | Sedang | Komunikasi perubahan + catatan rilis yang menjelaskan alasan keamanan |

---

## 12. Expected Benefits

| Pemangku kepentingan | Manfaat |
|---|---|
| **CTO** | Satu kelas kerentanan otorisasi ditutup; permukaan yang harus dibongkar saat Mode B tidak bertambah; model scope yang dibangun bertahan lintas roadmap |
| **Product Owner** | Produk dapat dijual ke organisasi dengan model organisasi apa pun tanpa kustomisasi kosakata; onboarding selesai di dalam sistem sehingga dapat diukur |
| **Security** | Pemisahan tugas nyata antara pemberi akses dan pemilik kredensial; non-repudiation pulih; jejak audit lengkap; jawaban siap untuk pertanyaan audit standar |
| **UI/UX** | Form dengan dua keputusan, bukan tujuh field; hilang satu kelas error validasi; hilang tugas pencocokan visual pada daftar unit panjang |
| **Administrator** | Tidak lagi menjadi kustodian rahasia; tidak lagi memilih dari daftar panjang; tidak lagi menyampaikan kredensial secara manual |
| **Pengguna baru** | Onboarding yang jelas dan konsisten; kredensial tidak beredar di riwayat chat |
| **Operasi/Dukungan** | Tiket "password tidak sampai" turun; status akses dapat dilihat langsung tanpa bertanya |

---

## 13. Final Recommendation

### 13.1 Yang dikerjakan sekarang

**Prioritas 1 — Requirement 2 (penguncian scope Unit).** Ini bukan permintaan UX; ini
penutupan celah otorisasi aktif (P-3). Kerjakan penegakan **server** lebih dulu; perubahan UI
mengikuti. Lolos ketiga filter konstitusi: menyelesaikan Authorization yang memang milik ECMP,
tidak menyentuh domain komplain, dan model scope-nya justru **dibutuhkan** oleh integrasi
enterprise (ADR-018 §14 menjadikannya prasyarat Mode B).

**Prioritas 2 — Requirement 1 (rename ke "Unit") + reframing layar ke "Grant Module Access".**
Murah, berumur panjang, dan menghapus klaim kepemilikan identitas yang keliru. Syarat: rename
menyeluruh dalam satu rilis (R-7), dan **tidak** menyentuh nama klaim ADR-015 (R-6).

**Prioritas 3 — Requirement 3 + 5 (hapus field password, bangkitkan otomatis, lengkapi
kontrol sementara).** Nilainya terutama pada **penghapusan**: menghilangkan field password
dari layar mengecilkan permukaan risiko sekaligus mempersiapkan penghapusan total di Mode B.
`force_password_change` sudah ada; yang ditambahkan hanya sekali-pakai, kedaluwarsa, dan
penguncian rute.

### 13.2 Yang dibatasi

**Requirement 4 (email kredensial)** — implementasikan **hanya untuk Mode A**, seluruhnya di
balik boundary Identity Adapter, dengan catatan eksplisit di ADR bahwa kapabilitas ini mati di
Mode B. Jangan bangun template engine, preferensi notifikasi, atau riwayat pengiriman — itu
milik Enterprise Global Notification.

### 13.3 Yang tidak dikerjakan

**Requirement 6 (activation link + secure token)** — **arahnya benar dan direkomendasikan
sebagai target arsitektur**, tetapi bukan pekerjaan ECMP. Membangunnya berarti membangun
penerbitan token, penyimpanan, kedaluwarsa, single-use, rate limiting, halaman aktivasi publik,
dan alur kirim-ulang di dalam kolom yang ADR-014 tetapkan milik Enterprise Platform — dan
ADR-014 mewajibkan seluruhnya mati di Mode B.

**Tindakan yang benar:** angkat Requirement 6 sebagai **requirement ECMP kepada pemilik
Enterprise Platform** dalam negosiasi kontrak identitas. Dokumen ini menjadi lampirannya.

> *Future Work — Di luar ruang lingkup Complaint Management Module: pembangunan sistem token
> aktivasi, halaman aktivasi publik, dan manajemen siklus kredensial di dalam ECMP.*

### 13.4 Blocker yang harus diputuskan sebelum eksekusi

1. **Kontrak identitas enterprise belum diperoleh** (CLAUDE.md §2). Tanpa itu, seluruh desain
   Requirement 4 dan 6 berdiri di atas asumsi. Requirement 1, 2, 3, dan 5 **tidak** terhalang
   oleh blocker ini.
2. **Definisi cakupan administrator belum ada sebagai konsep produk.** "Regional Admin" perlu
   ditetapkan formal: satu unit, subtree, atau daftar unit. Requirement 2 tidak dapat dieksekusi
   sebelum keputusan ini diambil oleh Product Owner.
3. **Kepemilikan `users:reset_password`** (SEC-PWD-001) perlu diputuskan bersamaan — menambah
   kapabilitas kredensial tanpa menjadwalkan pembongkaran yang lama akan memperbesar R-3.

---

## Lampiran A — Ringkasan pemetaan requirement

| Req | Diterima | Modifikasi terhadap permintaan asli | Alasan |
|---|---|---|---|
| 1 | Ya | Kata "(Optional)" dihapus, bukan dipertahankan; rename hanya lapisan tampilan | "Opsional" tidak pernah benar; ADR-015 memiliki nama klaim |
| 2 | Ya | Tiga kelas aktor, bukan penguncian tunggal; penegakan **server** | Penguncian tunggal mematahkan admin lintas unit; UI bukan kontrol keamanan |
| 3 | Ya (Mode A) | 16 karakter tetap (bukan 14–16); field password **dihapus** dari layar | Nilai utama ada pada penghapusan, bukan penambahan generator |
| 4 | Sebagian | Mode A saja, adapter-local, tanpa infrastruktur notifikasi baru | Enterprise Global Notification memilikinya (ADR-014) |
| 5 | Ya | Ditambah sekali-pakai, kedaluwarsa, penguncian rute; `force_password_change` sudah ada | Force-change tanpa kedaluwarsa menyisakan jendela paparan terbuka |
| 6 | Diadopsi sebagai target, **tidak diimplementasikan** | Diajukan sebagai requirement ke Enterprise Platform | ADR-014 mewajibkan jalur kredensial lokal mati di Mode B |

---

## Lampiran B — Rujukan yang diperiksa

| Rujukan | Yang dipastikan |
|---|---|
| `frontend/src/features/users/CreateUserModal.tsx` | Identitas read-only dari direktori; password manual `minLength=8`; daftar cabang tidak ter-scope |
| `frontend/messages/id.json:1833` | `"branchOptional": "Cabang (opsional)"` |
| `backend/app/modules/users/service.py:150–163, 211` | Validasi peran×cabang tanpa scope aktor; `force_password_change=True` sudah ditetapkan |
| `backend/app/modules/users/router.py:90, 197` | `users:create` tanpa dimensi scope; endpoint `users:reset_password` |
| ADR-014 v1.4 §Mode B | Forgot/Reset/Change Password disabled; local password storage prohibited; tabel kepemilikan kapabilitas |
| ADR-015 v1.3 | Enterprise memiliki identitas; ECMP menyimpan referensi; klaim org/branch/department |
| ADR-018 v1.0 §14 | Fondasi branch-centric; penutupan celah tiga level adalah prasyarat Mode B |
| CLAUDE.md §2 | Kontrak identitas enterprise belum diverifikasi |

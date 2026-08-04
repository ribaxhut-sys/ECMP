# PWDM-001 — Persona Workflow & Decision Model

| Field | Value |
|---|---|
| Document ID | PWDM-001 |
| Status | Draft |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-03 |
| Parent | PDS-000 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-000 → **PWDM-001** → (future) Information Architecture / Wireframe |

## Single responsibility

> Mendeskripsikan **bagaimana setiap persona bekerja sepanjang hari operasional** — urutan kerja, keputusan, dan friksi. Bukan layar, bukan komponen, bukan interaksi UI.

PWDM-001 tidak mendefinisikan ulang persona, Business Rule, CWX, atau apa pun yang sudah punya Source of Truth. Semua rujukan "siapa & tujuan" mengacu ke `PDS-000` — lih. `docs/ux/PDS-000-Persona-Design-Specification.md`.

---

## 1. Daily Workflow

### Customer Service
`Login` → orientasi ke pelanggan/case yang akan dilayani, tanpa backlog yang diwariskan dari sesi lain.
`Primary objective` → target sesi: setiap komplain hari itu tercatat lengkap & akurat sejak kontak pertama.
`Routine work` → menerima kontak → mencatat case baru (tidak ada case terkait, aktif maupun closed), menjawab follow-up (ditemukan case aktif milik pelanggan), atau meneruskan sebagai permintaan reopen ke Supervisor (ditemukan case terkait yang sudah closed).
`Interruptions` →
  - kontak baru masuk di tengah proses intake lain (tidak ada keputusan formal — bagian dari urutan kerja rutin).
  - informasi pelanggan tidak lengkap saat dicatat (keputusan: teruskan sekarang atau tahan untuk dilengkapi).
`Critical decisions` → apakah case sudah cukup lengkap untuk diteruskan, atau harus ditahan untuk dilengkapi dulu.
`Completion` → semua komplain hari itu tercatat lengkap; tidak ada yang harus diperbaiki ulang oleh pihak lain.
`Logout` → sesi ditutup tanpa case yang tertinggal dalam status "belum lengkap".

### Resolver / Case Handler
`Login` → melihat case apa saja yang assigned untuk hari ini.
`Primary objective` → setiap case assigned bergerak maju sepanjang sesi.
`Routine work` → memulai/melanjutkan penanganan case, memantau sisa SLA, mengajukan hasil dengan bukti saat selesai.
`Interruptions` →
  - hasil penanganan ditolak reviewer (keputusan: perbaiki & resubmit).
  - case lama dibuka kembali/reopened (keputusan: lanjutkan case lama).
  - diminta memberi konteks untuk eskalasi yang sedang ditangani Supervisor (keputusan: beri konteks ke Supervisor).
`Critical decisions` → aksi apa yang boleh dilakukan sekarang pada case ini — lanjut proses, ajukan review, atau serahkan konteks ke Supervisor.
`Completion` → semua case assigned berstatus jelas: selesai diajukan review, atau progresnya bisa dijelaskan.
`Logout` → tidak ada case yang diam tanpa progres yang bisa dipertanggungjawabkan.

### Supervisor
`Login` → melihat eskalasi baru, case mendekati/lewat SLA, dan antrian belum ter-assign — dalam urutan itu.
`Primary objective` → tidak ada case tanpa pemilik jelas, tidak ada SLA terlewat tanpa diketahui, semua pengajuan hasil diputuskan sebelum sesi berakhir.
`Routine work` → mendistribusikan case baru berdasar kapasitas unit; memantau SLA berjalan; menilai pengajuan hasil handler.
`Interruptions` →
  - eskalasi baru masuk (keputusan: tangani sendiri atau teruskan).
  - permintaan reopen atas case yang sudah closed (keputusan: setujui atau tolak reopen).
`Critical decisions` → assign ke siapa; approve atau reject hasil handler; menangani atau meneruskan eskalasi; menyetujui atau menolak reopen.
`Completion` → semua keputusan tertunda (assignment, approval, eskalasi, reopen) sudah diambil.
`Logout` → tidak ada case yang menunggu keputusan Supervisor yang belum diputuskan.

### Manager
`Login` → melihat indikator agregat yang menyimpang dari target.
`Primary objective` → memahami gambaran kinerja layanan hari itu, cukup untuk mengambil atau mengonfirmasi keputusan.
`Routine work` → meninjau tren per unit/kategori/periode untuk mengidentifikasi unit berisiko.
`Interruptions` → permintaan laporan ad hoc dari pihak lain di luar rutinitas.
`Critical decisions` → unit mana yang perlu perhatian tambahan; apakah angka agregat perlu di-drill-down ke level unit.
`Completion` → pemahaman kinerja hari itu cukup tanpa perlu verifikasi manual ke data operasional.
`Logout` → tidak ada pertanyaan kinerja yang masih terbuka dari sesi ini.

---

## 2. Decision Model

Legenda: setiap baris memetakan satu tahap workflow (Bagian 1) ke goal, keputusan, informasi yang dibutuhkan, hasil yang diharapkan, dan risiko bila informasi itu tidak tersedia.

### Customer Service

| Tahap | Goal | Keputusan | Informasi Dibutuhkan | Hasil Diharapkan | Risiko Bila Info Hilang |
|---|---|---|---|---|---|
| Login | Orientasi ke pelanggan yang akan dilayani | Tidak ada keputusan formal | Identitas pelanggan yang sedang dilayani | Siap menerima kontak pertama | Kontak dimulai tanpa konteks pelanggan |
| Primary objective | Menetapkan target sesi | — | — | Tujuan sesi jelas | — |
| Routine work | Mencatat case baru / menjawab follow-up / meneruskan reopen | Case baru, follow-up pada case aktif, atau permintaan reopen pada case closed? | Ada/tidaknya case milik pelanggan, dan status case tersebut (aktif atau closed) | Case tercatat sesuai statusnya: baru, follow-up terjawab tanpa tanya ulang, atau diteruskan sebagai permintaan reopen | Case closed keliru dicatat sebagai case baru (duplikat), atau follow-up dijawab tanpa konteks |
| Interruptions (kontak baru saat intake lain berjalan) | Mengelola kedatangan kontak baru di tengah proses intake yang sedang berjalan | Tidak ada keputusan formal | — | Intake yang sedang berjalan tidak terganggu tanpa alasan | — |
| Interruptions (informasi tidak lengkap) | Menangani intake yang informasinya belum lengkap | Teruskan sekarang atau tahan untuk dilengkapi? | Field yang kurang lengkap | Case diteruskan hanya saat layak diproses | Case tidak lengkap diteruskan, beban melengkapi berpindah ke pihak lain |
| Critical decisions | Menjamin kelengkapan sebelum case berpindah tangan | Case cukup lengkap untuk diteruskan? | Checklist field wajib untuk kategori komplain ini, dibandingkan dengan field yang sudah terisi | Case masuk antrian dalam kondisi siap diproses | Case belum lengkap masuk antrian, memicu bolak-balik |
| Completion | Evaluasi hasil sesi | — | Jumlah case yang butuh perbaikan ulang | Nol case yang harus diperbaiki pihak lain | Ketidaklengkapan baru terdeteksi setelah keluhan berulang |
| Logout | Menutup sesi tanpa case menggantung | Ada case yang belum selesai dicatat? | Status kelengkapan case yang sedang dikerjakan | Sesi ditutup bersih | Case setengah tercatat terbawa ke sesi berikutnya |

### Resolver / Case Handler

| Tahap | Goal | Keputusan | Informasi Dibutuhkan | Hasil Diharapkan | Risiko Bila Info Hilang |
|---|---|---|---|---|---|
| Login | Tahu case apa yang assigned | Tidak ada keputusan formal | Case yang sedang assigned | Siap memulai penanganan | Mulai kerja tanpa tahu urutan yang mendesak |
| Primary objective | Menetapkan target sesi | — | — | Tujuan sesi jelas | — |
| Routine work | Menangani case sesuai SLA | Case mana dikerjakan lebih dulu? | Sisa SLA; aksi yang boleh dilakukan sekarang | Case diproses sesuai urgensi | Case mendesak terlewat, SLA breach tanpa disadari |
| Interruptions (hasil ditolak reviewer) | Menangani hasil penanganan yang ditolak reviewer | Perbaiki & resubmit? | Alasan penolakan | Case yang ditolak kembali bergerak maju | Investigasi diulang dari awal karena alasan penolakan sebelumnya hilang |
| Interruptions (case reopened) | Melanjutkan case lama yang dibuka kembali | Lanjutkan case lama? | Riwayat penanganan sebelumnya | Case reopened kembali bergerak maju | Investigasi diulang dari awal karena riwayat penanganan sebelumnya hilang |
| Interruptions (konteks eskalasi diminta Supervisor) | Memberi konteks case untuk eskalasi yang sedang ditangani Supervisor | Beri konteks ke Supervisor? | Informasi yang diminta Supervisor | Supervisor mendapat konteks tanpa Handler kehilangan progres case | Supervisor mengambil keputusan eskalasi tanpa konteks lengkap dari Handler |
| Critical decisions | Menentukan case siap diajukan review | Ajukan sekarang atau lanjutkan penanganan? | Bukti/evidence yang relevan | Pengajuan review lengkap sekali jalan | Pengajuan ditolak karena bukti kurang, siklus bolak-balik |
| Completion | Evaluasi hasil sesi | — | Status akhir tiap case assigned | Tidak ada case diam tanpa progres yang bisa dijelaskan | Case terlupakan tanpa progres tercatat |
| Logout | Menutup sesi tanpa case tergantung tanpa keterangan | Ada case yang statusnya belum jelas? | Case yang masih in-progress | Sesi ditutup dengan status tiap case dapat dipertanggungjawabkan | Case terbawa ke sesi berikutnya tanpa konteks kenapa belum selesai |

### Supervisor

| Tahap | Goal | Keputusan | Informasi Dibutuhkan | Hasil Diharapkan | Risiko Bila Info Hilang |
|---|---|---|---|---|---|
| Login | Tahu apa yang butuh perhatian segera | Tidak ada keputusan formal | Eskalasi baru; case mendekati/lewat SLA; antrian belum ter-assign (urut) | Prioritas hari ini jelas sejak awal sesi | Hal kurang mendesak ditangani lebih dulu, eskalasi terlambat direspons |
| Primary objective | Menetapkan target sesi | — | — | Tujuan sesi jelas | — |
| Routine work | Distribusi beban kerja & memantau SLA unit | Assign ke siapa? | Beban kerja tiap handler/unit | Distribusi adil, tidak ada unit overload | Case menumpuk di satu handler, unit lain idle |
| Interruptions (eskalasi baru) | Menangani eskalasi baru | Tangani sendiri atau teruskan? | Alasan & konteks eskalasi | Eskalasi diputuskan tanpa menelusuri ulang riwayat | Keputusan diambil tanpa konteks lengkap |
| Interruptions (permintaan reopen) | Menangani permintaan reopen atas case closed | Setujui atau tolak reopen? | Riwayat closure untuk reopen | Reopen diputuskan tanpa menelusuri ulang riwayat closure dari awal | Keputusan diambil tanpa konteks lengkap riwayat closure |
| Critical decisions | Menilai pengajuan hasil handler | Approve atau reject? | Kelengkapan hasil penanganan yang menunggu approval | Closure sah, atau case kembali ke handler dengan alasan jelas | Closure tertunda tanpa alasan, atau ditutup tanpa kelengkapan |
| Completion | Evaluasi hasil sesi | — | Daftar keputusan yang masih terbuka | Nol keputusan menggantung di akhir sesi | Keputusan terbawa ke sesi berikutnya, case makin lama menunggu |
| Logout | Menutup sesi tanpa keputusan menggantung | Ada assignment/approval/eskalasi yang belum diputuskan? | Status semua item yang butuh keputusan Supervisor | Sesi ditutup bersih | Case terlantar tanpa keputusan sampai sesi berikutnya |

### Manager

| Tahap | Goal | Keputusan | Informasi Dibutuhkan | Hasil Diharapkan | Risiko Bila Info Hilang |
|---|---|---|---|---|---|
| Login | Tahu kondisi layanan hari ini secara agregat | Tidak ada keputusan formal | Indikator agregat yang menyimpang dari target | Tahu ke mana mengarahkan perhatian | Sesi dimulai tanpa gambaran risiko terkini |
| Primary objective | Menetapkan target sesi | — | — | Tujuan sesi jelas | — |
| Routine work | Meninjau tren untuk identifikasi unit berisiko | Unit mana perlu perhatian tambahan? | Tren per unit/kategori/periode | Perhatian terarah tanpa membaca setiap case | Risiko satu unit tidak terdeteksi sampai jadi masalah besar |
| Interruptions | Menjawab permintaan laporan pihak lain | Angka yang dilaporkan sudah bisa dipercaya? | Hasil pembandingan angka agregat dengan sumber data operasional | Laporan diberikan tanpa verifikasi manual tambahan | Angka tidak reconcile, laporan harus direvisi ulang |
| Critical decisions | Menentukan perlu drill-down atau cukup level agregat | Perlu masuk ke detail unit atau tidak? | Besaran penyimpangan angka unit dari target/tren normal | Keputusan diambil dengan bukti cukup, tanpa masuk ke detail transaksi individual | Keputusan diambil dari asumsi tanpa verifikasi ke sumber tren |
| Completion | Evaluasi hasil sesi | — | Ringkasan status vs target | Tidak perlu verifikasi manual tambahan | Keputusan diambil dengan data yang belum lengkap |
| Logout | Menutup sesi tanpa pertanyaan kinerja terbuka | Ada indikator yang masih perlu klarifikasi? | Status akhir indikator yang tadinya menyimpang | Sesi ditutup dengan gambaran kinerja final hari itu | Kekhawatiran kinerja terbawa tanpa catatan ke sesi berikutnya |

---

## 3. Time & Frequency Analysis

| Persona | Aktivitas | Frekuensi |
|---|---|---|
| Customer Service | Mencatat case baru | Many times per hour |
| Customer Service | Menjawab follow-up pelanggan | Many times per hour |
| Customer Service | Melengkapi data pelanggan yang kurang | Hourly |
| Resolver/Handler | Memulai/melanjutkan penanganan case | Hourly |
| Resolver/Handler | Memantau sisa SLA case yang sedang dikerjakan | Continuous |
| Resolver/Handler | Mengajukan hasil untuk review | Daily |
| Resolver/Handler | Menangani penolakan hasil (reject) | Daily (bervariasi) |
| Resolver/Handler | Melanjutkan case reopened | Rare |
| Resolver/Handler | Memberi konteks untuk eskalasi | Rare |
| Supervisor | Assign/redistribusi case | Hourly (dapat memuncak jadi many times/hour saat volume tinggi) |
| Supervisor | Memantau SLA unit | Continuous |
| Supervisor | Approve/reject hasil handler | Daily |
| Supervisor | Menangani eskalasi baru | Daily |
| Supervisor | Menyetujui/menolak reopen | Weekly |
| Manager | Meninjau indikator agregat harian | Daily |
| Manager | Meninjau tren per unit/kategori/periode | Weekly |
| Manager | Menjawab permintaan laporan ad hoc | Rare |

**Prioritas optimisasi tertinggi** — beririsan dengan tier *Immediate* di PDS-000 §4 (frekuensi tinggi **dan** berdampak ke keputusan/persona lain):
1. **Customer Service — kelengkapan data intake.** Paling sering terjadi, dan seluruh persona lain mewarisi kualitasnya (PDS-000 §6 Common).
2. **Resolver/Handler — kesadaran SLA berkelanjutan.** Continuous, risiko langsung ke pelanggaran SLA yang baru terlihat setelah terlambat.
3. **Supervisor — distribusi beban & respons eskalasi.** Frekuensi tinggi sekaligus fungsi gatekeeper kritikal (PDS-000 §6 — satu-satunya persona di dua level informasi sekaligus).
4. **Manager** — frekuensi jauh lebih rendah dari tiga persona lain; bukan prioritas optimisasi utama dibanding CS/Handler/Supervisor.

---

## 4. Context Switching Analysis

**Kehilangan konteks**
- Handler kehilangan konteks saat hasil ditolak reviewer dan harus merekonstruksi alasan penolakan.
- Handler kehilangan konteks saat case reopened setelah jeda waktu sejak closure.
- Supervisor kehilangan konteks saat menilai permintaan reopen tanpa melihat riwayat closure sebelumnya secara utuh.

**Pengulangan kerja**
- Customer Service berpotensi mengulang pertanyaan ke pelanggan bila case sebelumnya bolak-balik karena data tidak lengkap.
- Handler berpotensi mengulang investigasi dari awal pada case reopened/ditolak bila konteks penanganan sebelumnya tidak terbawa.
- Supervisor berpotensi menilai ulang kondisi case yang sama saat assignment jika informasi kapasitas tidak tersedia di titik keputusan.

**Pencarian informasi**
- Supervisor mencari beban kerja/kapasitas tiap handler sebelum bisa memutuskan assignment.
- Manager mencari/merekonsiliasi data operasional secara manual sebelum memberi angka ke pihak lain (JTBD Manager #3 mengasumsikan ini sebagai titik sakit saat ini).
- Handler mencari evidence/catatan penanganan sebelumnya saat menangani case reopened.

**Menunggu**
- Handler menunggu keputusan approve/reject Supervisor sebelum tahu apakah case selesai atau harus dikerjakan ulang.
- Supervisor menunggu pengajuan hasil dari Handler sebelum bisa mengambil keputusan closure.
- Customer Service berpotensi menunggu kejelasan status case saat menjawab follow-up pelanggan jika status terkini tidak segera diketahui.

**Perpindahan perhatian yang tidak perlu (level kerja, bukan navigasi layar)**
- Supervisor berpindah terus-menerus antara tiga mode kerja yang bersaing: distribusi (queue-level), pemantauan SLA (queue-level), dan approval/eskalasi (case-level) — tension yang sudah dicatat di PDS-000 §6.
- Manager berpindah antara level agregat (rutin) dan level unit (saat verifikasi), yang polanya tidak teratur karena dipicu penyimpangan angka, bukan jadwal tetap.

---

## 5. Workspace Success Model

| Persona | Sesi berhasil bila | Penyebab frustrasi | Selalu harus terlihat segera | Tidak boleh mengganggu alur kerja |
|---|---|---|---|---|
| Customer Service | Semua komplain hari itu tercatat lengkap & akurat sejak kontak pertama | Data pelanggan terpencar, harus tanya ulang, case bolak-balik karena tidak lengkap | Identitas pelanggan yang dilayani; ada/tidaknya case aktif miliknya | Keputusan assignment/closure — di luar tanggung jawab CS |
| Resolver / Case Handler | Semua case assigned bergerak maju — selesai diajukan atau statusnya jelas | Konteks case hilang saat reopened/ditolak; tidak tahu prioritas SLA | Case yang sedang assigned; sisa SLA; aksi yang boleh dilakukan sekarang | Proses assignment awal dan aktivitas Supervisor/Manager di luar case miliknya |
| Supervisor | Tidak ada case tanpa pemilik, tidak ada SLA terlewat tanpa diketahui, semua pengajuan diputuskan | Keputusan menumpuk tanpa info lengkap; harus menelusuri ulang riwayat untuk reopen/eskalasi | Eskalasi baru; case mendekati/lewat SLA; antrian belum ter-assign (urut prioritas) | Detail langkah-demi-langkah penanganan case yang sedang dikerjakan Handler |
| Manager | Gambaran kinerja hari itu cukup untuk mengambil/mengonfirmasi keputusan tanpa verifikasi manual | Angka tidak reconcile dengan operasional | Indikator agregat yang menyimpang dari target | Detail transaksi individual case, kecuali by exception |

---

## 6. Workflow Optimization Opportunities

Tanpa mengubah Business Rule, state machine, atau Authorization — hanya urutan, waktu, kontinuitas, dan dukungan keputusan.

**Sequence**
- Kelengkapan data intake saat ini belum menjadi gerbang sebelum case berpindah dari Customer Service ke antrian assignment, sehingga ketidaklengkapan berpotensi menjalar ke Handler/Supervisor.
- Urutan perhatian Supervisor saat ini mengikuti urutan kedatangan, belum tentu selaras dengan urutan urgensi yang sudah ditetapkan di PDS-000 §4 (eskalasi → SLA → antrian belum ter-assign).

**Timing**
- Sinyal risiko SLA saat ini terlihat oleh Handler dan Supervisor pada/sesudah breach terjadi, bukan sebelumnya — ini soal waktu munculnya sinyal, bukan aturan SLA itu sendiri.
- Indikator agregat bagi Manager saat ini berada dalam kondisi "siap dilaporkan" hanya pada saat permintaan ad hoc datang, bukan secara berkala, sehingga kerja rekonsiliasi terjadi mendadak.

**Continuity**
- Alasan penolakan reviewer dan riwayat closure sebelumnya belum tentu terbawa utuh ke Handler/Supervisor saat kasus kembali dibuka (reject atau reopen), sehingga rekonstruksi konteks dari nol dapat terjadi.
- Konteks case yang sama antara Handler dan Supervisor belum tentu berlanjut saat eskalasi terjadi, sehingga Supervisor berpotensi menelusuri ulang riwayat yang sudah diketahui Handler.

**Decision support**
- Visibilitas beban kerja/kapasitas handler bagi Supervisor belum tentu hadir tepat di titik keputusan assignment, melainkan terpisah dari keputusan itu.
- Angka yang sudah rekonsiliasi bagi Manager pada umumnya baru tersedia setelah permintaan laporan datang, bukan sebelumnya, sehingga keputusan drill-down bercampur dengan langkah verifikasi rutin.

---

## Related
- `docs/ux/PDS-000-Persona-Design-Specification.md` — sumber tunggal persona, JTBD, Information Priority, Responsibility Matrix, Workspace Goal
- `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003) — rujukan lifecycle Case

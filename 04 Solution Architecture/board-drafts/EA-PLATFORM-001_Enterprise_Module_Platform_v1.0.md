# ENTERPRISE MODULE PLATFORM ARCHITECTURE
## EA-PLATFORM-001 — Enterprise Modular Application Framework

| Field | Value |
|---|---|
| Document ID | **EA-PLATFORM-001** |
| Program pack | `../../18 Architecture Governance/ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md` |
| Version | 1.0 |
| Date | 2026-07-31 |
| Lifecycle (BR-002) | **DRAFT** — Architecture Board intake (bukan BASELINE / SoT) |
| Status | 🟡 **Draft for Architecture Board** — usulan kontrak HOST↔GUEST; **bukan** tiket implementasi |
| Owner | Chief Enterprise Architect |
| Co-owner **wajib** | **Enterprise Application Owner** |
| Approver | Architecture Board **dan** Enterprise Application Owner (bilateral) |
| Companion index | `../../26 Traceability/ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md` |
| Scope | Standar untuk seluruh Business Module di Enterprise Application |
| Reference design (guest) | Complaint Management Module (**EA-TARGET-CM-001**) — *reference design*, bukan “sudah implemented to platform” |
| Mode B | **CLOSED** (C-B6-1 / C-7) sampai Board unlock |

**Label:** **[FAKTA]** terbukti dari repository · **[DESAIN]** keputusan yang diusulkan · **[ASUMSI]** dugaan belum terverifikasi · **[BUTUH INFO]** informasi belum tersedia

---

## Board framing (wajib dibaca)

| Aturan | Isi |
|---|---|
| **Bukan tiket coding** | Registry, SDK, shell, entitlement service = kewajiban **HOST**. Draft ini meminta kapabilitas; **tidak** memerintahkan tim ECMP membangun ulang Enterprise Application diam-diam. |
| **HOST assumptions first** | Lampiran A (H1–H10) + kontrak Identity/Entitlement/Org/Event/UI **harus Closed** (atau waiver) sebelum implementasi guest yang bergantung padanya. Indeks: DTM-001. |
| **Bukan SoT sampai §0.3** | Status SoT / BASELINE hanya setelah co-ownership EP, sisi HOST di roadmap EP, validasi ≥2 modul (untuk v1.0 platform), dan Board accept. |
| **Mode A hedge** | Mode A standalone di ECMP tetap sah di bawah AUTHORIZED WITH CONDITIONS; divergensi Mode A/B hanya di adapters setelah unlock. |

---

# BAB 0 — PERINGATAN ARSITEKTUR (dibaca lebih dulu)

## 0.1 Ketegangan dalam mandat dokumen ini

Brief menyatakan: *"Enterprise Application dianggap SUDAH ADA. Jangan mendesain ulang Enterprise Application. Yang didesain adalah Enterprise Module Platform."*

**Kedua kalimat itu tidak dapat sepenuhnya dipenuhi bersamaan.**

Sebuah Module Platform terdiri dari dua sisi:

| Sisi | Isi | Siapa yang membangun |
|---|---|---|
| **Host side** | Module Registry · Shell yang me-mount modul · SDK yang dikonsumsi modul · Entitlement service · Event bus · Capability Registry | **Enterprise Application** |
| **Guest side** | Manifest · Adapter · Kontrak yang dipatuhi modul · Struktur internal modul | **Business Module** |

Registry, SDK, dan shell **adalah bagian dari Enterprise Application**. Mendesainnya berarti mendesain Enterprise Application.

**[DESAIN] Resolusi:** dokumen ini ditulis sebagai **kontrak dua sisi**. Setiap bab secara eksplisit menandai kewajiban **HOST** (Enterprise Application) dan **GUEST** (Business Module). Sisi HOST bukan perintah — ia **permintaan kapabilitas** yang harus dinegosiasikan dan dimiliki bersama.

Tanpa co-ownership Enterprise Application Owner, dokumen ini hanyalah standar internal satu tim yang kebetulan diberi nama "Enterprise".

## 0.2 Risiko terbesar dokumen ini

| # | Risiko | Mengapa nyata |
|---|---|---|
| R0-1 | **Enterprise Application mungkin sudah punya model ekstensi sendiri** | **[FAKTA]** Nol artefak Enterprise Application ditemukan di repository sepanjang audit. Bila model ekstensi sudah ada, dokumen ini harus **menyesuaikan diri**, bukan menggantikan |
| R0-2 | **Standar yang ditulis satu tim modul cenderung mengabadikan kebutuhan aksidental tim itu** | Complaint Module berat pada SLA, eskalasi, dan workflow. Analytics Module atau AI Module punya bentuk berbeda |
| R0-3 | **Second-system effect** | Setelah menemukan bahwa modul pertama salah arah, godaan terbesar adalah membangun platform yang terlalu ambisius |
| R0-4 | **Platform tanpa modul kedua adalah spekulasi** | Pola baru terbukti generik setelah **dua** implementasi berbeda, bukan satu |

## 0.3 Prasyarat sebelum dokumen ini menjadi SoT / BASELINE

- [ ] Enterprise Application Owner menjadi co-owner
- [ ] Dikonfirmasi apakah Enterprise Application sudah memiliki model modul/ekstensi (**H1**)
- [ ] Sisi HOST disetujui dan masuk roadmap Enterprise Application
- [ ] Asumsi HOST kritis (H2–H9 / setara K*+F* di EA-TARGET-CM-001) **Closed** atau waiver bertanggal — lihat DTM-001 & BOARD-008 §HOST Gate
- [ ] Minimal **dua** modul berbeda memvalidasi standar ini (Complaint + satu lagi) — gerbang deklarasi **v1.0** platform
- [ ] Architecture Board menerimanya sebagai `EA-PLATFORM-001` lifecycle **BASELINE** (BR-002)

**Sampai butir di atas terpenuhi, dokumen ini berstatus DRAFT Board — bukan standar yang berlaku, bukan backlog coding.**

### 0.4 Anti-skip (program ECMP)

| Melompati | Risiko |
|---|---|
| Coding Identity Adapter / enterprise `securitySchemes` / SSO UI sekarang | Melanggar C-B6-1 / C-7 |
| Menganggap Accept ADR-016/017/018 = Mode B unlocked | Board sudah menegaskan Mode B tetap CLOSED |
| Membangun Module Registry di repo ECMP sebagai “platform palsu” | Second-system + usurpasi HOST |
| Menjadikan Sprint/roadmap BAB 23 sebagai ticket tanpa G-HOST | Implementasi di atas asumsi kosong |

---

# BAB 1 — VISION

## 1.1 Apa itu Enterprise Module Platform

> **Enterprise Module Platform adalah kontrak yang memungkinkan sebuah domain bisnis dipasang ke dalam Enterprise Application tanpa membangun ulang satu pun kapabilitas bersama — dan tanpa Enterprise Application perlu mengetahui isi domain itu.**

Ia bukan framework, bukan library, bukan produk. Ia **kesepakatan**: apa yang disediakan host, apa yang dipatuhi guest, dan di mana batas keduanya.

## 1.2 Mengapa dibutuhkan — bukti dari modul pertama

**[FAKTA]** Complaint Module dibangun dengan asumsi standalone. Akibatnya, di dalam satu modul bisnis terdapat:

| Kapabilitas yang dibangun ulang | LOC |
|---|---:|
| Authentication, user directory, IAM, organization | 5.147 |
| Notification engine, audit store, search, settings, email | 4.006 |
| Workflow, execution, delivery, transport, provider abstraction | 3.632 |
| Shell UI, layout, theme, komponen bersama, halaman auth | ±2.340 |
| **Total** | **±15.100** |

**Proyeksi tanpa platform.** Bila 12 modul berikutnya mengulang pola yang sama:

| | Tanpa platform | Dengan platform |
|---|---:|---:|
| Kapabilitas dibangun ulang per modul | ±15.000 LOC | ±1.500 LOC (adapter) |
| 12 modul | **±180.000 LOC** | **±18.000 LOC** |
| Implementasi AuthN berbeda | 12 | 1 |
| Halaman login berbeda | 12 | 1 |
| Definisi izin berbeda | 12 | 1 skema |
| Permukaan audit terfragmentasi | 12 | 1 |

**Penghematan bukan intinya. Intinya adalah konsistensi:** satu cara masuk, satu cara diaudit, satu cara dipantau, satu cara dicabut aksesnya.

## 1.3 Tujuan jangka panjang

| # | Tujuan | Indikator keberhasilan |
|---|---|---|
| L1 | Modul baru siap produksi lebih cepat | Modul ke-3 dan seterusnya mencapai produksi < 40% waktu modul ke-1 |
| L2 | Nol duplikasi kapabilitas | Audit tahunan: tidak ada modul yang mengimplementasikan kapabilitas milik Enterprise |
| L3 | Modul dapat dipasang & dicabut tanpa merusak yang lain | Uji lifecycle enable/disable/upgrade/rollback lulus untuk setiap modul |
| L4 | Satu identitas, satu entitlement, satu audit | Pengguna tidak pernah melihat dua halaman login |
| L5 | Kontrak stabil lintas versi | Perubahan mayor Enterprise tidak memaksa penulisan ulang modul |

## 1.4 Manfaat bisnis

| # | Manfaat |
|---|---|
| B1 | **Time-to-market** — domain baru masuk lebih cepat karena tidak membangun fondasi |
| B2 | **Biaya perawatan turun** — satu implementasi AuthN dirawat, bukan dua belas |
| B3 | **Risiko kepatuhan turun** — audit dan entitlement terpusat dan seragam |
| B4 | **Pengalaman pengguna tunggal** — satu portal, satu navigasi, satu sesi |
| B5 | **Portabilitas tim** — pengembang berpindah antar modul tanpa belajar ulang fondasi |
| B6 | **Kemampuan mencabut** — modul bermasalah dinonaktifkan tanpa menurunkan sistem |

## 1.5 Non-tujuan

Platform ini **tidak** bertujuan: menyeragamkan model domain antar modul · memaksa satu bahasa pemrograman · menjadi service mesh · menggantikan Enterprise Application · menstandarkan proses bisnis.

---

# BAB 2 — PRINCIPLE

Sepuluh prinsip. Setiap prinsip menyatakan **konsekuensi** dan **cara mendeteksi pelanggarannya** — prinsip tanpa alat deteksi hanyalah slogan.

## P1 — Enterprise owns Capability. Module owns Meaning.

**Prinsip induk.** Semua prinsip lain adalah turunannya.

| Kapabilitas | Enterprise memiliki | Modul memiliki |
|---|---|---|
| Notification | Kanal, template engine, pengiriman, retry, preferensi global | Kapan peristiwa domain layak memberitahu, dan apa isinya |
| Workflow | Mesin, penjadwalan, kompensasi | State machine domain dan invariannya |
| Audit | Penyimpanan, retensi, non-repudiation, pencarian | Peristiwa domain apa yang layak diaudit |
| Search | Index, query engine, ranking | Apa yang layak dicari dan bagaimana diproyeksikan |
| Authorization | Identitas, entitlement ke modul | Arti setiap izin di dalam domain |
| Reporting | Permukaan, agregasi lintas-modul, distribusi | Definisi metrik domain |
| File | Penyimpanan, enkripsi, antivirus, kuota | Kebijakan lampiran domain |

**Konsekuensi:** pertanyaan *"siapa yang memiliki X?"* selalu dijawab dua kali — kapabilitasnya siapa, maknanya siapa.

**Deteksi pelanggaran:** modul memiliki tabel atau proses yang tidak menyebut konsep domainnya. Tabel bernama `notification_queue` di dalam modul keluhan adalah pelanggaran; tabel `complaint_notification_preference` bukan.

## P2 — Module owns Business Rule. Enterprise owns Infrastructure.

Aturan bisnis tidak boleh berada di luar modul yang memilikinya — termasuk tidak boleh dikonfigurasi di mesin workflow Enterprise, karena itu memindahkan invarian domain keluar dari tempat ia dapat diuji.

**Deteksi:** aturan domain yang hanya dapat diverifikasi dengan menjalankan sistem Enterprise.

## P3 — Module consumes Platform through Ports only.

Setiap kapabilitas Enterprise diakses lewat **port** (interface) yang dimiliki modul, dengan adapter yang menerjemahkan.

**Konsekuensi:** modul dapat berjalan penuh tanpa Enterprise (adapter in-memory), sehingga dapat diuji secara mandiri.

**Deteksi:** import langsung dari SDK/klien Enterprise di lapisan `domain` atau `application`.

## P4 — Module never calls Module.

Komunikasi antar modul **selalu** melalui Enterprise Application — event bus atau API terdaftar. Tidak ada pemanggilan langsung, tidak ada akses lintas skema database.

**Alasan:** panggilan langsung menciptakan graf ketergantungan yang membuat modul tidak dapat dinonaktifkan secara independen.

**Deteksi:** dependensi paket lintas modul; foreign key lintas skema.

## P5 — Enterprise entities are referenced, never owned.

Modul menyimpan **referensi opaque** (`external_user_id`, `org_unit_ref`, `customer_ref`) ke entitas milik Enterprise — tidak pernah salinan master, tidak pernah foreign key.

**[FAKTA] pelajaran dari modul pertama:** terdapat 16 foreign key ke `users.id`, empat di antaranya `ondelete="RESTRICT"`. Saat identitas berpindah ke Enterprise, seluruhnya menjadi referensi yatim. Ini kesalahan yang paling mahal dan paling mudah dicegah.

**Deteksi:** FK dari tabel modul ke tabel entitas Enterprise.

## P6 — Fail closed on security. Fail open on convenience.

| Kategori | Perilaku saat kapabilitas tidak tersedia |
|---|---|
| Identity, Entitlement, Authorization, Organization scope, Configuration wajib | **Tolak** |
| Notification, Search, Reporting, Metrics, Tracing | **Lanjutkan**, catat, antre |

**Deteksi:** adapter tanpa deklarasi mode kegagalan eksplisit.

## P7 — Enforcement belongs to the lowest layer that cannot be bypassed.

**[FAKTA] pelajaran termahal dari modul pertama:** Data Scope Resolver dibangun lengkap — resolver, tabel, test — dengan desain *opt-in per endpoint*. Hasilnya: **nol pemakaian** di seluruh router. Kontrol keamanan yang opsional adalah kontrol yang tidak ada.

**Konsekuensi:** scope filtering ditegakkan di **repository**, bukan di controller. Repository yang tidak menerapkannya **gagal di test arsitektur**.

**Deteksi:** test arsitektur yang memindai setiap repository.

## P8 — Contract before code.

Manifest, OpenAPI, dan skema event ditulis dan disepakati sebelum implementasi. Kontrak diverifikasi otomatis, bukan diperiksa manual.

**[FAKTA] pelajaran:** modul pertama memiliki 9 spesifikasi OpenAPI yang divalidasi CI — tetapi hanya **sintaksnya**. Tidak ada perbandingan spec dengan implementasi. Kontrak yang tidak diuji adalah dokumentasi, bukan kontrak.

**Deteksi:** contract test yang membandingkan spec dengan implementasi berjalan.

## P9 — Mode divergence terminates at one adapter.

**[FAKTA]** ADR-014 modul pertama menetapkan **Identity Adapter** dengan aturan: *"Business modules must not branch on deployment mode."*

**Digeneralisasi:** setiap perbedaan lingkungan (standalone/enterprise, dev/prod, tenant) berakhir di lapisan adapter. Domain tidak pernah tahu ia berjalan di mana.

**Deteksi:** `grep` untuk pengecekan mode di luar `adapters/` dan `bootstrap/`.

## P10 — Capability Ownership is decided before the first line of code.

**[FAKTA] pelajaran paling mahal:** modul pertama membangun ±15.100 LOC kapabilitas yang ternyata milik Enterprise, karena batas ditetapkan **setelah** implementasi.

**Konsekuensi:** artefak pertama sebuah modul baru bukan ADR teknologi, melainkan **Capability Ownership Matrix** yang disetujui.

**Deteksi:** Quality Gate G0 (BAB 21) menolak modul tanpa matrix yang disetujui.

---

# BAB 3 — ENTERPRISE CONTEXT

```
┌───────────────────────────────────────────────────────────────────────┐
│  ENTERPRISE APPLICATION            (sudah ada — tidak didesain ulang) │
│  Portal · Identity · Entitlement · Organization · Notification ·      │
│  Audit Store · Event Bus · File · Search · Config · Observability     │
└────────────────────────────────┬──────────────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────────────┐
│  ENTERPRISE MODULE PLATFORM             (kontrak — didesain dokumen)  │
│                                                                       │
│  HOST SIDE (kewajiban Enterprise Application)                         │
│  • Module Registry      • Module SDK        • Shell & mount point     │
│  • Capability Registry  • Manifest schema   • Lifecycle orchestrator  │
│                                                                       │
│  GUEST SIDE (kewajiban Business Module)                               │
│  • Manifest  • Ports & Adapters  • Contracts  • Quality Gate          │
└──────┬─────────────────┬──────────────────┬──────────────────┬────────┘
       │                 │                  │                  │
 ┌─────▼─────┐   ┌───────▼──────┐   ┌───────▼──────┐   ┌───────▼──────┐
 │ Complaint │   │   Customer   │   │    Asset     │   │   … 12 modul │
 │  Module   │   │    Module    │   │   Module     │   │              │
 └─────┬─────┘   └───────┬──────┘   └───────┬──────┘   └───────┬──────┘
       │                 │                  │                  │
 ┌─────▼─────┐   ┌───────▼──────┐   ┌───────▼──────┐   ┌───────▼──────┐
 │ Complaint │   │  Customer    │   │   Asset      │   │  Business    │
 │  Domain   │   │  Domain      │   │   Domain     │   │  Domain      │
 └───────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

**Aturan arah:** panah selalu ke bawah (host → guest) atau ke atas lewat kontrak (event, API terdaftar). **Tidak ada panah horizontal antar modul** (P4).

---

# BAB 4 — MODULE DEFINITION

## 4.1 Definisi

> **Business Module adalah unit yang memiliki satu Bounded Context, dapat dipasang dan dicabut secara independen, memiliki datanya sendiri, dan mengekspos kontrak yang stabil ke Enterprise Application.**

## 4.2 Kriteria kelayakan

Sebuah kandidat layak menjadi **Module** bila memenuhi **seluruh** kriteria:

| # | Kriteria | Uji |
|---|---|---|
| C1 | Memiliki Bounded Context sendiri — bahasa domainnya berbeda | Ahli domain berbeda dari modul lain |
| C2 | Memiliki data sendiri yang tidak ditulis pihak lain | Tidak ada tabel bersama |
| C3 | Dapat dinonaktifkan tanpa menghentikan modul lain | Uji disable |
| C4 | Memiliki siklus rilis sendiri yang bermakna | Ada alasan rilis independen |
| C5 | Memiliki pemilik bisnis yang jelas | Satu nama, bukan komite |
| C6 | Nilainya berdiri sendiri | Berguna meski modul lain tidak ada |

## 4.3 Pohon keputusan

```
Apakah punya Bounded Context & bahasa domain sendiri?
├── TIDAK → Apakah dipakai ≥2 modul?
│           ├── YA  → SHARED SERVICE (milik Enterprise)
│           └── TIDAK → FEATURE (di dalam modul yang ada)
└── YA  → Apakah punya data sendiri & dapat dicabut independen?
          ├── TIDAK → FEATURE
          └── YA  → Apakah punya pemilik bisnis & siklus rilis sendiri?
                    ├── TIDAK → FEATURE (evaluasi ulang 6 bulan)
                    └── YA  → MODULE
```

## 4.4 Contoh penerapan

| Kandidat | Klasifikasi | Alasan |
|---|---|---|
| Complaint Management | **Module** | BC sendiri, data sendiri, pemilik bisnis jelas |
| Complaint Escalation | **Feature** | Bagian dari BC Complaint; tidak berdiri sendiri |
| Notification | **Shared Service** | Dipakai seluruh modul |
| Approval | **Shared Service** *(kemungkinan)* | Bila polanya sama lintas domain; **[BUTUH INFO]** |
| Document | **Shared Service** | Penyimpanan & versioning generik |
| Analytics | **Shared Service** untuk permukaan; **Module** bila punya model domain sendiri | Perlu keputusan per kasus |
| AI Module | **[BUTUH INFO]** | Bergantung apakah ia domain atau kapabilitas |
| Helpdesk | **Module** — tetapi **waspada** | Berpotensi tumpang tindih dengan Complaint. Wajib pemisahan BC eksplisit |

**[DESAIN] Aturan anti-tumpang-tindih:** dua modul tidak boleh memiliki konsep dengan nama sama dan makna berbeda. Sebelum modul disetujui, Capability Registry diperiksa untuk tabrakan konsep.

## 4.5 Yang BUKAN Module

Kapabilitas teknis (logging, caching, queue) · lapisan (frontend saja / backend saja) · integrasi ke sistem eksternal (itu adapter) · laporan atau dashboard tunggal · pengelompokan organisasi tim.

---

# BAB 5 — MODULE LIFECYCLE

| Fase | HOST (Enterprise) | GUEST (Modul) | Gate |
|---|---|---|---|
| **Install** | Terima artefak, verifikasi tanda tangan & SBOM | Sediakan image/paket + manifest + migrasi | Artefak tervalidasi |
| **Register** | Simpan manifest di Registry, cek tabrakan id/rute/izin/event | Publikasikan manifest | Tidak ada konflik |
| **Validate** | Verifikasi kompatibilitas versi, kapabilitas yang diminta, skema izin & event | Sediakan endpoint validasi | Semua kontrak cocok |
| **Enable** | Aktifkan rute, menu, langganan event, entitlement | Jalankan startup, verifikasi adapter, lapor READY | Health `ready/deep` hijau |
| **Disable** | Sembunyikan menu, tolak rute, hentikan pengiriman event | Tolak request baru `403 MODULE_DISABLED`, selesaikan in-flight | Data tetap utuh |
| **Upgrade** | Orkestrasi rolling, jaga kompatibilitas kontrak | Migrasi maju kompatibel, dual-read selama transisi | Backup terverifikasi |
| **Rollback** | Kembalikan versi sebelumnya | Sediakan `downgrade` migrasi | Snapshot ada |
| **Remove** | Cabut registrasi, arsipkan manifest | Ekspor data domain, hapus skema setelah retensi | Persetujuan data owner |
| **Maintenance** | Mode baca-saja global | Tolak operasi tulis `503 MAINTENANCE` | — |
| **Retire** | Tandai deprecated, umumkan tanggal akhir | Sediakan jalur migrasi data ke penerus | Rencana suksesi disetujui |

**[DESAIN] Aturan kompatibilitas upgrade:** modul wajib mendukung **kontrak versi sebelumnya selama satu siklus rilis penuh**. Perubahan yang memutus kontrak = `MAJOR` + periode deprecation minimal satu rilis.

---

# BAB 6 — MODULE REGISTRY

**HOST SIDE** — dibangun Enterprise Application. **[BUTUH INFO]** apakah sudah ada.

## 6.1 Alur

```
Modul di-deploy
   ↓
Modul memanggil POST /platform/registry/register  { manifest }
   ↓
Registry: validasi skema manifest
   ↓
Registry: cek tabrakan (moduleId, route, menu, permission, eventName)
   ↓
Registry: cek kompatibilitas versi platform
   ↓
Registry: verifikasi kapabilitas yang diminta tersedia & diizinkan
   ↓
Registry: simpan, status = REGISTERED
   ↓
Admin/otomasi: ENABLE
   ↓
Registry: probe health → status = ACTIVE
   ↓
Portal membaca rute & menu; entitlement diaktifkan
```

## 6.2 Kontrak Registry (usulan)

| Endpoint | Arah | Fungsi |
|---|---|---|
| `POST /platform/registry/register` | Guest → Host | Mendaftarkan manifest |
| `PUT /platform/registry/{moduleId}/heartbeat` | Guest → Host | Kesehatan berkala |
| `POST /platform/registry/{moduleId}/enable` | Admin → Host | Aktivasi |
| `POST /platform/registry/{moduleId}/disable` | Admin → Host | Penonaktifan |
| `GET /platform/registry/modules` | Host | Daftar modul & status |
| `GET /platform/registry/{moduleId}/manifest` | Host | Manifest aktif |
| `DELETE /platform/registry/{moduleId}` | Admin → Host | Cabut registrasi |

## 6.3 Status modul

`UNKNOWN → REGISTERED → VALIDATED → ACTIVE ⇄ DISABLED → DEPRECATED → REMOVED`
`ACTIVE → DEGRADED` (health gagal) → `ACTIVE` atau `DISABLED`

## 6.4 Aturan tabrakan

**[DESAIN]** Registry **menolak** pendaftaran bila: `moduleId` sudah dipakai · prefix rute beririsan · kunci menu duplikat · kode izin duplikat dengan makna berbeda · nama event duplikat dengan skema berbeda · rentang kompatibilitas tidak terpenuhi.

---

# BAB 7 — MODULE MANIFEST

**[DESAIN]** Skema standar. Format YAML; wajib divalidasi JSON Schema di CI modul **dan** di Registry.

```yaml
apiVersion: platform/v1
kind: BusinessModule

metadata:
  id: complaint-management          # unik, kebab-case, immutable
  name: Complaint Management
  version: 2.0.0                    # SemVer modul
  owner: { business: Head of Customer Care, technical: Complaint Squad }
  description: Pengelolaan keluhan pelanggan end-to-end

compatibility:
  platform: ">=1.4 <2.0"            # rentang versi platform
  contracts:
    identity: v1
    entitlement: v1
    organization: v1

dependencies:
  capabilities:                     # kapabilitas Enterprise yang dibutuhkan
    - { name: identity,      required: true,  failureMode: closed }
    - { name: entitlement,   required: true,  failureMode: closed }
    - { name: organization,  required: true,  failureMode: closed }
    - { name: file-storage,  required: true,  failureMode: closed }
    - { name: notification,  required: false, failureMode: open }
    - { name: search-index,  required: false, failureMode: open }
    - { name: audit,         required: true,  failureMode: closed }
    - { name: event-bus,     required: true,  failureMode: closed }
  modules: []                       # HARUS kosong — P4

entitlement:
  key: complaint-management         # kunci entitlement di Enterprise

permissions:                        # katalog izin milik modul
  - { code: complaints:read,     description: Melihat keluhan }
  - { code: complaints:create,   description: Mendaftarkan keluhan }
  - { code: complaints:assign,   description: Menugaskan penanganan }
  - { code: complaints:escalate, description: Mengeskalasi keluhan }
  - { code: complaints:resolve,  description: Menyelesaikan keluhan }
  - { code: complaints:close,    description: Menutup keluhan }

scopes:
  organization: hierarchical        # none | flat | hierarchical
  data: [own, unit, unit-subtree, all]

routes:
  - { path: /complaints, entry: entry.js, permission: complaints:read }

menus:
  - { key: complaints, label: Keluhan, icon: inbox, order: 30,
      route: /complaints, permission: complaints:read }

events:
  publishes:
    - { name: ComplaintRegistered, version: 1, schema: contracts/events/complaint-registered.v1.json }
    - { name: ComplaintResolved,   version: 1, schema: contracts/events/complaint-resolved.v1.json }
  subscribes:
    - { name: UserDeactivated,     version: 1 }
    - { name: OrganizationChanged, version: 1 }
    - { name: EntitlementRevoked,  version: 1 }

api:
  basePath: /api/v1/cm
  spec: contracts/openapi/complaint-module.v1.yaml
  internal:
    live:  /internal/live
    ready: /internal/ready
    deep:  /internal/ready/deep
    metrics: /internal/metrics

data:
  schema: complaint                 # skema DB eksklusif modul
  migrations: migrations/
  referenceCaches: [ref_org_units, ref_users, ref_customers]

observability:
  metricsPrefix: complaint_
  alerts:
    - { name: SLABreachSpike, expr: rate(complaint_sla_breached_total[5m]) > 0.1, severity: warning }
```

**[DESAIN] Aturan manifest:** `metadata.id` immutable seumur hidup modul · `dependencies.modules` **wajib kosong** · setiap izin & event wajib punya skema · perubahan `permissions` atau `events.publishes` = `MAJOR`.

---

# BAB 8 — CAPABILITY MODEL

## 8.1 Taksonomi

| Jenis | Definisi | Contoh | Pemilik default |
|---|---|---|---|
| **Business Capability** | Kemampuan menghasilkan nilai bisnis | Menangani keluhan; menagih; mengelola aset | **Modul** |
| **Technical Capability** | Kemampuan teknis tanpa makna bisnis | Menyimpan berkas; mengirim pesan; mengindeks | **Enterprise** |
| **Shared Capability** | Technical Capability yang dipakai ≥2 modul | Notification, Audit, Search | **Enterprise** |
| **Module Capability** | Business Capability milik satu BC | Eskalasi keluhan; perhitungan SLA | **Modul** |
| **Enterprise Capability** | Kapabilitas lintas seluruh organisasi | Identity, Entitlement, Organization | **Enterprise** |

## 8.2 Uji penentuan pemilik

**[DESAIN]** Empat pertanyaan berurutan:

```
1. Apakah maknanya berubah bila domainnya berubah?
   YA → Modul memiliki MAKNA-nya.
2. Apakah mekanismenya sama untuk domain lain?
   YA → Enterprise memiliki KAPABILITAS-nya.
3. Bila (1) dan (2) sama-sama YA → PECAH.
   Enterprise = mekanisme; Modul = kebijakan/semantik.
4. Bila keduanya TIDAK → kandidat Feature, bukan Capability.
```

**Contoh penerapan pada Notification:**
1. Apakah *kapan mengirim* berubah bila domain berubah? **Ya** → makna milik modul.
2. Apakah *cara mengirim* sama untuk domain lain? **Ya** → kapabilitas milik Enterprise.
3. → **Pecah.** Enterprise memiliki `NotificationDelivery`; modul memiliki `NotificationIntent`.

## 8.3 Ownership · Delegation · Consumption

| Relasi | Arti | Aturan |
|---|---|---|
| **Ownership** | Pihak yang menentukan perilaku & memiliki datanya | Tepat **satu** pemilik. Tidak ada kepemilikan bersama |
| **Delegation** | Pemilik menyerahkan eksekusi ke pihak lain, tetap memiliki kebijakan | Modul mendelegasikan pengiriman ke Enterprise, tetap memiliki isi pesan |
| **Consumption** | Pihak memakai kapabilitas tanpa memilikinya | Selalu lewat port + kontrak versi |

**[DESAIN] Aturan besi:** *satu kapabilitas, satu pemilik.* Bila dua pihak merasa memiliki, kapabilitas itu **belum terdefinisi dengan benar** dan harus dipecah (§8.2 langkah 3).

---

# BAB 9 — CAPABILITY OWNERSHIP MATRIX

## 9.1 Aturan penentuan

**[DESAIN]** Matrix disusun **sebelum** modul dibangun (P10), memakai kolom wajib:

| Kolom | Isi |
|---|---|
| Capability | Nama kanonik dari Capability Registry |
| Type | Business / Technical / Shared / Enterprise |
| Owner | Tepat satu |
| Consumer | Daftar pihak yang memakai |
| Integration Method | `TOKEN` / `API` / `EVENT` / `SYNC` / `EMBED` / `LOCAL` |
| Failure Mode | `closed` / `open` |
| Contract | Rujukan kontrak versi |
| Status | Proposed / Agreed / Implemented / Deprecated |
| Reason | Alasan berbasis uji §8.2 |

## 9.2 Aturan ownership

| # | Aturan |
|---|---|
| O1 | Satu kapabilitas, satu pemilik — tanpa pengecualian |
| O2 | Pemilik menentukan kontrak; konsumen menyesuaikan |
| O3 | Perubahan pemilik memerlukan Board Resolution |
| O4 | Kapabilitas tanpa pemilik **tidak boleh** diimplementasikan siapa pun |
| O5 | Bila ≥2 modul membutuhkan kapabilitas yang sama, ia otomatis menjadi kandidat Shared Capability milik Enterprise |

## 9.3 Aturan delegation

| # | Aturan |
|---|---|
| D1 | Delegasi tidak memindahkan kepemilikan |
| D2 | Penerima delegasi tidak boleh mengubah semantik |
| D3 | Delegasi wajib punya mode kegagalan eksplisit |
| D4 | Delegasi didokumentasikan di manifest (`dependencies.capabilities`) |

## 9.4 Aturan consumption

| # | Aturan |
|---|---|
| U1 | Konsumsi hanya lewat port + kontrak versi |
| U2 | Konsumen wajib menangani ketidaktersediaan sesuai `failureMode` |
| U3 | Konsumen tidak boleh menyalin data pemilik kecuali sebagai **reference cache** ber-`last_synced_at` |
| U4 | Konsumen tidak boleh bergantung pada detail implementasi pemilik |

## 9.5 Capability Registry

**[DESAIN]** HOST SIDE. Daftar kanonik seluruh kapabilitas di Enterprise Application, dengan pemilik, versi kontrak, dan konsumen. **Satu-satunya sumber kebenaran** untuk pertanyaan "siapa memiliki X". Modul baru wajib memeriksanya sebelum membangun apa pun.

---

# BAB 10 — MODULE SDK

**HOST SIDE.** SDK dibangun & dirilis Enterprise Application. **[BUTUH INFO]** apakah sudah ada.

## 10.1 Prinsip SDK

**[DESAIN]**

| # | Prinsip |
|---|---|
| S1 | SDK mengekspos **kontrak**, bukan implementasi |
| S2 | SDK **tidak** membawa opini tentang framework internal modul |
| S3 | Setiap API SDK punya versi & jaminan kompatibilitas |
| S4 | SDK menyediakan **implementasi in-memory** untuk pengujian modul |
| S5 | Modul **tidak wajib** memakai SDK — ia boleh mengimplementasikan kontrak sendiri |

**S5 penting.** SDK adalah kemudahan, bukan belenggu. Yang wajib adalah **kontrak**, bukan pustakanya. Ini mencegah SDK menjadi titik kegagalan tunggal bagi seluruh modul.

## 10.2 Permukaan SDK

| API | Fungsi utama | Failure mode |
|---|---|---|
| **Identity** | `getPrincipal()`, `getExternalUserRef()`, klaim tervalidasi | closed |
| **Authorization** | `hasEntitlement(moduleKey)`, `getEnterpriseRoles()` | closed |
| **Organization** | `getOrgUnit(ref)`, `getAncestors(ref)`, `isDescendantOf(a,b)` | closed |
| **Navigation** | `navigate(route)`, `registerRoutes()`, `getBreadcrumb()` | open |
| **Notification** | `publishIntent(intent)` | open |
| **Logging** | logger terstruktur ber-korelasi otomatis | open |
| **Configuration** | `get(key, scope)`, `watch(key)` | closed untuk config wajib |
| **Storage** | `put(bytes, meta)`, `get(handle)`, `delete(handle)` | closed |
| **Search** | `publishProjection(doc)`, `query(spec)` | open |
| **Workflow** | `startProcess()`, `signal()`, `scheduleAt()` | open |
| **Monitoring** | `counter()`, `histogram()`, `gauge()` | open |
| **Telemetry** | `startSpan()`, propagasi trace context | open |
| **Audit** | `publishAuditEvent(event)` | closed |
| **Event Bus** | `publish(event)`, `subscribe(name, handler)` | closed |

## 10.3 Kontrak versi SDK

**[DESAIN]** SDK memakai SemVer. `MAJOR` hanya boleh naik bersamaan dengan `MAJOR` platform, dengan periode dukungan ganda minimal satu rilis. Modul mendeklarasikan rentangnya di `compatibility.platform`.

---

# BAB 11 — INTEGRATION CONTRACT

Format seragam. Kolom **Sisi** menandai siapa yang wajib menyediakan.

| # | Kapabilitas | Port (guest) | Metode | Failure | Sisi penyedia |
|---|---|---|---|---|---|
| 1 | **Authentication** | `IdentityProvider` | Token OIDC (RS256, alg pinning, JWKS) | closed | HOST |
| 2 | **Identity** | `IdentityProvider` | Token + API direktori | closed | HOST |
| 3 | **Entitlement** | `EntitlementProvider` | Klaim atau API | closed | HOST |
| 4 | **Organization** | `OrganizationDirectory` | API + sync ke reference cache | closed | HOST |
| 5 | **Notification** | `NotificationPublisher` | Event atau API | open | HOST |
| 6 | **Workflow** | `WorkflowClient` | API + callback | open | HOST |
| 7 | **Audit** | `AuditPublisher` | Event | closed | HOST |
| 8 | **Search** | `SearchIndexPublisher` | Event proyeksi + API query | open | HOST |
| 9 | **Configuration** | `ConfigurationProvider` | API + cache + watch | closed (wajib) | HOST |
| 10 | **Storage** | `FileStorage` | API | closed | HOST |
| 11 | **Logging** | stdout JSON terstruktur | konvensi | open | HOST (sink) |
| 12 | **Monitoring** | `MetricsSink` | pull `/internal/metrics` atau push | open | HOST |
| 13 | **Event Bus** | `DomainEventPublisher` | publish/subscribe | closed | HOST |
| 14 | **Scheduler** | `SchedulerClient` | API + callback | closed untuk job kritikal | HOST |

## 11.1 Kewajiban guest untuk setiap integrasi

**[DESAIN]** Setiap adapter **wajib**: mendeklarasikan `failureMode` di manifest · menerapkan timeout + circuit breaker · tidak membocorkan model Enterprise ke domain (anti-corruption layer) · membaca endpoint & nama klaim dari **konfigurasi**, bukan hardcode · menyediakan implementasi `inmemory` untuk pengujian.

## 11.2 Kewajiban host

**[DESAIN]** Setiap kapabilitas host **wajib**: memiliki kontrak berversi · memiliki lingkungan uji yang dapat diakses tim modul · mengumumkan perubahan yang memutus minimal satu rilis sebelumnya · menyediakan contoh payload nyata (bukan hanya skema).

**[FAKTA] pelajaran dari modul pertama:** kontrak identitas ditulis lengkap dan formal, tetapi tanpa satu pun contoh token nyata dari sistem penyedia. Seluruh implementasi menjadi hipotesis. **Kewajiban "contoh payload nyata" lahir dari kesalahan itu.**

---

# BAB 12 — EVENT MODEL

## 12.1 Envelope standar

**[DESAIN]** Seluruh event memakai envelope identik:

```json
{
  "eventId": "uuid-v4",
  "eventName": "ComplaintRegistered",
  "eventVersion": 1,
  "occurredAt": "2026-07-31T10:15:00Z",
  "producer": { "moduleId": "complaint-management", "version": "2.0.0" },
  "correlationId": "uuid-v4",
  "causationId": "uuid-v4",
  "partitionKey": "complaint-id-123",
  "tenantId": "optional",
  "payload": { }
}
```

## 12.2 Aturan

| Aspek | Aturan |
|---|---|
| **Publishing** | Wajib lewat **Transactional Outbox** — event dan perubahan state satu transaksi |
| **Subscription** | Deklaratif di manifest; handler wajib **idempoten** |
| **Version** | Perubahan payload yang memutus = **event baru** (`v2`), bukan modifikasi `v1` |
| **Delivery** | **At-least-once** — [FAKTA] sudah menjadi standar modul pertama (ADR-001) |
| **Ordering** | Dijamin per `partitionKey`, **tidak** global |
| **Retry** | Eksponensial backoff milik host; guest tidak mengimplementasikan retry sendiri |
| **Dead Letter** | DLQ milik host. Guest wajib menyediakan `POST /internal/outbox/{id}/replay` |
| **Idempotency** | Konsumen menyimpan `eventId` yang telah diproses; duplikat diabaikan diam-diam |
| **Correlation ID** | Diteruskan dari HTTP → domain → event → log → trace, tanpa putus |
| **Schema** | JSON Schema di `contracts/events/`; divalidasi CI **dan** Registry |

## 12.3 Aturan payload

**[DESAIN]** Payload event **hanya berisi referensi dan fakta domain**, tidak berisi salinan entitas Enterprise. `ComplaintRegistered` membawa `customerRef`, bukan objek pelanggan lengkap — konsumen yang membutuhkannya memanggil Customer Capability.

**Alasan:** payload gemuk membuat perubahan skema entitas Enterprise memutus seluruh event lintas modul.

---

# BAB 13 — API STANDARD

## 13.1 Pilihan protokol

**[DESAIN]**

| Protokol | Penggunaan | Status |
|---|---|---|
| **REST + JSON** | Standar wajib untuk seluruh API modul | ✅ Default |
| **Event (async)** | Komunikasi antar modul | ✅ Default |
| **gRPC** | Hanya untuk jalur internal berperforma tinggi, dengan persetujuan Board | ⚠️ Pengecualian |
| **GraphQL** | **Tidak** di tingkat modul. Bila dibutuhkan, ia kapabilitas agregasi milik Enterprise | ❌ |

**Alasan menolak GraphQL per-modul:** setiap modul mengekspos skema sendiri akan memaksa klien menyatukan puluhan skema — persoalan yang sama yang seharusnya diselesaikan platform, bukan diperbanyak.

## 13.2 Standar wajib

| Aspek | Aturan |
|---|---|
| **Versioning** | `/api/{version}/{moduleNamespace}` — mis. `/api/v1/cm` ([FAKTA] DEC-020) |
| **Envelope sukses** | `{ "data": ..., "meta": { ... } }` |
| **Envelope error** | `{ "code": "STRING_CODE", "message": "...", "details": {...} }` — [FAKTA] sudah konsisten di modul pertama |
| **Kode error** | Huruf besar, stabil, tidak pernah berubah makna |
| **Pagination** | **Satu** konvensi: `page` + `pageSize`, respons memuat `totalItems` |
| **Sorting** | `sort=field:asc,field2:desc` |
| **Filtering** | Query param eksplisit; tanpa bahasa query bebas |
| **Idempotency** | Header `Idempotency-Key` **wajib** pada seluruh POST yang mengubah state |
| **Correlation** | Header `X-Correlation-Id` diterima & diteruskan |
| **Internal API** | Prefix `/internal/` — tidak pernah diekspos publik |
| **Contract test** | **Wajib** — spec dibandingkan implementasi berjalan di CI |

## 13.3 API yang dilarang dimiliki modul

**[DESAIN]** Modul **tidak boleh** mengekspos: autentikasi · manajemen pengguna · manajemen organisasi · konfigurasi lintas-modul · audit store · pengiriman notifikasi · endpoint yang menulis data milik modul lain.

---

# BAB 14 — SECURITY MODEL

## 14.1 Pipeline standar

**[DESAIN]** Urutan **wajib** untuk setiap modul, setiap tahap fail-closed:

```
Token ──► [1] IDENTITY ADAPTER
              signature · iss/aud/exp/nbf · klaim wajib · alg pinning
              ↓ ExternalUserRef
          [2] ENTITLEMENT GATE          ── tanpa entitlement → 403
              ↓
          [3] IDENTITY CORRELATION      ── external ref → profil lokal (JIT)
              ↓ Principal
          [4] PERMISSION CHECK          ── matrix milik modul, dari DB → 403
              ↓
          [5] ORGANIZATION SCOPE        ── hierarkis → 403
              ↓
          [6] DATA SCOPE                ── di REPOSITORY, bukan opsional
              ↓
          Use case
```

## 14.2 Aturan tak dapat ditawar

| # | Aturan | Alasan berbasis pengalaman |
|---|---|---|
| A1 | **Modul tidak pernah menerbitkan kredensial atau token** | Permukaan kredensial lokal = jalur memperoleh sesi tanpa SSO/MFA/audit |
| A2 | **Permission tidak pernah berasal dari token** | [FAKTA] modul pertama sudah menerapkan ini — dipertahankan sebagai standar |
| A3 | **Peran enterprise tidak otomatis menjadi peran modul** | [FAKTA] `RoleMapper` modul pertama menolak `ADMIN`/`SUPER_ADMIN` dari klaim IdP. Realm dikelola tim lain — pass-through = privilege escalation |
| A4 | **Entitlement adalah gate terpisah dari autentikasi** | Autentikasi berhasil ≠ berhak masuk modul |
| A5 | **Data scope ditegakkan di repository** | [FAKTA] pendekatan opt-in menghasilkan nol pemakaian di modul pertama |
| A6 | **Tidak ada FK ke entitas Enterprise** | [FAKTA] 16 FK ke `users.id` menjadi utang saat identitas berpindah |
| A7 | **Secret hanya dari environment/vault; redaksi menyeluruh** | [FAKTA] modul pertama sudah menerapkan — dijadikan standar |
| A8 | **Konfigurasi divalidasi fail-fast saat startup** | [FAKTA] pola terbukti; kesalahan tertangkap sebelum melayani trafik |

## 14.3 Model izin

**[DESAIN]** Format kode izin: `{resource}:{action}` — mis. `complaints:escalate`. Izin dideklarasikan di manifest, disimpan modul, dan **dipetakan ke peran oleh modul**, bukan oleh Enterprise. Enterprise memiliki *siapa boleh masuk*; modul memiliki *boleh melakukan apa*.

## 14.4 Data Scope standar

| Level | Arti |
|---|---|
| `own` | Hanya objek yang dibuat/ditugaskan ke principal |
| `unit` | Objek pada unit organisasi principal |
| `unit-subtree` | Unit principal beserta seluruh turunannya |
| `all` | Seluruh objek dalam modul |

**[DESAIN]** Penegakan: setiap metode repository menerima `ScopeFilter`. **Test arsitektur wajib** memindai seluruh repository dan menggagalkan build bila ada yang tidak menerapkannya.

## 14.5 Audit

Modul **menerbitkan** event audit; Enterprise **menyimpan**. Modul tidak memiliki audit store. Riwayat domain (timeline) tetap milik modul karena ia bagian dari domain, bukan log sistem.

---

# BAB 15 — FRONTEND PLATFORM

## 15.1 Pembagian tanggung jawab

| Lapisan | Pemilik | Isi |
|---|---|---|
| **Enterprise Shell** | HOST | Chrome aplikasi, header, sidebar, user menu, notifikasi global |
| **Layout** | HOST | Grid, responsive, area konten |
| **Navigation** | HOST | Menu dirakit dari manifest seluruh modul |
| **Theme / Design tokens** | HOST | Warna, tipografi, spacing, mode gelap |
| **Design System** | HOST | Komponen primitif berversi |
| **Shared Component** | HOST | Button, Input, Modal, Table, Toast, Form, DatePicker |
| **Business Component** | **GUEST** | Komponen ber-makna domain |
| **Feature Module** | **GUEST** | Halaman & alur domain |
| **Module Adapter** | **GUEST** | Satu-satunya titik kontak ke host |

## 15.2 Module Adapter — pola wajib

**[DESAIN]** Setiap modul memiliki tepat satu folder `platform/` yang menjadi **anti-corruption layer UI**:

```
frontend/src/
├── module.manifest.ts
├── entry.tsx                 ← satu titik mount
├── features/                 ← business component & pages (milik modul)
├── domain/                   ← tipe & aturan tampilan
├── api/                      ← klien HTTP domain
└── platform/                 ← SATU-SATUNYA kontak ke host
    ├── ui.ts                 re-export design system host
    ├── auth.ts               useCurrentUser, usePermissions
    ├── navigation.ts         useNavigate, breadcrumb
    ├── notification.ts       toast
    ├── config.ts
    └── i18n.ts
```

**Aturan:** tidak ada file di luar `platform/` yang boleh mengimpor dari host. Ditegakkan lint rule.

**Manfaat:** saat host mengganti design system atau versi framework, hanya satu folder berubah.

## 15.3 Metode integrasi

**[BUTUH INFO] — kritikal, HOST SIDE**

| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **Module Federation** | Rilis independen, satu DOM, performa baik | Perlu keseragaman framework & versi |
| **Iframe** | Isolasi kuat, framework bebas | Navigasi, tema, dan tinggi sulit; UX terasa terpisah |
| **Route mount (build-time)** | Sederhana, type-safe | Modul terikat siklus rilis host |
| **Web Components** | Framework agnostik | Ergonomi & styling lebih sulit |

**[DESAIN] Rekomendasi:** **Module Federation** bila host dan seluruh modul memakai framework yang sama; **Web Components** bila keberagaman framework adalah kebutuhan nyata.

**[ASUMSI]** Host memakai React. **Bila salah, seluruh BAB 15 dan biaya frontend seluruh modul berubah drastis.** Ini informasi yang harus dikonfirmasi lebih dulu dari semuanya.

---

# BAB 16 — BACKEND PLATFORM

## 16.1 Gaya arsitektur wajib

**[DESAIN]** Setiap modul: **Modular Monolith internal + Hexagonal (Ports & Adapters)**, satu deployable unit per modul.

**Alasan:** modul adalah unit rilis; membelah satu modul menjadi banyak servis menambah biaya operasi tanpa manfaat, karena batas yang penting sudah ada di tingkat modul.

## 16.2 Struktur standar

```
backend/app/
├── bootstrap/          wiring, DI, lifespan, mode selection
├── domain/             MURNI — tanpa framework/ORM/HTTP
│   ├── <aggregate>/    entity, VO, event, rule, repository port
│   └── shared/
├── application/        use case, orkestrasi, DTO
├── ports/              KONTRAK KELUAR (Protocol saja)
├── adapters/
│   ├── enterprise/     produksi
│   ├── standalone/     dev/CI
│   └── inmemory/       test
├── infrastructure/     persistence milik modul + outbox
├── api/                HTTP adapter + /internal
└── security/           pipeline BAB 14
```

## 16.3 Aturan dependensi (wajib, ditegakkan test arsitektur)

| # | Aturan |
|---|---|
| D1 | `domain` hanya mengimpor `domain/shared` + stdlib |
| D2 | `application` → `domain` + `ports`. Tidak ke `adapters`/`infrastructure`/`api` |
| D3 | `adapters` → `ports`. Tidak ke `domain` internal / `application` |
| D4 | `api` → `application`. Tidak ke `domain` langsung |
| D5 | `security` tidak pernah diimpor `domain` |
| D6 | Pengecekan mode hanya di `adapters` + `bootstrap` (P9) |
| D7 | Tidak ada import lintas modul (P4) |

**[FAKTA] pelajaran:** modul pertama melanggar D5 — `core/authorization/*` mengimpor `modules/iam` dan `modules/audit`, sehingga `core` tidak dapat diekstrak. Aturan ini lahir dari kesalahan itu.

## 16.4 Repository & persistence

**[DESAIN]** Port repository di `domain`; implementasi di `infrastructure`. Satu transaksi = satu aggregate. Konsistensi lintas-aggregate lewat domain event. Objek domain **immutable** — [FAKTA] modul pertama memakai `@dataclass(frozen=True, slots=True)`; dijadikan standar.

## 16.5 Test arsitektur wajib

**[DESAIN]** Setiap modul wajib memiliki `tests/architecture/` yang menggagalkan build bila: aturan D1–D7 dilanggar · ada repository tanpa `ScopeFilter` · ada rute tanpa security dependency · ada FK ke entitas Enterprise · ada pengecekan mode di luar `adapters`/`bootstrap`.

**Alasan:** aturan arsitektur yang hanya ditulis akan dilanggar. Yang diuji, tidak.

---

# BAB 17 — DATABASE MODEL

## 17.1 Kepemilikan

**[DESAIN]**

| # | Aturan |
|---|---|
| DB1 | Setiap modul memiliki **skema eksklusif**. Tidak ada modul membaca skema modul lain |
| DB2 | **Tidak ada tabel shared.** Bila dua modul membutuhkan data yang sama, ia milik Enterprise |
| DB3 | **Tidak ada FK lintas kepemilikan** — ke Enterprise maupun ke modul lain |
| DB4 | Migrasi milik modul, dijalankan sebagai **job terpisah**, bukan di entrypoint aplikasi |
| DB5 | Setiap migrasi wajib punya `downgrade` — [FAKTA] modul pertama 44/44 memenuhi |

## 17.2 Reference data & cache

**[DESAIN]** Modul boleh menyimpan cache referensi entitas Enterprise dengan aturan ketat:

| Aturan | Isi |
|---|---|
| Penamaan | Prefix `ref_` — mis. `ref_org_units`, `ref_users` |
| Kolom wajib | `external_id`, `last_synced_at` |
| Sifat | **Hanya-baca** bagi modul |
| FK | **Tidak boleh** menjadi target FK dari tabel domain |
| Basi | Melewati ambang → operasi yang bergantung padanya **fail-closed** |
| Sinkronisasi | Event `*Changed` + rekonsiliasi berkala |

## 17.3 Deployment database

**[DESAIN]** Dua opsi sah:

| Opsi | Kapan |
|---|---|
| **Skema terpisah dalam satu instance** | Default — sederhana, transaksi cepat, batas ditegakkan izin skema |
| **Database terpisah per modul** | Bila kebutuhan isolasi/regulasi/skala menuntutnya |

Keduanya menjaga DB1–DB3. **[ASUMSI]** Opsi pertama cukup untuk mayoritas modul.

---

# BAB 18 — OBSERVABILITY

**[DESAIN]** Prinsip: **modul menghasilkan sinyal; Enterprise memiliki penyimpanan, dashboard, dan alert.**

| Pilar | GUEST wajib menghasilkan | HOST wajib menyediakan |
|---|---|---|
| **Logging** | JSON terstruktur ke stdout; `correlationId` di setiap baris; tanpa PII/secret | Sink, retensi, pencarian |
| **Metrics** | `/internal/metrics` — RED per endpoint + metrik domain berprefix `{module}_` | Scraper, storage, dashboard |
| **Tracing** | Span OpenTelemetry; propagasi trace context dari host | Collector, backend, UI |
| **Health** | `/internal/live`, `/internal/ready`, `/internal/ready/deep` | Prober, orkestrasi |
| **Alert** | Deklarasi kondisi alert di manifest | Alertmanager, routing, on-call |
| **Audit** | Event audit domain | Store, non-repudiation |
| **Dashboard** | Definisi metrik | Permukaan & distribusi |

## 18.1 Metrik standar wajib setiap modul

```
{module}_http_requests_total{method,route,status}
{module}_http_request_duration_seconds{method,route}
{module}_domain_events_published_total{event}
{module}_outbox_pending
{module}_enterprise_adapter_failures_total{capability}
{module}_enterprise_adapter_duration_seconds{capability}
```

**[DESAIN]** `enterprise_adapter_failures_total` adalah metrik terpenting di daftar ini: ia satu-satunya cara mendeteksi bahwa kontrak antara host dan guest sedang rusak.

---

# BAB 19 — DEVOPS

## 19.1 CI wajib setiap modul

| Gate | Blocking |
|---|---|
| Lint | ✅ |
| Type check | ✅ |
| Unit test + coverage (ambang per modul, minimal 80%) | ✅ |
| Integration test terhadap database nyata | ✅ |
| **Test arsitektur** (BAB 16.5) | ✅ |
| **Contract test** — OpenAPI ↔ implementasi | ✅ |
| **Contract test** — event ↔ skema | ✅ |
| **Manifest validation** terhadap JSON Schema | ✅ |
| Migrasi maju + mundur | ✅ |
| SAST, secret scanning, dependency audit | ✅ |
| Container scan + SBOM | ✅ |
| **Matriks mode**: `standalone` + `enterprise` | ✅ |
| E2E alur kritis | ✅ (modul matang) |
| a11y, bundle budget | ⚠️ warning |

## 19.2 CD

**[DESAIN]** Build di CI → push ke registry → deploy dari **image tag**, tidak pernah build di host produksi. Image ditandatangani; SBOM dilampirkan; provenance (commit, branch, tree state) di-bake sebagai OCI label — [FAKTA] pola ini sudah ada di modul pertama.

## 19.3 Versioning & kompatibilitas

| Perubahan | Bump |
|---|---|
| Perbaikan internal | PATCH |
| Fitur baru, kontrak kompatibel | MINOR |
| Perubahan kontrak API/event/izin | **MAJOR** + deprecation satu rilis |

**[DESAIN] Matriks kompatibilitas** modul ↔ platform dideklarasikan di manifest dan diverifikasi Registry saat pendaftaran. Registry **menolak** modul yang tidak kompatibel — kegagalan terjadi saat registrasi, bukan saat runtime.

## 19.4 Rollback

Setiap rilis wajib: migrasi `downgrade` teruji · image versi sebelumnya tetap tersedia · kontrak versi sebelumnya masih didukung · runbook rollback terverifikasi.

---

# BAB 20 — GOVERNANCE

## 20.1 Organ

| Organ | Wewenang |
|---|---|
| **Architecture Board** | Menyetujui standar platform, kepemilikan kapabilitas, pengecualian |
| **Platform Owner** | Memelihara SDK, Registry, Capability Registry |
| **Module Owner** | Memiliki domain, kontrak, dan roadmap modulnya |
| **Security Architect** | Memvalidasi pipeline keamanan setiap modul |

## 20.2 Registri wajib

| Registri | Isi | Pemilik |
|---|---|---|
| **Capability Registry** | Seluruh kapabilitas, pemilik, kontrak, konsumen | Platform Owner |
| **Module Registry** | Seluruh modul, versi, status, manifest | Platform Owner |
| **ADR Repository** | Keputusan arsitektur platform & modul | Architecture Board |
| **Contract Repository** | OpenAPI, skema event, katalog izin | Platform Owner |

## 20.3 Proses

**[DESAIN]** Modul baru melewati empat gerbang (detail BAB 21): **G0** Capability Ownership disetujui · **G1** Kontrak disetujui · **G2** Implementasi memenuhi Quality Gate · **G3** Registrasi & aktivasi.

## 20.4 Deprecation

**[DESAIN]** Kontrak yang di-deprecate: diumumkan minimal **satu rilis mayor** sebelumnya · pengganti tersedia sebelum pengumuman · konsumen diberi tahu lewat Registry · penghapusan memerlukan Board Resolution.

## 20.5 Pengecualian

Setiap penyimpangan dari standar ini memerlukan **Exception Request** tertulis dengan: alasan, dampak, mitigasi, dan **tanggal kedaluwarsa**.

**[DESAIN] Aturan:** pengecualian tanpa tanggal kedaluwarsa **tidak boleh disetujui**. [FAKTA] pelajaran dari modul pertama: gate lint ditandai *"non-blocking until burn-down"* tanpa tanggal, dan bertahan berbulan-bulan hingga 134 temuan menumpuk.

---

# BAB 21 — QUALITY GATE

## G0 — Boundary (sebelum baris kode pertama)

- [ ] Kelayakan modul lolos pohon keputusan BAB 4
- [ ] Capability Ownership Matrix disusun & **disetujui bilateral**
- [ ] Tidak ada tabrakan konsep di Capability Registry
- [ ] Bounded Context & ubiquitous language terdokumentasi
- [ ] Pemilik bisnis & teknis ditetapkan

## G1 — Contract (sebelum implementasi)

- [ ] Module Manifest lolos validasi skema
- [ ] OpenAPI ditulis dan direview
- [ ] Skema event ditulis dan direview
- [ ] Katalog izin ditetapkan
- [ ] Kapabilitas yang dikonsumsi + `failureMode` dideklarasikan
- [ ] **Contoh payload nyata** dari setiap kapabilitas host telah diterima

## G2 — Implementation

**Arsitektur**
- [ ] Aturan dependensi D1–D7 lolos test arsitektur
- [ ] Seluruh kapabilitas eksternal lewat port
- [ ] Tiga implementasi adapter tersedia (enterprise/standalone/inmemory)
- [ ] Pengecekan mode hanya di `adapters`/`bootstrap`

**Keamanan**
- [ ] Pipeline BAB 14 lengkap dan berurutan
- [ ] Modul tidak menerbitkan kredensial/token
- [ ] Permission tidak pernah dari token
- [ ] Peran enterprise tidak otomatis menjadi peran modul
- [ ] Entitlement Gate default-deny **dengan test yang membuktikan penolakan**
- [ ] Data scope di repository + test arsitektur
- [ ] Org scope hierarkis teruji
- [ ] Tidak ada FK ke entitas Enterprise
- [ ] Secret dari environment/vault; redaksi aktif
- [ ] Konfigurasi fail-fast saat startup

**Data**
- [ ] Skema eksklusif; tidak ada tabel shared
- [ ] Reference cache mengikuti aturan BAB 17.2
- [ ] Migrasi punya `downgrade`; dijalankan sebagai job terpisah

**Kontrak**
- [ ] Contract test API ↔ implementasi hijau
- [ ] Contract test event ↔ skema hijau
- [ ] Outbox + DLQ replay berfungsi
- [ ] Konsumen event idempoten (terbukti test duplikat)

**Frontend**
- [ ] Tidak ada shell, tema, navigasi, atau halaman auth di modul
- [ ] Satu `entry` + `module.manifest`
- [ ] Seluruh kontak host lewat `platform/`; lint rule aktif

**Observability**
- [ ] Log JSON ber-korelasi tanpa PII
- [ ] Metrik standar BAB 18.1 tersedia
- [ ] Tracing dengan propagasi context
- [ ] Health live/ready/deep

**Kualitas**
- [ ] Coverage ≥ ambang
- [ ] CI hijau pada matriks `standalone` + `enterprise`
- [ ] SAST, secret scan, container scan, SBOM hijau
- [ ] E2E alur kritis hijau

## G3 — Registration

- [ ] Manifest terdaftar tanpa tabrakan
- [ ] Kompatibilitas versi terverifikasi
- [ ] Uji lifecycle enable → disable → enable lulus
- [ ] Uji upgrade & rollback lulus
- [ ] Runbook operasional tersedia
- [ ] Backup & restore terverifikasi
- [ ] Alert terdaftar & on-call ditetapkan

---

# BAB 22 — REFERENCE IMPLEMENTATION

Complaint Management Module (`EA-TARGET-CM-001`) sebagai implementasi pertama.

## 22.1 Yang REUSABLE menjadi standar platform

| # | Pola | Asal | Status |
|---|---|---|---|
| 1 | **Enterprise owns Capability, Module owns Meaning** | Resolusi konflik kepemilikan | ✅ Prinsip P1 |
| 2 | **Identity Adapter** sebagai penutup divergensi mode | [FAKTA] ADR-014 v1.4 | ✅ Prinsip P9 |
| 3 | **Permission tidak pernah dari token** | [FAKTA] `PermissionResolver` | ✅ Aturan A2 |
| 4 | **Penolakan peran privileged dari IdP** | [FAKTA] `RoleMapper` | ✅ Aturan A3 |
| 5 | **Port/adapter dengan tiga implementasi** | [FAKTA] `integrations/customer/` | ✅ BAB 16 |
| 6 | **Fail-fast configuration validation** | [FAKTA] `validate_runtime_config` | ✅ Aturan A8 |
| 7 | **Secret redaction menyeluruh** | [FAKTA] `SECRET_INVENTORY` | ✅ Aturan A7 |
| 8 | **Domain object immutable** | [FAKTA] `frozen=True, slots=True` | ✅ BAB 16.4 |
| 9 | **Event Catalog sebagai SoT normatif + at-least-once + idempoten** | [FAKTA] EVT-CAT-001 v0.7 | ✅ BAB 12 |
| 10 | **Migrasi linear dengan `downgrade` 100%** | [FAKTA] 44/44 | ✅ Aturan DB5 |
| 11 | **Provenance build di OCI label** | [FAKTA] Dockerfile | ✅ BAB 19.2 |
| 12 | **Probe live/ready terpisah** | [FAKTA] `api/health.py` | ✅ BAB 18 |
| 13 | **Governance-as-code** (ADR, DEC, Board, RTM) | [FAKTA] folder governance | ✅ BAB 20 |

## 22.2 Anti-pola yang menjadi aturan larangan

| # | Kesalahan modul pertama | Menjadi |
|---|---|---|
| 1 | 16 FK ke `users.id` | Aturan A6 / DB3 |
| 2 | Data scope opt-in → **0 pemakaian** | Prinsip P7 + test arsitektur |
| 3 | ±15.100 LOC kapabilitas Enterprise dibangun ulang | Prinsip P10 + Gate G0 |
| 4 | Tiga model domain paralel tanpa tanggal pensiun | Aturan strangler bertanggal |
| 5 | `core` mengimpor `modules` | Aturan D5 |
| 6 | Kontrak identitas tanpa contoh payload nyata | Kewajiban host BAB 11.2 |
| 7 | Gate lint non-blocking tanpa tanggal | Aturan pengecualian BAB 20.5 |
| 8 | OpenAPI divalidasi sintaks saja | Contract test wajib BAB 19.1 |
| 9 | Frontend dengan shell & login sendiri | BAB 15 |
| 10 | Migrasi di entrypoint aplikasi | Aturan DB4 |

## 22.3 Yang SPESIFIK Complaint — tidak boleh digeneralisasi

| Elemen | Alasan tidak generik |
|---|---|
| SLA policy & breach detection | Tidak semua domain punya komitmen waktu |
| Eskalasi berjenjang cabang → pusat | Bentuk hierarki spesifik proses keluhan |
| Timeline sebagai konsep domain | Modul lain mungkin cukup dengan audit |
| Queue / tiket kunjungan | Sangat spesifik layanan tatap muka |
| Appointment | Terikat proses keluhan lapangan |
| Duplicate detection | Spesifik karakteristik keluhan |

**[DESAIN] Peringatan:** godaan terbesar setelah modul pertama adalah menaikkan SLA, eskalasi, dan timeline menjadi kapabilitas platform. **Jangan** — sampai minimal dua modul lain terbukti membutuhkannya dalam bentuk yang sama.

---

# BAB 23 — ROADMAP

> **Framing Board:** roadmap di bawah = *usulan evolusi kontrak/platform*, **bukan** jadwal implementasi ECMP Mode B. Rilis v0.1+ bergantung **G-HOST** (Lampiran A Closed) + co-ownership EP + (untuk pekerjaan guest Mode B) pembukaan **C-7**.

| Rilis | Fokus | Isi | Durasi | Gate |
|---|---|---|---|---|
| **v0.1** — Kontrak minimum | Kesepakatan | BAB 0 diselesaikan; Capability Registry v1; skema Manifest; kontrak Identity + Entitlement + Organization | 4 minggu | **G-HOST** mulai; **tanpa** coding Mode B di ECMP |
| **v0.5** — Modul pertama patuh | Validasi | Complaint Module memenuhi G0–G3; Registry manual; SDK identity/authz/config | 12 minggu | **POST C-7** untuk adapter enterprise |
| **v1.0** — Platform operasional | Generalisasi | Registry otomatis; SDK lengkap; frontend shell + module adapter; observability; CI template; **divalidasi modul kedua** | 16 minggu | Modul #2 + Board BASELINE |
| **v1.5** — Skala | Kematangan | Lifecycle penuh (upgrade/rollback/retire); versioning kontrak; deprecation; 3–5 modul aktif | 12 minggu | — |
| **v2.0** — Otonomi | Kemandirian | Self-service onboarding modul; katalog kapabilitas mandiri; governance otomatis; template modul; > 8 modul | 16 minggu | — |

**Total ±60 minggu (±14 bulan)** menuju v2.0 — estimasi *setelah* HOST commitments, bukan mulai coding hari ini.

**[DESAIN] Gerbang wajib menuju v1.0:** platform **tidak boleh** dinyatakan v1.0 sebelum **modul kedua yang berbeda karakternya** berhasil dipasang. Satu implementasi tidak membuktikan apa pun tentang generalitas.

---

# BAB 24 — FINAL RECOMMENDATION

## 24.1 Evolusi lima tahun

**Tahun 1 — Kontrak.** Dua sampai tiga modul. Fokus: membuktikan bahwa kontrak host–guest benar. Sebagian besar pekerjaan adalah negosiasi, bukan koding. Ukuran keberhasilan: modul kedua lebih cepat dari modul pertama.

**Tahun 2 — Konsistensi.** Lima sampai delapan modul. Pola stabil, SDK matang, template modul lahir. Muncul godaan pertama menaikkan hal domain-spesifik ke platform — **tahan**. Ukuran: waktu onboarding modul baru turun di bawah 40% modul pertama.

**Tahun 3 — Otonomi.** Sepuluh modul atau lebih. Tim modul beroperasi mandiri; platform menjadi produk dengan pengguna internal, roadmap, dan SLA sendiri. Ukuran: tim modul tidak lagi perlu bertanya ke tim platform untuk memulai.

**Tahun 4 — Konsolidasi.** Kapabilitas duplikat yang menyelinap dibersihkan; kontrak lama dipensiunkan; modul pertama kemungkinan perlu ditulis ulang mengikuti standar yang telah matang. **Rencanakan ini sejak sekarang** — modul pertama selalu menjadi yang paling tidak patuh.

**Tahun 5 — Pembaruan.** Platform v3 mempertimbangkan perubahan teknologi. Nilai sesungguhnya terbukti di sini: bila kontrak dirancang benar, mengganti teknologi host tidak memaksa menulis ulang modul.

## 24.2 Risiko terbesar

| Peringkat | Risiko | Mengapa paling berbahaya | Mitigasi |
|---|---|---|---|
| **1** | **Platform dirancang untuk satu modul** | Complaint Module berat pada SLA, eskalasi, dan workflow. Standar yang mengabadikan bentuk itu akan menyiksa Analytics Module dan AI Module | Gerbang v1.0: wajib divalidasi modul kedua yang berbeda karakternya |
| **2** | **Sisi HOST tidak pernah dibangun** | Dokumen ini menuntut Registry, SDK, dan shell dari Enterprise Application — yang mungkin tidak memiliki roadmap untuk itu | BAB 0: co-ownership Enterprise App Owner sebagai prasyarat SoT |
| **3** | **Platform menjadi bottleneck** | Bila setiap perubahan modul memerlukan perubahan platform, kecepatan seluruh organisasi ditentukan satu tim | Prinsip S5: kontrak wajib, SDK opsional. Modul boleh mengimplementasikan kontrak sendiri |
| **4** | **Standar tanpa penegakan** | [FAKTA] terbukti di modul pertama: data scope dibangun lengkap lalu tidak pernah dipakai | Setiap aturan wajib punya test arsitektur atau gate CI. Aturan tanpa alat deteksi dihapus dari dokumen |
| **5** | **Second-system effect** | Setelah menemukan modul pertama salah arah, godaan membangun platform sempurna sangat besar | Roadmap bertahap; v0.1 hanya kontrak minimum |
| **6** | **Pengecualian menjadi permanen** | [FAKTA] gate lint "non-blocking until burn-down" bertahan berbulan-bulan | Pengecualian tanpa tanggal kedaluwarsa tidak boleh disetujui |

## 24.3 Tiga keputusan desain terpenting

**Keputusan 1 — "Enterprise owns Capability, Module owns Meaning" sebagai prinsip induk.**
Ia menyelesaikan pertanyaan kepemilikan yang selama ini paling banyak memicu perdebatan, dan melakukannya tanpa memaksa salah satu pihak mengalah. Setiap kapabilitas dipecah menjadi mekanisme dan semantik. Tanpa prinsip ini, setiap modul baru mengulang perdebatan yang sama dari nol.

**Keputusan 2 — Penegakan di lapisan yang tidak dapat dilewati.**
Data scope di repository, aturan dependensi di test arsitektur, kontrak di contract test, manifest di Registry. Ini pelajaran termahal dari modul pertama: sebuah kontrol keamanan yang dibangun lengkap namun bersifat opsional menghasilkan **nol** pemakaian. Kontrol yang dapat dilewati adalah kontrol yang tidak ada.

**Keputusan 3 — Kontrak wajib, SDK opsional.**
SDK yang wajib menjadikan tim platform sebagai jalur kritis bagi setiap modul, dan menjadikan bug SDK sebagai insiden seluruh organisasi. Dengan mewajibkan kontrak dan menjadikan SDK sekadar kemudahan, modul tetap dapat bergerak ketika platform tertinggal — dan platform tetap dapat berevolusi tanpa memutus semua modul sekaligus.

## 24.4 Rekomendasi akhir

**Jangan mulai dari platform. Mulai dari kontrak.**

Godaan terbesar saat ini adalah membangun Registry, SDK, dan shell terlebih dahulu. Itu urutan yang salah. Yang menghasilkan nilai bukan perkakasnya, melainkan kesepakatan tentang siapa memiliki apa.

Tiga langkah pertama, berurutan:

1. **Bawa Enterprise Application Owner ke meja.** Tanpa co-ownership, dokumen ini adalah standar internal satu tim. Konfirmasi lebih dulu apakah Enterprise Application sudah memiliki model ekstensi — bila ya, dokumen ini menyesuaikan diri, bukan menggantikan.

2. **Bangun Capability Registry sebelum Module Registry.** Daftar "siapa memiliki apa" bernilai lebih besar daripada mekanisme pendaftaran modul, dan dapat dibuat minggu ini dengan spreadsheet.

3. **Selesaikan Complaint Module sampai G3 sebelum menstandarkan apa pun lagi.** Satu implementasi yang benar-benar tuntas mengajarkan lebih banyak daripada sepuluh dokumen. Setiap aturan di dokumen ini yang tidak terbukti berguna saat menuntaskan modul pertama, **hapus**.

Dan satu hal yang perlu diterima sejak awal: **modul pertama akan menjadi yang paling tidak patuh terhadap standar yang ia lahirkan sendiri.** Itu wajar. Rencanakan penulisan ulangnya di Tahun 4, dan jangan menahan standar ini agar tetap kompatibel dengan kesalahan modul pertama.

---

## Lampiran A — Informasi yang belum tersedia

| Kode | Informasi | Penyedia | Memblokir |
|---|---|---|---|
| H1 | Apakah Enterprise Application sudah punya model modul/ekstensi | Enterprise App Owner | **Seluruh dokumen** |
| H2 | Stack & versi framework host | Enterprise App Owner | BAB 10, 15 |
| H3 | Apakah Module Registry akan dibangun | Enterprise App Owner | BAB 6 |
| H4 | Teknologi event bus & kontrak DLQ | Enterprise App Owner | BAB 12 |
| H5 | Metode embed UI | Enterprise App Owner | BAB 15 |
| H6 | Mekanisme entitlement | Enterprise App Owner | BAB 14 |
| H7 | Model organisasi & API | Enterprise App Owner | BAB 11, 17 |
| H8 | Sink observability | Enterprise DevOps | BAB 18 |
| H9 | Contoh payload nyata setiap kapabilitas | Enterprise App Owner | BAB 11, Gate G1 |
| H10 | Modul kedua sebagai validator | Portfolio Owner | Gerbang v1.0 |

## Lampiran B — Prasyarat status SoT

Dokumen ini menjadi Single Source of Truth setelah: BAB 0 §0.3 terpenuhi · H1–H9 terjawab · sisi HOST masuk roadmap Enterprise Application · minimal dua modul memvalidasi · Architecture Board menerimanya sebagai `EA-PLATFORM-001 v1.0`.

**Sampai itu, dokumen ini adalah usulan standar bersama — bukan standar yang berlaku.**

---

*Dokumen desain arsitektur. Tidak ada file repository yang diubah dalam penyusunannya.*

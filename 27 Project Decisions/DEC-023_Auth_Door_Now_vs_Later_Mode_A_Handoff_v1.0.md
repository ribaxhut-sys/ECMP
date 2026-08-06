# Decision Record — Pintu auth: sekarang vs nanti (Mode A → Mode B handoff)

| Field | Value |
|---|---|
| ID | DEC-023 |
| Version | 1.1 |
| Owner | Product / Solution Architect |
| Reviewer | Business Owner |
| Approver | Business Owner |
| Status | 🟢 Accepted (ops / stakeholder working agreement) |
| Last Review | 2026-08-04 |
| Next Review | 2026-11-04 |

- Type: Project Decision (non-ADR)
- Status: Accepted (working agreement — **bukan** unlock Mode B)
- Date: 2026-08-04

## Context

Stakeholder ingin kelak login lewat Enterprise Platform (“mall”), lalu pilih Pengaduan.
Sementara host lab memakai domain `layanankami.tech`, muncul godaan membangun portal/login
seolah Enterprise sudah ada di apex domain.

Fleksibilitas yang diinginkan **benar**: saat Enterprise asli datang, yang diganti hanya
mekanisme masuk — bukan domain complaint. Cara yang salah: membangun “mall mini” di ECMP
yang nanti dibongkar.

## Decision

**Opsi: fleksibel di pintu auth (adapter), bukan membangun portal Enterprise palsu.**

### 1. Dua alamat (jangan dicampur)

| Peran (asumsi kerja) | URL | Pemilik niat |
|---|---|---|
| Portal Enterprise (stand-in mental / landing lab) | `https://layanankami.tech` | Landing statis di VPS (Opsi A) — **bukan** produk SSO EP |
| Modul Pengaduan (toko) | `https://pengaduan.layanankami.tech` | ECMP Mode A lab |

Asumsi “apex = Enterprise” **hanya untuk diskusi desain + landing sementara**.
Implementasi lab Opsi A: DNS apex → VPS, halaman statis + link ke modul
(lihat `deploy/APEX_LANDING_CUTOVER_CHECKLIST.md`). Tidak berarti ECMP boleh
mengimplementasikan SSO produksi, module switcher enterprise, atau Identity Adapter.

### 2. Sekarang (Mode A — boleh dipakai)

1. User membuka `https://pengaduan.layanankami.tech/login`
2. Login lokal (username/password lab + JWT) — DEC-020 lab auth
3. Memakai siklus complaint di dalam modul
4. Tidak ada syarat “harus lewat portal dulu”

### 3. Nanti (Mode B — setelah Board unlock)

1. User login di **Enterprise Platform** (SSO / session EP)
2. Memilih modul Pengaduan di navigasi EP
3. EP mengarahkan ke modul (deep-link / embed — detail protokol: OD-FE-002 + ADR-016)
4. ECMP menerima identitas lewat **Identity Adapter** (ADR-014/015), lalu AuthZ internal modul
5. Domain complaint **tidak** diubah hanya karena ganti cara login

**Analogi target UX (bukan spesifikasi teknis / bukan tiket coding):** pola portal
seperti `https://coretax.jakarta.go.id/login` (SSO di host platform, lalu masuk layanan).
Untuk ECMP, setara mentalnya adalah login di apex/portal EP dulu, baru ke modul
Pengaduan. Landing lab di `layanankami.tech` hari ini **bukan** tiruan SSO itu —
hanya pintu + link. Meniru `/login` SSO Coretax di repo ECMP sebelum Board unlock
dan kontrak IdP = **dilarang** (lihat §6).

### 4. Apa yang tetap vs apa yang diganti

| Lapisan | Sekarang | Saat mall asli datang |
|---|---|---|
| Complaint lifecycle, SLA, assignment, UI modul | Tetap | Tetap |
| Role–permission internal ECMP | Tetap (setelah entitlement EP) | Tetap |
| Cara membuktikan “siapa user ini” | Login lokal Mode A | Token/session dari EP via Identity Adapter |
| Portal, menu modul, password/MFA enterprise | Tidak dibangun di ECMP | Milik EP |
| `ECMP_AUTH_MODE` / flag enterprise | `dev` + kredensial lokal (lab) | `jwt` + OIDC nyata (setelah kontrak EP + unlock) |

### 5. Yang harus Enterprise Platform sediakan nanti (gap — jangan dikarang di ECMP)

Sampai kontrak bilateral ada, ini **daftar dependency**, bukan spesifikasi final:

- Issuer / JWKS / audience produksi yang EP miliki
- Klaim identitas yang disepakati (mis. subject / `external_user_id`, org unit bila dipakai)
- Cara masuk ke modul (URL deep-link, header, cookie domain, atau embed)
- Entitlement “user boleh buka modul Pengaduan”
- Aturan session / logout lintas portal–modul

Tanpa artefak di atas dari pemilik platform, coding Mode B = mengarang kontrak.

### 6. Yang dilarang sampai Board unlock (C-7 / C-B6-1)

- Coding Identity Adapter runtime produksi / SSO UI / OpenAPI enterprise `securitySchemes`
- Membangun portal chrome atau “pilih Pengaduan” sebagai produk di repo ECMP
- Menganggap Accept ADR-016/017/018 = izin implementasi Mode B
- Memaksa `layanankami.tech` (apex) menjadi SoR login enterprise buatan ECMP

Desain kontrak, daftar gap, dan migration plan **boleh**. Coding Mode B **tidak**.

## Rationale

- Selaras North Star: yang berubah nanti hanya mekanisme integrasi.
- Mempertahankan Mode A lab yang sudah jalan di `pengaduan.layanankami.tech`.
- Menghindari utang “mall mini” yang tidak fleksibel di praktik.
- Titik ganti yang benar = Identity Adapter + auth mode, bukan rebuild modul.

## Impact

- Operasional hari ini: tetap pandu user ke `/login` di subdomain pengaduan.
- Backlog: Mode B tetap CLOSED; item ini hanya menajamkan handoff narrative.
- Tidak mengubah OpenAPI, event catalog, atau perilaku domain complaint.

## Follow-up

1. Pakai dokumen ini saat stakeholder bertanya “kenapa belum login dari portal”.
2. Saat EP menyerahkan kontrak identitas nyata → Impact Analysis + usulan Board unlock Mode B.
3. Setelah unlock → kerjakan adapter/protokol (OD-FE-002), bukan redesign complaint.

## Related

- DEC-020 (lab auth: local JWT now, SSO later) — *file collision ID dengan DEC-020 SoT; lihat collision register*
- ADR-014 (Business Module), ADR-015 (Identity Contract)
- ADR-016 / 017 / 018 (Accepted with Conditions; Mode B tetap CLOSED)
- OD-FE-002 (browser auth protocol — OPEN, runtime CLOSED)
- `deploy/README.md` (edge `pengaduan.layanankami.tech`)
- `deploy/evidence/Mode_B_Ready_To_Connect_Checklist_20260804.md` (hijau/kuning/merah siap sambung)

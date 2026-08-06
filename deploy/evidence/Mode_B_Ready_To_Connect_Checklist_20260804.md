# Siap sambung Mode B? — daftar cek 1 halaman

| Field | Value |
|---|---|
| Date | 2026-08-04 |
| Status | **MERAH — belum siap sambung** (Mode B CLOSED) |
| Tujuan | Jawab: “saat pintu Enterprise terbuka, apakah mudah dikoneksi?” |
| Bukan | Tiket coding SSO / Identity Adapter / portal EP |

Acuan: DEC-023, ADR-014/015, C-7 / C-B6-1, `Mode_B_Blocked_Pending_IdP_Contract_20260801.md`.

## Legenda

| Warna | Arti |
|---|---|
| **Hijau** | Sudah ada / selaras; memperlancar sambungan nanti |
| **Kuning** | Ada sebagian / desain ada; masih gap atau belum diverifikasi ke EP |
| **Merah** | Blokir — tanpa ini tidak boleh / tidak bisa sambung produksi |

---

## A. Fondasi modul (siapa yang kita kerjakan)

| # | Item | Warna | Catatan |
|---|---|---|---|
| A1 | Modul Pengaduan terpisah dari portal (`pengaduan.…`) | **Hijau** | Opsi A cutover 2026-08-04 |
| A2 | Domain complaint Mode A jalan (lab) | **Hijau** | Login lokal + health OK |
| A3 | Apex = pintu sementara, bukan SSO palsu | **Hijau** | Landing + link; analogi Coretax di DEC-023 v1.1 |
| A4 | AuthZ internal modul (role–permission) | **Hijau** | Milik ECMP; dipakai setelah entitlement EP |
| A5 | Gerbang config Mode B (`jwt` + `OIDC_*`) ada di kode | **Kuning** | Ada fail-fast; **jangan** diisi dengan IdP karangan |

## B. Pintu Enterprise (milik platform — bukan ECMP)

| # | Item | Warna | Catatan |
|---|---|---|---|
| B1 | Board unlock Mode B (C-7 / C-B6-1) | **Merah** | Masih CLOSED |
| B2 | Kontrak IdP bilateral tertulis (issuer, JWKS, audience) | **Merah** | Belum ada artefak EP terverifikasi di repo |
| B3 | Klaim identitas disepakati (`sub` / external user, org, dll.) | **Merah** | ADR-015 arsitektur OK; mapping EP belum ditandatangani |
| B4 | Org-gap / kewajiban bilateral (C-B6-3) | **Merah** | Prasyarat unlock |
| B5 | Cara masuk ke modul (deep-link / embed / cookie) | **Kuning** | OD-FE-002 OPEN; runtime CLOSED |
| B6 | Entitlement “boleh buka Pengaduan” | **Merah** | SoR di EP |
| B7 | Sign-off security lab→staging Mode B | **Merah** | Setelah kontrak ada |

## C. Setelah B hijau — kerja sambungan (barulah coding Mode B)

| # | Item | Warna | Catatan |
|---|---|---|---|
| C1 | Identity Adapter runtime | **Merah** | Dilarang sampai unlock |
| C2 | `ECMP_AUTH_MODE=jwt` + OIDC nyata | **Merah** | Setelah B2–B3 |
| C3 | Nonaktifkan credential login Mode A di env bersama | **Kuning** | Aturan sudah ada; aktif saat Mode B |
| C4 | Uji handoff portal → modul (seperti pola Coretax) | **Merah** | Butuh EP + unlock |

---

## Verdict hari ini

```text
Fondasi modul (A)     → sebagian besar HIJAU  → memudahkan sambungan nanti
Pintu Enterprise (B)  → MERAH                 → belum bisa “colok”
Kerja sambungan (C)   → MERAH / diblokir      → tunggu B
```

**Mudah dikoneksi?**  
→ **Ya, secara arsitektur modul** (rumah siap, pintu disiapkan).  
→ **Belum, secara operasional** sampai baris B1–B4 & B6–B7 hijau.

## Jangan

- Mengarang `OIDC_*` / realm lab seolah kontrak EP  
- Membangun tiruan `coretax…/login` di `layanankami.tech`  
- Menganggap Accept ADR-016/017/018 = Mode B terbuka  

## Lanjut Mode A (aman)

- UAT/login lab di `pengaduan.…`  
- Fitur & SIT dual-SoT complaint  
- Jaga boundary modul (DEC-023)

## Unblock (urut)

1. Org-gap + kontrak IdP dari pemilik platform  
2. Board Resolution unlock Mode B  
3. Baru C1–C4  

*Dokumen ini boleh di-update warna tanpa mengubah ADR/Board.*

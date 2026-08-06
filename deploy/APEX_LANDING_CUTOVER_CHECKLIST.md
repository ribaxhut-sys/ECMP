# Cutover — Opsi A: `layanankami.tech` → VPS (landing saja)

Status: **CUTOVER DONE** (2026-08-04) — DNS apex/www → VPS; Caddy landing + TLS OK.
Acuan: DEC-023 (pintu auth), modul tetap di `pengaduan.layanankami.tech`.

## Tujuan

| Host | Isi di VPS |
|---|---|
| `layanankami.tech` | Landing statis + tombol ke modul |
| `pengaduan.layanankami.tech` | ECMP Mode A (login lokal) — **tidak berubah** |

Bukan SSO. Bukan portal Enterprise produk. Bukan memindahkan modul ke apex.

## Prasyarat

- [ ] VPS IP publik diketahui (lab: `187.124.137.64`)
- [ ] Modul sudah hijau di `https://pengaduan.layanankami.tech/login`
- [ ] Artefak repo ada: `deploy/apex-landing/`, Caddy dual-host, `ECMP_APEX_DOMAIN` di compose

## Langkah DNS (panel Hostinger)

1. Buka DNS domain `layanankami.tech`.
2. Catat dulu A record apex saat ini (rollback).
3. Set **A** untuk `@` (apex) → `187.124.137.64`.
4. Opsional: **A** atau **CNAME** `www` → IP yang sama / ke apex.
5. **Jangan** ubah record `pengaduan` (tetap ke VPS).
6. Tunggu propagasi:

```bash
dig +short layanankami.tech A
# harus: 187.124.137.64
```

> Sebelum IP apex = VPS, **jangan** recreate Caddy untuk apex — ACME/Let’s Encrypt akan gagal.

## Langkah VPS (setelah DNS benar)

```bash
cd /opt/ECMP

# Pastikan .env.prod memuat (tanpa menghapus secret yang ada):
#   ECMP_APEX_DOMAIN=layanankami.tech
#   ECMP_DOMAIN=pengaduan.layanankami.tech

grep -E '^ECMP_APEX_DOMAIN=' .env.prod || echo 'ECMP_APEX_DOMAIN=layanankami.tech' >> .env.prod

docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d caddy
```

## Verifikasi

```bash
curl -sSI https://layanankami.tech/ | head -15
# harap: HTTP/2 200, via Caddy (bukan Hostinger Website Builder)

curl -sS https://layanankami.tech/ | grep -o 'Masuk ke Pengaduan'

curl -sSI https://pengaduan.layanankami.tech/login | head -10
# modul tetap 200
```

Browser: buka `https://layanankami.tech` → klik **Masuk ke Pengaduan** → land di `/login` modul.

## Setelah sukses

- [ ] Nonaktifkan / abaikan situs Hostinger Website Builder untuk apex (DNS sudah tidak ke sana)
- [ ] Jangan bangun login SSO di apex

## Rollback DNS

Kembalikan A record `@` ke nilai Hostinger sebelumnya. Landing VPS tidak lagi terpanggil; modul di `pengaduan.…` tetap jalan.

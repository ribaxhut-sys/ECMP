# Full Lab Backup Checklist (VPS)
Version: 1.0  
Date: 2026-07-31  
Class: Operations checklist (planning) — **commands listed, not executed by this document**  
Related: `Host_Domain_Migration_Checklist_20260731.md` · SEC-BASE-001 §9 · `deploy/backup-postgres.sh`

| Field | Value |
|---|---|
| Purpose | Cadangan lengkap lab sebelum pindah domain/VPS atau DR |
| Scope | Host lab ECMP foundation |
| Do not | Commit secrets/backups to git · upload cleartext secrets to public storage |

---

## 0. Persiapan

| Step | Action | Done |
|---|---|---|
| 0.1 | Pilih lokasi **off-box** (mesin lain / disk terenkripsi). Jangan hanya di VPS yang sama. | ☐ |
| 0.2 | Catat timestamp UTC: `date -u +%Y%m%dT%H%M%SZ` → pakai sebagai `STAMP` | ☐ |
| 0.3 | Pastikan disk cukup (`df -h`) untuk dump + tarball | ☐ |

---

## 1. Database (wajib)

```bash
/opt/ECMP/deploy/backup-postgres.sh
ls -lh /opt/ECMP/backups/ecmp_*.sql.gz | tail -5
gzip -t /opt/ECMP/backups/ecmp_*.sql.gz   # atau file terbaru saja
```

| Step | Action | Done |
|---|---|---|
| 1.1 | Jalankan script backup | ☐ |
| 1.2 | Verifikasi `gzip -t` PASS pada file terbaru | ☐ |
| 1.3 | Salin file `.sql.gz` terbaru ke off-box | ☐ |
| 1.4 | Catat path + ukuran + SHA256 di evidence (tanpa isi DB) | ☐ |

```bash
# contoh fingerprint (aman dicatat)
sha256sum /opt/ECMP/backups/ecmp_<STAMP>.sql.gz
```

---

## 2. Secrets (wajib untuk restore, sensitif)

| Path tipikal | Isi |
|---|---|
| `/opt/ECMP/.env.prod` | Runtime secrets lab edge |
| `/opt/ECMP/.env` | Lab compose lokal (jika dipakai) |
| `/root/.ecmp-credentials` | Catatan password host (jika ada) |

```bash
# contoh: arsip terenkripsi (ganti OUT dan passphrase policy Anda)
umask 077
tar -C / -czf /root/ecmp-secrets-${STAMP}.tar.gz \
  opt/ECMP/.env.prod \
  opt/ECMP/.env \
  root/.ecmp-credentials 2>/dev/null || true
# enkripsi sebelum off-box, contoh:
# gpg -c /root/ecmp-secrets-${STAMP}.tar.gz
```

| Step | Action | Done |
|---|---|---|
| 2.1 | Kumpulkan file secret yang ada | ☐ |
| 2.2 | Enkripsi arsip | ☐ |
| 2.3 | Salin ke off-box; hapus salinan cleartext di `/tmp` jika ada | ☐ |
| 2.4 | **Jangan** masukkan ke git | ☐ |

Pada host **baru**, rencanakan **rotasi** JWT/DB password (SEC-BASE §3), bukan hanya restore secret lama selamanya.

---

## 3. Kode & config deploy (disarankan)

```bash
cd /opt/ECMP
git -c safe.directory=/opt/ECMP status -sb
git -c safe.directory=/opt/ECMP remote -v
git -c safe.directory=/opt/ECMP rev-parse HEAD
```

| Step | Action | Done |
|---|---|---|
| 3.1 | Pastikan remote GitHub reachable (SoT kode) | ☐ |
| 3.2 | Catat `HEAD` SHA + branch | ☐ |
| 3.3 | (Opsional) tarball working tree **tanpa** secret & tanpa dump besar | ☐ |

```bash
# opsional — exclude secrets & backups
tar -C /opt -czf /root/ecmp-tree-${STAMP}.tar.gz \
  --exclude='ECMP/.env' \
  --exclude='ECMP/.env.prod' \
  --exclude='ECMP/backups' \
  --exclude='ECMP/frontend/node_modules' \
  --exclude='ECMP/backend/.venv' \
  ECMP
```

Salin tarball ke off-box jika dipakai.

---

## 4. Edge / TLS state (opsional)

Compose lab memakai volume Caddy (`caddy_data`, `caddy_config`).

| Opsi | Kapan |
|---|---|
| **A — lewati** | Host baru: biarkan ACME terbit sertifikat baru (lebih bersih) |
| **B — backup volume** | Perlu cutover cepat tanpa re-issue |

```bash
# opsi B (contoh nama volume — sesuaikan `docker volume ls`)
docker volume ls | grep -i caddy
# docker run --rm -v <caddy_data>:/data -v /root:/backup alpine \
#   tar -czf /backup/caddy-data-${STAMP}.tar.gz -C /data .
```

| Step | Action | Done |
|---|---|---|
| 4.1 | Pilih A atau B | ☐ |
| 4.2 | Jika B: arsip volume + salin off-box | ☐ |

---

## 5. Host config out-of-git (disarankan)

```bash
# dokumentasikan saja; sesuaikan distro
sudo ufw status verbose > /root/ecmp-ufw-${STAMP}.txt || true
crontab -l > /root/ecmp-cron-root-${STAMP}.txt 2>/dev/null || true
crontab -u ecmp -l > /root/ecmp-cron-ecmp-${STAMP}.txt 2>/dev/null || true
systemctl list-timers --all 2>/dev/null | head -50 > /root/ecmp-timers-${STAMP}.txt || true
```

| Step | Action | Done |
|---|---|---|
| 5.1 | Export UFW / cron / catatan SSH policy | ☐ |
| 5.2 | Salin catatan ke off-box (bukan secret key privat kecuali enkripsi) | ☐ |
| 5.3 | Ingat: UFW tidak ikut cherry-pick Git (D-06) | ☐ |

---

## 6. Inventaris container (bukti)

```bash
cd /opt/ECMP
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod ps > /root/ecmp-compose-ps-${STAMP}.txt
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}' > /root/ecmp-images-${STAMP}.txt
```

Tidak wajib menyimpan image tar (besar); rebuild dari source di host baru biasanya cukup.

---

## 7. Paket off-box (manifest)

Di mesin tujuan backup, susun folder misalnya:

```text
ecmp-lab-backup-<STAMP>/
  MANIFEST.txt
  ecmp_<STAMP>.sql.gz
  ecmp-secrets-<STAMP>.tar.gz.gpg   # terenkripsi
  ecmp-tree-<STAMP>.tar.gz          # opsional
  ecmp-ufw-<STAMP>.txt
  ecmp-cron-*.txt
  ecmp-compose-ps-<STAMP>.txt
  HEAD.txt                          # isi: branch + SHA
```

`MANIFEST.txt` minimal:

```text
STAMP=
HOST=
FQDN=
HEAD_SHA=
BACKUP_SQL=
SQL_SHA256=
SECRETS_ARCHIVE=
NOTES=
```

| Step | Action | Done |
|---|---|---|
| 7.1 | Semua artefak di off-box | ☐ |
| 7.2 | MANIFEST lengkap | ☐ |
| 7.3 | Uji baca: `gzip -t` dump di off-box | ☐ |

---

## 8. Bukti di repo evidence (tanpa secret)

Isi singkat di `deploy/evidence/lab-backup-<STAMP>.md`:

- STAMP, host, FQDN  
- Nama file SQL + SHA256  
- Konfirmasi secrets di off-box terenkripsi (**jangan** tempel secret)  
- HEAD SHA  

| Step | Action | Done |
|---|---|---|
| 8.1 | Tulis evidence note | ☐ |

---

## 9. Urutan restore ringkas (referensi)

1. Provision host baru (SEC-BASE / MIG §B).  
2. Clone repo / ekstrak tree.  
3. Buat `.env.prod` (idealnya **rotasi** secret).  
4. `compose up` + restore SQL dari dump.  
5. Smoke `/health` `/login`.  
6. DNS cutover.  

Detail: `Host_Domain_Migration_Checklist_20260731.md`.

---

## Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Deploy Lead | _pending_ | | Checklist usable |
| Release Manager | _pending_ | | Evidence path OK |

—*End of Full Lab Backup Checklist v1.0*

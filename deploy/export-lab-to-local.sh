#!/usr/bin/env bash
# Export live VPS lab (code + Postgres + attachments + local env) for workstation restore.
# Usage: /opt/ECMP/deploy/export-lab-to-local.sh
# Output: $ROOT/backups/lab-local-export-STAMP/ and a single .tar.gz beside it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${ECMP_EXPORT_DIR:-$ROOT/backups}/lab-local-export-${STAMP}"
PG_USER="${POSTGRES_USER:-ecmp}"
PG_DB="${POSTGRES_DB:-ecmp}"

if ! docker ps --format '{{.Names}}' | grep -qx ecmp-postgres; then
  echo "export_failed: container ecmp-postgres is not running" >&2
  exit 1
fi

mkdir -p "$OUT/data" "$OUT/app" "$OUT/git" "$OUT/secrets"
chmod 700 "$OUT" "$OUT/secrets"

echo "==> Postgres dump"
DUMP="$OUT/data/ecmp_${STAMP}.sql.gz"
docker exec ecmp-postgres pg_dump -U "$PG_USER" -d "$PG_DB" --clean --if-exists \
  | gzip -c >"$DUMP"
chmod 600 "$DUMP"
gzip -t "$DUMP"
bytes="$(gzip -dc "$DUMP" | wc -c)"
if [ "$bytes" -lt 1000 ]; then
  echo "export_failed: dump too small (${bytes} bytes)" >&2
  exit 1
fi
sha256sum "$DUMP" | awk '{print $1}' >"$DUMP.sha256"

docker exec ecmp-postgres psql -U "$PG_USER" -d "$PG_DB" -tAc \
  "SELECT version_num FROM alembic_version;" | tr -d '[:space:]' >"$OUT/data/alembic.txt"

echo "==> verify dump on temp database"
docker exec ecmp-postgres psql -U "$PG_USER" -d postgres -v ON_ERROR_STOP=1 \
  -c "DROP DATABASE IF EXISTS ecmp_restore_verify;" \
  -c "CREATE DATABASE ecmp_restore_verify OWNER ${PG_USER};"
gzip -dc "$DUMP" | docker exec -i ecmp-postgres psql -U "$PG_USER" -d ecmp_restore_verify \
  -v ON_ERROR_STOP=1 >/tmp/ecmp-verify-restore.log
VERIFY_ALEMBIC="$(docker exec ecmp-postgres psql -U "$PG_USER" -d ecmp_restore_verify -tAc \
  "SELECT version_num FROM alembic_version;" | tr -d '[:space:]')"
LIVE_ALEMBIC="$(tr -d '[:space:]' <"$OUT/data/alembic.txt")"
if [ "$VERIFY_ALEMBIC" != "$LIVE_ALEMBIC" ]; then
  echo "export_failed: alembic mismatch live=$LIVE_ALEMBIC verify=$VERIFY_ALEMBIC" >&2
  docker exec ecmp-postgres psql -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS ecmp_restore_verify;"
  exit 1
fi
docker exec ecmp-postgres psql -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS ecmp_restore_verify;" >/dev/null
echo "    verify_ok alembic=$LIVE_ALEMBIC uncompressed=${bytes}"

echo "==> attachments volume"
ATTACH_VOL="ecmp_ecmp_attachments"
if ! docker volume inspect "$ATTACH_VOL" >/dev/null 2>&1; then
  echo "export_failed: volume $ATTACH_VOL not found" >&2
  exit 1
fi
docker run --rm \
  -v "$ATTACH_VOL":/data:ro \
  -v "$OUT/data":/backup \
  alpine:3.20 \
  tar -czf /backup/ecmp_attachments.tar.gz -C /data .
chmod 600 "$OUT/data/ecmp_attachments.tar.gz"
sha256sum "$OUT/data/ecmp_attachments.tar.gz" | awk '{print $1}' >"$OUT/data/ecmp_attachments.tar.gz.sha256"

echo "==> git metadata + bundle"
git -C "$ROOT" -c safe.directory="$ROOT" rev-parse --abbrev-ref HEAD >"$OUT/git/HEAD-branch.txt"
git -C "$ROOT" -c safe.directory="$ROOT" rev-parse HEAD >"$OUT/git/HEAD-sha.txt"
git -C "$ROOT" -c safe.directory="$ROOT" status -sb >"$OUT/git/status.txt"
git -C "$ROOT" -c safe.directory="$ROOT" log --oneline -20 >"$OUT/git/log-20.txt"
git -C "$ROOT" -c safe.directory="$ROOT" bundle create "$OUT/git/ecmp-HEAD.bundle" HEAD >/dev/null

echo "==> working tree (tanpa secret, node_modules, backups)"
tar -C "$(dirname "$ROOT")" -czf "$OUT/app/ECMP-working-tree.tar.gz" \
  --exclude='ECMP/.env' \
  --exclude='ECMP/.env.prod' \
  --exclude='ECMP/.env.local' \
  --exclude='ECMP/backups' \
  --exclude='ECMP/.git' \
  --exclude='ECMP/frontend/node_modules' \
  --exclude='ECMP/backend/.venv' \
  --exclude='ECMP/backend/.venv-ci' \
  --exclude='ECMP/**/node_modules' \
  --exclude='ECMP/**/.next' \
  --exclude='ECMP/**/__pycache__' \
  --exclude='ECMP/**/.pytest_cache' \
  --exclude='ECMP/**/.ruff_cache' \
  --exclude='ECMP/**/.venv' \
  "$(basename "$ROOT")"
sha256sum "$OUT/app/ECMP-working-tree.tar.gz" | awk '{print $1}' >"$OUT/app/ECMP-working-tree.tar.gz.sha256"

echo "==> secrets + env.local (chmod 700)"
umask 077
cp -a "$ROOT/.env" "$OUT/secrets/env.vps"
if [ -f "$ROOT/.env.prod" ]; then
  cp -a "$ROOT/.env.prod" "$OUT/secrets/env.prod.vps"
fi
if [ -f /root/.ecmp-credentials ]; then
  cp -a /root/.ecmp-credentials "$OUT/secrets/ecmp-credentials.host"
fi

python3 - "$ROOT/.env" "$OUT/secrets/env.local" <<'PY'
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
overrides = {
    "ENVIRONMENT": "development",
    "DEBUG": "false",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5433",
    "BACKEND_PORT": "8000",
    "FRONTEND_PORT": "3000",
    "ALLOWED_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
    "ALLOWED_HOSTS": "localhost,127.0.0.1,backend",
    "NEXT_PUBLIC_API_BASE_URL": "http://localhost:8000",
    "PASSWORD_RESET_FRONTEND_BASE_URL": "http://localhost:3000",
    "ECMP_AUTH_MODE": "dev",
    "ECMP_ENV": "local",
    "ECMP_LOCAL_CREDENTIAL_AUTH": "true",
    "ECMP_ENTERPRISE_MODE": "false",
    "EMAIL_PROVIDER": "logging",
    "CUSTOMER_PROVIDER": "local",
}
seen = set()
out = [
    "# Generated from VPS .env for local Docker (ports 3000/8000/5433).",
    "# JWT + Postgres password copied so lab logins match VPS.",
    "# Jangan commit file ini.",
    "",
]
for raw in src.read_text().splitlines():
    line = raw.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
        out.append(line)
        continue
    key, _, _val = line.partition("=")
    if key in overrides:
        out.append(f"{key}={overrides[key]}")
        seen.add(key)
    else:
        out.append(line)
        seen.add(key)
for key, val in overrides.items():
    if key not in seen:
        out.append(f"{key}={val}")
dst.write_text("\n".join(out) + "\n")
PY
chmod 600 "$OUT/secrets/"*

cat >"$OUT/secrets/CREDENTIALS.txt" <<'EOF'
Akun lab ada di database (password hash), bukan di git.

Sumber password lab (jika ada di paket ini):
  secrets/ecmp-credentials.host   ← salinan /root/.ecmp-credentials dari VPS

Jangan commit folder secrets/. Jangan tempel password ke chat/repo.
Login lokal memakai username yang sama dengan VPS (admin, NIP cabang/Pusat, dll.).
Role AGENT/SUPERVISOR/MANAGER sama di cabang dan Pusat; yang membedakan unit keanggotaan.
Contoh lab: 31206 Teguh = Agent Pusat; petugas UPPPD = Agent Cabang.
EOF
chmod 600 "$OUT/secrets/CREDENTIALS.txt"

cp -a "$ROOT/deploy/restore-lab-local.sh" "$OUT/restore-lab-local.sh"
chmod 755 "$OUT/restore-lab-local.sh"

HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
cat >"$OUT/MANIFEST.txt" <<EOF
STAMP=$STAMP
HOST=$(hostname)
HOST_IP=$HOST_IP
FQDN=pengaduan.layanankami.tech
LIVE_COMPOSE=docker-compose.yml + .env
HEAD_BRANCH=$(cat "$OUT/git/HEAD-branch.txt")
HEAD_SHA=$(cat "$OUT/git/HEAD-sha.txt")
ALEMBIC=$(cat "$OUT/data/alembic.txt")
BACKUP_SQL=data/ecmp_${STAMP}.sql.gz
SQL_SHA256=$(cat "$DUMP.sha256")
SQL_UNCOMPRESSED_BYTES=$bytes
ATTACHMENTS=data/ecmp_attachments.tar.gz
ATTACHMENTS_SHA256=$(cat "$OUT/data/ecmp_attachments.tar.gz.sha256")
TREE=app/ECMP-working-tree.tar.gz
TREE_SHA256=$(cat "$OUT/app/ECMP-working-tree.tar.gz.sha256")
NOTES=Mode A lab replica. Caddy/TLS publik tidak disertakan. Frontend harus di-build di lokal karena NEXT_PUBLIC_API_BASE_URL berbeda.
EOF

cat >"$OUT/README-RESTORE.md" <<EOF
# Restore ECMP lab ke mesin lokal

Paket ini adalah snapshot **VPS lab Mode A** ($(hostname), $STAMP UTC):
kode working tree, Postgres, lampiran, dan \`.env\` siap localhost.

Bukan salinan TLS/Caddy publik. Bukan Mode B / SSO.

## Prasyarat lokal

- Docker Engine + Docker Compose v2
- Port bebas: 3000 (UI), 8000 (API), 5433 (Postgres)
- **Build image di mesin lokal wajib** pada restore pertama — argumen
  \`NEXT_PUBLIC_API_BASE_URL\` di VPS ter-bake ke \`https://pengaduan.layanankami.tech\`.
  Rebuild ini hanya di laptop Anda, bukan di VPS.

## Unduh dari VPS

\`\`\`bash
scp -r root@${HOST_IP}:/opt/ECMP/backups/lab-local-export-${STAMP} .
# atau arsip tunggal:
scp root@${HOST_IP}:/opt/ECMP/backups/lab-local-export-${STAMP}.tar.gz .
tar -xzf lab-local-export-${STAMP}.tar.gz
\`\`\`

## Restore

\`\`\`bash
chmod +x lab-local-export-${STAMP}/restore-lab-local.sh
./lab-local-export-${STAMP}/restore-lab-local.sh \\
  --pack ./lab-local-export-${STAMP} \\
  --target ~/ecmp
\`\`\`

Lalu buka http://localhost:3000 — login akun lab VPS (lihat \`secrets/CREDENTIALS.txt\`).

## Isi paket

| Artefak | Isi |
|---|---|
| \`data/ecmp_*.sql.gz\` | Dump Postgres (\`--clean --if-exists\`), sudah diuji ke DB sementara di VPS |
| \`data/ecmp_attachments.tar.gz\` | Volume lampiran \`ecmp_ecmp_attachments\` |
| \`app/ECMP-working-tree.tar.gz\` | Working tree VPS (termasuk perubahan belum di-commit), tanpa \`.env\` / \`node_modules\` |
| \`git/ecmp-HEAD.bundle\` | Git bundle HEAD (opsional, untuk arsip histori) |
| \`secrets/env.local\` | Env Docker lokal (password DB + JWT sama dengan VPS) |
| \`secrets/env.vps\` | Salinan \`.env\` hidup di VPS |

Jangan masukkan \`secrets/\` ke git.
EOF

( cd "$OUT" && find . -type f ! -path './SHA256SUMS' -print0 | sort -z | xargs -0 sha256sum >SHA256SUMS )

echo "==> arsip tunggal"
ARCHIVE="${OUT}.tar.gz"
tar -C "$(dirname "$OUT")" -czf "$ARCHIVE" "$(basename "$OUT")"
chmod 600 "$ARCHIVE"

echo
echo "export_ok $OUT"
echo "archive   $ARCHIVE ($(du -h "$ARCHIVE" | awk '{print $1}'))"
ls -lh "$OUT/data" "$OUT/app" "$ARCHIVE"

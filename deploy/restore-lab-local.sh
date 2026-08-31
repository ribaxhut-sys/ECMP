#!/usr/bin/env bash
# Restore an ECMP lab-local export pack onto a workstation.
# Usage:
#   ./restore-lab-local.sh --pack /path/to/lab-local-export-STAMP --target ~/ecmp
#
# First local start builds images (NEXT_PUBLIC_API_BASE_URL differs from VPS).
# Do not run this on the live VPS.
set -euo pipefail

PACK=""
TARGET=""
BUILD=1

usage() {
  cat <<'EOF'
Restore ECMP lab export (database + attachments + working tree) for local Docker.

Usage:
  ./restore-lab-local.sh --pack DIR --target DIR [--no-build]

  --pack DIR     Folder lab-local-export-STAMP (hasil scp dari VPS)
  --target DIR   Direktori aplikasi lokal (akan dibuat jika belum ada)
  --no-build     Jangan docker compose build (hanya jika image sudah ada)
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --pack) PACK="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --no-build) BUILD=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage; exit 1 ;;
  esac
done

if [ -z "$PACK" ] || [ -z "$TARGET" ]; then
  usage
  exit 1
fi

PACK="$(cd "$PACK" && pwd)"
if [ ! -f "$PACK/MANIFEST.txt" ]; then
  echo "bukan paket export: $PACK (MANIFEST.txt tidak ada)" >&2
  exit 1
fi

if [ "$(hostname -s 2>/dev/null || hostname)" = "srv1869401" ]; then
  echo "script ini untuk mesin lokal, bukan VPS lab hidup." >&2
  exit 1
fi

command -v docker >/dev/null || { echo "docker tidak ditemukan" >&2; exit 1; }
docker compose version >/dev/null || { echo "docker compose tidak ditemukan" >&2; exit 1; }

mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"

echo "==> mengekstrak working tree ke $TARGET"
tar -xzf "$PACK/app/ECMP-working-tree.tar.gz" -C "$TARGET" --strip-components=1

if [ ! -f "$PACK/secrets/env.local" ]; then
  echo "secrets/env.local tidak ada — salin paket secrets dari VPS" >&2
  exit 1
fi
umask 077
cp -f "$PACK/secrets/env.local" "$TARGET/.env"
chmod 600 "$TARGET/.env"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ecmp}"
cd "$TARGET"

echo "==> postgres"
docker compose --env-file .env up -d postgres
for i in $(seq 1 60); do
  if docker compose --env-file .env exec -T postgres pg_isready -U ecmp -d ecmp >/dev/null 2>&1; then
    break
  fi
  sleep 2
  if [ "$i" -eq 60 ]; then
    echo "postgres tidak siap" >&2
    exit 1
  fi
done

DUMP="$(ls -1 "$PACK/data"/ecmp_*.sql.gz | head -1)"
echo "==> kosongkan skema (init compose + dump --clean sering bentrok FK)"
docker compose --env-file .env exec -T postgres psql -U ecmp -d ecmp -v ON_ERROR_STOP=1 \
  -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO ecmp; GRANT ALL ON SCHEMA public TO public;"
echo "==> restore SQL $DUMP"
gzip -dc "$DUMP" | docker compose --env-file .env exec -T postgres psql -U ecmp -d ecmp -v ON_ERROR_STOP=1 >/tmp/ecmp-restore-psql.log
tail -5 /tmp/ecmp-restore-psql.log

ATTACH_VOL="${COMPOSE_PROJECT_NAME}_ecmp_attachments"
if ! docker volume inspect "$ATTACH_VOL" >/dev/null 2>&1; then
  docker compose --env-file .env up -d --no-start backend >/dev/null
fi
echo "==> restore lampiran → volume $ATTACH_VOL"
docker run --rm \
  -v "$ATTACH_VOL":/data \
  -v "$PACK/data":/backup:ro \
  alpine:3.20 \
  sh -c 'rm -rf /data/* /data/.[!.]* 2>/dev/null || true; tar -xzf /backup/ecmp_attachments.tar.gz -C /data'

echo "==> backend + frontend"
if [ "$BUILD" -eq 1 ]; then
  docker compose --env-file .env up -d --build backend frontend
else
  docker compose --env-file .env up -d backend frontend
fi

echo
echo "restore selesai."
echo "  UI : http://localhost:3000"
echo "  API: http://localhost:8000/health"
echo "Login pakai akun lab VPS (lihat secrets/CREDENTIALS.txt di paket — jangan commit)."
echo "Cabang vs Pusat: role sama; yang membedakan unit keanggotaan. Contoh lab: 31206 Teguh = Agent Pusat."

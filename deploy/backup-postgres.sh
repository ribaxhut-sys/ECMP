#!/usr/bin/env bash
# Daily Postgres dump for ECMP foundation stack.
# Usage: /opt/ECMP/deploy/backup-postgres.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${ECMP_BACKUP_DIR:-$ROOT/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$BACKUP_DIR/ecmp_${STAMP}.sql.gz"
KEEP_DAYS="${ECMP_BACKUP_KEEP_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

cd "$ROOT"
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  exec -T postgres pg_dump -U ecmp -d ecmp --clean --if-exists \
  | gzip -c >"$FILE"
chmod 600 "$FILE"

# prune old dumps
find "$BACKUP_DIR" -type f -name 'ecmp_*.sql.gz' -mtime +"$KEEP_DAYS" -delete

echo "backup_ok $FILE ($(du -h "$FILE" | awk '{print $1}'))"

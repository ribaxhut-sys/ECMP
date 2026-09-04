#!/usr/bin/env bash
# Daily Postgres dump for the LIVE ECMP lab stack (ecmp-postgres).
# Usage: /opt/ECMP/deploy/backup-postgres.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${ECMP_BACKUP_DIR:-$ROOT/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$BACKUP_DIR/ecmp_${STAMP}.sql.gz"
KEEP_DAYS="${ECMP_BACKUP_KEEP_DAYS:-14}"
PG_USER="${POSTGRES_USER:-ecmp}"
PG_DB="${POSTGRES_DB:-ecmp}"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

if ! docker ps --format '{{.Names}}' | grep -qx ecmp-postgres; then
  echo "backup_failed: container ecmp-postgres is not running" >&2
  exit 1
fi

docker exec ecmp-postgres pg_dump -U "$PG_USER" -d "$PG_DB" --clean --if-exists \
  | gzip -c >"$FILE"
chmod 600 "$FILE"

if ! gzip -t "$FILE"; then
  echo "backup_failed: gzip integrity $FILE" >&2
  rm -f "$FILE"
  exit 1
fi

bytes="$(gzip -dc "$FILE" | wc -c)"
if [ "$bytes" -lt 1000 ]; then
  echo "backup_failed: dump too small (${bytes} bytes uncompressed)" >&2
  rm -f "$FILE"
  exit 1
fi

find "$BACKUP_DIR" -type f -name 'ecmp_*.sql.gz' -mtime +"$KEEP_DAYS" -delete

echo "backup_ok $FILE ($(du -h "$FILE" | awk '{print $1}'))"

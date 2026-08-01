#!/bin/sh
set -eu

# Named volume mounts often arrive as root-owned; ensure LocalStorageProvider
# path is writable by the runtime user before dropping privileges.
STORAGE_DIR="${ECMP_ATTACHMENT_STORAGE_DIR:-/app/storage/attachments}"
mkdir -p "${STORAGE_DIR}"

if [ "$(id -u)" = "0" ]; then
  chown -R ecmp:ecmp /app/storage
  run_as_ecmp() {
    exec setpriv --reuid=ecmp --regid=ecmp --init-groups -- "$@"
  }
else
  run_as_ecmp() {
    exec "$@"
  }
fi

echo "Running database migrations..."
if [ "$(id -u)" = "0" ]; then
  setpriv --reuid=ecmp --regid=ecmp --init-groups -- alembic upgrade head
else
  alembic upgrade head
fi

# Trust X-Forwarded-For / X-Forwarded-Proto / X-Forwarded-Host from the
# Compose reverse proxy. Uvicorn also reads $FORWARDED_ALLOW_IPS when set.
# Production compose sets FORWARDED_ALLOW_IPS=* because backend publishes no
# host ports and only the proxy can reach it on the internal network.
# Default remains loopback for non-compose / direct local runs.
FORWARDED_ALLOW_IPS="${FORWARDED_ALLOW_IPS:-127.0.0.1}"

echo "Starting API (graceful shutdown enabled; proxy-headers trusted for ${FORWARDED_ALLOW_IPS})..."
run_as_ecmp uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips "${FORWARDED_ALLOW_IPS}" \
  --timeout-graceful-shutdown 30

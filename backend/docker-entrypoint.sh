#!/bin/sh
set -eu

echo "Running database migrations..."
alembic upgrade head

# Trust X-Forwarded-For / X-Forwarded-Proto / X-Forwarded-Host from the
# Compose reverse proxy. Uvicorn also reads $FORWARDED_ALLOW_IPS when set.
# Production compose sets FORWARDED_ALLOW_IPS=* because backend publishes no
# host ports and only the proxy can reach it on the internal network.
# Default remains loopback for non-compose / direct local runs.
FORWARDED_ALLOW_IPS="${FORWARDED_ALLOW_IPS:-127.0.0.1}"

echo "Starting API (graceful shutdown enabled; proxy-headers trusted for ${FORWARDED_ALLOW_IPS})..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips "${FORWARDED_ALLOW_IPS}" \
  --timeout-graceful-shutdown 30

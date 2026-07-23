#!/bin/sh
set -eu

echo "Running database migrations..."
alembic upgrade head

echo "Starting API (graceful shutdown enabled)..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --timeout-graceful-shutdown 30

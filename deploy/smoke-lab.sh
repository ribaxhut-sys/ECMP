#!/usr/bin/env bash
# Minimal lab/smoke checks — not a full e2e suite.
# Usage: ./deploy/smoke-lab.sh [BASE_URL]
set -euo pipefail
BASE="${1:-http://127.0.0.1:8000}"
BASE="${BASE%/}"

echo "smoke_base=$BASE"

code=$(curl -sS -o /tmp/ecmp-smoke-health.json -w '%{http_code}' "$BASE/health" || curl -sS -o /tmp/ecmp-smoke-health.json -w '%{http_code}' "$BASE/health/")
echo "health_http=$code"
if [[ "$code" != "200" ]]; then
  echo "FAIL health" >&2
  cat /tmp/ecmp-smoke-health.json >&2 || true
  exit 1
fi
echo "health_body=$(head -c 200 /tmp/ecmp-smoke-health.json)"

# Frontend login page (when BASE is public edge)
if [[ "$BASE" == https://* ]] || [[ "$BASE" == http://*pengaduan* ]]; then
  fcode=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/login" || true)
  echo "login_page_http=$fcode"
fi

# Docs must not be public on edge after W-S04 (best-effort)
dcode=$(curl -sS -o /dev/null -w '%{http_code}' "$BASE/docs" || true)
echo "docs_http=$dcode (expect 404/405 on hardened edge; 200 may indicate W-S04 regress)"

echo "smoke_ok"

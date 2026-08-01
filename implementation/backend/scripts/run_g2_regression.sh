#!/usr/bin/env bash
# G2 Mode A regression — implementation/backend
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "g2_regression_cwd=$ROOT"
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
pytest -q tests/
echo "g2_regression_ok"

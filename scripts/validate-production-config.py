#!/usr/bin/env python3
"""R6-03 — fail-fast production configuration validator (CLI).

Usage (from repo root or backend/):

  python scripts/validate-production-config.py
  python scripts/validate-production-config.py --env-file .env
  python scripts/validate-production-config.py --require-production

Exit codes:
  0 = PASS
  1 = validation failed
  2 = usage / import error
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"env file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Do not override already-exported process env (ops overrides win).
        os.environ.setdefault(key, value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ECMP runtime configuration (R6-03).")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to env file (default: .env). Loaded with setdefault only.",
    )
    parser.add_argument(
        "--require-production",
        action="store_true",
        help="Fail if ENVIRONMENT is not production after loading env.",
    )
    parser.add_argument(
        "--allow-missing-env-file",
        action="store_true",
        help="Skip missing env file (use process environment only).",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    backend_dir = repo_root / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    env_path = Path(args.env_file)
    if not env_path.is_absolute():
        env_path = (Path.cwd() / env_path).resolve()
    try:
        if env_path.is_file():
            _load_dotenv(env_path)
            print(f"Loaded env file: {env_path}")
        elif args.allow_missing_env_file:
            print(f"Env file missing (allowed): {env_path}")
        else:
            print(f"ERROR: env file not found: {env_path}", file=sys.stderr)
            return 2
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    from app.core.config import (  # noqa: WPS433 — intentional late import after PYTHONPATH
        ConfigValidationError,
        Settings,
        collect_runtime_config_issues,
        validate_runtime_config,
    )

    # Clear lru_cache so CLI always reflects current process env.
    from app.core import config as config_mod

    config_mod.get_settings.cache_clear()
    settings = Settings()

    print(f"ENVIRONMENT={settings.environment}")
    print(f"APP_VERSION={settings.app_version}")
    print(f"DEBUG={settings.debug}")
    print(f"ECMP_AUTH_MODE={settings.ecmp_auth_mode}")
    print(f"ECMP_ENV={settings.ecmp_env}")
    print(f"ECMP_ENTERPRISE_MODE={settings.ecmp_enterprise_mode}")
    print(f"ECMP_LOCAL_CREDENTIAL_AUTH={settings.ecmp_local_credential_auth}")
    print(f"OIDC_ISSUER={'set' if (settings.oidc_issuer or '').strip() else 'missing'}")
    print(f"OIDC_AUDIENCE={'set' if (settings.oidc_audience or '').strip() else 'missing'}")
    print(f"OIDC_JWKS_URL={'set' if (settings.oidc_jwks_url or '').strip() else 'missing'}")
    print(f"ALLOWED_ORIGINS={settings.allowed_origins}")
    print(f"EMAIL_PROVIDER={settings.email_provider}")
    print("REDIS: not used (login lockout is in-memory; no REDIS_* required)")
    print("STORAGE: System Settings (storage.provider / storage.root.path), not env")

    if args.require_production and settings.environment != "production":
        print(
            "ERROR: --require-production set but ENVIRONMENT="
            f"{settings.environment!r}",
            file=sys.stderr,
        )
        return 1

    issues = collect_runtime_config_issues(settings)
    if not issues:
        print("Configuration validation: PASS")
        return 0

    try:
        validate_runtime_config(settings)
    except ConfigValidationError as exc:
        print(str(exc), file=sys.stderr)
        print(f"Configuration validation: FAIL ({len(exc.issues)} issue(s))", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

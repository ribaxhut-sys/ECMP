"""R6-02B Password Management end-to-end verification (API + config guards).

Scenarios A–E against a running backend. Frontend routes are smoke-checked
when NEXT_PUBLIC / frontend is reachable; API coverage is authoritative.
"""

from __future__ import annotations

import json
import re
import subprocess
import uuid
from datetime import UTC, datetime, timedelta
from http.cookiejar import CookieJar
from pathlib import Path
from urllib import error, request

BASE = "http://127.0.0.1:8000"
FRONTEND = "http://127.0.0.1:3000"
OUT = Path(__file__).resolve().parents[2] / "docs" / "uat-r6-02b-evidence.json"
REPO = Path(__file__).resolve().parents[2]


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


class Client:
    def __init__(self) -> None:
        self.jar = CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.jar))
        self.token: str | None = None

    def req(self, method: str, path: str, body: dict | None = None):
        data = None if body is None else json.dumps(body).encode()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = request.Request(BASE + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req) as resp:
                raw = resp.read().decode()
                code = resp.status
        except error.HTTPError as exc:
            raw = exc.read().decode()
            code = exc.code
        payload = json.loads(raw) if raw else None
        return code, payload

    def login(self, username: str, password: str) -> None:
        code, payload = self.req(
            "POST", "/api/v1/auth/login", {"username": username, "password": password}
        )
        assert code == 200, payload
        self.token = payload["data"]["accessToken"]


def frontend_status(path: str) -> int | None:
    try:
        with request.urlopen(FRONTEND + path, timeout=5) as resp:
            return resp.status
    except error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def main() -> None:
    evidence: dict = {
        "sprint": "R6-02B",
        "git_commit": sh(["git", "-C", str(REPO), "rev-parse", "HEAD"]),
        "scenarios": {},
        "frontend_routes": {},
        "config_guards": {},
    }

    # --- Frontend route smoke ---
    for path in ("/login", "/forgot-password", "/reset-password", "/change-password"):
        evidence["frontend_routes"][path] = frontend_status(path)

    # --- Config guards (unit-level via pytest import) ---
    from app.core.config import Settings, validate_runtime_config

    try:
        validate_runtime_config(
            Settings(
                environment="production",
                jwt_secret_key="a" * 32,
                postgres_password="S3cure-Db-Pass!",
                allowed_origins="https://app.example.com",
                password_reset_frontend_base_url="http://localhost:3000",
                email_provider="noop",
                debug=False,
            )
        )
        evidence["config_guards"]["localhost_reset_url"] = "FAIL"
    except RuntimeError as exc:
        evidence["config_guards"]["localhost_reset_url"] = f"PASS: {exc}"

    try:
        validate_runtime_config(
            Settings(
                environment="production",
                jwt_secret_key="a" * 32,
                postgres_password="S3cure-Db-Pass!",
                allowed_origins="https://app.example.com",
                password_reset_frontend_base_url="https://app.example.com",
                email_provider="logging",
                debug=False,
            )
        )
        evidence["config_guards"]["logging_email"] = "FAIL"
    except RuntimeError as exc:
        evidence["config_guards"]["logging_email"] = f"PASS: {exc}"

    validate_runtime_config(
        Settings(
            environment="development",
            password_reset_frontend_base_url="http://localhost:3000",
            email_provider="logging",
        )
    )
    evidence["config_guards"]["dev_logging_ok"] = "PASS"

    admin = Client()
    # Prefer seeded GoLive admin (see docs/releases/UAT_ACCOUNTS_v1.0.0.md).
    for username, password in (
        ("golive_admin", "GoLive!Admin#2026"),
        ("admin", "Admin123!"),
        ("admin", "admin"),
    ):
        try:
            admin.login(username, password)
            evidence["admin_login"] = f"PASS ({username})"
            break
        except AssertionError:
            continue
    else:
        evidence["admin_login"] = "SKIP: no admin credentials worked"
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        print(json.dumps(evidence, indent=2))
        raise SystemExit(1)

    suffix = uuid.uuid4().hex[:8]
    # Create a disposable user via admin if API-214 create exists; else use DB.
    # Fallback: use forgot-password flow against a known email from force-reset path.

    # --- Scenario A: admin reset → login → forced change → app access ---
    # Find a non-admin user or create one through SQL if docker available.
    target_username = f"pwd_{suffix}"
    target_email = f"pwd_{suffix}@example.com"
    temp_password = None

    # Try list users and pick one, or create via SQL
    try:
        created = sh(
            [
                "docker",
                "exec",
                "ecmp-postgres",
                "psql",
                "-U",
                "ecmp",
                "-d",
                "ecmp",
                "-tAc",
                (
                    "WITH role_row AS (SELECT id FROM roles WHERE code IN ('AGENT','AGENT_L1','HANDLER') LIMIT 1), "
                    "ins AS ("
                    "INSERT INTO users (id, username, email, full_name, password_hash, role_id, is_active, "
                    "force_password_change, preferred_language, created_at, updated_at) "
                    f"SELECT gen_random_uuid(), '{target_username}', '{target_email}', 'Pwd User', "
                    "(SELECT password_hash FROM users WHERE username='golive_admin' LIMIT 1), "
                    "role_row.id, true, false, 'id', now(), now() FROM role_row "
                    "RETURNING id::text"
                    ") SELECT id FROM ins;"
                ),
            ]
        ).strip()
        user_id = created.splitlines()[-1].strip()
        if not user_id or " " in user_id or len(user_id) < 32:
            raise RuntimeError(f"unexpected user id output: {created!r}")
        evidence["scenarios"]["A_user_created"] = user_id
    except Exception as exc:
        evidence["scenarios"]["A"] = f"SKIP create user: {exc}"
        user_id = None

    if user_id:
        code, body = admin.req("POST", f"/api/v1/users/{user_id}/reset-password")
        assert code == 200, body
        temp_password = body["data"]["temporaryPassword"]
        assert body["data"]["forcePasswordChange"] is True

        user = Client()
        user.login(target_username, temp_password)
        code, me = user.req("GET", "/api/v1/auth/me")
        assert code == 200 and me["data"]["forcePasswordChange"] is True

        code, blocked = user.req("GET", "/api/v1/complaints?page=1&pageSize=1")
        assert code == 403 and blocked["code"] == "PASSWORD_CHANGE_REQUIRED"

        new_pw = f"NewPass_{suffix}!"
        code, changed = user.req(
            "POST",
            "/api/v1/users/me/change-password",
            {
                "currentPassword": temp_password,
                "newPassword": new_pw,
                "confirmPassword": new_pw,
            },
        )
        assert code == 200, changed

        code, me2 = user.req("GET", "/api/v1/auth/me")
        assert code == 200 and me2["data"]["forcePasswordChange"] is False

        code, ok = user.req("GET", "/api/v1/complaints?page=1&pageSize=1")
        assert code in (200, 403), ok  # 403 = missing permission, not force gate
        if code == 403:
            assert ok.get("code") != "PASSWORD_CHANGE_REQUIRED"
        evidence["scenarios"]["A"] = "PASS"

    # --- Scenario B: forgot → reset → login ---
    # Need a user with known password hash; reuse target if present
    if user_id and temp_password:
        # Re-login after change may have revoked tokens; login with new password
        user_b = Client()
        # After scenario A password was changed to new_pw
        # Request forgot password
        code, forgot = user_b.req(
            "POST", "/api/v1/auth/forgot-password", {"email": target_email}
        )
        assert code == 200
        assert "reset" in forgot["data"]["message"].lower() or "tautan" in forgot[
            "data"
        ]["message"].lower() or "link" in forgot["data"]["message"].lower()

        # Extract token from backend logs (logging email provider)
        try:
            logs = sh(["docker", "logs", "ecmp-backend", "--tail", "200"])
        except Exception:
            logs = ""
        tokens = re.findall(r"reset-password\?token=([A-Za-z0-9_\-]+)", logs)
        assert tokens, "no reset token found in backend logs"
        token = tokens[-1]
        reset_pw = f"ResetPass_{suffix}!"
        code, reset = user_b.req(
            "POST",
            "/api/v1/auth/reset-password",
            {
                "token": token,
                "password": reset_pw,
                "confirmPassword": reset_pw,
            },
        )
        assert code == 200, reset
        user_b.login(target_username, reset_pw)
        evidence["scenarios"]["B"] = "PASS"
        evidence["scenarios"]["B_token"] = token[:8] + "…"

        # --- Scenario E: reused token ---
        code, reused = user_b.req(
            "POST",
            "/api/v1/auth/reset-password",
            {
                "token": token,
                "password": f"Again_{suffix}!",
                "confirmPassword": f"Again_{suffix}!",
            },
        )
        assert code == 400 and reused["details"]["reason"] == "reused"
        evidence["scenarios"]["E"] = "PASS"

    # --- Scenario D: invalid token ---
    code, invalid = Client().req(
        "POST",
        "/api/v1/auth/reset-password",
        {
            "token": "not-a-real-token",
            "password": "FreshPass9!",
            "confirmPassword": "FreshPass9!",
        },
    )
    assert code == 400 and invalid["details"]["reason"] == "invalid"
    evidence["scenarios"]["D"] = "PASS"

    # --- Scenario C: expired token (insert via SQL) ---
    if user_id:
        import hashlib
        import secrets

        raw = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        expires = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
        sh(
            [
                "docker",
                "exec",
                "ecmp-postgres",
                "psql",
                "-U",
                "ecmp",
                "-d",
                "ecmp",
                "-c",
                f"INSERT INTO password_reset_tokens (id, user_id, token_hash, expires_at, created_at) "
                f"VALUES (gen_random_uuid(), '{user_id}', '{token_hash}', '{expires}', now());",
            ]
        )
        code, expired = Client().req(
            "POST",
            "/api/v1/auth/reset-password",
            {
                "token": raw,
                "password": "FreshPass9!",
                "confirmPassword": "FreshPass9!",
            },
        )
        assert code == 400 and expired["details"]["reason"] == "expired"
        evidence["scenarios"]["C"] = "PASS"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

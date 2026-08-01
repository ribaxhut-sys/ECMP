"""R6-02 live Identity/RBAC verification against running RC."""
from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from http.cookiejar import CookieJar
from pathlib import Path
from urllib import error, request

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parents[1] / "uat-r6-02-evidence.json"


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


def psql(sql: str) -> str:
    return sh(
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
            sql,
        ]
    )


class Client:
    def __init__(self) -> None:
        self.jar = CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.jar))
        self.token: str | None = None
        self.last_headers: dict[str, str] = {}

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
                self.last_headers = {k: v for k, v in resp.headers.items()}
        except error.HTTPError as exc:
            raw = exc.read().decode()
            code = exc.code
            self.last_headers = {k: v for k, v in exc.headers.items()}
        payload = json.loads(raw) if raw else None
        return code, payload, self.last_headers

    def login(self, username: str, password: str) -> None:
        code, payload, _ = self.req(
            "POST", "/api/v1/auth/login", {"username": username, "password": password}
        )
        assert code == 200, payload
        self.token = payload["data"]["accessToken"]


def main() -> None:
    evidence: dict = {
        "container_id": sh(
            ["docker", "inspect", "ecmp-backend", "--format", "{{.Id}}"]
        ),
        "git_commit": sh(["git", "-C", "D:/ECMP", "rev-parse", "HEAD"]),
        "image": sh(
            [
                "docker",
                "inspect",
                "ecmp-backend",
                "--format",
                "{{.Config.Image}}",
            ]
        ),
    }
    suffix = uuid.uuid4().hex[:8]
    admin_role = psql("SELECT id FROM roles WHERE code='ADMIN'").strip()
    agent_role = psql("SELECT id FROM roles WHERE code='AGENT'").strip()
    viewer_role = psql("SELECT id FROM roles WHERE code='VIEWER'").strip()

    # ---------- UAT-019 (curl captures Set-Cookie reliably) ----------
    jar = Path(os.environ.get("TEMP", "/tmp")) / f"ecmp-r602-{suffix}.jar"
    if jar.exists():
        jar.unlink()
    login_hdr = subprocess.check_output(
        [
            "curl.exe",
            "-sS",
            "-D",
            "-",
            "-o",
            "NUL",
            "-c",
            str(jar),
            "-b",
            str(jar),
            "-X",
            "POST",
            f"{BASE}/api/v1/auth/login",
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(
                {
                    "username": "golive_supervisor",
                    "password": "GoLive!Supv#2026",
                }
            ),
        ],
        text=True,
        stderr=subprocess.STDOUT,
    )
    logout_hdr = subprocess.check_output(
        [
            "curl.exe",
            "-sS",
            "-D",
            "-",
            "-o",
            "NUL",
            "-c",
            str(jar),
            "-b",
            str(jar),
            "-X",
            "POST",
            f"{BASE}/api/v1/auth/logout",
        ],
        text=True,
        stderr=subprocess.STDOUT,
    )
    refresh_out = subprocess.check_output(
        [
            "curl.exe",
            "-sS",
            "-w",
            "\nHTTP_CODE:%{http_code}",
            "-c",
            str(jar),
            "-b",
            str(jar),
            "-X",
            "POST",
            f"{BASE}/api/v1/auth/refresh",
        ],
        text=True,
        stderr=subprocess.STDOUT,
    )
    logout_set = ""
    for line in logout_hdr.splitlines():
        if line.lower().startswith("set-cookie:"):
            logout_set = line.split(":", 1)[1].strip()
            break
    m_code = re.search(r"HTTP_CODE:(\d+)", refresh_out)
    refresh_code = int(m_code.group(1)) if m_code else 0
    logout_status = 204 if "204" in logout_hdr.splitlines()[0] else 0
    uat019 = {
        "login_headers": login_hdr,
        "logout_headers": logout_hdr,
        "logout_status": logout_status,
        "logout_set_cookie": logout_set,
        "httponly": "httponly" in logout_set.lower(),
        "samesite": "samesite=lax" in logout_set.lower(),
        "expired_or_max_age_0": (
            "max-age=0" in logout_set.lower() or "expires=" in logout_set.lower()
        ),
        "secure_present": "secure" in logout_set.lower(),
        "refresh_after_logout": refresh_code,
        "refresh_body": refresh_out,
        "pass": logout_status == 204
        and "httponly" in logout_set.lower()
        and "samesite=lax" in logout_set.lower()
        and ("max-age=0" in logout_set.lower() or "expires=" in logout_set.lower())
        and refresh_code == 401,
    }
    evidence["UAT-019"] = uat019

    # ---------- UAT-018 ----------
    c = Client()
    c.login("golive_supervisor", "GoLive!Supv#2026")
    code, payload, _ = c.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"uat018_{suffix}",
            "email": f"uat018_{suffix}@example.com",
            "fullName": "UAT018",
            "password": "TempPass!234",
            "roleId": agent_role,
            "isActive": True,
        },
    )
    user_id = (payload or {}).get("data", {}).get("id")
    db_row = psql(
        f"SELECT force_password_change||'|'||role_id::text FROM users WHERE id='{user_id}'"
    )
    junction = psql(
        f"SELECT string_agg(role_id::text, ',') FROM user_roles WHERE user_id='{user_id}'"
    )
    code_bad, _, _ = c.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"bad_{suffix}",
            "email": f"bad_{suffix}@example.com",
            "fullName": "Bad",
            "password": "TempPass!234",
            "roleId": "00000000-0000-0000-0000-000000000000",
            "isActive": True,
        },
    )
    orphan = int(psql(f"SELECT count(*) FROM users WHERE username='bad_{suffix}'") or 0)
    uat018 = {
        "api_status": code,
        "api_body": payload,
        "db_row": db_row,
        "junction": junction,
        "invalid_role_status": code_bad,
        "orphan_count": orphan,
        "pass": code == 201
        and user_id is not None
        and db_row.lower().startswith(("t|", "true|"))
        and agent_role in junction
        and orphan == 0,
    }
    evidence["UAT-018"] = uat018

    # ---------- UAT-020 ----------
    code_esc, body_esc, _ = c.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"esc_{suffix}",
            "email": f"esc_{suffix}@example.com",
            "fullName": "Esc",
            "password": "TempPass!234",
            "roleId": admin_role,
            "isActive": True,
        },
    )
    code_off, body_off, _ = c.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"off_{suffix}",
            "email": f"off_{suffix}@example.com",
            "fullName": "Off",
            "password": "TempPass!234",
            "roleId": agent_role,
            "isActive": True,
        },
    )
    off_id = (body_off or {}).get("data", {}).get("id")
    code_upd, body_upd, _ = c.req(
        "PUT", f"/api/v1/users/{off_id}", {"roleId": admin_role}
    )
    code_asg, body_asg, _ = c.req(
        "PUT", f"/api/v1/users/{off_id}/roles", {"roleIds": [admin_role]}
    )
    uat020 = {
        "create_admin": {"status": code_esc, "body": body_esc},
        "update_admin": {"status": code_upd, "body": body_upd},
        "assign_admin": {"status": code_asg, "body": body_asg},
        "pass": code_esc == 403 and code_upd == 403 and code_asg == 403,
    }
    evidence["UAT-020"] = uat020

    # ---------- UAT-021 ----------
    admin = Client()
    admin.login("golive_admin", "GoLive!Admin#2026")
    code_s, body_s, _ = admin.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"sync_{suffix}",
            "email": f"sync_{suffix}@example.com",
            "fullName": "Sync",
            "password": "TempPass!234",
            "roleId": agent_role,
            "isActive": True,
        },
    )
    sync_id = body_s["data"]["id"]
    admin.req(
        "PUT",
        f"/api/v1/users/{sync_id}/roles",
        {"roleIds": [agent_role, viewer_role]},
    )
    before = psql(
        f"SELECT string_agg(r.code,',' ORDER BY r.code) FROM user_roles ur "
        f"JOIN roles r ON r.id=ur.role_id WHERE ur.user_id='{sync_id}'"
    )
    code_p, body_p, _ = admin.req(
        "PUT", f"/api/v1/users/{sync_id}", {"roleId": viewer_role}
    )
    after_primary = psql(
        f"SELECT r.code FROM users u JOIN roles r ON r.id=u.role_id WHERE u.id='{sync_id}'"
    )
    after_j = psql(
        f"SELECT string_agg(r.code,',' ORDER BY r.code) FROM user_roles ur "
        f"JOIN roles r ON r.id=ur.role_id WHERE ur.user_id='{sync_id}'"
    )
    # AGENT was primary → removed; VIEWER primary inserted; secondary VIEWER already present → VIEWER only
    uat021 = {
        "create_status": code_s,
        "update_status": code_p,
        "before": before,
        "after_primary": after_primary,
        "after_junction": after_j,
        "api_body": body_p,
        "pass": code_p == 200
        and after_primary == "VIEWER"
        and after_j == "VIEWER"
        and "AGENT" not in after_j,
    }
    evidence["UAT-021"] = uat021

    # ---------- UAT-022 ----------
    code_fp, body_fp, _ = admin.req(
        "POST",
        "/api/v1/users",
        {
            "username": f"fp_{suffix}",
            "email": f"fp_{suffix}@example.com",
            "fullName": "FP",
            "password": "TempPass!234",
            "roleId": agent_role,
            "isActive": True,
        },
    )
    fp_id = body_fp["data"]["id"]
    f1 = psql(f"SELECT force_password_change FROM users WHERE id='{fp_id}'")
    code_rst, body_rst, _ = admin.req("POST", f"/api/v1/users/{fp_id}/reset-password")
    f2 = psql(f"SELECT force_password_change FROM users WHERE id='{fp_id}'")
    temp_pw = (body_rst or {}).get("data", {}).get("temporaryPassword")
    code_apw, _, _ = admin.req(
        "PUT", f"/api/v1/users/{fp_id}", {"password": "AdminSet!2345"}
    )
    f3 = psql(f"SELECT force_password_change FROM users WHERE id='{fp_id}'")
    self_c = Client()
    self_c.login(f"fp_{suffix}", "AdminSet!2345")
    code_self, body_self, _ = self_c.req(
        "POST",
        "/api/v1/users/me/change-password",
        {
            "currentPassword": "AdminSet!2345",
            "newPassword": "SelfChanged!234",
            "confirmPassword": "SelfChanged!234",
        },
    )
    f4 = psql(f"SELECT force_password_change FROM users WHERE id='{fp_id}'")
    # Forgot password: set force true, request reset, extract token from logs, reset clears flag
    psql(f"UPDATE users SET force_password_change=true WHERE id='{fp_id}'")
    code_fg, body_fg, _ = Client().req(
        "POST", "/api/v1/auth/forgot-password", {"email": f"fp_{suffix}@example.com"}
    )
    logs = sh(["docker", "logs", "ecmp-backend", "--tail", "120"])
    m = re.findall(r"reset-password\?token=([A-Za-z0-9_\-]+)", logs)
    token = m[-1] if m else None
    code_rr, body_rr, _ = (None, None, None)
    if token:
        code_rr, body_rr, _ = Client().req(
            "POST",
            "/api/v1/auth/reset-password",
            {
                "token": token,
                "password": "ForgotReset!234",
                "confirmPassword": "ForgotReset!234",
            },
        )
    f5 = psql(f"SELECT force_password_change FROM users WHERE id='{fp_id}'")
    uat022 = {
        "create_force": f1,
        "after_admin_reset": f2,
        "temp_password_present": bool(temp_pw),
        "after_admin_change": f3,
        "self_change_status": code_self,
        "after_self_change": f4,
        "forgot_status": code_fg,
        "reset_status": code_rr,
        "after_forgot_reset": f5,
        "pass": f1 == "t"
        and f2 == "t"
        and f3 == "t"
        and code_self == 200
        and f4 == "f"
        and code_fg == 200
        and code_rr == 200
        and f5 == "f",
    }
    evidence["UAT-022"] = uat022

    # ---------- ADMIN ----------
    code_me, body_me, _ = admin.req("GET", "/api/v1/auth/me")
    perms = body_me["data"]["permissions"]
    dup = int(
        psql(
            "SELECT count(*) FROM (SELECT role_id, permission_id FROM role_permissions "
            "GROUP BY 1,2 HAVING count(*)>1) x"
        )
        or 0
    )
    orphan_m = int(
        psql(
            "SELECT count(*) FROM role_permissions rp WHERE NOT EXISTS "
            "(SELECT 1 FROM permissions p WHERE p.id=rp.permission_id) OR NOT EXISTS "
            "(SELECT 1 FROM roles r WHERE r.id=rp.role_id)"
        )
        or 0
    )
    admin_cnt = int(
        psql(
            "SELECT count(*) FROM role_permissions rp JOIN roles r ON r.id=rp.role_id "
            "WHERE r.code='ADMIN'"
        )
        or 0
    )
    missing_vs_sa = psql(
        "SELECT string_agg(code, ',' ORDER BY code) FROM ("
        " SELECT p.code FROM role_permissions rp JOIN roles r ON r.id=rp.role_id "
        " JOIN permissions p ON p.id=rp.permission_id WHERE r.code='SUPER_ADMIN' "
        " EXCEPT "
        " SELECT p.code FROM role_permissions rp JOIN roles r ON r.id=rp.role_id "
        " JOIN permissions p ON p.id=rp.permission_id WHERE r.code='ADMIN'"
        ") x"
    )
    admin_audit = {
        "me_status": code_me,
        "effective_count": len(perms),
        "db_count": admin_cnt,
        "duplicates": dup,
        "orphans": orphan_m,
        "missing_vs_super_admin": missing_vs_sa,
        "has_wildcard": "*" in perms,
        "pass": code_me == 200
        and admin_cnt == 46
        and dup == 0
        and orphan_m == 0
        and not missing_vs_sa
        and len(perms) >= 44,
    }
    evidence["ADMIN"] = admin_audit

    # Matrix
    matrix = {
        k: ("PASS" if evidence[k]["pass"] else "FAIL")
        for k in ("UAT-018", "UAT-019", "UAT-020", "UAT-021", "UAT-022", "ADMIN")
    }
    evidence["matrix"] = matrix
    OUT.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(matrix, indent=2))
    print(f"Wrote {OUT}")
    for k, v in matrix.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()

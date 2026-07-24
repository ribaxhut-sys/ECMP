"""TASK-028 System Settings UAT (run against local backend)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import http.cookiejar


BASE = "http://127.0.0.1:8000"


class Client:
    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        self.token: str | None = None

    def req(self, method: str, path: str, body: dict | None = None):
        data = None if body is None else json.dumps(body).encode()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            BASE + path, data=data, headers=headers, method=method
        )
        try:
            with self.opener.open(request) as resp:
                raw = resp.read().decode()
                code = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode()
            code = exc.code
        payload = json.loads(raw) if raw else None
        return code, payload

    def login(self, username: str, password: str) -> None:
        code, payload = self.req(
            "POST",
            "/api/v1/auth/login",
            {"username": username, "password": password},
        )
        assert code == 200, payload
        self.token = payload["data"]["accessToken"]


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"PASS: {msg}")


def main() -> None:
    # Public — no auth
    anon = Client()
    code, pub = anon.req("GET", "/api/v1/settings/public")
    assert_true(code == 200, f"public settings HTTP {code}")
    assert_true(isinstance(pub["data"], list) and len(pub["data"]) >= 1, "public non-empty")
    assert_true(
        all(item["visibility"] == "PUBLIC" for item in pub["data"]),
        "public visibility only",
    )
    pub_keys = {item["key"] for item in pub["data"]}
    assert_true("company.name" in pub_keys, "company.name public")
    assert_true("dashboard.recent.limit" not in pub_keys, "protected excluded from public")

    admin = Client()
    admin.login("golive_admin", "GoLive!Admin#2026")

    code, all_settings = admin.req("GET", "/api/v1/settings")
    assert_true(code == 200, f"list settings HTTP {code}")
    keys = {item["key"] for item in all_settings["data"]}
    for expected in (
        "company.name",
        "company.logo",
        "app.language.default",
        "app.timezone",
        "dashboard.recent.limit",
        "complaint.number.prefix",
    ):
        assert_true(expected in keys, f"seed key {expected}")

    # Update company.name
    original = next(
        item["value"] for item in all_settings["data"] if item["key"] == "company.name"
    )
    code, updated = admin.req(
        "PUT", "/api/v1/settings/company.name", {"value": "ECMP UAT"}
    )
    assert_true(code == 200, f"update company.name HTTP {code}")
    assert_true(updated["data"]["value"] == "ECMP UAT", "value persisted")

    # Invalid integer
    code, bad = admin.req(
        "PUT", "/api/v1/settings/dashboard.recent.limit", {"value": "nope"}
    )
    assert_true(code == 400, f"invalid int rejected HTTP {code}")
    assert_true(bad["code"] == "VALIDATION_ERROR", "validation error code")

    # Restore
    code, _ = admin.req(
        "PUT", "/api/v1/settings/company.name", {"value": original}
    )
    assert_true(code == 200, "restore company.name")

    # Agent cannot update
    agent = Client()
    agent.login("golive_agent", "GoLive!Agent#2026")
    code, _ = agent.req("GET", "/api/v1/settings")
    assert_true(code == 403, f"agent list denied HTTP {code}")

    print("TASK-028 UAT complete.")


if __name__ == "__main__":
    main()

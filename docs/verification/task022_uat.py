"""TASK-022 SLA Policy & Configuration API UAT (run against local backend)."""

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
    admin = Client()
    admin.login("golive_admin", "GoLive!Admin#2026")

    suffix = __import__("uuid").uuid4().hex[:8]
    name = f"TASK-022 Policy {suffix}"
    body = {
        "name": name,
        "description": "UAT policy — targets only",
        "assignmentTargetMinutes": 30,
        "appointmentTargetMinutes": 120,
        "resolutionTargetMinutes": 240,
        "escalationTargetMinutes": 90,
        "overallTargetMinutes": 480,
    }

    code, created = admin.req("POST", "/api/v1/sla/policies", body)
    assert_true(code == 201, f"create policy HTTP {code}")
    policy = created["data"]
    pid = policy["id"]
    assert_true(policy.get("name") == name, "created policy name matches")
    assert_true(policy.get("isActive") is False, "new policy is inactive")
    assert_true(
        policy.get("assignmentTargetMinutes") == 30,
        "assignment target stored",
    )

    code, activated = admin.req("PUT", f"/api/v1/sla/policies/{pid}/activate")
    assert_true(code == 200, f"activate policy HTTP {code}")
    assert_true(activated["data"].get("isActive") is True, "activated isActive=true")

    code, listed = admin.req("GET", "/api/v1/sla/policies")
    assert_true(code == 200, f"list policies HTTP {code}")
    items = listed["data"]
    assert_true(isinstance(items, list), "list returns array")
    match = next((p for p in items if p["id"] == pid), None)
    assert_true(match is not None, "created policy in list")
    assert_true(match.get("isActive") is True, "active badge source isActive=true")
    active_count = sum(1 for p in items if p.get("isActive"))
    assert_true(active_count == 1, f"only one active policy (count={active_count})")

    print(
        "UAT PASS",
        json.dumps({"policyId": pid, "name": name, "isActive": True}),
    )
    print(
        "UI CHECK: open /settings, confirm Active badge on policy %r" % name
    )


if __name__ == "__main__":
    main()

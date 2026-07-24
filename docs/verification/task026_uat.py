"""TASK-026 KPI Foundation UAT (run against local backend)."""

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
    sup = Client()
    sup.login("golive_supervisor", "GoLive!Supv#2026")

    suffix = __import__("uuid").uuid4().hex[:8]

    # Ensure active SLA policy for complaint create
    body = {
        "name": f"TASK-026 Policy {suffix}",
        "description": "KPI UAT",
        "assignmentTargetMinutes": 60,
        "appointmentTargetMinutes": 120,
        "resolutionTargetMinutes": 240,
        "escalationTargetMinutes": 90,
        "overallTargetMinutes": 480,
    }
    code, created_p = admin.req("POST", "/api/v1/sla/policies", body)
    assert_true(code == 201, f"create policy HTTP {code}")
    code, _ = admin.req(
        "PUT", f"/api/v1/sla/policies/{created_p['data']['id']}/activate"
    )
    assert_true(code == 200, "activate policy")

    _, custs = sup.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    code, before = admin.req("GET", "/api/v1/kpi/summary")
    assert_true(code == 200, f"KPI summary HTTP {code}")
    assert_true("complaints" in before["data"], "complaints block present")
    assert_true("assignment" in before["data"], "assignment block present")
    total_before = before["data"]["complaints"]["total"]

    # Create sample complaints
    for i, priority in enumerate(("HIGH", "MEDIUM")):
        code, _ = admin.req(
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": f"TASK-026 KPI {suffix} {i}",
                "description": "KPI foundation sample",
                "priority": priority,
                "channel": "WEB",
                "category": "BILLING",
            },
        )
        assert_true(code in (200, 201), f"create complaint {i} HTTP {code}")

    code, after = admin.req("GET", "/api/v1/kpi/summary")
    assert_true(code == 200, "KPI summary after creates")
    total_after = after["data"]["complaints"]["total"]
    assert_true(total_after >= total_before + 2, "total increased by samples")
    assert_true(after["data"]["complaints"]["open"] >= 2, "open complaints counted")

    # Filters
    code, high = admin.req("GET", "/api/v1/kpi/summary?priority=HIGH")
    assert_true(code == 200, "priority filter")
    assert_true(
        high["data"]["complaints"]["total"] >= 1,
        "HIGH priority filter returns data",
    )

    code, billing = admin.req("GET", "/api/v1/kpi/summary?category=BILLING")
    assert_true(code == 200, "category filter")
    assert_true(
        billing["data"]["complaints"]["total"] >= 2,
        "BILLING category filter returns samples",
    )

    # Structure checks
    for key in ("assignment", "appointment", "resolution", "escalation", "overall"):
        block = after["data"][key]
        assert_true("completed" in block and "breached" in block, f"{key} metrics")

    print(
        "UAT PASS",
        json.dumps(
            {
                "totalBefore": total_before,
                "totalAfter": total_after,
                "open": after["data"]["complaints"]["open"],
                "closed": after["data"]["complaints"]["closed"],
                "assignmentCompleted": after["data"]["assignment"]["completed"],
                "assignmentBreached": after["data"]["assignment"]["breached"],
            }
        ),
    )
    print("UI CHECK: open /dashboard and confirm KPI Summary card")


if __name__ == "__main__":
    main()

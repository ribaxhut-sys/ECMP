"""TASK-027 Dashboard API UAT (run against local backend)."""

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

    # Ensure active SLA policy
    body = {
        "name": f"TASK-027 Policy {suffix}",
        "description": "Dashboard UAT",
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

    _, custs = admin.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    code, before = admin.req("GET", "/api/v1/dashboard/summary")
    assert_true(code == 200, f"dashboard summary HTTP {code}")
    data = before["data"]
    assert_true("header" in data, "header present")
    assert_true("sla" in data, "sla present")
    assert_true("recentActivity" in data, "recentActivity present")
    total_before = data["header"]["totalComplaints"]

    created_numbers: list[str] = []
    for i, priority in enumerate(("HIGH", "MEDIUM")):
        code, created = admin.req(
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": f"TASK-027 Dashboard {suffix} {i}",
                "description": "Dashboard API sample",
                "priority": priority,
                "channel": "WEB",
                "category": "BILLING",
            },
        )
        assert_true(code in (200, 201), f"create complaint {i} HTTP {code}")
        created_numbers.append(created["data"]["complaintNumber"])

    code, after = admin.req("GET", "/api/v1/dashboard/summary")
    assert_true(code == 200, "dashboard summary after creates")
    body = after["data"]
    assert_true(
        body["header"]["totalComplaints"] >= total_before + 2,
        "total increased",
    )
    assert_true(body["header"]["openComplaints"] >= 2, "open counted")
    for key in ("assignment", "appointment", "resolution", "escalation", "overall"):
        block = body["sla"][key]
        assert_true(
            "completed" in block and "breached" in block,
            f"sla.{key} metrics",
        )

    assert_true(isinstance(body["recentActivity"], list), "recentActivity list")
    assert_true(len(body["recentActivity"]) <= 10, "recentActivity max 10")
    if body["recentActivity"]:
        item = body["recentActivity"][0]
        for field in ("eventType", "complaintNumber", "timestamp", "actor"):
            assert_true(field in item, f"recentActivity.{field}")
        numbers = {row["complaintNumber"] for row in body["recentActivity"]}
        assert_true(
            any(n in numbers for n in created_numbers),
            "created complaints appear in recent activity",
        )

    # Supervisor with dashboard:read
    code, sup_summary = sup.req("GET", "/api/v1/dashboard/summary")
    assert_true(code == 200, f"supervisor dashboard:read HTTP {code}")
    assert_true("header" in sup_summary["data"], "supervisor sees header")

    print(
        "UAT PASS",
        json.dumps(
            {
                "totalBefore": total_before,
                "totalAfter": body["header"]["totalComplaints"],
                "open": body["header"]["openComplaints"],
                "closed": body["header"]["closedComplaints"],
                "recentCount": len(body["recentActivity"]),
                "sampleNumbers": created_numbers,
            }
        ),
    )
    print("UI CHECK: open /dashboard — Header, SLA, Recent Activity cards")


if __name__ == "__main__":
    main()

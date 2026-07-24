"""TASK-023 SLA Deadline Calculator UAT (run against local backend)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import http.cookiejar
from datetime import datetime, timedelta


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


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    admin = Client()
    admin.login("golive_admin", "GoLive!Admin#2026")
    actor = Client()
    actor.login("golive_supervisor", "GoLive!Supv#2026")

    suffix = __import__("uuid").uuid4().hex[:8]

    # 1) Create + activate policy A
    body_a = {
        "name": f"TASK-023 Policy A {suffix}",
        "description": "UAT policy A",
        "assignmentTargetMinutes": 60,
        "appointmentTargetMinutes": 120,
        "resolutionTargetMinutes": 240,
        "escalationTargetMinutes": 90,
        "overallTargetMinutes": 480,
    }
    code, created_a = admin.req("POST", "/api/v1/sla/policies", body_a)
    assert_true(code == 201, f"create policy A HTTP {code}")
    pid_a = created_a["data"]["id"]
    code, _ = admin.req("PUT", f"/api/v1/sla/policies/{pid_a}/activate")
    assert_true(code == 200, "activate policy A")

    _, custs = actor.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    # 2) Create complaint under policy A
    code, created = actor.req(
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": f"TASK-023 SLA Deadlines {suffix}",
            "description": "Verify due dates from active policy.",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
    )
    assert_true(code in (200, 201), f"create complaint HTTP {code}")
    cid = created["data"]["id"]
    created_at = parse_dt(created["data"]["createdAt"])

    code, sla = actor.req("GET", f"/api/v1/complaints/{cid}/sla")
    assert_true(code == 200, "API-314 returns SLA")
    data = sla["data"]
    assert_true(data.get("complaintId") == cid, "SLA linked to complaint")

    for key in (
        "assignmentStatus",
        "appointmentStatus",
        "resolutionStatus",
        "escalationStatus",
        "overallStatus",
    ):
        assert_true(data.get(key) == "PENDING", f"{key} is PENDING")

    expected = {
        "assignmentDueAt": created_at + timedelta(minutes=60),
        "appointmentDueAt": created_at + timedelta(minutes=120),
        "resolutionDueAt": created_at + timedelta(minutes=240),
        "escalationDueAt": created_at + timedelta(minutes=90),
        "overallDueAt": created_at + timedelta(minutes=480),
    }
    for key, exp in expected.items():
        got = parse_dt(data[key])
        assert_true(got == exp, f"{key} matches policy A ({got.isoformat()})")

    frozen = {k: data[k] for k in expected}

    # 3) Activate different policy B
    body_b = {
        "name": f"TASK-023 Policy B {suffix}",
        "description": "UAT policy B — faster targets",
        "assignmentTargetMinutes": 15,
        "appointmentTargetMinutes": 30,
        "resolutionTargetMinutes": 45,
        "escalationTargetMinutes": 20,
        "overallTargetMinutes": 60,
    }
    code, created_b = admin.req("POST", "/api/v1/sla/policies", body_b)
    assert_true(code == 201, f"create policy B HTTP {code}")
    pid_b = created_b["data"]["id"]
    code, _ = admin.req("PUT", f"/api/v1/sla/policies/{pid_b}/activate")
    assert_true(code == 200, "activate policy B")

    # 4) Existing complaint deadlines unchanged
    code, sla2 = actor.req("GET", f"/api/v1/complaints/{cid}/sla")
    assert_true(code == 200, "re-fetch existing SLA")
    data2 = sla2["data"]
    for key, value in frozen.items():
        assert_true(data2[key] == value, f"existing {key} unchanged after policy B")

    # 5) New complaint uses policy B
    code, created2 = actor.req(
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": f"TASK-023 New under B {suffix}",
            "description": "Should use policy B targets.",
            "priority": "LOW",
            "channel": "WEB",
        },
    )
    assert_true(code in (200, 201), f"create second complaint HTTP {code}")
    cid2 = created2["data"]["id"]
    created2_at = parse_dt(created2["data"]["createdAt"])
    code, sla_new = actor.req("GET", f"/api/v1/complaints/{cid2}/sla")
    assert_true(code == 200, "SLA for new complaint")
    new_data = sla_new["data"]
    assert_true(
        parse_dt(new_data["assignmentDueAt"])
        == created2_at + timedelta(minutes=15),
        "new complaint uses policy B assignment target",
    )
    assert_true(
        parse_dt(new_data["overallDueAt"]) == created2_at + timedelta(minutes=60),
        "new complaint uses policy B overall target",
    )

    print(
        "UAT PASS",
        json.dumps(
            {
                "complaintId": cid,
                "newComplaintId": cid2,
                "policyA": pid_a,
                "policyB": pid_b,
                "assignmentDueAt": frozen["assignmentDueAt"],
                "overallDueAt": frozen["overallDueAt"],
            }
        ),
    )
    print(
        "UI CHECK: open /complaints/%s and confirm SLA card due dates + PENDING"
        % cid
    )


if __name__ == "__main__":
    main()

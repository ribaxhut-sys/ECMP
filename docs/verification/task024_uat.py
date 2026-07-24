"""TASK-024 SLA Breach Detection UAT (run against local backend)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import http.cookiejar
from datetime import datetime, timedelta, timezone

import psycopg


BASE = "http://127.0.0.1:8000"
DSN = "postgresql://ecmp:ecmp@127.0.0.1:5433/ecmp"


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


def backdate_dues(complaint_id: str) -> None:
    past = datetime.now(timezone.utc) - timedelta(hours=3)
    with psycopg.connect(DSN) as conn:
        conn.execute(
            """
            UPDATE sla_records
            SET assignment_due_at = %s,
                appointment_due_at = %s,
                resolution_due_at = %s,
                escalation_due_at = %s,
                overall_due_at = %s
            WHERE complaint_id = %s::uuid
            """,
            (past, past, past, past, past, complaint_id),
        )
        conn.commit()


def main() -> None:
    admin = Client()
    admin.login("golive_admin", "GoLive!Admin#2026")
    sup = Client()
    sup.login("golive_supervisor", "GoLive!Supv#2026")

    suffix = __import__("uuid").uuid4().hex[:8]
    body = {
        "name": f"TASK-024 Policy {suffix}",
        "description": "UAT breach detection",
        "assignmentTargetMinutes": 60,
        "appointmentTargetMinutes": 120,
        "resolutionTargetMinutes": 240,
        "escalationTargetMinutes": 90,
        "overallTargetMinutes": 480,
    }
    code, created_p = admin.req("POST", "/api/v1/sla/policies", body)
    assert_true(code == 201, f"create policy HTTP {code}")
    pid = created_p["data"]["id"]
    code, _ = admin.req("PUT", f"/api/v1/sla/policies/{pid}/activate")
    assert_true(code == 200, "activate policy")

    _, custs = sup.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]
    _, me = sup.req("GET", "/api/v1/auth/me")
    # Prefer an agent assignee when available; fall back to self.
    code, users = admin.req("GET", "/api/v1/users?page=1&pageSize=20")
    assignee_id = me["data"]["id"]
    if code == 200:
        for u in users.get("data") or []:
            if u.get("username") == "golive_agent":
                assignee_id = u["id"]
                break

    # 1) Create + assign before due → COMPLETED
    code, c1 = sup.req(
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": f"TASK-024 Completed {suffix}",
            "description": "Assign before due",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
    )
    assert_true(code in (200, 201), f"create complaint 1 HTTP {code}")
    cid1 = c1["data"]["id"]

    code, _ = sup.req(
        "POST",
        f"/api/v1/complaints/{cid1}/assign",
        {"assigneeId": assignee_id},
    )
    assert_true(code == 200, f"assign complaint 1 HTTP {code}")

    code, sla1 = sup.req("GET", f"/api/v1/complaints/{cid1}/sla")
    assert_true(code == 200, "fetch SLA after assign")
    assert_true(
        sla1["data"]["assignmentStatus"] == "COMPLETED",
        f"assignment COMPLETED ({sla1['data']['assignmentStatus']})",
    )

    # 2) Create another, pass due → BREACHED
    code, c2 = sup.req(
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": f"TASK-024 Breached {suffix}",
            "description": "Pass due without completion",
            "priority": "HIGH",
            "channel": "WEB",
        },
    )
    assert_true(code in (200, 201), f"create complaint 2 HTTP {code}")
    cid2 = c2["data"]["id"]

    backdate_dues(cid2)
    assert_true(True, "backdated due timestamps (simulate pass due)")

    code, sla2 = sup.req("GET", f"/api/v1/complaints/{cid2}/sla")
    assert_true(code == 200, "fetch SLA after due passed")
    assert_true(
        sla2["data"]["assignmentStatus"] == "BREACHED",
        f"assignment BREACHED ({sla2['data']['assignmentStatus']})",
    )
    assert_true(
        sla2["data"]["overallStatus"] == "BREACHED",
        f"overall BREACHED ({sla2['data']['overallStatus']})",
    )

    print(
        "UAT PASS",
        json.dumps(
            {
                "completedComplaintId": cid1,
                "breachedComplaintId": cid2,
                "assignmentCompleted": sla1["data"]["assignmentStatus"],
                "assignmentBreached": sla2["data"]["assignmentStatus"],
                "overallBreached": sla2["data"]["overallStatus"],
            }
        ),
    )
    print(
        "UI CHECK: open /complaints/%s (COMPLETED) and /complaints/%s (BREACHED)"
        % (cid1, cid2)
    )


if __name__ == "__main__":
    main()

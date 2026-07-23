"""TASK-016 Appointment Completion API UAT (run against local backend)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import http.cookiejar
from datetime import date, timedelta

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


def _ho_engineer_role_id() -> str | None:
    """Resolve HO_ENGINEER role id from local Postgres (Docker)."""
    import subprocess

    try:
        out = subprocess.check_output(
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
                "SELECT id FROM roles WHERE code = 'HO_ENGINEER' LIMIT 1;",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def ensure_engineer(sup: Client) -> Client:
    """Create golive_engineer (HO_ENGINEER) if missing; return logged-in client."""
    eng = Client()
    code, _ = eng.req(
        "POST",
        "/api/v1/auth/login",
        {"username": "golive_engineer", "password": "GoLive!Eng#2026"},
    )
    if code == 200:
        eng.login("golive_engineer", "GoLive!Eng#2026")
        return eng

    role_id = None
    code, probe = Client.req(
        sup, "GET", "/api/v1/users?page=1&pageSize=100&isActive=true"
    )
    assert_true(code == 200, "list users for engineer bootstrap")
    for u in probe["data"]:
        if u.get("roleCode") == "HO_ENGINEER":
            role_id = u["roleId"]
            break
    if not role_id:
        import os

        role_id = os.environ.get("HO_ENGINEER_ROLE_ID") or _ho_engineer_role_id()
    assert_true(bool(role_id), "HO_ENGINEER role id available")

    code, created = Client.req(
        sup,
        "POST",
        "/api/v1/users",
        {
            "username": "golive_engineer",
            "email": "golive.engineer@ecmp.local",
            "fullName": "GoLive Engineer",
            "password": "GoLive!Eng#2026",
            "roleId": role_id,
            "isActive": True,
        },
    )
    assert_true(code in (200, 201), f"create golive_engineer HTTP {code}: {created}")
    eng.login("golive_engineer", "GoLive!Eng#2026")
    return eng


def main() -> None:
    sup = Client()
    sup.login("golive_supervisor", "GoLive!Supv#2026")
    sch = Client()
    sch.login("golive_scheduler", "GoLive!Sched#2026")
    eng = ensure_engineer(sup)

    _, me_eng = eng.req("GET", "/api/v1/auth/me")
    assert_true(
        "appointments:complete" in me_eng["data"]["permissions"],
        "engineer has appointments:complete",
    )
    _, me_sch = sch.req("GET", "/api/v1/auth/me")
    assert_true(
        "appointments:complete" not in me_sch["data"]["permissions"],
        "scheduler lacks appointments:complete",
    )

    _, me_sup = Client.req(sup, "GET", "/api/v1/auth/me")
    user_id = me_sup["data"]["id"]
    _, custs = Client.req(sup, "GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]
    _, users = Client.req(sch, "GET", "/api/v1/users?page=1&pageSize=20&isActive=true")
    engineer_id = users["data"][0]["id"]
    for u in users["data"]:
        if u["id"] != user_id:
            engineer_id = u["id"]
            break

    day = (date.today() + timedelta(days=12)).isoformat()

    def new_checked_in(subject: str, start: str, end: str) -> tuple[str, str, str]:
        code, created = Client.req(
            sup,
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-016 UAT",
                "priority": "MEDIUM",
                "channel": "WEB",
            },
        )
        assert_true(code in (200, 201), f"create complaint HTTP {code}")
        cid = created["data"]["id"]
        Client.req(sup, "POST", f"/api/v1/complaints/{cid}/assign", {"assigneeId": user_id})
        Client.req(
            sup,
            "PATCH",
            f"/api/v1/complaints/{cid}/status",
            {"status": "IN_PROGRESS", "note": "Working"},
        )
        code, esc = Client.req(
            sup,
            "POST",
            f"/api/v1/complaints/{cid}/escalations",
            {
                "reasonCode": "SPECIALIST_REQUIRED",
                "reasonDescription": "Requires HO specialist.",
                "diagnosis": "Branch troubleshooting completed.",
            },
        )
        eid = esc["data"]["id"]
        Client.req(
            sch,
            "POST",
            f"/api/v1/escalations/{eid}/approve",
            {"reviewNotes": "Approved for completion UAT."},
        )
        code, booked = Client.req(
            sch,
            "POST",
            f"/api/v1/escalations/{eid}/appointments",
            {
                "appointmentDate": day,
                "startTime": start,
                "endTime": end,
                "assignedEngineerId": engineer_id,
                "notes": "UAT booking",
            },
        )
        assert_true(code == 200 and booked["data"]["status"] == "BOOKED", "booked")
        aid = booked["data"]["id"]
        code, cin = Client.req(
            sch,
            "POST",
            f"/api/v1/appointments/{aid}/check-in",
            {"notes": "Customer arrived."},
        )
        assert_true(code == 200 and cin["data"]["status"] == "CHECKED_IN", "checked in")
        return cid, eid, aid

    c1, e1, a1 = new_checked_in("TASK-016 Completion UAT", "11:00", "12:00")

    # Unauthorized user rejected (scheduler has review, not complete)
    code, _ = Client.req(
        sch,
        "POST",
        f"/api/v1/appointments/{a1}/complete",
        {"result": "COMPLETED", "notes": "Should fail"},
    )
    assert_true(code == 403, "unauthorized user rejected")

    # Complete success
    code, done = Client.req(
        eng,
        "POST",
        f"/api/v1/appointments/{a1}/complete",
        {
            "result": "COMPLETED",
            "notes": "Customer meeting completed successfully.",
        },
    )
    assert_true(
        code == 200 and done["data"]["status"] == "COMPLETED",
        "complete success COMPLETED",
    )
    assert_true(done["data"].get("completionResult") == "COMPLETED", "completionResult")
    assert_true(bool(done["data"].get("completedAt")), "completedAt set")
    assert_true(bool(done["data"].get("completedBy")), "completedBy set")

    _, c1get = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(
        c1get["data"]["status"] == "IN_PROGRESS",
        "complaint remains IN_PROGRESS",
    )
    _, e1get = Client.req(sch, "GET", f"/api/v1/escalations/{e1}")
    assert_true(e1get["data"]["status"] == "APPROVED", "escalation remains APPROVED")
    assert_true(
        e1get["data"].get("activeAppointment", {}).get("status") == "COMPLETED",
        "refresh embeds COMPLETED",
    )

    _, got = Client.req(sup, "GET", f"/api/v1/appointments/{a1}")
    assert_true(
        got["data"]["status"] == "COMPLETED"
        and got["data"].get("completionResult") == "COMPLETED"
        and bool(got["data"].get("completedAt")),
        "GET shows COMPLETED",
    )

    _, tl = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [
        x for x in tl["data"] if x["eventType"] == "complaint.appointment_completed"
    ]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Appointment completed",
        "timeline visible appointment_completed",
    )

    # Duplicate completion rejected
    code, dup = Client.req(
        eng,
        "POST",
        f"/api/v1/appointments/{a1}/complete",
        {"result": "PARTIALLY_COMPLETED", "notes": "Again"},
    )
    assert_true(code == 400, "duplicate completion rejected")
    msg = dup.get("message") or ""
    assert_true("already been completed" in msg.lower(), "duplicate message")

    ids = {"complaintId": c1, "escalationId": e1, "appointmentId": a1}
    print("UAT PASS", json.dumps(ids))


if __name__ == "__main__":
    main()

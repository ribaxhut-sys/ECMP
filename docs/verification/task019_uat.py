"""TASK-019 Complaint Closure API UAT (run against local backend)."""

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

    _, me_sup = Client.req(sup, "GET", "/api/v1/auth/me")
    assert_true(
        "complaints:close" in me_sup["data"]["permissions"],
        "supervisor has complaints:close",
    )
    _, me_eng = eng.req("GET", "/api/v1/auth/me")
    assert_true(
        "complaints:close" not in me_eng["data"]["permissions"],
        "engineer lacks complaints:close",
    )

    user_id = me_sup["data"]["id"]
    _, custs = Client.req(sup, "GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]
    _, users = Client.req(sch, "GET", "/api/v1/users?page=1&pageSize=20&isActive=true")
    engineer_id = users["data"][0]["id"]
    for u in users["data"]:
        if u["id"] != user_id:
            engineer_id = u["id"]
            break

    day = (date.today() + timedelta(days=18)).isoformat()

    def new_with_final_resolution(subject: str, start: str, end: str) -> tuple[str, str]:
        code, created = Client.req(
            sup,
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-019 UAT",
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
            {"reviewNotes": "Approved for closure UAT."},
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
        code, done = Client.req(
            eng,
            "POST",
            f"/api/v1/appointments/{aid}/complete",
            {
                "result": "COMPLETED",
                "notes": "Field work completed for closure UAT.",
            },
        )
        assert_true(code == 200 and done["data"]["status"] == "COMPLETED", "completed")
        code, fr = Client.req(
            eng,
            "POST",
            f"/api/v1/complaints/{cid}/final-resolution",
            {
                "summary": "Root cause identified and corrective action completed.",
                "notes": "Verified for closure UAT.",
                "followUpRequired": False,
            },
        )
        assert_true(
            code == 200 and fr["data"]["status"] == "FINAL_RESOLUTION_SUBMITTED",
            "final resolution submitted",
        )
        return cid, eid

    c1, e1 = new_with_final_resolution("TASK-019 Closure UAT", "10:00", "11:00")

    # Unauthorized rejected
    code, _ = Client.req(
        eng,
        "POST",
        f"/api/v1/complaints/{c1}/close",
        {"notes": "Should fail"},
    )
    assert_true(code == 403, "unauthorized rejected")

    # Close Complaint
    code, closed = Client.req(
        sup,
        "POST",
        f"/api/v1/complaints/{c1}/close",
        {"notes": "Complaint verified and officially closed."},
    )
    assert_true(
        code == 200 and closed["data"]["status"] == "CLOSED",
        "close complaint success",
    )
    assert_true(bool(closed["data"].get("closedAt")), "closedAt set")
    assert_true(bool(closed["data"].get("closedBy")), "closedBy set")

    _, e1get = Client.req(sch, "GET", f"/api/v1/escalations/{e1}")
    assert_true(e1get["data"]["status"] == "APPROVED", "escalation remains APPROVED")

    # Refresh displays CLOSED
    code, got = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(code == 200 and got["data"]["status"] == "CLOSED", "refresh displays CLOSED")
    assert_true(bool(got["data"].get("closedAt")), "refresh shows closedAt")
    assert_true(
        "officially closed" in (got["data"].get("closureNotes") or ""),
        "refresh shows closureNotes",
    )

    _, tl = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [x for x in tl["data"] if x["eventType"] == "complaint.closed"]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Complaint closed",
        "timeline visible complaint.closed",
    )

    # Duplicate rejected
    code, dup = Client.req(
        sup,
        "POST",
        f"/api/v1/complaints/{c1}/close",
        {"notes": "Again"},
    )
    assert_true(code == 400, "duplicate rejected")
    msg = (dup or {}).get("message") or ""
    assert_true("already closed" in msg.lower(), "duplicate message")

    ids = {"complaintId": c1, "escalationId": e1}
    print("UAT PASS", json.dumps(ids))


if __name__ == "__main__":
    main()

"""TASK-020 Escalation Closure API UAT (run against local backend)."""

from __future__ import annotations

import json
import os
import subprocess
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


def _role_id(code: str) -> str | None:
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
                f"SELECT id FROM roles WHERE code = '{code}' LIMIT 1;",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def ensure_user(
    creator: Client,
    *,
    username: str,
    password: str,
    email: str,
    full_name: str,
    role_code: str,
) -> Client:
    client = Client()
    code, _ = client.req(
        "POST",
        "/api/v1/auth/login",
        {"username": username, "password": password},
    )
    if code == 200:
        client.login(username, password)
        return client

    role_id = None
    code, probe = creator.req("GET", "/api/v1/users?page=1&pageSize=100&isActive=true")
    assert_true(code == 200, f"list users for {role_code} bootstrap")
    for u in probe["data"]:
        if u.get("roleCode") == role_code:
            role_id = u["roleId"]
            break
    if not role_id:
        role_id = os.environ.get(f"{role_code}_ROLE_ID") or _role_id(role_code)
    assert_true(bool(role_id), f"{role_code} role id available")

    code, created = creator.req(
        "POST",
        "/api/v1/users",
        {
            "username": username,
            "email": email,
            "fullName": full_name,
            "password": password,
            "roleId": role_id,
            "isActive": True,
        },
    )
    assert_true(
        code in (200, 201),
        f"create {username} HTTP {code}: {created}",
    )
    client.login(username, password)
    return client


def main() -> None:
    sup = Client()
    sup.login("golive_supervisor", "GoLive!Supv#2026")
    sch = Client()
    sch.login("golive_scheduler", "GoLive!Sched#2026")
    eng = ensure_user(
        sup,
        username="golive_engineer",
        password="GoLive!Eng#2026",
        email="golive.engineer@ecmp.local",
        full_name="GoLive Engineer",
        role_code="HO_ENGINEER",
    )
    admin = ensure_user(
        sup,
        username="golive_admin",
        password="GoLive!Admin#2026",
        email="golive.admin@ecmp.local",
        full_name="GoLive Admin",
        role_code="ADMIN",
    )

    _, me_admin = admin.req("GET", "/api/v1/auth/me")
    assert_true(
        "escalations:close" in me_admin["data"]["permissions"]
        or "*" in me_admin["data"]["permissions"],
        "admin has escalations:close",
    )
    _, me_sup = Client.req(sup, "GET", "/api/v1/auth/me")
    assert_true(
        "escalations:close" not in me_sup["data"]["permissions"],
        "supervisor lacks escalations:close",
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

    day = (date.today() + timedelta(days=19)).isoformat()

    def new_closed_complaint(subject: str, start: str, end: str) -> tuple[str, str]:
        code, created = Client.req(
            sup,
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-020 UAT",
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
            {"reviewNotes": "Approved for escalation closure UAT."},
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
                "notes": "Field work completed for escalation closure UAT.",
            },
        )
        assert_true(code == 200 and done["data"]["status"] == "COMPLETED", "completed")
        code, fr = Client.req(
            eng,
            "POST",
            f"/api/v1/complaints/{cid}/final-resolution",
            {
                "summary": "Root cause identified and corrective action completed.",
                "notes": "Verified for escalation closure UAT.",
                "followUpRequired": False,
            },
        )
        assert_true(
            code == 200 and fr["data"]["status"] == "FINAL_RESOLUTION_SUBMITTED",
            "final resolution submitted",
        )
        code, closed = Client.req(
            sup,
            "POST",
            f"/api/v1/complaints/{cid}/close",
            {"notes": "Complaint verified and officially closed."},
        )
        assert_true(
            code == 200 and closed["data"]["status"] == "CLOSED",
            "complaint closed before escalation close",
        )
        return cid, eid

    c1, e1 = new_closed_complaint("TASK-020 Escalation Closure UAT", "10:00", "11:00")

    # Unauthorized rejected (supervisor)
    code, _ = Client.req(
        sup,
        "POST",
        f"/api/v1/escalations/{e1}/close",
        {"notes": "Should fail"},
    )
    assert_true(code == 403, "unauthorized rejected")

    # Close Escalation
    code, closed = Client.req(
        admin,
        "POST",
        f"/api/v1/escalations/{e1}/close",
        {"notes": "Escalation verified and officially closed."},
    )
    assert_true(
        code == 200 and closed["data"]["status"] == "CLOSED",
        "close escalation success",
    )
    assert_true(bool(closed["data"].get("closedAt")), "closedAt set")
    assert_true(bool(closed["data"].get("closedBy")), "closedBy set")
    assert_true(
        closed["data"].get("escalationId") == e1,
        "escalationId in response",
    )

    # Refresh displays CLOSED
    code, eg = Client.req(admin, "GET", f"/api/v1/escalations/{e1}")
    assert_true(code == 200 and eg["data"]["status"] == "CLOSED", "refresh displays CLOSED")
    assert_true(bool(eg["data"].get("closedAt")), "refresh shows closedAt")
    assert_true(
        "officially closed" in (eg["data"].get("closureNotes") or ""),
        "refresh shows closureNotes",
    )

    code, cg = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(
        code == 200 and cg["data"]["status"] == "CLOSED",
        "complaint remains CLOSED",
    )

    _, tl = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [x for x in tl["data"] if x["eventType"] == "escalation.closed"]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Escalation closed",
        "timeline visible escalation.closed",
    )

    # Duplicate rejected
    code, dup = Client.req(
        admin,
        "POST",
        f"/api/v1/escalations/{e1}/close",
        {"notes": "Again"},
    )
    assert_true(code == 400, "duplicate rejected")
    msg = (dup or {}).get("message") or ""
    assert_true("already closed" in msg.lower(), "duplicate message")

    ids = {"complaintId": c1, "escalationId": e1}
    print("UAT PASS", json.dumps(ids))


if __name__ == "__main__":
    main()

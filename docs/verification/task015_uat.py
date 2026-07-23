"""TASK-015 Customer Check-In API UAT (run against local backend)."""

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


def main() -> None:
    sup = Client()
    sup.login("golive_supervisor", "GoLive!Supv#2026")
    sch = Client()
    sch.login("golive_scheduler", "GoLive!Sched#2026")

    _, me_sch = sch.req("GET", "/api/v1/auth/me")
    assert_true(
        "escalations:review" in me_sch["data"]["permissions"],
        "scheduler has escalations:review",
    )
    _, me_sup = sup.req("GET", "/api/v1/auth/me")
    assert_true(
        "escalations:review" not in me_sup["data"]["permissions"],
        "supervisor lacks escalations:review",
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

    day = (date.today() + timedelta(days=10)).isoformat()

    def new_booked(subject: str, start: str, end: str) -> tuple[str, str, str]:
        code, created = Client.req(
            sup,
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-015 UAT",
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
            {"reviewNotes": "Approved for check-in UAT."},
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
        return cid, eid, booked["data"]["id"]

    c1, e1, a1 = new_booked("TASK-015 Check-In UAT", "09:00", "10:00")

    # Unauthorized user rejected
    code, _ = Client.req(
        sup,
        "POST",
        f"/api/v1/appointments/{a1}/check-in",
        {"notes": "Should fail"},
    )
    assert_true(code == 403, "unauthorized user rejected")

    # Check-In success
    code, cin = Client.req(
        sch,
        "POST",
        f"/api/v1/appointments/{a1}/check-in",
        {"notes": "Customer arrived and identity verified."},
    )
    assert_true(
        code == 200 and cin["data"]["status"] == "CHECKED_IN",
        "check-in success CHECKED_IN",
    )
    assert_true(bool(cin["data"].get("checkedInAt")), "checkedInAt set")
    assert_true(bool(cin["data"].get("checkedInBy")), "checkedInBy set")

    _, c1get = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(
        c1get["data"]["status"] == "IN_PROGRESS",
        "complaint remains IN_PROGRESS",
    )
    _, e1get = Client.req(sch, "GET", f"/api/v1/escalations/{e1}")
    assert_true(e1get["data"]["status"] == "APPROVED", "escalation remains APPROVED")
    assert_true(
        e1get["data"].get("activeAppointment", {}).get("status") == "CHECKED_IN",
        "refresh embeds CHECKED_IN",
    )

    _, got = Client.req(sup, "GET", f"/api/v1/appointments/{a1}")
    assert_true(
        got["data"]["status"] == "CHECKED_IN"
        and bool(got["data"].get("checkedInAt")),
        "GET shows CHECKED_IN",
    )

    _, tl = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [x for x in tl["data"] if x["eventType"] == "complaint.appointment_checked_in"]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Customer checked in",
        "timeline visible appointment_checked_in",
    )

    # Duplicate Check-In rejected
    code, dup = Client.req(
        sch,
        "POST",
        f"/api/v1/appointments/{a1}/check-in",
        {"notes": "Again"},
    )
    assert_true(code == 400, "duplicate check-in rejected")
    msg = dup.get("message") or ""
    assert_true("already been checked in" in msg.lower(), "duplicate message")

    ids = {
        "complaintId": c1,
        "escalationId": e1,
        "appointmentId": a1,
    }
    print("IDS", json.dumps(ids))
    print("=== UAT COMPLETE ===")


if __name__ == "__main__":
    main()

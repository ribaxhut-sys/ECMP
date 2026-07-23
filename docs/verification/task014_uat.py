"""TASK-014 Appointment Booking API UAT (run against local backend)."""

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
    user_id = me_sup["data"]["id"]
    _, custs = sup.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    # Engineer for assignment — prefer a second active user if available.
    _, users = sch.req("GET", "/api/v1/users?page=1&pageSize=20&isActive=true")
    engineer_id = users["data"][0]["id"]
    for u in users["data"]:
        if u["id"] != user_id:
            engineer_id = u["id"]
            break

    day = (date.today() + timedelta(days=7)).isoformat()

    def new_approved(subject: str) -> tuple[str, str]:
        code, created = sup.req(
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-014 UAT",
                "priority": "MEDIUM",
                "channel": "WEB",
            },
        )
        assert_true(code in (200, 201), f"create complaint HTTP {code}")
        cid = created["data"]["id"]
        code, _ = Client.req(
            sup, "POST", f"/api/v1/complaints/{cid}/assign", {"assigneeId": user_id}
        )
        assert_true(code == 200, "assign HTTP 200")
        code, st = Client.req(
            sup,
            "PATCH",
            f"/api/v1/complaints/{cid}/status",
            {"status": "IN_PROGRESS", "note": "Working"},
        )
        assert_true(
            code == 200 and st["data"]["status"] == "IN_PROGRESS",
            "status IN_PROGRESS",
        )
        code, esc = Client.req(
            sup,
            "POST",
            f"/api/v1/complaints/{cid}/escalations",
            {
                "reasonCode": "SPECIALIST_REQUIRED",
                "reasonDescription": "Requires HO specialist.",
                "diagnosis": "Branch troubleshooting completed.",
                "notes": "UAT",
            },
        )
        assert_true(code == 200, "request escalation HTTP 200")
        eid = esc["data"]["id"]
        code, appr = Client.req(
            sch,
            "POST",
            f"/api/v1/escalations/{eid}/approve",
            {"reviewNotes": "Approved for appointment booking."},
        )
        assert_true(
            code == 200 and appr["data"]["status"] == "APPROVED",
            "approve escalation",
        )
        return cid, eid

    # --- Create appointment success ---
    c1, e1 = new_approved("TASK-014 Book UAT")
    code, booked = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e1}/appointments",
        {
            "appointmentDate": day,
            "startTime": "09:00",
            "endTime": "10:00",
            "assignedEngineerId": engineer_id,
            "notes": "Customer confirmed.",
        },
    )
    assert_true(
        code == 200 and booked["data"]["status"] == "BOOKED",
        "create appointment success BOOKED",
    )
    appt_id = booked["data"]["id"]

    _, c1get = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(
        c1get["data"]["status"] == "IN_PROGRESS",
        "complaint remains IN_PROGRESS after book",
    )
    _, e1get = Client.req(sch, "GET", f"/api/v1/escalations/{e1}")
    assert_true(e1get["data"]["status"] == "APPROVED", "escalation remains APPROVED")
    assert_true(
        e1get["data"].get("activeAppointment", {}).get("id") == appt_id,
        "escalation embeds activeAppointment",
    )

    _, tl1 = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [x for x in tl1["data"] if x["eventType"] == "complaint.appointment_booked"]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Appointment booked",
        "timeline appointment_booked",
    )

    code, got = Client.req(sup, "GET", f"/api/v1/appointments/{appt_id}")
    assert_true(
        code == 200 and got["data"]["id"] == appt_id and got["data"]["status"] == "BOOKED",
        "GET appointment works",
    )

    # --- Reject duplicate active ---
    code, dup = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e1}/appointments",
        {
            "appointmentDate": day,
            "startTime": "11:00",
            "endTime": "12:00",
            "assignedEngineerId": engineer_id,
        },
    )
    assert_true(code == 400, "reject duplicate active appointment")
    msg = dup.get("message") or ""
    assert_true(
        "already has an active appointment" in msg.lower(),
        "duplicate message",
    )

    # --- Reject if escalation not APPROVED ---
    c2, e2 = new_approved("TASK-014 Rejected Esc UAT")
    # create a REQUESTED (not approved) via new complaint without approve
    code, created = Client.req(
        sup,
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": "TASK-014 Not Approved",
            "description": "TASK-014 UAT",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
    )
    cid_req = created["data"]["id"]
    Client.req(sup, "POST", f"/api/v1/complaints/{cid_req}/assign", {"assigneeId": user_id})
    Client.req(
        sup,
        "PATCH",
        f"/api/v1/complaints/{cid_req}/status",
        {"status": "IN_PROGRESS", "note": "Working"},
    )
    code, esc_req = Client.req(
        sup,
        "POST",
        f"/api/v1/complaints/{cid_req}/escalations",
        {
            "reasonCode": "COMPLEX_CASE",
            "reasonDescription": "Still requested.",
            "diagnosis": "Pending review.",
        },
    )
    e_req = esc_req["data"]["id"]
    code, bad = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e_req}/appointments",
        {
            "appointmentDate": day,
            "startTime": "13:00",
            "endTime": "14:00",
            "assignedEngineerId": engineer_id,
        },
    )
    assert_true(code == 400, "reject if escalation is not APPROVED")
    msg2 = bad.get("message") or ""
    assert_true("must be APPROVED" in msg2, "not-approved message")

    # --- Reject overlapping engineer schedule ---
    c3, e3 = new_approved("TASK-014 Overlap UAT")
    code, overlap = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e3}/appointments",
        {
            "appointmentDate": day,
            "startTime": "09:30",
            "endTime": "10:30",
            "assignedEngineerId": engineer_id,
            "notes": "Overlap attempt",
        },
    )
    assert_true(code == 400, "reject overlapping engineer schedule")
    msg3 = overlap.get("message") or ""
    assert_true("overlap" in msg3.lower(), "overlap message")

    # Book non-overlapping on same day succeeds
    code, ok2 = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e3}/appointments",
        {
            "appointmentDate": day,
            "startTime": "14:00",
            "endTime": "15:00",
            "assignedEngineerId": engineer_id,
        },
    )
    assert_true(
        code == 200 and ok2["data"]["status"] == "BOOKED",
        "non-overlapping book succeeds",
    )

    ids = {
        "bookedComplaintId": c1,
        "bookedEscalationId": e1,
        "bookedAppointmentId": appt_id,
        "secondComplaintId": c2,
        "secondEscalationId": e2,
        "overlapComplaintId": c3,
        "overlapEscalationId": e3,
    }
    print("IDS", json.dumps(ids))
    print("=== UAT COMPLETE ===")


if __name__ == "__main__":
    main()

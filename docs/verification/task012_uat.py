"""TASK-012 Escalation Review API UAT (run against local backend)."""

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
    _, custs = sup.req("GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    def new_in_progress(subject: str) -> str:
        code, created = sup.req(
            "POST",
            "/api/v1/complaints",
            {
                "customerId": cust_id,
                "subject": subject,
                "description": "TASK-012 UAT",
                "priority": "MEDIUM",
                "channel": "WEB",
            },
        )
        assert_true(code in (200, 201), f"create complaint HTTP {code}")
        cid = created["data"]["id"]
        code, _ = sup.req(
            "POST",
            f"/api/v1/complaints/{cid}/assign",
            {"assigneeId": user_id},
        )
        assert_true(code == 200, "assign HTTP 200")
        code, st = sup.req(
            "PATCH",
            f"/api/v1/complaints/{cid}/status",
            {"status": "IN_PROGRESS", "note": "Working"},
        )
        assert_true(
            code == 200 and st["data"]["status"] == "IN_PROGRESS",
            "status IN_PROGRESS",
        )
        return cid

    def request_esc(cid: str) -> str:
        code, payload = sup.req(
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
        return payload["data"]["id"]

    c1 = new_in_progress("TASK-012 Approve UAT")
    e1 = request_esc(c1)

    code, _ = Client.req(
        sup, "POST", f"/api/v1/escalations/{e1}/approve", {"reviewNotes": "Should fail"}
    )
    assert_true(code == 403, "supervisor approve returns 403")

    code, appr = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e1}/approve",
        {"reviewNotes": "Approved for Head Office handling."},
    )
    assert_true(
        code == 200 and appr["data"]["status"] == "APPROVED",
        "approve REQUESTED returns APPROVED",
    )
    assert_true(
        bool(appr["data"].get("reviewedBy")) and bool(appr["data"].get("reviewedAt")),
        "approve stores reviewedBy/At",
    )

    _, c1get = Client.req(sup, "GET", f"/api/v1/complaints/{c1}")
    assert_true(
        c1get["data"]["status"] == "IN_PROGRESS",
        "complaint remains IN_PROGRESS after approve",
    )

    _, e1get = Client.req(sch, "GET", f"/api/v1/escalations/{e1}")
    assert_true(e1get["data"]["status"] == "APPROVED", "GET escalation APPROVED")
    assert_true(
        e1get["data"]["reviewNotes"] == "Approved for Head Office handling.",
        "GET has reviewNotes",
    )
    assert_true(bool(e1get["data"].get("reviewedByName")), "GET has reviewedByName")

    _, tl1 = Client.req(sup, "GET", f"/api/v1/complaints/{c1}/timeline")
    ev = [x for x in tl1["data"] if x["eventType"] == "complaint.escalation_approved"]
    assert_true(
        len(ev) > 0 and ev[0]["summary"] == "Escalation approved",
        "timeline escalation_approved",
    )

    code, err = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e1}/reject",
        {"reviewNotes": "Second try"},
    )
    assert_true(code == 400, "second review of APPROVED returns 400")
    msg = err.get("message") or (err.get("error") or {}).get("message")
    assert_true(
        msg == "Escalation has already been reviewed.",
        "APPROVED re-review message",
    )

    c2 = new_in_progress("TASK-012 Reject UAT")
    e2 = request_esc(c2)
    code, rej = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e2}/reject",
        {"reviewNotes": "Issue can be resolved by Branch."},
    )
    assert_true(
        code == 200 and rej["data"]["status"] == "REJECTED",
        "reject REQUESTED returns REJECTED",
    )
    _, c2get = Client.req(sup, "GET", f"/api/v1/complaints/{c2}")
    assert_true(
        c2get["data"]["status"] == "IN_PROGRESS",
        "complaint remains IN_PROGRESS after reject",
    )
    _, tl2 = Client.req(sup, "GET", f"/api/v1/complaints/{c2}/timeline")
    ev2 = [x for x in tl2["data"] if x["eventType"] == "complaint.escalation_rejected"]
    assert_true(
        len(ev2) > 0 and ev2[0]["summary"] == "Escalation rejected",
        "timeline escalation_rejected",
    )
    code, _ = Client.req(
        sch,
        "POST",
        f"/api/v1/escalations/{e2}/approve",
        {"reviewNotes": "Again"},
    )
    assert_true(code == 400, "review of REJECTED returns 400")

    c3 = new_in_progress("TASK-012 Review UI")
    e3 = request_esc(c3)

    ids = {
        "approveComplaintId": c1,
        "approveEscalationId": e1,
        "rejectComplaintId": c2,
        "pendingComplaintId": c3,
        "pendingEscalationId": e3,
    }
    print("IDS", json.dumps(ids))
    print("=== UAT COMPLETE ===")


if __name__ == "__main__":
    main()

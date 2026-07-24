"""TASK-021 SLA Domain Foundation API UAT (run against local backend)."""

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

    _, custs = Client.req(sup, "GET", "/api/v1/customers?page=1&pageSize=1")
    cust_id = custs["data"][0]["id"]

    code, created = Client.req(
        sup,
        "POST",
        "/api/v1/complaints",
        {
            "customerId": cust_id,
            "subject": "TASK-021 SLA Foundation UAT",
            "description": "Verify SLA card and API-314.",
            "priority": "MEDIUM",
            "channel": "WEB",
        },
    )
    assert_true(code in (200, 201), f"create complaint HTTP {code}")
    cid = created["data"]["id"]

    code, sla = Client.req(sup, "GET", f"/api/v1/complaints/{cid}/sla")
    assert_true(code == 200, "API returns SLA object")
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
    for key in (
        "assignmentDueAt",
        "appointmentDueAt",
        "resolutionDueAt",
        "escalationDueAt",
        "overallDueAt",
    ):
        assert_true(data.get(key) is None, f"{key} is null (no calculations)")

    code, got = Client.req(sup, "GET", f"/api/v1/complaints/{cid}")
    assert_true(code == 200, "complaint detail available for SLA card")

    print("UAT PASS", json.dumps({"complaintId": cid, "slaId": data.get("id")}))
    print("UI CHECK: open /complaints/%s and confirm SLA card shows PENDING" % cid)


if __name__ == "__main__":
    main()

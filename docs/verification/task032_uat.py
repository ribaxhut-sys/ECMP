"""TASK-032 Attachment Viewer UAT (API + frontend readiness checks)."""

from __future__ import annotations

import json
import uuid
import urllib.error
import urllib.request
import http.cookiejar


BASE = "http://127.0.0.1:8000"
FE = "http://127.0.0.1:3000"


class Client:
    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )
        self.token: str | None = None

    def req(self, method: str, path: str, body: dict | None = None, raw: bytes | None = None, headers: dict | None = None):
        data = raw if raw is not None else (None if body is None else json.dumps(body).encode())
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        if self.token:
            hdrs["Authorization"] = f"Bearer {self.token}"
        if raw is not None:
            hdrs.pop("Content-Type", None)
            hdrs.update(headers or {})
        request = urllib.request.Request(BASE + path, data=data, headers=hdrs, method=method)
        try:
            with self.opener.open(request) as resp:
                payload = resp.read()
                code = resp.status
                ctype = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            code = exc.code
            ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
        if "application/json" in ctype:
            return code, json.loads(payload.decode() or "null")
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


def upload(client: Client, filename: str, content_type: str, data: bytes) -> str:
    boundary = "----ECMP" + uuid.uuid4().hex
    object_id = str(uuid.uuid4())
    chunks = [
        f"--{boundary}".encode(),
        b'Content-Disposition: form-data; name="objectType"',
        b"",
        b"complaint",
        f"--{boundary}".encode(),
        b'Content-Disposition: form-data; name="objectId"',
        b"",
        object_id.encode(),
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(),
        f"Content-Type: {content_type}".encode(),
        b"",
        data,
        f"--{boundary}--".encode(),
        b"",
    ]
    body = b"\r\n".join(chunks)
    code, payload = client.req(
        "POST",
        "/api/v1/attachments",
        raw=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    assert_true(code == 201, f"upload {filename} HTTP {code}")
    return payload["data"]["id"]


def main() -> None:
    client = Client()
    client.login("golive_admin", "GoLive!Admin#2026")

    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
    )
    pdf = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"

    png_id = upload(client, "uat-viewer.png", "image/png", png)
    pdf_id = upload(client, "uat-viewer.pdf", "application/pdf", pdf)

    code, meta = client.req("GET", f"/api/v1/attachments/{png_id}")
    assert_true(code == 200, f"metadata PNG HTTP {code}")
    assert_true(meta["data"]["mimeType"] == "image/png", "PNG mime")

    code, blob = client.req("GET", f"/api/v1/attachments/{png_id}/download")
    assert_true(code == 200, f"download PNG HTTP {code}")
    assert_true(isinstance(blob, (bytes, bytearray)) and len(blob) > 0, "PNG bytes")

    code, _ = client.req("GET", f"/api/v1/attachments/{pdf_id}/download")
    assert_true(code == 200, f"download PDF HTTP {code}")

    fe = urllib.request.urlopen(FE + "/attachments", timeout=5)
    assert_true(fe.status == 200, f"frontend /attachments HTTP {fe.status}")
    print(
        f"OPEN: {FE}/attachments?ids={png_id},{pdf_id}"
    )
    print("TASK-032 UAT PASS")


if __name__ == "__main__":
    main()

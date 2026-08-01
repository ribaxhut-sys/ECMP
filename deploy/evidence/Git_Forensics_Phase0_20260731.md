# Git Forensics — Phase 0 Evidence Collection

| Field | Value |
|---|---|
| Collected at | 2026-07-31 |
| Repository | `/opt/ECMP` |
| Collector role | Git Forensics Collector (evidence only) |
| Range | `$B..HEAD` where `B = git merge-base origin/main HEAD` |
| HEAD | `41a0f48bd316099498e3e6782cba383ddc977e1b` |
| origin/main | `c323f29b668ce096f543922fad587b32a9310811` |
| Branch status (at collection) | `main...origin/main [ahead 5, behind 14]` |
| Security | Secret-like values in diffs replaced with `[REDACTED]` |

---

## 1. Merge Base

```
B=$(git merge-base origin/main HEAD)
```

| Item | Value |
|---|---|
| Merge base (full) | `95baf196ef898f7ab4f8c722bc8c821df06e52d0` |
| Merge base (short) | `95baf19` |
| Commits in range `$B..HEAD` | `5` |

---

## 2. Commit Inventory

Command:

```bash
git log --format='%H|%h|%an|%ae|%ad|%s' --date=iso $B..HEAD
```

| Full hash | Short | Author | Email | Date (ISO) | Subject |
|---|---|---|---|---|---|
| `41a0f48bd316099498e3e6782cba383ddc977e1b` | `41a0f48` | root | root@srv1869401.hstgr.cloud | 2026-07-31 08:59:44 +0000 | Add login rate limiting and tighten SSH with UFW limit. |
| `ad4a37368321ce89adadd9bd70d16e2069eb4c2d` | `ad4a373` | root | root@srv1869401.hstgr.cloud | 2026-07-31 08:56:58 +0000 | Record non-destructive Postgres restore drill evidence. |
| `a476ebf9b630b48beca19f650179e80ccef799c4` | `a476ebf` | root | root@srv1869401.hstgr.cloud | 2026-07-31 08:56:36 +0000 | Add Users and Reports admin screens for the live lab. |
| `2f1348a178f80820fbe83ca150e351046b47688b` | `2f1348a` | root | root@srv1869401.hstgr.cloud | 2026-07-31 08:44:26 +0000 | Fix user provisioning so new accounts get IAM permissions. |
| `96f52eb21b1a2a68b0341e058ce17cd8545c7bf1` | `96f52eb` | root | root@srv1869401.hstgr.cloud | 2026-07-31 07:52:32 +0000 | Add HTTPS edge cutover for pengaduan.layanankami.tech. |

Chronological order (oldest → newest): `96f52eb` → `2f1348a` → `a476ebf` → `ad4a373` → `41a0f48`.

---

## 3. Changed Files

Command:

```bash
git log --name-status --format='===== %H %s =====' $B..HEAD
```

### 3.1 Per-commit name-status

#### `41a0f48` — Add login rate limiting and tighten SSH with UFW limit.

```
M	backend/app/core/errors.py
A	backend/app/core/rate_limit.py
M	backend/app/modules/auth/router.py
A	backend/tests/test_rate_limit.py
A	deploy/evidence/hardening-20260731.md
```

#### `ad4a373` — Record non-destructive Postgres restore drill evidence.

```
A	deploy/evidence/restore-drill-20260731.md
```

#### `a476ebf` — Add Users and Reports admin screens for the live lab.

```
A	deploy/evidence/backup-verify-20260731.md
M	frontend/src/app/(app)/reports/page.tsx
M	frontend/src/app/(app)/users/page.tsx
A	frontend/src/features/reports/ReportsView.tsx
A	frontend/src/features/reports/index.ts
A	frontend/src/features/users/UsersManagement.tsx
A	frontend/src/features/users/index.ts
M	frontend/src/lib/api/index.ts
A	frontend/src/lib/api/roles.ts
M	frontend/src/lib/api/users.ts
```

#### `2f1348a` — Fix user provisioning so new accounts get IAM permissions.

```
M	backend/app/modules/users/repository.py
M	backend/app/modules/users/service.py
M	backend/tests/test_users.py
M	deploy/README.md
M	deploy/SMOKE_UAT_2026-07-31.md
A	deploy/seed-lab-master-data.sql
```

#### `96f52eb` — Add HTTPS edge cutover for pengaduan.layanankami.tech.

```
A	.env.prod.example
M	.gitignore
A	27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md
A	deploy/Caddyfile
A	deploy/README.md
A	deploy/SMOKE_UAT_2026-07-31.md
A	deploy/backup-postgres.sh
A	docker-compose.prod.yml
```

### 3.2 Unique path inventory (`git diff --name-only $B..HEAD`)

```
.env.prod.example
.gitignore
27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md
backend/app/core/errors.py
backend/app/core/rate_limit.py
backend/app/modules/auth/router.py
backend/app/modules/users/repository.py
backend/app/modules/users/service.py
backend/tests/test_rate_limit.py
backend/tests/test_users.py
deploy/Caddyfile
deploy/README.md
deploy/SMOKE_UAT_2026-07-31.md
deploy/backup-postgres.sh
deploy/evidence/backup-verify-20260731.md
deploy/evidence/hardening-20260731.md
deploy/evidence/restore-drill-20260731.md
deploy/seed-lab-master-data.sql
docker-compose.prod.yml
frontend/src/app/(app)/reports/page.tsx
frontend/src/app/(app)/users/page.tsx
frontend/src/features/reports/ReportsView.tsx
frontend/src/features/reports/index.ts
frontend/src/features/users/UsersManagement.tsx
frontend/src/features/users/index.ts
frontend/src/lib/api/index.ts
frontend/src/lib/api/roles.ts
frontend/src/lib/api/users.ts
```

Total unique paths: **28**.

Rename detection (`git show --find-renames --diff-filter=R` on `41a0f48` and `96f52eb`): **none**.

---

## 4. Diff Statistics

Command:

```bash
git diff --stat $B..HEAD
```

```
 .env.prod.example                                  |  36 ++
 .gitignore                                         |   1 +
 .../DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md |  55 +++
 backend/app/core/errors.py                         |  12 +
 backend/app/core/rate_limit.py                     |  63 ++++
 backend/app/modules/auth/router.py                 |   3 +
 backend/app/modules/users/repository.py            |  37 +-
 backend/app/modules/users/service.py               |  15 +
 backend/tests/test_rate_limit.py                   |  34 ++
 backend/tests/test_users.py                        |   1 +
 deploy/Caddyfile                                   |  40 +++
 deploy/README.md                                   |  58 ++++
 deploy/SMOKE_UAT_2026-07-31.md                     |  25 ++
 deploy/backup-postgres.sh                          |  24 ++
 deploy/evidence/backup-verify-20260731.md          |   6 +
 deploy/evidence/hardening-20260731.md              |  11 +
 deploy/evidence/restore-drill-20260731.md          |  16 +
 deploy/seed-lab-master-data.sql                    |  48 +++
 docker-compose.prod.yml                            |  54 +++
 frontend/src/app/(app)/reports/page.tsx            |   9 +-
 frontend/src/app/(app)/users/page.tsx              |   9 +-
 frontend/src/features/reports/ReportsView.tsx      | 153 +++++++++
 frontend/src/features/reports/index.ts             |   1 +
 frontend/src/features/users/UsersManagement.tsx    | 377 +++++++++++++++++++++
 frontend/src/features/users/index.ts               |   1 +
 frontend/src/lib/api/index.ts                      |   6 +-
 frontend/src/lib/api/roles.ts                      |  26 ++
 frontend/src/lib/api/users.ts                      |  36 +-
 28 files changed, 1138 insertions(+), 19 deletions(-)
```

Numstat summary: **+1138 / −19** across **28** files.

---

## 5. Detailed Commit Evidence

### 5.1 All commits — `git show --stat --summary`

#### Commit `41a0f48bd316099498e3e6782cba383ddc977e1b`

```
commit 41a0f48bd316099498e3e6782cba383ddc977e1b
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 08:59:44 2026 +0000

    Add login rate limiting and tighten SSH with UFW limit.

    Protect the shared HTTPS lab from brute-force logins (10/min per IP) and rate-limit new SSH connections without blocking the current ops workflow.

    Co-authored-by: Cursor <cursoragent@cursor.com>

 backend/app/core/errors.py            | 12 +++++++
 backend/app/core/rate_limit.py        | 63 +++++++++++++++++++++++++++++++++++
 backend/app/modules/auth/router.py    |  3 ++
 backend/tests/test_rate_limit.py      | 34 +++++++++++++++++++
 deploy/evidence/hardening-20260731.md | 11 ++++++
 5 files changed, 123 insertions(+)
 create mode 100644 backend/app/core/rate_limit.py
 create mode 100644 backend/tests/test_rate_limit.py
 create mode 100644 deploy/evidence/hardening-20260731.md
```

#### Commit `ad4a37368321ce89adadd9bd70d16e2069eb4c2d`

```
commit ad4a37368321ce89adadd9bd70d16e2069eb4c2d
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 08:56:58 2026 +0000

    Record non-destructive Postgres restore drill evidence.

    Document a temp-database restore from the latest lab dump so backup integrity is proven without touching the live ECMP database.

    Co-authored-by: Cursor <cursoragent@cursor.com>

 deploy/evidence/restore-drill-20260731.md | 16 ++++++++++++++++
 1 file changed, 16 insertions(+)
 create mode 100644 deploy/evidence/restore-drill-20260731.md
```

#### Commit `a476ebf9b630b48beca19f650179e80ccef799c4`

```
commit a476ebf9b630b48beca19f650179e80ccef799c4
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 08:56:36 2026 +0000

    Add Users and Reports admin screens for the live lab.

    Replace placeholder routes with list/create users and report summary views wired to existing APIs, and record backup integrity evidence for the HTTPS environment.

    Co-authored-by: Cursor <cursoragent@cursor.com>

 deploy/evidence/backup-verify-20260731.md       |   6 +
 frontend/src/app/(app)/reports/page.tsx         |   9 +-
 frontend/src/app/(app)/users/page.tsx           |   9 +-
 frontend/src/features/reports/ReportsView.tsx   | 153 ++++++++++
 frontend/src/features/reports/index.ts          |   1 +
 frontend/src/features/users/UsersManagement.tsx | 377 ++++++++++++++++++++++++
 frontend/src/features/users/index.ts            |   1 +
 frontend/src/lib/api/index.ts                   |   6 +-
 frontend/src/lib/api/roles.ts                   |  26 ++
 frontend/src/lib/api/users.ts                   |  36 ++-
 10 files changed, 607 insertions(+), 17 deletions(-)
 create mode 100644 deploy/evidence/backup-verify-20260731.md
 create mode 100644 frontend/src/features/reports/ReportsView.tsx
 create mode 100644 frontend/src/features/reports/index.ts
 create mode 100644 frontend/src/features/users/UsersManagement.tsx
 create mode 100644 frontend/src/features/users/index.ts
 create mode 100644 frontend/src/lib/api/roles.ts
```

#### Commit `2f1348a178f80820fbe83ca150e351046b47688b`

```
commit 2f1348a178f80820fbe83ca150e351046b47688b
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 08:44:26 2026 +0000

    Fix user provisioning so new accounts get IAM permissions.

    Sync user_roles on create/role update and invalidate the permission cache, and add lab master-data seed plus UAT notes so complaint create/assign works on the shared HTTPS stack.

    Co-authored-by: Cursor <cursoragent@cursor.com>

 backend/app/modules/users/repository.py | 37 +++++++++++++++++++++++--
 backend/app/modules/users/service.py    | 15 +++++++++++
 backend/tests/test_users.py             |  1 +
 deploy/README.md                        | 11 ++++++++
 deploy/SMOKE_UAT_2026-07-31.md          | 12 +++++---
 deploy/seed-lab-master-data.sql         | 48 +++++++++++++++++++++++++++++++++
 6 files changed, 119 insertions(+), 5 deletions(-)
 create mode 100644 deploy/seed-lab-master-data.sql
```

#### Commit `96f52eb21b1a2a68b0341e058ce17cd8545c7bf1`

```
commit 96f52eb21b1a2a68b0341e058ce17cd8545c7bf1
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 07:52:32 2026 +0000

    Add HTTPS edge cutover for pengaduan.layanankami.tech.

    Introduce Caddy prod overlay, deploy runbook/backup script, DEC-020 auth phasing (local JWT now, SSO later), and smoke UAT notes so the VPS shared URL can run without Mode B SSO.

    Co-authored-by: Cursor <cursoragent@cursor.com>

 .env.prod.example                                  | 36 ++++++++++++++
 .gitignore                                         |  1 +
 .../DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md | 55 ++++++++++++++++++++++
 deploy/Caddyfile                                   | 40 ++++++++++++++++
 deploy/README.md                                   | 47 ++++++++++++++++++
 deploy/SMOKE_UAT_2026-07-31.md                     | 19 ++++++++
 deploy/backup-postgres.sh                          | 24 ++++++++++
 docker-compose.prod.yml                            | 54 +++++++++++++++++++++
 8 files changed, 276 insertions(+)
 create mode 100644 .env.prod.example
 create mode 100644 27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md
 create mode 100644 deploy/Caddyfile
 create mode 100644 deploy/README.md
 create mode 100644 deploy/SMOKE_UAT_2026-07-31.md
 create mode 100755 deploy/backup-postgres.sh
 create mode 100644 docker-compose.prod.yml
```

### 5.2 Full patch — `git show --find-renames` (requested commits only)

#### `41a0f48` — full show (no renames detected)

```
commit 41a0f48bd316099498e3e6782cba383ddc977e1b
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 08:59:44 2026 +0000

    Add login rate limiting and tighten SSH with UFW limit.

    Protect the shared HTTPS lab from brute-force logins (10/min per IP) and rate-limit new SSH connections without blocking the current ops workflow.

    Co-authored-by: Cursor <cursoragent@cursor.com>

diff --git a/backend/app/core/errors.py b/backend/app/core/errors.py
index ac579ef..1731dc4 100644
--- a/backend/app/core/errors.py
+++ b/backend/app/core/errors.py
@@ -89,3 +89,15 @@ class ConflictError(ApiError):

     def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
         super().__init__(409, "CONFLICT", message, details)
+
+
+class RateLimitError(ApiError):
+    """HTTP 429 — too many requests (e.g. login brute-force protection)."""
+
+    def __init__(
+        self,
+        message: str = "Too many requests. Try again later.",
+        *,
+        details: dict[str, Any] | None = None,
+    ) -> None:
+        super().__init__(429, "RATE_LIMITED", message, details)
diff --git a/backend/app/core/rate_limit.py b/backend/app/core/rate_limit.py
new file mode 100644
index 0000000..9f7312a
--- /dev/null
+++ b/backend/app/core/rate_limit.py
@@ -0,0 +1,63 @@
+"""Simple in-process fixed-window rate limiter (single-instance lab/prod compose)."""
+
+from __future__ import annotations
+
+import threading
+import time
+from collections import defaultdict, deque
+
+from app.core.errors import RateLimitError
+
+
+class FixedWindowRateLimiter:
+    """Allow ``limit`` events per ``window_seconds`` for each key."""
+
+    def __init__(self, *, limit: int, window_seconds: float) -> None:
+        if limit < 1:
+            raise ValueError("limit must be >= 1")
+        if window_seconds <= 0:
+            raise ValueError("window_seconds must be > 0")
+        self._limit = limit
+        self._window = window_seconds
+        self._hits: dict[str, deque[float]] = defaultdict(deque)
+        self._lock = threading.Lock()
+
+    def check(self, key: str) -> None:
+        now = time.monotonic()
+        with self._lock:
+            bucket = self._hits[key]
+            cutoff = now - self._window
+            while bucket and bucket[0] < cutoff:
+                bucket.popleft()
+            if len(bucket) >= self._limit:
+                retry_after = max(1, int(self._window - (now - bucket[0])) + 1)
+                raise RateLimitError(
+                    "Too many login attempts. Try again later.",
+                    details={"retryAfterSeconds": retry_after},
+                )
+            bucket.append(now)
+
+    def reset(self, key: str | None = None) -> None:
+        with self._lock:
+            if key is None:
+                self._hits.clear()
+            else:
+                self._hits.pop(key, None)
+
+
+# Lab/shared single-VM default: 10 attempts / minute / client IP.
+login_rate_limiter = FixedWindowRateLimiter(limit=10, window_seconds=60.0)
+
+
+def client_ip_from_request(request: object) -> str:
+    """Best-effort client IP behind Caddy (X-Forwarded-For) or direct socket."""
+    headers = getattr(request, "headers", None)
+    if headers is not None:
+        forwarded = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
+        if forwarded:
+            first = forwarded.split(",")[0].strip()
+            if first:
+                return first
+    client = getattr(request, "client", None)
+    host = getattr(client, "host", None) if client is not None else None
+    return host or "unknown"
diff --git a/backend/app/modules/auth/router.py b/backend/app/modules/auth/router.py
index 4c06128..81f6fb7 100644
--- a/backend/app/modules/auth/router.py
+++ b/backend/app/modules/auth/router.py
@@ -9,6 +9,7 @@ from sqlalchemy.orm import Session

 from app.core.auth import CurrentPrincipal
 from app.core.config import Settings, get_settings
+from app.core.rate_limit import client_ip_from_request, login_rate_limiter
 from app.core.schemas import DataResponse
 from app.db.session import get_db_session
 from app.modules.auth.repository import AuthRepository
@@ -68,10 +69,12 @@ def _read_refresh_cookie(request: Request, settings: Settings) -> str | None:
 )
 def login(
     payload: LoginRequest,
+    request: Request,
     response: Response,
     service: Annotated[AuthService, Depends(get_auth_service)],
     settings: Annotated[Settings, Depends(get_settings)],
 ) -> DataResponse[TokenResponse]:
+    login_rate_limiter.check(client_ip_from_request(request))
     session = service.login(payload)
     _set_refresh_cookie(response, raw_token=session.refresh_token, settings=settings)
     return DataResponse(data=session.tokens)
diff --git a/backend/tests/test_rate_limit.py b/backend/tests/test_rate_limit.py
new file mode 100644
index 0000000..9444b1d
--- /dev/null
+++ b/backend/tests/test_rate_limit.py
@@ -0,0 +1,34 @@
+"""Unit tests for fixed-window rate limiter."""
+
+from __future__ import annotations
+
+import pytest
+
+from app.core.errors import RateLimitError
+from app.core.rate_limit import FixedWindowRateLimiter
+
+
+def test_rate_limiter_allows_within_limit() -> None:
+    limiter = FixedWindowRateLimiter(limit=3, window_seconds=60)
+    limiter.check("ip-a")
+    limiter.check("ip-a")
+    limiter.check("ip-a")
+
+
+def test_rate_limiter_blocks_over_limit() -> None:
+    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)
+    limiter.check("ip-b")
+    limiter.check("ip-b")
+    with pytest.raises(RateLimitError) as exc:
+        limiter.check("ip-b")
+    assert exc.value.status_code == 429
+    assert exc.value.code == "RATE_LIMITED"
+    assert "retryAfterSeconds" in (exc.value.details or {})
+
+
+def test_rate_limiter_keys_are_independent() -> None:
+    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)
+    limiter.check("one")
+    limiter.check("two")
+    with pytest.raises(RateLimitError):
+        limiter.check("one")
diff --git a/deploy/evidence/hardening-20260731.md b/deploy/evidence/hardening-20260731.md
new file mode 100644
index 0000000..722a032
--- /dev/null
+++ b/deploy/evidence/hardening-20260731.md
@@ -0,0 +1,11 @@
+# Hardening — 2026-07-31
+
+## Priority execution
+1. GitHub push — **BLOCKED** (no PAT / `gh auth` on VPS); local branch ahead of origin.
+2. SSH — UFW `22/tcp` changed from `ALLOW` to **`LIMIT`** (rate-limit new connections).
+3. Login — backend fixed-window limiter: **10 attempts / 60s / client IP** on `POST /api/v1/auth/login` → HTTP **429** `RATE_LIMITED`.
+
+## Verification
+- Live: 10× bad login → 11th returns 429 with `retryAfterSeconds`.
+- Unit: `tests/test_rate_limit.py` PASS.
+- Legitimate login after backend restart (clears in-memory counters): PASS.
```

#### `96f52eb` — full show (no renames detected; secret-like values redacted)

```
commit 96f52eb21b1a2a68b0341e058ce17cd8545c7bf1
Author: root <root@srv1869401.hstgr.cloud>
Date:   Fri Jul 31 07:52:32 2026 +0000

    Add HTTPS edge cutover for pengaduan.layanankami.tech.

    Introduce Caddy prod overlay, deploy runbook/backup script, DEC-020 auth phasing (local JWT now, SSO later), and smoke UAT notes so the VPS shared URL can run without Mode B SSO.

    Co-authored-by: Cursor <cursoragent@cursor.com>

diff --git a/.env.prod.example b/.env.prod.example
new file mode 100644
index 0000000..356b517
--- /dev/null
+++ b/.env.prod.example
@@ -0,0 +1,36 @@
+# Copy to .env.prod (git-ignored) before cutover:
+#   cp .env.prod.example .env.prod
+#
+# Prerequisite: DNS A record
+#   pengaduan.layanankami.tech → <VPS public IPv4>
+# Verify: dig +short pengaduan.layanankami.tech A
+
+ENVIRONMENT=production
+APP_VERSION=1.0.0
+LOG_LEVEL=INFO
+DEBUG=false
+
+ECMP_DOMAIN=pengaduan.layanankami.tech
+CADDY_ACME_EMAIL=admin@layanankami.tech
+
+POSTGRES_USER=ecmp
+POSTGRES_PASSWORD=[REDACTED]
+POSTGRES_DB=ecmp
+POSTGRES_HOST=localhost
+POSTGRES_PORT=5433
+
+BACKEND_PORT=8000
+FRONTEND_PORT=3000
+
+# Same-origin API via Caddy (/api/* → backend)
+ALLOWED_ORIGINS=https://pengaduan.layanankami.tech
+ALLOWED_HOSTS=localhost,127.0.0.1,backend,pengaduan.layanankami.tech
+NEXT_PUBLIC_API_BASE_URL=https://pengaduan.layanankami.tech
+
+# REQUIRED: replace before shared use (openssl rand -hex 32)
+JWT_SECRET_KEY=[REDACTED]
+JWT_ALGORITHM=HS256
+JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
+JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
+
+# Auth phase (DEC-020): local JWT users now; SSO/OIDC later (not in this compose).
diff --git a/.gitignore b/.gitignore
index 25be2ec..1aad62c 100644
--- a/.gitignore
+++ b/.gitignore
@@ -48,6 +48,7 @@ backups/
 .env
 .env.*
 !.env.example
+!.env.prod.example

 # Local attachment blobs (TASK-029 LocalStorageProvider)
 backend/data/attachments/
diff --git a/27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md b/27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md
new file mode 100644
index 0000000..25421ae
--- /dev/null
+++ b/27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md
@@ -0,0 +1,55 @@
+# Decision Record — Lab auth: local JWT now, SSO later as target
+
+| Field | Value |
+|---|---|
+| ID | DEC-020 |
+| Version | 1.0 |
+| Owner | Product / Ops |
+| Reviewer | Solution Architect |
+| Approver | Business Owner |
+| Status | 🟢 Accepted (ops working agreement) |
+| Last Review | 2026-07-31 |
+| Next Review | 2026-10-31 |
+
+- Type: Project Decision (non-ADR)
+- Status: Accepted
+- Date: 2026-07-31
+- Context host: VPS lab → planned URL `https://pengaduan.layanankami.tech`
+
+## Context
+
+ECMP foundation lab runs on Docker Compose with **local JWT** users (no IdP).
+Stakeholders want a public subdomain later and mentioned SSO “as temporary login”.
+That phrasing conflicts with ADR-007 / ADR-012 (SSO/OIDC is the **target** auth path, not a stopgap).
+
+## Options
+
+- **A.** Build SSO/OIDC now alongside subdomain cutover.
+- **B.** Keep local JWT for lab and first HTTPS cutover; plan SSO/OIDC as a **later target** phase (not “temporary”).
+- **C.** Use SSO only as a short-lived temporary login, then replace again.
+
+## Decision
+
+**Opsi B.**
+
+1. **Now:** local username/password + JWT (seed/lab users in Postgres). Suitable for Mode A lab and initial `pengaduan.layanankami.tech` behind Caddy.
+2. **Later:** introduce SSO/OIDC per ADR-007 target / ADR-012 (e.g. Keycloak or corporate IdP) as the **intended** shared-environment login — not a temporary bridge.
+3. **Out of scope for current VPS cutover:** Mode B enterprise SSO coding, IdP procurement, and MFA product features.
+
+## Impact
+
+- Deploy edge: `deploy/Caddyfile` + `docker-compose.prod.yml` (no SSO services).
+- Lab credentials remain operational until an SSO migration runbook is accepted.
+- Any SSO work requires a separate decision/ADR activation — do not mix into Mode A compose without sign-off.
+
+## Related
+
+- ADR-007 Authentication Model
+- ADR-012 Target Authentication Architecture
+- `deploy/README.md` (subdomain cutover)
diff --git a/deploy/Caddyfile b/deploy/Caddyfile
new file mode 100644
index 0000000..6fd51be
--- /dev/null
+++ b/deploy/Caddyfile
@@ -0,0 +1,40 @@
+# ECMP edge — pengaduan.layanankami.tech
+# TLS via Let's Encrypt (needs DNS A → this VPS first).
+
+{
+	email {$CADDY_ACME_EMAIL}
+}
+
+{$ECMP_DOMAIN} {
+	encode gzip
+
+	# Backend API (FastAPI already serves /api/v1/...)
+	handle /api/* {
+		reverse_proxy backend:8000
+	}
+
+	# OpenAPI / health (optional ops access behind same host)
+	handle /health* {
+		reverse_proxy backend:8000
+	}
+	handle /docs* {
+		reverse_proxy backend:8000
+	}
+	handle /redoc* {
+		reverse_proxy backend:8000
+	}
+	handle /openapi.json {
+		reverse_proxy backend:8000
+	}
+
+	# Next.js frontend
+	handle {
+		reverse_proxy frontend:3000
+	}
+
+	header {
+		X-Content-Type-Options nosniff
+		Referrer-Policy strict-origin-when-cross-origin
+		-Server
+	}
+}
diff --git a/deploy/README.md b/deploy/README.md
new file mode 100644
index 0000000..9dc25ba
--- /dev/null
+++ b/deploy/README.md
@@ -0,0 +1,47 @@
+# ECMP edge deploy — `pengaduan.layanankami.tech`
+
+Lab Mode A (IP + ports 3000/8000) can keep running until DNS is ready.
+This folder adds **Caddy TLS reverse proxy** only — **no SSO**.
+
+## Auth (DEC-020)
+
+| Phase | Mechanism |
+|-------|-----------|
+| Now (lab / first shared URL) | Local JWT users (`admin` / password in DB) |
+| Later | SSO/OIDC as **target** login (not temporary stopgap) |
+
+## Cutover checklist
+
+1. **DNS** — create A record `pengaduan` → VPS IPv4 (`187.124.137.64`).
+2. **Wait** until `dig +short pengaduan.layanankami.tech A` returns that IP.
+3. **Env** — `cp .env.prod.example .env.prod` and set strong `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `CADDY_ACME_EMAIL`.
+4. **Bring up overlay**:
+   ```bash
+   cd /opt/ECMP
+   docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
+   ```
+5. **Verify** — `https://pengaduan.layanankami.tech/login` and `https://pengaduan.layanankami.tech/health`.
+6. Optional: firewall allow only 22/80/443; keep 3000/8000/5433 on localhost (prod overlay already binds them to `127.0.0.1`).
+
+## Rollback to lab-only
+
+```bash
+docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod stop caddy
+docker compose --env-file .env up -d
+```
+
+## Backup
+
+```bash
+/opt/ECMP/deploy/backup-postgres.sh
+```
+
+Dumps land in `backups/ecmp_*.sql.gz` (git-ignored). Cron example (02:15 UTC daily) is installed on the lab VPS; retain `ECMP_BACKUP_KEEP_DAYS` (default 14).
+
+## Host credentials
+
+On the VPS only (not in git): `/root/.ecmp-credentials` (mode 600) — admin + DB passwords after hardening.
+
+## Firewall
+
+UFW: allow `22`, `80`, `443` only. App ports stay on `127.0.0.1`.
diff --git a/deploy/SMOKE_UAT_2026-07-31.md b/deploy/SMOKE_UAT_2026-07-31.md
new file mode 100644
index 0000000..bd8d9d2
--- /dev/null
+++ b/deploy/SMOKE_UAT_2026-07-31.md
@@ -0,0 +1,19 @@
+# ECMP HTTPS smoke UAT — 2026-07-31 (VPS cutover)
+
+Target: `https://pengaduan.layanankami.tech`
+Environment: production compose + Caddy
+
+| Check | Result |
+|-------|--------|
+| GET `/health` | PASS — status ok, database up |
+| GET `/login` | PASS — 200 |
+| POST `/api/v1/auth/login` | PASS — access token issued |
+| GET `/api/v1/auth/me` | PASS — SUPER_ADMIN |
+| GET `/api/v1/dashboard/overview` | PASS — 200 |
+| GET `/api/v1/complaints` | PASS — empty list |
+| Pages `/dashboard` `/complaints` `/users` `/settings` | PASS — 200 |
+| Create complaint E2E | SKIP — no seed customers/branches/org yet |
+| Password rotation | PASS — old lab password rejected (401) |
+| TLS via Caddy | PASS — Let's Encrypt |
+
+Next product gap for fuller UAT: seed master data (organization, branch, customer) then create complaint.
diff --git a/deploy/backup-postgres.sh b/deploy/backup-postgres.sh
new file mode 100755
index 0000000..0ff6b26
--- /dev/null
+++ b/deploy/backup-postgres.sh
@@ -0,0 +1,24 @@
+#!/usr/bin/env bash
+# Daily Postgres dump for ECMP foundation stack.
+# Usage: /opt/ECMP/deploy/backup-postgres.sh
+set -euo pipefail
+
+ROOT="$(cd "$(dirname "$0")/.." && pwd)"
+BACKUP_DIR="${ECMP_BACKUP_DIR:-$ROOT/backups}"
+STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
+FILE="$BACKUP_DIR/ecmp_${STAMP}.sql.gz"
+KEEP_DAYS="${ECMP_BACKUP_KEEP_DAYS:-14}"
+
+mkdir -p "$BACKUP_DIR"
+chmod 700 "$BACKUP_DIR"
+
+cd "$ROOT"
+docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
+  exec -T postgres pg_dump -U ecmp -d ecmp --clean --if-exists \
+  | gzip -c >"$FILE"
+chmod 600 "$FILE"
+
+# prune old dumps
+find "$BACKUP_DIR" -type f -name 'ecmp_*.sql.gz' -mtime +"$KEEP_DAYS" -delete
+
+echo "backup_ok $FILE ($(du -h "$FILE" | awk '{print $1}'))"
diff --git a/docker-compose.prod.yml b/docker-compose.prod.yml
new file mode 100644
index 0000000..2bc8f4e
--- /dev/null
+++ b/docker-compose.prod.yml
@@ -0,0 +1,54 @@
+# Production / shared-host overlay for ECMP foundation stack.
+# Usage (after DNS A for $ECMP_DOMAIN points at this VPS):
+#   cp .env.prod.example .env.prod   # edit values
+#   docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
+#
+# Does NOT implement SSO/OIDC (see DEC-020). Local JWT login remains until SSO phase.
+
+services:
+  caddy:
+    image: caddy:2-alpine
+    container_name: ecmp-caddy
+    restart: unless-stopped
+    ports:
+      - "80:80"
+      - "443:443"
+      - "443:443/udp"
+    environment:
+      ECMP_DOMAIN: ${ECMP_DOMAIN:?set ECMP_DOMAIN}
+      CADDY_ACME_EMAIL: ${CADDY_ACME_EMAIL:?set CADDY_ACME_EMAIL}
+    volumes:
+      - ./deploy/Caddyfile:/etc/caddy/Caddyfile:ro
+      - caddy_data:/data
+      - caddy_config:/config
+    depends_on:
+      backend:
+        condition: service_healthy
+      frontend:
+        condition: service_healthy
+
+  # Bind app ports to localhost only — public traffic via Caddy :443
+  postgres:
+    ports: !override
+      - "127.0.0.1:${POSTGRES_PORT:-5433}:5432"
+
+  backend:
+    ports: !override
+      - "127.0.0.1:${BACKEND_PORT:-8000}:8000"
+    environment:
+      ENVIRONMENT: ${ENVIRONMENT:-production}
+      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
+      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
+
+  frontend:
+    ports: !override
+      - "127.0.0.1:${FRONTEND_PORT:-3000}:3000"
+    build:
+      context: ./frontend
+      dockerfile: Dockerfile
+      args:
+        NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL}
+
+volumes:
+  caddy_data:
+  caddy_config:
```

---

## 6. Potential Behavioral Overlap

Evidence-only signals (not conclusions):

| Signal | Commits | Shared surface |
|---|---|---|
| Auth / login path | `96f52eb`, `41a0f48` | Local JWT login story (DEC-020) + rate limit on `POST /api/v1/auth/login` |
| Users lifecycle | `2f1348a`, `a476ebf` | Backend IAM provisioning (`users` repository/service) + frontend Users admin UI / API client |
| Deploy ops docs | `96f52eb`, `2f1348a` | Same files evolved: `deploy/README.md`, `deploy/SMOKE_UAT_2026-07-31.md` |
| Backup / restore evidence chain | `96f52eb` (script), `a476ebf` (backup-verify), `ad4a373` (restore-drill) | Ops integrity narrative across three commits |
| Edge / X-Forwarded-For | `96f52eb` (Caddy), `41a0f48` (`client_ip_from_request`) | Client IP behind reverse proxy affects rate-limit keying |
| Divergence vs remote | local `ahead 5, behind 14` | Local `$B..HEAD` range does **not** include the 14 commits present on `origin/main` after merge-base; overlap with remote-only history is out of this evidence set |

Paths touched by ≥2 commits in `$B..HEAD` (file-level overlap):

- `deploy/README.md` — `96f52eb` (A), `2f1348a` (M)
- `deploy/SMOKE_UAT_2026-07-31.md` — `96f52eb` (A), `2f1348a` (M)

---

## 7. Files requiring manual review

| Path | Why flagged (evidence) |
|---|---|
| `.env.prod.example` | Contains `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` keys (values redacted in this report); sets `ENVIRONMENT=production` |
| `docker-compose.prod.yml` | Production overlay; sets `ENVIRONMENT` on backend; public ports 80/443 |
| `deploy/Caddyfile` | TLS edge + reverse proxy to backend/frontend; `/docs` and `/openapi.json` exposed on same host |
| `27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md` | Auth phasing decision (local JWT now / SSO later) |
| `backend/app/modules/auth/router.py` | Login behavior change (rate limiter check) |
| `backend/app/core/rate_limit.py` | New in-process limiter; IP derivation via `X-Forwarded-For` |
| `backend/app/modules/users/repository.py` | User/role provisioning + permission cache invalidation |
| `backend/app/modules/users/service.py` | Same IAM sync path as repository changes |
| `frontend/src/features/users/UsersManagement.tsx` | Large new admin UI for user create/list (377 lines) |
| `frontend/src/lib/api/users.ts` | Client API surface for users |
| `deploy/seed-lab-master-data.sql` | Lab master-data seed affecting complaint create/assign readiness |
| `deploy/backup-postgres.sh` | Execs into postgres with compose + `.env.prod`; dumps DB |
| `deploy/README.md` | References host credentials path `/root/.ecmp-credentials` (path only; file not in git) |

---

## Collection notes

- No repository mutation performed by this collector beyond writing this evidence file under `deploy/evidence/`.
- No checkout / merge / commit / rebase / stash / reset executed.
- `git status` at collection showed staged path `CLAUDE.md` outside `$B..HEAD` range (working-tree state only).
- Secret redaction applied to `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` values inside the `96f52eb` patch excerpt; filenames retained.

---

*End of Phase 0 Git Forensics evidence.*

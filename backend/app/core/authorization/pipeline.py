"""Authorization Middleware pipeline (TASK-040).

Unified flow for every RBAC-protected endpoint:

```text
Request
  → Authentication          (JWT Bearer → user_id + roles)
  → Permission Resolver     (TASK-038 IAM cache; skip if JWT has permissions claim)
  → Permission Check        (require_permissions / require_roles)
  → Org Unit Guard          (SECMIG-P4; opt-in G1 endpoints)
  → Data Scope Resolver     (TASK-039 IAM cache; optional / opt-in)
  → Data Scope Check        (require_data_scope; optional / opt-in)
  → Endpoint
```

Public helpers all share this pipeline. Endpoints that only call
``require_permissions(...)`` behave exactly as before.

This package does **not**:
- change Login/JWT issuance
- change PermissionResolver or DataScopeResolver internals
- auto-filter Complaint / Settings / Attachment / Notification / Audit data
- introduce a new cache or audit trail
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal

CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]

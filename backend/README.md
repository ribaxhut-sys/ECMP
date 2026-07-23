# ECMP Backend (Foundation)

FastAPI application for the Enterprise Complaint Management Platform.

**Version:** `1.0.0`

## Local (without Docker)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health: `GET http://localhost:8000/health`

## Structure

```text
app/
  api/                 # HTTP routers (health)
  core/                # config, logging, JWT, auth, errors, middleware
  db/                  # SQLAlchemy engine/session + mixins
  models/              # ORM models (ECMP v1.0 schema)
  modules/complaints/  # repository + service + schemas + router
  dependencies/        # DI foundation
alembic/               # migrations
```

## Complaint API (JWT)

| Method | Path | Permission / Role |
|--------|------|-------------------|
| POST | `/api/v1/auth/login` | public |
| POST | `/api/v1/auth/refresh` | refresh cookie |
| POST | `/api/v1/auth/logout` | refresh cookie |
| GET | `/api/v1/auth/me` | bearer |
| POST | `/api/v1/complaints` | `complaints:create` |
| GET | `/api/v1/complaints` | `complaints:read` |
| GET | `/api/v1/complaints/{id}` | `complaints:read` |
| PUT | `/api/v1/complaints/{id}` | `complaints:update` |
| POST | `/api/v1/complaints/{id}/assign` | `SUPERVISOR` + `complaints:assign` |
| GET | `/api/v1/complaints/{id}/assignments` | `complaints:read` |
| POST | `/api/v1/complaints/{id}/escalate` | `SUPERVISOR` + `complaints:escalate` |
| GET | `/api/v1/complaints/{id}/escalations` | `complaints:read` |

Auth: access JWT 15m; refresh token HttpOnly Secure SameSite=Lax cookie 7d with rotation.
Audit actions: `auth.login`, `auth.refresh`, `auth.logout`.

Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`

## Migrations

```bash
# inside backend container or local venv with DATABASE_URL pointing at Postgres
alembic upgrade head
alembic current
```

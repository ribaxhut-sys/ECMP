# ECMP Local Stack Foundation

Docker Compose stack for ECMP **v1.0.0**.

## Services

| Service  | URL                         |
|----------|-----------------------------|
| Frontend | http://localhost:3000       |
| Login    | http://localhost:3000/login |
| Backend  | http://localhost:8000       |
| Health   | http://localhost:8000/health|
| API docs | http://localhost:8000/docs (development only) |
| Postgres | localhost:5433              |
| pgAdmin  | http://localhost:5050 (`--profile tools`) |

> Host port **5433** avoids clashes with a local Postgres already bound to 5432. Inside the Compose network the DB remains `postgres:5432`.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Optional pgAdmin:

```bash
docker compose --profile tools up -d pgadmin
```

## Layout

```text
backend/     FastAPI + SQLAlchemy + Alembic
frontend/    Next.js (App Router) + Tailwind CSS
database/    Postgres init scripts
docs/        Knowledge portal + stack + release notes
```

## Release artifacts

- [Release notes v1.0.0](./releases/v1.0.0.md)
- [Deployment checklist](./deployment-checklist.md)
- [Rollback package](./releases/ROLLBACK_v1.0.0.md)
- [R6-03 Production configuration report](./releases/R6-03_PRODUCTION_CONFIGURATION_REPORT.md)
- [Production deployment guide](./deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Environment variable reference](./deployment/ENVIRONMENT_VARIABLE_REFERENCE.md)

Validate local/prod config:

```bash
python scripts/validate-production-config.py --env-file .env
```

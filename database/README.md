# Database

PostgreSQL bootstrap scripts mounted by Docker Compose into
`/docker-entrypoint-initdb.d` on first volume initialization.

Application schema is managed by Alembic in `backend/alembic/`.

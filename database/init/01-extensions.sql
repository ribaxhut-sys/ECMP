-- ECMP foundation database bootstrap
-- Extends default Postgres role/database created by POSTGRES_* env vars.
-- No business schema yet — Alembic owns application migrations.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

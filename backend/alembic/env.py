"""Alembic migration environment — wired to application settings."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure all models are registered on Base.metadata before autogenerate/upgrade.
from app import models  # noqa: E402, F401
from app.core.config import get_settings
from app.db.base import Base

# Pengumuman modul Pengaduan (landing page + management).
from app.modules.announcement import models as _announcement_orm  # noqa: E402, F401

# CM Batch 1 Aggregate persistence (S2 Task 01).
from app.modules.cm_batch1 import models as _cm_batch1_orm  # noqa: E402, F401

# CAP-008 Case Aggregate + inbox receipts.
from app.modules.cm_case.infrastructure import orm as _cm_case_orm  # noqa: E402, F401

# Complaint Domain Foundation ORM (CAPABILITY-004) — register for Alembic only.
from app.modules.complaint.infrastructure import orm as _complaint_orm  # noqa: E402, F401

# HQ arrival schedule holiday calendar.
from app.modules.hq_schedule import models as _hq_schedule_orm  # noqa: E402, F401

# Pengaduan Internal (domain terpisah dari F4 / Batch-1).
from app.modules.internal_complaint.infrastructure import (  # noqa: E402, F401
    orm as _internal_complaint_orm,
)

# Modul Pengetahuan (Knowledge Module).
from app.modules.knowledge import models as _knowledge_orm  # noqa: E402, F401

# Queue ORM lives under the Queue module (TASK-063) — register for Alembic only.
from app.modules.queue import orm as _queue_orm  # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

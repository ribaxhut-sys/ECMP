"""PermissionResolver unit + integration tests (TASK-038)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.rbac import permissions_for_role
from app.core.security import hash_password
from app.models import Role, User
from app.modules.iam.permission.models import Permission
from app.modules.iam.permission_cache import PermissionCache
from app.modules.iam.permission_resolver import PermissionResolver
from app.modules.iam.role_permission.models import RolePermission
from app.modules.iam.user_role.models import UserRole


def test_resolver_uses_cache() -> None:
    session = MagicMock()
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    cache.set(user_id, frozenset({"cached:perm"}))

    resolver = PermissionResolver(session, cache=cache)
    assert resolver.resolve(user_id) == frozenset({"cached:perm"})
    session.scalars.assert_not_called()


def test_resolver_invalidate() -> None:
    cache = PermissionCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    cache.set(user_id, frozenset({"x"}))
    resolver = PermissionResolver(MagicMock(), cache=cache)
    resolver.invalidate(user_id)
    assert cache.get(user_id) is None


def test_resolver_invalidate_all() -> None:
    cache = PermissionCache(ttl_seconds=300)
    cache.set(uuid.uuid4(), frozenset({"a"}))
    cache.set(uuid.uuid4(), frozenset({"b"}))
    resolver = PermissionResolver(MagicMock(), cache=cache)
    resolver.invalidate_all()
    assert len(cache) == 0


def test_legacy_seed_matrix_agent() -> None:
    """Historical matrix retained for migration seed parity (not runtime auth)."""
    perms = permissions_for_role("AGENT")
    assert "complaints:create" in perms
    assert "complaints:assign" not in perms


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


@pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for PermissionResolver integration tests",
)
class TestPermissionResolverIntegration:
    @pytest.fixture()
    def db_session(self) -> Generator[Session, None, None]:
        settings = get_settings()
        eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
        SessionLocal = sessionmaker(
            bind=eng, autoflush=False, autocommit=False, future=True
        )
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
            eng.dispose()

    def test_resolve_via_user_role_matrix(self, db_session: Session) -> None:
        exists = db_session.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'user_roles'"
            )
        ).scalar()
        if not exists:
            pytest.skip("user_roles table not migrated")

        agent = db_session.scalar(
            select(Role).where(Role.code == "AGENT", Role.deleted_at.is_(None))
        )
        if agent is None:
            pytest.skip("AGENT role missing")

        read = db_session.scalar(
            select(Permission).where(
                Permission.code == "complaints:read",
                Permission.deleted_at.is_(None),
            )
        )
        if read is None:
            pytest.skip("complaints:read not seeded (0025_permission_resolver)")

        user = User(
            username=f"resolver_{uuid.uuid4().hex[:8]}",
            email=f"resolver_{uuid.uuid4().hex[:8]}@example.com",
            full_name="Resolver Test",
            password_hash=hash_password("Secret123!"),
            role_id=agent.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(UserRole(user_id=user.id, role_id=agent.id))

        # Ensure AGENT has complaints:read (idempotent).
        if (
            db_session.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == agent.id,
                    RolePermission.permission_id == read.id,
                )
            )
            is None
        ):
            db_session.add(
                RolePermission(role_id=agent.id, permission_id=read.id)
            )
        db_session.commit()

        cache = PermissionCache(ttl_seconds=300)
        resolver = PermissionResolver(db_session, cache=cache)
        perms = resolver.resolve(user.id)
        assert "complaints:read" in perms

        # Second call hits cache (same frozenset identity from cache store).
        again = resolver.resolve(user.id)
        assert again == perms

        resolver.invalidate(user.id)
        assert cache.get(user.id) is None

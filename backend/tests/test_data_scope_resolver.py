"""Data Scope Resolver unit + integration tests (TASK-039)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.auth import Principal, require_data_scope, resolve_effective_scope
from app.core.config import get_settings
from app.core.errors import ForbiddenError
from app.core.security import hash_password
from app.models import Role, User
from app.modules.iam.data_scope.models import DataScope, ScopeType
from app.modules.iam.data_scope_resolver import DataScopeResolver, EffectiveScope
from app.modules.iam.permission_cache import (
    UserScopedTtlCache,
    reset_data_scope_cache_for_tests,
)
from app.modules.iam.user_role.models import UserRole


def test_effective_scope_helpers() -> None:
    scope = EffectiveScope(
        entries=frozenset(
            {
                (ScopeType.BRANCH.value, "b-1"),
                (ScopeType.ORGANIZATION.value, "org-9"),
                (ScopeType.CUSTOM.value, "region:west"),
            }
        )
    )
    assert not scope.has_global()
    assert scope.get_branches() == frozenset({"b-1"})
    assert scope.get_organizations() == frozenset({"org-9"})
    assert scope.get_custom_values() == frozenset({"region:west"})
    assert not scope.is_self_only()


def test_effective_scope_global_and_self() -> None:
    global_scope = EffectiveScope(entries=frozenset({(ScopeType.GLOBAL.value, None)}))
    assert global_scope.has_global()
    assert not global_scope.is_self_only()

    self_scope = EffectiveScope(entries=frozenset({(ScopeType.SELF.value, None)}))
    assert self_scope.is_self_only()
    assert not self_scope.has_global()


def test_resolver_uses_cache() -> None:
    session = MagicMock()
    cache: UserScopedTtlCache[object] = UserScopedTtlCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    cached = EffectiveScope(entries=frozenset({(ScopeType.GLOBAL.value, None)}))
    cache.set(user_id, cached)

    resolver = DataScopeResolver(session, cache=cache)
    assert resolver.resolve_scopes(user_id) is cached
    session.execute.assert_not_called()


def test_resolver_invalidate() -> None:
    cache: UserScopedTtlCache[object] = UserScopedTtlCache(ttl_seconds=300)
    user_id = uuid.uuid4()
    cache.set(user_id, EffectiveScope(entries=frozenset()))
    resolver = DataScopeResolver(MagicMock(), cache=cache)
    resolver.invalidate(user_id)
    assert cache.get(user_id) is None


def test_require_data_scope_forbidden_without_match() -> None:
    gate = require_data_scope("BRANCH")
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset(),
    )
    session = MagicMock()
    session.execute.return_value.all.return_value = []

    with pytest.raises(ForbiddenError):
        gate(principal=principal, session=session)


def test_require_data_scope_allows_global() -> None:
    gate = require_data_scope("BRANCH")
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset(),
    )
    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (ScopeType.GLOBAL.value, None)
    ]

    scope = gate(principal=principal, session=session)
    assert scope.has_global() is True


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
    reason="PostgreSQL not available for DataScopeResolver integration tests",
)
class TestDataScopeResolverIntegration:
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

    def _ensure_tables(self, db_session: Session) -> None:
        exists = db_session.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'data_scopes'"
            )
        ).scalar()
        if not exists:
            pytest.skip("data_scopes table not migrated")

    def _user_with_scopes(
        self,
        db_session: Session,
        *scopes: tuple[str, str | None],
    ) -> User:
        self._ensure_tables(db_session)
        role = Role(
            code=f"DS_{uuid.uuid4().hex[:8].upper()}",
            name="Data Scope Test Role",
            is_system=False,
            is_active=True,
        )
        db_session.add(role)
        db_session.flush()
        user = User(
            username=f"ds_{uuid.uuid4().hex[:8]}",
            email=f"ds_{uuid.uuid4().hex[:8]}@example.com",
            full_name="Data Scope Tester",
            password_hash=hash_password("Secret123!"),
            role_id=role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(UserRole(user_id=user.id, role_id=role.id))
        for scope_type, scope_value in scopes:
            db_session.add(
                DataScope(
                    role_id=role.id,
                    scope_type=scope_type,
                    scope_value=scope_value,
                )
            )
        db_session.commit()
        return user

    def test_global(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(db_session, (ScopeType.GLOBAL.value, None))
        resolver = DataScopeResolver(db_session)
        assert resolver.has_global_scope(user.id) is True
        assert resolver.get_branches(user.id) == frozenset()

    def test_organization(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(
            db_session, (ScopeType.ORGANIZATION.value, "org-42")
        )
        resolver = DataScopeResolver(db_session)
        assert resolver.get_organizations(user.id) == frozenset({"org-42"})
        assert resolver.has_global_scope(user.id) is False

    def test_branch(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(
            db_session,
            (ScopeType.BRANCH.value, "branch-a"),
            (ScopeType.BRANCH.value, "branch-b"),
        )
        resolver = DataScopeResolver(db_session)
        assert resolver.get_branches(user.id) == frozenset({"branch-a", "branch-b"})

    def test_self(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(db_session, (ScopeType.SELF.value, None))
        resolver = DataScopeResolver(db_session)
        assert resolver.is_self_only(user.id) is True

    def test_custom(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(
            db_session, (ScopeType.CUSTOM.value, "territory:north")
        )
        scope = resolve_effective_scope(user.id, db_session)
        assert scope.get_custom_values() == frozenset({"territory:north"})
        assert scope.has_type(ScopeType.CUSTOM)

    def test_cache_hit_and_invalidate(self, db_session: Session) -> None:
        reset_data_scope_cache_for_tests()
        user = self._user_with_scopes(db_session, (ScopeType.BRANCH.value, "b-9"))
        cache: UserScopedTtlCache[object] = UserScopedTtlCache(ttl_seconds=300)
        resolver = DataScopeResolver(db_session, cache=cache)
        first = resolver.resolve_scopes(user.id)
        assert "b-9" in first.get_branches()
        second = resolver.resolve_scopes(user.id)
        assert second is first
        resolver.invalidate(user.id)
        assert cache.get(user.id) is None

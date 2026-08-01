"""Configurable password policy (extensible for future complexity rules)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.core.errors import ValidationAppError
from app.core.security import verify_password
from app.core.user_messages import m


class PasswordRule(Protocol):
    """Single password constraint — add new rules without changing call sites."""

    def validate(self, password: str, *, current_hash: str | None = None) -> None: ...


@dataclass(frozen=True, slots=True)
class MinLengthRule:
    min_length: int

    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        _ = current_hash
        if len(password) < self.min_length:
            raise ValidationAppError(
                f"Kata sandi minimal {self.min_length} karakter",
                details={"field": "password", "minLength": self.min_length},
            )


@dataclass(frozen=True, slots=True)
class NotBlankRule:
    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        _ = current_hash
        if not password or not password.strip():
            raise ValidationAppError(
                m("auth.password_blank"),
                details={"field": "password"},
            )
        if password.strip() != password:
            raise ValidationAppError(
                m("auth.password_whitespace"),
                details={"field": "password"},
            )


@dataclass(frozen=True, slots=True)
class NotSameAsCurrentRule:
    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        if current_hash and verify_password(password, current_hash):
            raise ValidationAppError(
                m("auth.password_must_differ"),
                details={"field": "password"},
            )


@dataclass(frozen=True, slots=True)
class MaxLengthRule:
    max_length: int = 72  # bcrypt truncation boundary

    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        _ = current_hash
        if len(password) > self.max_length:
            raise ValidationAppError(
                f"Kata sandi maksimal {self.max_length} karakter",
                details={"field": "password", "maxLength": self.max_length},
            )


@dataclass(slots=True)
class PasswordPolicy:
    """Composable password policy. Default: blank / length / not-same-as-current."""

    min_length: int = 8
    rules: list[PasswordRule] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rules:
            self.rules = [
                NotBlankRule(),
                MinLengthRule(self.min_length),
                MaxLengthRule(),
                NotSameAsCurrentRule(),
            ]

    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        for rule in self.rules:
            rule.validate(password, current_hash=current_hash)


def get_password_policy(*, min_length: int) -> PasswordPolicy:
    return PasswordPolicy(min_length=min_length)

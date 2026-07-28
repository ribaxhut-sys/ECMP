"""Configurable password policy (extensible for future complexity rules)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.core.errors import ValidationAppError
from app.core.security import verify_password


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
                f"Password must be at least {self.min_length} characters",
                details={"field": "password", "minLength": self.min_length},
            )


@dataclass(frozen=True, slots=True)
class NotBlankRule:
    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        _ = current_hash
        if not password or not password.strip():
            raise ValidationAppError(
                "Password must not be blank",
                details={"field": "password"},
            )
        if password.strip() != password:
            raise ValidationAppError(
                "Password must not have leading or trailing whitespace",
                details={"field": "password"},
            )


@dataclass(frozen=True, slots=True)
class NotSameAsCurrentRule:
    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        if current_hash and verify_password(password, current_hash):
            raise ValidationAppError(
                "New password must be different from the current password",
                details={"field": "password"},
            )


@dataclass(frozen=True, slots=True)
class MaxLengthRule:
    max_length: int = 72  # bcrypt truncation boundary

    def validate(self, password: str, *, current_hash: str | None = None) -> None:
        _ = current_hash
        if len(password) > self.max_length:
            raise ValidationAppError(
                f"Password must be at most {self.max_length} characters",
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

"""User schema validation coverage (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from app.modules.users.schemas import UserCreateRequest, UserUpdateRequest


def test_user_create_validators_reject_bad_input() -> None:
    role_id = uuid.uuid4()
    base = {
        "username": "agent01",
        "email": "a@example.com",
        "fullName": "Agent One",
        "password": "Secret123",
        "roleId": str(role_id),
    }
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate({**base, "username": "  "})
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate({**base, "email": "not-an-email"})
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate({**base, "fullName": "   "})
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate({**base, "password": "  Secret123"})
    with pytest.raises(ValidationError):
        UserCreateRequest.model_validate({**base, "password": "        "})

    ok = UserCreateRequest.model_validate(
        {**base, "username": "  Agent01  ", "email": "  A@Example.COM "}
    )
    assert ok.username == "Agent01"
    assert ok.email == "a@example.com"


def test_user_update_validators_and_at_least_one_field() -> None:
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"username": "  "})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"email": "bad"})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"fullName": "  "})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"password": "  xxxxxxxx"})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"password": "        "})

    ok = UserUpdateRequest.model_validate({"username": "  newuser  "})
    assert ok.username == "newuser"
    assert UserUpdateRequest.model_validate({"email": None}).email is None

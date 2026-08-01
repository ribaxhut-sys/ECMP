"""Appointment API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import AppointmentCompletionResult
from app.core.user_messages import m

AppointmentStatusLiteral = Literal["BOOKED", "CHECKED_IN", "COMPLETED", "NO_SHOW"]
CompletionResultLiteral = Literal["COMPLETED", "PARTIALLY_COMPLETED"]


def _parse_hhmm(value: str) -> time:
    cleaned = value.strip()
    try:
        hour_s, minute_s = cleaned.split(":", 1)
        hour = int(hour_s)
        minute = int(minute_s[:2])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        return time(hour=hour, minute=minute)
    except (TypeError, ValueError):
        raise ValueError(m("validation.time_hhmm")) from None


class AppointmentCreate(BaseModel):
    """API-305 — book appointment on APPROVED escalation."""

    model_config = ConfigDict(populate_by_name=True)

    appointment_date: date = Field(alias="appointmentDate")
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    assigned_engineer_id: uuid.UUID = Field(alias="assignedEngineerId")
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def coerce_time(cls, value: object) -> object:
        if isinstance(value, str):
            return _parse_hhmm(value)
        return value

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def end_after_start(self) -> AppointmentCreate:
        if self.end_time <= self.start_time:
            raise ValueError(m("validation.end_after_start"))
        return self


class AppointmentCheckInRequest(BaseModel):
    """API-307 — customer check-in body."""

    model_config = ConfigDict(populate_by_name=True)

    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AppointmentCompleteRequest(BaseModel):
    """API-308 — appointment completion body."""

    model_config = ConfigDict(populate_by_name=True)

    result: CompletionResultLiteral = Field(default="COMPLETED")
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("result")
    @classmethod
    def validate_result(
        cls, value: CompletionResultLiteral
    ) -> CompletionResultLiteral:
        _ = AppointmentCompletionResult(value)
        return value

    @field_validator("notes")
    @classmethod
    def strip_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AppointmentNoShowRequest(BaseModel):
    """API-309 — customer no-show body."""

    model_config = ConfigDict(populate_by_name=True)

    reason: str | None = Field(default=None, max_length=5000)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class AppointmentSummary(BaseModel):
    """Slim appointment projection embedded on Escalation (API-302)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    status: str
    appointment_date: date = Field(alias="appointmentDate")
    appointment_start_time: time = Field(alias="appointmentStartTime")
    appointment_end_time: time = Field(alias="appointmentEndTime")
    assigned_engineer_id: uuid.UUID = Field(alias="assignedEngineerId")


class AppointmentBookResult(BaseModel):
    """API-305 slim create response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    status: Literal["BOOKED"]


class AppointmentCheckInResult(BaseModel):
    """API-307 slim check-in response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    status: Literal["CHECKED_IN"]
    checked_in_at: datetime = Field(alias="checkedInAt")
    checked_in_by: uuid.UUID = Field(alias="checkedInBy")


class AppointmentCompleteResult(BaseModel):
    """API-308 slim complete response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    status: Literal["COMPLETED"]
    completion_result: CompletionResultLiteral = Field(alias="completionResult")
    completed_at: datetime = Field(alias="completedAt")
    completed_by: uuid.UUID = Field(alias="completedBy")


class AppointmentNoShowResult(BaseModel):
    """API-309 slim no-show response."""

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    status: Literal["NO_SHOW"]
    no_show_at: datetime = Field(alias="noShowAt")
    no_show_by: uuid.UUID = Field(alias="noShowBy")


class AppointmentResponse(BaseModel):
    """API-306 full appointment detail."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    escalation_id: uuid.UUID = Field(alias="escalationId")
    appointment_date: date = Field(alias="appointmentDate")
    appointment_start_time: time = Field(alias="appointmentStartTime")
    appointment_end_time: time = Field(alias="appointmentEndTime")
    status: str
    assigned_engineer_id: uuid.UUID = Field(alias="assignedEngineerId")
    assigned_engineer_name: str | None = Field(
        default=None, alias="assignedEngineerName"
    )
    notes: str | None = None
    checked_in_at: datetime | None = Field(default=None, alias="checkedInAt")
    checked_in_by: uuid.UUID | None = Field(default=None, alias="checkedInBy")
    checkin_notes: str | None = Field(default=None, alias="checkinNotes")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    completed_by: uuid.UUID | None = Field(default=None, alias="completedBy")
    completion_notes: str | None = Field(default=None, alias="completionNotes")
    completion_result: str | None = Field(default=None, alias="completionResult")
    no_show_at: datetime | None = Field(default=None, alias="noShowAt")
    no_show_by: uuid.UUID | None = Field(default=None, alias="noShowBy")
    no_show_reason: str | None = Field(default=None, alias="noShowReason")
    created_by: uuid.UUID | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

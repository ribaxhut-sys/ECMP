"""Appointment API contracts (camelCase)."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AppointmentStatusLiteral = Literal["BOOKED"]


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
        raise ValueError("must be HH:MM") from None


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
            raise ValueError("endTime must be after startTime")
        return self


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
    status: AppointmentStatusLiteral


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
    created_by: uuid.UUID | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

"""HQ arrival schedule API contracts (camelCase)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ClosedReasonLiteral = Literal["WEEKEND", "HOLIDAY"]


class HolidayCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    holiday_date: date = Field(alias="holidayDate")
    label: str = Field(min_length=1, max_length=200)


class HolidayResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    holiday_date: date = Field(alias="holidayDate")
    label: str
    created_by: str | None = Field(default=None, alias="createdBy")
    created_at: datetime = Field(alias="createdAt")


class ProposalSummary(BaseModel):
    """One scheduled or branch-proposed slot occupant (Pusat detail view only)."""

    model_config = ConfigDict(populate_by_name=True)

    complaint_id: str = Field(alias="complaintId")
    complaint_number: str = Field(alias="complaintNumber")
    owning_unit_id: str | None = Field(default=None, alias="owningUnitId")
    unit_code: str = Field(alias="unitCode")
    # Case(s) tracking this complaint's escalation — scheduled cases only.
    case_numbers: list[str] = Field(default_factory=list, alias="caseNumbers")
    proposed_by: str | None = Field(default=None, alias="proposedBy")
    proposed_at: datetime | None = Field(default=None, alias="proposedAt")
    completed: bool = Field(
        default=False,
        description="HQ visit completed (HQ_CLOSED) — listed that day, does not consume capacity",
    )


class SlotAvailability(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: str = Field(alias="startTime")
    end_time: str = Field(alias="endTime")
    capacity: int
    is_break: bool = Field(default=False, alias="isBreak")
    scheduled_count: int = Field(alias="scheduledCount")
    proposed_count: int = Field(alias="proposedCount")
    available_count: int = Field(alias="availableCount")
    # Pusat detail only — empty for the branch-facing aggregate view.
    pending_proposals: list[ProposalSummary] = Field(
        default_factory=list, alias="pendingProposals"
    )
    scheduled_cases: list[ProposalSummary] = Field(
        default_factory=list, alias="scheduledCases"
    )


class DayAvailability(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: date
    weekday: int = Field(description="ISO weekday, 1=Mon..7=Sun")
    closed: bool
    closed_reason: ClosedReasonLiteral | None = Field(
        default=None, alias="closedReason"
    )
    holiday_label: str | None = Field(default=None, alias="holidayLabel")
    slots: list[SlotAvailability] = Field(default_factory=list)


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_time: str = Field(alias="startTime")
    end_time: str = Field(alias="endTime")
    slot_minutes: int = Field(alias="slotMinutes")
    capacity_per_slot: int = Field(alias="capacityPerSlot")
    days: list[DayAvailability] = Field(default_factory=list)

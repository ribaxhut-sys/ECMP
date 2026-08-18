"""Report API contracts (camelCase, aligned with OpenAPI)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AggregateComplaintStatus(StrEnum):
    """CM Aggregate lifecycle on report wires (DEC-025 §3.3)."""

    REGISTERED = "REGISTERED"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class ReportFilters(BaseModel):
    """Optional shared report filters (query params)."""

    model_config = ConfigDict(populate_by_name=True)

    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    date_from: datetime | None = Field(default=None, alias="dateFrom")
    date_to: datetime | None = Field(default=None, alias="dateTo")


class StatusCount(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: AggregateComplaintStatus
    count: int = Field(ge=0)


class BranchCount(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    branch_id: uuid.UUID | None = Field(default=None, alias="branchId")
    branch_code: str | None = Field(default=None, alias="branchCode")
    branch_name: str | None = Field(default=None, alias="branchName")
    unit_code: str | None = Field(default=None, alias="unitCode")
    total: int = Field(ge=0)
    open: int = Field(default=0, ge=0)
    closed: int = Field(default=0, ge=0)
    escalated: int = Field(default=0, ge=0)
    case_total: int = Field(default=0, ge=0, alias="caseTotal")
    case_open: int = Field(default=0, ge=0, alias="caseOpen")
    case_closed: int = Field(default=0, ge=0, alias="caseClosed")


class CycleTimeBucket(BaseModel):
    """Share of closed cases per age band (labels resolved by the UI)."""

    model_config = ConfigDict(populate_by_name=True)

    key: str
    count: int = Field(default=0, ge=0)


class CycleTimeData(BaseModel):
    """How long closed cases took, in days (RES-CM cycle time)."""

    model_config = ConfigDict(populate_by_name=True)

    closed_cases: int = Field(default=0, ge=0, alias="closedCases")
    average_days: float | None = Field(default=None, alias="averageDays")
    median_days: float | None = Field(default=None, alias="medianDays")
    p90_days: float | None = Field(default=None, alias="p90Days")
    fastest_days: float | None = Field(default=None, alias="fastestDays")
    slowest_days: float | None = Field(default=None, alias="slowestDays")
    buckets: list[CycleTimeBucket] = Field(default_factory=list)


class ReportSummaryData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(ge=0)
    by_status: list[StatusCount] = Field(alias="byStatus")

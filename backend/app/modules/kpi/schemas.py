"""KPI Foundation contracts (API-318 / TASK-026). Read-only aggregates."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ComplaintKpiCounts(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = 0
    open: int = Field(default=0, alias="open")
    closed: int = 0


class SlaStageKpiCounts(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    completed: int = 0
    breached: int = 0


class KpiSummaryResponse(BaseModel):
    """Live KPI summary — never persisted."""

    model_config = ConfigDict(populate_by_name=True)

    complaints: ComplaintKpiCounts
    assignment: SlaStageKpiCounts
    appointment: SlaStageKpiCounts
    resolution: SlaStageKpiCounts
    escalation: SlaStageKpiCounts
    overall: SlaStageKpiCounts

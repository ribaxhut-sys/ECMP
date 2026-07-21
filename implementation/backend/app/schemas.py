"""API contracts (camelCase) aligned to 07 API Catalog/openapi/case-service.v1.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CaseType = Literal["COMPLAINT", "INQUIRY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
# Sprint-01 contract exposes initial status only (OpenAPI CaseStatus enum).
CaseStatus = Literal["REGISTERED"]


class CaseCreateRequest(BaseModel):
    customerId: str = Field(min_length=1, max_length=64)
    caseType: CaseType
    priority: Priority
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    # max_length matches the VARCHAR(32) column — validation and storage must agree.
    channel: str | None = Field(default=None, max_length=32)


class Case(BaseModel):
    caseId: str
    customerId: str
    caseType: CaseType
    priority: Priority
    subject: str
    description: str
    status: CaseStatus
    channel: str | None = None
    customerVerified: bool = False
    createdAt: datetime
    createdBy: str
    updatedAt: datetime


class Error(BaseModel):
    code: str
    message: str
    details: dict | None = None

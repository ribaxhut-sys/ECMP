"""Normalized Master Customer provider results (transport-agnostic)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CustomerLookupStatus(str, Enum):
    """Normalized outcomes — business code must not see HTTP/DB details."""

    FOUND = "found"
    NOT_FOUND = "not_found"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class MinimalCustomer:
    """Batch-1 minimal customer projection (read-only)."""

    customer_id: str
    customer_number: str
    identity_number: str
    reference_number: str
    display_name: str
    status: str = "ACTIVE"
    phone: str = ""
    email: str = ""


@dataclass(frozen=True)
class CustomerLookupResult:
    status: CustomerLookupStatus
    customer: MinimalCustomer | None = None
    candidates: tuple[MinimalCustomer, ...] = ()


@dataclass(frozen=True)
class CustomerExistsResult:
    status: CustomerLookupStatus
    exists: bool = False

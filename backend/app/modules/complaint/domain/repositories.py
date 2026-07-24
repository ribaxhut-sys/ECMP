"""Complaint + Assignment + Escalation + SLA repository ports (CAPABILITY-004…008).

Domain-facing contracts. Implementations live under ``infrastructure/repositories/``.
No SQLAlchemy. No Queue imports. Returns domain models only.
No business rules — persistence CRUD only.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.modules.complaint.domain.models import (
    Assignment,
    Complaint,
    ComplaintSLA,
    Escalation,
    SLAPolicy,
)


class ComplaintRepository(ABC):
    """Persistence port for the Complaint aggregate root."""

    @abstractmethod
    async def add(self, complaint: Complaint) -> Complaint:
        """Insert a new complaint. Returns the persisted domain model."""

    @abstractmethod
    async def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        """Load a complaint by identity, or None if missing."""

    @abstractmethod
    async def update(self, complaint: Complaint) -> Complaint:
        """Replace an existing complaint snapshot. Returns the persisted model."""

    @abstractmethod
    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        """List complaints for an organization (created_at ASC, complaint_id ASC)."""

    @abstractmethod
    async def list_by_queue_ticket(
        self, queue_ticket_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        """List complaints linked to a visit-context ticket id."""

    @abstractmethod
    async def delete(self, complaint_id: uuid.UUID) -> bool:
        """Hard-delete a complaint. Returns True when a row was removed."""


class AssignmentRepository(ABC):
    """Persistence port for Assignment child entities (append-only history)."""

    @abstractmethod
    async def add(self, assignment: Assignment) -> Assignment:
        """Insert a new assignment row. Returns the persisted domain model."""

    @abstractmethod
    async def update(self, assignment: Assignment) -> Assignment:
        """Persist release fields on an existing assignment (is_active / released_*)."""

    @abstractmethod
    async def get_by_id(self, assignment_id: uuid.UUID) -> Assignment | None:
        """Load an assignment by identity, or None if missing."""

    @abstractmethod
    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Assignment | None:
        """Return the single active assignment for a complaint, if any."""

    @abstractmethod
    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Assignment, ...]:
        """Assignment history for a complaint (assigned_at ASC, assignment_id ASC)."""


class EscalationRepository(ABC):
    """Persistence port for Escalation child entities (append-only history)."""

    @abstractmethod
    async def add(self, escalation: Escalation) -> Escalation:
        """Insert a new escalation row. Returns the persisted domain model."""

    @abstractmethod
    async def update(self, escalation: Escalation) -> Escalation:
        """Persist release fields on an existing escalation (is_current / released_at)."""

    @abstractmethod
    async def get_by_id(self, escalation_id: uuid.UUID) -> Escalation | None:
        """Load an escalation by identity, or None if missing."""

    @abstractmethod
    async def get_current_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Escalation | None:
        """Return the single current escalation for a complaint, if any."""

    @abstractmethod
    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Escalation, ...]:
        """Escalation history for a complaint (escalated_at ASC, escalation_id ASC)."""


class SLAPolicyRepository(ABC):
    """Persistence port for SLAPolicy entities (CAPABILITY-008)."""

    @abstractmethod
    async def get_by_id(self, policy_id: uuid.UUID) -> SLAPolicy | None:
        """Load a policy by identity, or None if missing."""

    @abstractmethod
    async def get_default(self) -> SLAPolicy | None:
        """Return the default SLA policy, if configured."""

    @abstractmethod
    async def add(self, policy: SLAPolicy) -> SLAPolicy:
        """Insert a new policy. Returns the persisted domain model."""


class ComplaintSlaRepository(ABC):
    """Persistence port for ComplaintSLA child entities (CAPABILITY-008)."""

    @abstractmethod
    async def add(self, sla: ComplaintSLA) -> ComplaintSLA:
        """Insert a new SLA row. Returns the persisted domain model."""

    @abstractmethod
    async def update(self, sla: ComplaintSLA) -> ComplaintSLA:
        """Persist completion / breach fields on an existing SLA."""

    @abstractmethod
    async def get_by_id(self, sla_id: uuid.UUID) -> ComplaintSLA | None:
        """Load an SLA by identity, or None if missing."""

    @abstractmethod
    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        """Return the single active SLA for a complaint, if any."""

    @abstractmethod
    async def get_latest_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        """Return the most recent SLA for a complaint (active preferred)."""


__all__ = [
    "AssignmentRepository",
    "ComplaintRepository",
    "ComplaintSlaRepository",
    "EscalationRepository",
    "SLAPolicyRepository",
]

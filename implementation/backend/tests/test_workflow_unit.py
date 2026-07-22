"""Domain workflow unit tests — pure, no DB/HTTP."""

from __future__ import annotations

from app.domain import workflow


def test_baseline_subset_excludes_reopen():
    assert not workflow.is_allowed_transition("CLOSED", "REOPENED")
    assert workflow.is_allowed_transition("REGISTERED", "ASSIGNED")
    assert workflow.is_allowed_transition("PENDING_REVIEW", "CLOSED")


def test_assignable_statuses():
    assert workflow.assignable_statuses() == frozenset({"REGISTERED", "REOPENED"})


def test_requires_resolution_and_reason():
    assert workflow.requires_resolution_code("CLOSED")
    assert not workflow.requires_resolution_code("IN_PROGRESS")
    assert workflow.requires_reason("CLOSED", "REOPENED", is_admin_override=False)
    assert workflow.requires_reason("ASSIGNED", "IN_PROGRESS", is_admin_override=True)
    assert not workflow.requires_reason("ASSIGNED", "IN_PROGRESS", is_admin_override=False)

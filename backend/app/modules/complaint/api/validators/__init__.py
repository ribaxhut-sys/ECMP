"""Shared request field validators (CAPABILITY-004)."""

from __future__ import annotations


def strip_required(value: str, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be blank")
    return cleaned


def strip_optional(value: str) -> str:
    return (value or "").strip()


__all__ = ["strip_optional", "strip_required"]

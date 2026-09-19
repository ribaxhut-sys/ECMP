"""DEC-027 — display names for Mode A personas (codes unchanged).

Revision ID: 0091_role_display_names_dec027
Revises: 0090_resend_note_presets
Create Date: 2026-08-20

Updates ``roles.name`` / ``description`` only. Role codes stay AGENT,
SUPERVISOR, MANAGER, VIEWER, ADMIN and aliases. SUPERVISOR is not deleted.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0091_role_display_names_dec027"
down_revision: Union[str, None] = "0090_resend_note_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# code → (name, description)
_DISPLAY: dict[str, tuple[str, str]] = {
    "AGENT": (
        "CRO",
        "Customer Relationship Officer — front-line complaint intake and handling",
    ),
    "CS_AGENT": ("CRO", "Alias of AGENT (CRO)"),
    "HANDLER": ("CRO", "Alias of AGENT (CRO)"),
    "BRANCH_OFFICER": ("CRO", "Alias of AGENT (CRO)"),
    "SUPERVISOR": (
        "Staff KaSatPel",
        "Staff of Kepala Satuan Pelaksana — unit assign, escalate, approve",
    ),
    "BRANCH_SUPERVISOR": ("Staff KaSatPel", "Alias of SUPERVISOR (Staff KaSatPel)"),
    "MANAGER": (
        "KaSatPel",
        "Kepala Satuan Pelaksana — unit head (BC-8.4); not a SUPERVISOR alias",
    ),
    "VIEWER": ("Viewer", "Read-only viewer — all units, no domain mutations"),
    "ADMIN": ("Admin", "Module administrator"),
    "ADMINISTRATOR": ("Admin", "Alias of ADMIN"),
}

_DOWN: dict[str, tuple[str, str]] = {
    "AGENT": ("Agent", "Front-line complaint agent"),
    "CS_AGENT": ("CS Agent", "Alias of Agent"),
    "HANDLER": ("Handler", "Alias of Agent"),
    "BRANCH_OFFICER": ("Branch Officer", "Alias of Agent"),
    "SUPERVISOR": ("Supervisor", "Branch / operations supervisor"),
    "BRANCH_SUPERVISOR": ("Branch Supervisor", "Alias of Supervisor"),
    "MANAGER": (
        "Manager",
        "Branch manager persona (BC-8.4) — manages own-branch user membership",
    ),
    "VIEWER": ("Viewer", "Read-only viewer"),
    "ADMIN": ("Administrator", "System administrator"),
    "ADMINISTRATOR": ("Administrator alias", "Alias of Admin"),
}


def upgrade() -> None:
    conn = op.get_bind()
    for code, (name, description) in _DISPLAY.items():
        conn.execute(
            sa.text(
                """
                UPDATE roles
                SET name = :name,
                    description = :description,
                    updated_at = now()
                WHERE code = :code
                  AND deleted_at IS NULL
                """
            ),
            {"code": code, "name": name, "description": description},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code, (name, description) in _DOWN.items():
        conn.execute(
            sa.text(
                """
                UPDATE roles
                SET name = :name,
                    description = :description,
                    updated_at = now()
                WHERE code = :code
                  AND deleted_at IS NULL
                """
            ),
            {"code": code, "name": name, "description": description},
        )

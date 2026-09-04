"""Shorten Case Number sequence from 6 digits to 4 (CASE-YYYY-NNNN).

Revision ID: 0095_case_number_four_digits
Revises: 0094_cm_batch1_presets
Create Date: 2026-08-22

BQ-004 padding change (Product Owner): ``CASE-2026-000002`` → ``CASE-2026-0002``.
Rewrites stored case numbers and matching timeline/audit JSON so existing
rows stay findable after the value-object canonical form changes.
"""

from __future__ import annotations

import json
import re
from typing import Any, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0095_case_number_four_digits"
down_revision: Union[str, None] = "0094_cm_batch1_presets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LEGACY = re.compile(r"^CASE-(\d{4})-(\d{6})$")
_CANON = re.compile(r"^CASE-(\d{4})-(\d{4})$")
_EMBEDDED_LEGACY = re.compile(r"CASE-\d{4}-\d{6}")
_EMBEDDED_CANON = re.compile(r"CASE-\d{4}-\d{4}(?!\d)")


def _to_four(value: str) -> str | None:
    match = _LEGACY.fullmatch(value)
    if not match:
        return None
    seq = int(match.group(2))
    if seq < 1 or seq > 9999:
        return None
    return f"CASE-{match.group(1)}-{seq:04d}"


def _to_six(value: str) -> str | None:
    match = _CANON.fullmatch(value)
    if not match:
        return None
    seq = int(match.group(2))
    return f"CASE-{match.group(1)}-{seq:06d}"


def _rewrite_json(obj: Any, convert) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, val in obj.items():
            if key == "caseNumber" and isinstance(val, str):
                nxt = convert(val)
                out[key] = nxt if nxt else val
            else:
                out[key] = _rewrite_json(val, convert)
        return out
    if isinstance(obj, list):
        return [_rewrite_json(item, convert) for item in obj]
    if isinstance(obj, str):
        def repl(match: re.Match[str]) -> str:
            nxt = convert(match.group(0))
            return nxt or match.group(0)

        pattern = _EMBEDDED_LEGACY if convert is _to_four else _EMBEDDED_CANON
        return pattern.sub(repl, obj)
    return obj


def _load_json(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def _migrate_cases(conn, convert) -> None:
    rows = conn.execute(sa.text("SELECT id, case_number FROM cm_cases")).fetchall()
    for row in rows:
        nxt = convert(row.case_number)
        if nxt and nxt != row.case_number:
            conn.execute(
                sa.text("UPDATE cm_cases SET case_number = :n WHERE id = :i"),
                {"n": nxt, "i": row.id},
            )


def _migrate_json_table(conn, table: str, columns: tuple[str, ...], convert) -> None:
    col_sql = ", ".join(columns)
    rows = conn.execute(sa.text(f"SELECT id, {col_sql} FROM {table}")).fetchall()
    for row in rows:
        updates: dict[str, Any] = {}
        mapping = row._mapping
        for col in columns:
            current = _load_json(mapping[col])
            rewritten = _rewrite_json(current, convert)
            if rewritten != current:
                updates[col] = rewritten
        if not updates:
            continue
        assignments = ", ".join(f"{col} = CAST(:{col} AS jsonb)" for col in updates)
        params = {col: json.dumps(val) for col, val in updates.items()}
        params["i"] = row.id
        conn.execute(sa.text(f"UPDATE {table} SET {assignments} WHERE id = :i"), params)


def _migrate_timeline_description(conn, convert) -> None:
    rows = conn.execute(
        sa.text("SELECT id, description FROM timeline_entries WHERE description IS NOT NULL")
    ).fetchall()
    pattern = _EMBEDDED_LEGACY if convert is _to_four else _EMBEDDED_CANON
    for row in rows:
        if not row.description:
            continue

        def repl(match: re.Match[str]) -> str:
            nxt = convert(match.group(0))
            return nxt or match.group(0)

        nxt = pattern.sub(repl, row.description)
        if nxt != row.description:
            conn.execute(
                sa.text("UPDATE timeline_entries SET description = :n WHERE id = :i"),
                {"n": nxt, "i": row.id},
            )


def upgrade() -> None:
    conn = op.get_bind()
    _migrate_cases(conn, _to_four)
    _migrate_json_table(conn, "timeline_entries", ("metadata",), _to_four)
    _migrate_timeline_description(conn, _to_four)
    _migrate_json_table(
        conn, "audit_logs", ("old_values", "new_values", "metadata"), _to_four
    )


def downgrade() -> None:
    conn = op.get_bind()
    _migrate_cases(conn, _to_six)
    _migrate_json_table(conn, "timeline_entries", ("metadata",), _to_six)
    _migrate_timeline_description(conn, _to_six)
    _migrate_json_table(
        conn, "audit_logs", ("old_values", "new_values", "metadata"), _to_six
    )

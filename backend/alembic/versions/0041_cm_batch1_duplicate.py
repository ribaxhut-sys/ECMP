"""CM Batch 1 FR-003 duplicate decision / later-review tables (S2 Task 02).



Revision ID: 0041_cm_batch1_duplicate

Revises: 0040_cm_batch1_persistence

Create Date: 2026-07-29



Creates:

- cm_batch1_duplicate_decisions (API-506 history / BR-018 linkage)

- cm_batch1_later_review_items (FR-003 E1 degraded later-review)



Does NOT modify 0040_cm_batch1_persistence. No Case / Batch-2 columns.

"""



from __future__ import annotations



from typing import Sequence, Union



import sqlalchemy as sa

from alembic import op

from sqlalchemy.dialects import postgresql



revision: str = "0041_cm_batch1_duplicate"

down_revision: Union[str, None] = "0040_cm_batch1_persistence"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:

    op.create_table(

        "cm_batch1_duplicate_decisions",

        sa.Column(

            "id",

            postgresql.UUID(as_uuid=True),

            server_default=sa.text("gen_random_uuid()"),

            nullable=False,

        ),

        sa.Column("customer_id", sa.String(length=128), nullable=False),

        sa.Column("decision", sa.String(length=32), nullable=False),

        sa.Column(

            "surviving_complaint_id",

            postgresql.UUID(as_uuid=True),

            nullable=True,

        ),

        sa.Column(

            "source_complaint_id",

            postgresql.UUID(as_uuid=True),

            nullable=True,

        ),

        sa.Column("justification", sa.Text(), nullable=True),

        sa.Column("staging_token", sa.String(length=256), nullable=True),

        sa.Column(

            "warning",

            sa.Boolean(),

            server_default=sa.text("false"),

            nullable=False,

        ),

        sa.Column(

            "hard_block",

            sa.Boolean(),

            server_default=sa.text("false"),

            nullable=False,

        ),

        sa.Column("policy_version", sa.String(length=64), nullable=False),

        sa.Column("candidate_snapshot", sa.Text(), nullable=True),

        sa.Column("actor_id", sa.String(length=128), nullable=True),

        sa.Column("later_review_work_item_id", sa.String(length=128), nullable=True),

        sa.Column(

            "case_created",

            sa.Boolean(),

            server_default=sa.text("false"),

            nullable=False,

        ),

        sa.Column(

            "created_at",

            sa.DateTime(timezone=True),

            server_default=sa.text("now()"),

            nullable=False,

        ),

        sa.ForeignKeyConstraint(

            ["surviving_complaint_id"],

            ["cm_batch1_complaints.id"],

            name="fk_cm_batch1_dup_surviving",

            ondelete="SET NULL",

        ),

        sa.ForeignKeyConstraint(

            ["source_complaint_id"],

            ["cm_batch1_complaints.id"],

            name="fk_cm_batch1_dup_source",

            ondelete="SET NULL",

        ),

        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_duplicate_decisions"),

    )

    op.create_index(

        "ix_cm_batch1_dup_decisions_customer_id",

        "cm_batch1_duplicate_decisions",

        ["customer_id"],

    )

    op.create_index(

        "ix_cm_batch1_dup_decisions_surviving",

        "cm_batch1_duplicate_decisions",

        ["surviving_complaint_id"],

    )

    op.create_index(

        "ix_cm_batch1_dup_decisions_created_at",

        "cm_batch1_duplicate_decisions",

        ["created_at"],

    )



    op.create_table(

        "cm_batch1_later_review_items",

        sa.Column(

            "id",

            postgresql.UUID(as_uuid=True),

            server_default=sa.text("gen_random_uuid()"),

            nullable=False,

        ),

        sa.Column("work_item_id", sa.String(length=64), nullable=False),

        sa.Column("customer_id", sa.String(length=128), nullable=False),

        sa.Column("reason", sa.String(length=64), nullable=False),

        sa.Column("status", sa.String(length=32), nullable=False),

        sa.Column(

            "created_at",

            sa.DateTime(timezone=True),

            server_default=sa.text("now()"),

            nullable=False,

        ),

        sa.PrimaryKeyConstraint("id", name="pk_cm_batch1_later_review_items"),

        sa.UniqueConstraint(

            "work_item_id", name="uq_cm_batch1_later_review_work_item_id"

        ),

    )

    op.create_index(

        "ix_cm_batch1_later_review_customer_id",

        "cm_batch1_later_review_items",

        ["customer_id"],

    )

    op.create_index(

        "ix_cm_batch1_later_review_status",

        "cm_batch1_later_review_items",

        ["status"],

    )





def downgrade() -> None:

    op.drop_index(

        "ix_cm_batch1_later_review_status",

        table_name="cm_batch1_later_review_items",

    )

    op.drop_index(

        "ix_cm_batch1_later_review_customer_id",

        table_name="cm_batch1_later_review_items",

    )

    op.drop_table("cm_batch1_later_review_items")

    op.drop_index(

        "ix_cm_batch1_dup_decisions_created_at",

        table_name="cm_batch1_duplicate_decisions",

    )

    op.drop_index(

        "ix_cm_batch1_dup_decisions_surviving",

        table_name="cm_batch1_duplicate_decisions",

    )

    op.drop_index(

        "ix_cm_batch1_dup_decisions_customer_id",

        table_name="cm_batch1_duplicate_decisions",

    )

    op.drop_table("cm_batch1_duplicate_decisions")



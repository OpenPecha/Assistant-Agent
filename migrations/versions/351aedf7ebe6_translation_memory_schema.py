"""translation memory schema

Revision ID: 351aedf7ebe6
Revises: 8ef199eeb359
Create Date: 2026-04-01 10:37:30.969952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '351aedf7ebe6'
down_revision: Union[str, Sequence[str], None] = '8ef199eeb359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "translation_memory",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "assistant_id",
            sa.UUID(),
            sa.ForeignKey("assistant.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("target_text", sa.Text(), nullable=False),
        sa.Column("target_language", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.execute(
        """
        CREATE INDEX idx_translation_memory_source_trgm
        ON translation_memory
        USING gist (source_text gist_trgm_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_translation_memory_source_trgm")
    op.drop_table("translation_memory")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")

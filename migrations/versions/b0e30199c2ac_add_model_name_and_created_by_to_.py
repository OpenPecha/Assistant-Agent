"""add model_name and created_by to translation_memory

Revision ID: b0e30199c2ac
Revises: 351aedf7ebe6
Create Date: 2026-04-02 11:29:38.766793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0e30199c2ac'
down_revision: Union[str, Sequence[str], None] = '351aedf7ebe6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('translation_memory', sa.Column('model_name', sa.String(length=255), nullable=True))
    op.add_column('translation_memory', sa.Column('created_by', sa.String(length=255), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('translation_memory', 'created_by')
    op.drop_column('translation_memory', 'model_name')

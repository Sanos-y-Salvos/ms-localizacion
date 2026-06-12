"""add especie

Revision ID: 003
Revises: 002
Create Date: 2026-06-12

"""
from typing import Sequence, Union
from alembic import op

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE localizaciones ADD COLUMN IF NOT EXISTS especie VARCHAR(50)")


def downgrade() -> None:
    op.execute("ALTER TABLE localizaciones DROP COLUMN IF EXISTS especie")

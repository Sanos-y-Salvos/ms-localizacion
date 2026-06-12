"""add descripcion, codigo_chip, foto_url

Revision ID: 002
Revises: 001
Create Date: 2026-06-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE localizaciones ADD COLUMN IF NOT EXISTS descripcion TEXT")
    op.execute("ALTER TABLE localizaciones ADD COLUMN IF NOT EXISTS codigo_chip VARCHAR(100)")
    op.execute("ALTER TABLE localizaciones ADD COLUMN IF NOT EXISTS foto_url VARCHAR(500)")


def downgrade() -> None:
    op.execute("ALTER TABLE localizaciones DROP COLUMN IF EXISTS descripcion")
    op.execute("ALTER TABLE localizaciones DROP COLUMN IF EXISTS codigo_chip")
    op.execute("ALTER TABLE localizaciones DROP COLUMN IF EXISTS foto_url")

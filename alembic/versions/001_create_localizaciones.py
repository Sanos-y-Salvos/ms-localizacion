"""create localizaciones

Revision ID: 001
Revises: 
Create Date: 2026-06-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        'localizaciones',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('reporte_id', sa.String(36), nullable=False, index=True),
        sa.Column('tipo_reporte', sa.String(20), nullable=False),
        sa.Column('estado_reporte', sa.String(20), nullable=False, server_default='EN_BUSQUEDA'),
        sa.Column('nombre_mascota', sa.String(100), nullable=True),
        sa.Column('latitud', sa.Float, nullable=False),
        sa.Column('longitud', sa.Float, nullable=False),
        sa.Column('ubicacion', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('direccion_aproximada', sa.Text, nullable=True),
        sa.Column('descripcion', sa.Text, nullable=True),
        sa.Column('codigo_chip', sa.String(100), nullable=True),
        sa.Column('foto_url', sa.String(500), nullable=True),
        sa.Column('activo', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index('idx_localizaciones_reporte_id', 'localizaciones', ['reporte_id'])
    op.create_index('idx_localizaciones_activo_estado', 'localizaciones', ['activo', 'estado_reporte'])
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_localizaciones_ubicacion
        ON localizaciones USING GIST (ubicacion)
    """)
    op.execute("""
        CREATE OR REPLACE FUNCTION sync_ubicacion()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.ubicacion := ST_SetSRID(ST_MakePoint(NEW.longitud, NEW.latitud), 4326);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("""
        CREATE TRIGGER trg_sync_ubicacion
        BEFORE INSERT OR UPDATE OF latitud, longitud
        ON localizaciones
        FOR EACH ROW EXECUTE FUNCTION sync_ubicacion()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_sync_ubicacion ON localizaciones")
    op.execute("DROP FUNCTION IF EXISTS sync_ubicacion")
    op.drop_table('localizaciones')

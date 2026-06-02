-- ============================================================
-- ms-localizacion: 001_create_localizaciones.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS localizaciones (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporte_id           UUID        NOT NULL,
    tipo_reporte         VARCHAR(20) NOT NULL CHECK (tipo_reporte IN ('PERDIDA', 'ENCONTRADA')),
    estado_reporte       VARCHAR(20) NOT NULL DEFAULT 'EN_BUSQUEDA',
    nombre_mascota       VARCHAR(100),

    latitud              DOUBLE PRECISION NOT NULL,
    longitud             DOUBLE PRECISION NOT NULL,

    -- Columna geográfica PostGIS (SRID 4326 = WGS 84)
    ubicacion            GEOGRAPHY(POINT, 4326),

    direccion_aproximada TEXT,
    descripcion_lugar    TEXT,
    activo               BOOLEAN     NOT NULL DEFAULT TRUE,
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice espacial para ST_DWithin
CREATE INDEX IF NOT EXISTS idx_localizaciones_ubicacion
    ON localizaciones USING GIST (ubicacion);

CREATE INDEX IF NOT EXISTS idx_localizaciones_reporte_id
    ON localizaciones (reporte_id);

CREATE INDEX IF NOT EXISTS idx_localizaciones_activo_estado
    ON localizaciones (activo, estado_reporte);

-- Trigger: sincroniza ubicacion desde latitud/longitud
CREATE OR REPLACE FUNCTION sync_ubicacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ubicacion := ST_SetSRID(ST_MakePoint(NEW.longitud, NEW.latitud), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_ubicacion ON localizaciones;
CREATE TRIGGER trg_sync_ubicacion
    BEFORE INSERT OR UPDATE OF latitud, longitud
    ON localizaciones
    FOR EACH ROW EXECUTE FUNCTION sync_ubicacion();

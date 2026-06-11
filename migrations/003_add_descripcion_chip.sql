-- ms-localizacion: 003_add_descripcion_chip.sql
ALTER TABLE localizaciones
    ADD COLUMN IF NOT EXISTS descripcion TEXT;

-- Renombrar descripcion_lugar a descripcion si aun existe
-- (solo ejecutar si la columna descripcion_lugar existe)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'localizaciones' AND column_name = 'descripcion_lugar'
    ) THEN
        UPDATE localizaciones SET descripcion = descripcion_lugar WHERE descripcion IS NULL;
        ALTER TABLE localizaciones DROP COLUMN descripcion_lugar;
    END IF;
END $$;

ALTER TABLE localizaciones
    ADD COLUMN IF NOT EXISTS codigo_chip VARCHAR(100);

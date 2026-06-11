-- ============================================================
-- ms-localizacion: 002_add_foto_url.sql
-- Agrega columna foto_url a tabla existente
-- ============================================================
ALTER TABLE localizaciones
    ADD COLUMN IF NOT EXISTS foto_url VARCHAR(500);

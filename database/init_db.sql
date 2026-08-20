-- ============================================================
-- Horizonte Inventory - creacion del rol y de la base de datos
-- Ejecutar UNA sola vez, como usuario postgres:
--   sudo -u postgres psql -f database/init_db.sql
-- ============================================================

-- Usuario que utiliza la aplicacion (no es superusuario).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'horizonte_app') THEN
        CREATE ROLE horizonte_app LOGIN PASSWORD 'Horizonte2026';
    END IF;
END
$$;

-- Base de datos del proyecto.
SELECT 'CREATE DATABASE horizonte OWNER horizonte_app'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'horizonte')\gexec

-- ============================================================
-- Horizonte Inventory - estructura de la base de datos
-- Motor: PostgreSQL 14+
-- Ejecutar como usuario postgres:
--   sudo -u postgres psql -f database/schema.sql
-- ============================================================

-- Tabla principal exigida por el enunciado.
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id            SERIAL PRIMARY KEY,
    code          VARCHAR(30)     NOT NULL UNIQUE,
    name          VARCHAR(150)    NOT NULL,
    category      VARCHAR(60)     NOT NULL,
    price         NUMERIC(12, 2)  NOT NULL CHECK (price >= 0),
    quantity      INTEGER         NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    registered_at TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indices para los filtros de inventario (categoria / existencias).
CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_products_quantity ON products (quantity);

-- Permisos para el usuario de la aplicacion.
GRANT SELECT, INSERT, UPDATE, DELETE ON products TO horizonte_app;
GRANT USAGE, SELECT ON SEQUENCE products_id_seq TO horizonte_app;

"""
Capa de acceso a datos de Horizonte Inventory.

Toda la comunicacion con PostgreSQL pasa por este modulo. La aplicacion
(app.py) nunca escribe SQL directamente: asi la logica web queda separada
de la logica de persistencia.
"""

import os
import psycopg2
import psycopg2.extras


# ---------------------------------------------------------------------------
# Configuracion de la conexion (se lee de variables de entorno)
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "horizonte"),
    "user": os.getenv("DB_USER", "horizonte_app"),
    "password": os.getenv("DB_PASSWORD", "Horizonte2026"),
}


def get_connection():
    """Abre una conexion nueva a PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def check_connection():
    """Devuelve True si la base de datos responde. Usado por /health."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return True
    finally:
        conn.close()


def _query(sql, params=None, fetch="all"):
    """Ejecuta una consulta y devuelve los resultados como diccionarios."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            result = None
            if fetch == "all":
                result = [dict(row) for row in cur.fetchall()]
            elif fetch == "one":
                row = cur.fetchone()
                result = dict(row) if row else None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Consultas de inventario
# ---------------------------------------------------------------------------

BASE_SELECT = """
    SELECT id, code, name, category, price, quantity, registered_at
    FROM products
"""


def list_products(filtro="todos", categoria=None, busqueda=None):
    """
    Lista productos aplicando los filtros del requerimiento 6.B:
      todos       -> todo el catalogo
      disponibles -> quantity > 0
      agotados    -> quantity = 0
      categoria   -> filtrado por categoria exacta
    """
    sql = BASE_SELECT
    where = []
    params = []

    if filtro == "disponibles":
        where.append("quantity > 0")
    elif filtro == "agotados":
        where.append("quantity = 0")
    elif filtro == "categoria" and categoria:
        where.append("category = %s")
        params.append(categoria)

    if busqueda:
        where.append("(LOWER(name) LIKE %s OR LOWER(code) LIKE %s)")
        term = f"%{busqueda.lower()}%"
        params.extend([term, term])

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id ASC"

    return _query(sql, params)


def get_product(product_id):
    """Devuelve un producto por su ID, o None si no existe."""
    return _query(BASE_SELECT + " WHERE id = %s", (product_id,), fetch="one")


def get_product_by_code(code):
    """Devuelve un producto por su codigo, o None si no existe."""
    return _query(BASE_SELECT + " WHERE code = %s", (code,), fetch="one")


def list_categories():
    """Categorias existentes, para poblar los filtros y el formulario."""
    rows = _query("SELECT DISTINCT category FROM products ORDER BY category;")
    return [row["category"] for row in rows]


def get_stats():
    """Totales mostrados en el encabezado del inventario."""
    return _query(
        """
        SELECT
            COUNT(*)                                        AS total,
            COUNT(*) FILTER (WHERE quantity > 0)            AS disponibles,
            COUNT(*) FILTER (WHERE quantity = 0)            AS agotados,
            COALESCE(SUM(price * quantity), 0)              AS valor_inventario
        FROM products;
        """,
        fetch="one",
    )


# ---------------------------------------------------------------------------
# Operaciones CRUD
# ---------------------------------------------------------------------------

def create_product(code, name, category, price, quantity):
    """Inserta un producto y devuelve el registro creado."""
    return _query(
        """
        INSERT INTO products (code, name, category, price, quantity)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, code, name, category, price, quantity, registered_at;
        """,
        (code, name, category, price, quantity),
        fetch="one",
    )


def update_product(product_id, code, name, category, price, quantity):
    """Actualiza un producto existente y devuelve el registro actualizado."""
    return _query(
        """
        UPDATE products
        SET code = %s, name = %s, category = %s, price = %s, quantity = %s
        WHERE id = %s
        RETURNING id, code, name, category, price, quantity, registered_at;
        """,
        (code, name, category, price, quantity, product_id),
        fetch="one",
    )


def delete_product(product_id):
    """Elimina un producto y devuelve el registro eliminado (o None)."""
    return _query(
        "DELETE FROM products WHERE id = %s RETURNING id, code, name;",
        (product_id,),
        fetch="one",
    )

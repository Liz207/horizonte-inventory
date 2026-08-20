"""
Horizonte Inventory
Libreria Horizonte S.R.L. - Examen Integral ITI-522 (Computacion en la Nube)

Aplicacion web de inventario que corre completamente dentro de una maquina
virtual: Flask (servidor web) + PostgreSQL (persistencia) + archivo de logs.
No depende de ningun servicio externo.
"""

import logging
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from logging.handlers import RotatingFileHandler

from flask import (
    Flask, flash, jsonify, redirect, render_template, request, url_for
)

import db

# ---------------------------------------------------------------------------
# Rutas y configuracion general
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "application.log")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

os.makedirs(LOG_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging: mismo formato que pide el enunciado
#   2026-08-19 09:15:32 INFO Application started
# ---------------------------------------------------------------------------

formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

log = logging.getLogger("horizonte")
log.setLevel(logging.INFO)
log.addHandler(file_handler)
log.addHandler(console_handler)
log.propagate = False

# ---------------------------------------------------------------------------
# Aplicacion Flask
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "horizonte-inventory-local")


@app.template_filter("colones")
def colones(value):
    """Formatea un precio como moneda local: 12345.5 -> C 12 345,50"""
    try:
        value = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return value
    entero, decimales = f"{value:,.2f}".split(".")
    return "\u20a1 " + entero.replace(",", " ") + "," + decimales


@app.template_filter("fecha")
def fecha(value):
    """Fecha de registro legible."""
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    return value


@app.after_request
def registrar_solicitud(response):
    """Registra en el log toda solicitud recibida (requisito 8)."""
    if request.path.startswith("/static"):
        return response
    log.info(
        "Request %s %s -> %s (%s)",
        request.method, request.path, response.status_code,
        request.remote_addr,
    )
    return response


@app.errorhandler(404)
def no_encontrado(error):
    log.warning("Ruta no encontrada: %s", request.path)
    return render_template("error.html",
                           codigo=404,
                           mensaje="Esa pagina no existe en Horizonte Inventory."), 404


@app.errorhandler(500)
def error_interno(error):
    log.error("Error interno en %s: %s", request.path, error)
    return render_template("error.html",
                           codigo=500,
                           mensaje="La aplicacion no pudo completar la operacion."), 500


# ---------------------------------------------------------------------------
# Validacion de formularios
# ---------------------------------------------------------------------------

def leer_formulario(form):
    """
    Valida y normaliza los datos del formulario de producto.
    Devuelve (datos, errores).
    """
    datos = {
        "code": (form.get("code") or "").strip().upper(),
        "name": (form.get("name") or "").strip(),
        "category": (form.get("category") or "").strip(),
        "price": (form.get("price") or "").strip(),
        "quantity": (form.get("quantity") or "").strip(),
    }
    errores = []

    if not datos["code"]:
        errores.append("El codigo es obligatorio.")
    if not datos["name"]:
        errores.append("El nombre es obligatorio.")
    if not datos["category"]:
        errores.append("La categoria es obligatoria.")

    try:
        datos["price"] = Decimal(datos["price"])
        if datos["price"] < 0:
            errores.append("El precio no puede ser negativo.")
    except (InvalidOperation, TypeError):
        errores.append("El precio debe ser un numero.")

    try:
        datos["quantity"] = int(datos["quantity"])
        if datos["quantity"] < 0:
            errores.append("La cantidad no puede ser negativa.")
    except (ValueError, TypeError):
        errores.append("La cantidad debe ser un numero entero.")

    return datos, errores


# ---------------------------------------------------------------------------
# Interfaz web
# ---------------------------------------------------------------------------

@app.route("/")
def inventario():
    """Pagina principal: catalogo con los filtros de inventario."""
    filtro = request.args.get("filtro", "todos")
    categoria = request.args.get("categoria") or None
    busqueda = request.args.get("q") or None

    if categoria:
        filtro = "categoria"

    productos = db.list_products(filtro, categoria, busqueda)
    return render_template(
        "index.html",
        productos=productos,
        categorias=db.list_categories(),
        stats=db.get_stats(),
        filtro=filtro,
        categoria=categoria,
        busqueda=busqueda or "",
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    """Registrar producto."""
    if request.method == "POST":
        datos, errores = leer_formulario(request.form)

        if not errores and db.get_product_by_code(datos["code"]):
            errores.append(f"Ya existe un producto con el codigo {datos['code']}.")

        if errores:
            log.warning("Registro rechazado: %s", " | ".join(errores))
            return render_template("form.html", producto=request.form,
                                   categorias=db.list_categories(),
                                   errores=errores, modo="crear"), 400

        producto = db.create_product(**datos)
        log.info("Product created: %s (%s)", producto["code"], producto["name"])
        flash(f"Producto {producto['code']} registrado.", "ok")
        return redirect(url_for("inventario"))

    return render_template("form.html", producto={}, errores=[],
                           categorias=db.list_categories(), modo="crear")


@app.route("/productos/<int:product_id>/editar", methods=["GET", "POST"])
def editar_producto(product_id):
    """Editar producto."""
    producto = db.get_product(product_id)
    if not producto:
        log.warning("Intento de editar producto inexistente: id=%s", product_id)
        return render_template("error.html", codigo=404,
                               mensaje="Ese producto ya no existe."), 404

    if request.method == "POST":
        datos, errores = leer_formulario(request.form)

        existente = db.get_product_by_code(datos["code"]) if not errores else None
        if existente and existente["id"] != product_id:
            errores.append(f"El codigo {datos['code']} ya pertenece a otro producto.")

        if errores:
            log.warning("Edicion rechazada (id=%s): %s", product_id, " | ".join(errores))
            return render_template("form.html", producto=request.form,
                                   categorias=db.list_categories(),
                                   errores=errores, modo="editar",
                                   product_id=product_id), 400

        actualizado = db.update_product(product_id, **datos)
        log.info("Product updated: %s (%s)", actualizado["code"], actualizado["name"])
        flash(f"Producto {actualizado['code']} actualizado.", "ok")
        return redirect(url_for("inventario"))

    return render_template("form.html", producto=producto, errores=[],
                           categorias=db.list_categories(), modo="editar",
                           product_id=product_id)


@app.route("/productos/<int:product_id>/eliminar", methods=["POST"])
def eliminar_producto(product_id):
    """Eliminar producto."""
    eliminado = db.delete_product(product_id)
    if not eliminado:
        log.warning("Intento de eliminar producto inexistente: id=%s", product_id)
        return render_template("error.html", codigo=404,
                               mensaje="Ese producto ya no existe."), 404

    log.info("Product deleted: %s (%s)", eliminado["code"], eliminado["name"])
    flash(f"Producto {eliminado['code']} eliminado.", "ok")
    return redirect(url_for("inventario"))


# ---------------------------------------------------------------------------
# API REST (util para demostrar el CRUD con curl)
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Endpoint de comprobacion exigido por el enunciado."""
    try:
        db.check_connection()
        return jsonify({"status": "ok"})
    except Exception as error:
        log.error("Database connection failed: %s", error)
        return jsonify({"status": "error", "detail": str(error)}), 503


@app.route("/api/products", methods=["GET"])
def api_listar():
    filtro = request.args.get("filtro", "todos")
    categoria = request.args.get("categoria")
    productos = db.list_products(filtro, categoria)
    return jsonify([_serializar(p) for p in productos])


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_obtener(product_id):
    producto = db.get_product(product_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(_serializar(producto))


@app.route("/api/products", methods=["POST"])
def api_crear():
    datos = request.get_json(silent=True) or {}
    normalizados, errores = leer_formulario(datos)
    if errores:
        log.warning("API: creacion rechazada: %s", " | ".join(errores))
        return jsonify({"errors": errores}), 400
    if db.get_product_by_code(normalizados["code"]):
        return jsonify({"errors": ["El codigo ya existe"]}), 409

    producto = db.create_product(**normalizados)
    log.info("Product created: %s (%s)", producto["code"], producto["name"])
    return jsonify(_serializar(producto)), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def api_actualizar(product_id):
    if not db.get_product(product_id):
        return jsonify({"error": "Producto no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    normalizados, errores = leer_formulario(datos)
    if errores:
        return jsonify({"errors": errores}), 400

    producto = db.update_product(product_id, **normalizados)
    log.info("Product updated: %s (%s)", producto["code"], producto["name"])
    return jsonify(_serializar(producto))


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_eliminar(product_id):
    eliminado = db.delete_product(product_id)
    if not eliminado:
        return jsonify({"error": "Producto no encontrado"}), 404
    log.info("Product deleted: %s (%s)", eliminado["code"], eliminado["name"])
    return jsonify({"deleted": eliminado["code"]})


def _serializar(producto):
    """Convierte tipos de PostgreSQL a JSON."""
    salida = dict(producto)
    salida["price"] = float(salida["price"])
    salida["registered_at"] = salida["registered_at"].isoformat()
    return salida


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("Application started")
    log.info("Escuchando en http://%s:%s", APP_HOST, APP_PORT)
    try:
        db.check_connection()
        log.info("Database connection OK (%s@%s:%s/%s)",
                 db.DB_CONFIG["user"], db.DB_CONFIG["host"],
                 db.DB_CONFIG["port"], db.DB_CONFIG["dbname"])
    except Exception as error:
        log.error("Database connection failed: %s", error)

    app.run(host=APP_HOST, port=APP_PORT, debug=False)

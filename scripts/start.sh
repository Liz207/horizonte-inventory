#!/usr/bin/env bash
# ============================================================
# Horizonte Inventory - arranque del sistema
#   ./scripts/start.sh
# Inicia PostgreSQL (si esta detenido) y luego la aplicacion web.
# ============================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PID_FILE="$PROJECT_DIR/scripts/app.pid"
LOG_FILE="$PROJECT_DIR/logs/application.log"

# --- Configuracion -------------------------------------------------------
if [[ -f "$PROJECT_DIR/.env" ]]; then
  set -a; source "$PROJECT_DIR/.env"; set +a
fi
APP_PORT="${APP_PORT:-8080}"

mkdir -p "$PROJECT_DIR/logs"

# --- Evitar arrancar dos veces -------------------------------------------
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "La aplicacion ya esta en ejecucion (PID $(cat "$PID_FILE"))."
  echo "Deténgala primero con ./scripts/stop.sh"
  exit 0
fi

# --- 1. Base de datos ----------------------------------------------------
echo "==> Verificando PostgreSQL"
if ! pg_isready -q 2>/dev/null; then
  sudo systemctl start postgresql
  sleep 3
fi
pg_isready || { echo "PostgreSQL no responde."; exit 1; }
echo "    PostgreSQL activo."

# --- 2. Aplicacion web ---------------------------------------------------
echo "==> Iniciando Horizonte Inventory"
PYTHON="$PROJECT_DIR/venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3)"

cd "$PROJECT_DIR/source"
nohup "$PYTHON" app.py >> "$PROJECT_DIR/logs/stdout.log" 2>&1 &
echo $! > "$PID_FILE"
cd "$PROJECT_DIR"

# --- 3. Comprobacion /health --------------------------------------------
echo "==> Esperando respuesta de /health"
for intento in $(seq 1 15); do
  if curl -fs "http://localhost:${APP_PORT}/health" >/dev/null 2>&1; then
    echo
    echo "Horizonte Inventory esta en linea."
    echo "  Aplicacion : http://localhost:${APP_PORT}"
    echo "  Health     : http://localhost:${APP_PORT}/health -> $(curl -s http://localhost:${APP_PORT}/health)"
    echo "  Logs       : $LOG_FILE"
    echo "  PID        : $(cat "$PID_FILE")"
    exit 0
  fi
  sleep 1
done

echo "La aplicacion no respondio a tiempo. Revise $LOG_FILE"
exit 1

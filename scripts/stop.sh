#!/usr/bin/env bash
# ============================================================
# Horizonte Inventory - detener la aplicacion
#   ./scripts/stop.sh
# PostgreSQL se deja activo (es un servicio del sistema).
# ============================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$PROJECT_DIR/scripts/app.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No hay archivo de PID: la aplicacion no fue iniciada con start.sh."
  pkill -f "python.*app.py" && echo "Procesos residuales detenidos." || echo "Nada que detener."
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  sleep 2
  kill -0 "$PID" 2>/dev/null && kill -9 "$PID"
  echo "Horizonte Inventory detenido (PID $PID)."
else
  echo "El proceso $PID ya no existe."
fi

rm -f "$PID_FILE"

# Para detener tambien la base de datos:
#   sudo systemctl stop postgresql

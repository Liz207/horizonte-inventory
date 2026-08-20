#!/usr/bin/env bash
# ============================================================
# Horizonte Inventory - instalacion en Ubuntu Server
# Se ejecuta UNA sola vez, con internet disponible:
#   sudo ./scripts/install.sh
# Despues de esto la aplicacion funciona sin internet.
# ============================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ $EUID -ne 0 ]]; then
  echo "Ejecute este script con sudo: sudo ./scripts/install.sh"
  exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"

echo "==> 1/5 Instalando paquetes del sistema"
apt-get update
apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib curl

echo "==> 2/5 Habilitando PostgreSQL"
systemctl enable --now postgresql

echo "==> 3/5 Creando rol, base de datos, tabla y datos de prueba"
sudo -u postgres psql -v ON_ERROR_STOP=1 < "$PROJECT_DIR/database/init_db.sql"
sudo -u postgres psql -v ON_ERROR_STOP=1 -d horizonte < "$PROJECT_DIR/database/schema.sql"
sudo -u postgres psql -v ON_ERROR_STOP=1 -d horizonte < "$PROJECT_DIR/database/seed.sql"

echo "==> 4/5 Creando entorno virtual de Python"
sudo -u "$REAL_USER" python3 -m venv "$PROJECT_DIR/venv"
sudo -u "$REAL_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$REAL_USER" "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/source/requirements.txt"

echo "==> 5/5 Preparando archivo de configuracion y carpeta de logs"
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi
mkdir -p "$PROJECT_DIR/logs"
chown -R "$REAL_USER":"$REAL_USER" "$PROJECT_DIR"

echo
echo "Instalacion completada."
echo "Inicie la aplicacion con:  ./scripts/start.sh"

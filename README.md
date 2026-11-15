# Horizonte Inventory

<!-- local-development:start -->
## Desarrollo local

Consulta [RUNNING.md](RUNNING.md) para ubicar cada componente, abrirlo en su IDE, compilarlo y conocer las comprobaciones realizadas y los requisitos pendientes.
<!-- local-development:end -->

Sistema de inventario de **Libreria Horizonte S.R.L.**
Examen Integral ITI-522 — Computacion en la Nube — Universidad Tecnica Nacional.

| Estudiante 1 | *Ingrid Sequeira Blandón* |
|---|---|
| **Estudiante 2** | *Keylin Martinez* |
| **Repositorio** |https://github.com/Liz207/horizonte-inventory.git|

---

## 1. Objetivo del proyecto

Sustituir el control manual de inventario en hojas de calculo por una aplicacion
web que permita **registrar, consultar, editar y eliminar** productos del catalogo
de la libreria (libros, material educativo y articulos de oficina).

Todo el sistema —servidor web, base de datos y archivo de bitacora— se ejecuta
**dentro de una unica maquina virtual** y **no depende de ningun servicio externo**:
no se usan CDN, ni fuentes web, ni APIs de terceros. Es la simulacion local de una
infraestructura que despues podria migrarse a un proveedor de nube.

## 2. Sistema operativo utilizado

**Ubuntu Server 22.04.5 LTS** (64 bits) sobre **Oracle VirtualBox**.
Recursos de la VM: 2 vCPU, 4 GB de RAM, 50 GB de disco.
El procedimiento completo de creacion de la VM esta en
[`docs/instalacion-vm.md`](docs/instalacion-vm.md).

## 3. Lenguaje utilizado

**Python 3.10**

## 4. Framework utilizado

**Flask 3.1** (plantillas Jinja2 renderizadas en el servidor).
La interfaz usa CSS propio (`source/static/styles.css`) — sin librerias externas,
para que la aplicacion funcione con la VM totalmente desconectada de internet.

## 5. Motor de base de datos

**PostgreSQL 16**, instalado y ejecutandose dentro de la misma VM.
Base de datos: `horizonte` · usuario de la aplicacion: `horizonte_app` ·
tabla principal: `products` · datos de prueba: **24 productos**.

## 6. Puerto de la aplicacion

**8080** → `http://localhost:8080`
(se puede cambiar con la variable `APP_PORT` del archivo `.env`).

---

## Instalacion (una sola vez, con internet)

```bash
git clone <URL-DEL-REPOSITORIO> horizonte-inventory
cd horizonte-inventory
sudo ./scripts/install.sh
```

El script instala Python, PostgreSQL y las dependencias; crea el rol y la base de
datos; ejecuta `schema.sql` y `seed.sql`; y genera el archivo `.env` a partir de
`.env.example`. **Despues de este paso la aplicacion ya no necesita internet.**

Si prefiere hacerlo manualmente:

```bash
sudo apt update && sudo apt install -y python3 python3-venv postgresql curl
sudo systemctl enable --now postgresql
sudo -u postgres psql -f database/init_db.sql
sudo -u postgres psql -d horizonte -f database/schema.sql
sudo -u postgres psql -d horizonte -f database/seed.sql
python3 -m venv venv && ./venv/bin/pip install -r source/requirements.txt
cp .env.example .env
```

## 7. Como iniciar la aplicacion

```bash
./scripts/start.sh
```

El script verifica que PostgreSQL este activo, arranca la aplicacion en segundo
plano, guarda su PID en `scripts/app.pid` y espera a que `/health` responda:

```
==> Verificando PostgreSQL
    PostgreSQL activo.
==> Iniciando Horizonte Inventory
==> Esperando respuesta de /health

Horizonte Inventory esta en linea.
  Aplicacion : http://localhost:8080
  Health     : http://localhost:8080/health -> {"status":"ok"}
  Logs       : /home/usuario/horizonte-inventory/logs/application.log
```

## 8. Como detener la aplicacion

```bash
./scripts/stop.sh
```

PostgreSQL queda activo por ser un servicio del sistema. Para detenerlo tambien:
`sudo systemctl stop postgresql`.

## 9. Como acceder mediante navegador

- **Desde la VM (Ubuntu con escritorio o navegador de texto):** `http://localhost:8080`
- **Desde la VM en modo consola:** `curl http://localhost:8080/health`
- **Desde el equipo anfitrion:** configure en VirtualBox el reenvio de puertos
  `8080 → 8080` (NAT) o use adaptador *Bridge* y entre a `http://<IP-de-la-VM>:8080`.
  La IP se obtiene con `ip a`. Ver detalles en `docs/instalacion-vm.md`.

Pantallas disponibles:

| Ruta | Funcion |
|---|---|
| `/` | Inventario completo, con totales, buscador y filtros |
| `/?filtro=disponibles` | Solo productos con existencias |
| `/?filtro=agotados` | Solo productos sin existencias |
| `/?categoria=Libros` | Productos por categoria |
| `/productos/nuevo` | Registrar producto |
| `/productos/<id>/editar` | Editar producto |

## 10. Como comprobar `/health`

```bash
curl http://localhost:8080/health
```

Respuesta esperada:

```json
{"status": "ok"}
```

Si la base de datos esta caida, el endpoint responde `503` con
`{"status": "error", ...}` y escribe una linea `ERROR` en la bitacora.

### API REST (para comprobar el CRUD con `curl`)

```bash
# Consultar
curl http://localhost:8080/api/products
curl "http://localhost:8080/api/products?filtro=agotados"

# Registrar
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -d '{"code":"BOOK-777","name":"Libro de prueba","category":"Libros","price":"9500","quantity":"5"}'

# Editar
curl -X PUT http://localhost:8080/api/products/25 \
  -H "Content-Type: application/json" \
  -d '{"code":"BOOK-777","name":"Libro editado","category":"Libros","price":"9900","quantity":"3"}'

# Eliminar
curl -X DELETE http://localhost:8080/api/products/25
```

## 11. Ubicacion de los logs

```
logs/application.log
```

Formato: `AAAA-MM-DD HH:MM:SS NIVEL mensaje`. Registra el inicio de la aplicacion,
cada solicitud recibida, la creacion / modificacion / eliminacion de productos y
los errores. Para verlo en vivo mientras se usa la aplicacion:

```bash
tail -f logs/application.log
```

Ejemplo real:

```
2026-08-20 19:17:53 INFO Application started
2026-08-20 19:17:53 INFO Database connection OK (horizonte_app@localhost:5432/horizonte)
2026-08-20 19:17:57 INFO Request GET /health -> 200 (127.0.0.1)
2026-08-20 19:17:57 INFO Product created: TEST-999 (Producto de prueba)
2026-08-20 19:18:20 INFO Product updated: TEST-999 (Producto editado)
2026-08-20 19:18:20 INFO Product deleted: WEB-001 (Alta desde formulario)
2026-08-20 19:18:34 ERROR Database connection failed: connection refused
```

---

## Estructura del repositorio

```
horizonte-inventory/
├── source/                 aplicacion web
│   ├── app.py              rutas, validaciones, logging, /health
│   ├── db.py               acceso a PostgreSQL (CRUD y consultas)
│   ├── templates/          base, index, form, error (Jinja2)
│   ├── static/styles.css   estilos propios, sin CDN
│   └── requirements.txt
├── database/
│   ├── init_db.sql         rol y base de datos
│   ├── schema.sql          tabla products e indices
│   └── seed.sql            24 productos de prueba
├── logs/application.log    bitacora de la aplicacion
├── scripts/
│   ├── install.sh          instalacion inicial de la VM
│   ├── start.sh            arranque del sistema
│   ├── stop.sh             detencion de la aplicacion
│   └── horizonte.service   (opcional) arranque automatico con systemd
├── docs/
│   ├── arquitectura.md     diagrama y explicacion
│   └── instalacion-vm.md   creacion de la VM en VirtualBox
├── evidence/               capturas de pantalla
├── README.md
└── CHANGELOG.md
```

## Modelo de datos

```sql
CREATE TABLE products (
    id            SERIAL PRIMARY KEY,
    code          VARCHAR(30)    NOT NULL UNIQUE,
    name          VARCHAR(150)   NOT NULL,
    category      VARCHAR(60)    NOT NULL,
    price         NUMERIC(12,2)  NOT NULL CHECK (price >= 0),
    quantity      INTEGER        NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    registered_at TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Comprobar la persistencia

```bash
./scripts/stop.sh
./scripts/start.sh
curl http://localhost:8080/api/products | head
```

Los datos siguen ahi porque viven en PostgreSQL, no en la memoria de la aplicacion.
Tambien se pueden consultar directamente:

```bash
sudo -u postgres psql -d horizonte -c "SELECT id, code, name, quantity FROM products ORDER BY id;"
```

## Arranque automatico (opcional)

```bash
sudo cp scripts/horizonte.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now horizonte
```

Revise antes las rutas y el usuario dentro del archivo `.service`.

## Solucion de problemas

| Sintoma | Causa probable | Solucion |
|---|---|---|
| `/health` responde 503 | PostgreSQL detenido | `sudo systemctl start postgresql` |
| `password authentication failed` | credenciales distintas en `.env` | ajuste `DB_USER` / `DB_PASSWORD` |
| `Address already in use` | la aplicacion ya corria | `./scripts/stop.sh` y vuelva a iniciar |
| No abre desde el anfitrion | falta reenvio de puertos | configure NAT 8080→8080 en VirtualBox |
| `logs/` vacio | la app no arranco | revise `logs/stdout.log` |

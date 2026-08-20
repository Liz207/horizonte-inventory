# CHANGELOG

Todos los cambios relevantes del proyecto Horizonte Inventory.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y versionado segun [SemVer](https://semver.org/lang/es/).

## [1.0.0] — 2026-08-20

Primera version funcional entregada para el Examen Integral de ITI-522.

### Agregado
- Aplicacion web **Horizonte Inventory** en Python 3.12 + Flask 3.1.
- CRUD completo de productos desde la interfaz web (registrar, consultar,
  editar y eliminar).
- API REST equivalente en `/api/products` para comprobaciones con `curl`.
- Filtros de inventario: todos, disponibles, sin existencias y por categoria,
  ademas de buscador por nombre o codigo.
- Panel de totales: productos registrados, con existencias, agotados y valor
  del inventario.
- Base de datos PostgreSQL 16 con la tabla `products` (`init_db.sql`,
  `schema.sql`) e indices por categoria y existencias.
- Seed con 24 productos de prueba, incluyendo articulos agotados para
  demostrar el filtro correspondiente.
- Bitacora en `logs/application.log` con inicio de la aplicacion, solicitudes
  recibidas, altas, modificaciones, eliminaciones y errores; rotacion
  automatica a los 2 MB.
- Endpoint `/health` que verifica la conexion a la base de datos.
- Scripts `install.sh`, `start.sh` y `stop.sh`, y unidad opcional de systemd.
- Validacion de formularios (codigo unico, precio y cantidad no negativos) con
  paginas de error 404 y 500 propias.
- Documentacion: `README.md`, `docs/arquitectura.md`, `docs/instalacion-vm.md`
  y carpeta `evidence/`.

### Seguridad
- La aplicacion se conecta con el rol `horizonte_app`, que no es superusuario y
  solo tiene permisos sobre la tabla `products`.
- Las credenciales viven en `.env` (excluido del repositorio mediante
  `.gitignore`); se versiona unicamente `.env.example`.

## [0.2.0] — 2026-08-18

### Agregado
- Interfaz web con listado de productos y formulario de registro.
- Conexion a PostgreSQL mediante psycopg2 y capa de datos `db.py`.

### Cambiado
- El almacenamiento en memoria del prototipo se sustituyo por tablas
  persistentes en PostgreSQL.

## [0.1.0] — 2026-08-15

### Agregado
- Estructura inicial del repositorio.
- Prototipo de Flask con la ruta `/health`.
- Maquina virtual Ubuntu Server 24.04 LTS creada en VirtualBox.

# Arquitectura — Horizonte Inventory

Toda la solucion vive dentro de **una sola maquina virtual**. No hay servicios
externos, contenedores, balanceadores ni dominios publicos: es una arquitectura
autocontenida, equivalente a un unico servidor de aplicaciones en la nube.

## Diagrama

```
        Usuario
          │
          ▼
     Navegador Web
          │  HTTP :8080
          ▼
┌──────────────────────────────────────────────────────┐
│ Maquina Virtual — VirtualBox                         │
│ 2 vCPU · 4 GB RAM · 50 GB disco · Red NAT (8080)     │
│                                                      │
│   ┌────────────────────────────────────────┐         │
│   │ Sistema Operativo                      │         │
│   │ Ubuntu Server 22.04.5 LTS                │         │
│   └───────────────────┬────────────────────┘         │
│                       │                              │
│   ┌───────────────────▼────────────────────┐         │
│   │ Aplicacion Web — Horizonte Inventory   │         │
│   │ Python 3.10 + Flask 3.1                │         │
│   │ app.py  ·  db.py  ·  templates/        │         │
│   │ Rutas: / · /productos · /api · /health │         │
│   └────────┬──────────────────────┬────────┘         │
│            │ psycopg2 :5432       │ logging          │
│   ┌────────▼─────────┐   ┌────────▼──────────┐       │
│   │ Base de Datos    │   │ Logs              │       │
│   │ PostgreSQL 16    │   │ logs/             │       │
│   │ BD: horizonte    │   │ application.log   │       │
│   │ Tabla: products  │   │                   │       │
│   └──────────────────┘   └───────────────────┘       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Componentes

| Componente | Tecnologia | Funcion |
|---|---|---|
| Virtualizacion | Oracle VirtualBox 7 | Aloja la VM y expone el puerto 8080 |
| Sistema operativo | Ubuntu Server 22.04.5 LTS | Servicios, red y arranque |
| Servidor de aplicacion | Flask 3.1 sobre Python 3.10 | Rutas, validaciones, plantillas |
| Acceso a datos | psycopg2 (`db.py`) | Consultas SQL parametrizadas |
| Persistencia | PostgreSQL 16 (`systemd`) | Tabla `products` |
| Bitacora | modulo `logging` de Python | `logs/application.log`, con rotacion |
| Automatizacion | Bash (`install/start/stop.sh`) | Instalacion y operacion |

## Flujo de una solicitud

1. El usuario abre `http://localhost:8080` en el navegador.
2. Flask atiende la ruta y llama a la funcion correspondiente de `db.py`.
3. `db.py` abre una conexion a PostgreSQL, ejecuta la consulta parametrizada,
   confirma la transaccion y cierra la conexion.
4. Flask renderiza la plantilla Jinja2 con los datos obtenidos.
5. El `after_request` escribe una linea en `logs/application.log`; las
   operaciones de alta, edicion y borrado agregan su propia linea.

## Decisiones de diseno

- **Separacion de responsabilidades.** `app.py` maneja HTTP y `db.py` maneja SQL.
  Migrar a otro motor de base de datos requeriria cambiar un solo archivo.
- **Consultas parametrizadas.** Todos los valores se envian como parametros de
  psycopg2, nunca concatenados: evita inyeccion de SQL.
- **Sin dependencias de red.** Los estilos son un CSS propio y las tipografias
  son las del sistema, de modo que la interfaz se ve igual con la VM aislada.
- **Configuracion por variables de entorno.** El archivo `.env` separa las
  credenciales del codigo; es el mismo patron que se usaria al migrar a la nube.
- **Rol de base de datos con privilegios minimos.** `horizonte_app` solo puede
  leer y escribir en `products`.

## Ruta de migracion a la nube (siguiente etapa)

| Componente local | Equivalente en nube |
|---|---|
| VM de VirtualBox | Instancia EC2 / Azure VM / Compute Engine |
| PostgreSQL en la VM | Amazon RDS / Azure Database for PostgreSQL |
| `logs/application.log` | CloudWatch Logs / Azure Monitor |
| `start.sh` | Unidad de systemd, contenedor o servicio administrado |
| `.env` | Secrets Manager / Key Vault |

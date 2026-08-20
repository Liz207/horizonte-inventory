# Creacion de la maquina virtual (VirtualBox + Ubuntu Server)

Guia completa, desde la descarga de la imagen hasta la exportacion del archivo
`.ova` que se entrega en el Drive.

---

## 0. Requisitos previos

- **VirtualBox 7.x** instalado en el equipo anfitrion
  (menu *Ayuda → Acerca de* para ver la version).
- **Virtualizacion habilitada en la BIOS/UEFI** (Intel VT-x o AMD-V). Si
  VirtualBox solo ofrece sistemas de 32 bits, esta opcion esta desactivada.
- Al menos **60 GB libres** en disco y 8 GB de RAM en el anfitrion.
- ISO de **Ubuntu Server 24.04 LTS** (o 22.04 LTS), descargada de
  `https://ubuntu.com/download/server` — archivo
  `ubuntu-24.04.x-live-server-amd64.iso`.

> Se usa la edicion **Server** (sin escritorio): consume menos recursos y es lo
> que se usaria en un servidor real. La aplicacion se comprueba con `curl` desde
> la consola de la VM y con el navegador del anfitrion mediante reenvio de puertos.

---

## 1. Crear la maquina virtual

1. VirtualBox → **Nueva**.
2. **Nombre:** `Horizonte-Inventory-VM`
3. **Carpeta:** deje la predeterminada o elija un disco con espacio.
4. **Imagen ISO:** seleccione el ISO de Ubuntu Server descargado.
5. Marque **"Skip Unattended Installation" / "Omitir instalacion desatendida"**.
   Asi la instalacion se hace paso a paso y usted controla usuario y contrasena.
6. **Siguiente** → *Hardware*:
   - **Memoria base:** `4096 MB` (4 GB)
   - **Procesadores:** `2`
   - No marque *Enable EFI* (no es necesario).
7. **Siguiente** → *Disco duro virtual*:
   - **Crear un disco virtual ahora**
   - **Tamano:** `50 GB`
   - Deje *Pre-asignar tamano completo* **sin marcar** (disco dinamico, ocupa
     solo lo que se use).
8. **Siguiente → Terminar.**

## 2. Configurar la red y el reenvio de puertos

Con la VM apagada: **Configuracion → Red → Adaptador 1**.

- **Conectado a:** `NAT`
- **Avanzadas → Reenvio de puertos → Agregar** dos reglas:

| Nombre | Protocolo | IP anfitrion | Puerto anfitrion | IP invitado | Puerto invitado |
|---|---|---|---|---|---|
| App  | TCP | 127.0.0.1 | 8080 | *(vacio)* | 8080 |
| SSH  | TCP | 127.0.0.1 | 2222 | *(vacio)* | 22   |

Con esto, desde el anfitrion:
- La aplicacion se abre en `http://localhost:8080`
- Se entra por consola con `ssh usuario@localhost -p 2222`

> **Alternativa:** adaptador *Adaptador puente (Bridge)*. La VM recibe una IP de
> la red local (`ip a`) y se accede con `http://<IP-de-la-VM>:8080`. Es mas
> comodo para la demostracion en clase, pero la IP cambia de red en red; NAT con
> reenvio funciona siempre.

## 3. Instalar Ubuntu Server

Inicie la VM y siga el instalador:

1. **Idioma:** English (recomendado; evita mensajes mezclados en la terminal).
2. **Actualizar el instalador:** *Continue without updating*.
3. **Teclado:** `Spanish (Latin American)` si su teclado es latino.
4. **Tipo de instalacion:** `Ubuntu Server` (no la *minimized*).
5. **Red:** deje DHCP; el adaptador debe mostrar una IP `10.0.2.15` (NAT).
6. **Proxy y mirror:** deje los valores predeterminados.
7. **Almacenamiento:** *Use an entire disk* → confirme con **Continue**
   (borra unicamente el disco virtual).
8. **Perfil:**
   - Nombre: `Estudiante Horizonte`
   - Nombre del servidor: `horizonte-vm`
   - Usuario: `horizonte`
   - Contrasena: la que usted defina — **anotela y pongala en el README de
     entrega para que el profesor pueda iniciar sesion.**
9. **Ubuntu Pro:** *Skip for now*.
10. **SSH:** marque **Install OpenSSH server** (permite trabajar comodo desde el
    anfitrion y copiar evidencias).
11. **Snaps:** no seleccione ninguno.
12. Espere a que termine y elija **Reboot Now**. Si pide retirar el medio de
    instalacion, presione Enter; si la VM vuelve al instalador, apaguela y quite
    el ISO en *Configuracion → Almacenamiento*.

## 4. Preparar el sistema

Inicie sesion con el usuario creado y ejecute:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl
```

Verifique version y red (sirven como evidencia 2):

```bash
lsb_release -a
uname -a
ip a
free -h
df -h /
```

## 5. Desplegar Horizonte Inventory

```bash
git clone <URL-DEL-REPOSITORIO> horizonte-inventory
cd horizonte-inventory
sudo ./scripts/install.sh
./scripts/start.sh
```

Comprobaciones dentro de la VM:

```bash
curl http://localhost:8080/health         # {"status": "ok"}
curl -s http://localhost:8080/api/products | head
tail -f logs/application.log
```

Desde el anfitrion, abra `http://localhost:8080` en el navegador (con la regla
de reenvio de puertos ya configurada).

## 6. Firewall (si lo activa)

Ubuntu Server trae `ufw` inactivo. Si decide habilitarlo:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp
sudo ufw enable
sudo ufw status
```

## 7. Que la aplicacion inicie sola al encender la VM (opcional pero recomendado)

Facilita la revision: el profesor enciende la VM y el sistema ya esta arriba.

```bash
sudo cp scripts/horizonte.service /etc/systemd/system/
sudo nano /etc/systemd/system/horizonte.service   # ajuste usuario y rutas
sudo systemctl daemon-reload
sudo systemctl enable --now horizonte
systemctl status horizonte
```

## 8. Tomar las evidencias

Antes de exportar, capture las 10 pantallas indicadas en `evidence/README.md`.
Para copiar archivos de la VM al anfitrion:

```bash
scp -P 2222 horizonte@localhost:~/horizonte-inventory/logs/application.log .
```

## 9. Exportar la maquina virtual (.ova)

1. Apague la VM correctamente: `sudo poweroff`.
2. VirtualBox → seleccione la VM → menu **Archivo → Exportar servicio virtualizado**.
3. Formato: **OVF 2.0**, archivo `Horizonte-Inventory-VM.ova`.
4. Exporte y suba el `.ova` a Google Drive o OneDrive.
5. **Comparta el enlace con permiso de lectura para cualquiera con el vinculo**
   y verifiquelo en una ventana de incognito antes de entregar.

> El `.ova` de una VM con 50 GB dinamicos suele pesar entre 3 y 6 GB. Para
> reducirlo, antes de exportar ejecute dentro de la VM:
> ```bash
> sudo apt clean && sudo journalctl --vacuum-time=1d
> ```

## 10. Datos que debe entregar junto con la VM

| Dato | Valor |
|---|---|
| Usuario de la VM | `horizonte` |
| Contrasena | *(la que definio)* |
| Ruta del proyecto | `/home/horizonte/horizonte-inventory` |
| Iniciar el sistema | `./scripts/start.sh` |
| URL de la aplicacion | `http://localhost:8080` |
| Usuario de PostgreSQL | `horizonte_app` / `Horizonte2026` |

## Problemas frecuentes

| Sintoma | Solucion |
|---|---|
| VirtualBox solo muestra SO de 32 bits | Habilite VT-x/AMD-V en la BIOS y desactive Hyper-V en Windows (`bcdedit /set hypervisorlaunchtype off`) |
| La VM arranca al instalador otra vez | Quite el ISO en *Configuracion → Almacenamiento* |
| `http://localhost:8080` no abre en el anfitrion | Revise la regla de reenvio y que la app este corriendo (`./scripts/start.sh`) |
| Pantalla muy pequena | `Ver → Escala`, o trabaje por SSH desde el anfitrion |
| Sin internet dentro de la VM | Adaptador en NAT y cable conectado en el anfitrion; pruebe `ping -c2 1.1.1.1` |

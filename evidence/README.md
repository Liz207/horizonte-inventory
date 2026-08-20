# Evidencias

Capturas de pantalla exigidas por el punto 14 del enunciado. Guarde cada imagen
en esta carpeta con el nombre indicado (PNG o JPG).

| # | Archivo | Que debe mostrar | Como obtenerla |
|---|---|---|---|
| 1 | `01-vm-ejecutandose.png` | La VM encendida en VirtualBox | Captura de la ventana de VirtualBox con la VM en estado *Corriendo* |
| 2 | `02-sistema-operativo.png` | Version del SO | `lsb_release -a && uname -a && free -h` |
| 3 | `03-aplicacion-web.png` | La aplicacion en el navegador | Abrir `http://localhost:8080` |
| 4 | `04-lista-productos.png` | Listado con los 24 productos y filtros | Pantalla principal, mostrando los totales |
| 5 | `05-creacion-producto.png` | Un producto recien registrado | Formulario lleno + mensaje "Producto XXX registrado" |
| 6 | `06-base-de-datos.png` | Los registros en PostgreSQL | `sudo -u postgres psql -d horizonte -c "SELECT * FROM products;"` |
| 7 | `07-health.png` | Respuesta del endpoint | `curl http://localhost:8080/health` |
| 8 | `08-logs.png` | El archivo de bitacora | `tail -20 logs/application.log` |
| 9 | `09-script-inicio.png` | Salida del script de arranque | `./scripts/start.sh` |
| 10 | `10-repositorio.png` | El repositorio publico | Pagina del repositorio en GitHub/Bitbucket |

Recomendacion: para la evidencia 8, haga una alta, una edicion y una eliminacion
y luego capture el log, de modo que se vean las lineas `Product created`,
`Product updated` y `Product deleted` en la misma imagen.

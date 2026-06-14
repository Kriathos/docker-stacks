# Configuración del stack Storage

Este archivo documenta las configuraciones específicas del stack `storage`.

## Rutas de datos locales en Windows

`docker-compose.yml` monta varias carpetas locales de Windows. Asegúrate de que estas rutas existan o cámbialas a rutas válidas:

- `F:/sftp`
- `F:/sftpgo-data`
- `F:/minio-data`
- `F:/apache-fileserver`

## Volúmenes y persistencia

- `sqlserver_data`: datos de SQL Server
- `db2_data`: datos de DB2

Si prefieres no usar volumenes locales, puedes eliminarlas del `docker-compose.yml` y usar volúmenes Docker gestionados.

## Credenciales de acceso

- SQL Server:
  - Usuario: `sa`
  - Contraseña: `Generar en docker-compose.yml`
- DB2:
  - Usuario: `db2inst1`
  - Contraseña: `Generar en docker-compose.yml`
  - Base de datos: `SAMPLE`
- SFTPGo:
  - Puerto SFTP: `2022`
  - HTTP UI: `51500` (interno)
- MinIO:
  - Usuario: `admin`
  - Contraseña: `Generar en docker-compose.yml`

## Exposición de puertos

Algunos puertos están comentados en `docker-compose.yml`. Si necesitas acceso directo desde el host, descomenta las líneas correspondientes:

- MinIO: `9000`, consola `9001`
- Apache Fileserver: `80`

## Red Docker

Este stack se conecta a la red externa `mynet` para trabajar con el proxy Nginx del stack `web`.

```powershell
docker network create mynet --driver bridge
```

## Notas de configuración

- Si no deseas usar `F:/`, actualiza los montajes de volumen con rutas locales válidas.
- El servicio `sftpgo` está configurado para usar SQLite internamente.

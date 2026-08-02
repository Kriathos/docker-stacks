# Configuración del stack Storage

Este archivo documenta las configuraciones específicas del stack `storage`.

## Ejecutar el Stack

El archivo de configuración principal se llama `docker-compose-storage.yml`. Para interactuar con el stack, siempre debes especificar el nombre del archivo con la opción `-f`:

### Iniciar el stack
```powershell
docker-compose -f docker-compose-storage.yml up -d
```

### Verificar estado
```powershell
docker-compose -f docker-compose-storage.yml ps
```

### Detener el stack
```powershell
docker-compose -f docker-compose-storage.yml down
```

### Limpiar completamente (elimina datos y volúmenes)
```powershell
docker-compose -f docker-compose-storage.yml down -v
```

### Ver logs
```powershell
# Logs de un servicio específico
docker-compose -f docker-compose-storage.yml logs -f sqlserver

# Todos los logs
docker-compose -f docker-compose-storage.yml logs -f
```

### Ejecutar comandos dentro de un contenedor
```powershell
# Ejemplo: acceder a SQL Server
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa
```

---

## Archivos de Configuración

### docker-compose-storage.yml

Archivo principal de configuración del stack Storage. Contiene la definición de todos los servicios:
- SQL Server
- IBM DB2
- SFTPGo
- MinIO
- Apache File Server

**Ubicación**: `./docker-compose-storage.yml`

**Notas**: 
- Este es el archivo que debes usar con `-f docker-compose-storage.yml` en todos tus comandos docker-compose
- Contiene la configuración de redes (external `mynet`), volúmenes y servicios
- Las contraseñas están marcadas con `CONTRASEÑA` - reemplázalas con valores seguros

---

## Rutas de datos locales en Windows

`docker-compose-storage.yml` monta varias carpetas locales de Windows. Asegúrate de que estas rutas existan o cámbialas a rutas válidas:

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

Este stack se conecta a la red externa `mynet` para trabajar con el proxy Caddy del stack `web`.

### Crear la red (si no existe)
```powershell
docker network create mynet --driver bridge
```

### Verificar que la red existe
```powershell
docker network ls | findstr mynet
```

### Inspeccionar la red
```powershell
docker network inspect mynet
```

### Conectar servicios a la red
Los servicios que necesiten comunicarse entre diferentes stacks (p.ej., `sftpgo`, `minio`, `file-server`) están configurados para conectarse automáticamente a la red `mynet` en `docker-compose-storage.yml`.

## Notas de configuración

- Si no deseas usar `F:/`, actualiza los montajes de volumen con rutas locales válidas.
- El servicio `sftpgo` está configurado para usar SQLite internamente.

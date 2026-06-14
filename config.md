# Configuración global del proyecto

Este archivo describe las dependencias y ajustes comunes a todos los stacks del repositorio.

## Red externa compartida

Todos los stacks dependen de una red Docker externa llamada `mynet` para que los servicios puedan comunicarse entre sí.

Crear la red si no existe:

```powershell
docker network create mynet --driver bridge
```

## Montajes locales en Windows

Algunos stacks usan rutas absolutas de Windows para montar datos en los contenedores. Verifica que las siguientes carpetas existan o ajústalas al entorno local:

- `F:/sftp`
- `F:/sftpgo-data`
- `F:/minio-data`
- `F:/apache-fileserver`

Si no deseas usar `F:/`, reemplaza las rutas en `storage/docker-compose.yml` por carpetas válidas en tu equipo.

## Hosts y nombres de dominio

El stack `web` utiliza nombres de dominio personalizados en `web/nginx.conf`. Para acceder a ellos desde el navegador, agrega las entradas necesarias a tu archivo de hosts de Windows:

```text
127.0.0.1 sftp.luispicado.com
127.0.0.1 minio.luispicado.com
127.0.0.1 minio-api.luispicado.com
127.0.0.1 data.luispicado.com
127.0.0.1 kraft-ui.luispicado.com
127.0.0.1 kraft-api.luispicado.com
127.0.0.1 zoo-ui.luispicado.com
127.0.0.1 zoo-api.luispicado.com
127.0.0.1 jupyter.luispicado.com
127.0.0.1 mlflow.luispicado.com
127.0.0.1 airflow.luispicado.com
127.0.0.1 vault.luispicado.com
127.0.0.1 spark.luispicado.com
```

## Docker Compose

Puedes usar cualquiera de estos comandos según tu versión de Docker:

```powershell
docker compose up -d
# o
docker-compose up -d
```

## Seguridad y producción

- Las contraseñas y credenciales en este proyecto son de prueba.
- No uses estas configuraciones en producción sin revisar autenticación, cifrado y permisos.
- El proxy Nginx expone varios servicios internos y asume un ambiente de prueba.

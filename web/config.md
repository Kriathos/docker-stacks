# Configuración del stack Web

Este archivo describe la configuración del proxy Nginx y las dependencias de los servicios conectados.

## Proxy Nginx

El archivo de configuración principal es `nginx.conf`.

### Comportamiento

- Sirve contenido estático desde `nginx_html`
- Reenvía solicitudes a servicios internos por nombre de host Docker
- Usa `proxy_pass` hacia los nombres de servicio definidos en los otros stacks

## Dominios proxy

Los nombres de host locales mapeados en `nginx.conf` son:

- `sftp.luispicado.com`
- `minio.luispicado.com`
- `minio-api.luispicado.com`
- `data.luispicado.com`
- `kraft-ui.luispicado.com`
- `kraft-api.luispicado.com`
- `zoo-ui.luispicado.com`
- `zoo-api.luispicado.com`
- `jupyter.luispicado.com`
- `mlflow.luispicado.com`
- `airflow.luispicado.com`
- `vault.luispicado.com`
- `spark.luispicado.com`

## Requisitos

- Red Docker externa `mynet`
- Todos los servicios proxy deben estar activos en la misma red
- Las entradas del archivo hosts de Windows deben resolver los dominios al localhost

## Puertos

- HTTP: `80`
- HTTPS: `443`

> Nota: Actualmente la configuración define los puertos, pero no está configurado ningún certificado TLS. Si habilitas HTTPS, agrega certificados y bloqueos de SSL apropiados.

## Ajustes de red

El stack usa la red externa `mynet` para conectarse a otros contenedores que no están definidos en `web/docker-compose.yml`.

```powershell
docker network create mynet --driver bridge
```

## Consejos

- Si un servicio no responde, verifica que el nombre del servicio y el puerto interno coincidan con el `proxy_pass` en `nginx.conf`
- Si prefieres no usar hostnames, puedes acceder a los servicios directamente si sus puertos están expuestos en los otros stacks

# Caddy Reverse Proxy Stack - Arquitectura y Funcionamiento

## Descripción General

Este stack implementa una arquitectura de microservicios con **Caddy** como reverse proxy centralizado, orquestando el acceso a múltiples servicios backend a través de un punto de entrada único. Caddy actúa como puerta de enlace (API Gateway) proporcionando enrutamiento inteligente, terminación TLS automática, balanceo de carga básico, y servicio de contenido estático.

## Arquitectura del Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENTE / INTERNET                          │
│                    (HTTP/HTTPS :80/:443)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │  CADDY Container  │
                   │  (Reverse Proxy)  │
                   │  2.8              │
                   └────────┬──────────┘
                            │
        ┌───────────────────┼───────────────────┬──────────────┐
        │                   │                   │              │
        ▼                   ▼                   ▼              ▼
   ┌─────────┐      ┌─────────────┐    ┌──────────────┐  ┌──────────┐
   │  Static │      │   SFTPGo    │    │    MinIO     │  │ Apache   │
   │   HTML  │      │  (SFTP UI)  │    │(API + Console)  │FileServer│
   │:80/port │      │ :51500      │    │:9000/:9001   │  │ :80      │
   └─────────┘      └─────────────┘    └──────────────┘  └──────────┘
        │                   │                   │              │
        │                   │                   │              │
        │            ┌──────┴───────────────────┴──────────────┘
        │            │
        ▼            ▼
   ┌──────────────────────┐
   │  Docker Network      │
   │  (mynet - bridge)    │
   └──────────────────────┘
```

## Componentes Principales

### 1. **Caddy (Reverse Proxy)**
- **Versión**: 2.8
- **Función**: Gateway centralizado que enruta tráfico hacia servicios backend
- **Características**:
  - Terminación TLS automática con Let's Encrypt
  - Enrutamiento basado en dominio (virtual hosts)
  - Servicio de archivos estáticos
  - Proxy inverso con manejo automático de headers
  - Admin API en puerto 2019 (deshabilitada en esta configuración)

### 2. **Contenido Estático**
- **Punto de entrada**: `http://your-domain.com:80/`
- **Ubicación**: `/usr/share/caddy/html`
- Sirve `index.html` como landing page
- Caddy intercede cualquier request a `/` que no coincida con otros dominios

### 3. **SFTPGo Web UI**
- **Dominio**: `sftp.luispicado.com`
- **Backend**: Container `sftpgo` en puerto 51500
- **Protocolo**: HTTP/HTTPS (terminación en Caddy)

### 4. **MinIO - Object Storage**
- **API Endpoint**: `minio-api.luispicado.com` → Container `minio:9000`
- **Console (Admin)**: `minio.luispicado.com` → Container `minio:9001`
- Funcionalidad S3-compatible para almacenamiento distribuido

### 5. **Apache File Server**
- **Dominio**: `data.luispicado.com`
- **Backend**: Container `apache-fileserver:80`
- Servicio de descarga/streaming de archivos

### 6. **Apache Spark Master**
- **Dominio**: `spark.luispicado.com`
- **Backend**: Container `spark:8080`
- Interfaz web de monitoreo del cluster Spark

## Flujo de Tráfico

### Ejemplo 1: Request al Landing Page
```
1. Cliente → GET http://example.com/
2. Caddy (líneas 7-10) → Valida que no sea un dominio específico
3. Caddy → Sirve /usr/share/caddy/html/index.html
4. Respuesta → Contenido HTML estático
```

### Ejemplo 2: Request a MinIO Console
```
1. Cliente → GET https://minio.luispicado.com/login
2. Caddy (línea 23-24) → Reconoce dominio "minio.luispicado.com"
3. Caddy → Proxy inverso a container "minio" puerto 9001
4. MinIO → Procesa request y responde
5. Caddy → Retorna respuesta al cliente con headers ajustados
```

### Ejemplo 3: Request a SFTPGo
```
1. Cliente → GET https://sftp.luispicado.com/
2. Caddy (línea 13-14) → Reconoce dominio "sftp.luispicado.com"
3. Caddy → Establece conexión con container "sftpgo:51500"
4. SFTPGo → Retorna página de login
5. Headers → Caddy preserva X-Forwarded-For, X-Forwarded-Proto, etc.
```

## Enrutamiento y Resolución de Dominios

### Orden de Precedencia de Bloques Caddy
Caddy evalúa requests en este orden:

1. **Dominios específicos** (líneas 13-35)
   - `sftp.luispicado.com` → SFTPGo
   - `minio-api.luispicado.com` → MinIO API
   - `minio.luispicado.com` → MinIO Console
   - `data.luispicado.com` → Apache File Server
   - `spark.luispicado.com` → Spark Master

2. **Default `:80` fallback** (líneas 7-10)
   - Aplica si el dominio no coincide con ninguno de los anteriores
   - Sirve archivos estáticos desde `/usr/share/caddy/html`

### Resolución de Nombres
- Los dominios (`sftp.luispicado.com`, `minio.luispicado.com`, etc.) deben estar configurados en:
  - **DNS externo** si se accede desde internet
  - **Hosts locales** (`/etc/hosts` o `C:\Windows\System32\drivers\etc\hosts`) para desarrollo
  - **Docker DNS interno** (automático dentro de la red `mynet`)

## Networking - Docker Network (mynet)

El stack usa una red bridge externa llamada `mynet`:

```yaml
networks:
  mynet:
    external: true
```

**Ventajas**:
- Permite que múltiples docker-compose.yml en diferentes directorios se comuniquen
- Service discovery automático: Caddy resuelve `sftpgo`, `minio`, `apache-fileserver`, `spark` por nombre
- Aislamiento de tráfico entre contenedores y máquina host
- Facilita escalabilidad horizontal

**Requisito**: La red debe existir previamente:
```bash
docker network create mynet
```

## Persistencia y Volúmenes

### Caddy Volumes
```yaml
volumes:
  - ./Caddyfile:/etc/caddy/Caddyfile:ro        # Config (read-only)
  - ./html:/usr/share/caddy/html               # Contenido estático
  - caddy_data:/data                           # Certs, cache
  - caddy_config:/config                       # Config persistente
```

**caddy_data**: Almacena certificados TLS generados automáticamente por Let's Encrypt
**caddy_config**: Guarda la configuración persistente y caché de Caddy

## Características de Seguridad

### HTTPS/TLS Automático
- Caddy solicita certificados automáticamente a Let's Encrypt
- Requiere que los dominios sean públicos y accesibles desde internet
- Renovación automática 30 días antes de expiración

### Headers de Proxy Inverso
Caddy inyecta automáticamente:
- `X-Forwarded-For`: IP original del cliente
- `X-Forwarded-Proto`: Protocolo original (http/https)
- `X-Forwarded-Host`: Dominio original

Esto permite que servicios backend conozcan el cliente real.

### Admin API
```
admin off  # (línea 3)
```
Deshabilita el Admin API en puerto 2019. Para producción, considerar habilitar solo en localhost.

### Política de Reinicio
```
restart: always
```
Caddy se reinicia automáticamente si falla, garantizando alta disponibilidad.

## Patrones de Routing Avanzados

### Dominio Comodín
Para capturar múltiples subdominios:
```
*.luispicado.com {
  reverse_proxy {http.request.host} ...
}
```

### Reescritura de Rutas
```
example.com/api {
  reverse_proxy backend:3000
  uri strip_prefix /api
}
```

### Middleware Personalizado
```
example.com {
  header X-Custom-Header "value"
  reverse_proxy backend:3000
}
```

## Monitoreo y Debugging

### Logs de Caddy
```bash
docker logs caddy -f
```

### Validar Sintaxis del Caddyfile
```bash
docker run --rm -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile caddy:2.8 validate
```

### Test de Conectividad
```bash
# Desde container Caddy hacia backend
docker exec caddy curl http://minio:9001

# Desde máquina host (si están en mynet)
docker run --rm --network mynet caddy:2.8 curl http://minio:9001
```

## Escalabilidad y Mejores Prácticas

### Horizontal Scaling
1. **Múltiples instancias de Caddy**: Usar load balancer (nginx, HAProxy)
2. **Estado compartido**: Usar `caddy_config` en volumen compartido (NFS, etc.)

### Gestión de Certificados
- En producción, configurar storage externo para certificados (S3, B2)
- Implementar Caddy Cluster para sincronizar certs entre múltiples instancias

### Rate Limiting
```
example.com {
  rate_limit * 100/1m
  reverse_proxy backend:3000
}
```

### Compresión
Caddy comprime automáticamente respuestas (gzip, brotli) - no requiere configuración

### Caching
```
example.com {
  header Cache-Control "max-age=3600, public"
  file_server
}
```

## Troubleshooting

### "Connection refused" a backend
- Verificar que el container backend está corriendo: `docker ps`
- Verificar puerto correcto en Caddyfile: `reverse_proxy container:puerto`
- Verificar que ambos containers están en la red `mynet`

### Certificados TLS no se generan
- Verificar acceso a internet desde Caddy
- Verificar que DNS resuelve el dominio
- Verificar puertos 80 y 443 abiertos

### 502 Bad Gateway
- Backend no respondiendo
- Port mismatch entre Caddyfile y backend
- Backend requiere headers específicos

### Rendimiento lento
- Revisar logs: `docker logs caddy`
- Verificar conexión de red entre containers
- Aumentar recursos asignados al container

## Referencias

- [Documentación Caddy](https://caddyserver.com/docs)
- [Caddyfile Directives](https://caddyserver.com/docs/caddyfile/directives)
- [Reverse Proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Docker Networking](https://docs.docker.com/network/)

# Guía de Configuración del Stack Caddy

Documento técnico para configurar e implementar el reverse proxy centralizado con Caddy. Cubre configuración de docker-compose, Caddyfile, y activos estáticos.

## Índice
1. [docker-compose.yml](#docker-composeyml)
2. [Caddyfile](#caddyfile)
3. [index.html](#indexhtml)
4. [Setup Inicial](#setup-inicial)
5. [Validación y Testing](#validación-y-testing)
6. [Deployment](#deployment)

---

## docker-compose.yml

### Estructura General

```yaml
version: "3.9"

networks:
  mynet:
    external: true

services:
  caddy:
    image: caddy:2.8
    container_name: caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./html:/usr/share/caddy/html
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - mynet

volumes:
  caddy_data:
  caddy_config:
```

### Desglose de Configuración

#### 1. **Versión y Especificación**

```yaml
version: "3.9"
```

- **3.9**: Versión recomendada de Docker Compose (compatible con Docker 20.10+)
- Soporta sintaxis moderna y características avanzadas de networking
- Recomendación: Usar 3.9 o superior para compatibilidad con volumenes nombrados y redes externas

#### 2. **Networks - Red Personalizada**

```yaml
networks:
  mynet:
    external: true
```

**Propósito**: Define una red bridge que conecta múltiples contenedores Docker sin acceso directo al host.

**¿Por qué external: true?**
- Permite que múltiples docker-compose.yml (en diferentes directorios) se conecten a la misma red
- Facilita la comunicación entre servicios en diferentes docker-compose
- Ejemplo: Si tienes Caddy en `/web` y MinIO en `/minio`, ambos pueden estar en `mynet`

**Crear la red antes de iniciar servicios**:
```bash
docker network create mynet
```

**Verificar que existe**:
```bash
docker network ls | grep mynet
```

**Inspeccionar la red**:
```bash
docker network inspect mynet
```

#### 3. **Service: Caddy**

##### 3.1 - Image y Container

```yaml
image: caddy:2.8
container_name: caddy
```

- **Image**: `caddy:2.8` - Versión estable recomendada (2.8.x es LTS)
- **container_name**: Debe ser único en el host. Usado para DNS dentro de `mynet`

**Considerar alternativas**:
```yaml
# Usar última versión (riesgoso en producción)
image: caddy:latest

# Versión específica (más control)
image: caddy:2.8.4

# Con plugins (construir imagen personalizada)
# Requiere Dockerfile custom
```

##### 3.2 - Política de Reinicio

```yaml
restart: always
```

**Opciones disponibles**:
- `no`: No reinicia automáticamente
- `always`: Reinicia siempre (incluso si se detiene manualmente)
- `unless-stopped`: Reinicia a menos que se detuviera explícitamente
- `on-failure`: Reinicia solo en caso de error (con max-retries)

**Recomendación para producción**:
```yaml
restart: unless-stopped
```

##### 3.3 - Puertos

```yaml
ports:
  - "80:80"      # Host:Container
  - "443:443"
```

**Mapeo de puertos**:
- `80:80`: Tráfico HTTP
- `443:443`: Tráfico HTTPS (TLS)

**En producción**:
```yaml
ports:
  - "127.0.0.1:80:80"    # Solo localhost (seguridad)
  - "127.0.0.1:443:443"
```

Luego usar un load balancer (nginx) en el host para acceso público.

**Puertos alternativos** (si 80/443 están ocupados):
```yaml
ports:
  - "8080:80"
  - "8443:443"
```

Actualizar Caddyfile:
```
:8080 {
  root * /usr/share/caddy/html
  file_server
}
```

##### 3.4 - Volúmenes

```yaml
volumes:
  - ./Caddyfile:/etc/caddy/Caddyfile:ro
  - ./html:/usr/share/caddy/html
  - caddy_data:/data
  - caddy_config:/config
```

**Análisis de cada volumen**:

| Volumen | Tipo | Propósito | Permisos |
|---------|------|----------|----------|
| `./Caddyfile` | Bind | Configuración del reverse proxy | `:ro` (read-only) |
| `./html` | Bind | Contenido estático (landing page) | RW (lectura/escritura) |
| `caddy_data` | Named | Certificados TLS, cache | RW (gestionado por Docker) |
| `caddy_config` | Named | Configuración persistente de Caddy | RW (gestionado por Docker) |

**Volúmenes Bind** (Bind Mounts):
- Mapean rutas del host al contenedor
- Permiten editar archivos directamente en el host
- Cambios se reflejan inmediatamente en el contenedor

```bash
# Verificar que archivos existen
ls -la ./Caddyfile
ls -la ./html/index.html

# Editar y el cambio es inmediato (si no es read-only)
echo "Nueva config" >> ./Caddyfile
# Caddy NO recargará automáticamente - requiere reload manual
docker exec caddy caddy reload -c /etc/caddy/Caddyfile
```

**Volúmenes Nombrados** (Named Volumes):
- Gestionados completamente por Docker
- Persistencia entre reinicios
- Perfecto para datos que no necesitan edición manual

```bash
# Listar volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect web_caddy_data

# Respaldar volumen
docker run --rm -v web_caddy_data:/data -v $(pwd):/backup alpine tar czf /backup/caddy_data.tar.gz /data

# Restaurar volumen
docker run --rm -v web_caddy_data:/data -v $(pwd):/backup alpine tar xzf /backup/caddy_data.tar.gz -C /
```

**Configuración recomendada para producción**:
```yaml
volumes:
  - ./Caddyfile:/etc/caddy/Caddyfile:ro
  - ./html:/usr/share/caddy/html:ro      # También read-only
  - caddy_data:/data
  - caddy_config:/config
  - /etc/letsencrypt:/etc/letsencrypt    # Compartir certs con host
```

##### 3.5 - Networks

```yaml
networks:
  - mynet
```

Conecta el contenedor `caddy` a la red `mynet`, permitiendo:
- Resolver DNS de otros contenedores: `minio:9001`, `sftpgo:51500`
- Comunicación aislada del host
- Service discovery automático

##### 3.6 - Variables de Entorno (Opcional)

Agregar si necesitas configuración dinámica:

```yaml
environment:
  - TZ=America/Mexico_City
  - CADDY_ADMIN=0.0.0.0:2019
```

```bash
# Luego, acceder al Admin API desde el host
docker exec caddy curl http://localhost:2019/config/
```

#### 4. **Volúmenes Nombrados (Nivel Raíz)**

```yaml
volumes:
  caddy_data:
  caddy_config:
```

Define volúmenes nombrados para persistencia. Caddy los crea automáticamente en primera ejecución.

**Ubicación en disco** (en la mayoría de Linux):
```
/var/lib/docker/volumes/web_caddy_data/_data
/var/lib/docker/volumes/web_caddy_config/_data
```

---

## Caddyfile

El Caddyfile es la configuración declarativa del reverse proxy. Define cómo Caddy enruta tráfico.

### Sintaxis General

```
# Comentarios comienzan con #

# Bloque global (opcional)
{
  directive value
}

# Bloque de sitio
site.com {
  directive value
  directive value
}

# Bloque con puerto
:8080 {
  directive value
}
```

### Análisis del Caddyfile Actual

```
{
  # Opcional: logging global
  admin off
}
```

**`admin off`**: Deshabilita el Admin API (puerto 2019)

**Alternativas**:
```
{
  admin localhost:2019        # Solo desde localhost
  admin 0.0.0.0:2019         # Cualquier interfaz (riesgoso)
  log {
    output stdout
    level info
  }
}
```

### Bloque 1: Contenido Estático (Default)

```
:80 {
  root * /usr/share/caddy/html
  file_server
}
```

**Análisis**:
- `:80` - Escucha en puerto 80 (HTTP)
- `root * /usr/share/caddy/html` - Directorio raíz de archivos
  - `*` = aplica a todos los dominios/rutas que no tengan bloque específico
  - `/usr/share/caddy/html` = ruta dentro del contenedor (mapeada desde `./html` del host)
- `file_server` - Sirve archivos estáticos

**Comportamiento**:
```
GET http://example.com/          → /usr/share/caddy/html/index.html
GET http://example.com/about     → /usr/share/caddy/html/about (si existe)
GET http://example.com/style.css → /usr/share/caddy/html/style.css
```

**Extensión con directives adicionales**:

```
:80 {
  root * /usr/share/caddy/html
  
  # Servir index.html para directorios
  try_files {path} {path}/ /index.html
  
  # Compresión (automática pero explícita)
  encode gzip
  
  # Caching en cliente
  header Cache-Control "max-age=3600, public"
  
  # Headers de seguridad
  header X-Frame-Options "SAMEORIGIN"
  header X-Content-Type-Options "nosniff"
  
  file_server
}
```

### Bloque 2-6: Reverse Proxy a Servicios

```
sftp.luispicado.com {
  reverse_proxy sftpgo:51500
}
```

**Análisis**:
- `sftp.luispicado.com` - Solo este dominio
- `reverse_proxy sftpgo:51500` - Proxy a container `sftpgo` puerto 51500

**Flujo**:
```
1. Cliente: GET https://sftp.luispicado.com/dashboard
2. Caddy valida Host header = "sftp.luispicado.com"
3. Caddy conecta a container "sftpgo:51500" (resolve vía DNS de red mynet)
4. Caddy transmite: GET /dashboard
5. SFTPGo responde con HTML
6. Caddy añade headers de proxy (X-Forwarded-*)
7. Caddy retorna respuesta al cliente
```

#### Reverse Proxy Avanzado: MinIO API

```
minio-api.luispicado.com {
  reverse_proxy minio:9000
}
```

**Consideración**: MinIO API requiere URL paths específicas (`/minio/...`). Por defecto, Caddy preserva paths, así que funciona correctamente.

**Si necesitaras reescribir paths**:
```
minio-api.luispicado.com {
  uri strip_prefix /v1
  reverse_proxy minio:9000
}
```

#### MinIO Console

```
minio.luispicado.com {
  reverse_proxy minio:9001
}
```

La consola web de MinIO escucha en puerto 9001 (separado de la API).

#### Apache File Server

```
data.luispicado.com {
  reverse_proxy apache-fileserver:80
}
```

**Nota**: El puerto 80 dentro del contenedor, mapeado a través de la red `mynet`.

#### Spark Master UI

```
spark.luispicado.com {
  reverse_proxy spark:8080
}
```

Spark Master UI escucha en puerto 8080 por defecto.

### Configuración Completa Recomendada (Producción)

```
{
  admin off
  
  # Logging
  log {
    output stdout
    format json
    level info
  }
  
  # TLS Global
  auto_https on
  ocsp_stapling off  # Si es problema de performance
}

# HTTPS redirigido automáticamente
http://* {
  redir https://{host}{uri} permanent
}

# Landing page
:80 {
  root * /usr/share/caddy/html
  
  try_files {path} {path}/ /index.html
  encode gzip
  header Cache-Control "public, max-age=3600"
  header X-Frame-Options "SAMEORIGIN"
  header X-Content-Type-Options "nosniff"
  
  file_server
}

# SFTPGo
sftp.luispicado.com {
  reverse_proxy sftpgo:51500 {
    header_up X-Forwarded-Port {http.request.port}
    header_up X-Real-IP {http.client_ip}
  }
  
  encode gzip
}

# MinIO API
minio-api.luispicado.com {
  reverse_proxy minio:9000 {
    header_up Host {upstream_hostport}
    header_up X-Amz-Date {now.http_date}
  }
}

# MinIO Console
minio.luispicado.com {
  reverse_proxy minio:9001 {
    header_up Host {upstream_hostport}
  }
}

# Apache File Server
data.luispicado.com {
  reverse_proxy apache-fileserver:80 {
    header_up X-Forwarded-Proto https
    header_up X-Forwarded-Host {http.request.host}
  }
  
  # Caching para downloads
  header Cache-Control "public, max-age=86400"
}

# Spark Master UI
spark.luispicado.com {
  reverse_proxy spark:8080 {
    header_up Host localhost:8080
  }
}
```

### Headers de Proxy Inverso (Best Practices)

**Headers que Caddy añade automáticamente**:
- `X-Forwarded-For`: IP del cliente
- `X-Forwarded-Proto`: http o https
- `X-Forwarded-Host`: Dominio original
- `X-Forwarded-Port`: Puerto original

**Agregar headers personalizados**:
```
example.com {
  header_up X-Custom-Header "value"
  header_down X-Internal-Debug "removed"
  reverse_proxy backend:3000
}
```

- `header_up`: Headers enviados al backend
- `header_down`: Headers enviados al cliente

---

## index.html

### Estructura Actual

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Bienvenido al Mundo de los Microservicios</title>
  <style>
    /* Estilos inline */
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 Bienvenido</h1>
  </div>
  <footer>
    Julio, 2026
  </footer>
</body>
</html>
```

### Mejora Recomendada para Producción

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Landing page del stack de microservicios">
  <meta name="theme-color" content="#2a5298">
  
  <title>Microservicios - Stack Caddy</title>
  
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #1e3c72, #2a5298);
      color: #fff;
      text-align: center;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    
    .container {
      max-width: 800px;
      background: rgba(0, 0, 0, 0.3);
      padding: 60px 40px;
      border-radius: 10px;
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    h1 {
      font-size: 2.5rem;
      margin-bottom: 20px;
      font-weight: 700;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    p {
      font-size: 1.1rem;
      line-height: 1.6;
      margin-bottom: 30px;
      color: #e0e0e0;
    }
    
    .services {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin: 40px 0;
    }
    
    .service {
      background: rgba(255, 255, 255, 0.1);
      padding: 20px;
      border-radius: 8px;
      transition: transform 0.3s, background 0.3s;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .service:hover {
      transform: translateY(-5px);
      background: rgba(255, 255, 255, 0.15);
    }
    
    .service h3 {
      margin-bottom: 10px;
      font-size: 1.2rem;
    }
    
    a {
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      border-bottom: 2px solid #2a5298;
      transition: border-color 0.3s;
    }
    
    a:hover {
      border-bottom-color: #fff;
    }
    
    footer {
      margin-top: 60px;
      font-size: 0.9rem;
      color: #aaa;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding-top: 20px;
    }
    
    .status {
      display: inline-block;
      width: 10px;
      height: 10px;
      background: #4ade80;
      border-radius: 50%;
      margin-right: 5px;
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 Bienvenido al Stack de Microservicios</h1>
    
    <p>Servidor centralizado con <strong>Caddy</strong> como reverse proxy.</p>
    
    <div class="services">
      <div class="service">
        <h3>📤 SFTPGo</h3>
        <p><a href="https://sftp.luispicado.com" target="_blank" rel="noopener">Gestor SFTP</a></p>
      </div>
      
      <div class="service">
        <h3>📦 MinIO</h3>
        <p><a href="https://minio.luispicado.com" target="_blank" rel="noopener">Console</a> | 
           <a href="https://minio-api.luispicado.com" target="_blank" rel="noopener">API</a></p>
      </div>
      
      <div class="service">
        <h3>📊 Spark</h3>
        <p><a href="https://spark.luispicado.com" target="_blank" rel="noopener">Master UI</a></p>
      </div>
      
      <div class="service">
        <h3>📁 Data</h3>
        <p><a href="https://data.luispicado.com" target="_blank" rel="noopener">File Server</a></p>
      </div>
    </div>
    
    <footer>
      <span class="status"></span> Stack activo - Agosto 2026
    </footer>
  </div>
  
  <script>
    // Verificar disponibilidad de servicios (opcional)
    const services = [
      { name: 'SFTPGo', url: 'https://sftp.luispicado.com' },
      { name: 'MinIO', url: 'https://minio.luispicado.com' },
      { name: 'Spark', url: 'https://spark.luispicado.com' }
    ];
    
    services.forEach(service => {
      fetch(service.url, { method: 'HEAD', mode: 'no-cors' })
        .then(() => console.log(`✓ ${service.name} disponible`))
        .catch(() => console.warn(`✗ ${service.name} no disponible`));
    });
  </script>
</body>
</html>
```

### Cambios Clave

| Mejora | Propósito |
|--------|----------|
| `viewport` meta | Responsive en móviles |
| `description` meta | SEO |
| Flexbox/Grid | Layout flexible |
| Backdrop filter | Efecto glassmorphism |
| Grid de servicios | Navegar fácilmente a backends |
| Links a servicios | Acceso directo a cada UI |
| Script JS | Verificar disponibilidad (opcional) |

### Ubicación del Archivo

```
c:\Users\luisp\windows-code\
├── web/
│   ├── docker-compose-caddy.yml
│   ├── Caddyfile
│   ├── html/
│   │   └── index.html           ← Este archivo
│   ├── README.md
│   └── config.md
```

**Nota**: El volumen `./html:/usr/share/caddy/html` mapea la carpeta `html/` del host al contenedor.

---

## Setup Inicial

### Paso 1: Crear la Red Docker

```bash
docker network create mynet
```

### Paso 2: Crear Estructura de Carpetas

```bash
cd /path/to/web

# Crear carpeta para contenido estático
mkdir -p html

# Crear Caddyfile si no existe
touch Caddyfile

# Crear docker-compose-caddy.yml si no existe
touch docker-compose-caddy.yml
```

### Paso 3: Copiar Configuración

Asegurar que estos archivos están en su lugar:

```
web/
├── docker-compose-caddy.yml    ← Debe existir
├── Caddyfile                   ← Debe existir
└── html/
    └── index.html              ← Debe existir
```

### Paso 4: Iniciar Caddy

```bash
cd web

# Iniciar en background
docker-compose -f docker-compose-caddy.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose-caddy.yml logs -f caddy

# Detener
docker-compose -f docker-compose-caddy.yml down
```

### Paso 5: Verificar

```bash
# Verificar que está corriendo
docker ps | grep caddy

# Test HTTP
curl http://localhost/

# Test de conexión a backend
docker exec caddy curl http://minio:9001
```

---

## Validación y Testing

### 1. Validar Sintaxis del Caddyfile

```bash
docker run --rm -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile caddy:2.8 validate
```

**Output esperado**:
```
Valid configuration
```

### 2. Verificar Logs

```bash
docker-compose -f docker-compose-caddy.yml logs caddy

# Con follow (-f)
docker-compose -f docker-compose-caddy.yml logs -f caddy

# Últimas 50 líneas
docker-compose -f docker-compose-caddy.yml logs --tail 50 caddy
```

### 3. Test de Conectividad Entre Contenedores

```bash
# Desde Caddy hacia MinIO
docker exec caddy curl -I http://minio:9001/

# Desde Caddy hacia SFTPGo
docker exec caddy curl -I http://sftpgo:51500/

# Si los servicios están en mynet, resolución de DNS funciona automáticamente
```

### 4. Test de Reverse Proxy

```bash
# Desde máquina host
curl -H "Host: minio.luispicado.com" http://localhost/

# Si falla, revisar si el request llega a Caddy
docker exec caddy tail /var/log/caddy/error.log
```

### 5. Test de TLS/HTTPS

```bash
# Verificar certificados en volumen
docker volume inspect web_caddy_data

# Dentro del container
docker exec caddy ls -la /data/caddy/certificates/
```

### 6. Health Check Manual

```bash
#!/bin/bash
set -e

echo "Testing HTTP..."
curl -s http://localhost/ > /dev/null && echo "✓ HTTP OK"

echo "Testing Caddy connectivity..."
docker exec caddy curl -s http://minio:9001 > /dev/null && echo "✓ MinIO reachable"

echo "All tests passed!"
```

---

## Deployment

### Ambiente de Desarrollo

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose-caddy.yml logs -f

# Editar Caddyfile y recargar (sin restart)
vim Caddyfile
docker exec caddy caddy reload -c /etc/caddy/Caddyfile
```

### Ambiente de Staging

```yaml
# docker-compose-caddy.yml
services:
  caddy:
    image: caddy:2.8
    restart: unless-stopped
    environment:
      - CADDY_EMAIL=admin@luispicado.com   # Para Let's Encrypt
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./html:/usr/share/caddy/html
      - caddy_data:/data
      - caddy_config:/config
      - /var/log/caddy:/var/log/caddy      # Logs persistentes
```

### Ambiente de Producción

```yaml
version: "3.9"

networks:
  mynet:
    external: true

services:
  caddy:
    image: caddy:2.8
    container_name: caddy
    restart: unless-stopped
    
    # Limitar recursos
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
    
    ports:
      # Solo en interfaces específicas
      - "127.0.0.1:80:80"
      - "127.0.0.1:443:443"
    
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./html:/usr/share/caddy/html:ro
      - caddy_data:/data
      - caddy_config:/config
      - /var/log/caddy:/var/log/caddy
    
    environment:
      - CADDY_EMAIL=admin@luispicado.com
      - TZ=America/Mexico_City
    
    networks:
      - mynet
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  caddy_data:
  caddy_config:
```

### Backup y Restore

**Respaldar certificados**:
```bash
docker run --rm -v web_caddy_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/caddy_data.tar.gz /data
```

**Restaurar certificados**:
```bash
docker volume create web_caddy_data
docker run --rm -v web_caddy_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/caddy_data.tar.gz -C /
```

### Monitoring (Prometheus/Grafana)

```
{
  admin 127.0.0.1:2019
  
  log {
    output stdout
    format json
    level info
  }
  
  # Metrics endpoint
  metrics /metrics
}

metrics.localhost:2019 {
  reverse_proxy localhost:2019
}
```

---

## Checklist de Verificación Final

- [ ] Red `mynet` creada: `docker network create mynet`
- [ ] Caddyfile válido: `docker run --rm -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile caddy:2.8 validate`
- [ ] Carpeta `html/` existe con `index.html`
- [ ] docker-compose-caddy.yml tiene versión 3.9+
- [ ] Todos los servicios backend están en la red `mynet`
- [ ] Puertos 80 y 443 disponibles en host
- [ ] Contenedor Caddy inicia: `docker-compose -f docker-compose-caddy.yml up`
- [ ] Página estática accesible: `curl http://localhost/`
- [ ] Reverse proxy funciona: `docker exec caddy curl http://minio:9001`
- [ ] Certificados generados (si HTTPS): `docker exec caddy ls /data/caddy/certificates/`

---

## Referencias y Recursos

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Caddyfile Syntax](https://caddyserver.com/docs/caddyfile/syntax)
- [Reverse Proxy Directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/compose-file-v3/)
- [Docker Networking Best Practices](https://docs.docker.com/network/)

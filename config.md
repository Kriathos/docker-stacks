# ⚙️ Configuración Global del Proyecto

Documento de referencia para la configuración, variables de entorno y parámetros globales del laboratorio.

---

## 📋 Tabla de Contenidos

1. [Red Docker](#-red-docker-mynet)
2. [Rutas Windows](#-rutas-y-montajes-windows)
3. [Hosts Locales](#-hosts-y-nombres-de-dominio)
4. [Variables de Entorno](#-variables-de-entorno)
5. [Docker Compose](#-docker-compose)
6. [Seguridad](#-seguridad-y-producción)

---

## 🌉 Red Docker (mynet)

### Crear la Red

```powershell
# Crear red bridge externa (OBLIGATORIO)
docker network create mynet --driver bridge

# Verificar creación
docker network ls | findstr mynet

# Ver detalles
docker network inspect mynet
```

### Especificaciones de Red

| Propiedad | Valor | Nota |
|-----------|-------|------|
| **Driver** | bridge | Aislamiento del host |
| **Scope** | local | Máquina local |
| **Subnet** | 172.18.0.0/16 | Por defecto (modificable) |
| **Gateway** | 172.18.0.1 | Por defecto |
| **Internal** | false | Acceso a internet |
| **External** | true | Compartida entre compose files |

### DNS y Service Discovery

La red `mynet` proporciona DNS automático para service discovery:

```powershell
# Dentro de un contenedor, todos estos funcionan:
curl http://caddy:80
curl http://sqlserver:1433
curl http://minio:9000
curl http://kafka1:9092
curl http://spark:7077
curl http://jupyter:8888

# Los nombres se resuelven automáticamente
# NO requiere configuración adicional
```

### Troubleshooting de Red

```powershell
# Si los servicios no se comunican:

# 1. Verificar que ambos están en mynet
docker network inspect mynet | grep -A 20 "Containers"

# 2. Verificar conectividad
docker run --rm --network mynet alpine ping caddy
docker run --rm --network mynet alpine curl http://minio:9000

# 3. Ver logs del contenedor
docker logs <container_name>

# 4. Última opción: recrear red
docker network rm mynet
docker network create mynet --driver bridge
```

---

## 🖥️ Rutas y Montajes Windows

### Estructura de Directorios

```
C:\Users\<usuario>\windows-code\
│
├── web/                          # Stack Caddy
│   ├── docker-compose-caddy.yml
│   ├── Caddyfile
│   ├── html/
│   ├── README.md
│   └── config.md
│
├── storage/                       # Stack Storage
│   ├── docker-compose-storage.yml
│   ├── docker-compose.yml
│   ├── README.md
│   ├── config.md
│   └── setup.md
│
├── kafka-kraft/                   # Kafka KRaft
│   ├── docker-compose.yml
│   ├── README.md
│   ├── config.md
│   └── ...
│
├── kafka-zookeeper/               # Kafka + Zookeeper
│   ├── docker-compose.yml
│   ├── README.md
│   ├── config.md
│   └── ...
│
├── databricks/                    # Stack Databricks
│   ├── docker-compose.yml
│   ├── README.md
│   ├── config.md
│   ├── setup.md
│   ├── dags/                      # Airflow DAGs
│   └── notebooks/                 # Jupyter notebooks
│
├── README.md                      # 📖 Documento principal
├── SETUP.md                       # 🚀 Guía instalación
├── ARCHITECTURE.md                # 🏗️ Arquitectura
├── config.md                      # ⚙️ Este archivo
├── credenciales.md                # 🔐 Credenciales centralizadas
└── .gitignore                     # Git exclusiones
```

### Volúmenes en Windows

Algunos stacks usan rutas locales Windows para persistencia.

#### Storage Stack

```yaml
# docker-compose-storage.yml
volumes:
  # SFTP Server
  - "F:/sftp:/srv/sftpgo"                    # Home directory SFTP
  - "F:/sftpgo-data:/var/lib/sftpgo"         # Database SFTPGo
  
  # MinIO
  - "F:/minio-data:/data"                    # Data MinIO
  
  # Apache File Server
  - "F:/apache-fileserver:/usr/local/apache2/htdocs/"  # HTML files
```

### Cambiar Rutas

Si no tienes acceso a `F:/` o prefieres otras rutas:

**Opción 1: Usar `C:/` (Requiere permisos)**

```yaml
# En storage/docker-compose-storage.yml

volumes:
  - "C:/data/sftp:/srv/sftpgo"
  - "C:/data/sftpgo:/var/lib/sftpgo"
  - "C:/data/minio:/data"
  - "C:/data/apache:/usr/local/apache2/htdocs/"
```

**Opción 2: Usar volúmenes nombrados (Recomendado)**

```yaml
# En storage/docker-compose-storage.yml

volumes:
  sftp_data:
  sftpgo_config:
  minio_data:
  apache_html:

services:
  sftpgo:
    volumes:
      - sftp_data:/srv/sftpgo
      - sftpgo_config:/var/lib/sftpgo
  
  minio:
    volumes:
      - minio_data:/data
  
  file-server:
    volumes:
      - apache_html:/usr/local/apache2/htdocs/
```

### Crear Directorios Requeridos

```powershell
# Si usas rutas Windows, crea las carpetas primero:

New-Item -Path "F:\sftp" -ItemType Directory -Force
New-Item -Path "F:\sftpgo-data" -ItemType Directory -Force
New-Item -Path "F:\minio-data" -ItemType Directory -Force
New-Item -Path "F:\apache-fileserver" -ItemType Directory -Force

# O verifica que existen:
Test-Path "F:\sftp"
Test-Path "F:\sftpgo-data"
Test-Path "F:\minio-data"
Test-Path "F:\apache-fileserver"
```

---

## 📍 Hosts y Nombres de Dominio

### Configurar Hosts Locales

Edita `C:\Windows\System32\drivers\etc\hosts` como administrador:

```powershell
# Abrir con permisos
notepad C:\Windows\System32\drivers\etc\hosts
```

Agrega estas líneas:

```hosts
# ================================================
# Laboratorio de Infraestructura de Datos
# ================================================

# Proxy Central (Caddy)
127.0.0.1 localhost
127.0.0.1 landing.local

# Storage Stack
127.0.0.1 sftp.local
127.0.0.1 minio.local
127.0.0.1 minio-api.local
127.0.0.1 data.local
127.0.0.1 spark.local

# Kafka Stack
127.0.0.1 kraft-ui.local
127.0.0.1 kraft-api.local
127.0.0.1 zoo-ui.local
127.0.0.1 zoo-api.local

# Databricks Stack
127.0.0.1 jupyter.local
127.0.0.1 mlflow.local
127.0.0.1 airflow.local
127.0.0.1 vault.local

# ================================================
```

### Verificar Resolución

```powershell
# Test DNS local
nslookup minio.local
nslookup jupyter.local

# Test con curl
curl http://jupyter.local:8888
curl http://minio.local:9001
```

### Dominios Personalizados

Si prefieres usar tus propios domainios en lugar de `.local`:

**1. Edita el archivo hosts:**
```hosts
127.0.0.1 minio.tudominio.com
127.0.0.1 jupyter.tudominio.com
```

**2. Actualiza el Caddyfile:**
```
minio.tudominio.com {
  reverse_proxy minio:9001
}

jupyter.tudominio.com {
  reverse_proxy jupyter:8888
}
```

**3. Reinicia Caddy:**
```powershell
cd .\web
docker-compose -f docker-compose-caddy.yml down
docker-compose -f docker-compose-caddy.yml up -d
```

---

## 🔧 Variables de Entorno

### Variables Globales

Pueden definirse en `.env` en la raíz (si es necesario):

```bash
# .env (opcional)
COMPOSE_PROJECT_NAME=lab
DOCKER_DEFAULT_PLATFORM=linux/amd64
DOCKER_NETWORK=mynet
```

### Por Stack

Cada `docker-compose-*.yml` define sus propias variables:

#### Storage Stack

```yaml
environment:
  SA_PASSWORD: "Generar"              # SQL Server
  DB2INST1_PASSWORD: "Generar"        # DB2
  MINIO_ROOT_PASSWORD: "Generar"      # MinIO
  LICENSE: "accept"                   # DB2 license
  ACCEPT_EULA: "Y"                    # SQL Server
```

#### Kafka Stack (KRaft)

```yaml
environment:
  KAFKA_NODE_ID: 1
  KAFKA_PROCESS_ROLES: "broker,controller"
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
  KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka1:29093,2@kafka2:29093,3@kafka3:29093"
```

#### Databricks Stack

```yaml
environment:
  AIRFLOW__CORE__FERNET_KEY: "Generar"
  AIRFLOW__CORE__LOAD_EXAMPLES: "false"
  AIRFLOW__WEBSERVER__EXPOSE_CONFIG: "true"
  POSTGRES_PASSWORD: "Generar"
```

---

## 🐳 Docker Compose

### Comandos Básicos

```powershell
# Navegar al directorio del stack
cd .\web

# Iniciar servicios (background)
docker-compose -f docker-compose-caddy.yml up -d

# Detener servicios
docker-compose -f docker-compose-caddy.yml down

# Ver estado
docker-compose -f docker-compose-caddy.yml ps

# Ver logs
docker-compose -f docker-compose-caddy.yml logs -f

# Logs de servicio específico
docker-compose -f docker-compose-caddy.yml logs -f caddy

# Ejecutar comando en contenedor
docker-compose -f docker-compose-caddy.yml exec caddy ls -la /etc/caddy

# Eliminar volúmenes (⚠️ borra datos)
docker-compose -f docker-compose-caddy.yml down -v
```

### Archivos Docker Compose

Cada stack tiene un archivo específico:

| Stack | Archivo |
|-------|---------|
| **Web (Caddy)** | `web/docker-compose-caddy.yml` |
| **Storage** | `storage/docker-compose-storage.yml` |
| **Kafka KRaft** | `kafka-kraft/docker-compose.yml` |
| **Kafka Zookeeper** | `kafka-zookeeper/docker-compose.yml` |
| **Databricks** | `databricks/docker-compose.yml` |

### Sintaxis `-f` (Force compose file)

```powershell
# Forma correcta (especificar archivo)
docker-compose -f storage/docker-compose-storage.yml up -d

# ❌ NO hacer esto (busca docker-compose.yml por defecto)
cd storage
docker-compose up -d  # Busca docker-compose.yml, si no existe falla
```

---

## 🔐 Seguridad y Producción

### ⚠️ Credenciales en Laboratorio

Este proyecto contiene credenciales hardcoded en `credenciales.md` y `docker-compose-*.yml`.

**Está bien para:**
- ✅ Desarrollo local
- ✅ Laboratorio aislado
- ✅ Experimentación
- ✅ Educación

**NO está bien para:**
- ❌ Producción
- ❌ Datos reales
- ❌ Equipos compartidos
- ❌ Servidor público

### Checklist Seguridad

Antes de usar datos reales:

- [ ] Cambiar todas las contraseñas en `credenciales.md`
- [ ] Usar variables de entorno o `.env` files
- [ ] Implementar Vault para gestión de secretos
- [ ] Habilitar autenticación en Caddy (Basic Auth, OAuth)
- [ ] Usar HTTPS con certificados válidos (Let's Encrypt)
- [ ] Implementar rate limiting en Caddy
- [ ] Habilitar logging y auditoría
- [ ] Revisar permisos de archivos
- [ ] Usar redes privadas VPN
- [ ] Realizar security scan de imágenes Docker

### Ejemplo: Usar .env

```bash
# .env (agregar a .gitignore)
MINIO_PASSWORD=aMy$ecureP@ssw0rd
SQL_SERVER_PASSWORD=Secure#Pass2024
DB2_PASSWORD=DB2$ecure123
AIRFLOW_PASSWORD=Airflow@2024

POSTGRES_PASSWORD=Postgres$ecure2024
FERNET_KEY=5nRu2XvHe3mL...
```

```yaml
# docker-compose.yml
environment:
  MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
  SA_PASSWORD: ${SQL_SERVER_PASSWORD}
```

---

## 📊 Límites de Recursos

### Docker Desktop Configuración

En Docker Desktop Settings → Resources:

```
CPUs:       4-8 (recomendado 8)
Memory:     8-16 GB (recomendado 16)
Disk:       100+ GB disponible
Swap:       2 GB
```

### Por Contenedor (docker-compose)

```yaml
services:
  spark-master:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Monitoreo

```powershell
# Ver uso en tiempo real
docker stats

# Ver disco usado
docker system df

# Ver imágenes y tamaño
docker images

# Limpiar sin usar espacio
docker system prune
docker system prune -a  # Elimina imágenes no usadas
```

---

## 🔗 Puertos Expuestos

### Mapping de Puertos

| Servicio | Host | Container | Propósito |
|----------|------|-----------|----------|
| Caddy HTTP | 80 | 80 | HTTP proxy |
| Caddy HTTPS | 443 | 443 | HTTPS proxy |
| SQL Server | 1433 | 1433 | Database |
| DB2 | 50000 | 50000 | Database |
| MinIO API | 9000 | 9000 | S3 API |
| MinIO Console | 9001 | 9001 | S3 Web UI |
| SFTPGo | 2022 | 2022 | SFTP |
| Jupyter | 8888 | 8888 | Notebooks |
| Spark Master | 8080 | 8080 | Spark UI |
| Airflow | 8082 | 8082 | Airflow UI |
| MLflow | 5000 | 5000 | ML Tracking |
| Vault | 8200 | 8200 | Secrets |
| Kafka UI | 8080 | 8080 | Kafka Dashboard (KRaft) |

### Cambiar Puertos

Si un puerto está en uso, cámbialo en `docker-compose-*.yml`:

```yaml
services:
  jupyter:
    ports:
      - "8889:8888"  # Host:Container
    # Ahora acceso en localhost:8889
```

---

## 🧪 Testing y Validación

### Health Checks

```powershell
# Caddy
curl http://localhost/

# Jupyter
curl -I http://localhost:8888

# Spark Master
curl -s http://localhost:8080 | grep -i "Spark"

# SQL Server
docker-compose -f storage/docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa -Q "SELECT 1"

# MinIO
docker-compose -f storage/docker-compose-storage.yml exec minio mc --help
```

### Connectivity Test

```powershell
# Entre contenedores (desde Windows)
docker run --rm --network mynet alpine \
  sh -c "ping caddy && echo OK"

# Desde Spark a SQL Server
docker-compose -f databricks/docker-compose.yml exec spark \
  spark-shell -c "sqlserver:1433" --help
```

---

## 📖 Referencias

- [Docker Compose Docs](https://docs.docker.com/compose/compose-file/)
- [Docker Network Docs](https://docs.docker.com/network/)
- [Caddy Docs](https://caddyserver.com/docs/)
- [Kafka Docs](https://kafka.apache.org/documentation/)
- [Spark Docs](https://spark.apache.org/docs/latest/)

---

<div align="center">

[📖 Leer README](./README.md) • [🚀 Leer SETUP](./SETUP.md) • [🏗️ Ver arquitectura](./ARCHITECTURE.md)

</div>

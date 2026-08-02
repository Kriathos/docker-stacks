# 🏗️ Arquitectura Detallada del Laboratorio

Documento técnico que describe la arquitectura, componentes y patrones de integración del laboratorio.

---

## 📐 Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                        APLICACIONES CLIENTE                     │
│              (Browser, CLI Tools, Python Scripts)               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTP/HTTPS :80/:443
                               ▼
                    ┌──────────────────────┐
                    │   🌐 CADDY PROXY     │
                    │  (Reverse Proxy)     │
                    │                      │
                    │ ✓ TLS Automático     │
                    │ ✓ Enrutamiento Host  │
                    │ ✓ Load Balancing     │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┬─────────────┐
        │                      │                      │             │
        ▼                      ▼                      ▼             ▼
    ┌────────────┐      ┌──────────────┐     ┌──────────────┐  ┌────────────┐
    │ 🔬         │      │      📨     │     │      💾      │  │ 🔗 Custom │
    │ DATABRICKS │      │    KAFKA     │     │   STORAGE    │  │ ROUTES     │
    │            │      │              │     │              │  │            │
    │ • Spark    │      │ • KRaft(3)   │     │ • SQL Server │  │ • Custom   │
    │ • Jupyter  │      │ • Zookeeper  │     │ • DB2        │  │   services │
    │ • Airflow  │      │ • Debezium   │     │ • MinIO      │  │            │
    │ • MLflow   │      │ • Connect    │     │ • SFTPGo     │  └────────────┘
    │ • Vault    │      │ • PostgreSQL │     │ • Apache     │
    └────────────┘      └──────────────┘     └──────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               │ Intracommunication
                               │
                    ┌──────────▼───────────┐
                    │  🌉 DOCKER NETWORK   │
                    │  (mynet - bridge)    │
                    │                      │
                    │ • Service Discovery  │
                    │ • DNS Resolution     │
                    │ • Isolated Traffic   │
                    └──────────────────────┘
                               │
                    ┌──────────▼────────────┐
                    │  📦 PERSISTENT DATA   │
                    │                       │
                    │ • Named Volumes       │
                    │ • Bind Mounts Windows │
                    │ • Certificados TLS    │
                    └───────────────────────┘
```

---

## 🔌 Componentes Principales

### 1. Caddy Reverse Proxy (Web Stack)

**Propósito:** Gateway HTTP/HTTPS centralizado

**Características:**
- ✅ Terminación TLS automática con Let's Encrypt
- ✅ Enrutamiento basado en Host header
- ✅ Compresión automática (gzip, brotli)
- ✅ Caching inteligente
- ✅ Admin API para reload sin downtime
- ✅ Logging structured en JSON

**Configuración:**
- **Puerto host:** 80 (HTTP), 443 (HTTPS)
- **Puerto container:** 80, 443
- **Volúmenes:**
  - `./Caddyfile` → config (read-only)
  - `./html` → landing page estática
  - `caddy_data` → certificados TLS
  - `caddy_config` → config persistente

**Enrutamiento:**
```
landing.local → ./html/index.html (estático)
sftp.local → sftpgo:51500
minio.local → minio:9001 (console)
minio-api.local → minio:9000 (API S3)
data.local → apache-fileserver:80
spark.local → spark:8080
jupyter.local → jupyter:8888
mlflow.local → mlflow:5000
airflow.local → airflow-webserver:8082
vault.local → vault:8200
kraft-ui.local → kafka-ui:8080 (KRaft)
zoo-ui.local → kafka-ui:8080 (Zookeeper)
```

---

### 2. Databricks Stack (Data Processing)

**Propósito:** Análisis de datos, ML y orquestación local

**Arquitectura:**
```
┌─────────────────────────────────────────┐
│       Apache Spark Cluster              │
│  ┌────────────┐       ┌────────────┐    │
│  │   Master   │       │   Worker   │    │
│  │ :7077/8080 │◄─────►│   :8081    │    │
│  └────────────┘       └────────────┘    │
└─────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    ┌────┴────────────────────┴─────┐
    │                               │
    │  Jupyter Lab                  │
    │ (Notebooks + PySpark)         │
    │ :8888                         │
    │                               │
    └───────────────┬───────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
  MLflow         Airflow           Vault
  :5000          :8082            :8200
  
  PostgreSQL (:5432) - Metadatos y estado
```

**Componentes:**
| Servicio | Puerto | Propósito |
|----------|--------|----------|
| spark-master | 7077, 8080 | Master del cluster |
| spark-worker | 8081 | Worker de Spark |
| jupyter | 8888 | Notebooks interactivos |
| mlflow | 5000 | Tracking de experimentos |
| airflow-webserver | 8082 | UI de Airflow |
| airflow-scheduler | - | Scheduler de DAGs |
| vault | 8200 | Gestión de secretos |
| postgres | 5432 | Metadatos y persistencia |

**Casos de uso:**
- 📊 Análisis exploratorio de datos
- 🤖 Entrenamiento de modelos ML
- 🔄 Transformación ETL
- 📈 Reportes automáticos
- 🔐 Gestión de credenciales

---

### 3. Kafka Stack (Streaming & Messaging)

**Propósito:** Plataforma de eventos y mensajería

**Arquitectura (Opción KRaft - Recomendada):**
```
┌──────────────────────────────────────┐
│      Kafka Cluster (3 Brokers)       │
│  ┌──────────┬──────────┬──────────┐  │
│  │ Broker 1 │ Broker 2 │ Broker 3 │  │
│  │ :9092    │ :9093    │ :9094    │  │
│  └──────────┴──────────┴──────────┘  │
│  (Sin Zookeeper - KRaft Quorum)      │
└──────────┬───────────────────────────┘
           │
    ┌──────▼───────────┐
    │ Debezium Connect │
    │   (CDC Broker)   │
    │   :8083          │
    └──────┬───────────┘
           │
    ┌──────▼───────────┐
    │    PostgreSQL    │
    │  (Source CDC)    │
    │   :5432          │
    └──────────────────┘
```

**Arquitectura (Opción Zookeeper - Tradicional):**
```
┌──────────────────────────────────────┐
│   Zookeeper Ensemble (3 Nodes)       │
│  ┌──────────┬──────────┬──────────┐  │
│  │  Zoo 1   │  Zoo 2   │  Zoo 3   │  │
│  │ :2181    │ :2181    │ :2181    │  │
│  └──────────┴──────────┴──────────┘  │
└──────────────────────────────────────┘
           ▲
           │ Coordinación
           │
┌──────────▼───────────────────────────┐
│   Kafka Cluster (3 Brokers)          │
│  ┌──────────┬──────────┬──────────┐  │
│  │ Broker 1 │ Broker 2 │ Broker 3 │  │
│  │ :9092    │ :9093    │ :9094    │  │
│  └──────────┴──────────┴──────────┘  │
└──────────┬───────────────────────────┘
           │
    ┌──────▼───────────┐
    │ Debezium Connect │
    │   :8083          │
    └──────┬───────────┘
           │
    ┌──────▼───────────┐
    │    PostgreSQL    │
    │   :5432          │
    └──────────────────┘
```

**Componentes:**
| Servicio | Puerto | Propósito |
|----------|--------|----------|
| kafka1,2,3 | 9092-9094 | Brokers (KRaft o ZK) |
| zookeeper1-3 | 2181 | Coordinación (solo Zookeeper) |
| debezium-connect | 8083 | CDC Connectors |
| postgres-cdc | 5432 | Source de cambios |
| kafka-ui | 8080 | Dashboard (opcional) |

**Topics por defecto:**
- `postgres.public.*` - Cambios desde PostgreSQL
- `test-*` - Topics de prueba
- Personalizados según DAGs de Debezium

---

### 4. Storage Stack (Data Persistence)

**Propósito:** Almacenamiento multiformato

**Arquitectura:**
```
┌─────────────────────────────────────┐
│    Base de Datos Relacionales       │
│  ┌──────────────────────────────┐   │
│  │ SQL Server (MSSQL)           │   │
│  │ Transaccional                │   │
│  │ :1433                        │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Base de Datos Empresarial           │
│  ┌──────────────────────────────┐   │
│  │ IBM DB2                      │   │
│  │ Warehouse clásico            │   │
│  │ :50000                       │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    Object Storage                   │
│  ┌──────────────────────────────┐   │
│  │ MinIO (S3-compatible)        │   │
│  │ API:9000, Console:9001       │   │
│  │ Buckets para datos/backups   │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    File Server                      │
│  ┌──────────────────────────────┐   │
│  │ SFTPGo                       │   │
│  │ SFTP:2022, Web:51500         │   │
│  │ + Apache HTTP:80             │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Componentes:**
| Servicio | Puerto | Propósito |
|----------|--------|----------|
| sqlserver | 1433 | MSSQL transaccional |
| db2 | 50000 | IBM DB2 enterprise |
| minio | 9000, 9001 | S3-compatible object storage |
| sftpgo | 2022, 51500 | SFTP + web UI |
| apache-fileserver | 80 | Static file server |

**Volúmenes:**
- `sqlserver_data` → SQL Server data
- `db2_data` → DB2 data
- `F:/sftp` → SFTP home directory
- `F:/sftpgo-data` → SFTPGo database
- `F:/minio-data` → MinIO data
- `F:/apache-fileserver` → Static files

---

## 🔗 Patrones de Integración

### Patrón 1: Change Data Capture (CDC)

```
PostgreSQL (Kafka Stack)
        │
        │ (INSERT/UPDATE/DELETE)
        ▼
   Debezium Connect
        │
        │ (Cambios como eventos)
        ▼
   Kafka Topics
   (postgres.public.*)
        │
        │ (Consume)
        ▼
   Spark Streaming (Databricks)
        │
        │ (Procesa)
        ▼
   SQL Server / MinIO (Storage)
   (Almacena resultados)
```

**Ejemplo:** Replicación de tablas PostgreSQL → Kafka → Spark → SQL Server

---

### Patrón 2: Data Lake

```
SFTP Upload (Storage)
        │
        │ (Raw files)
        ▼
   SFTPGo Ingesta
        │
        ▼
   MinIO Bucket (raw/)
        │
        │ (Consume)
        ▼
   Spark (Databricks)
        │
        │ (Transform)
        ▼
   MinIO Bucket (processed/)
   +
   SQL Server (Catalog)
```

**Ejemplo:** Procesos ETL con Jupyter → MinIO → SQL Server

---

### Patrón 3: Machine Learning Pipeline

```
Data Source (SQL Server/MinIO)
        │
        │ (Read)
        ▼
   Jupyter Notebook (Databricks)
        │
        ├─► Feature Engineering
        │
        ├─► Model Training
        │
        └─► MLflow Tracking
                │
                │ (Registra)
                ▼
          ML Model Registry
```

**Ejemplo:** Training en Jupyter, track en MLflow, deploy modelo

---

### Patrón 4: Workflow Automation

```
Airflow DAG (Databricks)
        │
        ├─► Task 1: Extract (SQL Server)
        │
        ├─► Task 2: Transform (Spark)
        │
        └─► Task 3: Load (MinIO/Storage)
        
        Scheduled daily @ 02:00 UTC
        Retries: 3
        SLA: 1 hour
```

**Ejemplo:** ETL schedule automático con alertas

---

## 🌉 Red Docker (mynet)

### Características

- **Tipo:** Bridge network
- **Scope:** Local machine
- **Aislamiento:** Separa contenedores de host
- **DNS:** Service discovery integrado
- **IPAM:** Subnet 172.18.0.0/16 (por defecto)

### Resolución de Nombres

Dentro de la red `mynet`, los servicios se resuelven por nombre:

```powershell
# Desde Databricks → Storage
curl http://sqlserver:1433
curl http://minio:9000

# Desde Kafka → Storage  
docker exec kafka1 curl http://minio:9000

# Desde Caddy → Todos
curl http://sftpgo:51500
curl http://spark:8080
```

### Comunicación Cross-Stack

```
Databricks ◄─────► Kafka
   │                  │
   └──────┬───────────┘
          │
       Storage
```

Todos los stacks conectados a `mynet` pueden comunicarse sin configuración adicional.

---

## 💾 Persistencia de Datos

### Tipos de Volúmenes

**Named Volumes** (Gestionados por Docker):
```yaml
volumes:
  caddy_data:
  caddy_config:
  sqlserver_data:
  db2_data:
```

**Bind Mounts** (Mapeo directo Windows):
```yaml
volumes:
  - F:/sftp:/srv/sftpgo
  - F:/minio-data:/data
  - ./Caddyfile:/etc/caddy/Caddyfile:ro
```

### Estrategia de Backup

```powershell
# Backup volumes nombrados
docker run --rm \
  -v sqlserver_data:/data \
  -v C:/backups:/backup \
  alpine tar czf /backup/sqlserver_data.tar.gz /data

# Backup bind mounts (standard Windows)
robocopy F:\minio-data C:\backups\minio-data /S /E
```

---

## 🔐 Seguridad de Red

### Aislamiento

```
┌─────────────────────────────────┐
│      Host Windows               │
│   (C:\, D:\, etc.)              │
│                                 │
│  ┌───────────────────────────┐  │
│  │   Docker Network (mynet)  │  │
│  │   (Isolated Bridge)       │  │
│  │                           │  │
│  │  • Contenedores ◄────────►│  │
│  │  • No pueden escapar      │  │
│  │  • Acceso limitado host   │  │
│  │                           │  │
│  └───────────────────────────┘  │
│          ▲     ▲                │
│          │     │                │
│    Puertos expuestos            │
│   (80/443 Caddy, etc)           │
│                                 │
└─────────────────────────────────┘
```

### Políticas

- ✅ Red externa (`mynet`) - Service discovery
- ✅ No hay contenedores en `host` network (riesgoso)
- ✅ Secretos en `credenciales.md` (NO en repo production)
- ✅ Vault para gestión de secretos en Databricks

---

## 📊 Límites de Recursos

### Recomendado

```yaml
# Por contenedor heavy (Spark, Kafka)
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G

# Por contenedor light (Caddy, Jupyter)
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Monitoreo

```powershell
# Ver uso de recursos en tiempo real
docker stats

# Ver disco usado
docker system df

# Ver memoria por contenedor
docker ps -q | xargs docker inspect --format='{{.Name}} {{.HostConfig.Memory}}' | awk '{print $1, $2/1024/1024 "MB"}'
```

---

## 🔄 Ciclo de Vida

### Startup Order (Recomendado)

```
1. Docker Network (mynet)
   └─ docker network create mynet

2. Caddy (Web)
   └─ cd web && docker-compose -f docker-compose-caddy.yml up -d
   └─ Wait: ~5 sec (TLS certs generation)

3. Storage Stack
   └─ cd storage && docker-compose -f docker-compose-storage.yml up -d
   └─ Wait: ~30 sec (SQL Server, DB2 startup)

4. Kafka (KRaft o Zookeeper)
   └─ cd kafka-kraft && docker-compose up -d
   └─ Wait: ~30 sec (KRaft) o ~60 sec (ZK, brokers stabilize)

5. Databricks Stack
   └─ cd databricks && docker-compose up -d
   └─ Wait: ~30 sec (Airflow scheduler startup)
```

### Shutdown Order

```
1. Databricks   → docker-compose down
2. Kafka        → docker-compose down
3. Storage      → docker-compose -f docker-compose-storage.yml down
4. Caddy        → docker-compose -f docker-compose-caddy.yml down
```

---

## 📈 Escalabilidad

### Horizontal

```yaml
# Aumentar replicas de Kafka
kafka:
  deploy:
    replicas: 5  # De 3 a 5

# Aumentar workers de Spark
spark-worker:
  deploy:
    replicas: 3  # De 1 a 3
```

### Vertical

```yaml
# Aumentar recursos de Spark Master
spark-master:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
```

---

## 🔗 Patrones de Conectividad

### Databricks ↔ Storage

```python
# PySpark en Jupyter
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ReadSQL") \
    .getOrCreate()

# Leer desde SQL Server
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[dbo].[table_name]") \
    .option("user", "sa") \
    .option("password", "password") \
    .load()
```

### Databricks ↔ Kafka

```python
# Spark Streaming desde Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "postgres.public.table") \
    .load()
```

### Kafka ↔ Storage (Debezium)

```json
POST /connectors

{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres-cdc",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "password",
    "database.dbname": "demo",
    "database.server.name": "postgres",
    "table.include.list": "public.*"
  }
}
```

---

## 🎯 Conclusión Arquitectónica

Este laboratorio implementa una arquitectura **Lambda** simplificada:

```
        Sources (SQL, Kafka, Files)
                 │
        ┌────────┼────────┐
        │                 │
        ▼                 ▼
    Batch Lane        Speed Lane
    (Spark ETL)    (Kafka Streaming)
        │                 │
        └────────┬────────┘
                 ▼
        Serving Layer
        (SQL Server, MinIO)
```

**Beneficios:**
- ✅ Flexibilidad de procesamiento (batch + streaming)
- ✅ Escalabilidad independiente por layer
- ✅ Tolerancia a fallos
- ✅ Reutilizable para aprendizaje

---

<div align="center">

[📖 Leer README](./README.md) • [🚀 Leer SETUP](./SETUP.md) • [⚙️ Ver config](./config.md)

</div>

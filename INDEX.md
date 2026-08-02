# 📑 Índice Completo del Proyecto

Navegación rápida a toda la documentación del laboratorio de infraestructura de datos.

---

## 🎯 Inicio Rápido (5 minutos)

**¿Nuevo en el proyecto?** Comienza aquí:

1. **[README.md](./README.md)** - Visión general y características
   - Descripción del proyecto
   - Stacks disponibles
   - Quick start básico
   - Troubleshooting común

2. **[SETUP.md](./SETUP.md)** - Instalación completa (30-45 min)
   - Requisitos
   - Paso a paso detallado
   - Verificación de cada componente
   - Troubleshooting específico

---

## 🏗️ Entender la Arquitectura

### Documentación Detallada
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitectura global
  - Diagramas ASCII de alto nivel
  - Componentes principales
  - Patrones de integración
  - Flujos de datos
  - Persistencia y volúmenes
  - Seguridad de red
  - Ciclo de vida y escalabilidad

### Configuración Global
- **[config.md](./config.md)** - Configuración centralizada
  - Red Docker (mynet)
  - Rutas Windows
  - Hosts y dominios
  - Variables de entorno
  - Docker Compose
  - Seguridad y producción
  - Limites de recursos
  - Puertos expuestos

### Credenciales
- **[credenciales.md](./credenciales.md)** - Gestión de secretos
  - Databricks Stack
  - Kafka Stack (KRaft y Zookeeper)
  - Storage Stack
  - Web Stack
  - Convenciones
  - Actualizar credenciales
  - Checklist de seguridad

---

## 📚 Documentación por Stack

### 🌐 Web Stack (Caddy Proxy)
**Gateway HTTP/HTTPS centralizado**

| Documento | Propósito |
|-----------|-----------|
| [web/README.md](./web/README.md) | Descripción y uso de Caddy |
| [web/config.md](./web/config.md) | Configuración del Caddyfile |

**Servicios:** Caddy proxy, landing page estática

**Puertos:** 80 (HTTP), 443 (HTTPS)

---

### 💾 Storage Stack
**Bases de datos transaccionales, almacenamiento y archivo**

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [storage/README.md](./storage/README.md) | Descripción del stack | 5 min |
| [storage/config.md](./storage/config.md) | Configuración docker-compose | 10 min |
| [storage/setup.md](./storage/setup.md) | **Setup paso a paso** | **30 min** |

**Servicios:**
- SQL Server (MSSQL) - Base de datos transaccional
- IBM DB2 - Base de datos empresarial
- MinIO - Object storage S3-compatible
- SFTPGo - Servidor SFTP con UI web
- Apache HTTP - Servidor de archivos estáticos

**Puertos:** 1433 (SQL), 50000 (DB2), 9000-9001 (MinIO), 2022 (SFTP), 80 (Apache)

**Iniciar:**
```powershell
cd .\storage
docker-compose -f docker-compose-storage.yml up -d
```

---

### 📨 Kafka Stack (Completo)
**Plataforma de streaming y mensajería con dos arquitecturas**

#### Arquitectura General
| Documento | Propósito |
|-----------|-----------|
| [kafka/README.md](./kafka/README.md) | Descripción general de Kafka |
| [kafka/config.md](./kafka/config.md) | Configuración global de Kafka |

#### Kafka KRaft (Moderno - Recomendado)
| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [kafka-kraft/README.md](./kafka-kraft/README.md) | Descripción KRaft | 5 min |
| [kafka-kraft/config.md](./kafka-kraft/config.md) | Configuración KRaft | 10 min |
| [kafka-kraft/setup.md](./kafka-kraft/setup.md) | **Setup paso a paso** | **20-30 min** |

**Servicios:**
- Kafka Brokers (3 nodos)
- Debezium Connect (CDC)
- PostgreSQL (CDC source)
- Kafka UI (dashboard)

**Iniciar:**
```powershell
cd .\kafka-kraft
docker-compose up -d
```

#### Kafka + Zookeeper (Tradicional)
| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [kafka-zookeeper/README.md](./kafka-zookeeper/README.md) | Descripción Zookeeper | 5 min |
| [kafka-zookeeper/config.md](./kafka-zookeeper/config.md) | Configuración ZK | 10 min |
| [kafka-zookeeper/setup.md](./kafka-zookeeper/setup.md) | **Setup paso a paso** | **25-35 min** |

**Servicios:**
- Zookeeper Ensemble (3 nodos)
- Kafka Brokers (3 nodos)
- Debezium Connect (CDC)
- PostgreSQL (CDC source)
- Kafka UI (dashboard)

**Iniciar:**
```powershell
cd .\kafka-zookeeper
docker-compose up -d
```

**Comparativa:** [Leer en kafka/README.md](./kafka/README.md)

---

### 🔬 Databricks Stack
**Análisis de datos, ML y orquestación local**

| Documento | Propósito | Tiempo |
|-----------|-----------|--------|
| [databricks/README.md](./databricks/README.md) | Descripción del stack | 5 min |
| [databricks/config.md](./databricks/config.md) | Configuración de servicios | 10 min |
| [databricks/setup.md](./databricks/setup.md) | **Setup paso a paso** | **30-45 min** |

**Servicios:**
- Apache Spark (Master + Worker)
- Jupyter Lab (notebooks interactivos)
- MLflow (tracking de experimentos ML)
- Apache Airflow (orquestación de DAGs)
- HashiCorp Vault (gestión de secretos)
- PostgreSQL (metadatos)

**Puertos:** 7077/8080 (Spark), 8888 (Jupyter), 5000 (MLflow), 8082 (Airflow), 8200 (Vault), 5432 (PostgreSQL)

**Iniciar:**
```powershell
cd .\databricks
docker-compose up -d
```

**Requisito previo:** Generar Fernet Key para Airflow (ver setup.md)

---

## 🚀 Guías por Caso de Uso

### 1️⃣ "Quiero empezar desde cero"
1. Leer [README.md](./README.md) (5 min)
2. Seguir [SETUP.md](./SETUP.md) paso a paso (45 min)
3. Verificar todo funciona (10 min)
4. **¡Listo!** → Continuar explorando

### 2️⃣ "Quiero entender la arquitectura"
1. Leer [ARCHITECTURE.md](./ARCHITECTURE.md) (15 min)
2. Revisar diagramas ASCII
3. Leer patrones de integración
4. Consultar [config.md](./config.md) para detalles

### 3️⃣ "Quiero trabajar con datos"
1. Setup Storage Stack ([setup.md](./storage/setup.md)) - 30 min
2. Setup Databricks Stack ([setup.md](./databricks/setup.md)) - 30 min
3. Leer ejemplos de integración en [ARCHITECTURE.md](./ARCHITECTURE.md)
4. Crear notebooks en Jupyter
5. Consultar credenciales en [credenciales.md](./credenciales.md)

### 4️⃣ "Quiero usar streaming"
1. Elige arquitectura:
   - KRaft: Moderno, recomendado → [setup.md](./kafka-kraft/setup.md)
   - Zookeeper: Legacy, tradicional → [setup.md](./kafka-zookeeper/setup.md)
2. Setup Kafka (20-35 min)
3. Configurar CDC desde PostgreSQL
4. Consumir en Spark (Databricks)
5. Guardar en Storage

### 5️⃣ "Tengo un problema"
1. Buscar en sección "Troubleshooting":
   - [SETUP.md](./SETUP.md#-troubleshooting-del-setup)
   - [storage/setup.md](./storage/setup.md#-troubleshooting)
   - [databricks/setup.md](./databricks/setup.md#-troubleshooting)
   - [kafka-kraft/setup.md](./kafka-kraft/setup.md#-troubleshooting)
   - [kafka-zookeeper/setup.md](./kafka-zookeeper/setup.md#-troubleshooting)

2. Si no encuentra, revisar logs:
   ```powershell
   docker-compose logs -f <servicio>
   ```

3. Consultar [config.md](./config.md#-troubleshooting-de-red)

---

## 🔗 Integración Entre Stacks

### Patrón 1: CDC → Spark → Storage
```
PostgreSQL (Kafka Stack)
    ↓ CDC
Kafka Topics (postgres.*)
    ↓ Consume
Spark (Databricks)
    ↓ Process
SQL Server / MinIO (Storage)
```

**Ver:** [ARCHITECTURE.md - Patrón CDC](./ARCHITECTURE.md#patrón-1-change-data-capture-cdc)

### Patrón 2: Data Lake
```
Files (SFTP)
    ↓
MinIO Bucket (raw)
    ↓
Spark (Transform)
    ↓
MinIO Bucket (processed) + SQL Server
```

**Ver:** [ARCHITECTURE.md - Patrón Data Lake](./ARCHITECTURE.md#patrón-2-data-lake)

### Patrón 3: ML Pipeline
```
SQL Server / MinIO
    ↓
Jupyter (Feature Engineering)
    ↓
MLflow (Track)
    ↓
Model Registry
```

**Ver:** [ARCHITECTURE.md - Patrón ML](./ARCHITECTURE.md#patrón-3-machine-learning-pipeline)

### Patrón 4: Workflow Automation
```
Airflow DAG
├─ Extract (SQL Server)
├─ Transform (Spark)
└─ Load (MinIO/Storage)
```

**Ver:** [ARCHITECTURE.md - Patrón Workflow](./ARCHITECTURE.md#patrón-4-workflow-automation)

---

## 📊 Matriz de Servicios

| Servicio | Stack | Puerto | Propósito |
|----------|-------|--------|----------|
| **Caddy** | Web | 80, 443 | Reverse proxy |
| **SQL Server** | Storage | 1433 | Base de datos relacional |
| **DB2** | Storage | 50000 | Base de datos empresarial |
| **MinIO API** | Storage | 9000 | Object storage API |
| **MinIO Console** | Storage | 9001 | Object storage web UI |
| **SFTPGo** | Storage | 2022, 51500 | SFTP + web UI |
| **Apache** | Storage | 80 | File server |
| **Kafka Brokers** | Kafka | 9092-9094 | Messaging |
| **Zookeeper** | Kafka ZK | 2181 | Cluster coordination |
| **Debezium** | Kafka | 8083 | CDC platform |
| **Kafka UI** | Kafka | 8080 | Kafka dashboard |
| **PostgreSQL** | Kafka | 5432 | CDC source |
| **Spark Master** | Databricks | 7077, 8080 | Compute master |
| **Spark Worker** | Databricks | 8081 | Compute worker |
| **Jupyter** | Databricks | 8888 | Notebooks |
| **Airflow** | Databricks | 8082 | Orchestration |
| **MLflow** | Databricks | 5000 | ML tracking |
| **Vault** | Databricks | 8200 | Secrets management |
| **PostgreSQL** | Databricks | 5432 | Metadata DB |

---

## 🛠️ Comandos Rápidos

### Iniciar Todos los Stacks
```powershell
# 1. Red Docker
docker network create mynet

# 2. Caddy (Proxy)
cd web
docker-compose -f docker-compose-caddy.yml up -d

# 3. Storage
cd ..\storage
docker-compose -f docker-compose-storage.yml up -d

# 4. Kafka KRaft (o Zookeeper)
cd ..\kafka-kraft
docker-compose up -d

# 5. Databricks
cd ..\databricks
docker-compose up -d
```

### Ver Estado
```powershell
docker ps
docker network inspect mynet
```

### Detener Todo
```powershell
cd .\web && docker-compose -f docker-compose-caddy.yml down
cd ..\storage && docker-compose -f docker-compose-storage.yml down
cd ..\kafka-kraft && docker-compose down
cd ..\databricks && docker-compose down
```

### Limpiar (⚠️ Borra datos)
```powershell
# En cada carpeta:
docker-compose down -v
docker system prune -a --volumes
```

---

## ✅ Checklist de Instalación

- [ ] Docker Desktop instalado
- [ ] WSL2 habilitado
- [ ] Red `mynet` creada
- [ ] Archivo hosts configurado (opcional)
- [ ] Credenciales actualizadas (opcional)
- [ ] Caddy iniciado
- [ ] Storage iniciado
- [ ] Kafka iniciado
- [ ] Databricks iniciado
- [ ] Todos los contenedores corriendo
- [ ] Interfaces web accesibles

---

## 📞 Soporte Rápido

### "¿Por dónde empiezo?"
→ [README.md](./README.md)

### "¿Cómo instalo todo?"
→ [SETUP.md](./SETUP.md)

### "¿Cuál es la arquitectura?"
→ [ARCHITECTURE.md](./ARCHITECTURE.md)

### "¿Cómo configuro X?"
→ [config.md](./config.md)

### "¿Cuáles son las credenciales?"
→ [credenciales.md](./credenciales.md)

### "¿Cómo setup Storage?"
→ [storage/setup.md](./storage/setup.md)

### "¿Cómo setup Databricks?"
→ [databricks/setup.md](./databricks/setup.md)

### "¿Cómo setup Kafka KRaft?"
→ [kafka-kraft/setup.md](./kafka-kraft/setup.md)

### "¿Cómo setup Kafka Zookeeper?"
→ [kafka-zookeeper/setup.md](./kafka-zookeeper/setup.md)

### "Tengo un problema"
→ Buscar "Troubleshooting" en el documento relevante

---

## 🎓 Niveles de Documentación

### Nivel 1: Conceptual (Primeros 5 minutos)
- [README.md](./README.md) - ¿Qué es este proyecto?

### Nivel 2: Instalación (30-45 minutos)
- [SETUP.md](./SETUP.md) - Instalación paso a paso

### Nivel 3: Configuración (1-2 horas)
- [config.md](./config.md) - Parámetros y ajustes
- [credenciales.md](./credenciales.md) - Acceso a servicios

### Nivel 4: Arquitectura (2-3 horas)
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Diseño profundo
- Stack READMEs - Detalles por servicio

### Nivel 5: Integración (3-5 horas)
- Stack setup.md - Casos de uso
- Ejemplos de código - Patrones reales

### Nivel 6: Producción (5+ horas)
- Seguridad y hardening
- Monitoreo y alertas
- Backup y disaster recovery

---

## 📚 Recursos Externos

- [Docker Documentation](https://docs.docker.com/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

<div align="center">

**¿Dónde empiezo?** → [README.md](./README.md) → [SETUP.md](./SETUP.md) → Explorar

**¿Necesitas ayuda?** → Busca en esta página o en los documentos específicos

[📖 README](./README.md) | [🚀 SETUP](./SETUP.md) | [🏗️ ARCHITECTURE](./ARCHITECTURE.md) | [⚙️ CONFIG](./config.md) | [🔐 CREDENTIALS](./credenciales.md)

</div>

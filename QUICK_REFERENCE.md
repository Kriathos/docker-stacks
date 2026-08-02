# ⚡ Quick Reference - Comandos Esenciales

Tarjeta de referencia rápida con comandos más usados del laboratorio.

**Guardar esta página para acceso rápido** 📌

---

## 🚀 Startup & Shutdown

### Crear Red (Una sola vez)
```powershell
docker network create mynet
```

### Iniciar Todo
```powershell
# 1. Caddy
cd web
docker-compose -f docker-compose-caddy.yml up -d

# 2. Storage
cd ..\storage
docker-compose -f docker-compose-storage.yml up -d

# 3. Kafka (elegir una)
# Opción A: KRaft
cd ..\kafka-kraft && docker-compose up -d
# Opción B: Zookeeper
cd ..\kafka-zookeeper && docker-compose up -d

# 4. Databricks
cd ..\databricks
docker-compose up -d
```

### Iniciar un Stack Específico
```powershell
cd .\<stack>
docker-compose -f docker-compose-<stack>.yml up -d
# O si es docker-compose.yml por defecto:
docker-compose up -d
```

### Detener un Stack
```powershell
cd .\<stack>
docker-compose down
# O con volúmenes (borra datos):
docker-compose down -v
```

### Detener Todo
```powershell
# Script PowerShell
cd .\web && docker-compose -f docker-compose-caddy.yml down
cd ..\storage && docker-compose -f docker-compose-storage.yml down
cd ..\kafka-kraft && docker-compose down
cd ..\databricks && docker-compose down
```

---

## 📊 Ver Estado

### Todos los Contenedores
```powershell
docker ps
docker ps -a  # incluyendo detenidos
```

### Estado de un Stack
```powershell
cd .\<stack>
docker-compose ps
docker-compose ps -a
```

### Logs en Vivo
```powershell
docker-compose logs -f              # todos los servicios
docker-compose logs -f <servicio>   # servicio específico
docker-compose logs --tail 100      # últimas 100 líneas
```

### Usar un Contenedor
```powershell
docker-compose exec <servicio> <comando>
# Ejemplo:
docker-compose exec sqlserver sqlcmd -S localhost -U sa
docker-compose exec postgres psql -U airflow -d airflow
```

---

## 💾 Storage Stack

### Conectar a SQL Server
```powershell
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa

# Dentro de sqlcmd:
SELECT @@VERSION
GO
CREATE DATABASE TestDB
GO
EXIT
```

### Conectar a DB2
```powershell
docker-compose -f docker-compose-storage.yml exec db2 bash
su - db2inst1
db2 connect to SAMPLE
db2 "SELECT * FROM syscat.tables"
db2 terminate
exit
exit
```

### Conectar a PostgreSQL
```powershell
docker-compose -f docker-compose-storage.yml exec postgres psql -U postgres -d demo

# Dentro de psql:
\dt                      # ver tablas
\du                      # ver usuarios
SELECT COUNT(*) FROM users;
\q                       # salir
```

### Verificar MinIO
```powershell
docker-compose -f docker-compose-storage.yml exec minio mc --help

# O acceder web
URL: http://minio.local:9001
Usuario: admin
Contraseña: minioadmin
```

### Conectar a SFTPGo
```powershell
# Web UI:
URL: http://sftp.local:51500

# SFTP CLI:
sftp -P 2022 username@localhost
```

---

## 📨 Kafka Stack

### Ver Estado del Cluster

#### KRaft
```powershell
cd .\kafka-kraft
docker-compose exec kafka1 kafka-metadata.sh \
  --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log \
  --print
```

#### Zookeeper
```powershell
cd .\kafka-zookeeper
docker-compose exec zookeeper1 zkServer.sh status
docker-compose exec zookeeper1 zkCli.sh ls /brokers/ids
```

### Listar Topics
```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092
```

### Crear Topic
```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --create \
  --topic my-topic \
  --bootstrap-server kafka1:9092 \
  --partitions 3 \
  --replication-factor 3
```

### Describir Topic
```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --describe \
  --topic my-topic \
  --bootstrap-server kafka1:9092
```

### Productor (Enviar Mensajes)
```powershell
docker-compose exec kafka1 kafka-console-producer.sh \
  --broker-list kafka1:9092 \
  --topic my-topic

# Escribe mensajes y Ctrl+C para salir
```

### Consumidor (Leer Mensajes)
```powershell
docker-compose exec kafka1 kafka-console-consumer.sh \
  --bootstrap-server kafka1:9092 \
  --topic my-topic \
  --from-beginning
```

### Kafka UI
```
URL: http://kafka-ui.local:8080
(o http://localhost:8080)
```

### Verificar Debezium
```powershell
# Listar connectores
curl http://localhost:8083/connectors

# Ver estado de conector
curl http://localhost:8083/connectors/postgres-connector/status

# Ver logs
docker-compose logs debezium-connect
```

---

## 🔬 Databricks Stack

### Jupyter Lab
```
URL: http://jupyter.local:8888
Token: docker-compose logs jupyter | findstr "token="
```

### Airflow
```
URL: http://airflow.local:8082
Usuario: airflow
Contraseña: airflow
```

### MLflow
```
URL: http://mlflow.local:5000
(sin autenticación)
```

### Spark Master UI
```
URL: http://spark.local:8080
(o http://localhost:8080)
```

### Vault
```
URL: http://vault.local:8200
Token: mytoken (por defecto)
```

### Conectar a PostgreSQL (Airflow metadata)
```powershell
docker-compose exec postgres psql -U airflow -d airflow

# Dentro de psql:
\dt                    # ver tablas
SELECT COUNT(*) FROM dag;
\q                     # salir
```

---

## 🔐 Acceso a Servicios

### Desde Windows (Browser)
```
http://localhost/              # Caddy landing page
http://jupyter.local:8888      # Jupyter
http://airflow.local:8082      # Airflow
http://mlflow.local:5000       # MLflow
http://spark.local:8080        # Spark Master
http://vault.local:8200        # Vault
http://minio.local:9001        # MinIO Console
http://sftp.local:51500        # SFTPGo UI
http://kafka-ui.local:8080     # Kafka UI
```

### Desde Contenedor (Docker Network)
```powershell
# Acceder cualquier servicio por nombre DNS automático
docker run --rm --network mynet alpine \
  curl http://sqlserver:1433 \
  curl http://minio:9000 \
  curl http://kafka1:9092
```

---

## 🧪 Verificación Rápida

### Todos los Servicios
```powershell
# Contar contenedores (esperado: 15-20)
docker ps | Measure-Object

# Ver red
docker network inspect mynet | Select-String "Containers" -A 50

# Ver volúmenes
docker volume ls

# Ver imágenes
docker images
```

### SQL Server
```powershell
docker-compose -f storage/docker-compose-storage.yml exec sqlserver \
  sqlcmd -S localhost -U sa -Q "SELECT @@VERSION"
```

### Kafka
```powershell
cd kafka-kraft
docker-compose exec kafka1 kafka-broker-api-versions.sh --bootstrap-server kafka1:9092
```

### Spark
```powershell
docker-compose -f databricks/docker-compose.yml exec spark-master \
  spark-shell --version
```

---

## 🔧 Configuración Común

### Cambiar Puerto
```yaml
# En docker-compose-*.yml
services:
  jupyter:
    ports:
      - "8889:8888"  # host:container
```

### Cambiar Contraseña
```yaml
# En docker-compose-*.yml
environment:
  POSTGRES_PASSWORD: "nueva-contraseña"
  SA_PASSWORD: "NuevaSeg@2024"
```

### Cambiar Ruta (Storage)
```yaml
# En docker-compose-storage.yml
volumes:
  - "C:/data/sftp:/srv/sftpgo"  # cambiar de F:/
```

### Cambiar Límites de Memoria
```yaml
# En docker-compose-*.yml
deploy:
  resources:
    limits:
      memory: 2G      # cambiar de 1G
      cpus: '2'       # cambiar de 1
```

---

## 🐛 Troubleshooting Rápido

### El contenedor no inicia
```powershell
# Ver error
docker-compose logs <servicio>

# Reintentar
docker-compose restart <servicio>

# Nuclear: reiniciar todo
docker-compose down
docker-compose up -d
```

### Conexión rechazada
```powershell
# Verificar que está corriendo
docker ps | findstr <servicio>

# Verificar puerto
netstat -an | findstr :<puerto>

# Esperar iniciación (60 seg)
Start-Sleep -Seconds 60
```

### Sin conexión entre contenedores
```powershell
# Verificar que están en mynet
docker network inspect mynet | Select-String <container>

# Test DNS
docker run --rm --network mynet alpine ping <servicio>
```

### Disco lleno
```powershell
# Ver uso
docker system df

# Limpiar
docker system prune -a --volumes
docker volume prune
```

---

## 📋 Credenciales (Default)

```
SQL Server
  Usuario: sa
  Contraseña: Generar (en docker-compose.yml)

DB2
  Usuario: db2inst1
  Contraseña: Generar (en docker-compose.yml)

PostgreSQL
  Usuario: postgres / airflow
  Contraseña: Generar (en docker-compose.yml)

MinIO
  Usuario: admin
  Contraseña: Generar (en docker-compose.yml)

Airflow
  Usuario: airflow
  Contraseña: airflow

Jupyter
  Token: Ver logs

Spark
  Sin autenticación

Kafka
  Sin autenticación (SASL opcional)

Vault
  Token: mytoken (dev mode)

SFTPGo
  Crear en web UI en primer acceso
```

**Ver detalles en:** [credenciales.md](./credenciales.md)

---

## 📚 Documentación Completa

| Documento | Para Qué | Tiempo |
|-----------|----------|--------|
| [README.md](./README.md) | Visión general | 5 min |
| [SETUP.md](./SETUP.md) | Instalación | 45 min |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Diseño profundo | 30 min |
| [config.md](./config.md) | Configuración | 20 min |
| [credenciales.md](./credenciales.md) | Acceso | 10 min |
| [INDEX.md](./INDEX.md) | Navegación | 10 min |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | Este archivo | 5 min |

---

## ⚡ Una Línea de Comandos

```powershell
# Create network, start all, wait 90 sec
docker network create mynet; cd web; docker-compose -f docker-compose-caddy.yml up -d; cd ..\storage; docker-compose -f docker-compose-storage.yml up -d; cd ..\kafka-kraft; docker-compose up -d; cd ..\databricks; docker-compose up -d; Start-Sleep -Seconds 90; docker ps
```

---

<div align="center">

**Bookmark esta página** 📌

[📖 README](./README.md) | [🚀 SETUP](./SETUP.md) | [🏗️ ARCHITECTURE](./ARCHITECTURE.md) | [🗺️ INDEX](./INDEX.md) | [📑 QUICK_REF](./QUICK_REFERENCE.md)

</div>

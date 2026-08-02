# 🔐 Credenciales Centralizadas del Proyecto

**⚠️ IMPORTANTE:** Este archivo contiene credenciales de laboratorio. 

- **Para desarrollo local:** Está bien usar estas credenciales
- **Para datos reales:** REEMPLAZA todas las credenciales por valores seguros
- **Para producción:** Usa HashiCorp Vault, AWS Secrets Manager, o similar
- **Antes de publicar:** Revisa que no haya credenciales reales en este archivo

---

## 📋 Tabla de Contenidos

1. [Databricks Stack](#databricks-stack)
2. [Kafka Stack](#kafka-stack)
3. [Storage Stack](#storage-stack)
4. [Web (Caddy)](#web-caddy-stack)
5. [Convenciones](#-convenciones)
6. [Actualizar Credenciales](#-actualizar-credenciales)

---

## 🔬 Databricks Stack

### Apache Spark

```yaml
# databricks/docker-compose.yml
services:
  spark-master:
    environment:
      SPARK_PUBLIC_DNS: "spark.local"
```

**Propósito:** Computación distribuida

**Credenciales:** Ninguna (sin autenticación por defecto)

**Acceso:**
- URL: http://spark.local:8080
- Usuarios/contraseña: No requerida

---

### Jupyter Lab

```yaml
services:
  jupyter:
    ports:
      - "8888:8888"
    environment:
      JUPYTER_TOKEN: "generará automáticamente"
```

**Propósito:** Notebooks interactivos con PySpark

**Credenciales:** Token automático

**Obtener token:**
```powershell
docker-compose logs jupyter | grep "token="
# Salida: http://127.0.0.1:8888/?token=abc123...
```

**Acceso:**
- URL: http://jupyter.local:8888
- Token: Ver logs arriba

**Cambiar token:**
```yaml
environment:
  JUPYTER_TOKEN: "mi-token-seguro-123"
```

---

### PostgreSQL (Metadatos Airflow)

```yaml
services:
  postgres:
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: "Generar"        # ← CAMBIAR
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"
```

**Propósito:** Base datos para Airflow metadata

**Credenciales:**
- **Usuario:** `airflow`
- **Contraseña:** `Generar` (reemplazar)
- **Base de datos:** `airflow`
- **Puerto:** 5432

**Generar contraseña segura:**
```powershell
$pass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | % {[char]$_})
Write-Host $pass
```

**Conectar (CLI):**
```powershell
docker-compose exec postgres psql -U airflow -d airflow -c "\du"
```

---

### Apache Airflow

```yaml
services:
  airflow-webserver:
    environment:
      AIRFLOW_UID: 50000
      AIRFLOW_GID: 50000
      AIRFLOW__CORE__FERNET_KEY: "Generar"  # ← CAMBIAR
      AIRFLOW__CORE__DAGS_FOLDER: "/opt/airflow/dags"
```

**Propósito:** Orquestación de workflows

**Credenciales (UI Web):**
- **Usuario:** `airflow`
- **Contraseña:** `airflow`

**Generar Fernet Key (Obligatorio):**
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Salida: gAAAAABl8mJ_2X...
# Copia esta salida a AIRFLOW__CORE__FERNET_KEY
```

**Acceso:**
- URL: http://airflow.local:8082
- Usuario: `airflow`
- Contraseña: `airflow`

**Cambiar contraseña:**
```powershell
docker-compose exec airflow-webserver airflow users modify --username airflow --password nueva-contraseña
```

---

### MLflow

```yaml
services:
  mlflow:
    ports:
      - "5000:5000"
    # Sin credenciales (asume entorno seguro)
```

**Propósito:** Tracking de experimentos ML

**Credenciales:** Ninguna (sin autenticación)

**Acceso:**
- URL: http://mlflow.local:5000
- Usuario/Contraseña: No requiere

**Registrar experimento (Python):**
```python
import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("accuracy", 0.95)
```

---

### HashiCorp Vault

```yaml
services:
  vault:
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: "mytoken"  # ← CAMBIAR
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
```

**Propósito:** Gestión centralizada de secretos

**Credenciales (Modo Dev):**
- **Root Token:** `mytoken`
- **URL:** http://vault.local:8200
- **Unseal Key:** Automático en dev mode

**Acceso UI:**
- URL: http://vault.local:8200
- Token: `mytoken`

**Generar token seguro:**
```powershell
$token = -join ((65..90) + (97..122) | Get-Random -Count 20 | % {[char]$_})
Write-Host $token
# Copiar a VAULT_DEV_ROOT_TOKEN_ID
```

**Crear secreto en Vault (CLI):**
```powershell
docker-compose exec vault vault kv put secret/database/postgres \
  username=postgres \
  password=secure-password
```

---

## 📨 Kafka Stack

### PostgreSQL (CDC Source)

```yaml
services:
  postgres-cdc:
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: "Generar"        # ← CAMBIAR
      POSTGRES_DB: demo
    ports:
      - "5432:5432"
```

**Propósito:** Source de datos para Debezium CDC

**Credenciales:**
- **Usuario:** `postgres`
- **Contraseña:** `Generar` (reemplazar)
- **Base de datos:** `demo`
- **Puerto:** 5432

**Conectar:**
```powershell
docker-compose exec postgres-cdc psql -U postgres -d demo -c "\dt"
```

**Crear tabla de prueba:**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
```

---

### Kafka (KRaft)

```yaml
services:
  kafka1:
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: "broker,controller"
      # Sin credenciales por defecto (SASL/SCRAM puede agregarse)
```

**Propósito:** Cluster de Kafka (3 brokers)

**Credenciales:** Ninguna (sin SASL/SCRAM habilitado)

**Acceso:**
- Bootstrap Servers: `kafka1:9092,kafka2:9093,kafka3:9094`
- No requiere usuario/contraseña

**Crear topic:**
```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --create \
  --topic test-topic \
  --bootstrap-server kafka1:9092 \
  --partitions 3 \
  --replication-factor 3
```

---

### Kafka (Zookeeper)

```yaml
services:
  kafka1:
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: "zookeeper1:2181,zookeeper2:2181,zookeeper3:2181"
      # Sin credenciales por defecto
```

**Propósito:** Cluster de Kafka con coordinador Zookeeper

**Credenciales:** Ninguna

**Acceso:**
- Bootstrap Servers: `kafka1:9092,kafka2:9093,kafka3:9094`
- Zookeeper Connect: `zookeeper1:2181,zookeeper2:2181,zookeeper3:2181`

---

### Debezium Connect

```yaml
services:
  debezium:
    ports:
      - "8083:8083"
    # Sin credenciales en UI (asume red privada)
```

**Propósito:** Change Data Capture desde PostgreSQL

**Credenciales:**
- Las credenciales están en la configuración del connector
- Ver [Configurar Connector](#-configurar-debezium-connector)

**Acceso REST API:**
- URL: http://kafka.local:8083
- No requiere autenticación

**Configurar Connector CDC:**
```json
POST http://kafka.local:8083/connectors

{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres-cdc",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "Generar",        # ← Usar credencial de PostgreSQL arriba
    "database.dbname": "demo",
    "database.server.name": "postgres",
    "table.include.list": "public.users",
    "publication.name": "dbz_publication",
    "slot.name": "dbz_slot"
  }
}
```

---

## 💾 Storage Stack

### SQL Server

```yaml
services:
  sqlserver:
    environment:
      SA_PASSWORD: "Generar"              # ← CAMBIAR (complejidad requerida)
      ACCEPT_EULA: "Y"
    ports:
      - "1433:1433"
```

**Propósito:** Base de datos relacional MSSQL

**Credenciales:**
- **Usuario:** `sa` (System Administrator)
- **Contraseña:** `Generar` (reemplazar)
- **Puerto:** 1433

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- Debe contener mayúsculas, minúsculas, números y símbolos

**Ejemplo de contraseña segura:**
```
Secure$Pass2024!
P@ssw0rd#SQL2024
DB2$ecure_123!abc
```

**Conectar (CLI):**
```powershell
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa
# Ingresa contraseña cuando se pida
```

**Crear base de datos:**
```sql
CREATE DATABASE MyDatabase;
USE MyDatabase;
CREATE TABLE users (
  id INT PRIMARY KEY IDENTITY(1,1),
  name NVARCHAR(100),
  email NVARCHAR(100)
);
```

---

### IBM DB2

```yaml
services:
  db2:
    environment:
      DB2INST1_PASSWORD: "Generar"        # ← CAMBIAR
      LICENSE: "accept"
      DBNAME: "SAMPLE"
    ports:
      - "50000:50000"
```

**Propósito:** Base de datos empresarial IBM

**Credenciales:**
- **Usuario:** `db2inst1`
- **Contraseña:** `Generar` (reemplazar)
- **Base de datos:** `SAMPLE`
- **Puerto:** 50000

**Requisitos de contraseña:**
- Mínimo 8 caracteres
- No puede contener nombre de usuario

**Conectar (CLI):**
```powershell
docker-compose -f docker-compose-storage.yml exec db2 bash

# Dentro del contenedor:
su - db2inst1  # (ingresa contraseña)
db2 connect to SAMPLE
db2 "SELECT * FROM syscat.tables"
```

**Crear tabla:**
```sql
db2 "CREATE TABLE users (
  id INT NOT NULL,
  name VARCHAR(100),
  PRIMARY KEY (id)
)"
```

---

### MinIO (S3-Compatible)

```yaml
services:
  minio:
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: "Generar"      # ← CAMBIAR
    ports:
      - "9000:9000"
      - "9001:9001"
```

**Propósito:** Object storage compatible con S3

**Credenciales (Admin):**
- **Usuario:** `admin`
- **Contraseña:** `Generar` (reemplazar)
- **API Port:** 9000
- **Console Port:** 9001

**Acceso:**
- URL Console: http://minio.local:9001
- URL API: http://minio-api.local:9000

**Generar contraseña:**
```powershell
$pass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | % {[char]$_})
Write-Host $pass
```

**Conectar (CLI):**
```powershell
docker-compose -f docker-compose-storage.yml exec minio mc alias set minio http://localhost:9000 admin password

mc mb minio/my-bucket
mc cp file.txt minio/my-bucket/
```

**Conectar (Python):**
```python
from minio import Minio

client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="Generar",
    secure=False
)

# Crear bucket
client.make_bucket("my-bucket")

# Subir archivo
client.fput_object("my-bucket", "file.txt", "local_file.txt")
```

---

### SFTPGo

```yaml
services:
  sftpgo:
    ports:
      - "2022:2022"
      - "51500:51500"
    # Credenciales en web UI (crear usuarios desde interfaz)
```

**Propósito:** Servidor SFTP con interfaz web

**Credenciales:**
- **Usuario Admin (UI):** Crear en primer acceso
- **Puerto SFTP:** 2022
- **Puerto UI Web:** 51500

**Acceso UI Web:**
- URL: http://sftp.local:51500
- Crear usuario admin en primer login

**Conectar SFTP:**
```powershell
sftp -P 2022 username@localhost
# Ingresa contraseña cuando se pida
```

**Crear usuario desde CLI:**
```powershell
docker-compose -f docker-compose-storage.yml exec sftpgo \
  sftpgo add-user username \
  --password password \
  --home-dir /data/sftp/username
```

---

### Apache File Server

```yaml
services:
  file-server:
    ports:
      - "80:80"
    # Sin credenciales (servidor público)
```

**Propósito:** Servidor HTTP de archivos estáticos

**Credenciales:** Ninguna

**Acceso:**
- URL: http://data.local
- Archivos: `F:/apache-fileserver/`

**Agregar archivo:**
```powershell
Copy-Item "C:\archivo.pdf" "F:\apache-fileserver\archivo.pdf"

# Accesible en: http://data.local/archivo.pdf
```

---

## 🌐 Web (Caddy) Stack

### Caddy Reverse Proxy

```yaml
services:
  caddy:
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    # Sin credenciales (asume red privada)
```

**Propósito:** Proxy inverso HTTP/HTTPS

**Credenciales:**
- **Admin API:** Deshabilitada en producción
- **TLS:** Let's Encrypt (automático)

**Acceso:**
- URL: http://localhost o https://localhost
- No requiere autenticación

**Configurar autenticación (opcional):**
```
landing.local {
  # Basic auth
  basicauth / {
    admin Generar_contraseña_aquí
  }
  
  root * /usr/share/caddy/html
  file_server
}
```

---

## 📝 Convenciones

### Nombres de Credenciales

En `docker-compose-*.yml`:

```yaml
# ✅ CORRECTO - Placeholder claro
SA_PASSWORD: "Generar"
DB_PASSWORD: "Generar"

# ❌ INCORRECTO - Contraseña real
SA_PASSWORD: "MySecurePass123"

# ❌ INCORRECTO - Demasiado vago
PASSWORD: "pass"
```

### Almacenamiento Seguro

**Desarrollo:**
```powershell
# .env file (agregar a .gitignore)
POSTGRES_PASSWORD=MySecurePassword123
MINIO_PASSWORD=MyMinIOPassword456
```

**Producción:**
```bash
# Usar Vault, Secrets Manager, o similar
vault kv put secret/database/postgres password=secure-password
aws secretsmanager put-secret --name db-password --secret-string ...
```

---

## 🔄 Actualizar Credenciales

### Paso 1: Generar Nueva Credencial

```powershell
# Contraseña segura
$newpass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | % {[char]$_})
Write-Host $newpass

# O usar generador online (último recurso)
# https://www.random.org/strings/
```

### Paso 2: Actualizar docker-compose-*.yml

```yaml
# Antes
POSTGRES_PASSWORD: "Generar"

# Después
POSTGRES_PASSWORD: "MyNewSecure123!"
```

### Paso 3: Reiniciar Contenedor

```powershell
# Detener
docker-compose -f docker-compose-*.yml down

# Iniciar con nueva contraseña
docker-compose -f docker-compose-*.yml up -d
```

### Paso 4: Actualizar Credenciales.md

```markdown
# Antes
- **Contraseña:** `Generar`

# Después
- **Contraseña:** `(Actualizada a valor seguro)`
```

### Paso 5: Sincronizar Otras Aplicaciones

Si otras apps conectan a este servicio:
- Jupyter → PostgreSQL
- Spark → SQL Server
- Debezium → PostgreSQL
- Etc.

Actualizar las credenciales en las otras apps también.

---

## ✅ Checklist de Seguridad

Antes de usar datos reales:

- [ ] Todas las contraseñas cambiadaspara CAMBIAR
- [ ] Valores reales, no "Generar"
- [ ] Contraseñas de 12+ caracteres
- [ ] Caracteres especiales incluidos
- [ ] Archivo `.env` en `.gitignore`
- [ ] No commits credenciales reales
- [ ] SSH keys para acceso remoto
- [ ] TLS/HTTPS en producción
- [ ] Firewall rules configuradas
- [ ] Audit logging habilitado
- [ ] Vault o Secrets Manager en uso

---

<div align="center">

⚠️ **Recuerda:** Este archivo es solo para laboratorio local.

Para producción, usa gestión de secretos empresarial.

[📖 Leer README](./README.md) • [⚙️ Ver config](./config.md) • [🚀 Ver SETUP](./SETUP.md)

</div>

# 🚀 Setup Databricks Stack

Guía paso a paso para iniciar el stack de datos y ML (Spark, Jupyter, MLflow, Airflow, Vault).

---

## ✅ Pre-requisitos

- ✅ Docker Desktop instalado y corriendo
- ✅ Red `mynet` creada: `docker network create mynet`
- ✅ 4GB RAM mínimo (8GB recomendado)
- ✅ 20GB disco disponible
- ✅ Python 3.7+ (para generar Fernet Key)

---

## 🔐 Paso 1: Generar Fernet Key para Airflow

Airflow requiere una clave Fernet para cifrar contraseñas. Debe generarse antes de iniciar.

### 1.1 Generar Clave

```powershell
# Opción 1: Con Python (si está instalado)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Salida esperada (copiar esta línea completa):
# gAAAAABl8mJ_2X9nZ8kL...
```

**Si no tienes Python instalado:**
```powershell
# Opción 2: Con Docker
docker run --rm python:3.9 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 1.2 Guardar la Clave

**Copia la clave generada en los dos lugares:**

1. En `docker-compose.yml`:
```yaml
airflow-webserver:
  environment:
    AIRFLOW__CORE__FERNET_KEY: "gAAAAABl8mJ_2X9nZ8kL..."  # ← PEGAR AQUÍ

airflow-scheduler:
  environment:
    AIRFLOW__CORE__FERNET_KEY: "gAAAAABl8mJ_2X9nZ8kL..."  # ← PEGAR AQUÍ
```

2. En `credenciales.md` (raíz):
```markdown
## Databricks Stack

### Airflow Fernet Key
- **Fernet Key:** `gAAAAABl8mJ_2X9nZ8kL...`
```

---

## 🔑 Paso 2: Configurar Credenciales

Lee [`credenciales.md`](../credenciales.md) en raíz.

### 2.1 Actualizar Contraseñas (Recomendado)

Edita `docker-compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_PASSWORD: "Secure$Pass2024"  # Cambiar de "Generar"

airflow-webserver:
  environment:
    AIRFLOW__CORE__FERNET_KEY: "gAAAAABl..."  # ← REQUERIDO
    # Usuario/contraseña airflow/airflow (configurado automáticamente)

vault:
  environment:
    VAULT_DEV_ROOT_TOKEN_ID: "mytoken123"  # Cambiar si deseas
```

### 2.2 Generar Contraseña Segura

```powershell
$pass = -join ((65..90) + (97..122) + (48..57) + (33..47) | Get-Random -Count 16 | % {[char]$_})
Write-Host $pass
```

---

## 📁 Paso 3: Crear Directorios para DAGs y Notebooks

### 3.1 Crear Estructura

```powershell
# Navegar al directorio databricks
cd .\databricks

# Crear directorios
New-Item -Path "dags" -ItemType Directory -Force
New-Item -Path "notebooks" -ItemType Directory -Force
New-Item -Path "mlruns" -ItemType Directory -Force
New-Item -Path "logs" -ItemType Directory -Force

# Verificar
ls -Directory
```

### 3.2 Crear DAG de Ejemplo

Crea archivo `dags/example_dag.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'example_etl',
    default_args=default_args,
    description='Example ETL DAG',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    task1 = BashOperator(
        task_id='print_hello',
        bash_command='echo "Starting ETL..."'
    )

    task2 = BashOperator(
        task_id='print_goodbye',
        bash_command='echo "ETL completed!"'
    )

    task1 >> task2
```

---

## 🚀 Paso 4: Iniciar Databricks Stack

### 4.1 Iniciar Servicios

```powershell
# Navegar al directorio
cd .\databricks

# Iniciar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE               NAMES
xxxxx          postgres:13         postgres
xxxxx          bitnami/spark:latest  spark-master
xxxxx          bitnami/spark:latest  spark-worker
xxxxx          jupyter/datascience  jupyter
xxxxx          apache/airflow:2.x   airflow-webserver
xxxxx          apache/airflow:2.x   airflow-scheduler
xxxxx          vault:latest        vault
xxxxx          python:3.9          mlflow
```

### 4.2 Esperar a que Inicien

Diferentes servicios tienen diferentes tiempos de inicio:

```powershell
# PostgreSQL: ~5 segundos
# Spark Master: ~10 segundos
# Spark Worker: ~10 segundos
# Jupyter: ~15 segundos
# Airflow Webserver: ~30 segundos (primero)
# Airflow Scheduler: ~10 segundos
# Vault: ~5 segundos
# MLflow: ~5 segundos

# Total esperado: ~60-90 segundos

# Ver logs de Airflow (toma más tiempo)
docker-compose logs -f airflow-webserver

# Buscar: "Serving Flask app..." o similar
```

---

## ✅ Paso 5: Verificar Conectividad

### 5.1 Test PostgreSQL

```powershell
# Conectar a PostgreSQL
docker-compose exec postgres psql -U airflow -d airflow -c "\du"

# Deberías ver lista de usuarios
# postgres | Superuser | Create role, Create DB
# airflow  |           | Cannot login
```

### 5.2 Test Spark Master

```powershell
# Verificar que Spark responde
docker-compose exec spark-master spark-shell --version

# Deberías ver versión de Spark
```

### 5.3 Test Jupyter

```powershell
# Ver token de Jupyter
docker-compose logs jupyter | findstr "token="

# Salida esperada:
# http://127.0.0.1:8888/?token=abc123...
```

### 5.4 Test Airflow

```powershell
# Ver logs de Airflow
docker-compose logs airflow-webserver | Select-String "Running on"

# Salida esperada:
# * Running on http://0.0.0.0:8082
```

### 5.5 Test MLflow

```powershell
# Verificar MLflow
curl -I http://localhost:5000

# Deberías ver: HTTP/1.1 200 OK
```

### 5.6 Test Vault

```powershell
# Verificar Vault
docker-compose exec vault vault status

# Deberías ver: Sealed: false (dev mode)
```

---

## 🌐 Paso 6: Acceder a Interfaces Web

Ahora que todo está corriendo, accede a las UIs:

### 6.1 Jupyter Lab

```
URL: http://jupyter.local:8888
(o http://localhost:8888 si no configuraste hosts)

Token: Obtener de logs:
docker-compose logs jupyter | findstr "token="

Acceder:
1. Copia URL de logs
2. Pega en navegador
3. No requiere usuario/contraseña (token)
```

**Crear primer notebook:**
1. Click "New" → Python 3
2. Ejecutar:
```python
import pyspark
print(f"PySpark version: {pyspark.__version__}")

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("test").getOrCreate()
spark.range(10).show()
```

### 6.2 Airflow Web UI

```
URL: http://airflow.local:8082
(o http://localhost:8082)

Usuario: airflow
Contraseña: airflow

Verificar DAG:
1. Login
2. Buscar "example_etl" en DAGs
3. Click para ver detalles
4. Trigger manualmente si deseas
```

### 6.3 MLflow UI

```
URL: http://mlflow.local:5000
(o http://localhost:5000)

Sin autenticación
Sin datos por defecto (se crean al trackear experimentos)

Crear experiment (desde Jupyter):
```python
import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.1)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_artifact("model.pkl")
```

### 6.4 Vault UI

```
URL: http://vault.local:8200
(o http://localhost:8200)

Token: (el que configuraste en docker-compose.yml)

Crear secret:
1. Login con token
2. Click "Create secret"
3. Path: secret/my-secret
4. Key: password
5. Value: my-password
6. Save
```

### 6.5 Spark Master UI

```
URL: http://spark.local:8080
(o http://localhost:8080)

No requiere autenticación
Muestra estado del cluster y jobs
```

---

## 📊 Paso 7: Crear Pipeline de Prueba

### 7.1 Crear Notebook en Jupyter

En Jupyter, crea celda con:

```python
# Setup
from pyspark.sql import SparkSession
import pandas as pd
from datetime import datetime

spark = SparkSession.builder \
    .appName("DataPipeline") \
    .getOrCreate()

# Crear DataFrame de prueba
data = [
    ("Alice", 25, "Engineering"),
    ("Bob", 30, "Sales"),
    ("Charlie", 28, "Engineering"),
]

df = spark.createDataFrame(data, ["name", "age", "department"])

# Mostrar
df.show()

# Estadísticas
df.groupBy("department").count().show()

# Guardar a CSV
df.coalesce(1).write.mode("overwrite").csv("/tmp/employees")

print(f"Pipeline completado: {datetime.now()}")
```

### 7.2 Trackear en MLflow

En celda siguiente:

```python
import mlflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("spark-experiment")

# Generar datos
X, y = make_regression(n_samples=100, n_features=10)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Entrenar
model = RandomForestRegressor(n_estimators=10)
model.fit(X_train, y_train)

# Trackear en MLflow
with mlflow.start_run():
    mlflow.log_param("n_estimators", 10)
    mlflow.log_metric("train_score", model.score(X_train, y_train))
    mlflow.log_metric("test_score", model.score(X_test, y_test))
    mlflow.log_artifact(__file__)

print("Experimento registrado en MLflow!")
```

### 7.3 Crear DAG en Airflow

Crea `dags/spark_etl_dag.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'spark_etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
)

spark_task = SparkSubmitOperator(
    task_id='run_spark_job',
    application='/opt/spark-apps/job.py',
    master='spark://spark-master:7077',
    name='ETL Job',
    dag=dag,
)

spark_task
```

---

## 🔗 Paso 8: Integración con Otros Stacks

### 8.1 Conectar a SQL Server (Storage Stack)

```python
# En Jupyter Notebook

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ReadSQL") \
    .getOrCreate()

# Leer
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[TestDB].[dbo].[Users]") \
    .option("user", "sa") \
    .option("password", "tu-contraseña") \
    .load()

df.show()

# Escribir
df.write \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[TestDB].[dbo].[UsersProcessed]") \
    .option("user", "sa") \
    .option("password", "tu-contraseña") \
    .mode("overwrite") \
    .save()
```

### 8.2 Conectar a MinIO (Storage Stack)

```python
# En Jupyter Notebook

# Configurar Spark para MinIO
spark.conf.set("fs.s3a.endpoint", "http://minio:9000")
spark.conf.set("fs.s3a.access.key", "admin")
spark.conf.set("fs.s3a.secret.key", "tu-contraseña")
spark.conf.set("fs.s3a.path.style.access", "true")
spark.conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

# Leer desde MinIO
df = spark.read.parquet("s3a://my-bucket/data.parquet")
df.show()

# Escribir a MinIO
df.write.parquet("s3a://my-bucket/processed_data.parquet")
```

### 8.3 Consumir Kafka (Kafka Stack)

```python
# En Jupyter Notebook

# Spark Structured Streaming desde Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "postgres.public.users") \
    .load()

# Procesar
result = df.select("*")

# Guardar
query = result \
    .writeStream \
    .format("parquet") \
    .option("path", "/tmp/kafka-data") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

# Ejecutar por 30 segundos
query.awaitTermination(30)
query.stop()
```

---

## 🛑 Paso 9: Detener Stack

### 9.1 Detener Servicios

```powershell
# Detener pero mantener datos
docker-compose down

# Verificar
docker ps | findstr databricks
# No debe haber resultados
```

### 9.2 Limpiar (⚠️ Borra datos)

```powershell
# Eliminar volúmenes y datos
docker-compose down -v

# Limpiar directorios locales
Remove-Item "dags\*" -Recurse -Force
Remove-Item "notebooks\*" -Recurse -Force
Remove-Item "mlruns\*" -Recurse -Force
Remove-Item "logs\*" -Recurse -Force
```

---

## 🆘 Troubleshooting

### Problema: "Airflow fails to start"

**Síntoma:** Container de Airflow se detiene o no inicia

**Soluciones:**
1. Verificar Fernet Key generada correctamente
2. Ver logs: `docker-compose logs airflow-webserver`
3. Esperar más tiempo (primer inicio es lento)
4. Aumentar RAM de Docker Desktop

### Problema: "Jupyter token invalid"

**Síntoma:** No puedo acceder a Jupyter con token

**Solución:**
```powershell
# Obtener token actual
docker-compose logs jupyter | Select-String "token=" | Select-Object -Last 1

# O reiniciar
docker-compose restart jupyter
```

### Problema: "Spark job fails with 'host unreachable'"

**Síntoma:** Error conectando a Storage Stack

**Soluciones:**
1. Verificar que Storage Stack está corriendo
2. Verificar que ambos están en `mynet`
3. Ver logs: `docker-compose logs spark-master`
4. Test conectividad: `docker-compose exec spark-master ping sqlserver`

### Problema: "PostgreSQL connection refused"

**Síntoma:** Airflow no puede conectar a base datos

**Soluciones:**
1. Verificar que PostgreSQL está corriendo
2. Verificar credenciales en docker-compose.yml
3. Ver logs de Postgres: `docker-compose logs postgres`
4. Esperar más tiempo al iniciar (tarda ~15 segundos)

---

## ✅ Checklist de Verificación

Una vez completado el setup:

- [ ] Todos los contenedores están corriendo (`docker ps`)
- [ ] PostgreSQL responde
- [ ] Spark Master accesible en :8080
- [ ] Jupyter accesible en :8888
- [ ] Airflow accesible en :8082
- [ ] MLflow accesible en :5000
- [ ] Vault accesible en :8200
- [ ] Notebook de ejemplo ejecutado correctamente
- [ ] DAG de ejemplo visible en Airflow
- [ ] Experiment trackeo en MLflow funciona
- [ ] Conecta a SQL Server desde Spark
- [ ] Conecta a MinIO desde Spark

---

## 📚 Siguientes Pasos

1. **Crear tus propios notebooks**
   - Analiza datos del Storage Stack
   - Entrena modelos ML
   - Visualiza resultados

2. **Automatizar con Airflow**
   - Crea DAGs complejos
   - Integra con Spark
   - Schedule ejecución

3. **Track experimentos ML**
   - Usa MLflow para registrar
   - Compara modelos
   - Registra artifacts

4. **Integración Completa**
   - ETL: SQL Server → Spark → MinIO
   - Streaming: Kafka → Spark → Parquet
   - ML: Data Prep → Training → MLflow

---

<div align="center">

[📖 Leer README](../databricks/README.md) • [⚙️ Ver config](../databricks/config.md) • [🚀 Leer SETUP central](../SETUP.md)

</div>

# 🔗 Ejemplos de Integración Entre Stacks

Ejemplos reales y verificables de cómo integrar múltiples stacks para crear pipelines complejos.

---

## 📋 Tabla de Contenidos

1. [CDC: PostgreSQL → Kafka → Spark](#patrón-1-cdc-postgresql--kafka--spark)
2. [Data Lake: Archivos → MinIO → Spark → SQL](#patrón-2-data-lake-archivos--minio--spark--sql)
3. [ML Pipeline: Datos → Jupyter → MLflow → Airflow](#patrón-3-ml-pipeline-datos--jupyter--mlflow--airflow)
4. [Real-time Analytics: Kafka → Spark Streaming → Storage](#patrón-4-real-time-analytics-kafka--spark-streaming--storage)
5. [ETL Automático: Airflow Orchestrating Everything](#patrón-5-etl-automático-airflow-orchestrating-everything)

---

## Patrón 1: CDC (PostgreSQL → Kafka → Spark)

### 1.1 Objetivo

Capturar cambios en PostgreSQL, transmitirlos por Kafka, y procesarlos en Spark.

**Flujo:**
```
PostgreSQL Changes
    ↓ (CDC)
Debezium Connector
    ↓
Kafka Topics (postgres.*)
    ↓
Spark Streaming
    ↓
SQL Server / MinIO (Destino)
```

### 1.2 Setup

#### Paso 1: Crear tabla en PostgreSQL (Kafka Stack)

```powershell
cd .\kafka-kraft

# Conectar a PostgreSQL
docker-compose exec postgres-cdc psql -U postgres -d demo

# Crear tabla
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Insertar datos de prueba
INSERT INTO products (name, price) VALUES ('Laptop', 999.99);
INSERT INTO products (name, price) VALUES ('Mouse', 29.99);

# Salir
\q
```

#### Paso 2: Crear publicación en PostgreSQL

```powershell
docker-compose exec postgres-cdc psql -U postgres -d demo

CREATE PUBLICATION dbz_publication FOR TABLE products;
\dP

\q
```

#### Paso 3: Registrar Debezium Connector

```powershell
# Registrar CDC connector
$connectorConfig = @{
  "name" = "postgres-products-connector"
  "config" = @{
    "connector.class" = "io.debezium.connector.postgresql.PostgresConnector"
    "database.hostname" = "postgres-cdc"
    "database.port" = "5432"
    "database.user" = "postgres"
    "database.password" = "postgres"
    "database.dbname" = "demo"
    "database.server.name" = "postgres"
    "publication.name" = "dbz_publication"
    "slot.name" = "dbz_products_slot"
    "plugin.name" = "pgoutput"
    "table.include.list" = "public.products"
    "transforms" = "route"
    "transforms.route.type" = "org.apache.kafka.connect.transforms.RegexRouter"
    "transforms.route.regex" = "([^.]+)\\.([^.]+)\\.([^.]+)"
    "transforms.route.replacement" = "$3"
  }
}

$json = $connectorConfig | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8083/connectors" `
  -ContentType "application/json" `
  -Body $json

# Verificar status
Invoke-RestMethod -Uri "http://localhost:8083/connectors/postgres-products-connector/status"
```

#### Paso 4: Verificar Topics Creados

```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092 | findstr "postgres"

# Deberías ver: postgres.public.products
```

#### Paso 5: Producir Cambios

```powershell
docker-compose exec postgres-cdc psql -U postgres -d demo

# Estos cambios se replicarán automáticamente
INSERT INTO products (name, price) VALUES ('Keyboard', 79.99);
UPDATE products SET price = 899.99 WHERE id = 1;

\q
```

#### Paso 6: Consumir desde Spark

En Jupyter (Databricks Stack):

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DecimalType, TimestampType

spark = SparkSession.builder.appName("CDCConsumer").getOrCreate()

# Definir esquema (Debezium envelope)
schema = StructType([
    StructField("before", StructType([
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("price", DecimalType(10, 2)),
        StructField("updated_at", TimestampType())
    ])),
    StructField("after", StructType([
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("price", DecimalType(10, 2)),
        StructField("updated_at", TimestampType())
    ])),
    StructField("op", StringType()),  # c=create, u=update, d=delete
    StructField("ts_ms", StringType())
])

# Leer desde Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "postgres.public.products") \
    .option("startingOffsets", "earliest") \
    .option("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer") \
    .load()

# Parse JSON
from pyspark.sql.functions import col, from_json, get_json_object

parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("cdc")
).select(
    col("cdc.after.id"),
    col("cdc.after.name"),
    col("cdc.after.price"),
    col("cdc.op").alias("operation")
)

# Mostrar en tiempo real
query = parsed \
    .writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination(60)
query.stop()

# Resultado esperado:
# id | name      | price | operation
# 1  | Laptop    | 899.99| u (update)
# 2  | Mouse     | 29.99 | c (create)
# 3  | Keyboard  | 79.99 | c (create)
```

#### Paso 7: Guardar Cambios en SQL Server

```python
# Continuación del código anterior

# Escribir a SQL Server
query = parsed \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoint_products") \
    .foreachBatch(lambda df, batchId: write_to_sqlserver(df, batchId)) \
    .start()

def write_to_sqlserver(df, batchId):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:sqlserver://sqlserver:1433") \
        .option("dbtable", "[TestDB].[dbo].[products_cdc]") \
        .option("user", "sa") \
        .option("password", "tu-contraseña") \
        .mode("append") \
        .save()

query.awaitTermination()
```

---

## Patrón 2: Data Lake (Archivos → MinIO → Spark → SQL)

### 2.1 Objetivo

Construir un data lake simple: raw → processing → curated.

**Flujo:**
```
CSV Files (SFTP Upload)
    ↓
MinIO Bucket (raw/)
    ↓
Spark Processing
    ↓
MinIO Bucket (processed/)
    ↓
SQL Server (Catalog)
```

### 2.2 Setup

#### Paso 1: Crear Buckets en MinIO

```powershell
docker-compose -f storage/docker-compose-storage.yml exec minio mc alias set minio http://localhost:9000 admin minioadmin

# Crear buckets
docker-compose -f storage/docker-compose-storage.yml exec minio mc mb minio/raw
docker-compose -f storage/docker-compose-storage.yml exec minio mc mb minio/processed
docker-compose -f storage/docker-compose-storage.yml exec minio mc mb minio/curated
```

#### Paso 2: Subir Datos CSV

Crear archivo de prueba `sales.csv`:
```
date,product,quantity,price
2024-01-01,Laptop,5,999.99
2024-01-01,Mouse,10,29.99
2024-01-02,Keyboard,8,79.99
```

```powershell
# Subir a MinIO
docker-compose -f storage/docker-compose-storage.yml exec minio \
  mc cp /tmp/sales.csv minio/raw/sales.csv
```

#### Paso 3: Procesar con Spark

En Jupyter:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum as spark_sum, avg, count

spark = SparkSession.builder \
    .appName("DataLakePipeline") \
    .getOrCreate()

# Configurar MinIO
spark.conf.set("fs.s3a.endpoint", "http://minio:9000")
spark.conf.set("fs.s3a.access.key", "admin")
spark.conf.set("fs.s3a.secret.key", "minioadmin")
spark.conf.set("fs.s3a.path.style.access", "true")

# Leer datos raw
df_raw = spark.read.csv("s3a://raw/sales.csv", header=True, inferSchema=True)

print("Raw data:")
df_raw.show()

# Procesar
df_processed = df_raw \
    .withColumn("date", to_date(col("date"), "yyyy-MM-dd")) \
    .withColumn("quantity", col("quantity").cast("integer")) \
    .withColumn("price", col("price").cast("decimal(10,2)")) \
    .withColumn("total", col("quantity") * col("price"))

# Guardar procesado
df_processed.write \
    .mode("overwrite") \
    .parquet("s3a://processed/sales_processed.parquet")

print("✓ Datos procesados guardados en s3a://processed/")

# Agregar datos (curated layer)
df_curated = df_processed.groupBy("date", "product") \
    .agg(
        count("*").alias("transactions"),
        spark_sum("quantity").alias("total_quantity"),
        spark_sum("total").alias("total_revenue"),
        avg("price").alias("avg_price")
    )

df_curated.show()

# Guardar curado
df_curated.write \
    .mode("overwrite") \
    .parquet("s3a://curated/sales_summary.parquet")

print("✓ Datos curados guardados en s3a://curated/")

# Guardar en SQL Server para catalog
df_curated.write \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[TestDB].[dbo].[sales_summary]") \
    .option("user", "sa") \
    .option("password", "tu-contraseña") \
    .mode("overwrite") \
    .save()

print("✓ Catalog actualizado en SQL Server")
```

---

## Patrón 3: ML Pipeline (Datos → Jupyter → MLflow → Airflow)

### 3.1 Objetivo

Pipeline completo de ML: experiment tracking, model registry, y scheduled training.

**Flujo:**
```
SQL Server (Training Data)
    ↓
Jupyter Notebook
    ↓
Feature Engineering & Training
    ↓
MLflow (Model Registry)
    ↓
Airflow (Schedule Retraining)
```

### 3.2 Ejemplo: Predicción de Precios

#### Paso 1: Crear Tabla de Entrenamiento

```powershell
docker-compose -f storage/docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa

CREATE TABLE house_prices (
  id INT PRIMARY KEY,
  square_feet INT,
  bedrooms INT,
  bathrooms INT,
  age_years INT,
  price DECIMAL(12,2)
);

INSERT INTO house_prices VALUES (1, 2000, 3, 2, 10, 450000);
INSERT INTO house_prices VALUES (2, 1500, 2, 1, 20, 300000);
INSERT INTO house_prices VALUES (3, 3000, 4, 3, 5, 600000);
INSERT INTO house_prices VALUES (4, 1800, 3, 2, 15, 400000);
INSERT INTO house_prices VALUES (5, 2500, 4, 2, 8, 550000);

GO
EXIT
```

#### Paso 2: Jupyter - Entrenar Modelo

```python
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
import mlflow
import mlflow.spark

spark = SparkSession.builder \
    .appName("HousePricePrediction") \
    .getOrCreate()

# Setup MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("house-price-prediction")

# Leer datos desde SQL Server
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[TestDB].[dbo].[house_prices]") \
    .option("user", "sa") \
    .option("password", "tu-contraseña") \
    .load()

df.show()

# Feature Engineering
assembler = VectorAssembler(
    inputCols=["square_feet", "bedrooms", "bathrooms", "age_years"],
    outputCol="features"
)

# Modelo
rf = RandomForestRegressor(
    numTrees=10,
    maxDepth=5,
    seed=42,
    labelCol="price",
    featuresCol="features"
)

pipeline = Pipeline(stages=[assembler, rf])

# Track con MLflow
with mlflow.start_run():
    # Entrenar
    model = pipeline.fit(df)
    
    # Predecir
    predictions = model.transform(df)
    
    # Evaluar
    evaluator = RegressionEvaluator(labelCol="price", predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    r2 = evaluator.setMetricName("r2").evaluate(predictions)
    
    # Log metrics
    mlflow.log_param("num_trees", 10)
    mlflow.log_param("max_depth", 5)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    
    # Log modelo
    mlflow.spark.log_model(model, "house_price_model")
    
    print(f"RMSE: {rmse:.2f}")
    print(f"R2: {r2:.4f}")
    print(f"✓ Modelo registrado en MLflow")

# Hacer predicción
new_house = spark.createDataFrame([
    (2200, 3, 2, 12)
], ["square_feet", "bedrooms", "bathrooms", "age_years"])

new_pred = model.transform(new_house)
print(f"\nPredicción para casa nueva: ${new_pred.select('prediction').collect()[0][0]:,.2f}")
```

#### Paso 3: Airflow - Schedule Retraining

Crear `databricks/dags/retrain_model_dag.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'retrain_house_price_model',
    default_args=default_args,
    description='Retrain house price model daily',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

def retrain_model():
    import subprocess
    # Ejecutar notebook de training
    subprocess.run([
        'spark-submit',
        '/opt/spark-apps/train_model.py'
    ])

task_retrain = PythonOperator(
    task_id='retrain_model',
    python_callable=retrain_model,
    dag=dag,
)

task_notify = BashOperator(
    task_id='notify_completion',
    bash_command='echo "Model retrained successfully" | mail -s "Model Retrain" admin@example.com',
    dag=dag,
)

task_retrain >> task_notify
```

---

## Patrón 4: Real-time Analytics (Kafka → Spark Streaming → Storage)

### 4.1 Objetivo

Análisis en tiempo real: procesar eventos Kafka y guardar agregaciones.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, avg, sum as spark_sum
import json

spark = SparkSession.builder \
    .appName("RealtimeAnalytics") \
    .getOrCreate()

# Leer desde Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "events") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON events
from pyspark.sql.functions import from_json

schema = StructType([
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("amount", DecimalType(10, 2)),
    StructField("timestamp", TimestampType())
])

events = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Agregaciones por ventana de 5 minutos
analytics = events \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window("timestamp", "5 minutes"),
        "event_type"
    ) \
    .agg(
        count("*").alias("event_count"),
        avg("amount").alias("avg_amount"),
        spark_sum("amount").alias("total_amount")
    )

# Escribir a SQL Server
query = analytics \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoint_analytics") \
    .foreachBatch(lambda df, batchId: write_analytics(df, batchId)) \
    .start()

def write_analytics(df, batchId):
    df.select(
        col("window.start"),
        col("window.end"),
        col("event_type"),
        col("event_count"),
        col("avg_amount"),
        col("total_amount")
    ).write \
        .format("jdbc") \
        .option("url", "jdbc:sqlserver://sqlserver:1433") \
        .option("dbtable", "[TestDB].[dbo].[realtime_analytics]") \
        .option("user", "sa") \
        .option("password", "tu-contraseña") \
        .mode("append") \
        .save()

query.awaitTermination()
```

---

## Patrón 5: ETL Automático (Airflow Orchestrating Everything)

### 5.1 DAG Complejo

Crear `databricks/dags/full_etl_pipeline.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.models import Variable

default_args = {
    'owner': 'data-eng',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

dag = DAG(
    'full_etl_pipeline',
    default_args=default_args,
    description='Full ETL: Extract → Transform → Load',
    schedule_interval='0 2 * * *',  # 2 AM diario
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# Task 1: Extraer de PostgreSQL
extract = BashOperator(
    task_id='extract_data',
    bash_command='''
        spark-submit --class ExtractData \
        /opt/spark-apps/etl.jar \
        --source postgres-cdc \
        --output s3a://raw/{{ ds }}/
    ''',
    dag=dag,
)

# Task 2: Transformar
transform = PythonOperator(
    task_id='transform_data',
    python_callable=lambda: subprocess.run([
        'spark-submit',
        '/opt/spark-apps/transform.py',
        '--input', 's3a://raw/{{ ds }}/',
        '--output', 's3a://processed/{{ ds }}/'
    ]),
    dag=dag,
)

# Task 3: Cargar a SQL Server
load = BashOperator(
    task_id='load_to_warehouse',
    bash_command='''
        spark-submit --class LoadData \
        /opt/spark-apps/etl.jar \
        --source s3a://processed/{{ ds }}/ \
        --target sql-server \
        --table warehouse_facts
    ''',
    dag=dag,
)

# Task 4: Actualizar catalog en MLflow
update_catalog = PythonOperator(
    task_id='update_catalog',
    python_callable=lambda: update_mlflow_registry('warehouse_facts', '{{ ds }}'),
    dag=dag,
)

# Task 5: Notificar
notify = BashOperator(
    task_id='notify_completion',
    bash_command='curl -X POST http://slack.com/notify -d "ETL completed for {{ ds }}"',
    dag=dag,
)

# Definir dependencias
extract >> transform >> load >> update_catalog >> notify
```

---

## 📊 Monitoreo de Integraciones

```python
# Verificar salud de pipelines
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HealthCheck").getOrCreate()

# Contar eventos en Kafka
kafka_count = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "events") \
    .load() \
    .count()

# Contar registros en SQL Server
sql_count = spark.read.jdbc(
    "jdbc:sqlserver://sqlserver:1433",
    "[TestDB].[dbo].[facts]",
    {"user": "sa", "password": "pwd"}
).count()

print(f"Kafka Events: {kafka_count}")
print(f"SQL Server Facts: {sql_count}")
print(f"Lag: {kafka_count - sql_count} events")
```

---

## 🔗 Relacionado

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Patrones de integración
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Comandos rápidos
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Solucionar problemas

---

<div align="center">

**Pon estos patrones en producción con precaución.**

[📖 README](./README.md) | [🔗 INTEGRATIONS](./INTEGRATIONS.md) | [🔐 SECURITY](./SECURITY.md)

</div>

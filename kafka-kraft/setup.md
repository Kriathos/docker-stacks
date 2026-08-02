# 🚀 Setup Kafka KRaft Stack

Guía paso a paso para iniciar el stack de Kafka con arquitectura KRaft (moderno, sin Zookeeper).

**Tiempo estimado:** 20-30 minutos

---

## ✅ Pre-requisitos

- ✅ Docker Desktop instalado y corriendo
- ✅ Red `mynet` creada: `docker network create mynet`
- ✅ 4GB RAM mínimo (8GB recomendado)
- ✅ 15GB disco disponible
- ✅ PostgreSQL corriendo (para CDC - opcional pero recomendado)

---

## 🤔 ¿Qué es KRaft?

**KRaft** = Kafka Raft Consensus

- Arquitectura **moderna** de Kafka (disponible desde v3.3)
- **Sin Zookeeper** (elimina dependencia externa)
- **Quórum de brokers** para coordinación
- **Menos overhead** operacional
- **Más escalable** para clusters grandes

**Recomendado para:** Nuevos proyectos, producción moderna

---

## 📁 Paso 1: Revisar Configuración

### 1.1 Verificar Archivo de Composición

```powershell
# Navegar al directorio
cd .\kafka-kraft

# Ver contenido
cat docker-compose.yml | Select-String "KAFKA_"
```

**Configuración esperada KRaft:**
```yaml
environment:
  KAFKA_NODE_ID: 1
  KAFKA_PROCESS_ROLES: "broker,controller"
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
  KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka1:29093,2@kafka2:29093,3@kafka3:29093"
```

### 1.2 Entender la Estructura

```
3 Brokers Kafka
├── kafka1 (Node ID 1) - Broker + Controller
├── kafka2 (Node ID 2) - Broker + Controller
└── kafka3 (Node ID 3) - Broker + Controller

Sin Zookeeper
→ Coordinación mediante Quórum Raft
```

---

## 🚀 Paso 2: Iniciar Kafka KRaft Stack

### 2.1 Iniciar Servicios

```powershell
# Navegar al directorio
cd .\kafka-kraft

# Iniciar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE               NAMES
xxxxx          confluentinc/cp-kafka   kafka1
xxxxx          confluentinc/cp-kafka   kafka2
xxxxx          confluentinc/cp-kafka   kafka3
xxxxx          confluentinc/cp-kafka   kafka-ui
xxxxx          postgres:13         postgres-cdc
xxxxx          debezium/connect    debezium-connect
```

### 2.2 Esperar a que Inicien

Los brokers KRaft tardan **30-60 segundos** en estabilizarse:

```powershell
# Ver logs de Kafka para verificar inicialización
docker-compose logs -f kafka1

# Buscar estos mensajes de éxito:
# "[KafkaRaftClient StateStore] Snapshot"
# "[Broker] Started up successfully"
# "[BrokerServer] Active log stored"

# Cuando veas esto, los brokers están listos:
# "Transitioning from STARTING to RECOVERY"
# "Transitioning from RECOVERY to RUNNING"
```

**Esperar confirmación (puede tomar 60+ segundos):**

```powershell
# Opción 1: Esperar con timeout
Start-Sleep -Seconds 60

# Opción 2: Monitorear hasta listo
docker-compose logs -f kafka1 | Select-String "RUNNING"
```

---

## ✅ Paso 3: Verificar Conectividad

### 3.1 Listar Brokers

```powershell
# Ver información del cluster
docker-compose exec kafka1 kafka-broker-api-versions.sh --bootstrap-server kafka1:9092

# Deberías ver la versión de Kafka y APIs soportadas
```

### 3.2 Listar Metadatos

```powershell
# Ver información de quórum y brokers
docker-compose exec kafka1 kafka-metadata.sh \
  --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log \
  --print

# Salida esperada:
# Current leader: 1
# Quorum voters: 1,2,3
```

### 3.3 Test de Comunicación

```powershell
# Ping entre brokers
docker-compose exec kafka1 nc -zv kafka2:29092
docker-compose exec kafka1 nc -zv kafka3:29092

# Deberías ver: "succeeded"
```

### 3.4 Verificar PostgreSQL para CDC

```powershell
# Si tienes PostgreSQL corriendo
docker-compose exec postgres-cdc psql -U postgres -d demo -c "SELECT version();"

# Deberías ver versión de PostgreSQL
```

---

## 📊 Paso 4: Crear Topics

### 4.1 Crear Topic Simple

```powershell
# Crear topic de prueba
docker-compose exec kafka1 kafka-topics.sh \
  --create \
  --topic test-topic \
  --bootstrap-server kafka1:9092 \
  --partitions 3 \
  --replication-factor 3

# Verificar creación
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092
```

**Esperado:** Deberías ver `test-topic` en la lista

### 4.2 Ver Detalles del Topic

```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --describe \
  --topic test-topic \
  --bootstrap-server kafka1:9092

# Salida esperada:
# Topic: test-topic
# Partition: 0  Leader: 1  Replicas: 1,2,3
# Partition: 1  Leader: 2  Replicas: 2,3,1
# Partition: 2  Leader: 3  Replicas: 3,1,2
```

---

## 📤 Paso 5: Enviar y Consumir Mensajes

### 5.1 Productor (Enviar Mensajes)

```powershell
# Abrir terminal interactiva de productor
docker-compose exec kafka1 kafka-console-producer.sh \
  --broker-list kafka1:9092 \
  --topic test-topic

# Escribe mensajes (uno por línea):
# Mensaje 1
# Mensaje 2
# Mensaje 3

# Presiona Ctrl+C para salir
```

### 5.2 Consumidor (Leer Mensajes)

En otra ventana PowerShell:

```powershell
# Abrir terminal de consumidor (desde el inicio)
docker-compose exec kafka1 kafka-console-consumer.sh \
  --bootstrap-server kafka1:9092 \
  --topic test-topic \
  --from-beginning

# Deberías ver los mensajes que enviaste
# Presiona Ctrl+C para salir
```

---

## 🔄 Paso 6: Configurar CDC con Debezium (Opcional)

Si tienes PostgreSQL en Storage Stack o aquí:

### 6.1 Verificar Conectividad a PostgreSQL

```powershell
# Verificar que PostgreSQL está accesible desde Debezium
docker-compose exec postgres-cdc psql -U postgres -d demo -c "\du"

# Si no funciona, verificar logs
docker-compose logs postgres-cdc
```

### 6.2 Crear Publicación en PostgreSQL

```powershell
# Conectar a PostgreSQL
docker-compose exec postgres-cdc psql -U postgres -d demo

# Ejecutar (en el prompt psql):
CREATE PUBLICATION dbz_publication FOR ALL TABLES;

# Verificar
\dP

# Salir
\q
```

### 6.3 Crear Connector en Debezium

```powershell
# Registrar connector PostgreSQL
Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8083/connectors" `
  -ContentType "application/json" `
  -Body @"
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres-cdc",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "demo",
    "database.server.name": "postgres",
    "publication.name": "dbz_publication",
    "slot.name": "dbz_slot",
    "plugin.name": "pgoutput",
    "table.include.list": "public.*"
  }
}
"@

# Ver conectores
Invoke-RestMethod -Uri "http://localhost:8083/connectors"

# Deberías ver: ["postgres-connector"]
```

### 6.4 Verificar Topics CDC

```powershell
# Listar topics (ahora incluye postgres.*)
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092

# Esperado: tópicos como:
# postgres.public.users
# postgres.public.orders
# etc.
```

---

## 🌐 Paso 7: Kafka UI (Dashboard)

### 7.1 Acceder a Kafka UI

```
URL: http://kafka-ui.local:8080
(o http://localhost:8080 si no configuraste hosts)

Sin autenticación requerida
```

**En Kafka UI verás:**
- Brokers (3 nodos KRaft)
- Topics y particiones
- Consumer groups
- Mensajes en tiempo real
- Connectors de Debezium

### 7.2 Crear Topic desde UI

1. Click "Topics" → "Create Topic"
2. Name: `my-events`
3. Partitions: `3`
4. Replication Factor: `3`
5. Click "Create"

---

## 🔗 Paso 8: Integración con Otros Stacks

### 8.1 Consumir desde Spark (Databricks Stack)

```python
# En Jupyter Notebook

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaConsumer") \
    .getOrCreate()

# Consumir desde Kafka KRaft
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "test-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Mostrar esquema
df.printSchema()

# Mostrar datos
df.select("value") \
    .writeStream \
    .format("console") \
    .option("truncate", False) \
    .start() \
    .awaitTermination(30)
```

### 8.2 Replicar de PostgreSQL via CDC

```
PostgreSQL (Storage o aquí)
    ↓
Debezium Connect
    ↓
Kafka Topics (postgres.public.*)
    ↓
Spark Streaming (Databricks)
    ↓
SQL Server / MinIO (Storage)
```

**Ver logs de replicación:**
```powershell
docker-compose logs -f debezium-connect
```

---

## 🛑 Paso 9: Detener Stack

### 9.1 Detener Servicios

```powershell
# Detener pero mantener datos
docker-compose down

# Verificar
docker ps | findstr kafka
# No debe haber resultados
```

### 9.2 Limpiar (⚠️ Borra datos)

```powershell
# Eliminar volúmenes
docker-compose down -v

# Ver volúmenes eliminados
docker volume ls | findstr kafka
```

---

## 🆘 Troubleshooting

### Problema: "Broker failed to start"

**Síntoma:** Container se detiene inmediatamente

**Soluciones:**
1. Verificar logs: `docker-compose logs kafka1`
2. Esperar más tiempo (primer inicio tarda ~60 seg)
3. Aumentar RAM de Docker Desktop
4. Revisar que la red `mynet` existe

### Problema: "Brokers not initializing"

**Síntoma:** Logs muestran "Transitioning" pero se detiene

**Soluciones:**
1. Esperar más tiempo (hasta 120 segundos)
2. Ver logs de todos los brokers: `docker-compose logs`
3. Verificar KAFKA_CONTROLLER_QUORUM_VOTERS en docker-compose.yml
4. Reintentar: `docker-compose restart`

### Problema: "Cannot connect to broker"

**Síntoma:** Error al crear topics o enviar mensajes

**Soluciones:**
1. Verificar brokers corriendo: `docker-compose ps`
2. Esperar inicialización completa
3. Verificar red: `docker network inspect mynet | grep kafka`
4. Ver logs: `docker-compose logs kafka1`

### Problema: "Debezium connector fails"

**Síntoma:** Error registrando CDC connector

**Soluciones:**
1. Verificar PostgreSQL accesible: `docker-compose exec postgres-cdc psql...`
2. Crear publicación en PostgreSQL primero
3. Verificar credenciales correctas
4. Ver logs de Debezium: `docker-compose logs debezium-connect`

### Problema: "Kafka UI no conecta"

**Síntoma:** Kafka UI muestra "Offline"

**Soluciones:**
1. Verificar kafka1 corriendo
2. Revisar que kafka-ui puede acceder a kafka1:9092
3. Reintentar actualizar página
4. Ver logs: `docker-compose logs kafka-ui`

---

## ✅ Checklist de Verificación

Una vez completado el setup:

- [ ] Todos los contenedores corriendo (`docker-compose ps`)
- [ ] Kafka logs muestran "RUNNING"
- [ ] Brokers listar correctamente
- [ ] Topic de prueba creado
- [ ] Productor-consumidor funcionando
- [ ] Kafka UI accesible y muestra brokers
- [ ] PostgreSQL conecta (si configuraste CDC)
- [ ] Debezium connector registrado (opcional)
- [ ] Topics CDC aparecen (postgres.*)
- [ ] Spark puede consumir desde Kafka (test)

---

## 📚 Siguientes Pasos

1. **Explorar Kafka**
   - Crear más topics
   - Entender particiones y replication
   - Monitorear con Kafka UI

2. **Integrar CDC**
   - Configurar completamente Debezium
   - Replicar tablas PostgreSQL
   - Monitorear cambios en tiempo real

3. **Consumir desde Spark**
   - Procesar eventos Kafka
   - Escribir a Storage
   - Crear pipelines

4. **Producción**
   - Monitoreo con Prometheus/Grafana
   - Backup y recovery
   - Security (SASL/SCRAM)

---

## 🔍 Comandos Útiles

```powershell
# Ver estado del cluster
docker-compose exec kafka1 kafka-metadata.sh --snapshot ... --print

# Listar todos los topics
docker-compose exec kafka1 kafka-topics.sh --list --bootstrap-server kafka1:9092

# Ver detalles de topic
docker-compose exec kafka1 kafka-topics.sh --describe --topic test-topic --bootstrap-server kafka1:9092

# Ver consumer groups
docker-compose exec kafka1 kafka-consumer-groups.sh --list --bootstrap-server kafka1:9092

# Ver logs de offset
docker-compose exec kafka1 kafka-consumer-groups.sh --describe --group test-group --bootstrap-server kafka1:9092

# Eliminar topic
docker-compose exec kafka1 kafka-topics.sh --delete --topic test-topic --bootstrap-server kafka1:9092
```

---

<div align="center">

[📖 Leer README](../kafka-kraft/README.md) • [⚙️ Ver config](../kafka-kraft/config.md) • [🚀 Leer SETUP central](../SETUP.md)

</div>

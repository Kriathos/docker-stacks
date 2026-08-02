# 🚀 Setup Kafka + Zookeeper Stack

Guía paso a paso para iniciar el stack de Kafka con arquitectura clásica (Zookeeper + Kafka).

**Tiempo estimado:** 25-35 minutos

---

## ✅ Pre-requisitos

- ✅ Docker Desktop instalado y corriendo
- ✅ Red `mynet` creada: `docker network create mynet`
- ✅ 4GB RAM mínimo (8GB recomendado)
- ✅ 15GB disco disponible
- ✅ PostgreSQL corriendo (para CDC - opcional pero recomendado)

---

## 🤔 ¿Cuándo Usar Zookeeper?

**Zookeeper + Kafka** es la arquitectura **tradicional** de Kafka

**Características:**
- Arquitectura **probada** en producción
- Zookeeper coordinador externo
- Compatible con ecosistema maduro
- Bien documentada

**Recomendado para:**
- Migración de sistemas legacy
- Cuando necesitas máxima compatibilidad
- Equipos familiarizados con Zookeeper
- Debugging de problemas complejos

**Comparativa con KRaft:**
| Característica | Zookeeper | KRaft |
|---|---|---|
| Complejidad | Media | Baja |
| Componentes | 3 ZK + 3 Kafka | 3 Kafka |
| Latencia | Mayor | Menor |
| Estado Productivo | ✅ GA | ✅ GA (v3.3+) |
| Recomendación | Legacy | Nuevo |

---

## 📁 Paso 1: Revisar Configuración

### 1.1 Verificar Archivo de Composición

```powershell
# Navegar al directorio
cd .\kafka-zookeeper

# Ver configuración de Zookeeper
cat docker-compose.yml | Select-String "zookeeper"

# Ver configuración de Kafka
cat docker-compose.yml | Select-String "KAFKA_ZOOKEEPER"
```

**Configuración esperada:**
```yaml
zookeeper:
  environment:
    ZOO_CFG_EXTRA: "server.1=zookeeper1:2888:3888 server.2=zookeeper2:2888:3888 server.3=zookeeper3:2888:3888"
    ZOO_MY_ID: 1

kafka:
  environment:
    KAFKA_ZOOKEEPER_CONNECT: "zookeeper1:2181,zookeeper2:2181,zookeeper3:2181"
```

### 1.2 Entender la Arquitectura

```
Zookeeper Cluster (3 nodos)
├── zookeeper1 (Server ID 1)
├── zookeeper2 (Server ID 2)
└── zookeeper3 (Server ID 3)
    ↓
    Coordina
    ↓
Kafka Brokers (3 nodos)
├── kafka1 (Broker ID 1)
├── kafka2 (Broker ID 2)
└── kafka3 (Broker ID 3)
```

---

## 🚀 Paso 2: Iniciar Zookeeper Ensemble

### 2.1 Iniciar Stack

```powershell
# Navegar al directorio
cd .\kafka-zookeeper

# Iniciar todos los servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE                  NAMES
xxxxx          confluentinc/cp-zookeeper   zookeeper1
xxxxx          confluentinc/cp-zookeeper   zookeeper2
xxxxx          confluentinc/cp-zookeeper   zookeeper3
xxxxx          confluentinc/cp-kafka       kafka1
xxxxx          confluentinc/cp-kafka       kafka2
xxxxx          confluentinc/cp-kafka       kafka3
xxxxx          confluentinc/cp-kafka       kafka-ui
xxxxx          postgres:13             postgres-cdc
xxxxx          debezium/connect        debezium-connect
```

### 2.2 Esperar a que Inicien

Zookeeper tarda **MÁS tiempo** que KRaft:

```powershell
# Zookeeper: ~30-60 segundos (election + quorum)
# Kafka: ~30-45 segundos (esperar conexión a ZK)

# Monitorear inicialización
docker-compose logs -f zookeeper1

# Buscar este mensaje de éxito:
# "Server startup"
# "Started AdminServer"

# Luego monitorear Kafka
docker-compose logs -f kafka1

# Buscar:
# "[Kafka Server] started"
# "Registered broker"
```

**Esperar confirmación completa (60-90 segundos):**

```powershell
# Opción 1: Esperar fijo
Start-Sleep -Seconds 90

# Opción 2: Verificar logs
docker-compose logs | Select-String "Server startup" | Measure-Object
# Si ves 3 líneas (3 ZK nodes), está listo
```

---

## ✅ Paso 3: Verificar Zookeeper Ensemble

### 3.1 Conectar a Zookeeper

```powershell
# Conectar a ZK y ver estado
docker-compose exec zookeeper1 zkServer.sh status

# Esperado: "Mode: leader" o "Mode: follower"
```

### 3.2 Listar Brokers Registrados

```powershell
# Ver brokers en Zookeeper
docker-compose exec zookeeper1 zkCli.sh <<EOF
ls /brokers/ids
quit
EOF

# Deberías ver: [1, 2, 3]
```

### 3.3 Verificar Quórum

```powershell
# Ver detalles del ensemble
docker-compose logs zookeeper1 | Select-String "Mode:"

# Esperado:
# zookeeper1: Mode: leader (o follower)
# zookeeper2: Mode: follower
# zookeeper3: Mode: follower
```

---

## ✅ Paso 4: Verificar Kafka Brokers

### 4.1 Conectar a Kafka

```powershell
# Ver información de brokers
docker-compose exec kafka1 kafka-broker-api-versions.sh --bootstrap-server kafka1:9092

# Deberías ver versión de Kafka
```

### 4.2 Listar Brokers

```powershell
# Ver todos los brokers registrados
docker-compose exec kafka1 kafka-metadata.sh --snapshot /var/kafka/logs/__cluster_metadata-0/00000000000000000000.log --print

# O via Zookeeper
docker-compose exec zookeeper1 zkCli.sh <<EOF
ls /brokers/ids
get /brokers/ids/1
quit
EOF
```

### 4.3 Verificar Coordinador de Controlador

```powershell
# En arquitectura Zookeeper, un broker es "Controller"
# Ver cuál es el controlador
docker-compose logs | Select-String "becomes New Controller"

# Esperado: Uno de los brokers es elegido Controller
```

---

## 📊 Paso 5: Crear Topics

### 5.1 Crear Topic Simple

```powershell
# Crear topic
docker-compose exec kafka1 kafka-topics.sh \
  --create \
  --topic test-topic \
  --bootstrap-server kafka1:9092 \
  --partitions 3 \
  --replication-factor 3

# Listar topics
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092

# Deberías ver: test-topic
```

### 5.2 Ver Detalles del Topic

```powershell
docker-compose exec kafka1 kafka-topics.sh \
  --describe \
  --topic test-topic \
  --bootstrap-server kafka1:9092

# Salida esperada:
# Topic: test-topic
# Partition: 0  Leader: 2  Replicas: 2,3,1  Isr: 2,3,1
# Partition: 1  Leader: 3  Replicas: 3,1,2  Isr: 3,1,2
# Partition: 2  Leader: 1  Replicas: 1,2,3  Isr: 1,2,3
```

---

## 📤 Paso 6: Enviar y Consumir Mensajes

### 6.1 Productor (Enviar Mensajes)

```powershell
# Abrir terminal de productor
docker-compose exec kafka1 kafka-console-producer.sh \
  --broker-list kafka1:9092,kafka2:9093,kafka3:9094 \
  --topic test-topic

# Escribe mensajes:
# Mensaje test 1
# Mensaje test 2
# Mensaje test 3

# Ctrl+C para salir
```

### 6.2 Consumidor (Leer Mensajes)

En otra ventana:

```powershell
# Consumidor desde el inicio
docker-compose exec kafka1 kafka-console-consumer.sh \
  --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 \
  --topic test-topic \
  --from-beginning

# Deberías ver los mensajes anteriores
# Ctrl+C para salir
```

---

## 🔄 Paso 7: Configurar CDC con Debezium

### 7.1 Crear Publicación en PostgreSQL

```powershell
# Conectar a PostgreSQL
docker-compose exec postgres-cdc psql -U postgres -d demo

# Crear publicación
CREATE PUBLICATION dbz_publication FOR ALL TABLES;
\dP

# Salir
\q
```

### 7.2 Crear Connector en Debezium

```powershell
# Registrar conector PostgreSQL
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

# Verificar
Invoke-RestMethod -Uri "http://localhost:8083/connectors"
```

### 7.3 Verificar Topics CDC

```powershell
# Listar todos los topics (incluye postgres.*)
docker-compose exec kafka1 kafka-topics.sh \
  --list \
  --bootstrap-server kafka1:9092

# Esperado: tópicos como postgres.public.users, etc.
```

---

## 🌐 Paso 8: Kafka UI (Dashboard)

### 8.1 Acceder a Kafka UI

```
URL: http://kafka-ui.local:8080
(o http://localhost:8080)

Muestra:
- Zookeeper ensemble status
- Brokers (3 nodos Kafka)
- Topics y particiones
- Consumer groups
- Mensajes
```

### 8.2 Monitorear desde UI

1. Click "Cluster"
   - Ver Zookeeper nodes
   - Ver Kafka brokers

2. Click "Topics"
   - Ver topics disponibles
   - Ver lag de consumer groups

3. Click "Brokers"
   - Ver líder y followers
   - Ver replicación

---

## 🔗 Paso 9: Integración con Otros Stacks

### 9.1 Consumir desde Spark

```python
# En Jupyter Notebook (Databricks Stack)

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaConsumer") \
    .getOrCreate()

# Consumir desde Kafka (Zookeeper)
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092") \
    .option("subscribe", "test-topic") \
    .option("startingOffsets", "earliest") \
    .load()

df.select("value") \
    .writeStream \
    .format("console") \
    .start() \
    .awaitTermination(30)
```

### 9.2 Replicar cambios via CDC

```
PostgreSQL → Debezium → Kafka Topics → Spark → Storage
```

---

## 🛑 Paso 10: Detener Stack

### 10.1 Detener Servicios

```powershell
# Detener
docker-compose down

# Verificar
docker ps | findstr kafka
docker ps | findstr zookeeper
```

### 10.2 Limpiar (⚠️ Borra datos)

```powershell
docker-compose down -v
```

---

## 🆘 Troubleshooting

### Problema: "Zookeeper fails to start"

**Síntoma:** Container zookeeper se detiene

**Soluciones:**
1. Ver logs: `docker-compose logs zookeeper1`
2. Esperar más tiempo (Zookeeper election tarda ~60 seg)
3. Verificar red `mynet` existe
4. Revisar que no hay conflicto de puertos 2181, 2888, 3888

### Problema: "Kafka cannot connect to Zookeeper"

**Síntoma:** Kafka logs muestran "Cannot connect to Zookeeper"

**Soluciones:**
1. Esperar a que Zookeeper esté completamente iniciado
2. Verificar que Zookeeper ensemble estable: `docker-compose logs zookeeper1 | grep Mode`
3. Verificar KAFKA_ZOOKEEPER_CONNECT correcta en docker-compose.yml
4. Reintentar: `docker-compose restart`

### Problema: "Cannot create topic"

**Síntoma:** Error al crear topic

**Soluciones:**
1. Esperar a que Kafka esté completamente iniciado
2. Verificar brokers registrados: `docker-compose logs | Select-String "broker/"`
3. Verificar que hay 3 brokers: `docker-compose exec kafka1 kafka-broker-api-versions.sh...`
4. Revisar si topic ya existe

### Problema: "Debezium connector fails"

**Síntoma:** Error registrando connector CDC

**Soluciones:**
1. Verificar PostgreSQL conecta
2. Verificar publicación creada: `\dP` en psql
3. Verificar credenciales PostgreSQL
4. Ver logs: `docker-compose logs debezium-connect`

### Problema: "Zookeeper ensemble not quorum"

**Síntoma:** Solo 1 o 2 ZK nodes started, no elección líder

**Soluciones:**
1. Esperar más tiempo (~120 segundos)
2. Verificar todas los zookeeper containers corriendo
3. Revisar los ZOO_MY_ID están diferentes (1, 2, 3)
4. Revisar ZOO_CFG_EXTRA bien formateado

---

## ✅ Checklist de Verificación

Una vez completado el setup:

- [ ] 3 Zookeeper nodes corriendo
- [ ] 3 Kafka brokers corriendo
- [ ] Zookeeper ensemble elegido líder
- [ ] Brokers registrados en Zookeeper
- [ ] Un broker elegido Controller
- [ ] Topic de prueba creado
- [ ] Productor-consumidor funcionando
- [ ] Kafka UI muestra cluster
- [ ] PostgreSQL conecta (si CDC)
- [ ] Debezium connector registrado (opcional)
- [ ] Topics CDC aparecen (postgres.*)
- [ ] Spark consume desde Kafka (test)

---

## 📚 Siguientes Pasos

1. **Explorar Kafka**
   - Crear más topics
   - Monitorear con Kafka UI
   - Entender replication factor

2. **Integrar CDC**
   - Capturar cambios PostgreSQL
   - Replicar a Kafka
   - Consumir cambios en Spark

3. **Producción**
   - Configurar SASL/SCRAM
   - Setup Prometheus/Grafana
   - Backup y recovery

---

## 🔍 Comandos Útiles

```powershell
# Ver estado de Zookeeper ensemble
docker-compose exec zookeeper1 zkServer.sh status

# Ver brokers en Zookeeper
docker-compose exec zookeeper1 zkCli.sh -server localhost:2181 ls /brokers/ids

# Ver controller
docker-compose logs | Select-String "becomes New Controller"

# Listar topics
docker-compose exec kafka1 kafka-topics.sh --list --bootstrap-server kafka1:9092

# Crear topic
docker-compose exec kafka1 kafka-topics.sh --create --topic new-topic --bootstrap-server kafka1:9092 --partitions 3 --replication-factor 3

# Describir topic
docker-compose exec kafka1 kafka-topics.sh --describe --topic test-topic --bootstrap-server kafka1:9092

# Eliminar topic
docker-compose exec kafka1 kafka-topics.sh --delete --topic test-topic --bootstrap-server kafka1:9092
```

---

<div align="center">

[📖 Leer README](../kafka-zookeeper/README.md) • [⚙️ Ver config](../kafka-zookeeper/config.md) • [🚀 Leer SETUP central](../SETUP.md)

</div>

# ⚡ Kafka KRaft Stack

<div align="center">

![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=flat-square&logo=apache-kafka&logoColor=white)
![KRaft](https://img.shields.io/badge/KRaft%20Mode-Modern-brightgreen?style=flat-square)
![Debezium](https://img.shields.io/badge/Debezium-FF6D00?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)

**Arquitectura moderna de Kafka sin Zookeeper**

[Descripción](#descripción) • [Inicio Rápido](#-inicio-rápido) • [Uso](#-uso) • [CDC](#-cdc-change-data-capture)

</div>

---

## 📋 Descripción

Stack de **Kafka KRaft** - arquitectura moderna sin coordinador Zookeeper externo.

**Beneficios:**
- ✅ Cluster con 3 brokers independientes
- ✅ Coordinación integrada
- ✅ Menor complejidad operacional
- ✅ Mejor escalabilidad

---

## 🚀 Inicio Rápido

```powershell
cd .\\kafka-kraft
docker compose up -d
docker compose ps
```

---

## 🛠️ Servicios

| Servicio | Puerto | Rol |
|----------|--------|-----|
| **kafka-1** | 9092 | Broker (Controller) |
| **kafka-2** | 9093 | Broker |
| **kafka-3** | 9094 | Broker |
| **debezium** | 8083 | Kafka Connect |
| **postgres** | 5432 | Source DB |

---

## 💼 Uso

### Crear topic
```powershell
docker compose exec kafka-1 kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic my-topic \
  --partitions 3 --replication-factor 2
```

### Listar topics
```powershell
docker compose exec kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
```

### Producir
```powershell
docker compose exec kafka-1 kafka-console-producer \
  --bootstrap-server localhost:9092 --topic my-topic
```

### Consumir
```powershell
docker compose exec kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 --topic my-topic --from-beginning
```

### Script Python
```powershell
python .\\consumidor-kraft.py
```

---

## 🔄 CDC - Change Data Capture

### Crear conector PostgreSQL
```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": 5432,
      "database.user": "postgres",
      "database.password": "CHANGE_ME",
      "database.dbname": "demo",
      "database.server.name": "demo",
      "plugin.name": "pgoutput"
    }
  }'
```

### Ver conectores
```bash
curl http://localhost:8083/connectors
```

### Consumir eventos CDC
```powershell
docker compose exec kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic demo.public.tabla_nombre \
  --from-beginning
```

---

## 🛑 Operaciones

### Detener
```powershell
docker compose down
```

### Limpiar (⚠️ borra datos)
```powershell
docker compose down -v
```

### Ver logs
```powershell
docker compose logs -f kafka-1
```

---

## ✋ Problemas

| Problema | Solución |
|----------|----------|
| ❌ Broker no inicia | `docker compose logs kafka-1` |
| ❌ Brokers offline | Verificar `mynet` |
| ❌ Topic no se crea | Esperar 30-60 seg |
| ❌ CDC no funciona | Ver Debezium: `curl http://localhost:8083/connectors` |

---

## 📚 Recursos

- [Kafka KRaft](https://kafka.apache.org/documentation/#kraft)
- [Debezium PostgreSQL](https://debezium.io/documentation/reference/latest/connectors/postgresql.html)

---

<div align="center">

[⬆ Arriba](#-kafka-kraft-stack) • [📨 Zookeeper Stack](../kafka-zookeeper/README.md) • [← Kafka](../README.md) • [← Proyecto Principal](../../README.md)

</div>

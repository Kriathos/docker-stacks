# 🐘 Kafka + Zookeeper Stack

<div align="center">

![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=flat-square&logo=apache-kafka&logoColor=white)
![Zookeeper](https://img.shields.io/badge/Zookeeper-Legacy-orange?style=flat-square&logo=apache&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-FF6D00?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)

**Arquitectura clásica de Kafka con coordinador Zookeeper**

[Descripción](#descripción) • [Inicio Rápido](#-inicio-rápido) • [Uso](#-uso) • [CDC](#-cdc)

</div>

---

## 📋 Descripción

Stack de **Kafka + Zookeeper** - arquitectura tradicional y probada.

Esta arquitectura es ideal para:
- 📚 Validar compatibilidad legacy
- 🔄 Migrar sistemas existentes
- 🧪 Debuggear problemas complejos
- ✅ Probada en producción

**Componentes:**
- ✅ Zookeeper para coordinación
- ✅ Broker Kafka clásico
- ✅ Debezium Connect para CDC
- ✅ PostgreSQL como source

---

## 🚀 Inicio Rápido

```powershell
cd .\\kafka-zookeeper
docker compose up -d
docker compose ps
```

---

## 🛠️ Servicios

| Servicio | Puerto | Rol |
|----------|--------|-----|
| **zookeeper** | 2181 | Coordinación |
| **kafka** | 9092 | Broker |
| **debezium** | 8083 | Kafka Connect |
| **postgres** | 5432 | Source DB |

---

## 💼 Uso

### Crear topic
```powershell
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic my-topic \
  --partitions 3 --replication-factor 1
```

### Listar topics
```powershell
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### Producir
```powershell
docker compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:9092 --topic my-topic
```

### Consumir
```powershell
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 --topic my-topic --from-beginning
```

### Script Python
```powershell
python .\\consumidor-zookeeper.py
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
      "database.password": "postgres",
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
docker compose logs -f kafka
```

---

## ✋ Problemas

| Problema | Solución |
|----------|----------|
| ❌ Zookeeper offline | `docker compose logs zookeeper` |
| ❌ Broker no conecta | Verifica Zookeeper primero |
| ❌ Topics no persisten | Revisar volúmenes |

---

## 📚 Recursos

- [Apache Kafka](https://kafka.apache.org/)
- [Zookeeper](https://zookeeper.apache.org/)
- [Debezium](https://debezium.io/)

---

<div align="center">



1. Crea la red Docker `mynet`:

```powershell
docker network create mynet --driver bridge
```

2. Levanta el stack:

```powershell
cd .\kafka\kafka-zookeeper
docker compose up -d
```

3. Verifica que los servicios estén en `Up`:

```powershell
docker compose ps
```

4. Crea la tabla de prueba en PostgreSQL.
5. Despliega el connector en Kafka Connect.
6. Confirma el topic `cdc.public.clientes` en Kafka UI.

## Puertos relevantes

| Servicio | Puerto host | Nota |
|---|---|---|
| Kafka broker | `51435` | Broker principal |
| PostgreSQL | `51436` | Base `demo` |

> Si deseas acceso directo a Kafka UI o Kafka Connect, descomenta los puertos en `docker-compose.yml`.

## KRaft vs Zookeeper

| Pregunta | KRaft | Zookeeper |
|---|---|---|
| ¿Requiere Zookeeper? | No | Sí |
| ¿Ideal para nuevos proyectos? | Sí | No, solo compatibilidad legacy |
| ¿Número de brokers mínimo? | 3 | 1+ |
| ¿Complejidad de operación? | Menor | Mayor |
| ¿Uso en este repo? | `kafka-kraft` | `kafka-zookeeper` |

## Uso del consumidor

Ejecuta el script específico de este stack:

```powershell
python .\consumidor-zookeeper.py
```

### Ejemplo de ejecución

```powershell
python .\consumidor-zookeeper.py --bootstrap-servers localhost:51435 --topic cdc.public.clientes --verbose
```

## Checklist esencial

- [ ] `mynet` creada
- [ ] Containers levantados
- [ ] Tabla `clientes` creada en PostgreSQL
- [ ] Connector Debezium desplegado
- [ ] Topic `cdc.public.clientes` visible en Kafka UI
- [ ] Consumer recibiendo mensajes en tiempo real

## Configuración y credenciales

- Revisa `config.md` para detalles propios de este stack.
- Las credenciales del proyecto se almacenan en el root: `..\credenciales.md`.

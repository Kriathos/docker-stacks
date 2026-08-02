# 📨 Kafka Stack

<div align="center">

![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=flat-square&logo=apache-kafka&logoColor=white)
![Debezium](https://img.shields.io/badge/Debezium-FF6D00?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![Zookeeper](https://img.shields.io/badge/Zookeeper-0074D9?style=flat-square&logo=apache&logoColor=white)

**Plataforma de mensajería, streaming y Change Data Capture**

[Descripción](#descripción) • [Arquitecturas](#-arquitecturas) • [Inicio Rápido](#-inicio-rápido) • [Comparativa](#-comparativa) • [Uso](#-uso)

</div>

---

## 📋 Descripción

Stack de mensajería y streaming empresarial con dos arquitecturas disponibles:

- **KRaft (Moderno)**: Kafka sin Zookeeper, arquitectura distribuida y escalable
- **Zookeeper (Tradicional)**: Kafka clásico con coordinación de cluster

Ambas incluyen **Debezium Connect** para Change Data Capture (CDC) desde PostgreSQL a Kafka en tiempo real.

Perfecto para:
- 🔄 Arquitecturas event-driven
- 📊 Streaming de datos
- 🔄 Replicación de cambios (CDC)
- 📤 Integración entre sistemas
- 🧪 Experimentación con streaming

---

## 🏗️ Arquitecturas

### 1️⃣ Kafka KRaft (Recomendado)

**Cluster moderno de Kafka sin Zookeeper**

```
3 Brokers KRaft
    ↓
Debezium Connect → CDC PostgreSQL → Topics Kafka
    ↓
Consumers
```

📖 [Documentación completa](./kafka-kraft/README.md)

**Características:**
- ✅ 3 brokers Kafka con modo KRaft
- ✅ Mayor escalabilidad
- ✅ Menos complejidad operacional
- ✅ Menos consumo de recursos

**Cuándo usar:**
- Nuevos proyectos
- Producción moderna
- Clusters grandes

---

### 2️⃣ Kafka + Zookeeper (Tradicional)

**Cluster clásico con coordinador Zookeeper**

```
Zookeeper Cluster
    ↓
3 Brokers Kafka
    ↓
Debezium Connect → CDC PostgreSQL → Topics Kafka
    ↓
Consumers
```

📖 [Documentación completa](./kafka-zookeeper/README.md)

**Características:**
- ✅ Zookeeper para coordinación
- ✅ Arquitectura probada
- ✅ Herramientas maduras
- ✅ Compatibilidad histórica

**Cuándo usar:**
- Migración de sistemas legacy
- Compatibilidad garantizada
- Debugging de problemas

---

## 🛠️ Tecnologías Comunes

| Componente | Versión | Propósito |
|-----------|---------|----------|
| **Kafka** | 3.x | Broker de mensajes distribuido |
| **Debezium** | Latest | CDC desde PostgreSQL |
| **PostgreSQL** | 13 | Source para CDC |
| **Kafka UI** | Latest | Monitoreo visual |

---

## 🚀 Inicio Rápido

### Opción 1: KRaft (Moderno) ⭐

```powershell
cd .\kafka-kraft
docker compose up -d
docker compose ps
```

### Opción 2: Zookeeper (Tradicional)

```powershell
cd .\kafka-zookeeper
docker compose up -d
docker compose ps
```

---

## 📊 Comparativa

| Aspecto | KRaft | Zookeeper |
|--------|-------|-----------|
| **Complejidad** | Baja | Media |
| **Escalabilidad** | Alta | Media |
| **Consumo recursos** | Bajo | Medio |
| **Madurez** | Reciente | Muy probada |
| **Brokers mínimos** | 1 | 1 + ZK |

---

## 💼 Uso Común

### Crear un topic

```powershell
docker compose exec kafka-1 kafka-topics --bootstrap-server localhost:9092 --create --topic test-topic --partitions 3 --replication-factor 2
```

### Producir mensajes

```powershell
docker compose exec kafka-1 kafka-console-producer --bootstrap-server localhost:9092 --topic test-topic
```

### Consumir mensajes

```powershell
docker compose exec kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

### Verificar connectors Debezium

```powershell
curl http://localhost:8083/connectors
```

### Ver logs del cluster

```powershell
docker compose logs -f kafka-1
```

### Usar scripts Python

```powershell
# KRaft
python .\kafka-kraft\consumidor-kraft.py

# Zookeeper
python .\kafka-zookeeper\consumidor-zookeeper.py
```

---

## 🔌 Integración con otros stacks

### Databricks
- Spark consume eventos de Kafka para análisis en tiempo real
- MLflow registra modelos para procesamiento

### Storage
- PostgreSQL fuente de CDC via Debezium
- MinIO destino para respaldos de topics

---

## 📁 Estructura

```
kafka/
├── README.md                      # Este archivo
├── kafka-kraft/                   # Stack KRaft moderno
│   ├── docker-compose.yml
│   ├── README.md
│   └── consumidor-kraft.py
├── kafka-zookeeper/               # Stack Zookeeper tradicional
│   ├── docker-compose.yml
│   ├── README.md
│   └── consumidor-zookeeper.py
├── consumer.py                    # Consumidor genérico
└── old/                           # Configuraciones legacy
```

---

## ⚙️ Configuración Global

Todas las credenciales están centralizadas en [`credenciales.md`](../credenciales.md):
- 🔐 Credenciales PostgreSQL
- 🔑 Credenciales Debezium
- 🗝️ Configuración de conectores

---

## 🛑 Detener y limpiar

```powershell
# Detener servicios (mantiene datos)
docker compose down

# Limpiar todo (⚠️ borra datos y volúmenes)
docker compose down -v

# Ver últimos logs
docker compose logs --tail 50
```

---

## ✋ Solución de Problemas

| Problema | Solución |
|----------|----------|
| ❌ Brokers no se comunican | Verificar red `mynet` |
| ❌ CDC no funciona | Revisar `docker compose logs connector` |
| ❌ Topics no persisten | Volúmenes deben estar configurados |
| ❌ Zookeeper offline | Reiniciar: `docker compose restart` |
| ❌ Kafka UI no accesible | Revisar puertos en `docker-compose.yml` |

---

## 📚 Recursos

- [Apache Kafka](https://kafka.apache.org/) - Documentación oficial
- [Debezium](https://debezium.io/) - CDC platform
- [KRaft Mode](https://kafka.apache.org/documentation/#kraft) - Modo sin Zookeeper

---

<div align="center">

**Elige tu arquitectura y comienza a hacer streaming →**

[📖 KRaft Stack](./kafka-kraft/README.md) | [📖 Zookeeper Stack](./kafka-zookeeper/README.md)

[⬆ Volver arriba](#-kafka-stack) • [← Volver al proyecto principal](../README.md)

</div>


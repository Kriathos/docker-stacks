# Kafka Docker Stacks

Este directorio contiene dos topologías Kafka pensadas para experimentar con mensajería, CDC y arquitecturas legacy vs modernas.

## Qué incluye

- `kafka-kraft/`: Kafka KRaft con 3 brokers, Debezium Kafka Connect y Kafka UI.
- `kafka-zookeeper/`: Apache Kafka tradicional con Zookeeper, Debezium Kafka Connect y Kafka UI.
- `consumidor-kraft.py` y `consumidor-zookeeper.py` en cada subcarpeta para consumo directo.
- `consumer.py` como ejemplo genérico de consumidor Kafka.
- `config.md` con detalles de configuración.

## Arquitectura de Kafka

```mermaid
flowchart LR
  subgraph KRaft[Kafka KRaft stack]
    pg1[PostgreSQL: demo]
    connect1[Debezium Kafka Connect]
    kafka1[Kafka Broker 1]
    kafka2[Kafka Broker 2]
    kafka3[Kafka Broker 3]
    ui1[Kafka UI]
  end
  subgraph Zookeeper[Kafka Zookeeper stack]
    pg2[PostgreSQL: demo]
    zoo[Zookeeper]
    kafkaZ[Kafka Broker]
    connect2[Debezium Kafka Connect]
    ui2[Kafka UI]
  end
  pg1 --> connect1
  connect1 --> kafka1
  connect1 --> kafka2
  connect1 --> kafka3
  kafka1 --> ui1
  kafka2 --> ui1
  kafka3 --> ui1
  pg2 --> connect2
  connect2 --> kafkaZ
  kafkaZ --> ui2
  zoo --> kafkaZ
  consumer[Python Consumer scripts] --> kafka1
  consumer --> kafkaZ
```

## Avance rápido

1. Crea la red Docker global si aún no existe:

```powershell
docker network create mynet --driver bridge
```

2. Inicia el stack de tu preferencia:

```powershell
cd .\kafka\kafka-kraft
docker compose up -d
```

o

```powershell
cd .\kafka\kafka-zookeeper
docker compose up -d
```

3. Revisa el estado de los contenedores:

```powershell
docker compose ps
```

4. Usa el consumidor apropiado según el stack:

- `kafka/kafka-kraft/consumidor-kraft.py`
- `kafka/kafka-zookeeper/consumidor-zookeeper.py`

## Comparativa KRaft vs Zookeeper

| Característica | KRaft | Zookeeper |
|---|---|---|
| Coordinador | Integrado en Kafka | Zookeeper externo |
| Complejidad | Menor | Mayor |
| Recomendado para | Nuevos laboratorios | Validación legacy |
| Brokers | 3 | 1 |
| Gestión de metadatos | Interna | Distribuida |

## Acceso de puertos

### Kafka KRaft

- Broker 1: `localhost:51437`
- Broker 2: `localhost:51438`
- Broker 3: `localhost:51439`
- PostgreSQL: `localhost:51440`

### Kafka Zookeeper

- Broker Kafka: `localhost:51435`
- PostgreSQL: `localhost:51436`

## Credenciales y configuración

- Consulta `..\credenciales.md` para ver todas las credenciales usadas en los `docker-compose.yml` del repositorio.
- Usa `kafka/config.md` para detalles de redes y parámetros adicionales.

## Recomendaciones

- Usa `kafka-kraft` para familiarizarte con Kafka moderno sin Zookeeper.
- Usa `kafka-zookeeper` para probar compatibilidad con arquitecturas clásicas.
- Si accedes desde el host, habilita los puertos de Kafka UI y Kafka Connect en el `docker-compose.yml` o usa el proxy `web`.

## Documentación adicional

- `kafka/kafka-kraft/README.md`
- `kafka/kafka-zookeeper/README.md`
- `kafka/config.md`


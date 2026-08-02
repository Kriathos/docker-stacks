# Configuración del stack Kafka Zookeeper

## Red

Este stack usa la red Docker externa `mynet` para comunicarse con otros servicios y con el proxy Nginx.

```powershell
docker network create mynet --driver bridge
```

## Servicios

- `zookeeper`: coordinación del cluster
- `kafka`: broker Kafka tradicional
- `kafka-connect`: Debezium Connect
- `kafka-ui`: interfaz de monitoreo
- `postgres`: fuente de datos para CDC

## Puertos y conexión

- Kafka: `localhost:51435`
- PostgreSQL: `localhost:51436`

Los puertos internos de Kafka UI y Kafka Connect están comentados. Para acceso directo, habilita los puertos en `docker-compose.yml`.

## Zookeeper y Kafka

- `KAFKA_ZOOKEEPER_CONNECT`: `zookeeper:2181`
- `KAFKA_ADVERTISED_LISTENERS`: `PLAINTEXT://kafka:9092`
- `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`: `1`

## Kafka Connect

- `BOOTSTRAP_SERVERS`: `kafka:29092`
- `GROUP_ID`: `1`
- `CONFIG_STORAGE_TOPIC`: `debezium-configs`
- `OFFSET_STORAGE_TOPIC`: `debezium-offsets`
- `STATUS_STORAGE_TOPIC`: `debezium-status`

## PostgreSQL

- Base de datos: `demo`
- Usuario: `postgres`
- Contraseña: `postgres`

Consulta `..\credenciales.md` para las credenciales centralizadas.

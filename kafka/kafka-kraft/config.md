# Configuración del stack Kafka KRaft

## Red

Este stack utiliza la red Docker externa `mynet` para permitir comunicación con otros servicios y con el proxy Nginx.

```powershell
docker network create mynet --driver bridge
```

## Servicios y volúmenes

- `kafka1`, `kafka2`, `kafka3`: volúmenes persistentes de datos en `/var/lib/kafka/data`
- `postgres`: volumen de datos en `/var/lib/postgresql/data`

## Kafka KRaft

- `KAFKA_PROCESS_ROLES`: broker,controller
- `KAFKA_NODE_ID`: 1, 2 o 3 según el broker
- `KAFKA_CONTROLLER_QUORUM_VOTERS`: 1@kafka1:9093,2@kafka2:9093,3@kafka3:9093

## Kafka Connect

- Usa `debezium/connect:2.5`
- Configuración interna de `BOOTSTRAP_SERVERS` apunta al clúster KRaft
- Los puertos `8083` están comentados en el compose; usa el proxy `web` o habilítalos directamente si lo deseas.

## PostgreSQL

- Base de datos: `demo`
- Usuario: `postgres`
- Contraseña: `postgres`

Para credenciales consolidadas, consulta `..\credenciales.md`.

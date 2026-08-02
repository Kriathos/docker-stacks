# Configuración del stack Kafka

Este archivo documenta los ajustes y diferencias entre los dos despliegues Kafka disponibles.

## Estructura

El stack Kafka contiene dos configuraciones principales:

- `kafka-kraft/docker-compose.yml`: clúster Kafka en modo KRaft con 3 brokers
- `kafka-zookeeper/docker-compose.yml`: despliegue Kafka tradicional con Zookeeper

## Redes

Ambas configuraciones usan estas redes:

- `kafka-net`: red interna de Kafka
- `mynet`: red externa compartida con otros stacks

```powershell
docker network create mynet --driver bridge
```

## KRaft

- Brokers: `kafka1`, `kafka2`, `kafka3`
- Puertos host: `51437`, `51438`, `51439`
- UI: `kafka-ui-kraft` (puerto interno `8080`, actualmente comentado)
- Kafka Connect: `kafka-connect-kraft` (puerto interno `8083`, actualmente comentado)
- PostgreSQL de Debezium: `postgres_kraft` en `51440`

### Nota

El proxy Nginx del stack `web` es necesario para acceder a `kafka-ui-kraft` y `kafka-connect-kraft` sin exponer puertos adicionales.

## Zookeeper

- Zookeeper: `zookeeper`
- Kafka: `kafka_zoo` en host `51435`
- UI: `kafka-ui-zoo` (puerto interno `8080`, actualmente comentado)
- Kafka Connect: `kafka-connect-zoo` (puerto interno `8083`, actualmente comentado)
- PostgreSQL de Debezium: `postgres_zoo` en `51436`

## Conexión desde host

Si deseas ejecutar `consumer.py` o conectarte desde el host, utiliza los puertos expuestos en el `docker-compose.yml`:

- KRaft broker 1: `localhost:51437`
- Zookeeper broker: `localhost:51435`

Ejemplo para `consumer.py`:

```powershell
python .\consumer.py --bootstrap-servers localhost:51437 --topic cdc.public.clientes
```

## Ajustes de puerto en `docker-compose.yml`

Las configuraciones de `kafka-ui` y `kafka-connect` tienen los puertos comentados. Si no utilizas el proxy `web`, descomenta los puertos para habilitar el acceso directo desde el host.

## Consejos

- Usa KRaft para prácticas modernas de Kafka sin Zookeeper
- Usa Zookeeper solo si necesitas estudiar el modo legacy o validar compatibilidad
- Si agregas temas o conectores, asegúrate de que todos los servicios estén en la misma red `mynet`

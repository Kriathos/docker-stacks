# Docker Stacks

Laboratorio local de microservicios para simular plataformas de datos y servicios de almacenamiento, desplegados con Docker y expuestos de forma segura.

## Lenguaje

**Grupo**:
Conjunto de microservicios relacionados por un mismo tema, como Kafka con Zookeeper, Kafka con KRaft, Databricks o Storage.
_Evitar_: Lab, tema, stack

**Stack**:
El conjunto de servicios de un grupo, declarado en un único archivo de Docker Compose.
_Evitar_: Grupo, proyecto

**Servicio**:
Un microservicio individual dentro de un stack, como `kafka1`, `sqlserver` o `minio`.
_Evitar_: Contenedor, container

**Topic**:
Canal de mensajes de Kafka. Este término se reserva exclusivamente para Kafka y no se usa para agrupar microservicios.
_Evitar_: Tema, grupo

**Metastore**:
Servicio que guarda los metadatos de las tablas: nombre, columnas y ruta donde están los datos. En el laboratorio es Hive Metastore, con Postgres como base.
_Evitar_: Catálogo, base de datos

**Datalab**:
Red externa de Docker compartida por los grupos. Conecta los servicios que Caddy debe alcanzar o que necesitan hablar entre grupos.
_Evitar_: Red compartida, mynet

**Puerto reservado**:
80, 443 y 51430 a 51440. El router los reenvía a la PC, y solo se publican los TCP que los usan.
_Evitar_: Puerto libre

**Puerto publicado**:
Puerto del host que un servicio expone con `ports:`. Los reservados solo los usan los TCP del router; los nuevos empiezan en 51500.
_Evitar_: Puerto abierto, puerto expuesto

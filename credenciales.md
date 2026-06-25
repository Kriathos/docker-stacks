# Credenciales del proyecto

Este archivo centraliza todas las credenciales y secretos que están definidos en los `docker-compose.yml` del repositorio.
No se deben replicar estas credenciales en los README de cada stack.

## Databricks (`databricks/docker-compose.yml`)

- PostgreSQL Airflow
  - Usuario: `airflow`
  - Contraseña: `Generar en docker-compose.yml`
  - Base de datos: `airflow`
- Jupyter Lab
  - Token de acceso: `Generar en docker-compose.yml`
- HashiCorp Vault
  - Token raíz de desarrollo: `Generar en docker-compose.yml`
- Airflow
  - Clave Fernet: `Se debe generar con Python`
  - python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

## Kafka (`kafka/kafka-kraft/docker-compose.yml` y `kafka/kafka-zookeeper/docker-compose.yml`)

- PostgreSQL CDC
  - Usuario: `postgres`
  - Contraseña: `Generar en docker-compose.yml`
  - Base de datos: `demo`

## Storage (`storage/docker-compose.yml`)

- SQL Server
  - Usuario: `sa`
  - Contraseña: `Generar en docker-compose.yml`
- IBM DB2
  - Usuario: `db2inst1`
  - Contraseña: `Generar en docker-compose.yml`
  - Base de datos: `SAMPLE`
- MinIO
  - Usuario root: `admin`
  - Contraseña root: `Generar en docker-compose.yml`

## Servicios sin credenciales explícitas en docker-compose

- `web/docker-compose.yml` no define usuarios ni contraseñas.
- `storage/sftpgo` usa SQLite interno y no agrega credenciales en el `docker-compose.yml`.

## Recomendaciones

- Mantén este archivo como la única fuente de credenciales para el repositorio.
- Cambia las contraseñas antes de usar el laboratorio fuera de un entorno controlado.
- Si agregas un nuevo stack, añade las credenciales aquí y actualiza el compose correspondiente.
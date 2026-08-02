# 🔧 Guía Completa de Troubleshooting

Soluciones detalladas para problemas comunes en el laboratorio.

---

## 📋 Tabla de Contenidos

1. [Instalación y Setup](#instalación-y-setup)
2. [Docker y Networking](#docker-y-networking)
3. [Storage Stack](#storage-stack)
4. [Kafka Stack](#kafka-stack)
5. [Databricks Stack](#databricks-stack)
6. [Integración Entre Stacks](#integración-entre-stacks)
7. [Performance](#performance)
8. [Datos y Persistencia](#datos-y-persistencia)

---

## 🚀 Instalación y Setup

### Problema: "Docker command not found"

**Síntomas:**
```
'docker' is not recognized as an internal or external command
```

**Causas comunes:**
- Docker Desktop no instalado
- PowerShell no está reiniciado después de instalar
- Ruta de Docker no en PATH

**Soluciones:**
```powershell
# 1. Verificar instalación
Get-Command docker

# 2. Reiniciar PowerShell
# Cierra y reabre PowerShell

# 3. Instalar Docker Desktop
# https://www.docker.com/products/docker-desktop

# 4. Agregar al PATH manualmente
$env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"

# 5. Verificar instalación
docker --version
```

---

### Problema: "WSL2 not found / not enabled"

**Síntomas:**
```
Error during connect: This error may indicate that the docker daemon is not running
WSL 2 installation is incomplete
```

**Soluciones:**
```powershell
# 1. Verificar WSL2 status
wsl -l -v

# 2. Si no aparece, habilitar WSL2
wsl --set-default-version 2

# 3. Verificar que WSL2 está instalado
wsl --install -d Ubuntu

# 4. En Docker Desktop:
# Settings → Resources → WSL Integration → Habilitar

# 5. Reiniciar Docker Desktop
```

---

### Problema: "Not enough disk space"

**Síntomas:**
```
docker: Error response from daemon: no space left on device
```

**Soluciones:**
```powershell
# 1. Ver uso de disco
docker system df

# 2. Limpiar imágenes no usadas
docker image prune -a

# 3. Limpiar volúmenes no usados
docker volume prune

# 4. Limpiar contenedores detenidos
docker container prune

# 5. Limpieza completa (⚠️ destructivo)
docker system prune -a --volumes

# 6. Liberar espacio en host
# Eliminar archivos temporales, logs, etc.

# 7. Aumentar disco asignado a Docker
# Docker Desktop → Settings → Resources → Disk image size
```

---

### Problema: "Out of memory"

**Síntomas:**
```
137 exit code
OOMKilled
Container exits unexpectedly
```

**Soluciones:**
```powershell
# 1. Ver memoria usada
docker stats

# 2. Limitar memoria por contenedor
# En docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G

# 3. Aumentar RAM en Docker Desktop
# Settings → Resources → Memory: 8-16GB

# 4. Detener servicios innecesarios
docker-compose down

# 5. Reiniciar Docker
# Cierra Docker Desktop y reabre
```

---

### Problema: "Port already in use"

**Síntomas:**
```
Address already in use
bind: address already in use
Error: listen EADDRINUSE: address already in use :::8080
```

**Soluciones:**
```powershell
# 1. Encontrar qué está usando el puerto
netstat -ano | findstr ":8080"

# 2. Ver proceso asociado
Get-Process -Id <PID>

# 3. Matar proceso
Stop-Process -Id <PID> -Force

# 4. O cambiar puerto en docker-compose.yml
ports:
  - "8081:8080"  # Cambiar de 8080 a 8081

# 5. O cambiar en aplicación si es posible
```

---

## 🌐 Docker y Networking

### Problema: "Containers cannot communicate"

**Síntomas:**
```
Connection refused
Cannot reach [servicio]
ping [servicio]: name or service not known
```

**Soluciones:**
```powershell
# 1. Verificar que red existe
docker network ls | findstr mynet

# 2. Si no existe, crear
docker network create mynet

# 3. Verificar que contenedores están en mynet
docker network inspect mynet | Select-String "Containers" -A 50

# 4. Si contenedor no está, agregar:
docker network connect mynet <container>

# 5. Test de conectividad
docker run --rm --network mynet alpine \
  sh -c "ping -c 1 sqlserver && echo OK"

# 6. Verificar DNS interno
docker run --rm --network mynet alpine nslookup kafka1

# 7. Ver logs de servicio
docker-compose logs <servicio>
```

---

### Problema: "Network is external and host unreachable"

**Síntomas:**
```
error: network mynet is external and host unreachable
Cannot start container: network not found
```

**Soluciones:**
```powershell
# 1. Crear la red si no existe
docker network create mynet --driver bridge

# 2. Verificar que fue creada
docker network ls | findstr mynet

# 3. Reiniciar Docker si aún así falla
# Cierra y reabre Docker Desktop

# 4. Crear red con opciones específicas
docker network create mynet \
  --driver bridge \
  --subnet 172.18.0.0/16 \
  --gateway 172.18.0.1

# 5. Si todo falla, eliminar y recrear
docker network rm mynet
docker network create mynet
```

---

### Problema: "DNS resolution failing"

**Síntomas:**
```
Cannot resolve minio.local
nslookup minio.local: Non-existent domain
```

**Soluciones:**
```powershell
# 1. Verificar archivo hosts (Windows)
Get-Content "C:\Windows\System32\drivers\etc\hosts" | findstr "minio"

# 2. Agregegar manualmente si falta
notepad C:\Windows\System32\drivers\etc\hosts
# Agregar: 127.0.0.1 minio.local

# 3. Limpiar DNS cache
ipconfig /flushdns

# 4. Reiniciar PowerShell

# 5. Test
nslookup minio.local

# 6. Si aún falla, usar IP directamente
curl http://127.0.0.1:9001
```

---

## 💾 Storage Stack

### Problema: "SQL Server fails to start"

**Síntomas:**
```
SQL Server 2022 setup failed
Container exits with error
```

**Soluciones:**
```powershell
# 1. Ver logs
docker-compose -f docker-compose-storage.yml logs sqlserver

# 2. Verificar RAM disponible (mínimo 2GB)
docker stats

# 3. Esperar más tiempo (primer inicio tarda ~30 seg)
Start-Sleep -Seconds 60

# 4. Verificar contraseña en docker-compose.yml
# SA_PASSWORD debe tener:
# - 8+ caracteres
# - Mayúsculas, minúsculas, números, símbolos

# 5. Reintentar
docker-compose -f docker-compose-storage.yml restart sqlserver

# 6. Si persiste, limpiar y reiniciar
docker-compose -f docker-compose-storage.yml down -v
docker-compose -f docker-compose-storage.yml up -d
```

---

### Problema: "Cannot connect to SQL Server"

**Síntomas:**
```
Login failed for user 'sa'
Connection timeout
Named pipe provider error 40
```

**Soluciones:**
```powershell
# 1. Verificar que está corriendo
docker-compose -f docker-compose-storage.yml ps | findstr sqlserver

# 2. Esperar inicialización completa
# Ver logs hasta "SQL Server is now ready..."
docker-compose -f docker-compose-storage.yml logs sqlserver

# 3. Verificar contraseña correcta
# docker-compose-storage.yml → SA_PASSWORD

# 4. Intentar conexión
docker-compose -f docker-compose-storage.yml exec sqlserver \
  sqlcmd -S localhost -U sa -P "contraseña"

# 5. Verificar puerto
netstat -an | findstr ":1433"

# 6. Reintentar después de esperar
Start-Sleep -Seconds 30
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa
```

---

### Problema: "MinIO permission denied"

**Síntomas:**
```
MinIO: permission denied
Cannot write to volume
```

**Soluciones:**
```powershell
# 1. Verificar que carpeta existe
Test-Path "F:\minio-data"

# 2. Crear si no existe
New-Item -Path "F:\minio-data" -ItemType Directory -Force

# 3. Verificar permisos
# Click derecho en F:\minio-data → Properties → Security

# 4. Si tienes permisos pero falla, usar volumen nombrado
# En docker-compose-storage.yml:
volumes:
  minio_data:

services:
  minio:
    volumes:
      - minio_data:/data

# 5. Recrear
docker-compose -f docker-compose-storage.yml down -v
docker-compose -f docker-compose-storage.yml up -d
```

---

### Problema: "SFTPGo port 2022 in use"

**Síntomas:**
```
Error starting SFTPGo
Port 2022 already in use
```

**Soluciones:**
```powershell
# 1. Ver qué está usando 2022
netstat -ano | findstr ":2022"

# 2. Matar proceso
Stop-Process -Id <PID> -Force

# 3. O cambiar puerto en docker-compose-storage.yml
services:
  sftpgo:
    ports:
      - "2023:2022"

# 4. Actualizar cliente SFTP
sftp -P 2023 user@localhost
```

---

## 📨 Kafka Stack

### Problema: "Kafka brokers not initializing (KRaft)"

**Síntomas:**
```
Brokers stuck in STARTING
Cannot reach bootstrap server
```

**Causas comunes:**
- Primera inicialización toma mucho tiempo
- Quórum no establecido
- Problemas de red

**Soluciones:**
```powershell
cd .\kafka-kraft

# 1. Ver logs de todos los brokers
docker-compose logs

# 2. Esperar más tiempo (60-120 seg)
Start-Sleep -Seconds 120

# 3. Verificar estado
docker-compose exec kafka1 kafka-metadata.sh \
  --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log \
  --print

# 4. Revisar logs específicos
docker-compose logs kafka1 | Select-String "RUNNING"

# 5. Si quórum falla, reiniciar todo
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 120

# 6. Verificar configuración KAFKA_CONTROLLER_QUORUM_VOTERS
cat docker-compose.yml | Select-String "CONTROLLER_QUORUM"
```

---

### Problema: "Zookeeper ensemble not forming"

**Síntomas:**
```
Zookeeper failed to start
Cannot form quorum
Only 1-2 ZK nodes active
```

**Soluciones:**
```powershell
cd .\kafka-zookeeper

# 1. Verificar que los 3 ZK nodes están corriendo
docker-compose ps | findstr zookeeper

# 2. Ver logs de ZK
docker-compose logs zookeeper1

# 3. Esperar más tiempo (hasta 2 minutos)
Start-Sleep -Seconds 120

# 4. Verificar cada ZK node tiene ID único
cat docker-compose.yml | Select-String "ZOO_MY_ID"
# Esperado: 1, 2, 3 (diferentes)

# 5. Verificar conectividad entre ZK nodes
docker-compose exec zookeeper1 nc -zv zookeeper2 2888
docker-compose exec zookeeper1 nc -zv zookeeper3 2888

# 6. Si falla, reconstruir
docker-compose down -v
docker-compose up -d
Start-Sleep -Seconds 120
```

---

### Problema: "Cannot create Kafka topic"

**Síntomas:**
```
Error while executing topic command
Topic not created
Broker not available
```

**Soluciones:**
```powershell
# 1. Verificar que brokers están corriendo
docker-compose ps | findstr kafka

# 2. Esperar a que se estabilicen (después de docker-compose up -d)
Start-Sleep -Seconds 60

# 3. Listar brokers
docker-compose exec kafka1 kafka-broker-api-versions.sh \
  --bootstrap-server kafka1:9092

# 4. Crear topic con más verbose
docker-compose exec kafka1 kafka-topics.sh \
  --create \
  --topic test \
  --bootstrap-server kafka1:9092 \
  --partitions 3 \
  --replication-factor 3 \
  --verbose

# 5. Si dice "broker not available", esperar más
# Los brokers tardan en registrarse en Zookeeper

# 6. Ver logs del broker
docker-compose logs kafka1 | Select-String "registered"
```

---

### Problema: "Debezium connector fails"

**Síntomas:**
```
Connector in FAILED state
Cannot connect to PostgreSQL
Connector keeps crashing
```

**Soluciones:**
```powershell
# 1. Ver status del connector
curl http://localhost:8083/connectors/postgres-connector/status

# 2. Ver logs de Debezium
docker-compose logs debezium-connect

# 3. Verificar que PostgreSQL está corriendo
docker-compose exec postgres-cdc psql -U postgres -d demo -c "\du"

# 4. Crear publicación en PostgreSQL
docker-compose exec postgres-cdc psql -U postgres -d demo
# Dentro de psql:
CREATE PUBLICATION dbz_publication FOR ALL TABLES;
\dP
\q

# 5. Eliminar y recrear connector
curl -X DELETE http://localhost:8083/connectors/postgres-connector

# 6. Registrar de nuevo
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{...connector config...}'

# 7. Ver nuevamente
curl http://localhost:8083/connectors/postgres-connector/status
```

---

## 🔬 Databricks Stack

### Problema: "Airflow fails to start"

**Síntomas:**
```
Airflow container exits
Cannot initialize database
```

**Causas comunes:**
- Fernet Key no generada
- PostgreSQL no disponible
- Permisos incorrectos

**Soluciones:**
```powershell
cd .\databricks

# 1. Verificar Fernet Key en docker-compose.yml
cat docker-compose.yml | Select-String "FERNET_KEY"

# 2. Si no está o está como "Generar", generar uno nuevo
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3. Actualizar docker-compose.yml con la clave

# 4. Eliminar y recrear
docker-compose down -v
docker-compose up -d

# 5. Esperar (primer init tarda ~30 seg)
Start-Sleep -Seconds 60

# 6. Ver logs
docker-compose logs airflow-webserver

# 7. Buscar errores
docker-compose logs airflow-webserver | Select-String "ERROR"
```

---

### Problema: "Jupyter token invalid"

**Síntomas:**
```
Token not working
Cannot login to Jupyter
```

**Soluciones:**
```powershell
cd .\databricks

# 1. Obtener token actual
docker-compose logs jupyter | Select-String "token=" | Select-Object -Last 1

# 2. Copiar URL completa del token

# 3. Si no funciona, reiniciar
docker-compose restart jupyter

# 4. Esperar reinicio
Start-Sleep -Seconds 10

# 5. Obtener token nuevo
docker-compose logs jupyter | Select-String "token="

# 6. Usar nueva URL
```

---

### Problema: "PostgreSQL connection refused"

**Síntomas:**
```
Cannot connect to database
Airflow metadata database error
Connection refused
```

**Soluciones:**
```powershell
cd .\databricks

# 1. Verificar que está corriendo
docker-compose ps | findstr postgres

# 2. Esperar inicialización (primeros 15 segundos)
Start-Sleep -Seconds 20

# 3. Conectar manualmente
docker-compose exec postgres psql -U airflow -d airflow

# 4. Si falla, ver logs
docker-compose logs postgres

# 5. Reiniciar
docker-compose restart postgres
Start-Sleep -Seconds 20

# 6. Reiniciar Airflow
docker-compose restart airflow-webserver
```

---

### Problema: "Spark job fails - host unreachable"

**Síntomas:**
```
Spark worker cannot reach master
Connection to spark://spark-master failed
```

**Soluciones:**
```powershell
cd .\databricks

# 1. Verificar que Spark Master está corriendo
docker-compose ps | findstr spark

# 2. Verificar conectividad
docker-compose exec spark-master spark-shell --version

# 3. Verificar que Worker puede alcanzar Master
docker-compose exec spark-worker spark-shell --version

# 4. Revisar logs del Worker
docker-compose logs spark-worker | Select-String "ERROR"

# 5. Verificar configuración de red
docker-compose exec spark-worker ping spark-master

# 6. Reconstruir si falla
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 30
```

---

## 🔗 Integración Entre Stacks

### Problema: "Spark cannot connect to SQL Server"

**Síntomas:**
```
JDBC connection timeout
Cannot connect to host sqlserver
```

**Soluciones:**
```powershell
# 1. Verificar que SQL Server está en mynet
docker network inspect mynet | Select-String "sqlserver"

# 2. Test de conectividad desde Spark
docker-compose -f databricks/docker-compose.yml exec spark-master \
  bash -c "echo quit | telnet sqlserver 1433"

# 3. Verificar credenciales en código Spark
# URL: jdbc:sqlserver://sqlserver:1433
# Usuario: sa
# Contraseña: (la del docker-compose-storage.yml)

# 4. Verificar que SQL Server está corriendo
docker-compose -f storage/docker-compose-storage.yml ps

# 5. Crear base de datos de prueba en SQL Server
docker-compose -f storage/docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa
# CREATE DATABASE TestDB; GO EXIT

# 6. Reintentar desde Jupyter
# Usar credenciales correctas y URL correcta
```

---

### Problema: "Spark cannot reach MinIO"

**Síntomas:**
```
S3A connection error
Cannot access s3a://bucket
```

**Soluciones:**
```powershell
# 1. Verificar que MinIO está en mynet
docker network inspect mynet | Select-String "minio"

# 2. Test de conectividad
docker-compose -f databricks/docker-compose.yml exec spark-master \
  curl http://minio:9000

# 3. Configurar Spark correctamente
spark.conf.set("fs.s3a.endpoint", "http://minio:9000")
spark.conf.set("fs.s3a.access.key", "admin")
spark.conf.set("fs.s3a.secret.key", "minioadmin")

# 4. Crear bucket en MinIO primero
# URL: http://minio.local:9001

# 5. Reintentar
# df.write.parquet("s3a://bucket/path")
```

---

### Problema: "Kafka topics no se ven desde Spark"

**Síntomas:**
```
Topic not found
Cannot subscribe to topic
Broker unreachable
```

**Soluciones:**
```powershell
# 1. Verificar que Kafka está en mynet
docker network inspect mynet | Select-String "kafka"

# 2. Listar topics desde Kafka
docker-compose -f kafka-kraft/docker-compose.yml exec kafka1 \
  kafka-topics.sh --list --bootstrap-server kafka1:9092

# 3. Crear topic si no existe
docker-compose -f kafka-kraft/docker-compose.yml exec kafka1 \
  kafka-topics.sh --create --topic test-topic \
  --bootstrap-server kafka1:9092 --partitions 3 --replication-factor 3

# 4. En Spark, usar bootstrap.servers correcto
df = spark.readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "kafka1:9092") \
  .option("subscribe", "test-topic") \
  .load()

# 5. Producir datos para probar
docker-compose -f kafka-kraft/docker-compose.yml exec kafka1 \
  kafka-console-producer.sh --broker-list kafka1:9092 \
  --topic test-topic
```

---

## ⚡ Performance

### Problema: "Stack runs slowly"

**Síntomas:**
```
Queries lentas
Procesamiento tardío
Respuestas lentas de servicios
```

**Soluciones:**
```powershell
# 1. Ver uso de recursos
docker stats

# 2. Identificar contenedor que consume mucho
docker stats --no-stream | sort -k 4 -rn

# 3. Aumentar límites
# En docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '4'

# 4. Aumentar RAM en Docker Desktop
# Docker Desktop → Settings → Resources

# 5. Verificar disco lleno
docker system df

# 6. Limpiar si es necesario
docker system prune -a

# 7. Revisar si hay queries N+1 o ineficientes
```

---

### Problema: "Database queries very slow"

**Síntomas:**
```
Queries tardan mucho
Timeout en operaciones
CPU alto en SQL Server
```

**Soluciones:**
```powershell
# 1. Crear índices en SQL Server
docker-compose -f storage/docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa
# CREATE INDEX idx_name ON table(column);
# GO

# 2. Analyizar query performance
# SET STATISTICS IO ON; (en sqlcmd)

# 3. Ver bloqueos
# sp_who2 (en sqlcmd)

# 4. Aumentar RAM asignada a SQL Server
# En docker-compose-storage.yml:
environment:
  MSSQL_MEMORY_LIMIT_MB: 2048

# 5. Reiniciar SQL Server
docker-compose -f docker-compose-storage.yml restart sqlserver
```

---

## 📦 Datos y Persistencia

### Problema: "Datos perdidos después de reiniciar"

**Síntomas:**
```
Container reinicia y no hay datos
Volumen vacío
```

**Causas comunes:**
- Usar docker-compose down -v (elimina volúmenes)
- Volumen no configurado correctamente
- Bind mount no mapeado

**Soluciones:**
```powershell
# 1. Verificar volúmenes
docker volume ls | findstr <stack>

# 2. Ver volumen en docker-compose.yml
cat docker-compose.yml | Select-String "volumes:"

# 3. Si usa bind mount, verificar ruta existe
Test-Path "F:\minio-data"

# 4. Si usa volumen nombrado, verificar existe
docker volume inspect <volume_name>

# 5. Nunca usar docker-compose down -v en producción
# Usar solo: docker-compose down

# 6. Para backup
docker run --rm -v <volume>:/data -v $(pwd):/backup \
  alpine tar czf /backup/backup.tar.gz /data

# 7. Para restore
docker run --rm -v <volume>:/data -v $(pwd):/backup \
  alpine tar xzf /backup/backup.tar.gz -C /
```

---

### Problema: "Volumen dañado o corrupto"

**Síntomas:**
```
Docker error: volume is corrupted
Cannot mount volume
Permission denied on volume
```

**Soluciones:**
```powershell
# 1. Detener contenedores
docker-compose down

# 2. Inspeccionar volumen
docker volume inspect <volume_name>

# 3. Limpiar volumen dañado
docker volume rm <volume_name>

# 4. Recrear volumen
docker-compose up -d

# 5. Si persiste, limpiar sistema completo
docker system prune -a --volumes

# ⚠️ ADVERTENCIA: Esto elimina TODOS los datos
```

---

## 📞 Soporte Adicional

### Comandos de Debug Útiles

```powershell
# Ver todos los contenedores
docker ps -a

# Ver logs de todos
docker-compose logs

# Ver eventos en tiempo real
docker events

# Inspeccionar contenedor
docker inspect <container_id>

# Acceder a shell del contenedor
docker-compose exec <servicio> bash
docker-compose exec <servicio> sh

# Ver resources
docker stats

# Ver redes
docker network ls
docker network inspect mynet

# Ver volúmenes
docker volume ls
docker volume inspect <volume>

# Limpiar
docker system prune -a
docker image prune
docker container prune
docker volume prune
```

### Contacto y Escalación

Si un problema persiste después de intentar estas soluciones:

1. **Recolectar información:**
   ```powershell
   docker --version
   docker-compose version
   docker system df
   docker ps -a
   docker logs <container>
   ```

2. **Buscar en documentación:**
   - [README.md](./README.md)
   - [config.md](./config.md)
   - Stack-specific setup.md

3. **Revisar GitHub Issues**
   - Otros usuarios pueden haber tenido el mismo problema

4. **Crear Issue con información:**
   - Docker version
   - Comando exacto que falla
   - Logs completos
   - Pasos para reproducir

---

<div align="center">

**¿Encontraste la solución?** → Vuelve a trabajar 🚀

**¿Aún no?** → Revisa logs, reinicia, y intenta de nuevo

[📖 README](./README.md) | [🚀 SETUP](./SETUP.md) | [⚙️ CONFIG](./config.md) | [🔧 TROUBLESHOOTING](./TROUBLESHOOTING.md)

</div>

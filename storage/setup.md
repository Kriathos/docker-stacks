# 🚀 Setup Storage Stack

Guía paso a paso para iniciar el stack de almacenamiento (SQL Server, DB2, MinIO, SFTPGo, Apache).

---

## ✅ Pre-requisitos

- ✅ Docker Desktop instalado y corriendo
- ✅ Red `mynet` creada: `docker network create mynet`
- ✅ 4GB RAM mínimo (8GB recomendado)
- ✅ 30GB disco disponible
- ✅ Rutas Windows configuradas (F:/ o alternativa)

---

## 📁 Paso 1: Preparar Directorios

Los volúmenes persisten datos en Windows. Crea los directorios requeridos:

### 1.1 Crear Carpetas

```powershell
# Si usas F:/
New-Item -Path "F:\sftp" -ItemType Directory -Force
New-Item -Path "F:\sftpgo-data" -ItemType Directory -Force
New-Item -Path "F:\minio-data" -ItemType Directory -Force
New-Item -Path "F:\apache-fileserver" -ItemType Directory -Force

# Verificar
Test-Path "F:\sftp"
Test-Path "F:\sftpgo-data"
Test-Path "F:\minio-data"
Test-Path "F:\apache-fileserver"
```

### 1.2 Si Usas Rutas Diferentes

Si no tienes `F:/`, reemplaza en `docker-compose-storage.yml`:

```yaml
# Ejemplo: Usar C:/data/
volumes:
  - "C:/data/sftp:/srv/sftpgo"
  - "C:/data/sftpgo:/var/lib/sftpgo"
  - "C:/data/minio:/data"
  - "C:/data/apache:/usr/local/apache2/htdocs/"
```

---

## 🔐 Paso 2: Actualizar Credenciales

Lee [`credenciales.md`](../credenciales.md) en raíz para credenciales completas.

### 2.1 Actualizar Contraseñas (Opcional)

Edita `docker-compose-storage.yml`:

```yaml
sqlserver:
  environment:
    SA_PASSWORD: "Secure$Pass2024"  # Cambiar de "Generar"

db2:
  environment:
    DB2INST1_PASSWORD: "DB2$Pass2024"

minio:
  environment:
    MINIO_ROOT_PASSWORD: "Minio$Pass2024"
```

**Requisitos de contraseña:**
- SQL Server: 8+ caracteres, mayúsculas, minúsculas, números, símbolos
- DB2: 8+ caracteres, sin nombre de usuario
- MinIO: sin restricciones, pero 12+ caracteres recomendado

### 2.2 Generar Contraseña Segura

```powershell
$pass = -join ((65..90) + (97..122) + (48..57) + (33..47) | Get-Random -Count 16 | % {[char]$_})
Write-Host $pass
```

---

## 🚀 Paso 3: Iniciar Storage Stack

### 3.1 Iniciar Servicios

```powershell
# Navegar al directorio
cd .\storage

# Iniciar todos los servicios en background
docker-compose -f docker-compose-storage.yml up -d

# Verificar que están corriendo
docker-compose -f docker-compose-storage.yml ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE                  STATUS
xxxxx          mcr.microsoft.com/mssql/server:2022-latest   Up 10s
xxxxx          ibmcom/db2             Up 5s
xxxxx          drakkan/sftpgo:latest  Up 3s
xxxxx          minio/minio            Up 2s
xxxxx          httpd:2.4              Up 1s
```

### 3.2 Esperar a que Inicien

SQL Server y DB2 tardan más en iniciarse:

```powershell
# SQL Server: ~30 segundos
# DB2: ~60 segundos
# SFTPGo, MinIO, Apache: ~5 segundos

# Ver logs de SQL Server
docker-compose -f docker-compose-storage.yml logs -f sqlserver

# Esperar a ver: "Server is ready for client connections"
```

---

## ✅ Paso 4: Verificar Conectividad

### 4.1 Test SQL Server

```powershell
# Conectar a SQL Server
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa

# Deberías ver el prompt: "1>"

# Ejecutar query
SELECT @@VERSION
GO

# Ver resultado
# Microsoft SQL Server 2022...

# Salir
EXIT
```

### 4.2 Test DB2

```powershell
# Acceder a bash de DB2
docker-compose -f docker-compose-storage.yml exec db2 bash

# Dentro del contenedor:
su - db2inst1
# Ingresa contraseña

# Conectar a base de datos
db2 connect to SAMPLE

# Ver tablas
db2 "LIST TABLES FOR SYSTEM"

# Salir
db2 terminate
exit
exit
```

### 4.3 Test MinIO

```powershell
# Verificar conectividad a MinIO
docker-compose -f docker-compose-storage.yml exec minio mc --help

# Si ves output de ayuda, está ok
```

### 4.4 Test SFTPGo

```powershell
# Verificar puerto SFTP escucha
netstat -an | findstr "2022"
# Deberías ver: TCP 127.0.0.1:2022 LISTENING

# O con curl
curl -I http://localhost:51500
# Deberías ver: HTTP/1.1 200 OK
```

### 4.5 Test Apache

```powershell
# Verificar Apache
curl http://localhost/
# Deberías ver contenido de F:/apache-fileserver/
```

---

## 🌐 Paso 5: Acceder a Interfaces Web

Una vez verificado, accede a las UIs web:

### 5.1 MinIO Console

```
URL: http://minio.local:9001
(o http://localhost:9001 si no configuraste hosts)

Usuario: admin
Contraseña: (la que configuraste en docker-compose-storage.yml)
```

**Crear bucket:**
1. Login a MinIO Console
2. Click "Create Bucket"
3. Nombre: `my-data`
4. Click "Create"

### 5.2 SFTPGo Web UI

```
URL: http://sftp.local:51500
(o http://localhost:51500)

Crear usuario admin en primer acceso:
1. Username: admin
2. Password: (elige contraseña)
3. Click "Save"
```

**Crear usuario SFTP:**
1. Login a SFTPGo
2. Menu → Users → Add User
3. Username: testuser
4. Password: (genera contraseña)
5. Home Dir: /data/sftp/testuser
6. Save

### 5.3 Apache File Server

```
URL: http://data.local
(o http://localhost)

Agregar archivos:
1. Copia archivos a F:/apache-fileserver/
2. Accesibles automáticamente en URL
```

---

## 📊 Paso 6: Crear Datos de Prueba

### 6.1 SQL Server - Crear Base de Datos

```powershell
# Conectar
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa

# Ejecutar comandos (en el prompt de sqlcmd):
CREATE DATABASE TestDB;
GO

USE TestDB;
GO

CREATE TABLE Users (
  ID INT PRIMARY KEY IDENTITY(1,1),
  Name NVARCHAR(100),
  Email NVARCHAR(100),
  CreatedAt DATETIME DEFAULT GETDATE()
);
GO

INSERT INTO Users (Name, Email) VALUES ('Alice', 'alice@test.com');
INSERT INTO Users (Name, Email) VALUES ('Bob', 'bob@test.com');
GO

SELECT * FROM Users;
GO

EXIT
```

### 6.2 DB2 - Crear Tabla

```powershell
# Conectar a DB2
docker-compose -f docker-compose-storage.yml exec db2 bash

su - db2inst1
# Ingresa contraseña

db2 connect to SAMPLE

# Crear tabla
db2 "CREATE TABLE USERS (ID INT NOT NULL PRIMARY KEY, NAME VARCHAR(100), EMAIL VARCHAR(100))"

# Insertar datos
db2 "INSERT INTO USERS VALUES (1, 'Alice', 'alice@test.com')"
db2 "INSERT INTO USERS VALUES (2, 'Bob', 'bob@test.com')"

# Ver datos
db2 "SELECT * FROM USERS"

db2 terminate
exit
exit
```

### 6.3 MinIO - Crear Bucket y Subir Archivo

```powershell
# Desde Windows, crear un archivo de prueba
@"
This is a test file for MinIO.
Uploaded from Windows.
"@ | Out-File -Encoding UTF8 "F:\test.txt"

# Desde contenedor
docker-compose -f docker-compose-storage.yml exec minio mc alias set local http://localhost:9000 admin minioadmin

docker-compose -f docker-compose-storage.yml exec minio mc mb local/test-bucket

docker-compose -f docker-compose-storage.yml exec minio mc cp /data/test.txt local/test-bucket/
```

### 6.4 SFTPGo - Subir Archivo

```powershell
# Conectar por SFTP desde Windows
# Opción 1: Usar WinSCP (GUI)
#   - Host: localhost
#   - Puerto: 2022
#   - Usuario: testuser
#   - Contraseña: (la que creaste)

# Opción 2: Usar OpenSSH (CLI)
# (Requiere OpenSSH instalado en Windows)
sftp -P 2022 testuser@localhost
# Cuando pida contraseña, ingresa

# Dentro de SFTP:
put C:\archivo.txt
quit
```

---

## 🔗 Paso 7: Integración con Otros Stacks

### 7.1 Acceso desde Databricks (Spark)

```python
# En Jupyter Notebook (Databricks stack)

# Leer desde SQL Server
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ReadSQL").getOrCreate()

df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:sqlserver://sqlserver:1433") \
    .option("dbtable", "[TestDB].[dbo].[Users]") \
    .option("user", "sa") \
    .option("password", "tu-contraseña") \
    .load()

df.show()
```

### 7.2 Acceso desde Kafka (CDC)

Ver [`credenciales.md`](../credenciales.md) sección Kafka para configurar Debezium CDC hacia SQL Server.

---

## 🛑 Paso 8: Detener Stack

### 8.1 Detener Servicios

```powershell
# Detener pero mantener datos
docker-compose -f docker-compose-storage.yml down

# Verificar que se detuvieron
docker ps | findstr storage
# No debe haber resultados
```

### 8.2 Limpiar Volúmenes (⚠️ Borra datos)

```powershell
# ⚠️ ADVERTENCIA: Esto elimina TODOS los datos

# Opción 1: Eliminar volúmenes nombrados
docker-compose -f docker-compose-storage.yml down -v

# Opción 2: Limpiar directorios Windows (si usas bind mounts)
Remove-Item "F:\sftp\*" -Recurse -Force
Remove-Item "F:\sftpgo-data\*" -Recurse -Force
Remove-Item "F:\minio-data\*" -Recurse -Force
Remove-Item "F:\apache-fileserver\*" -Recurse -Force
```

---

## 🆘 Troubleshooting

### Problema: "SQL Server failed to initialize"

**Síntoma:** Container de SQL Server se detiene con error

**Soluciones:**
1. Aumentar RAM de Docker Desktop a 4GB+
2. Esperar más tiempo (puede tomar 60 segundos)
3. Ver logs: `docker-compose logs sqlserver`
4. Reintentar: `docker-compose down && docker-compose up -d`

### Problema: "DB2 license not accepted"

**Síntoma:** Container DB2 no inicia

**Solución:**
Verificar que `LICENSE: "accept"` está en docker-compose-storage.yml

### Problema: "MinIO volume permission denied"

**Síntoma:** MinIO no puede escribir datos

**Solución:**
1. Verificar que la carpeta existe: `Test-Path F:\minio-data`
2. Verificar permisos: Click derecho → Properties → Security
3. Alternativa: Usar volumen nombrado en lugar de bind mount

### Problema: "SFTPGo port 2022 already in use"

**Síntoma:** Error "Address already in use"

**Soluciones:**
1. Cambiar puerto en docker-compose-storage.yml:
   ```yaml
   ports:
     - "2023:2022"  # Usar 2023 en lugar de 2022
   ```

2. O encontrar qué está usando el puerto:
   ```powershell
   netstat -ano | findstr ":2022"
   taskkill /PID <PID> /F
   ```

### Problema: "Apache forbidden (403)"

**Síntoma:** Error 403 en http://localhost/

**Soluciones:**
1. Verificar que existe `F:\apache-fileserver`
2. Agregar un archivo de prueba
3. Verificar permisos del directorio
4. Ver logs: `docker-compose logs file-server`

---

## ✅ Checklist de Verificación

Una vez completado el setup:

- [ ] Todos los contenedores están corriendo (`docker ps`)
- [ ] SQL Server responde a queries
- [ ] DB2 conecta y lista tablas
- [ ] MinIO Console accesible en :9001
- [ ] SFTPGo Web UI accesible en :51500
- [ ] Apache File Server responde en puerto 80
- [ ] Datos de prueba creados en SQL Server
- [ ] Datos de prueba creados en MinIO
- [ ] Spark puede conectar a SQL Server (desde Databricks)
- [ ] Debezium puede conectar a PostgreSQL (desde Kafka)

---

## 📚 Siguientes Pasos

1. **Integrar con Databricks Stack**
   - Leer datos de SQL Server con Spark
   - Escribir resultados a MinIO

2. **Integrar con Kafka Stack**
   - Configurar CDC desde PostgreSQL
   - Replicar cambios a SQL Server

3. **Automatizar con Airflow**
   - Crear DAGs que orquesten ETL
   - Schedule jobs automáticos

4. **Monitoreo**
   - Revisar logs regularmente
   - Monitorear uso de disco
   - Revisar performance de queries

---

<div align="center">

[📖 Leer README](../storage/README.md) • [⚙️ Ver config](../storage/config.md) • [🚀 Leer SETUP central](../SETUP.md)

</div>

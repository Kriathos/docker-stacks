# 🚀 Guía de Instalación y Setup

Guía paso a paso para instalar y configurar el laboratorio completo de infraestructura de datos.

**Tiempo estimado:** 30-45 minutos (primera ejecución)

---

## ✅ Pre-requisitos

### Sistema Operativo
- ✅ Windows 10/11 Pro, Enterprise o Education
- ✅ WSL2 habilitado
- ✅ Virtualización habilitada en BIOS

### Software Requerido
- ✅ Docker Desktop 4.0 o superior
- ✅ PowerShell 5.0+ o PowerShell Core 7+
- ✅ Git (opcional pero recomendado)

### Recursos Hardware Mínimo
- ✅ 8GB RAM (16GB recomendado)
- ✅ 50GB disco disponible
- ✅ Procesador con virtualización

---

## 📋 Paso 1: Verificar Instalación de Docker

### 1.1 Verificar Docker Desktop

```powershell
# Verificar versión de Docker
docker --version
# Esperado: Docker version 20.10+

# Verificar Docker Compose
docker compose version
# Esperado: Docker Compose version 2.0+

# Verificar que Docker daemon está corriendo
docker ps
# Si no hay error, Docker está funcionando
```

### 1.2 Habilitar WSL2

```powershell
# Verificar que WSL2 está habilitado
wsl -l -v
# Esperado: distribution* <version> 2

# Si es necesario, habilitar WSL2
wsl --set-default-version 2
```

### 1.3 Configurar Docker para WSL2

En Docker Desktop:
1. Settings → Resources → WSL Integration
2. ✅ Habilitar "Windows Subsystem for Linux"
3. ✅ Seleccionar distribución WSL2 (si aplica)
4. Click "Apply & Restart"

---

## 📁 Paso 2: Clonar el Repositorio

### 2.1 Opción A: Con Git (Recomendado)

```powershell
# Navegar a ubicación deseada
cd C:\Users\<tu-usuario>\

# Clonar repositorio
git clone https://github.com/tu-usuario/data-infrastructure-lab.git

# Navegar al directorio
cd data-infrastructure-lab

# Ver estructura
dir
```

### 2.2 Opción B: Descarga Manual

1. Ir a [GitHub Releases](https://github.com/tu-usuario/data-infrastructure-lab/releases)
2. Descargar `.zip` de la versión
3. Extraer en `C:\Users\<tu-usuario>\data-infrastructure-lab`
4. Abrir PowerShell en esa carpeta

### 2.3 Verificar Estructura

```powershell
# Debe existir:
Test-Path .\web
Test-Path .\storage
Test-Path .\kafka-kraft
Test-Path .\kafka-zookeeper
Test-Path .\databricks
Test-Path .\README.md
Test-Path .\config.md
Test-Path .\credenciales.md
```

---

## 🌉 Paso 3: Crear Red Docker Compartida

La red `mynet` es **obligatoria** para que los stacks se comuniquen.

### 3.1 Crear la Red

```powershell
# Crear red bridge externa
docker network create mynet --driver bridge

# Verificar creación
docker network ls | findstr mynet

# Ver detalles
docker network inspect mynet
```

### 3.2 Verificar Conectividad

```powershell
# Si la red existe, debes ver salida similar a:
# NETWORK ID     NAME      DRIVER    SCOPE
# abc123def456   mynet     bridge    local
```

---

## 🖥️ Paso 4: Configurar Archivo Hosts (Recomendado)

Los dominios locales hacen más fácil acceder a los servicios.

### 4.1 Abrir Archivo Hosts

```powershell
# Abrir como administrador (requiere permisos)
notepad C:\Windows\System32\drivers\etc\hosts
```

### 4.2 Agregar Entradas

Añade al final del archivo:

```hosts
# ===============================================
# Laboratorio de Infraestructura de Datos
# ===============================================

# Proxy Central (Caddy)
127.0.0.1 localhost
127.0.0.1 landing.local

# Storage Stack
127.0.0.1 sftp.local
127.0.0.1 minio.local
127.0.0.1 minio-api.local
127.0.0.1 data.local
127.0.0.1 spark.local

# Kafka Stack
127.0.0.1 kraft-ui.local
127.0.0.1 zoo-ui.local

# Databricks Stack
127.0.0.1 jupyter.local
127.0.0.1 mlflow.local
127.0.0.1 airflow.local
127.0.0.1 vault.local

# ===============================================
```

### 4.3 Guardar

- Ctrl+S
- Cerrar notepad
- No es necesario reiniciar

---

## 🔐 Paso 5: Revisar y Actualizar Credenciales

### 5.1 Leer Credenciales Actuales

```powershell
# Ver todas las credenciales
cat .\credenciales.md

# O abrirlo en editor
notepad .\credenciales.md
```

### 5.2 Actualizar Contraseñas (RECOMENDADO)

Para desarrollo local, está bien dejar las credenciales por defecto. Pero si planeas usar datos reales:

1. Abre `credenciales.md`
2. Busca "Generar en docker-compose.yml"
3. Reemplaza con contraseñas seguras
4. Actualiza los archivos `docker-compose-*.yml` correspondientes

**Generar contraseña segura:**
```powershell
# PowerShell
$pass = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 16 | ForEach-Object {[char]$_})
Write-Host $pass
```

---

## 🔧 Paso 6: Revisar Configuración Global

### 6.1 Leer config.md

```powershell
cat .\config.md
```

### 6.2 Verificar Rutas de Windows

Si usas rutas diferentes a `F:/`, actualiza:
- `storage/docker-compose-storage.yml` - rutas de SFTPGo, MinIO, Apache
- Cualquier volumen con rutas absolutas Windows

**Ejemplo de cambio:**
```yaml
# Antes (si no tienes F:/)
volumes:
  - "F:/sftp:/srv/sftpgo"

# Después (ejemplo con C:/)
volumes:
  - "C:/data/sftp:/srv/sftpgo"
```

---

## 🌐 Paso 7: Iniciar Proxy Caddy (Obligatorio)

El proxy Caddy es el punto de entrada central. Debe estar corriendo.

### 7.1 Iniciar Caddy

```powershell
# Navegar a web
cd .\web

# Iniciar Caddy
docker-compose -f docker-compose-caddy.yml up -d

# Verificar
docker-compose -f docker-compose-caddy.yml ps

# Esperado: caddy container con estado "Up"
```

### 7.2 Verificar

```powershell
# Test HTTP
curl http://localhost/

# Deberías ver HTML de landing page
```

### 7.3 Ver Logs (Si hay problemas)

```powershell
docker-compose -f docker-compose-caddy.yml logs caddy
```

---

## 💾 Paso 8: Iniciar Storage Stack

Stack de bases de datos y almacenamiento.

### 8.1 Preparar Directorios

```powershell
# Navegar a storage
cd ..\storage

# Crear directorios de datos (si no existen)
New-Item -Path "F:\sftp" -ItemType Directory -Force
New-Item -Path "F:\sftpgo-data" -ItemType Directory -Force
New-Item -Path "F:\minio-data" -ItemType Directory -Force
New-Item -Path "F:\apache-fileserver" -ItemType Directory -Force

# O si usas otras rutas, ajusta según config.md
```

### 8.2 Iniciar Servicios

```powershell
# Iniciar stack
docker-compose -f docker-compose-storage.yml up -d

# Verificar
docker-compose -f docker-compose-storage.yml ps

# Esperado: sqlserver, db2, sftpgo, minio, file-server en "Up"
```

### 8.3 Verificar Conectividad

```powershell
# Test SQL Server
docker-compose -f docker-compose-storage.yml exec sqlserver sqlcmd -S localhost -U sa -Q "SELECT @@VERSION"

# Test MinIO
docker-compose -f docker-compose-storage.yml exec minio mc --help
```

### 8.4 Ver Logs (Si hay problemas)

```powershell
docker-compose -f docker-compose-storage.yml logs -f
```

---

## 📨 Paso 9: Iniciar Kafka Stack

Stack de mensajería y streaming. Elige una arquitectura.

### 9.1 Opción A: KRaft (Moderno - Recomendado)

```powershell
# Navegar a kafka-kraft
cd ..\kafka-kraft

# Iniciar
docker-compose up -d

# Verificar
docker-compose ps

# Esperar ~30 segundos para que los brokers se estabilicen
Start-Sleep -Seconds 30

# Ver logs de brokers
docker-compose logs kafka1
```

### 9.2 Opción B: Zookeeper (Tradicional)

```powershell
# Navegar a kafka-zookeeper
cd ..\kafka-zookeeper

# Iniciar
docker-compose up -d

# Verificar
docker-compose ps

# Esperar ~60 segundos (Zookeeper y Kafka tardan más)
Start-Sleep -Seconds 60

# Ver logs
docker-compose logs zookeeper
```

### 9.3 Verificar Kafka (Después de esperar)

```powershell
# Listar topics
docker-compose exec kafka1 kafka-topics.sh --list --bootstrap-server kafka1:9092

# Ver brokers
docker-compose exec kafka1 kafka-metadata.sh --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log --print
```

---

## 🔬 Paso 10: Iniciar Databricks Stack

Stack de datos, ML y orquestación.

### 10.1 Generar Clave Fernet (Airflow)

```powershell
# Generar clave Fernet para Airflow
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copiar la salida
# Ej: gAAAAABl...
```

### 10.2 Actualizar docker-compose-databricks.yml

```powershell
# Abrir archivo
notepad .\databricks\docker-compose.yml

# Buscar: AIRFLOW__CORE__FERNET_KEY
# Reemplazar con la clave generada arriba

# Guardar
```

### 10.3 Iniciar Databricks

```powershell
# Navegar
cd ..\databricks

# Iniciar
docker-compose up -d

# Verificar
docker-compose ps

# Esperar ~30 segundos para que Airflow inicie
Start-Sleep -Seconds 30
```

### 10.4 Verificar Servicios

```powershell
# Ver logs
docker-compose logs -f airflow-webserver

# Esperar a ver "INFO:root:Started server process"
```

---

## ✅ Paso 11: Verificación Final

### 11.1 Verificar Todos los Contenedores

```powershell
# Ver todos en ejecución
docker ps

# Deberías ver ~15-20 contenedores corriendo
docker ps --format "{{.Image}} {{.Status}}"
```

### 11.2 Verificar Red

```powershell
# Ver servicios en mynet
docker network inspect mynet | grep -A 1 "Containers"
```

### 11.3 Test de Conectividad

```powershell
# Desde Windows hacia localhost
curl http://localhost/

# Desde Windows hacia Caddy
curl -H "Host: minio.local" http://localhost/

# Desde contenedor a otro contenedor
docker run --rm --network mynet alpine curl http://minio:9001
```

### 11.4 Acceder a Servicios

Ahora puedes acceder a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Caddy Landing | http://localhost/ | - |
| Jupyter Lab | http://jupyter.local:8888 | Ver credenciales.md |
| Spark Master | http://spark.local:8080 | - |
| Airflow | http://airflow.local:8082 | airflow/airflow |
| MLflow | http://mlflow.local:5000 | - |
| Vault | http://vault.local:8200 | Ver credenciales.md |
| MinIO Console | http://minio.local:9001 | admin/minioadmin |
| SFTPGo | http://sftp.local:51500 | Ver credenciales.md |

---

## 🛑 Paso 12: Parar Stacks (Cuando Termines)

### 12.1 Detener Individual

```powershell
# Ejemplo: detener Databricks
cd .\databricks
docker-compose down

# Ejemplo: detener Storage
cd ..\storage
docker-compose -f docker-compose-storage.yml down
```

### 12.2 Detener Todo

```powershell
# Opción 1: Detener cada stack manual
cd .\web && docker-compose -f docker-compose-caddy.yml down
cd ..\storage && docker-compose -f docker-compose-storage.yml down
cd ..\kafka-kraft && docker-compose down
cd ..\databricks && docker-compose down

# Opción 2: Script PowerShell (Copia en archivo cleanup.ps1)
```

### 12.3 Limpiar Volúmenes (⚠️ Borra datos)

```powershell
# ADVERTENCIA: Esto elimina TODOS los datos

# Limpiar un stack
cd .\databricks
docker-compose down -v

# Limpiar todo (más destructivo)
docker system prune -a --volumes
```

---

## 🔄 Reiniciar desde Cero

Si algo sale mal y quieres empezar de cero:

```powershell
# 1. Parar todos los contenedores
docker-compose down -v  # En cada carpeta

# 2. Limpiar sistema Docker
docker system prune -a --volumes

# 3. Recrear red
docker network rm mynet
docker network create mynet --driver bridge

# 4. Reiniciar desde Paso 7 (Iniciar Caddy)
```

---

## 🆘 Troubleshooting del Setup

| Problema | Causa | Solución |
|----------|-------|----------|
| Docker command not found | Docker no instalado | Instalar Docker Desktop desde docker.com |
| Network create already exists | Red ya existe | No es problema, continuar |
| Port 80/443 in use | Otro servicio usa puertos | Cambiar puertos en docker-compose o parar conflicto |
| Contenedor dice "no matching manifest" | Arquitectura CPU incompatible | Verificar que WSL2 está habilitado |
| WSL2 no disponible | Windows 10 antigua | Actualizar Windows a build 19041+ |
| Disco lleno rápido | Volúmenes sin límite | Revisar `docker system df` |
| Memoria insuficiente | Recursos RAM limitados | Aumentar en Docker Desktop Settings |

---

## 📚 Próximos Pasos

Una vez que todo esté funcionando:

1. **Lee la documentación de cada stack**
   - [Storage](./storage/README.md)
   - [Kafka](./kafka/README.md)
   - [Databricks](./databricks/README.md)
   - [Web](./web/README.md)

2. **Crea tu primer pipeline**
   - Conecta datos desde Storage a Kafka
   - Usa Spark para procesar
   - Guarda resultados en MinIO

3. **Experimenta con Airflow**
   - Define DAGs en `databricks/dags/`
   - Orquesta flujos automáticos

4. **Integra con tus datos**
   - Copia datos a SQL Server
   - Configura CDC en PostgreSQL
   - Consume eventos desde Kafka

---

## 📞 Soporte

Si tienes problemas durante el setup:

1. Revisa los [Logs](#-ver-logs-si-hay-problemas)
2. Consulta [config.md](./config.md)
3. Lee el README de cada stack
4. Abre un issue en GitHub

---

<div align="center">

**Setup completado. ¡Bienvenido al laboratorio!** 🎉

[📖 Leer README](./README.md) • [⚙️ Ver config](./config.md) • [🔐 Ver credenciales](./credenciales.md)

</div>

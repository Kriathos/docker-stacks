# 🐳 Laboratorio Integrado de Infraestructura de Datos

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%2BWSL2-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

**Ecosistema modular de datos, mensajería e infraestructura empresarial en Docker**

[Inicio Rápido](#-inicio-rápido) • [Stacks](#-stacks-disponibles) • [Documentación](#-documentación) • [Arquitectura](#-arquitectura) • [Configuración](#-configuración-inicial)

</div>

---

## 📖 Descripción

Laboratorio profesional de infraestructura de datos y mensajería para Windows con Docker Compose. Proporciona múltiples stacks independientes pero interconectados que representan patrones modernos de arquitectura empresarial.

**Ideal para:**
- 🎓 Aprendizaje de arquitecturas de microservicios
- 🧪 Validación de flujos de integración multi-tecnología
- 📊 Experimentación con streaming, CDC y orquestación
- 🏗️ Prototipos locales antes de despliegue cloud
- 🔬 Laboratorios de desarrollo con datos reales
- 🚀 Demostración de capabilidades empresariales

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                      🌐 NAVEGADOR / CLIENTE 🌐                     │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    💫 CADDY PROXY 💫       │
                    │   (Reverse Proxy Central)   │
                    │  Puerto 80 / 443 (HTTPS)    │
                    └────────┬────────────────────┘
                             │
        ┌────────────────────┼────────────────────┬─────────────────┐
        │                    │                    │                 │
        ▼                    ▼                    ▼                 ▼
    ┌────────────┐  ┌──────────────┐   ┌────────────┐   ┌──────────────┐
    │ DATABRICKS │  │     KAFKA    │   │  STORAGE   │   │   CUSTOM     │
    │  (Datos)   │  │ (Mensajería) │   │(BasesDatos)│   │  (Usuarios)  │
    └────────────┘  └──────────────┘   └────────────┘   └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼──────────┐
                    │ 🌉 Red Docker 🌉 │
                    │ (mynet - bridge)  │
                    └───────────────────┘
```

---

## ⚡ Stacks Disponibles

### 🔬 **Databricks** - Análisis de Datos y Machine Learning
**Computación distribuida, notebooks, ML y orquestación**

| Servicio | Propósito | Puerto |
|----------|-----------|--------|
| Apache Spark | Computación distribuida | 7077, 8080, 8081 |
| Jupyter Lab | Notebooks interactivos | 8888 |
| MLflow | Tracking de experimentos ML | 5000 |
| Apache Airflow | Orquestación de DAGs | 8082 |
| HashiCorp Vault | Gestión de secretos | 8200 |
| PostgreSQL | Metadatos y base de datos | 5432 |

📖 [Documentación completa](./databricks/README.md) | ⚙️ [Configuración](./databricks/config.md) | 🚀 [Setup](./databricks/setup.md)

**Casos de uso:** Análisis exploratorio, ML training, ETL local, experimentos controlados

---

### 📨 **Kafka** - Streaming y Change Data Capture
**Plataforma de mensajería empresarial con dos arquitecturas**

#### KRaft (Moderno - Recomendado)
| Servicio | Propósito | Replicas |
|----------|-----------|----------|
| Kafka Broker | Cluster con KRaft | 3 |
| Debezium Connect | CDC desde PostgreSQL | 1 |
| PostgreSQL | Source de datos | 1 |

#### Zookeeper (Tradicional)
| Servicio | Propósito | Replicas |
|----------|-----------|----------|
| Zookeeper | Coordinador de cluster | 3 |
| Kafka Broker | Cluster con ZK | 3 |
| Debezium Connect | CDC desde PostgreSQL | 1 |
| PostgreSQL | Source de datos | 1 |

📖 [Documentación completa](./kafka/README.md) | 📖 [KRaft](./kafka-kraft/README.md) | 📖 [Zookeeper](./kafka-zookeeper/README.md)

**Casos de uso:** Event streaming, CDC, replicación de datos, arquitecturas event-driven

---

### 💾 **Storage** - Bases de Datos y Almacenamiento
**Stack polivalente de almacenamiento: transaccional, NoSQL y objeto**

| Servicio | Tipo | Propósito | Puerto |
|----------|------|----------|--------|
| SQL Server | RDBMS | Base datos relacional (MSSQL) | 1433 |
| IBM DB2 | RDBMS | Base datos empresarial | 50000 |
| MinIO | Object Storage | S3-compatible local | 9000, 9001 |
| SFTPGo | File Transfer | Servidor SFTP con UI web | 2022 |
| Apache HTTP | Static Files | Servicio de archivos | 80 |

📖 [Documentación completa](./storage/README.md) | ⚙️ [Configuración](./storage/config.md) | 🚀 [Setup](./storage/setup.md)

**Casos de uso:** Multi-BD, data warehouse local, file server, lakehouse prototyping

---

### 🌐 **Web** - Proxy Inverso Centralizado
**Gateway HTTP/HTTPS con enrutamiento inteligente**

| Servicio | Propósito | Puerto |
|----------|-----------|--------|
| Caddy | Reverse proxy + TLS auto | 80, 443 |
| Landing Page | Interfaz central de acceso | 80 |

📖 [Documentación completa](./web/README.md) | ⚙️ [Configuración](./web/config.md)

**Casos de uso:** Enrutamiento centralizado, HTTPS automático, acceso único a todos los servicios

---

## 🚀 Inicio Rápido

### Paso 1: Verificar Requisitos

```powershell
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version

# WSL2 habilitado
wsl -l -v
```

**Requisitos mínimos:**
- ✅ Docker Desktop 4.0+ para Windows
- ✅ WSL2 habilitado
- ✅ 8GB RAM disponible (16GB recomendado)
- ✅ PowerShell 5.0+ o PowerShell Core

### Paso 2: Crear Red Compartida

```powershell
# Crear red Docker para interconectar stacks
docker network create mynet --driver bridge

# Verificar
docker network ls | findstr mynet
```

### Paso 3: Configurar Hosts Locales (Recomendado)

Edita `C:\Windows\System32\drivers\etc\hosts` como administrador:

```hosts
# Caddy proxy y servicios
127.0.0.1 localhost
127.0.0.1 sftp.local
127.0.0.1 minio.local
127.0.0.1 minio-api.local
127.0.0.1 data.local
127.0.0.1 spark.local

# Kafka
127.0.0.1 kraft-ui.local
127.0.0.1 zoo-ui.local

# Databricks
127.0.0.1 jupyter.local
127.0.0.1 mlflow.local
127.0.0.1 airflow.local
127.0.0.1 vault.local
```

### Paso 4: Iniciar Stacks

**🌐 Primero: Proxy web (recomendado)**
```powershell
cd .\web
docker-compose -f docker-compose-caddy.yml up -d
docker-compose -f docker-compose-caddy.yml ps
```

**💾 Stack de Storage**
```powershell
cd .\storage
docker-compose -f docker-compose-storage.yml up -d
docker-compose -f docker-compose-storage.yml ps
```

**📨 Stack de Kafka (KRaft por defecto)**
```powershell
cd .\kafka-kraft
docker-compose up -d
docker-compose ps
```

**🔬 Stack de Databricks**
```powershell
cd .\databricks
docker-compose up -d
docker-compose ps
```

### Paso 5: Verificar Conectividad

```powershell
# Ver todos los contenedores corriendo
docker ps

# Verificar red
docker network inspect mynet

# Ver logs de un servicio
docker-compose logs -f <servicio>
```

---

## 📚 Documentación Completa

### Guías de Inicio
| Documento | Propósito |
|-----------|----------|
| [`SETUP.md`](./SETUP.md) | 🚀 Guía paso a paso de instalación |
| [`README.md`](./README.md) | 📖 Este documento |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | 🏗️ Arquitectura detallada y diagramas |

### Configuración Global
| Documento | Propósito |
|-----------|----------|
| [`config.md`](./config.md) | ⚙️ Configuración global, variables y parámetros |
| [`credenciales.md`](./credenciales.md) | 🔐 Credenciales centralizadas (⚠️ No para producción) |

### Documentación por Stack
| Stack | README | Config | Setup |
|-------|--------|--------|-------|
| **Web (Caddy)** | [📖](./web/README.md) | [⚙️](./web/config.md) | - |
| **Storage** | [📖](./storage/README.md) | [⚙️](./storage/config.md) | [🚀](./storage/setup.md) |
| **Kafka** | [📖](./kafka/README.md) | [⚙️](./kafka/config.md) | - |
| **Kafka KRaft** | [📖](./kafka-kraft/README.md) | [⚙️](./kafka-kraft/config.md) | - |
| **Kafka Zookeeper** | [📖](./kafka-zookeeper/README.md) | [⚙️](./kafka-zookeeper/config.md) | - |
| **Databricks** | [📖](./databricks/README.md) | [⚙️](./databricks/config.md) | [🚀](./databricks/setup.md) |

---

## ⚙️ Configuración Inicial

Ver [`config.md`](./config.md) para:
- 🌉 Configuración de red Docker (`mynet`)
- 🖥️ Montajes locales en Windows
- 📍 Configuración de hosts y dominios
- 🔑 Variables de entorno globales
- 🔒 Consideraciones de seguridad

---

## 🔐 Credenciales

**⚠️ Importante:** Este proyecto contiene credenciales de laboratorio en [`credenciales.md`](./credenciales.md).

**Antes de usar en producción:**
1. ✅ Reemplaza todas las contraseñas por valores seguros
2. ✅ Usa gestión de secretos (Vault, AWS Secrets Manager, etc.)
3. ✅ Implementa autenticación multi-factor
4. ✅ Habilita cifrado en tránsito y en reposo
5. ✅ Realiza auditoría de seguridad completa

Todas las credenciales están centralizadas en [`credenciales.md`](./credenciales.md) - No las repliques en otros archivos.

---

## 🛠️ Operaciones Comunes

### Iniciar un Stack
```powershell
cd .\<stack>
docker-compose -f docker-compose-<stack>.yml up -d
```

### Detener un Stack
```powershell
cd .\<stack>
docker-compose -f docker-compose-<stack>.yml down
```

### Limpiar Volúmenes (⚠️ Borra datos)
```powershell
cd .\<stack>
docker-compose -f docker-compose-<stack>.yml down -v
```

### Ver Logs en Vivo
```powershell
cd .\<stack>
docker-compose logs -f <servicio>
```

### Ejecutar Comando en Contenedor
```powershell
docker-compose -f docker-compose-<stack>.yml exec <servicio> <comando>
```

### Verificar Red
```powershell
docker network inspect mynet
```

### Limpiar Todo (⚠️ Destructivo)
```powershell
# Detener y eliminar TODOS los contenedores
docker-compose -f docker-compose-<stack>.yml down -v
docker system prune -a
docker network rm mynet
```

---

## 🔍 Troubleshooting

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Servicios no comunican | Connection refused | Verificar `docker network inspect mynet` |
| Contenedor no inicia | Error en logs | Ver `docker-compose logs -f <servicio>` |
| Hostnames no resuelven | ERR_NAME_NOT_RESOLVED | Verificar archivo hosts y Caddy corriendo |
| Puerto en uso | Bind error | Cambiar puerto en `docker-compose-*.yml` |
| Contenedor lento | High latency | Revisar recursos Docker (CPU/RAM) |
| Volúmenes persistencia | Datos perdidos | Verificar montar con volúmenes nombrados |
| TLS certificados | HTTPS error | Verificar directorios caddy_data y caddy_config |

---

## 🎯 Casos de Uso

### 📚 Aprendizaje Académico
Entorno completo para estudiar data engineering sin necesidad de cloud.

### 🧪 Pruebas de Concepto (PoC)
Valida arquitecturas complejas antes de invertir en infraestructura cloud.

### 🔬 Investigación y Experimentación
Laboratorio aislado y reproducible para probar nuevas tecnologías.

### 📊 Desarrollo Local
Stack reproducible idéntico al que usarás en producción.

### 🚀 Demostración
Muestra capacidades empresariales sin necesidad de múltiples clouds.

---

## 📊 Matriz Tecnológica

| Categoría | Tecnologías |
|-----------|-------------|
| **Compute** | Apache Spark, Docker, Kubernetes |
| **Data Processing** | PySpark, Python, Jupyter |
| **Storage** | PostgreSQL, SQL Server, DB2, MinIO, HDFS |
| **Streaming** | Apache Kafka (KRaft/Zookeeper), Debezium, CDC |
| **Orchestration** | Apache Airflow, Kubernetes Operators |
| **ML/Analytics** | MLflow, Scikit-Learn, Spark MLlib |
| **Secrets** | HashiCorp Vault |
| **Web/Proxy** | Caddy, Nginx |
| **Container** | Docker, Docker Compose |

---

## 🚀 Despliegue en GitHub

Este repositorio está diseñado para ser compartido y replicado fácilmente:

1. **Clon el repositorio**
   ```powershell
   git clone https://github.com/tu-usuario/data-infrastructure-lab.git
   cd data-infrastructure-lab
   ```

2. **Sigue la guía SETUP.md**
   ```powershell
   # Lee la guía completa
   cat .\SETUP.md
   ```

3. **Inicia los stacks según necesites**
   ```powershell
   # Ver documentación de cada stack
   # Ejemplo: cat .\storage\setup.md
   ```

4. **Customiza según tu necesidad**
   - Modifica credenciales en `credenciales.md`
   - Ajusta rutas Windows en `config.md`
   - Personaliza `docker-compose-*.yml`

---

## 📞 Soporte y Contribuciones

- 📖 Lee la documentación completa en cada carpeta
- 🐛 Reporta problemas en Issues
- 🔗 Referencias están en `config.md` y `credenciales.md`
- ✨ Las mejoras son bienvenidas via Pull Requests

---

## 📄 Licencia

MIT License - Libre para uso educativo, de laboratorio y comercial. Ver LICENSE.

---

## 🙏 Créditos

Construido para educación en infraestructura de datos moderna con tecnologías open-source.

---

<div align="center">

**Laboratorio completo de ingeniería de datos y microservicios para Windows**

[📖 Leer documentación completa](./SETUP.md) • [🔧 Ver configuración](./config.md) • [🔐 Ver credenciales](./credenciales.md)

[⬆ Volver arriba](#-laboratorio-integrado-de-infraestructura-de-datos)

</div>

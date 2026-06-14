# 📡 Web Stack

<div align="center">

![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)
![Reverse Proxy](https://img.shields.io/badge/Reverse%20Proxy-Load%20Balancer-blue?style=flat-square)
![Docker Network](https://img.shields.io/badge/Docker%20Network-mynet-2496ED?style=flat-square&logo=docker&logoColor=white)

**Proxy centralizado para orquestación de stacks**

[Descripción](#descripción) • [Servicios](#-servicios) • [Inicio Rápido](#-inicio-rápido) • [Configuración](#-configuración) • [Rutas](#-rutas)

</div>

---

## 📋 Descripción

Stack de **Nginx** como proxy inverso centralizado para todos los servicios.

**Beneficios:**
- ✅ Acceso unificado por hostnames locales
- ✅ Enrutamiento automático a servicios internos
- ✅ Simplifica integración entre stacks
- ✅ Gestión centralizada de puertos
- ✅ Sin necesidad de exponer puertos individuales

---

## 🚀 Inicio Rápido

> **Prerrequisito:** crea `nginx.conf` siguiendo la guía en [config.md](config.md) antes de levantar el stack.

```powershell
cd .\\web
docker compose up -d
docker compose ps
```

---

## 📍 Servicios y rutas

| Hostname | Servicio | Descripción |
|----------|----------|------------|
| **sftp.dominio.com** | SFTPGo:8080 | UI SFTP |
| **minio.dominio.com** | MinIO:9001 | Consola MinIO |
| **minio-api.dominio.com** | MinIO:9000 | API S3 |
| **data.dominio.com** | Apache:80 | Archivos estáticos |
| **kraft-ui.dominio.com** | Kafka UI KRaft:8080 | Monitor Kafka |
| **kraft-api.dominio.com** | Debezium KRaft:8083 | Connect |
| **zoo-ui.dominio.com** | Kafka UI Zoo:8080 | Monitor Zoo |
| **zoo-api.dominio.com** | Debezium Zoo:8083 | Connect Zoo |
| **jupyter.dominio.com** | Jupyter:8888 | Notebooks |
| **mlflow.dominio.com** | MLflow:5000 | ML Tracking |
| **airflow.dominio.com** | Airflow:8080 | Orquestación |
| **vault.dominio.com** | Vault:8200 | Gestión secretos |
| **spark.dominio.com** | Spark:8080 | Cluster Spark |

---

## ⚙️ Configuración

### nginx.conf

El archivo de configuración de Nginx **no está versionado** porque contiene dominios locales personales. Debes crearlo antes de levantar el stack.

📖 [Guía completa para crear nginx.conf](config.md) — template, explicación de cada bloque, WebSocket y validación.

### Archivo hosts Windows

Editar: `C:\Windows\System32\drivers\etc\hosts`

```text
127.0.0.1 sftp.dominio.com
127.0.0.1 minio.dominio.com
127.0.0.1 minio-api.dominio.com
127.0.0.1 data.dominio.com
127.0.0.1 kraft-ui.dominio.com
127.0.0.1 kraft-api.dominio.com
127.0.0.1 zoo-ui.dominio.com
127.0.0.1 zoo-api.dominio.com
127.0.0.1 jupyter.dominio.com
127.0.0.1 mlflow.dominio.com
127.0.0.1 airflow.dominio.com
127.0.0.1 vault.dominio.com
127.0.0.1 spark.dominio.com
```

### Network Docker

Todos los servicios en red `mynet`:
```bash
docker network create mynet --driver bridge
```

---

## 💼 Uso

### Acceder a servicios

```powershell
# Jupyter Lab
http://jupyter.dominio.com

# MinIO Console
http://minio.dominio.com

# MLflow
http://mlflow.dominio.com

# Airflow
http://airflow.dominio.com

# Kafka Monitor
http://kraft-ui.dominio.com
```

### Configurar nuevas rutas

Agrega un bloque `server` en `nginx.conf` (ver [config.md](config.md) para el template completo):

```nginx
server {
    listen 80;
    server_name mi-servicio.tu-dominio.com;

    location / {
        proxy_pass http://nombre-contenedor:puerto-interno;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Recargar sin reiniciar el contenedor:
```powershell
docker compose exec nginx nginx -s reload
```

---

## 🏗️ Arquitectura

```mermaid
flowchart TB
  Browser[🌐 Browser]
  
  Browser -->|HTTP requests| Nginx["📡 Nginx<br/>Port 80"]
  
  Nginx -->|sftp.dominio.com| SFTPGo["SFTPGo"]
  Nginx -->|minio.dominio.com| MinIO["MinIO"]
  Nginx -->|jupyter.dominio.com| Jupyter["Jupyter"]
  Nginx -->|mlflow.dominio.com| MLflow["MLflow"]
  Nginx -->|airflow.dominio.com| Airflow["Airflow"]
  Nginx -->|kraft-ui.dominio.com| KafkaUI["Kafka UI"]
  
  style Nginx fill:#f4c,stroke:#333
  style Browser fill:#a2a,stroke:#333
```

---

## 🔌 Integración con stacks

### Storage
- MinIO disponible en `minio.dominio.com`
- SFTPGo en `sftp.dominio.com`
- Apache en `data.dominio.com`

### Kafka
- KRaft UI en `kraft-ui.dominio.com`
- Zookeeper UI en `zoo-ui.dominio.com`
- Debezium API en `kraft-api.dominio.com`

### Databricks
- Jupyter en `jupyter.dominio.com`
- MLflow en `mlflow.dominio.com`
- Airflow en `airflow.dominio.com`
- Spark en `spark.dominio.com`

---

## 🛑 Operaciones

### Detener
```powershell
docker compose down
```

### Ver logs
```powershell
docker compose logs -f nginx
```

### Recargar configuración
```powershell
docker compose exec nginx nginx -s reload
```

### Verificar servicios
```powershell
docker network inspect mynet
```

---

## ✋ Problemas

| Problema | Solución |
|----------|----------|
| ❌ Hostname no resuelve | Verificar `/etc/hosts` |
| ❌ 502 Bad Gateway | Servicio no activo o no en `mynet` |
| ❌ Nginx no inicia | `docker compose logs nginx` |
| ❌ Puerto 80 en uso | Cambiar puerto en `docker-compose.yml` |

---

## ⚠️ Seguridad

- Solo para **desarrollo local**
- Sin TLS/HTTPS configurado
- No expongas en redes no controladas
- Para producción: agregar certificados SSL

---

## 📚 Recursos

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Nginx Proxy Config](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [⚙️ Guía nginx.conf de este proyecto](config.md)

---

<div align="center">

[⬆ Arriba](#-web-stack) • [← Proyecto Principal](../README.md) • [⚙️ nginx.conf Guide](config.md)

**Stacks relacionados:** [🔬 Databricks](../databricks/README.md) • [📨 Kafka](../kafka/README.md) • [💾 Storage](../storage/README.md)

</div>

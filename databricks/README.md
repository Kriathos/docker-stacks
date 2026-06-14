# 🔬 Databricks Stack

<div align="center">

![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=flat-square&logo=apache-spark&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37726?style=flat-square&logo=jupyter&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=python&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat-square&logo=apache-airflow&logoColor=white)
![Vault](https://img.shields.io/badge/HashiCorp%20Vault-000000?style=flat-square&logo=vault&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)

**Laboratorio integrado de análisis de datos, machine learning y orquestación**

[Descripción](#descripción) • [Tecnologías](#-tecnologías) • [Servicios](#-servicios) • [Inicio Rápido](#-inicio-rápido) • [Configuración](#-configuración) • [Uso](#-uso)

</div>

---

## 📋 Descripción

Stack especializado para ciencia de datos, análisis y machine learning en local. Proporciona un entorno completo con:

- **Computación distribuida** con Apache Spark
- **Notebooks interactivos** con Jupyter Lab
- **Experimentación ML** con MLflow para tracking
- **Orquestación de workflows** con Apache Airflow
- **Gestión de secretos** con HashiCorp Vault
- **Base de datos** PostgreSQL para almacenar metadatos

Ideal para prototipado, investigación y desarrollo de pipelines de datos localmente sin dependencias cloud.

---

## 🛠️ Tecnologías

| Servicio | Versión | Puerto | Descripción |
|----------|---------|--------|------------|
| **Spark Master** | 3.x | 7077, 8080 | Master del cluster Spark |
| **Spark Worker** | 3.x | 8081 | Nodo worker del cluster |
| **Jupyter Lab** | Latest | 8888 | Notebooks interactivos |
| **MLflow** | Latest | 5000 | Tracking de experimentos |
| **Airflow Webserver** | 2.x | 8082 | Orquestación de DAGs |
| **Airflow Scheduler** | 2.x | - | Scheduler de tareas |
| **Vault** | Latest | 8200 | Gestión de secretos |
| **PostgreSQL** | 13 | 5432 | Metadatos y persistencia |

---

## 🔌 Servicios

### Análisis y Exploración
- **Jupyter Lab** con PySpark preconfigurado
- Delta Lake integration
- Librerías de ciencia de datos (pandas, numpy, scikit-learn)

### Orquestación
- **Airflow** con LocalExecutor
- DAGs definidos en `dags/`
- PostgreSQL para metadatos

### Tracking de ML
- **MLflow** para registrar experimentos
- Artefactos en `mlruns/`
- Gestión de modelos

### Secretos
- **Vault** en modo dev
- Integración con Jupyter y Airflow

---

## 🚀 Inicio Rápido

### 1. Preparar el entorno
```powershell
cd .\databricks
```

### 2. Iniciar servicios
```powershell
docker compose up -d
```

### 3. Verificar servicios activos
```powershell
docker compose ps
```

### 4. Acceder a los servicios

| Servicio | URL |
|----------|-----|
| Jupyter Lab | http://localhost:8888 |
| Spark Master UI | http://localhost:8080 |
| Airflow | http://localhost:8082 |
| MLflow | http://localhost:5000 |
| Vault UI | http://localhost:8200 |

---

## ⚙️ Configuración

### Variables de entorno

```bash
JUPYTER_ENABLE_LAB=yes
AIRFLOW_HOME=/opt/airflow
VAULT_ADDR=http://vault:8200
```

### Credenciales

Todas las credenciales están centralizadas en [`credenciales.md`](../credenciales.md):
- 🔐 Usuarios y contraseñas
- 🔑 Tokens de Vault
- 🗝️ Claves de acceso

### Configuración de red

- Red compartida: `mynet`
- Comunicación interna: `servicename:puerto`
- Acceso desde host: `localhost:puerto`

---

## 💼 Uso Común

### Ejecutar notebooks
```powershell
# Ver logs de Jupyter
docker compose logs -f jupyter

# Acceder a http://localhost:8888
# Token disponible en logs
```

### Monitorear Spark
```powershell
# Acceder a http://localhost:8080
docker compose logs -f spark-master
```

### Crear DAG en Airflow
```powershell
# Los DAGs van en ./dags/
# Crear archivo: ./dags/mi_dag.py
docker compose logs -f airflow-scheduler
```

### Consultar PostgreSQL
```powershell
docker compose exec postgres psql -U postgres -d airflow -c "SELECT * FROM dag_run LIMIT 10;"
```

### Gestionar Vault
```powershell
# Acceder a http://localhost:8200
docker compose exec vault vault secrets list
```

---

## 📁 Estructura

```
databricks/
├── docker-compose.yml          # Configuración de servicios
├── README.md                    # Este archivo
├── notebooks/                   # Notebooks Jupyter
│   ├── Conexiones.ipynb
│   ├── TestDelta.ipynb
│   ├── TestMinio.ipynb
│   └── TestVault.ipynb
├── dags/                        # DAGs de Airflow
├── jars/                        # Librerías personalizadas
├── mlruns/                      # Experimentos MLflow
└── vault/                       # Datos de Vault (NO VERSIONADO)
```

---

## 🔌 Integración con otros stacks

- **Kafka → Databricks**: Consume eventos en tiempo real
- **Storage → Databricks**: Lee de MinIO o SQL Server
- **MLflow compartido**: Modelos reutilizables

---

## 🛑 Detener y limpiar

```powershell
# Detener (mantiene volúmenes)
docker compose down

# Limpiar todo (⚠️ borra datos)
docker compose down -v

# Ver logs de errores
docker compose logs --tail 50
```

---

## ✋ Solución de Problemas

| Problema | Solución |
|----------|----------|
| ❌ Jupyter no accesible | Revisar `docker compose logs jupyter` |
| ❌ Spark worker offline | Reiniciar: `docker compose restart spark-master` |
| ❌ Airflow no sincroniza DAGs | DAGs en `./dags/` se monitorean automáticamente |
| ❌ Vault sealed | Acceder a http://localhost:8200 |
| ❌ PostgreSQL conexión rechazada | Verificar credenciales en `credenciales.md` |

---

<div align="center">

[⬆ Volver arriba](#-databricks-stack) • [← Volver al proyecto principal](../README.md)

</div>

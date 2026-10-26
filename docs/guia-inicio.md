# Guía de inicio: primer login de cada grupo

Esta guía recorre los grupos del laboratorio en el orden en que conviene levantarlos y dice qué hacer la primera vez que entras a cada servicio. Para la configuración general (`.env`, DNS, puertos), ver la [guía del laboratorio](guia.md).

Antes de empezar:

```powershell
.\scripts\labs.ps1 up all
.\scripts\labs.ps1 status
```

Si un grupo no aparece como `running`, revisa su log con `docker logs <contenedor>` antes de seguir.

---

## 1. seguridad (Caddy y CrowdSec)

**Servicios:** Caddy (entrada HTTP y HTTPS de todo el laboratorio) y CrowdSec (lee los logs de Caddy).

**Primer arranque:**
1. Caddy pide certificados a Let's Encrypt la primera vez que llega una petición a cada subdominio. Verifica en `docker logs caddy` que aparezca `certificate obtained`. Si aparece `too many`, espera a que Let's Encrypt libere el límite y no reinicies en bucle.
2. CrowdSec no necesita configuración manual para empezar. Para ver si detectó algo: `docker exec crowdsec cscli alerts list`.

**Cambios posteriores al Caddyfile:** `docker restart caddy`. Con `admin off` no se puede recargar en caliente.

---

## 2. storage

**Servicios:** SQL Server, DB2, SFTPGo, MinIO y Apache Fileserver.

| Servicio | Dónde entrar | Primer login |
|---|---|---|
| SQL Server | DBeaver o SSMS, `<tu-ip>,51430` | Usuario `sa` y clave `SQLSERVER_SA_PASSWORD`. Crea un usuario propio para trabajar y deja `sa` solo para administrar. |
| DB2 | DBeaver, `<tu-ip>:51431`, base `SAMPLE` | Usuario `db2inst1` y clave `DB2_INSTANCE_PASSWORD`. El primer arranque tarda varios minutos. |
| SFTPGo | `https://sftp.luispicado.com` | La primera vez pide crear el administrador. Después, agrega los usuarios SFTP que necesites desde la web. |
| MinIO | `https://minio.luispicado.com` | Usuario `MINIO_ROOT_USER` y clave `MINIO_ROOT_PASSWORD`. **Crea los buckets `bronce` y `warehouse`** (ver nota). |
| Apache Fileserver | `https://data.luispicado.com` | Pide el usuario y clave de Caddy. No requiere configuración. |

> **Nota sobre MinIO:** los notebooks de Jupyter escriben en el bucket `bronce`, y Hive Metastore guarda sus tablas Delta en `warehouse`. Ninguno de los dos se crea solo. Hazlo desde la consola: *Buckets → Create Bucket*.

---

## 3. kafka-zookeeper

**Servicios:** Zookeeper, Kafka, Kafka UI, Kafka Connect y Postgres (para Connect).

**Primer login:**
1. Abre Kafka UI en `https://zoo-ui.luispicado.com` (clave de Caddy). Debe mostrar el cluster y sus topics.
2. Kafka Connect responde en `https://zoo-api.luispicado.com` (clave de Caddy). Revisa los conectores registrados con `GET /connectors`, por ejemplo desde el navegador tras la clave de Caddy.
3. Desde Jupyter, el broker se alcanza en `kafka:29092`.

> No hay usuario ni contraseña de Kafka: el listener es `PLAINTEXT`. Ver [riesgos conocidos](../SECURITY.md).

---

## 4. kafka-kraft

**Servicios:** tres brokers Kafka en modo KRaft, Kafka UI, Kafka Connect y Postgres.

**Primer login:**
1. Abre Kafka UI en `https://kraft-ui.luispicado.com` (clave de Caddy) y confirma que los tres brokers aparecen.
2. Kafka Connect responde en `https://kraft-api.luispicado.com` (clave de Caddy).
3. Desde Jupyter, un broker se alcanza en `kafka1:9092`.

> `KRAFT_CLUSTER_ID` en `.env` debe coincidir con el que guardó el volumen. Si no coincide, los brokers no arrancan. No lo cambies una vez creado el volumen.

---

## 5. databricks

**Servicios:** Spark (master y worker), Jupyter, MLflow, Hive Metastore con su Postgres, y Vault.

**Primer login, en este orden:**

1. **Vault.** Abre `https://vault.luispicado.com`. Como ya está inicializado, solo hay que desbloquearlo si se reinició:
   ```powershell
   docker exec -it vault vault operator unseal   # tres veces, con tres claves distintas
   ```
   Si nunca se inicializó, `docker exec -it vault vault operator init` genera las 5 claves. Guárdalas fuera del repositorio.

2. **Spark.** `https://spark.luispicado.com` (clave de Caddy). Debe aparecer un worker vivo (`spark-worker`). Si dice `aliveworkers: 0`, revisa que el worker esté solo en `datalab`.

3. **MLflow.** `https://mlflow.luispicado.com` (clave de Caddy). No hay usuario que crear. Sus datos quedan en `stacks/databricks/mlruns`.

4. **Hive Metastore.** No tiene interfaz. Revisa que haya escuchado en el puerto 9083:
   ```powershell
   docker logs hive-metastore
   ```
   El esquema se crea solo al arrancar. Antes de usarlo desde Spark, el bucket `warehouse` debe existir en MinIO.

5. **Jupyter.** `https://jupyter.luispicado.com`. Pide el token `JUPYTER_TOKEN` de `.env`. Al entrar, abre un notebook de prueba y ejecuta una sesión de Spark conectada al master:
   ```python
   from pyspark.sql import SparkSession
   spark = SparkSession.builder.master("spark://spark:7077").getOrCreate()
   ```
   Si no conecta, revisa que el bucket `bronce` exista antes de leer o escribir en MinIO.

---

## 6. orquestacion

**Servicios:** Airflow (webserver, scheduler, init) y su Postgres.

**Primer arranque:**
1. Construye la imagen la primera vez, porque incluye Java, PySpark y papermill:
   ```powershell
   docker compose -f stacks/orquestacion/compose.yaml build
   ```
2. `airflow-init` aparece como `Exited (0)`. Es normal: solo migra la base de datos y termina. No lo reinicies salvo que quieras volver a migrar.
3. Crea el usuario administrador. Sin él no puedes entrar al webserver:
   ```powershell
   docker exec -it airflow-webserver airflow users create --username admin --firstname Admin --lastname Lab --role Admin --email admin@example.com --password "TU_CLAVE"
   ```
4. Entra a `https://airflow.luispicado.com` con ese usuario. El DAG `notebook_papermill` ejecuta `TestMinio.ipynb` y deja la copia en `stacks/orquestacion/notebooks_out`.

---

## 7. observabilidad

**Servicios:** Prometheus, Grafana y cAdvisor. Las métricas del host Windows las da `windows_exporter`, que corre como servicio fuera de Docker.

**Antes de Grafana, confirma `windows_exporter`:**
```powershell
Get-Service windows_exporter
curl.exe -s http://localhost:9182/metrics | Select-Object -First 3
```
Si no responde, instálalo como indica la [sección 2 de la guía](guia.md#2-requisitos-previos).

**Primer login en Grafana:**
1. Abre `https://grafana.luispicado.com` con `GRAFANA_ADMIN_USER` y `GRAFANA_ADMIN_PASSWORD`.
2. Agrega la fuente de datos: **Connections → Data sources → Add data source → Prometheus**. URL: `http://prometheus:9090`. Guarda con *Save & test*.
3. Para el panel de Windows, importa el dashboard con ID 14694 (*Dashboards → New → Import*) y elige la fuente Prometheus. Si algún panel queda vacío, revisa que su variable `server` tenga el valor `host.docker.internal:9182`.

**Prometheus:** `https://prometheus.luispicado.com` (clave de Caddy). En **Status → Targets** deben aparecer `prometheus`, `cadvisor` y `windows-host` como `UP`.

---

## 8. monitoreo

**Servicios:** Uptime Kuma, ntfy y Portainer.

**Primer login:**
1. **Uptime Kuma:** `https://kuma.luispicado.com`. La primera vez crea la cuenta de administrador.
2. **ntfy:** `https://ntfy.luispicado.com`. No permite acceso anónimo, así que crea el usuario antes de usarlo:
   ```powershell
   docker exec -it ntfy ntfy user add --role=admin TU_USUARIO
   ```
   Después, en Uptime Kuma, agrega una notificación de tipo ntfy con URL `http://ntfy:80`, tu tópico y un token creado para ese usuario.
3. **Portainer:** `https://portainer.luispicado.com`.
   - Primero pide la clave de Caddy.
   - Luego pide un **setup token** que aparece en los logs:
     ```powershell
     docker logs portainer 2>&1 | Select-String setup_token | Select-Object -Last 1
     ```
   - Crea la cuenta de administrador **dentro de 5 minutos**. Si se pasa el tiempo, reinicia con `docker restart portainer` y vuelve a intentar.
   - Al elegir el entorno, usa el Docker local. **No habilites Edge Compute.**

---

## 9. herramientas

**Servicios:** pgAdmin, FileBrowser y Homepage.

**Primer login:**
1. **pgAdmin:** `https://pgadmin.luispicado.com` con `PGADMIN_DEFAULT_EMAIL` y `PGADMIN_DEFAULT_PASSWORD`. Para agregar un servidor, usa el nombre del contenedor como host y el puerto `5432`. Ejemplo: host `airflow-postgres`, usuario `airflow`, base `airflow`. Los datos de cada Postgres están en la [sección 6 de la guía](guia.md#herramientas).
2. **FileBrowser:** `https://files.luispicado.com` con `FILEBROWSER_ADMIN_USER` y `FILEBROWSER_ADMIN_PASSWORD`. Trabaja sobre `${DATA_ROOT}/apache-fileserver`, la misma carpeta que sirve `data.luispicado.com`.
3. **Homepage:** `https://luispicado.com`. No pide login. Sus enlaces están en `stacks/herramientas/homepage/config`.

---

## Orden recomendado la primera vez

1. `seguridad` (Caddy necesita estar arriba para que los dominios respondan).
2. `storage` y crear los buckets `bronce` y `warehouse` en MinIO.
3. `kafka-zookeeper` y `kafka-kraft`.
4. `databricks`: desbloquear Vault, luego probar Spark, Jupyter y Hive.
5. `orquestacion`: construir la imagen y crear el usuario de Airflow.
6. `observabilidad`: Grafana y el dashboard de Windows.
7. `monitoreo`: Uptime Kuma, ntfy y Portainer (el setup token caduca en 5 minutos).
8. `herramientas`: pgAdmin y FileBrowser.

Las pantallas de login que dependen de tu decisión (claves, usuarios, tokens) quedan en tus manos. Ninguna contraseña se guarda en esta guía.

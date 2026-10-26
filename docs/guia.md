# Guía del laboratorio

Esta guía explica cómo está organizado el laboratorio, cómo levantarlo, cómo entrar a cada servicio y cómo agregar uno nuevo. Para el primer arranque paso a paso, de cada grupo, mira [Guía de inicio](guia-inicio.md).

---

## 1. Resumen

El laboratorio está dividido en **grupos**. Cada grupo es un conjunto de **servicios** que están relacionados, y se declaran en un **stack** (un archivo `compose.yaml` dentro de `stacks/<grupo>/`).

| Grupo | Stack | Servicios |
|---|---|---|
| `storage` | `stacks/storage/compose.yaml` | SQL Server, DB2, SFTPGo, MinIO, Apache Fileserver |
| `kafka-zookeeper` | `stacks/kafka-zookeeper/compose.yaml` | Zookeeper, Kafka, Kafka UI, Kafka Connect, Postgres |
| `kafka-kraft` | `stacks/kafka-kraft/compose.yaml` | 3 brokers Kafka KRaft, Kafka UI, Kafka Connect, Postgres |
| `databricks` | `stacks/databricks/compose.yaml` | Spark (master y worker), Jupyter, MLflow, Hive Metastore con su Postgres, Vault |
| `orquestacion` | `stacks/orquestacion/compose.yaml` | Airflow y su Postgres |
| `observabilidad` | `stacks/observabilidad/compose.yaml` | Prometheus, Grafana, cAdvisor |
| `monitoreo` | `stacks/monitoreo/compose.yaml` | Uptime Kuma, ntfy, Portainer |
| `herramientas` | `stacks/herramientas/compose.yaml` | pgAdmin, FileBrowser, Homepage |
| `seguridad` | `stacks/seguridad/compose.yaml` | Caddy, CrowdSec |

Las métricas del host Windows no son un contenedor: las da `windows_exporter`, que corre como servicio de Windows fuera de Docker y que Prometheus consulta en `host.docker.internal:9182`. Ver [sección 2](#2-requisitos-previos).

**Redes:**
- Cada grupo tiene su propia red interna, creada por Docker Compose.
- La red compartida `datalab` conecta los servicios que necesitan hablar entre grupos, y los servicios HTTP que Caddy debe alcanzar.
- Un servicio que se llama por su nombre (por ejemplo, Spark worker → `spark:7077`) debe estar en **una sola** red compartida con el destino. Si el nombre resuelve a dos IPs en redes distintas, la conexión falla. Por eso `spark-worker` y `jupyter` están solo en `datalab`. Ver [ADR 0002](adr/0002-un-stack-por-grupo-y-red-datalab.md).

---

## 2. Requisitos previos

1. **Docker Desktop** instalado y corriendo.
2. **Carpeta de datos** (`DATA_ROOT` en `.env`): debe existir y contiene estas subcarpetas: `sftp`, `sftpgo-data`, `minio-data`, `apache-fileserver` y `sql-backups`. Con `DATA_ROOT=F:`, las rutas son `F:/sftp`, `F:/sql-backups`, etc. Si tu carpeta raíz es otra unidad, cámbiala en `DATA_ROOT`.
3. **PowerShell 7** (`pwsh`) para ejecutar `scripts\labs.ps1`.
4. **Archivo `.env`** en la raíz del proyecto (ver sección 3).
5. **windows_exporter** en Windows, para las métricas del host (CPU, memoria, disco, red, NTP). Se instala una vez y corre como servicio:
   ```powershell
   winget install -e --id Prometheus.WindowsExporter --silent --accept-package-agreements --accept-source-agreements
   # Como administrador: registrar el servicio con los colectores que usa el dashboard
   $exe = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter windows_exporter.exe | Select-Object -First 1).FullName
   sc.exe create windows_exporter binPath= "`"$exe`" --collectors.enabled=cpu,memory,logical_disk,physical_disk,net,os,service,system,time" start= auto
   sc.exe description windows_exporter "Prometheus exporter de metricas de Windows (puerto 9182)"
   sc.exe start windows_exporter
   # Regla de firewall para que Docker llegue al puerto 9182
   New-NetFirewallRule -DisplayName "windows_exporter 9182" -Direction Inbound -Protocol TCP -LocalPort 9182 -Action Allow
   ```
   Comprueba que responda: `curl.exe -s http://localhost:9182/metrics | Select-Object -First 3`.

   > El colector `time` expone la sincronización NTP (`windows_time_clock_sync_source`). El offset en segundos no lo expone esta versión del exporter.

---

## 3. Configuración inicial (una sola vez)

### 3.1 Crear `.env`

```powershell
Copy-Item .env.example .env
```

Abre `.env` y completa cada valor vacío. Las contraseñas actuales están en `credenciales.md` (archivo local, ignorado por git).

Compose se detiene con un mensaje claro si una variable obligatoria está vacía (`${VAR:?}`).

El `.env` va **en la raíz**, una sola vez para todos los grupos. `scripts\labs.ps1` lo pasa a cada stack con `--env-file`. Si ejecutas `docker compose` a mano desde una carpeta de stack, indícalo tú:

```powershell
docker compose --env-file ..\..\.env -f stacks\storage\compose.yaml up -d
```

Variables sensibles a tener en cuenta:

- `PGADMIN_DEFAULT_EMAIL` debe ser una dirección de correo válida (con `@`), porque pgAdmin la usa como usuario de login.
- `KRAFT_CLUSTER_ID` debe coincidir con el `cluster.id` que ya guardó el volumen de Kafka KRaft. Si lo cambias, los brokers no arrancan.

### 3.2 Generar la contraseña de los servicios sin login

Caddy protege con usuario y clave los servicios que no tienen login propio (Apache, Kafka UI, Kafka Connect, MLflow, Spark, Prometheus y Portainer, como primera capa). Genera el hash:

```powershell
docker run --rm caddy:2.8 caddy hash-password --plaintext "TU_CLAVE"
```

Copia el resultado en `.env`, **entre comillas simples** (porque contiene `$`):

```
CADDY_BASIC_USER=luis
CADDY_BASIC_PASSWORD_HASH='$2a$14$...'
```

La clave que escribes en el navegador es `TU_CLAVE`. El hash solo va en `.env`.

### 3.3 Generar la clave de Airflow

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Pégala en `AIRFLOW_FERNET_KEY`.

---

## 4. Levantar y bajar

Todo se controla con `scripts\labs.ps1`:

```powershell
.\scripts\labs.ps1 validate all     # revisa los compose sin levantar nada
.\scripts\labs.ps1 up all           # levanta todos los grupos
.\scripts\labs.ps1 down all         # baja todos los grupos
.\scripts\labs.ps1 status           # muestra los contenedores activos
```

### ¿Uno a uno o todo de una vez?

Ambas formas funcionan:

- **Todo de una vez** (`up all`): útil al encender la PC. El script crea la red `datalab`, levanta los grupos en orden y deja `seguridad` al final.
- **Un grupo a la vez** (`up storage`, `up databricks`, etc.): útil cuando solo necesitas una parte o quieres reiniciar un grupo sin afectar a los demás.

Un solo comando de Docker Compose no basta para todo, porque cada grupo es un proyecto independiente con su propio archivo. El script es el que une los grupos.

Para bajar un solo grupo: `.\scripts\labs.ps1 down databricks`. **Los volúmenes (datos) se conservan**: `down` no usa `-v`.

> **Cuidado con `-v`:** `docker compose down -v` borra los volúmenes del grupo. No lo uses si quieres conservar datos.

---

## 5. Puertos y DNS

### 5.1 Router

Reenvía estos puertos a la IP de la PC:

| Puerto | Uso |
|---|---|
| 80, 443 | Caddy (HTTP y HTTPS) |
| 51430 | SQL Server |
| 51431 | DB2 |
| 51432 | SFTP |
| 51435 | Kafka con Zookeeper |
| 51437 a 51439 | Brokers Kafka KRaft |

Los puertos TCP son los que definen las variables `*_HOST_PORT` de `.env`. Los Postgres no publican puerto: se administran desde pgAdmin.

**Reglas de puertos:**

- **80, 443 y 51430 a 51440** están reservados para el router. Solo se publican los TCP que el router reenvía. Ningún otro servicio los usa, aunque el número esté libre.
- **Dentro de cada stack** los servicios usan sus puertos estándar (5432, 8080, 9092, etc.). Eso no requiere publicarlos en el host.
- **Si un servicio necesita un puerto publicado en el host**, usa uno desde **51500 en adelante**. Los puertos 51441 a 51499 tampoco se usan, para evitar confusiones.

### 5.2 Cloudflare DNS

Crea un registro **A** por cada subdominio, apuntando a tu IP pública, con la **nube gris** (solo DNS).

**Por qué nube gris:** Caddy necesita recibir directamente el tráfico para obtener los certificados de Let's Encrypt (el desafío `tls-alpn-01` falla a través del proxy). Con nube naranja, Cloudflare responde o redirige antes de que la petición llegue a Caddy, y además aplica su límite de 100 MB. Si la raíz tiene nube naranja, verás `ERR_TOO_MANY_REDIRECTS` aunque Caddy esté bien.

| Subdominio | Servicio | Login |
|---|---|---|
| `luispicado.com` (raíz) | Homepage | Ninguno (página de inicio pública) |
| `www` | Redirige a la raíz | Ninguno |
| `sftp` | SFTPGo (web admin) | Propio de SFTPGo |
| `minio` | Consola MinIO | Propio de MinIO |
| `minio-api` | API S3 de MinIO | Llaves de MinIO |
| `data` | Apache Fileserver | Caddy (usuario común) |
| `kraft-ui`, `zoo-ui` | Kafka UI | Caddy |
| `kraft-api`, `zoo-api` | Kafka Connect (REST) | Caddy |
| `jupyter` | Jupyter Lab | Token (`JUPYTER_TOKEN`) |
| `mlflow` | MLflow | Caddy |
| `spark` | Spark UI | Caddy |
| `vault` | Vault | Propio de Vault |
| `airflow` | Airflow | Propio de Airflow |
| `grafana` | Grafana | Propio de Grafana |
| `prometheus` | Prometheus | Caddy |
| `kuma` | Uptime Kuma | Propio de Uptime Kuma |
| `portainer` | Portainer | Caddy y luego Portainer |
| `ntfy` | ntfy | Propio de ntfy |
| `pgadmin` | pgAdmin | Propio de pgAdmin |
| `files` | FileBrowser | Propio de FileBrowser |

Todas las URLs son `https://<subdominio>.luispicado.com`, salvo la raíz, que es `https://luispicado.com`. El registro `www` redirige con 301 a la raíz. Requiere su propio registro A en nube gris, además de la entrada del Caddyfile.

---

## 6. Cómo entrar a cada servicio

### Storage

- **SQL Server**: DBeaver o SSMS, host `<tu-ip>,51430`, usuario `sa`, clave `SQLSERVER_SA_PASSWORD`. El montaje `${DATA_ROOT}/sql-backups` está en `/var/opt/mssql/backups`, para que los `BACKUP` de SQL Server caigan en esa carpeta del host.
- **DB2**: DBeaver, host `<tu-ip>`, puerto `51431`, base `SAMPLE`, usuario `db2inst1`, clave `DB2_INSTANCE_PASSWORD`. El primer arranque tarda varios minutos.
- **SFTP**: cliente SFTP (WinSCP, FileZilla) en `<tu-ip>:51432`. La administración web está en `https://sftp.luispicado.com`. La primera vez te pedirá crear el administrador.
- **MinIO**: consola en `https://minio.luispicado.com` con `MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD`. La API S3 está en `https://minio-api.luispicado.com`. Crea los buckets que usan los notebooks y Hive (ver Databricks).
- **Apache Fileserver**: `https://data.luispicado.com`. Pide el usuario y clave de Caddy. Sirve la carpeta `${DATA_ROOT}/apache-fileserver`.

### Kafka

- **Kafka UI**: `https://kraft-ui.luispicado.com` y `https://zoo-ui.luispicado.com` (clave de Caddy).
- **Kafka Connect**: `https://kraft-api.luispicado.com` y `https://zoo-api.luispicado.com` (clave de Caddy). Ya hay conectores Debezium con sus topics de configuración, offsets y estado.
- **Desde Jupyter** (que está en `datalab`): usa `kafka1:9092` para KRaft o `kafka:29092` para Zookeeper.

> **Limitación conocida:** los brokers anuncian sus nombres internos (`kafka1`, `kafka`). Un cliente que esté fuera de Docker, como DBeaver o un consumidor en tu PC, no podrá conectarse a los brokers hasta que ajustemos `KAFKA_ADVERTISED_LISTENERS` para usar la IP o el dominio público.

### Databricks

- **Jupyter**: `https://jupyter.luispicado.com` con el token `JUPYTER_TOKEN`. Los notebooks leen y escriben en MinIO en `s3a://bronce/`, así que el bucket `bronce` debe existir.
- **Spark UI**: `https://spark.luispicado.com` (clave de Caddy). La página principal muestra los workers vivos: debe aparecer uno (`spark-worker`).
- **MLflow**: `https://mlflow.luispicado.com` (clave de Caddy). Desde Jupyter, apunta el cliente a `http://mlflow:5000`. Las corridas, parámetros y métricas se guardan en `stacks/databricks/mlruns`.
- **SQL en Jupyter**: en un notebook, carga la extensión con `%load_ext sparksql_magic` y luego usa `%%sql` al inicio de una celda para consultar las tablas de Spark. Reemplaza al editor SQL de Databricks; no hay un servicio aparte.
- **Vault**: `https://vault.luispicado.com`. Vault ya está inicializado. **Cada vez que se reinicia, queda sellado** y hay que desbloquearlo con 3 de sus 5 claves:
  ```powershell
  docker exec -it vault vault operator unseal   # repetir tres veces, con una clave distinta cada vez
  ```
  La inicialización inicial se hace una sola vez con `docker exec -it vault vault operator init`. Guarda las claves fuera del repositorio.

### Hive Metastore (catálogo de tablas)

Hive Metastore guarda los metadatos de cada tabla: su nombre, sus columnas y la ruta donde están los datos. Los datos Delta quedan en MinIO, en `s3a://warehouse/`. Sus metadatos están en el Postgres `hive-postgres`, que no publica puerto: solo se administra desde pgAdmin.

Configuración, una sola vez:

1. **Crea el bucket `warehouse`** en la consola de MinIO (`https://minio.luispicado.com`). Hive no lo crea.
2. **El esquema se inicializa solo.** Al arrancar, el contenedor ejecuta `schematool -initOrUpgradeSchema` contra `hive-postgres`. No hace falta ejecutar nada a mano.
3. **Revisa que el servicio arrancó** y escucha en el puerto 9083:
   ```powershell
   docker logs hive-metastore
   ```

Uso desde Jupyter: crea la sesión de Spark con soporte de Hive y conserva la configuración de `s3a` que ya usan los notebooks:

```python
spark = (SparkSession.builder
    .config("hive.metastore.uris", "thrift://hive-metastore:9083")
    .config("spark.sql.warehouse.dir", "s3a://warehouse/")
    .enableHiveSupport()
    .getOrCreate())
```

Después, las tablas se guardan y se registran en el mismo paso:

```python
df.write.format("delta").mode("overwrite").saveAsTable("default.sales_order_header")
```

Y se consultan con `%%sql SHOW TABLES` o desde DBeaver conectado al Postgres de metadatos, a través de pgAdmin.

> **Pendiente de probar:** el servicio arranca y acepta conexiones en 9083, pero todavía no se ha probado una escritura completa de tabla Delta en MinIO seguida de su aparición en `SHOW TABLES`.

### Orquestación

- **Notebooks con papermill**: el DAG `notebook_papermill` ejecuta `TestMinio.ipynb` con papermill y guarda la copia en `stacks/orquestacion/notebooks_out`. La imagen de Airflow trae Java, PySpark y papermill, así que la primera vez hay que construirla:
  ```powershell
  docker compose -f stacks/orquestacion/compose.yaml build
  ```
- **Airflow**: `https://airflow.luispicado.com`. La base de metadatos es nueva (no conserva el historial anterior). Crea el usuario administrador la primera vez:
  ```powershell
  docker exec -it airflow-webserver airflow users create --username admin --firstname Admin --lastname Lab --role Admin --email admin@example.com --password "TU_CLAVE"
  ```
  `airflow-init` aparece como `Exited (0)`: es normal. Solo migra la base de datos al arrancar y termina.

### Observabilidad

- **Grafana**: `https://grafana.luispicado.com` con `GRAFANA_ADMIN_USER` y `GRAFANA_ADMIN_PASSWORD`. La primera vez agrega la fuente de datos: **Connections → Data sources → Add → Prometheus**, con URL `http://prometheus:9090`, y guarda con *Save & test*.
- **Dashboard de Windows**: en Grafana, importa el dashboard con ID 14694 (*Dashboards → New → Import*) y elige la fuente Prometheus. Las consultas de ese dashboard usan nombres de métricas de versiones viejas del exporter; los paneles de CPU, memoria, disco, uptime, procesadores, RAM, swap, threads, procesos y NTP ya están corregidos en la versión que usa el laboratorio. Si algún panel no muestra datos, revisa su consulta contra `windows_exporter` (`curl.exe -s http://localhost:9182/metrics`).
- **Prometheus**: `https://prometheus.luispicado.com` (clave de Caddy). Recoge tres targets: `prometheus`, `cadvisor` y `windows-host` (`host.docker.internal:9182`, el servicio de Windows). Consulta su estado en **Status → Targets**.
- **cAdvisor**: no tiene interfaz ni puerto publicado; Prometheus lo consulta por la red interna.
- **Node Exporter ya no existe en el proyecto**: no podía medir el host Windows desde Docker Desktop (no puede montar `/` del host con propagación `rslave`), y lo que medía era la VM de Linux. Las métricas del host ahora vienen de `windows_exporter`. Ver [ADR 0007](adr/0007-metricas-del-host-con-windows-exporter.md).

### Monitoreo

- **Uptime Kuma**: `https://kuma.luispicado.com`. Crea la cuenta en el primer acceso.
- **ntfy**: `https://ntfy.luispicado.com`. No permite acceso anónimo. Crea tu usuario con:
  ```powershell
  docker exec -it ntfy ntfy user add --role=admin TU_USUARIO
  ```
  Para que Uptime Kuma envíe alertas, agrega ntfy como notificación con la URL interna `http://ntfy:80`, un tópico y un token creado para ese usuario. En el celular, instala la app de ntfy y suscríbete al mismo servidor.
- **Portainer**: `https://portainer.luispicado.com`. Tiene dos capas de login:
  1. Primero, el usuario y clave de Caddy (`CADDY_BASIC_USER` y la clave de `CADDY_BASIC_PASSWORD_HASH`).
  2. Después, la pantalla de Portainer. Pide un **setup token** que Portainer imprime en sus logs al arrancar:
     ```powershell
     docker logs portainer 2>&1 | Select-String setup_token | Select-Object -Last 1
     ```
     Usa el último que aparezca. Luego crea la cuenta de administrador. Si pasan 5 minutos sin crearla, Portainer se bloquea por seguridad: reinicia con `docker restart portainer` para volver a tener la ventana.
  3. Al elegir el entorno, usa el Docker local. **No habilites Edge Compute**: solo sirve para administrar dispositivos remotos con el Edge Agent.

  La cuenta de administrador se guarda en el volumen `portainer_data`. Reiniciar el contenedor no la borra, así que solo la creas la primera vez. Se pierde si se borra ese volumen.

> **Riesgo:** Portainer tiene acceso al socket de Docker, y quien entre a Portainer controla la PC. Por eso va detrás de Caddy y necesita una clave fuerte también para la cuenta de Portainer.

### Herramientas

- **pgAdmin**: `https://pgadmin.luispicado.com` con `PGADMIN_DEFAULT_EMAIL` (un correo válido) y `PGADMIN_DEFAULT_PASSWORD`. Para conectar un Postgres, en pgAdmin usa como host el nombre del contenedor y el puerto `5432`:

  | Postgres | Host | Puerto | Usuario | Base | Clave |
  |---|---|---|---|---|---|
  | KRaft | `postgres_kraft` | 5432 | `postgres` | `demo` | `KRAFT_POSTGRES_PASSWORD` |
  | Zookeeper | `postgres_zoo` | 5432 | `postgres` | `demo` | `ZOO_POSTGRES_PASSWORD` |
  | Airflow | `airflow-postgres` | 5432 | `airflow` | `airflow` | `AIRFLOW_POSTGRES_PASSWORD` |
  | Hive Metastore | `hive-postgres` | 5432 | `hive` | `metastore` | `HIVE_POSTGRES_PASSWORD` |

  Estos Postgres solo se alcanzan desde `datalab`, por eso pgAdmin tiene que estar en esa red.
- **FileBrowser**: `https://files.luispicado.com` con `FILEBROWSER_ADMIN_USER` y `FILEBROWSER_ADMIN_PASSWORD`. Permite subir, bajar, renombrar y borrar archivos desde el navegador. Trabaja sobre la misma carpeta que `data.luispicado.com` (`${DATA_ROOT}/apache-fileserver`), así que un archivo subido aquí aparece allá. Desde FileBrowser también se pueden crear enlaces para compartir: no los crees para archivos que no deban ser públicos.
- **Homepage**: `https://luispicado.com`. Es la página de inicio y enlaza a los demás servicios. Su configuración vive en `stacks/herramientas/homepage/config`. Esa carpeta se monta con escritura: homepage necesita escribir sus logs ahí.

---

## 7. Agregar un servicio nuevo

1. **Agrégalo al stack de su grupo** (`stacks/<grupo>/compose.yaml`).
2. **Si tiene interfaz web**, conéctalo a `datalab`:
   ```yaml
   networks:
     - default
     - datalab
   ```
   Si además otros servicios lo llaman **por su nombre** (como `spark:7077`), ponlo solo en `datalab` para que el nombre resuelva a una sola IP. Ver [ADR 0002](adr/0002-un-stack-por-grupo-y-red-datalab.md).
3. **Agrega su subdominio en `stacks/seguridad/Caddyfile`**:
   ```
   nuevo.{$DOMAIN} {
     import logs
     import proteger                 # solo si el servicio NO tiene login propio
     reverse_proxy nombre-contenedor:puerto
   }
   ```
4. **Crea el registro A** en Cloudflare, nube gris.
5. **Reinicia Caddy.** Con `admin off` no se puede recargar en caliente:
   ```powershell
   docker restart caddy
   ```
   Antes de reiniciar, valida el Caddyfile: `docker exec caddy caddy validate --config /etc/caddy/Caddyfile`. Hazlo después de crear el registro DNS: si Caddy intenta el certificado antes, cada intento fallido cuenta contra el límite de Let's Encrypt.
6. **Valida antes de levantar:** `.\scripts\labs.ps1 validate <grupo>`.

---

## 8. Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `Falta X en .env` | Variable obligatoria vacía | Completa `.env` |
| `docker compose falló` | Error de sintaxis o de imagen | Ejecuta `validate <grupo>` y revisa el mensaje |
| `Conflict. The container name ... is already in use` | Quedó un contenedor de una versión anterior del stack | Quítalo con `docker rm -f <nombre>` (no borra volúmenes) y vuelve a levantar |
| `WARN Found orphan containers` | Un servicio cambió de nombre en el compose y su contenedor viejo sigue en el proyecto | Quita el contenedor huérfano con `docker rm -f <nombre>` |
| Caddy devuelve 502 | El contenedor destino no está levantado o no está en `datalab` | Revisa `status` y la red |
| `ERR_TOO_MANY_REDIRECTS` en la raíz | El registro de la raíz tiene nube naranja y Cloudflare redirige en bucle | Cambia el registro a nube gris |
| `DNS_PROBE_FINISHED_NXDOMAIN` en `www` | No existe el registro `www` | Crea el registro A `www` en nube gris |
| Certificado no válido | El registro DNS aún no apunta a tu IP o el puerto 80 no está abierto | Verifica DNS y el reenvío del router |
| Caddy tarda en obtener certificados | Let's Encrypt limita las cuentas nuevas por IP (10 cada 3 horas) y los dominios sin DNS fallan | Espera la hora indicada en el log, o crea los registros DNS antes de levantar |
| Cambios en `Caddyfile` no aplican | Caddy no recarga en caliente (`admin off`) | `docker restart caddy` |
| Caddy no inicia con `subject does not qualify for certificate: 'prometheus.'` | `DOMAIN` está vacío en el entorno de Caddy | Revisa que `DOMAIN` esté en `.env` y que el compose la pase al contenedor |
| Caddy no inicia con `not a directory` al montar `Caddyfile` | El archivo no existe en la ruta del compose y Docker creó una carpeta en su lugar | Restaura el archivo desde la carpeta correcta y borra la carpeta vacía |
| Airflow no abre | Falta crear el usuario o `airflow-init` no terminó | `docker logs airflow-init` (debe terminar con `Exited (0)`) |
| Vault responde pero está sellado | Se reinició y necesita desbloqueo | `docker exec -it vault vault operator unseal` tres veces |
| Portainer dice `timed out` al crear la cuenta | Pasaron 5 minutos sin crearla | `docker restart portainer` y crear la cuenta de inmediato |
| Spark worker sin registrarse (`aliveworkers: 0`) | El worker resuelve `spark` a una IP de otra red donde el master no escucha | Deja el worker solo en `datalab`, como está ahora |
| Jupyter no llega a `spark:7077` | Mismo caso que el worker | Deja Jupyter solo en `datalab` |
| homepage responde 500 | Su carpeta de configuración está montada de solo lectura y no puede crear `logs` | Monta `./homepage/config` sin `:ro` |
| Prometheus no muestra `windows-host` | El servicio `windows_exporter` no corre, o el firewall bloquea el 9182 | `Get-Service windows_exporter`, y la regla de firewall de la sección 2 |
| Panel de Grafana sin datos | Su consulta usa un nombre de métrica que la versión actual del exporter no expone, o la variable `server` está vacía | Revisa la consulta y que `server` tenga valor |
| pgAdmin no conecta a un Postgres | El Postgres no está en `datalab` o el host está mal escrito | Usa el nombre del contenedor (`postgres_kraft`, `postgres_zoo`, `airflow-postgres`, `hive-postgres`) y el puerto `5432` |
| pgAdmin se reinicia en bucle con `does not appear to be a valid email address` | `PGADMIN_DEFAULT_EMAIL` no tiene formato de correo | Pon un correo válido en `.env` y recrea el contenedor |
| Hive Metastore no arranca | La base de metadatos no está lista o falta un JAR | `docker logs hive-metastore`. Los JARs deben ser legibles por el usuario `hive` |
| FileBrowser da error al entrar con las credenciales de `.env` (403 en `/api/login`) | `FB_USERNAME` y `FB_PASSWORD` solo se usan la primera vez que se crea la base de datos. Si cambiaste `.env` después, la clave guardada es la vieja | Actualiza la clave del admin en la base: detén el contenedor, ejecuta `filebrowser users update <usuario> --password <clave> -d /database/filebrowser.db` en un contenedor temporal con el volumen `herramientas_filebrowser_db`, y vuelve a iniciar. No basta con reiniciar |
| `saveAsTable` no registra la tabla | La sesión de Spark no tiene `enableHiveSupport()` o no apunta a `thrift://hive-metastore:9083` | Crea la sesión como se indica en la sección Hive Metastore |

Para ver los logs de cualquier servicio: `docker logs -f <nombre-contenedor>`.

---

## 9. Lista de seguridad

- [ ] `.env` y `credenciales.md` no se suben a git.
- [ ] Caddy tiene una clave fuerte para los servicios sin login.
- [ ] Cambiaste las contraseñas que estaban en el historial de git (queda pendiente por decisión tuya).
- [ ] Portainer tiene clave fuerte en Caddy y en su propio login, o no está publicado.
- [ ] Revisas los logs de CrowdSec: `docker exec crowdsec cscli alerts list`.
- [ ] Solo están abiertos en el router los puertos 80, 443 y los TCP reservados que usas (51430 a 51440). Los Postgres no publican puerto.
- [ ] Kafka usa PLAINTEXT y está expuesto por TCP: sin TLS ni autenticación. Revisar antes de dar acceso a terceros.
- [ ] La regla de firewall de `windows_exporter` (puerto 9182) está abierta en todos los perfiles de red. Si no necesitas que otros equipos lo lean, limítala a Docker o elimínala.

---

## 10. Archivos antiguos

- `old/`: todo lo del proyecto anterior. Incluye los compose duplicados, la carpeta `kafka/` completa (con los consumidores de Python y los scripts de SQL) y la documentación previa. Está ignorada por git. Si necesitas algo de ahí, cópialo de vuelta.
- `old/web-bak-2/`: la carpeta `web/` de la versión anterior (Caddy y su compose). La reemplaza `stacks/seguridad/`, que es la configuración vigente.

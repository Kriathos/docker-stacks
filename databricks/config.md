# Configuración del stack Databricks

Este archivo describe los ajustes específicos del stack `databricks` y las dependencias de configuración.

## Red Docker

El stack usa una red externa llamada `mynet`:

```powershell
docker network create mynet --driver bridge
```

## Vault

Archivo de configuración: `vault/config/config.hcl`

- `storage "file"` almacena datos en `/vault/data`
- `listener "tcp"` escucha en `0.0.0.0:8200`
- `tls_disable = 1` deshabilita TLS para pruebas
- `ui = true` habilita la interfaz de Vault

### Acceso a Vault

Actualmente `vault` no expone puerto externo en `docker-compose.yml`. Para conectarlo desde el host, agrega:

```yaml
ports:
  - "8200:8200"
```

## Jupyter

La configuración de Jupyter Lab se define en el comando de arranque de `docker-compose.yml`.

- Token: `(definido en docker-compose.yml)`
- Directorio raíz: `/home/jovyan/work`
- Paquetes instalados: `jupyter`, `jupyterlab`, `pyspark==3.5.0`, `delta-spark==3.0.0`, `hvac`

## Airflow

Variables importantes:

- `AIRFLOW__CORE__EXECUTOR = LocalExecutor`
- `AIRFLOW__CORE__FERNET_KEY` está fijado en el compose
- `AIRFLOW__CORE__DAGS_FOLDER = /opt/airflow/dags`
- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN = postgresql+psycopg2://airflow:<CHANGE_ME>@postgres/airflow`

## MLflow

- Backend store: `sqlite:///mlflow.db`
- Artifact root: `/mlruns`
- Volumen local: `./mlruns:/mlruns`

## Puertos internos y exposición

El stack usa varios puertos dentro del contenedor:

- Spark Master UI: `8080`
- Spark RPC: `7077`
- Jupyter: `8888`
- MLflow: `5000`
- Airflow Webserver: `8080` en el contenedor, mapeado a `8081` en el host
- Vault: `8200`

Si necesitas abrir otros puertos, agrega la sección `ports:` al servicio correspondiente.

## Volúmenes persistentes

- `spark_data`
- `spark_parquet`
- `postgres_data`

Los directorios locales montados son:

- `./notebooks`
- `./jars`
- `./mlruns`
- `./vault/data`
- `./vault/config`

## Consejos

- Si agregas dependencias a Jupyter, es preferible construir una imagen personalizada para evitar instalaciones en cada inicio.
- Mantén `mynet` y el proxy Nginx en `web` si quieres acceder a los servicios por nombre de dominio.

# Imagen de Airflow para el laboratorio.
# Agrega Java y PySpark para que los notebooks de databricks puedan ejecutarse,
# y papermill para correrlos desde un DAG con parámetros.
FROM apache/airflow:2.9.0-python3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
# Ruta válida en amd64. En arm64 la ruta es java-17-openjdk-arm64.
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow
# Mismas versiones que usa el servicio jupyter de databricks
RUN pip install --no-cache-dir pyspark==3.5.0 delta-spark==3.0.0 papermill ipykernel

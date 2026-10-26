from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Ejecuta un notebook de databricks con papermill. Cada corrida guarda una copia
# ejecutada en notebooks_out, con la fecha y hora en el nombre.
with DAG(
    "notebook_papermill",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    run_test_minio = BashOperator(
        task_id="run_test_minio",
        bash_command=(
            "papermill /opt/airflow/notebooks/TestMinio.ipynb "
            "/opt/airflow/notebooks_out/TestMinio_{{ ts_nodash }}.ipynb"
        ),
    )

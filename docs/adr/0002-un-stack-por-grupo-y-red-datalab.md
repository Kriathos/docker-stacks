# 0002: Un stack de Compose por grupo, con la red externa datalab para cruzar grupos

Cada grupo de servicios relacionados vive en su propio `compose.yaml` y tiene su red interna. Los servicios que deben comunicarse entre grupos, o que Caddy debe alcanzar, se conectan además a la red externa `datalab`. Se eligió así para poder levantar o bajar un grupo sin tocar los demás, y para que el aislamiento sea el predeterminado.

## Regla de nombres

Un servicio que otros llaman **por su nombre de servicio** (por ejemplo, `spark:7077` desde el worker, o `postgres_kraft` desde pgAdmin) debe estar en **una sola** red compartida con ese destino. Si el nombre aparece en dos redes distintas, Docker puede resolverlo a una IP donde el destino no escucha.

Casos reales que lo motivaron:

- El worker de Spark y Jupyter estaban en `databricks_default` además de `datalab`. `spark` resolvía a una IP de `databricks_default` donde el master no escuchaba (`Connection refused`). Quedaron solo en `datalab`.
- Un Postgres con alias `postgres` colisionaba con `postgres_zoo` y `postgres_kraft` en `datalab`. Airflow falló con autenticación. Se renombró a `airflow-postgres`.

Por eso, los servicios que se llaman por nombre sin ser un servicio web publicado se conectan solo a `datalab`, y cada nombre debe ser único en esa red.


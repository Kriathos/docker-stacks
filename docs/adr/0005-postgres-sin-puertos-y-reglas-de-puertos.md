# 0005: Postgres sin puertos publicados, administrados con pgAdmin, y reglas de puertos del host

Los Postgres de KRaft, Zookeeper, Airflow y Hive Metastore no publican su puerto en el router. Los de KRaft, Zookeeper y Airflow dejan de publicarlo; el de Hive nunca lo publicó. Se administran desde pgAdmin, que corre en la red `datalab` y los alcanza por el nombre del contenedor y el puerto 5432. pgAdmin se publica por Caddy con su propio login. Así se liberan 51433, 51436 y 51440, y los usuarios externos pueden explorar las bases sin que ninguna quede abierta en el router. Se descartó dejarlos públicos porque cada puerto abierto es una puerta más, y se descartó una VPN porque los usuarios no pueden instalar software.

Las reglas de puertos del host quedan así: 80 y 443 para Caddy; 51430 a 51440 solo para los TCP que el router reenvía; y cualquier puerto publicado nuevo desde 51500 en adelante. Los puertos internos de los contenedores no están sujetos a esta regla.

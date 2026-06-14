# Databricks notebook source
# MAGIC %md
# MAGIC # Setup del Laboratorio de Streaming
# MAGIC
# MAGIC Este notebook prepara los datos sinteticos base en Delta para clientes,
# MAGIC conductores y estado operativo del conductor. El diseño esta orientado a
# MAGIC un laboratorio guiado sobre una plataforma de viajes similar a Uber/Didi en
# MAGIC Costa Rica.

# COMMAND ----------

# Bibliotecas
from datetime import datetime
import random
import uuid
from zoneinfo import ZoneInfo

from pyspark.sql import functions as F
from pyspark.sql import types as T

# COMMAND ----------

# Parametros
dbutils.widgets.text("catalog", "raw_data_preprod")
dbutils.widgets.text("schema", "bootcamp")
dbutils.widgets.text("seed", "20260527")
dbutils.widgets.text("passenger_count", "10000")
dbutils.widgets.text("driver_count", "1500")
dbutils.widgets.text("simulation_timezone", "America/Costa_Rica")

CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA = dbutils.widgets.get("schema").strip()
SEED = int(dbutils.widgets.get("seed"))
PASSENGER_COUNT = int(dbutils.widgets.get("passenger_count"))
DRIVER_COUNT = int(dbutils.widgets.get("driver_count"))
SIMULATION_TIMEZONE = dbutils.widgets.get("simulation_timezone").strip() or "America/Costa_Rica"

# Semilla fija para que el escenario sea reproducible
random.seed(SEED)

TABLE_GEO = f"{CATALOG}.{SCHEMA}.lab_geo_cantones"
TABLE_CLIENTES = f"{CATALOG}.{SCHEMA}.lab_clientes"
TABLE_CONDUCTORES = f"{CATALOG}.{SCHEMA}.lab_conductores"
TABLE_ESTADO = f"{CATALOG}.{SCHEMA}.lab_estado_conductores"
TABLE_ESTADO_CLIENTES = f"{CATALOG}.{SCHEMA}.lab_estado_clientes"
TABLE_ESTADO_VIAJES = f"{CATALOG}.{SCHEMA}.lab_estado_viajes"

# COMMAND ----------

# Datasets Provincia y Canton
PROVINCIA_CONFIG = {
    "San Jose": {"latitud": 9.7489, "longitud": -84.1118, "lat_spread": 0.19, "lon_spread": 0.22, "peso": 1.00},
    "Alajuela": {"latitud": 10.3916, "longitud": -84.4383, "lat_spread": 0.28, "lon_spread": 0.31, "peso": 0.82},
    "Cartago": {"latitud": 9.8644, "longitud": -83.9194, "lat_spread": 0.18, "lon_spread": 0.20, "peso": 0.61},
    "Heredia": {"latitud": 10.0024, "longitud": -84.1165, "lat_spread": 0.13, "lon_spread": 0.16, "peso": 0.66},
    "Guanacaste": {"latitud": 10.5247, "longitud": -85.3548, "lat_spread": 0.35, "lon_spread": 0.40, "peso": 0.50},
    "Puntarenas": {"latitud": 9.9763, "longitud": -84.8384, "lat_spread": 0.38, "lon_spread": 0.42, "peso": 0.56},
    "Limon": {"latitud": 9.9907, "longitud": -83.0350, "lat_spread": 0.26, "lon_spread": 0.28, "peso": 0.48},
}

CANTON_REFERENCE = {
    "San Jose": [
        "San Jose", "Escazu", "Desamparados", "Puriscal", "Tarrazu", "Aserri", "Mora", "Goicoechea",
        "Santa Ana", "Alajuelita", "Vazquez de Coronado", "Acosta", "Tibas", "Moravia", "Montes de Oca",
        "Turrubares", "Dota", "Curridabat", "Perez Zeledon", "Leon Cortes Castro",
    ],
    "Alajuela": [
        "Alajuela", "San Ramon", "Grecia", "San Mateo", "Atenas", "Naranjo", "Palmares", "Poas",
        "Orotina", "San Carlos", "Zarcero", "Valverde Vega", "Upala", "Los Chiles", "Guatuso", "Rio Cuarto",
    ],
    "Cartago": [
        "Cartago", "Paraiso", "La Union", "Jimenez", "Turrialba", "Alvarado", "Oreamuno", "El Guarco",
    ],
    "Heredia": [
        "Heredia", "Barva", "Santo Domingo", "Santa Barbara", "San Rafael", "San Isidro", "Belen",
        "Flores", "San Pablo", "Sarapiqui",
    ],
    "Guanacaste": [
        "Liberia", "Nicoya", "Santa Cruz", "Bagaces", "Carrillo", "Canas", "Abangares", "Tilaran",
        "Nandayure", "La Cruz", "Hojancha",
    ],
    "Puntarenas": [
        "Puntarenas", "Esparza", "Buenos Aires", "Montes de Oro", "Osa", "Quepos", "Golfito", "Coto Brus",
        "Parrita", "Corredores", "Garabito", "Monteverde", "Puerto Jimenez",
    ],
    "Limon": [
        "Limon", "Pococi", "Siquirres", "Talamanca", "Matina", "Guacimo",
    ],
}

URBAN_CANTONS = {
    ("San Jose", "San Jose"),
    ("San Jose", "Escazu"),
    ("San Jose", "Desamparados"),
    ("San Jose", "Goicoechea"),
    ("San Jose", "Santa Ana"),
    ("San Jose", "Alajuelita"),
    ("San Jose", "Tibas"),
    ("San Jose", "Moravia"),
    ("San Jose", "Montes de Oca"),
    ("San Jose", "Curridabat"),
    ("Alajuela", "Alajuela"),
    ("Alajuela", "San Ramon"),
    ("Alajuela", "Grecia"),
    ("Alajuela", "Atenas"),
    ("Alajuela", "Palmares"),
    ("Alajuela", "San Carlos"),
    ("Cartago", "Cartago"),
    ("Cartago", "Paraiso"),
    ("Cartago", "La Union"),
    ("Cartago", "Turrialba"),
    ("Heredia", "Heredia"),
    ("Heredia", "Barva"),
    ("Heredia", "Santo Domingo"),
    ("Heredia", "San Rafael"),
    ("Heredia", "Belen"),
    ("Heredia", "Flores"),
    ("Heredia", "San Pablo"),
    ("Guanacaste", "Liberia"),
    ("Guanacaste", "Nicoya"),
    ("Guanacaste", "Santa Cruz"),
    ("Guanacaste", "Carrillo"),
    ("Puntarenas", "Puntarenas"),
    ("Puntarenas", "Quepos"),
    ("Puntarenas", "Garabito"),
    ("Puntarenas", "Golfito"),
    ("Limon", "Limon"),
    ("Limon", "Pococi"),
    ("Limon", "Siquirres"),
}

# Funciones
# Expande un listado base hasta obtener un catalogo sintetico unico del tamano solicitado
def build_catalog(base_values, target_size, label):
    catalog = []
    seen = set()

    for value in base_values:
        normalized_value = value.strip()
        if normalized_value and normalized_value not in seen:
            catalog.append(normalized_value)
            seen.add(normalized_value)
        if len(catalog) == target_size:
            return catalog

    for first_value in base_values:
        for second_value in base_values:
            if first_value == second_value:
                continue
            compound_value = f"{first_value.strip()} {second_value.strip()}"
            if compound_value not in seen:
                catalog.append(compound_value)
                seen.add(compound_value)
            if len(catalog) == target_size:
                return catalog

    raise ValueError(f"No fue posible generar {target_size} valores unicos para {label}")

# Datasets Nombres y Apellidos
FEMALE_BASE_NAMES = [
    "Sofia", "Valeria", "Camila", "Daniela", "Gabriela", "Mariana", "Paula", "Lucia", "Andrea", "Isabel",
    "Fernanda", "Catalina", "Natalia", "Carolina", "Melissa", "Alejandra", "Adriana", "Ana", "Beatriz", "Claudia",
    "Diana", "Elena", "Fabiana", "Gloria", "Helena", "Ines", "Jimena", "Karen", "Laura", "Lourdes",
    "Marcela", "Maria", "Monica", "Noelia", "Patricia", "Raquel", "Rebeca", "Rocio", "Sara", "Tatiana",
    "Veronica", "Yessenia", "Zuleika", "Fiorella", "Allison", "Dayana", "Priscila", "Mireya", "Ariana", "Karla",
    "Mia", "Yamileth", "Nicole", "Stephanie", "Johanna", "Lorena", "Estefania", "Viviana", "Aura", "Cinthya",
    "Maribel", "Giselle", "Roxana", "Nadia", "Lisbeth", "Mayela", "Margarita", "Jessica", "Silvia", "Aylin",
]
MALE_BASE_NAMES = [
    "Luis", "Jose", "Carlos", "Andres", "Daniel", "Javier", "Fernando", "Diego", "Sebastian", "Gabriel",
    "Manuel", "Ricardo", "Adrian", "Pablo", "Mateo", "Alejandro", "Alonso", "Brayan", "Cristian", "David",
    "Edgar", "Esteban", "Felipe", "Gerardo", "Hector", "Ivan", "Joaquin", "Kevin", "Leonardo", "Marco",
    "Mauricio", "Nicolas", "Oscar", "Rafael", "Rodrigo", "Sergio", "Tomas", "Ulises", "Victor", "Wilberth",
    "Yendrick", "Isaac", "Axel", "Aaron", "Julian", "Bryan", "Elias", "Fabio", "Gilberto", "Harold",
    "Jonathan", "Kenneth", "Marvin", "Noel", "Randall", "Steven", "Allan", "Byron", "Cesar", "Cristopher",
    "Dylan", "Emilio", "Freddy", "Henry", "Jason", "Moises", "Ruben", "Wesley", "Xavier", "Yorleny",
]
LAST_NAME_BASES = [
    "Rodriguez", "Garcia", "Lopez", "Mora", "Jimenez", "Vargas", "Castro", "Solis", "Rojas", "Navarro",
    "Hernandez", "Araya", "Alvarado", "Ramirez", "Chaves", "Quesada", "Brenes", "Cordero", "Salazar", "Campos",
    "Villalobos", "Segura", "Cruz", "Mendez", "Blanco", "Pineda", "Montero", "Calderon", "Murillo", "Aguilar",
    "Valverde", "Cespedes", "Benavides", "Bonilla", "Arias", "Leiva", "Badilla", "Madrigal", "Porras", "Bermudez",
    "Soto", "Zamora", "Carranza", "Gamboa", "Molina", "Vega", "Mata", "Cascante", "Barquero", "Elizondo",
    "Corrales", "Ulate", "Fonseca", "Cabrera", "Fernandez", "Gomez", "Perez", "Sanchez", "Diaz", "Ruiz",
    "Alvarez", "Torres", "Flores", "Rivera", "Ortiz", "Morales", "Gutierrez", "Silva", "Romero", "Medina",
    "Herrera", "Guerrero", "Rivas", "Nunez", "Mendoza", "Castillo", "Duarte", "Valenzuela", "Figueroa", "Acosta",
    "Becerra", "Bravo", "Cano", "Contreras", "Delgado", "Dominguez", "Escobar", "Espinoza", "Franco", "Fuentes",
    "Gallardo", "Ibarra", "Lara", "Lozano", "Marquez", "Orozco", "Palacios", "Paredes", "Pena", "Quintero",
    "Reyes", "Santana", "Toledo", "Valencia", "Velasco", "Varela", "Zavala", "Cedeno", "Cisneros", "Coronado",
    "Cuadra", "Duran", "Enriquez", "Fajardo", "Gallegos", "Godoy", "Granados", "Guevara", "Hurtado", "Jaramillo",
    "Ledesma", "Lemus", "Linares", "Lucero", "Macias", "Maldonado", "Mena", "Mercado", "Miranda", "Montoya",
]

FEMALE_NAMES = build_catalog(FEMALE_BASE_NAMES, 150, "FEMALE_NAMES")
MALE_NAMES = build_catalog(MALE_BASE_NAMES, 150, "MALE_NAMES")
LAST_NAMES = build_catalog(LAST_NAME_BASES, 300, "LAST_NAMES")

# Genera un valor pseudoaleatorio deterministico entre 0 y 1 a partir de una llave
def deterministic_ratio(key):
    max_uuid_value = float((1 << 128) - 1)
    return uuid.uuid5(uuid.NAMESPACE_DNS, key).int / max_uuid_value

# Transforma el valor deterministico a un rango centrado entre -1 y 1
def centered_ratio(key):
    return (deterministic_ratio(key) * 2.0) - 1.0

# Construye la referencia geografica sintetica de todos los cantones del laboratorio
def build_geo_reference():
    geo_rows = []
    for provincia, cantones in CANTON_REFERENCE.items():
        province_cfg = PROVINCIA_CONFIG[provincia]
        total_cantones = len(cantones)

        for position, canton in enumerate(cantones, start=1):
            lat_offset = centered_ratio(f"{provincia}:{canton}:lat") * province_cfg["lat_spread"]
            lon_offset = centered_ratio(f"{provincia}:{canton}:lon") * province_cfg["lon_spread"]
            canton_weight_factor = 0.65 + ((total_cantones - position + 1) / total_cantones) * 0.35
            synthetic_density = 0.75 + (deterministic_ratio(f"{provincia}:{canton}:peso") * 0.5)
            urban_bonus = 1.20 if (provincia, canton) in URBAN_CANTONS else 0.86

            geo_rows.append(
                {
                    "provincia": provincia,
                    "canton": canton,
                    "latitud": round(province_cfg["latitud"] + lat_offset, 6),
                    "longitud": round(province_cfg["longitud"] + lon_offset, 6),
                    "peso": round(province_cfg["peso"] * canton_weight_factor * synthetic_density * urban_bonus, 4),
                    "zona": "urbana" if (provincia, canton) in URBAN_CANTONS else "rural",
                }
            )

    return geo_rows

GEO_REFERENCE = build_geo_reference()

# COMMAND ----------

# Selecciona una geografia aleatoria ponderada por densidad sintetica
def weighted_geo_choice():
    weights = [item["peso"] for item in GEO_REFERENCE]
    return random.choices(GEO_REFERENCE, weights=weights, k=1)[0]

# Crea una pequena variacion de coordenadas para evitar puntos identicos
def random_offset(max_delta=0.0125):
    return round(random.uniform(-max_delta, max_delta), 6)

# Arma un nombre completo sintetico segun el genero elegido
def build_name(gender):
    first_name_pool = FEMALE_NAMES if gender == "F" else MALE_NAMES
    return f"{random.choice(first_name_pool)} {random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"

# Define la edad valida segun si la persona es conductor o pasajero
def build_age(person_type):
    if person_type == "driver":
        return random.randint(23, 65)
    return random.randint(18, 74)

# Obtiene la marca de tiempo local usada como fecha base del setup
def current_simulation_timestamp():
    return datetime.now(ZoneInfo(SIMULATION_TIMEZONE)).replace(tzinfo=None, microsecond=0)

# Genera el catalogo completo de conductores o pasajeros cubriendo todos los cantones
def build_person_records(total_rows, prefix, person_type):
    if total_rows < len(GEO_REFERENCE):
        raise ValueError(
            f"El total de registros para {prefix} debe ser al menos {len(GEO_REFERENCE)} para cubrir todos los cantones"
        )

    records = []
    created_at = current_simulation_timestamp()
    mandatory_geo_rows = GEO_REFERENCE.copy()
    random.shuffle(mandatory_geo_rows)

    for index in range(total_rows):
        geo = mandatory_geo_rows[index] if index < len(mandatory_geo_rows) else weighted_geo_choice()
        gender = random.choices(["F", "M"], weights=[0.46, 0.54], k=1)[0]
        age = build_age(person_type)

        records.append(
            {
                f"id_{prefix}": f"{prefix}_{index + 1:06d}",
                "nombre_completo": build_name(gender),
                "genero": gender,
                "edad": age,
                "provincia": geo["provincia"],
                "canton": geo["canton"],
                "zona": geo["zona"],
                "latitud_base": round(geo["latitud"] + random_offset(), 6),
                "longitud_base": round(geo["longitud"] + random_offset(), 6),
                "activo": True,
                "created_at": created_at,
            }
        )

    return records

# Schemas de Tablas
clientes_schema = T.StructType(
    [
        T.StructField("id_pasajero", T.StringType(), False),
        T.StructField("nombre_completo", T.StringType(), False),
        T.StructField("genero", T.StringType(), False),
        T.StructField("edad", T.IntegerType(), False),
        T.StructField("provincia", T.StringType(), False),
        T.StructField("canton", T.StringType(), False),
        T.StructField("zona", T.StringType(), False),
        T.StructField("latitud_base", T.DoubleType(), False),
        T.StructField("longitud_base", T.DoubleType(), False),
        T.StructField("activo", T.BooleanType(), False),
        T.StructField("created_at", T.TimestampType(), False),
    ]
)


conductores_schema = T.StructType(
    [
        T.StructField("id_conductor", T.StringType(), False),
        T.StructField("nombre_completo", T.StringType(), False),
        T.StructField("genero", T.StringType(), False),
        T.StructField("edad", T.IntegerType(), False),
        T.StructField("provincia", T.StringType(), False),
        T.StructField("canton", T.StringType(), False),
        T.StructField("zona", T.StringType(), False),
        T.StructField("latitud_base", T.DoubleType(), False),
        T.StructField("longitud_base", T.DoubleType(), False),
        T.StructField("activo", T.BooleanType(), False),
        T.StructField("created_at", T.TimestampType(), False),
    ]
)


geo_schema = T.StructType(
    [
        T.StructField("provincia", T.StringType(), False),
        T.StructField("canton", T.StringType(), False),
        T.StructField("latitud", T.DoubleType(), False),
        T.StructField("longitud", T.DoubleType(), False),
        T.StructField("peso", T.DoubleType(), False),
        T.StructField("zona", T.StringType(), False),
    ]
)

estado_clientes_schema = T.StructType(
    [
        T.StructField("id_pasajero", T.StringType(), False),
        T.StructField("provincia_actual", T.StringType(), False),
        T.StructField("canton_actual", T.StringType(), False),
        T.StructField("zona_actual", T.StringType(), False),
        T.StructField("ultima_latitud", T.DoubleType(), False),
        T.StructField("ultima_longitud", T.DoubleType(), False),
        T.StructField("estado_pasajero", T.StringType(), False),
        T.StructField("id_viaje_activo", T.StringType(), True),
        T.StructField("id_conductor_activo", T.StringType(), True),
        T.StructField("etapa_viaje", T.StringType(), True),
        T.StructField("pickup_latitud", T.DoubleType(), True),
        T.StructField("pickup_longitud", T.DoubleType(), True),
        T.StructField("dropoff_latitud", T.DoubleType(), True),
        T.StructField("dropoff_longitud", T.DoubleType(), True),
        T.StructField("request_ts", T.TimestampType(), True),
        T.StructField("accepted_ts_plan", T.TimestampType(), True),
        T.StructField("pickup_ts_plan", T.TimestampType(), True),
        T.StructField("dropoff_ts_plan", T.TimestampType(), True),
        T.StructField("cancel_ts_plan", T.TimestampType(), True),
        T.StructField("updated_at", T.TimestampType(), False),
    ]
)


viajes_schema = T.StructType(
    [
        T.StructField("id_viaje", T.StringType(), False),
        T.StructField("id_conductor", T.StringType(), False),
        T.StructField("id_pasajero", T.StringType(), False),
        T.StructField("provincia", T.StringType(), False),
        T.StructField("canton", T.StringType(), False),
        T.StructField("zona", T.StringType(), False),
        T.StructField("pickup_latitud", T.DoubleType(), False),
        T.StructField("pickup_longitud", T.DoubleType(), False),
        T.StructField("dropoff_latitud", T.DoubleType(), True),
        T.StructField("dropoff_longitud", T.DoubleType(), True),
        T.StructField("distancia_km", T.DoubleType(), False),
        T.StructField("tarifa_km", T.DoubleType(), False),
        T.StructField("monto_estimado", T.DoubleType(), False),
        T.StructField("tiempo_llegada_seg", T.IntegerType(), True),
        T.StructField("duracion_viaje_seg", T.IntegerType(), True),
        T.StructField("request_ts", T.TimestampType(), True),
        T.StructField("accepted_ts_plan", T.TimestampType(), True),
        T.StructField("pickup_ts_plan", T.TimestampType(), True),
        T.StructField("dropoff_ts_plan", T.TimestampType(), True),
        T.StructField("cancel_ts_plan", T.TimestampType(), True),
        T.StructField("etapa_viaje", T.StringType(), True),
        T.StructField("estado_final", T.StringType(), True),
        T.StructField("hora_pico_plan", T.BooleanType(), True),
        T.StructField("updated_at", T.TimestampType(), False),
    ]
)

# COMMAND ----------

# Main
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE SCHEMA {SCHEMA}")

setup_ts = current_simulation_timestamp()

geo_df = spark.createDataFrame(GEO_REFERENCE, schema=geo_schema)

clientes_records = build_person_records(PASSENGER_COUNT, "pasajero", "passenger")
clientes_df = spark.createDataFrame(clientes_records, schema=clientes_schema)

conductores_records = build_person_records(DRIVER_COUNT, "conductor", "driver")
conductores_df = spark.createDataFrame(conductores_records, schema=conductores_schema)

# Estado inicial de conductores: todos disponibles, sin viaje activo y ubicados en su punto base
estado_df = (
    conductores_df.select(
        "id_conductor",
        F.col("provincia").alias("provincia_actual"),
        F.col("canton").alias("canton_actual"),
        F.col("zona").alias("zona_actual"),
        F.col("latitud_base").alias("ultima_latitud"),
        F.col("longitud_base").alias("ultima_longitud"),
    )
    .withColumn("estado_conductor", F.lit("disponible"))
    .withColumn("id_viaje_activo", F.lit(None).cast(T.StringType()))
    .withColumn("id_pasajero_activo", F.lit(None).cast(T.StringType()))
    .withColumn("etapa_viaje", F.lit(None).cast(T.StringType()))
    .withColumn("pickup_latitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("pickup_longitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("dropoff_latitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("dropoff_longitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("distancia_km_plan", F.lit(None).cast(T.DoubleType()))
    .withColumn("duracion_min_plan", F.lit(None).cast(T.IntegerType()))
    .withColumn("tarifa_km_plan", F.lit(None).cast(T.DoubleType()))
    .withColumn("hora_pico_plan", F.lit(None).cast(T.BooleanType()))
    .withColumn("request_ts", F.lit(None).cast(T.TimestampType()))
    .withColumn("accepted_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("pickup_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("dropoff_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("cancel_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("tiempo_llegada_seg_plan", F.lit(None).cast(T.IntegerType()))
    .withColumn("duracion_viaje_seg_plan", F.lit(None).cast(T.IntegerType()))
    .withColumn("disponible_desde", F.lit(setup_ts).cast(T.TimestampType()))
    .withColumn("updated_at", F.lit(setup_ts).cast(T.TimestampType()))
)

# Estado inicial de pasajeros: todos disponibles, sin viaje activo y ubicados en su punto base
estado_clientes_df = (
    clientes_df.select(
        "id_pasajero",
        F.col("provincia").alias("provincia_actual"),
        F.col("canton").alias("canton_actual"),
        F.col("zona").alias("zona_actual"),
        F.col("latitud_base").alias("ultima_latitud"),
        F.col("longitud_base").alias("ultima_longitud"),
    )
    .withColumn("estado_pasajero", F.lit("disponible"))
    .withColumn("id_viaje_activo", F.lit(None).cast(T.StringType()))
    .withColumn("id_conductor_activo", F.lit(None).cast(T.StringType()))
    .withColumn("etapa_viaje", F.lit(None).cast(T.StringType()))
    .withColumn("pickup_latitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("pickup_longitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("dropoff_latitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("dropoff_longitud", F.lit(None).cast(T.DoubleType()))
    .withColumn("request_ts", F.lit(None).cast(T.TimestampType()))
    .withColumn("accepted_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("pickup_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("dropoff_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("cancel_ts_plan", F.lit(None).cast(T.TimestampType()))
    .withColumn("updated_at", F.lit(setup_ts).cast(T.TimestampType()))
)

# Estado inicial de viajes
estado_viajes_df = spark.createDataFrame([], schema=viajes_schema)

# Persistencia completa del universo base del laboratorio en tablas Delta administradas
(geo_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_GEO))
(clientes_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_CLIENTES))
(conductores_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_CONDUCTORES))
(estado_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_ESTADO))
(estado_clientes_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_ESTADO_CLIENTES))
(estado_viajes_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE_ESTADO_VIAJES))

# COMMAND ----------

# Validaciones finales: comprueban cobertura geografica, volumen, edades y unicidad de estados
validaciones = {
    "geo_cobertura_completa": spark.table(TABLE_GEO).select("provincia", "canton").distinct().count() == len(GEO_REFERENCE),
    "clientes_creados": spark.table(TABLE_CLIENTES).count() == PASSENGER_COUNT,
    "conductores_creados": spark.table(TABLE_CONDUCTORES).count() == DRIVER_COUNT,
    "solo_mayores_edad_clientes": spark.table(TABLE_CLIENTES).filter(F.col("edad") < 18).count() == 0,
    "solo_mayores_edad_conductores": spark.table(TABLE_CONDUCTORES).filter(F.col("edad") < 23).count() == 0,
    "clientes_cubren_todos_los_cantones": (
        spark.table(TABLE_CLIENTES).select("provincia", "canton").distinct().count() == len(GEO_REFERENCE)
    ),
    "conductores_cubren_todos_los_cantones": (
        spark.table(TABLE_CONDUCTORES).select("provincia", "canton").distinct().count() == len(GEO_REFERENCE)
    ),
    "tabla_estado_clientes_creada": spark.table(TABLE_ESTADO_CLIENTES).count() == PASSENGER_COUNT,
    "tabla_estado_viajes_creada": spark.table(TABLE_ESTADO_VIAJES).count() == 0,
    "estado_unico_por_conductor": (
        spark.table(TABLE_ESTADO)
        .groupBy("id_conductor")
        .count()
        .filter(F.col("count") > 1)
        .count()
        == 0
    ),
    "estado_unico_por_pasajero": (
        spark.table(TABLE_ESTADO_CLIENTES)
        .groupBy("id_pasajero")
        .count()
        .filter(F.col("count") > 1)
        .count()
        == 0
    ),
    "provincias_y_cantones_poblados": (
        spark.table(TABLE_CLIENTES)
        .filter(F.col("provincia").isNull() | F.col("canton").isNull())
        .count()
        == 0
    ),
}

failed_checks = [name for name, result in validaciones.items() if not result]
if failed_checks:
 raise ValueError(f"Fallaron validaciones de setup: {failed_checks}")

# Evidencia visual de las validaciones para el presentador o el estudiante
display(
 spark.createDataFrame(
 [(key, str(value)) for key, value in validaciones.items()],
 schema="validacion string, resultado string",
 )
)

# Resumen final de las tablas preparadas por el setup
print(f"Tablas listas en {CATALOG}.{SCHEMA}")
print(f"Geo: {TABLE_GEO}")
print(f"Cantones cubiertos: {len(GEO_REFERENCE)}")
print(f"Clientes: {TABLE_CLIENTES}")
print(f"Conductores: {TABLE_CONDUCTORES}")
print(f"Estado: {TABLE_ESTADO}")
print(f"Estado clientes: {TABLE_ESTADO_CLIENTES}")
print(f"Estado viajes: {TABLE_ESTADO_VIAJES}")
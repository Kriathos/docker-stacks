# ⚙️ Configuración de Nginx — `nginx.conf`

<div align="center">

**Guía para crear el archivo de configuración del proxy reverso**

[¿Por qué no está versionado?](#por-qué-no-está-versionado) • [Template completo](#template-completo) • [Adaptar al entorno](#adaptar-al-entorno-propio) • [Nuevas rutas](#agregar-nuevas-rutas) • [WebSocket](#caso-especial-websocket) • [Validar](#validar-la-configuración)

</div>

---

## ¿Por qué no está versionado?

El archivo `nginx.conf` contiene **nombres de dominio personales o específicos del entorno local** de cada usuario (ej: `mi-lab.com`, `mi-empresa.local`). Por eso cada persona debe crear su propia versión adaptada a sus dominios locales.

Esta guía documenta la estructura completa del archivo para que sea totalmente replicable.

---

## Estructura del archivo

El archivo tiene dos bloques raíz:

```nginx
events { }   # Motor de eventos Nginx — puede dejarse vacío para labs locales

http {
  # Un bloque server por cada servicio expuesto
}
```

### Patrón de cada bloque `server`

```nginx
server {
    listen 80;                            # Puerto HTTP — no cambiar
    server_name servicio.tu-dominio.com;  # Hostname que escribirás en el navegador

    location / {
        proxy_pass http://nombre-contenedor:puerto-interno;  # Nombre exacto del servicio en docker-compose.yml
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

> El valor de `proxy_pass` debe usar el **nombre del servicio** definido en el `docker-compose.yml` del stack correspondiente, no `localhost`.

---

## Template completo

Crea el archivo `web/nginx.conf` con el siguiente contenido. Reemplaza `tu-dominio.com` por el hostname que uses en tu entorno.

```nginx
events {}

http {

  # ─── Página de bienvenida Nginx (opcional) ───────────────────────────────
  server {
    listen 80;
    location / {
      root /usr/share/nginx/html;
      index index.html;
    }
  }

  # ─── Storage Stack ────────────────────────────────────────────────────────

  # SFTPGo Web UI
  server {
    listen 80;
    server_name sftp.tu-dominio.com;
    location / {
      proxy_pass http://sftpgo:51500;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # MinIO API (S3)
  server {
    listen 80;
    server_name minio-api.tu-dominio.com;
    location / {
      proxy_pass http://minio:9000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # MinIO Console
  server {
    listen 80;
    server_name minio.tu-dominio.com;
    location / {
      proxy_pass http://minio:9001;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Apache File Server
  server {
    listen 80;
    server_name data.tu-dominio.com;
    location / {
      proxy_pass http://apache-fileserver:80;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # ─── Kafka Stack ──────────────────────────────────────────────────────────

  # Kafka UI — KRaft
  server {
    listen 80;
    server_name kraft-ui.tu-dominio.com;
    location / {
      proxy_pass http://kafka-ui-kraft:8080;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Kafka Connect API — KRaft (Debezium)
  server {
    listen 80;
    server_name kraft-api.tu-dominio.com;
    location / {
      proxy_pass http://kafka-connect-kraft:8083;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Kafka UI — Zookeeper
  server {
    listen 80;
    server_name zoo-ui.tu-dominio.com;
    location / {
      proxy_pass http://kafka-ui-zoo:8080;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Kafka Connect API — Zookeeper (Debezium)
  server {
    listen 80;
    server_name zoo-api.tu-dominio.com;
    location / {
      proxy_pass http://kafka-connect-zoo:8083;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # ─── Databricks Stack ─────────────────────────────────────────────────────

  # Jupyter Lab — requiere soporte WebSocket (ver nota al pie)
  server {
    listen 80;
    server_name jupyter.tu-dominio.com;
    location / {
      proxy_pass http://jupyter:8888;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_read_timeout 86400;
    }
  }

  # MLflow
  server {
    listen 80;
    server_name mlflow.tu-dominio.com;
    location / {
      proxy_pass http://mlflow:5000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Airflow Webserver
  server {
    listen 80;
    server_name airflow.tu-dominio.com;
    location / {
      proxy_pass http://airflow-webserver:8080;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # HashiCorp Vault
  server {
    listen 80;
    server_name vault.tu-dominio.com;
    location / {
      proxy_pass http://vault:8200;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # Spark Master UI
  server {
    listen 80;
    server_name spark.tu-dominio.com;
    location / {
      proxy_pass http://spark:8080;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

}
```

---

## Adaptar al entorno propio

### 1. Elegir un dominio local

Reemplaza `tu-dominio.com` por el nombre que prefieras. Ejemplos comunes en labs:

| Estilo | Ejemplo |
|--------|---------|
| Dominio ficticio | `mi-lab.com` → `jupyter.mi-lab.com` |
| Subdominio local | `local` → `jupyter.local` |
| Empresa/proyecto | `datalab.dev` → `jupyter.datalab.dev` |

No hace falta registrar el dominio: solo funciona en tu máquina gracias al archivo `hosts`.

### 2. Actualizar el archivo `hosts` de Windows

Edita `C:\Windows\System32\drivers\etc\hosts` **como administrador** y agrega una línea por cada hostname:

```text
127.0.0.1 sftp.tu-dominio.com
127.0.0.1 minio.tu-dominio.com
127.0.0.1 minio-api.tu-dominio.com
127.0.0.1 data.tu-dominio.com
127.0.0.1 kraft-ui.tu-dominio.com
127.0.0.1 kraft-api.tu-dominio.com
127.0.0.1 zoo-ui.tu-dominio.com
127.0.0.1 zoo-api.tu-dominio.com
127.0.0.1 jupyter.tu-dominio.com
127.0.0.1 mlflow.tu-dominio.com
127.0.0.1 airflow.tu-dominio.com
127.0.0.1 vault.tu-dominio.com
127.0.0.1 spark.tu-dominio.com
```

> La configuración global de hosts del proyecto está documentada en [config.md](../config.md).

---

## Agregar nuevas rutas

Para exponer un servicio adicional, agrega un bloque `server` dentro del bloque `http {}`:

```nginx
server {
    listen 80;
    server_name mi-servicio.tu-dominio.com;

    location / {
        proxy_pass http://nombre-del-contenedor:puerto-interno;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Pasos completos:
1. Agregar el bloque `server` en `nginx.conf`
2. Agregar la entrada en el archivo `hosts` de Windows
3. Recargar Nginx sin reiniciar el contenedor:

```powershell
docker compose exec nginx nginx -s reload
```

---

## Caso especial: WebSocket

Jupyter Lab y otras aplicaciones interactivas requieren cabeceras WebSocket. Sin ellas los kernels fallan silenciosamente o la UI no carga.

```nginx
location / {
    proxy_pass http://servicio:puerto;
    proxy_http_version 1.1;

    # Cabeceras obligatorias para WebSocket
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Cabeceras estándar
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeout largo para sesiones interactivas
    proxy_read_timeout 86400;
}
```

---

## Validar la configuración

```powershell
# Verificar sintaxis antes de aplicar
docker compose exec nginx nginx -t

# Recargar sin downtime (no reinicia el contenedor)
docker compose exec nginx nginx -s reload

# Ver logs de acceso y errores
docker compose logs nginx

# Seguir logs en tiempo real
docker compose logs -f nginx
```

---

<div align="center">

[⬆ Arriba](#️-configuración-de-nginx--nginxconf) • [← Web Stack README](README.md) • [← Proyecto Principal](../README.md)

</div>

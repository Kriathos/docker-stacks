# 🔐 Guía de Seguridad

Guía completa para securizar el laboratorio de desarrollo e implementar prácticas de seguridad en producción.

---

## ⚠️ Disclaimer Importante

**Este laboratorio está diseñado para desarrollo y educación, NO para producción.**

- ✅ Excelente para aprendizaje, testing, prototipado
- ❌ NO usar credenciales hardcodeadas en producción
- ❌ NO exponer servicios directamente a internet sin hardening
- ❌ NO confiar en configuración por defecto para datos sensibles

---

## 📋 Tabla de Contenidos

0. [Estado actual del laboratorio](#estado-actual-del-laboratorio)
1. [Desarrollo (Seguro)](#desarrollo-seguro)
2. [Transición a Producción](#transición-a-producción)
3. [Gestión de Secretos](#gestión-de-secretos)
4. [Autenticación y Autorización](#autenticación-y-autorización)
5. [Cifrado](#cifrado)
6. [Networking](#networking)
7. [Compliance](#compliance)

---

## 🧭 Estado actual del laboratorio

Esta sección describe la configuración real del proyecto. Las secciones siguientes son ejemplos generales.

### Exposición a internet

- **Caddy (80 y 443):** entrada HTTP y HTTPS para todos los subdominios. La lista está en la [guía](docs/guia.md#52-cloudflare-dns).
- **TCP publicados por el router:** SQL Server (51430), DB2 (51431), SFTP (51432), Kafka con Zookeeper (51435) y los brokers KRaft (51437 a 51439). Son los únicos puertos reservados que se usan.
- **Postgres:** no publican puerto. Solo se alcanzan desde la red `datalab`, a través de pgAdmin.
- **Puertos nuevos:** los publicados empiezan en 51500. Ver [ADR 0005](docs/adr/0005-postgres-sin-puertos-y-reglas-de-puertos.md).

### Autenticación

- **Servicios con login propio:** SFTPGo, MinIO, Vault, Airflow, Grafana, Uptime Kuma, ntfy (sin acceso anónimo), pgAdmin, FileBrowser y Jupyter (con token).
- **Servicios con clave de Caddy:** Apache, Kafka UI, Kafka Connect, MLflow, Spark UI y Prometheus.
- **Portainer:** primero la clave de Caddy, después su propio login. Controla el socket de Docker, así que quien entre controla la PC.

Ver [ADR 0004](docs/adr/0004-autenticacion-por-capas-en-caddy.md).

### Riesgos conocidos

- **Kafka sin cifrado ni autenticación:** los listeners están en `PLAINTEXT`. Quien llegue a los puertos 51435 o 51437 a 51439 puede producir y consumir mensajes. Pendiente: TLS y SASL.
- **SQL Server y DB2 por TCP directo:** están expuestos con su usuario administrador (`sa` y `db2inst1`). El compose no configura TLS para ninguno de los dos.
- **Clave de Caddy compartida:** es la misma para todos los servicios protegidos. CrowdSec detecta intentos fallidos, pero según la configuración actual no los bloquea.
- **windows_exporter (puerto 9182):** corre en Windows y su regla de firewall acepta conexiones entrantes en todos los perfiles de red. Cualquier equipo de la red local puede leer las métricas del host. Si no lo necesitas, limita la regla a Docker o elimínala ([ADR 0007](docs/adr/0007-metricas-del-host-con-windows-exporter.md)).
- **Portainer con socket de Docker:** quien entre a Portainer controla los contenedores y, en la práctica, la PC. Su setup token aparece en los logs del contenedor mientras no se cree la cuenta.
- **Vault sellado tras reinicio:** mientras esté sellado no entrega secretos, pero el desbloqueo exige 3 de sus 5 claves. Guárdalas fuera del repositorio.
- **Contraseñas en el historial de git:** las que ya estaban antes de moverlas a `.env` se conservaron por decisión propia ([ADR 0003](docs/adr/0003-secretos-en-env-sin-versionar.md)).

---

## ✅ Desarrollo (Seguro)

### 1. Archivos Sensibles en .gitignore

```bash
# .gitignore
credenciales.txt
.env
.env.local
*.key
*.pem
secrets/
sensitive/
docker-compose.override.yml
```

---

### 2. Usar .env para Desarrollo Local

```bash
# .env (agregar a .gitignore)
POSTGRES_PASSWORD=mi-contraseña-local-123
MINIO_PASSWORD=mi-minio-local-456
SA_PASSWORD=MiSQL$Local2024
AIRFLOW_FERNET_KEY=gAAAAABl...
```

```yaml
# docker-compose.yml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

```powershell
# Cargar .env antes de ejecutar
$env:POSTGRES_PASSWORD = "..."
docker-compose up -d
```

---

### 3. Credenciales No en Código

✅ **BIEN:**
```python
# Obtener de variable de entorno
import os
password = os.getenv("DB_PASSWORD")
```

❌ **MAL:**
```python
# Hardcodeada
password = "MySecurePass123"
```

---

### 4. Redes Aisladas

```yaml
# Los servicios se conectan a su red de grupo (default) y a datalab solo si Caddy
# o otro grupo los necesitan. Sin ports:, nada es accesible desde el host.
networks:
  - default
  - datalab
```

---

### 5. Puertos No Expuestos

```yaml
# ✅ BIEN - Solo interno
services:
  database:
    # Sin ports: definido
    # Solo accesible desde otros contenedores

# ❌ MAL - Expuesto
services:
  database:
    ports:
      - "5432:5432"  # Accesible desde localhost
```

---

## 🚀 Transición a Producción

### Checklist de Seguridad Pre-Producción

- [ ] Todas las credenciales en variables de entorno
- [ ] `.env` en `.gitignore`
- [ ] Sin hardcoding de passwords
- [ ] HTTPS habilitado (Let's Encrypt)
- [ ] Firewall configurado
- [ ] VPN o private network para acceso
- [ ] Logs auditoría habilitados
- [ ] Backup y recovery testado
- [ ] Monitoreo y alertas configurados
- [ ] Security scan de imágenes
- [ ] Roles y permisos RBAC
- [ ] Encryption at rest y in transit

---

## 🔑 Gestión de Secretos

### 1. HashiCorp Vault (Recomendado)

Ya está en Databricks Stack. Usarlo en producción:

```bash
# Iniciar Vault en modo no-dev
vault server -config=/path/to/config.hcl

# Unseal Vault
vault operator unseal

# Crear secret
vault kv put secret/database/postgres \
  username=admin \
  password=secure-password
```

```python
# Acceder secreto desde Python
import hvac

client = hvac.Client(url='https://vault.example.com:8200', token='mytoken')
secret = client.secrets.kv.read_secret_version(path='secret/database/postgres')
password = secret['data']['data']['password']
```

---

### 2. AWS Secrets Manager (Si usas AWS)

```bash
# Crear secreto
aws secretsmanager create-secret \
  --name prod/database/password \
  --secret-string "secure-password"

# Leer secreto
aws secretsmanager get-secret-value \
  --secret-id prod/database/password
```

---

### 3. Azure Key Vault (Si usas Azure)

```bash
# Crear secreto
az keyvault secret set --vault-name mykeyvault \
  --name db-password --value "secure-password"

# Leer secreto
az keyvault secret show --vault-name mykeyvault \
  --name db-password
```

---

### 4. Generar Credenciales Seguras

```powershell
# PowerShell - Contraseña random
$password = -join ((65..90) + (97..122) + (48..57) + (33..47) | Get-Random -Count 32 | % {[char]$_})
Write-Output $password

# Python
import secrets
password = secrets.token_urlsafe(32)
print(password)

# OpenSSL
openssl rand -base64 32
```

---

## 👤 Autenticación y Autorización

### 1. SQL Server - Crear Usuarios Específicos

```sql
-- En lugar de usar 'sa'
CREATE LOGIN appuser WITH PASSWORD = 'SecurePass123!';
CREATE USER appuser FOR LOGIN appuser;
GRANT SELECT, INSERT, UPDATE ON MyDatabase TO appuser;
```

---

### 2. PostgreSQL - Usuarios con Permisos Limitados

```sql
-- Crear usuario específico
CREATE ROLE app_user WITH LOGIN ENCRYPTED PASSWORD 'secure';
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

---

### 3. Airflow - Cambiar Credenciales por Defecto

```python
# En Airflow webserver
python -m airflow users create \
  --username myuser \
  --password mysecurepassword \
  --firstname My \
  --lastname User \
  --role Admin \
  --email me@example.com

# Cambiar contraseña de 'airflow'
python -m airflow users modify --username airflow --password newsecurepass
```

---

### 4. MinIO - Crear Usuarios IAM

```bash
# Crear usuario MinIO
mc admin user add minio appuser apppassword

# Asignar policy
mc admin policy attach minio readwrite --user=appuser
```

---

## 🔒 Cifrado

### 1. TLS/HTTPS

Caddy lo configura automáticamente:

```
# Caddyfile
example.com {
  # HTTPS automático con Let's Encrypt
  reverse_proxy backend:3000
}
```

---

### 2. Cifrado en Reposo (at rest)

```yaml
# Docker Compose - Cifrar volumen
volumes:
  encrypted_data:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
```

---

### 3. Cifrado en Tránsito (in transit)

```yaml
# Todas las conexiones entre contenedores de la misma red
# Docker maneja cifrado por defecto

# Para conexiones externas, usar TLS:
services:
  api:
    environment:
      SSL_ENABLED: "true"
      SSL_CERT_PATH: /etc/ssl/certs/server.crt
      SSL_KEY_PATH: /etc/ssl/private/server.key
    volumes:
      - ./certs/server.crt:/etc/ssl/certs/server.crt:ro
      - ./certs/server.key:/etc/ssl/private/server.key:ro
```

---

## 🌐 Networking

### 1. Firewall - Permitir Solo Necesario

```bash
# Windows Firewall (PowerShell - Admin)
New-NetFirewallRule -DisplayName "Allow Caddy" `
  -Direction Inbound -Protocol TCP -LocalPort 80,443 `
  -Action Allow

# Denegar otros puertos
New-NetFirewallRule -DisplayName "Block Kafka" `
  -Direction Inbound -Protocol TCP -LocalPort 9092 `
  -Action Block
```

---

### 2. Exponer Solo Puertos Necesarios

```yaml
# ✅ BIEN - Solo Caddy expuesto. En este laboratorio, además, los TCP reservados
# (51430 a 51440) que el router reenvía. Los Postgres no publican puerto.
services:
  caddy:
    ports:
      - "80:80"
      - "443:443"
  
  # MinIO y Apache van por Caddy, sin puerto publicado

# ❌ MAL - Todos los puertos expuestos
services:
  sqlserver:
    ports:
      - "1433:1433"  # Accesible desde internet
  minio:
    ports:
      - "9000:9000"  # Accesible desde internet
```

---

### 3. VPN para Acceso Remoto

Para producción con datos sensibles:

```bash
# OpenVPN setup (ejemplo)
docker run -d \
  --name openvpn \
  --cap-add=NET_ADMIN \
  -v /data/openvpn:/etc/openvpn \
  -p 1194:1194/udp \
  kylemanna/openvpn
```

---

### 4. Rate Limiting en Caddy

```
# Caddyfile
example.com {
  rate_limit * 100/1m
  
  # 100 requests por minuto por IP
  reverse_proxy backend:3000
}
```

---

## 🛡️ Compliance

### 1. Auditoría (Logging)

```yaml
# docker-compose.yml
services:
  all:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=myapp"
```

---

### 2. GDPR Compliance

Para datos personales:

- ✅ Encriptar datos en reposo
- ✅ Encriptar datos en tránsito
- ✅ Implementar right-to-be-forgotten (borrar datos)
- ✅ Auditoria de acceso
- ✅ Data classification
- ✅ Privacy impact assessment

---

### 3. HIPAA Compliance (Healthcare)

Si trabajas con datos de salud:

- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Access control (MFA)
- ✅ Audit logging (6 años)
- ✅ Backup y recovery tested
- ✅ Business Associate Agreement

---

### 4. SOC 2 Type II

Para empresas que necesitan certificación:

- ✅ Security policies
- ✅ Incident response plan
- ✅ Vulnerability scanning
- ✅ Penetration testing
- ✅ Employee training
- ✅ Change management
- ✅ Disaster recovery

---

## 🔍 Scanning de Seguridad

### 1. Escanear Imágenes Docker

```bash
# Con Trivy
trivy image confluentinc/cp-kafka:latest

# Con Snyk
snyk container test confluentinc/cp-kafka:latest

# Con Docker Scout
docker scout cves confluentinc/cp-kafka:latest
```

---

### 2. Escanear Código

```bash
# Con OWASP Dependency Check
dependency-check --project "MyProject" --scan .

# Con npm audit (si usas Node)
npm audit

# Con pip audit (si usas Python)
pip-audit
```

---

### 3. Scanning de Secretos

```bash
# Con git-secrets
git secrets --install
git secrets --scan

# Con detect-secrets
detect-secrets scan > .secrets.baseline
```

---

## 📋 Producción Checklist

### Pre-Deploy

- [ ] Todas credenciales en Vault/Secrets Manager
- [ ] HTTPS habilitado y certificados válidos
- [ ] Firewall configurado (solo puertos necesarios)
- [ ] VPN para acceso administrativo
- [ ] Backup y restore testado
- [ ] Monitoring y alertas configurados
- [ ] Logs centralizados (ELK, CloudWatch, etc.)
- [ ] Security scanning completado
- [ ] Penetration testing realizado
- [ ] Incident response plan documentado

### Post-Deploy

- [ ] Monitorear logs para anomalías
- [ ] Revisar acceso a datos sensibles
- [ ] Actualizar políticas de seguridad
- [ ] Entrenar equipo en seguridad
- [ ] Testear disaster recovery mensualmente
- [ ] Revisar y rotar credenciales trimestralmente
- [ ] Actualizar dependencias de seguridad
- [ ] Realizar auditoría anual

---

## 🚨 Incident Response

Si sospechas una violación de seguridad:

1. **Detectar:** Revisar logs para actividad sospechosa
2. **Contener:** Aislar sistemas afectados
3. **Investigar:** Determinar alcance del incidente
4. **Erradicar:** Remover acceso no autorizado
5. **Recuperar:** Restaurar sistemas a estado seguro
6. **Reportar:** Notificar a stakeholders si es necesario
7. **Mejorar:** Implementar controles para prevenir recurrencia

---

## 📚 Recursos de Seguridad

- [OWASP Top 10](https://owasp.org/Top10/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)

---

## 🔗 Relacionado

- [Guía del laboratorio](docs/guia.md) - Configuración y solución de problemas
- [ADR 0003](docs/adr/0003-secretos-en-env-sin-versionar.md) - Secretos en `.env`
- [ADR 0004](docs/adr/0004-autenticacion-por-capas-en-caddy.md) - Autenticación por capas
- [ADR 0005](docs/adr/0005-postgres-sin-puertos-y-reglas-de-puertos.md) - Postgres y puertos

---

<div align="center">

**La seguridad es un proceso, no un producto.**

[📖 README](./README.md) | [🔐 SECURITY](./SECURITY.md) | [🔧 Guía](./docs/guia.md)

</div>

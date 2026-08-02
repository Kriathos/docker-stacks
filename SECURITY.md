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

1. [Desarrollo (Seguro)](#desarrollo-seguro)
2. [Transición a Producción](#transición-a-producción)
3. [Gestión de Secretos](#gestión-de-secretos)
4. [Autenticación y Autorización](#autenticación-y-autorización)
5. [Cifrado](#cifrado)
6. [Networking](#networking)
7. [Compliance](#compliance)

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
# Desarrollo - La red mynet aísla del host
networks:
  mynet:
    external: true
    # No exponer al host directamente
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
# Todas las conexiones entre contenedores en mynet
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
# ✅ BIEN - Solo Caddy y SSH expuestos
services:
  caddy:
    ports:
      - "80:80"
      - "443:443"
  
  # SQL, MinIO, Kafka: NO expuestos directamente

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

- [credenciales.md](./credenciales.md) - Gestión de secretos
- [config.md](./config.md) - Configuración segura
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Diseño seguro

---

<div align="center">

**La seguridad es un proceso, no un producto.**

[📖 README](./README.md) | [🔐 SECURITY](./SECURITY.md) | [🔧 TROUBLESHOOTING](./TROUBLESHOOTING.md)

</div>

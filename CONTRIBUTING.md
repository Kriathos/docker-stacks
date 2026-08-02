# 🤝 Guía de Contribución

¿Te interesa contribuir al laboratorio? ¡Bienvenido! Esta guía te mostrará cómo participar.

---

## 📋 Tabla de Contenidos

1. [Código de Conducta](#código-de-conducta)
2. [¿Cómo Contribuir?](#cómo-contribuir)
3. [Process de Contribución](#process-de-contribución)
4. [Estándares de Código](#estándares-de-código)
5. [Documentación](#documentación)
6. [Testing](#testing)

---

## 📝 Código de Conducta

Este proyecto se adhiere a un código de conducta que esperamos todos respetemos:

- ✅ Sé respetuoso con otros contribuidores
- ✅ Sé inclusivo e acogedor
- ✅ Proporciona crítica constructiva
- ✅ Enfócate en lo que es mejor para la comunidad
- ✅ Sé responsable de tus palabras y acciones

**Conducta inaceptable:**
- ❌ Lenguaje ofensivo o discriminatorio
- ❌ Acoso o intimidación
- ❌ Spam o publicidad
- ❌ Violación de privacidad

---

## 🚀 ¿Cómo Contribuir?

### Tipos de Contribuciones Bienvenidas

1. **🐛 Reportar Bugs**
   - Encontraste un problema
   - Crea un GitHub Issue detallado

2. **📚 Mejorar Documentación**
   - Correcciones ortográficas
   - Clarificaciones
   - Nuevos ejemplos
   - Traducciones

3. **✨ Nuevas Características**
   - Mejoras al stack
   - Nuevos servicios
   - Optimizaciones

4. **🧪 Tests**
   - Cobertura de testing
   - Scripts de validación

5. **🎨 Mejoras de UI/UX**
   - Mejor landing page
   - Dashboards mejorados
   - Documentación visual

### Reportar Bugs

**Antes de reportar:**
- Verifica que no exista un issue similar
- Intenta reproducir el problema
- Recolecta información relevante

**Al reportar:**
```markdown
### Descripción
Descripción clara del problema

### Pasos para Reproducir
1. Paso 1
2. Paso 2
3. Paso 3

### Comportamiento Esperado
Qué debería pasar

### Comportamiento Actual
Qué está pasando

### Información del Sistema
- OS: [ej. Windows 11]
- Docker version: [ej. 25.0]
- Docker Compose version: [ej. 2.25]

### Logs
```
<paste logs aquí>
```

### Screenshots
[Si aplica]
```

---

## 📋 Process de Contribución

### Paso 1: Fork el Repositorio

```bash
# En GitHub, click "Fork"
git clone https://github.com/tu-usuario/repo.git
cd repo
```

### Paso 2: Crear Rama para Tu Feature

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama
git checkout -b feature/tu-feature
# O para bugs: git checkout -b fix/descripcion-bug
```

**Naming convention:**
- Features: `feature/nombre-descriptivo`
- Bugs: `fix/descripcion-bug`
- Docs: `docs/mejora`
- Tests: `test/cobertura`

### Paso 3: Hacer Cambios

```bash
# Editar archivos
# Commit regularmente
git add .
git commit -m "Descripción clara del cambio"
```

**Commit messages:**
```
# ✅ BIEN
feat: add Kafka KRaft setup.md
fix: resolve SQL Server connection timeout
docs: clarify docker-compose usage
test: add integration tests for CDC

# ❌ MAL
fixed stuff
update
changes
wip
```

### Paso 4: Push a Tu Fork

```bash
git push origin feature/tu-feature
```

### Paso 5: Crear Pull Request

1. Ve a GitHub
2. Click "Compare & pull request"
3. Describe tus cambios
4. Referencia issues si aplica (Fixes #123)
5. Espera review

**PR Template:**
```markdown
## Descripción
Explicación clara de los cambios

## Tipo de Cambio
- [ ] Feature nueva
- [ ] Bug fix
- [ ] Mejora de documentación
- [ ] Refactoring
- [ ] Test

## Cambios
- Cambio 1
- Cambio 2

## Testing Realizado
Describe cómo testeaste

## Checklist
- [ ] Mi código sigue los estándares
- [ ] Actualicé documentación
- [ ] Agregué tests si es necesario
- [ ] No rompo tests existentes
- [ ] Revisamé el código yo mismo
```

### Paso 6: Responder a Reviews

Cuando los maintainers revisen:
- Lee los comentarios cuidadosamente
- Haz los cambios solicitados
- Responde preguntas
- Push cambios adicionales a la misma rama

```bash
git add .
git commit -m "Address review comments"
git push origin feature/tu-feature
```

### Paso 7: Merge

Después de aprobación:
- Los maintainers hacen el merge
- Tu rama se elimina
- Tu contribución aparece en CHANGELOG

---

## 📝 Estándares de Código

### Documentación

Todos los cambios requieren documentación:

```markdown
# ✅ BIEN - Bien documentado
# Nueva feature con ejemplos

# ❌ MAL - Sin documentación
# Agregué esto
```

### Docker & Compose

```yaml
# ✅ BIEN - Claro y bien estructura
services:
  my-service:
    image: myimage:latest
    container_name: my-service
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      VAR_NAME: value
    volumes:
      - my_volume:/data
    networks:
      - mynet

# ❌ MAL - Falta información
services:
  service:
    image: image
```

### Python (Spark, Airflow)

```python
# ✅ BIEN - Type hints y docstrings
def process_data(df: DataFrame, threshold: int) -> DataFrame:
    """Process DataFrame with given threshold.
    
    Args:
        df: Input DataFrame
        threshold: Minimum value filter
        
    Returns:
        Processed DataFrame
    """
    return df.filter(df.value >= threshold)

# ❌ MAL - Sin documentación
def process_data(df, threshold):
    return df.filter(df.value >= threshold)
```

### Markdown

```markdown
# ✅ BIEN - Bien formateado
## Sección
Párrafo explicativo.

```bash
comando
```

# ❌ MAL - Desorganizado
Sección
comando aquí
más texto
```

---

## 📚 Documentación

### Agregar Nueva Feature

1. **Documenta en README.md**
   ```markdown
   ### Mi Nueva Feature
   Descripción breve
   
   📖 [Documentación completa](./docs/feature.md)
   ```

2. **Crea archivo de documentación**
   - `setup.md` para instrucciones de setup
   - `config.md` para configuración
   - `README.md` para descripción general

3. **Actualiza INDEX.md** si es necesario

### Actualizar Documentación Existente

- Mantén el tono consistente
- Usa ejemplos verificables
- Incluye troubleshooting
- Link a recursos relacionados

---

## 🧪 Testing

### Antes de Hacer PR

Verifica que todo funciona:

```bash
# 1. Lint & Format
# (implementar si es necesario)

# 2. Tests
./run_tests.sh
# o
pytest tests/

# 3. Build Docker
docker-compose build

# 4. Setup local
docker-compose up -d

# 5. Verify manually
# Accede a servicios y verifica funcionan
```

### Tests Esperados

Para cambios de código:
- Unit tests
- Integration tests si aplica
- Manual testing

Para cambios de documentación:
- Verificar liens
- Verificar ejemplos funcionan
- Revisar ortografía

---

## 🔄 Workflow Completo Ejemplo

```bash
# 1. Fork repo en GitHub

# 2. Clone tu fork
git clone https://github.com/tu-usuario/repo.git
cd repo

# 3. Agregar upstream
git remote add upstream https://github.com/original/repo.git

# 4. Crear rama
git checkout -b fix/sql-connection-timeout

# 5. Hacer cambios
# Editar archivos...

# 6. Commit
git add storage/config.md
git commit -m "fix: clarify SQL Server connection parameters"

# 7. Push
git push origin fix/sql-connection-timeout

# 8. Create PR en GitHub

# 9. Responder a reviews
# Hacer cambios según feedback...

# 10. Merge automático después de aprobación
```

---

## 🎯 Buenas Prácticas

### Do's ✅

- ✅ Comunícate claramente
- ✅ Sé paciente con reviews
- ✅ Prueba tus cambios
- ✅ Documenta tu trabajo
- ✅ Referencia issues relacionados
- ✅ Respeta el código existente
- ✅ Proporciona contexto en PRs
- ✅ Agradece los reviews

### Don'ts ❌

- ❌ No hagas cambios no relacionados en una PR
- ❌ No ignores comentarios de review
- ❌ No adds credenciales al código
- ❌ No cambies archivos de configuración sin discusión
- ❌ No hagas force push a PR abierto
- ❌ No publiques código sin tests
- ❌ No edites PRs de otros sin permiso
- ❌ No reportes problemas genéricos sin detalles

---

## 🏆 Reconocimiento

Agradecemos todas las contribuciones, grandes y pequeñas:

- 🐛 Bug reports
- 📚 Documentación
- 💡 Ideas
- ❓ Preguntas (ayudan a mejorar docs)
- ✨ Features
- 🧪 Tests

Todos los contribuidores serán listados en CONTRIBUTORS.md

---

## 📞 Ayuda

¿Preguntas? Puedes:

1. Revisar la documentación existente
2. Abrir un GitHub Discussion
3. Crear un issue con la pregunta
4. Contactar a los maintainers

---

## 📋 Checklist para Contribuidores

Antes de hacer PR:

- [ ] Leí este documento
- [ ] Mi código sigue los estándares
- [ ] Actualicé documentación
- [ ] Mis cambios funcionan localmente
- [ ] No agregué credenciales
- [ ] Commit messages son claros
- [ ] No hay cambios no relacionados
- [ ] Está listo para review

---

<div align="center">

**¡Gracias por contribuir al laboratorio!**

[📖 README](./README.md) | [🤝 CONTRIBUTING](./CONTRIBUTING.md) | [📝 CODE OF CONDUCT](./CODE_OF_CONDUCT.md)

</div>

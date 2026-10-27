# 0003: Secretos en `.env` sin versionar, con `.env.example` en git

Las contraseñas viven en `.env`, que está en `.gitignore`, y los compose exigen cada variable con `${VAR:?}` para fallar si falta alguna. Se descartó escribir contraseñas dentro de los compose porque quedan en el historial de git, y se descartó un gestor de secretos global porque el laboratorio no necesita esa complejidad todavía. Las contraseñas que ya estaban en el historial se conservaron por decisión explícita, y eso queda como riesgo aceptado.

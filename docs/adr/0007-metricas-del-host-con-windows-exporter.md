# 0007: Métricas del host con windows_exporter en lugar de Node Exporter

## Estado

Aceptada.

## Contexto

Prometheus necesita métricas del host (CPU, memoria, disco, red y hora). El laboratorio corre sobre Windows 11 con Docker Desktop, y Docker Desktop ejecuta los contenedores dentro de una máquina virtual Linux.

Node Exporter, en su versión de contenedor, requiere montar `/` del sistema con propagación `rslave`. Docker Desktop no permite ese montaje y el contenedor falla con `path / is mounted on / but it is not a shared or slave mount`. Aun si arrancara, mediría la VM de Linux, no la PC.

## Decisión

Las métricas del host las entrega `windows_exporter` (versión 0.31.9), instalado como servicio de Windows y escuchando en el puerto 9182. Prometheus lo consulta desde el contenedor en `host.docker.internal:9182` (job `windows-host`).

Los colectores habilitados son `cpu,memory,logical_disk,physical_disk,net,os,service,system,time`. El colector `time` expone la sincronización NTP (`windows_time_clock_sync_source`); el offset en segundos no lo expone esta versión.

Node Exporter se retira del grupo `observabilidad`. cAdvisor se mantiene para las métricas por contenedor.

## Consecuencias

- El exporter corre fuera de Docker, así que hay que instalarlo y registrarlo como servicio una vez (ver [guía, sección 2](../guia.md#2-requisitos-previos)).
- Se abre el puerto 9182 en el firewall de Windows. Ver el riesgo en [SECURITY.md](../../SECURITY.md#riesgos-conocidos).
- Si el equipo cambia de sistema operativo, esta decisión deja de aplicar y habrá que volver a evaluar Node Exporter sobre el host correspondiente.

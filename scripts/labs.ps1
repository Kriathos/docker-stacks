# Levanta, baja o valida los grupos del laboratorio.
#
# Ejemplos:
#   .\scripts\labs.ps1 up all
#   .\scripts\labs.ps1 up storage
#   .\scripts\labs.ps1 down all
#   .\scripts\labs.ps1 status
#   .\scripts\labs.ps1 validate

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('up', 'down', 'status', 'validate')]
    [string]$Accion,

    [Parameter(Position = 1)]
    [string]$Grupo = 'all'
)

$ErrorActionPreference = 'Stop'

$raiz = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $raiz '.env'

# Orden de arranque. Seguridad va al final porque Caddy enruta hacia los demás.
$grupos = [ordered]@{
    'storage'         = 'stacks/storage/compose.yaml'
    'kafka-zookeeper' = 'stacks/kafka-zookeeper/compose.yaml'
    'kafka-kraft'     = 'stacks/kafka-kraft/compose.yaml'
    'databricks'      = 'stacks/databricks/compose.yaml'
    'orquestacion'    = 'stacks/orquestacion/compose.yaml'
    'observabilidad'  = 'stacks/observabilidad/compose.yaml'
    'monitoreo'       = 'stacks/monitoreo/compose.yaml'
    'herramientas'    = 'stacks/herramientas/compose.yaml'
    'seguridad'       = 'stacks/seguridad/compose.yaml'
}

if ($Grupo -eq 'all') {
    $seleccion = @($grupos.Keys)
}
elseif ($grupos.Contains($Grupo)) {
    $seleccion = @($Grupo)
}
else {
    throw "Grupo desconocido: '$Grupo'. Opciones: all, $($grupos.Keys -join ', ')"
}

if ($Accion -ne 'status' -and -not (Test-Path $envFile)) {
    throw "No existe .env en $raiz. Copia .env.example a .env y completa los valores."
}

# La red compartida se crea una sola vez.
function Asegurar-Red {
    $existe = docker network ls --filter 'name=^datalab$' --format '{{.Name}}'
    if (-not $existe) {
        docker network create datalab | Out-Null
        Write-Host 'Red datalab creada.'
    }
}

function Ejecutar-Compose([string]$ruta, [string[]]$argumentos) {
    $archivo = Join-Path $raiz $ruta
    docker compose --env-file $envFile -f $archivo @argumentos
    if ($LASTEXITCODE -ne 0) { throw "docker compose falló en $ruta" }
}

switch ($Accion) {
    'up' {
        Asegurar-Red
        foreach ($g in $seleccion) {
            Write-Host "== Levantando $g"
            Ejecutar-Compose $grupos[$g] @('up', '-d')
        }
    }
    'down' {
        # Bajar en orden inverso al de subida.
        [array]::Reverse($seleccion)
        foreach ($g in $seleccion) {
            Write-Host "== Bajando $g"
            Ejecutar-Compose $grupos[$g] @('down')
        }
    }
    'status' {
        docker ps --filter 'label=com.docker.compose.project' --format 'table {{.Label "com.docker.compose.project"}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}'
    }
    'validate' {
        foreach ($g in $seleccion) {
            Write-Host "== Validando $g"
            Ejecutar-Compose $grupos[$g] @('config', '-q')
        }
        Write-Host 'Validación correcta.'
    }
}

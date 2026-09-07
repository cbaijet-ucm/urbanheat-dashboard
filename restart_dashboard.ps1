# Antes de iniciar, elimina TODOS los listeners vivos del puerto 8501.
# Así no pueden coexistir versiones antiguas de Streamlit.
$dashboardDir = $PSScriptRoot
$projectDir = Split-Path -Parent $dashboardDir
$python = Join-Path $projectDir ".urbanheat\Scripts\python.exe"
$app = Join-Path $dashboardDir "app.py"

$listenerPids = @(
    netstat -ano -p tcp |
        Select-String '^\s*TCP\s+\S+:8501\s+\S+\s+LISTENING\s+(\d+)\s*$' |
        ForEach-Object { [int]$_.Matches[0].Groups[1].Value } |
        Select-Object -Unique
)

foreach ($processId in $listenerPids) {
    taskkill /PID $processId /T /F | Out-Null
}

Start-Sleep -Seconds 2

if (netstat -ano -p tcp | Select-String '^\s*TCP\s+\S+:8501\s+\S+\s+LISTENING\s+') {
    throw "El puerto 8501 sigue ocupado; no se inicia una nueva instancia."
}

# Reinicia tambiÃ©n el servidor auxiliar de PNG para no conservar handlers antiguos.
$assetServerPids = @(
    netstat -ano -p tcp |
        Select-String '^\s*TCP\s+\S+:8766\s+\S+\s+LISTENING\s+(\d+)\s*$' |
        ForEach-Object { [int]$_.Matches[0].Groups[1].Value } |
        Select-Object -Unique
)
foreach ($processId in $assetServerPids) {
    taskkill /PID $processId /T /F | Out-Null
}

Start-Process `
    -FilePath $python `
    -ArgumentList "-B", "-m", "streamlit", "run", $app, "--server.port", "8501", "--server.headless", "true" `
    -WorkingDirectory $projectDir `
    -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Host "UrbanHeat BCN disponible en http://localhost:8501"

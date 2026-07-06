# Pont USB serie (ESP32 Arduino) -> broker MQTT Brésil
# Usage : npm run iot:serial
# Fermer miniterm / moniteur Arduino avant (un seul processus par COMx).

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$port = if ($env:SERIAL_PORT) { $env:SERIAL_PORT } else { "COM5" }

$running = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'serial_mqtt_bridge_bresil\.py' }

if ($running) {
    Write-Host "Pont serie deja actif - arret de l'instance precedente..." -ForegroundColor Yellow
    & "$PSScriptRoot\stop_iot_bridge.ps1"
    Start-Sleep -Seconds 1
}

# Verifie que le port COM est libre
$test = python -c "import serial; s=serial.Serial('$port',115200,timeout=1); s.close(); print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERREUR : $port occupe (Acces refuse)." -ForegroundColor Red
    Write-Host "Ferme miniterm, le moniteur serie Arduino, ou tout autre programme sur $port." -ForegroundColor Yellow
    Write-Host "Puis relance : npm run iot:serial" -ForegroundColor Yellow
    exit 1
}

Write-Host "Pont serie $port -> MQTT (topic entrepot_A)" -ForegroundColor Cyan
Write-Host "Chaine : capteur -> MQTT -> iot:bridge -> Aiven | Arret : Ctrl+C" -ForegroundColor DarkGray

$env:PYTHONIOENCODING = 'utf-8'
python -u scripts/serial_mqtt_bridge_bresil.py --port $port

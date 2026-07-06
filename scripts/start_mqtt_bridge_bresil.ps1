# Pont MQTT Brésil (ESP32) -> Aiven
# Usage : npm run iot:bridge

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Error "Fichier .env manquant a la racine (MYSQL_URL requis)."
}

$running = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'mqtt_bridge_bresil\.py' }

if ($running) {
    Write-Host "Pont MQTT deja actif - arret de l'instance precedente..." -ForegroundColor Yellow
    & "$PSScriptRoot\stop_iot_bridge.ps1"
    Start-Sleep -Seconds 1
}

Write-Host "Pont MQTT Brésil -> Aiven" -ForegroundColor Cyan
Write-Host "Broker : localhost:1883 (npm run iot:up) | Arret : Ctrl+C" -ForegroundColor DarkGray

$env:PYTHONIOENCODING = 'utf-8'
python -u scripts/mqtt_bridge_bresil.py

# Pont MQTT Brésil (ESP32) -> Aiven
# Usage : npm run iot:bridge

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Error "Fichier .env manquant a la racine (MYSQL_URL requis)."
}

Write-Host "Pont MQTT Brésil -> Aiven (ESP32 toutes les 30 s)" -ForegroundColor Cyan
Write-Host "Broker : localhost:1883 (npm run iot:up) | Arret : Ctrl+C" -ForegroundColor DarkGray

$env:PYTHONIOENCODING = 'utf-8'
python -u scripts/mqtt_bridge_bresil.py

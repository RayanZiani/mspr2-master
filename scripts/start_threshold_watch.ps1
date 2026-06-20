# Surveillance seuils + alertes Discord (dernier releve Aiven, toutes les 60 s).
#
# Usage :
#   powershell -File scripts/start_threshold_watch.ps1
#   powershell -File scripts/start_threshold_watch.ps1 -Interval 60

param(
    [int]$Interval = 60
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Error "Fichier .env manquant a la racine (MYSQL_URL + DISCORD_WEBHOOK_URL requis)."
}

$running = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "threshold_watch_aiven\.py" }

if ($running) {
    Write-Host "Surveillance seuils deja active - arret de l instance en cours..." -ForegroundColor Yellow
    & "$PSScriptRoot\stop_threshold_watch.ps1"
    Start-Sleep -Seconds 1
}

Write-Host "Surveillance seuils -> Aiven + Discord (intervalle ${Interval}s)" -ForegroundColor Cyan
Write-Host "Arret : Ctrl+C ou npm run sim:watch:stop" -ForegroundColor DarkGray

$env:PYTHONIOENCODING = "utf-8"
python -u scripts/threshold_watch_aiven.py --interval $Interval

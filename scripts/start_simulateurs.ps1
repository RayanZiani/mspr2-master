# Lance le simulateur de capteurs (Equateur + Colombie -> Aiven).
# Le Brésil est exclu par défaut (données via broker MQTT / ESP32).
# Affichage + insertion BDD toutes les 30 s (1 releve par capteur actif).
#
# Usage :
#   powershell -File scripts/start_simulateurs.ps1
#   powershell -File scripts/start_simulateurs.ps1 -Pays EC
#   powershell -File scripts/start_simulateurs.ps1 -IncludeBresil

param(
    [ValidateSet("ALL", "BR", "EC", "CO")]
    [string]$Pays = "ALL",
    [string]$ExcludePays = "BR",
    [switch]$IncludeBresil
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Error "Fichier .env manquant a la racine (MYSQL_URL requis)."
}

$running = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'simulate_releves_aiven\.py' }

if ($running) {
    Write-Host "Simulateur deja actif - arret des instances en double..." -ForegroundColor Yellow
    & "$PSScriptRoot\stop_simulateurs.ps1"
    Start-Sleep -Seconds 1
}

if ($IncludeBresil) {
    $ExcludePays = ""
}

Write-Host "Simulateur capteurs -> Aiven (pays=$Pays, exclude=$ExcludePays)" -ForegroundColor Cyan
Write-Host "Affichage + insert BDD : 30 s | Arret : Ctrl+C ou npm run sim:stop" -ForegroundColor DarkGray

$env:PYTHONIOENCODING = 'utf-8'
$args = @("--pays", $Pays, "--interval", "30")
if ($ExcludePays) {
    $args += @("--exclude-pays", $ExcludePays)
}
python -u scripts/simulate_releves_aiven.py @args

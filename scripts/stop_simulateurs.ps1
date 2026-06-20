# Arrête tous les simulateurs Aiven en cours (évite les doublons BR / EC / CO).
# Usage : npm run sim:stop

$ErrorActionPreference = "SilentlyContinue"

$procs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -match 'simulate_releves_aiven\.py' }

if (-not $procs) {
    Write-Host "Aucun simulateur en cours." -ForegroundColor DarkGray
    exit 0
}

foreach ($p in $procs) {
    Write-Host "Arret PID $($p.ProcessId) : $($p.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $p.ProcessId -Force
}

Write-Host "Simulateurs arretes." -ForegroundColor Green

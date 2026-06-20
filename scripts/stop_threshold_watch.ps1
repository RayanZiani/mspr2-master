$procs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "threshold_watch_aiven\.py" }

if (-not $procs) {
    Write-Host "Aucune surveillance seuils en cours." -ForegroundColor DarkGray
    exit 0
}

foreach ($p in $procs) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "Arret PID $($p.ProcessId)" -ForegroundColor Yellow
}

Write-Host "Surveillance seuils arretee." -ForegroundColor Green

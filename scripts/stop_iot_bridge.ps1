$patterns = @(
    "mqtt_bridge_bresil\.py",
    "serial_mqtt_bridge_bresil\.py"
)

$procs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $cmd = $_.CommandLine
        $patterns | Where-Object { $cmd -match $_ }
    }

if (-not $procs) {
    Write-Host "Aucun pont IoT (MQTT/serie) en cours." -ForegroundColor DarkGray
    exit 0
}

foreach ($p in $procs) {
    Write-Host "Arret PID $($p.ProcessId) : $($p.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "Ponts IoT arretes." -ForegroundColor Green

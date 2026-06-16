$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

function Wait-Url([string]$Url, [string]$Label, [int]$Retries = 60) {
    Write-Host "Attente $Label ($Url)..."
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            Write-Host "OK: $Label"
            return
        } catch {
            Start-Sleep -Seconds 5
        }
    }
    throw "ERREUR: $Label indisponible après $($Retries * 5)s"
}

Wait-Url 'http://localhost:8001/health' 'API Brésil'
Wait-Url 'http://localhost:8002/health' 'API Équateur'
Wait-Url 'http://localhost:8003/health' 'API Colombie'
Wait-Url 'http://localhost/api/health' 'API Siège'
Wait-Url 'http://localhost/' 'Frontend Siège'

Write-Host 'Stack FutureKawa prête pour les tests.'

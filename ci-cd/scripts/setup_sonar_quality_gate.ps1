# Quality Gate SonarQube MSPR niveau 3 — version PowerShell (Windows)
# Usage :
#   $env:SONAR_TOKEN = "squ_..."   # User Token ADMIN (pas Global Analysis Token)
#   .\ci-cd\scripts\setup_sonar_quality_gate.ps1

param(
    [string]$SonarHost = "http://localhost:9000"
)

$ErrorActionPreference = "Stop"

if (-not $env:SONAR_TOKEN) {
    Write-Error "SONAR_TOKEN requis. Genere un User Token admin : SonarQube > My Account > Security > Generate Token > Type: User Token"
}

$GateName = "FutureKawa CI"
$ProjectKey = "futurekawa"
$Headers = @{ Authorization = "Bearer $env:SONAR_TOKEN" }

function Invoke-SonarPost($Url, $Body) {
    Invoke-RestMethod -Uri $Url -Method Post -Headers $Headers -Body $Body
}

Write-Host "=== Creation Quality Gate : $GateName ==="
try {
    Invoke-SonarPost "$SonarHost/api/qualitygates/create?name=$([uri]::EscapeDataString($GateName))" @{}
} catch {
    Write-Host "  (gate deja existante ou erreur ignoree)"
}

Write-Host "=== Suppression des conditions existantes ==="
$show = Invoke-RestMethod -Uri "$SonarHost/api/qualitygates/show?name=$([uri]::EscapeDataString($GateName))" -Headers $Headers
foreach ($cond in $show.conditions) {
    Invoke-SonarPost "$SonarHost/api/qualitygates/delete_condition?id=$($cond.id)" @{}
    Write-Host "  - condition supprimee: $($cond.id)"
}

Write-Host "=== Ajout des conditions MSPR (niveau 3) ==="
$conditions = @(
    @{ metric = "security_rating"; op = "GT"; error = "1" },
    @{ metric = "sqale_rating"; op = "GT"; error = "1" },
    @{ metric = "reliability_rating"; op = "GT"; error = "3" },
    @{ metric = "coverage"; op = "LT"; error = "50" },
    @{ metric = "duplicated_lines_density"; op = "GT"; error = "25" },
    @{ metric = "security_hotspots_reviewed"; op = "LT"; error = "100" }
)

foreach ($c in $conditions) {
    $body = @{
        gateName = $GateName
        metric   = $c.metric
        op       = $c.op
        error    = $c.error
    }
    Invoke-SonarPost "$SonarHost/api/qualitygates/create_condition" $body
    Write-Host "  + $($c.metric) $($c.op) $($c.error)"
}

Write-Host "=== Association au projet $ProjectKey ==="
Invoke-SonarPost "$SonarHost/api/qualitygates/select?projectKey=$ProjectKey&gateName=$([uri]::EscapeDataString($GateName))" @{}

Write-Host ""
Write-Host "Quality Gate '$GateName' configuree avec 6 conditions bloquantes."
Write-Host "1. SonarQube > Security Hotspots > revoir les points (Safe ou Fixed)"
Write-Host "2. Jenkins > Build Now"
Write-Host "3. Verifier http://localhost:9000/dashboard?id=$ProjectKey"

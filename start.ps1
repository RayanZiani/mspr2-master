# Lance toute l'application FutureKawa (3 pays + siège) en une commande.
# Usage : .\start.ps1          (logs en direct)
#         .\start.ps1 -Detached (arrière-plan)

param([switch]$Detached)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

node scripts/ensure-env.mjs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Detached) {
  docker compose up --build -d
  Write-Host ""
  Write-Host "Application démarrée : http://localhost"
  Write-Host "Arrêt : npm run stop  ou  docker compose down"
} else {
  docker compose up --build
}

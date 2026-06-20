# Vide les relevés température/humidité sur Aiven (table releve_capteur).
# Conserve lots, entrepôts, capteurs, alertes.
#
# Usage :
#   powershell -File scripts/clear_releve_capteur_aiven.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

python scripts/clear_releve_capteur_aiven.py
exit $LASTEXITCODE

# Vide les relevés température/humidité sur Aiven (table releve_capteur).
# Conserve lots, entrepôts, capteurs, alertes.
#
# Usage :
#   powershell -File scripts/clear_releve_capteur_aiven.ps1
#   powershell -File scripts/clear_releve_capteur_aiven.ps1 -Pays BR

param(
    [ValidateSet("", "BR", "EC", "CO")]
    [string]$Pays = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

$args = @()
if ($Pays) {
    $args += @("--pays", $Pays)
}

python scripts/clear_releve_capteur_aiven.py @args
exit $LASTEXITCODE

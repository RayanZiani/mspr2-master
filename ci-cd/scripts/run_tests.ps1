param(
    [ValidateSet('unit', 'integration', 'api', 'e2e', 'all')]
    [string]$Mode = 'all'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

New-Item -ItemType Directory -Force -Path tests/reports, tests/e2e/.auth | Out-Null

function Install-PythonDeps {
    python -m pip install --upgrade pip -q
    python -m pip install -r tests/requirements.txt -q
    python -m pip install -r pays/bresil/api/requirements.txt -q
    python -m pip install -r siege/api/requirements.txt -q 2>$null
}

function Invoke-UnitTests {
    Push-Location tests
    python -m pytest unit/ -v -m unit `
        --junitxml=reports/unit-results.xml `
        --alluredir=reports/allure-results `
        --cov=../pays/bresil/api/services `
        --cov=../pays/equateur/api/services `
        --cov=../pays/colombie/api/services `
        --cov=../siege/api/services `
        --cov-report=xml:reports/coverage.xml `
        --cov-report=html:reports/htmlcov `
        --cov-report=term-missing
    Pop-Location
}

function Invoke-IntegrationTests {
    Push-Location tests
    python -m pytest integration/ -v -m integration `
        --junitxml=reports/integration-results.xml `
        --alluredir=reports/allure-results
    Pop-Location
}

function Invoke-ApiTests {
    npx newman run tests/api/FutureKawa.postman_collection.json `
        --environment tests/api/FutureKawa.postman_environment.json `
        --reporters cli,junit `
        --reporter-junit-export tests/reports/newman-results.xml
}

function Invoke-E2eTests {
    npx playwright install chromium
    Push-Location tests/e2e
    npx playwright test
    Pop-Location
}

Install-PythonDeps

switch ($Mode) {
    'unit' { Invoke-UnitTests }
    'integration' { Invoke-IntegrationTests }
    'api' { Invoke-ApiTests }
    'e2e' { Invoke-E2eTests }
    'all' {
        Invoke-UnitTests
        Invoke-IntegrationTests
        Invoke-ApiTests
        Invoke-E2eTests
    }
}

Write-Host "Tests $Mode terminés."

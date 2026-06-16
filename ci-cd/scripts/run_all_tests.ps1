$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

Write-Host "=== 1/7 Stack Docker ===" -ForegroundColor Cyan
$prevErrorAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
docker compose up -d --build api-siege api-bresil api-equateur api-colombie nginx 2>&1 | ForEach-Object { Write-Host $_ }
$dockerExit = $LASTEXITCODE
$ErrorActionPreference = $prevErrorAction
if ($dockerExit -ne 0) { throw "docker compose a échoué (code $dockerExit)" }
powershell -ExecutionPolicy Bypass -File ci-cd/scripts/wait_for_stack.ps1

Write-Host "=== 2/7 Tests unitaires (Docker Python 3.11) ===" -ForegroundColor Cyan
docker run --rm -v "${Root}:/workspace" -w /workspace/tests python:3.11-slim `
  bash -c "pip install -q -r requirements.txt -r ../pays/bresil/api/requirements.txt -r ../siege/api/requirements.txt && python -m pytest unit/ -m unit -v --junitxml=reports/unit-results.xml"

Write-Host "=== 3/7 Tests integration ===" -ForegroundColor Cyan
Set-Location tests
python -m pytest integration/ -m integration -v --junitxml=reports/integration-results.xml
Set-Location $Root

Write-Host "=== 4/7 Tests API Newman ===" -ForegroundColor Cyan
npx newman run tests/api/FutureKawa.postman_collection.json `
  --environment tests/api/FutureKawa.postman_environment.json `
  --reporters cli,junit `
  --reporter-junit-export tests/reports/newman-results.xml

Write-Host "=== 5/7 Tests E2E Playwright ===" -ForegroundColor Cyan
Push-Location tests/e2e
npx playwright test
Pop-Location

Write-Host "=== 6/7 Lint Python (flake8) ===" -ForegroundColor Cyan
npm run lint

Write-Host "=== 7/7 Analyse statique (Bandit) ===" -ForegroundColor Cyan
docker run --rm -v "${Root}:/workspace" -w /workspace python:3.11-slim `
  bash -c "pip install -q bandit pylint && bash ci-cd/scripts/run_static_analysis.sh"

Write-Host "=== Tous les tests terminés ===" -ForegroundColor Green

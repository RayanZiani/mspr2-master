#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-all}"
mkdir -p tests/reports tests/e2e/.auth

install_python_deps() {
  python3 -m pip install -r tests/requirements.txt -q --break-system-packages
}

install_api_deps() {
  python3 -m pip install -r tests/requirements-api-runtime.txt -q --break-system-packages
}

run_unit_tests() {
  echo "=== Tests unitaires (pytest directement dans Jenkins) ==="
  install_api_deps
  python3 -m pytest tests/unit/ -v -m unit \
    --cov-config=.coveragerc \
    --cov=. \
    --junitxml=tests/reports/unit-results.xml \
    --alluredir=tests/reports/allure-results \
    --cov-report=xml:tests/reports/coverage.xml \
    --cov-report=html:tests/reports/htmlcov \
    --cov-report=term-missing
}

run_unit_tests_local() {
  echo "=== Tests unitaires (pytest local) ==="
  install_python_deps
  install_api_deps
  python3 -m pytest tests/unit/ -v -m unit \
    --cov-config=.coveragerc \
    --cov=. \
    --junitxml=tests/reports/unit-results.xml \
    --alluredir=tests/reports/allure-results \
    --cov-report=xml:tests/reports/coverage.xml \
    --cov-report=html:tests/reports/htmlcov \
    --cov-report=term-missing
}

run_integration_tests() {
  echo "=== Tests d'intégration (pytest + httpx) ==="
  if [ -n "${RENDER:-}" ]; then
    echo "Mode Render : agrégation via API Siège (${API_SIEGE_URL:-https://mspr2-master.onrender.com})"
  else
    echo "Mode Docker : APIs pays directes + API Siège"
  fi
  python3 -m pytest tests/integration/ -v -m integration \
    --junitxml=tests/reports/integration-results.xml \
    --alluredir=tests/reports/allure-results \
    -ra
}

run_api_tests() {
  echo "=== Tests API (Newman / Postman) ==="
  local env_file="tests/api/FutureKawa.postman_environment.json"
  local newman_args=(
  )

  if [ -n "${RENDER:-}" ]; then
    env_file="tests/api/FutureKawa.postman_environment.render.json"
    echo "Mode Render : API Siège sur ${API_SIEGE_URL:-https://mspr2-master.onrender.com}"
    newman_args+=(--folder "Siège")
  else
    echo "Mode local Docker : toutes les APIs"
  fi

  npx newman run tests/api/FutureKawa.postman_collection.json \
    --environment "$env_file" \
    "${newman_args[@]}" \
    --env-var "API_SIEGE_URL=${API_SIEGE_URL:-}" \
    --reporters cli,junit \
    --reporter-junit-export tests/reports/newman-results.xml
}

run_e2e_tests() {
  if [ "${SKIP_E2E:-false}" = "true" ]; then
    echo "ERREUR: SKIP_E2E=true — les tests E2E sont obligatoires dans le pipeline CI"
    exit 1
  fi
  echo "=== Tests E2E (Playwright) ==="
  export E2E_BASE_URL="${E2E_BASE_URL:-${FRONTEND_URL:-http://localhost:80}}"
  echo "E2E base URL: ${E2E_BASE_URL}"
  if echo "${E2E_BASE_URL}" | grep -qi onrender; then
    echo "Mode Render : retries activés pour cold start"
  fi
  bash ci-cd/scripts/install_playwright_deps.sh
  npx playwright install chromium
  cd tests/e2e
  npx playwright test
}

install_python_deps

case "$MODE" in
  unit) run_unit_tests ;;
  integration) run_integration_tests ;;
  api) run_api_tests ;;
  e2e) run_e2e_tests ;;
  all)
    run_unit_tests
    run_integration_tests
    run_api_tests
    run_e2e_tests
    ;;
  *)
    echo "Usage: $0 [unit|integration|api|e2e|all]"
    exit 1
    ;;
esac

#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-all}"
mkdir -p tests/reports tests/e2e/.auth

install_python_deps() {
  python3 -m pip install -r tests/requirements.txt -q --break-system-packages
}

run_unit_tests() {
  echo "=== Tests unitaires (pytest via Docker Python 3.11) ==="
  docker run --rm -v "$ROOT_DIR:/workspace" -w /workspace/tests python:3.11-slim \
    bash -c "pip install -q -r requirements.txt -r ../pays/bresil/api/requirements.txt -r ../siege/api/requirements.txt \
      && python -m pytest unit/ -v -m unit \
      --junitxml=reports/unit-results.xml \
      --alluredir=reports/allure-results \
      --cov=../pays/bresil/api/services \
      --cov=../pays/equateur/api/services \
      --cov=../pays/colombie/api/services \
      --cov=../siege/api/services \
      --cov-report=xml:reports/coverage.xml \
      --cov-report=html:reports/htmlcov \
      --cov-report=term-missing"
}

run_unit_tests_local() {
  echo "=== Tests unitaires (pytest local) ==="
  install_python_deps
  python3 -m pip install -r pays/bresil/api/requirements.txt -q --break-system-packages
  python3 -m pip install -r siege/api/requirements.txt -q --break-system-packages
  cd tests
  python3 -m pytest unit/ -v -m unit \
    --junitxml=reports/unit-results.xml \
    --alluredir=reports/allure-results \
    --cov=../pays/bresil/api/services \
    --cov=../pays/equateur/api/services \
    --cov=../pays/colombie/api/services \
    --cov=../siege/api/services \
    --cov-report=xml:reports/coverage.xml \
    --cov-report=html:reports/htmlcov \
    --cov-report=term-missing
}

run_integration_tests() {
  echo "=== Tests d'intégration (pytest + httpx) ==="
  cd tests
  python3 -m pytest integration/ -v -m integration \
    --junitxml=reports/integration-results.xml \
    --alluredir=reports/allure-results
}

run_api_tests() {
  echo "=== Tests API (Newman / Postman) ==="
  npx newman run tests/api/FutureKawa.postman_collection.json \
    --environment tests/api/FutureKawa.postman_environment.json \
    --reporters cli,junit \
    --reporter-junit-export tests/reports/newman-results.xml
}

run_e2e_tests() {
  echo "=== Tests E2E (Playwright) ==="
  npx playwright install chromium || true
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

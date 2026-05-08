#!/bin/bash
set -e

echo "=== Tests unitaires ==="
cd tests
python -m pytest unit/ -v --junitxml=reports/unit-results.xml --cov=../pays/bresil/api --cov-report=xml:reports/coverage.xml

echo "=== Tests E2E Playwright ==="
npx playwright test e2e/specs/ --reporter=junit --output=reports/e2e-results.xml

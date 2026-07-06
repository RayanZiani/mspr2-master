#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p tests/reports

echo "=== Pylint ==="
: > tests/reports/pylint-report.txt
for api_path in pays/bresil/api pays/equateur/api pays/colombie/api siege/api; do
  api_parent="$(dirname "$api_path")"
  echo "=== ${api_path} ===" >> tests/reports/pylint-report.txt
  pylint "$api_path" \
    --rcfile=.pylintrc \
    --init-hook="import sys; sys.path.insert(0, '${ROOT_DIR}/${api_parent}')" \
    --output-format=parseable \
    --exit-zero \
    >> tests/reports/pylint-report.txt || true
done

echo "=== Bandit (sécurité Python) ==="
bandit -r pays/bresil/api pays/equateur/api pays/colombie/api siege/api \
  -f json \
  -o tests/reports/bandit-report.json \
  --exit-zero

python3 - <<'PY'
import json
import sys

with open("tests/reports/bandit-report.json", encoding="utf-8") as f:
    data = json.load(f)

high = [r for r in data.get("results", []) if r.get("issue_severity") == "HIGH"]
if high:
    print(f"BANDIT: {len(high)} vulnérabilité(s) HIGH")
    for item in high[:5]:
        print("-", item.get("issue_text"))
    sys.exit(1)
print("BANDIT: aucune vulnérabilité HIGH")
PY

echo "Analyse statique terminée."

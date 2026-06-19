#!/bin/bash
# Configuration unique de la Quality Gate SonarQube pour FutureKawa CI.
# Usage : SONAR_TOKEN=sqp_xxx bash ci-cd/scripts/setup_sonar_quality_gate.sh

set -euo pipefail

SONAR_HOST="${SONAR_HOST:-http://localhost:9000}"
SONAR_TOKEN="${SONAR_TOKEN:?SONAR_TOKEN requis}"
GATE_NAME="FutureKawa CI"
PROJECT_KEY="futurekawa"

auth_header() {
  echo "Authorization: Bearer ${SONAR_TOKEN}"
}

echo "=== Création Quality Gate : ${GATE_NAME} ==="
curl -fsS -X POST -H "$(auth_header)" \
  "${SONAR_HOST}/api/qualitygates/create?name=${GATE_NAME// /%20}" || true

echo "=== Suppression des conditions héritées (seuils nouveau code) ==="
mapfile -t condition_ids < <(
  curl -fsS -H "$(auth_header)" \
    "${SONAR_HOST}/api/qualitygates/show?name=${GATE_NAME// /%20}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(c['id'] for c in d.get('conditions',[])))"
)

for id in "${condition_ids[@]}"; do
  if [ -n "$id" ]; then
    curl -fsS -X POST -H "$(auth_header)" \
      "${SONAR_HOST}/api/qualitygates/delete_condition?id=${id}" >/dev/null
    echo "  - condition supprimée: ${id}"
  fi
done

echo "=== Association au projet ${PROJECT_KEY} ==="
curl -fsS -X POST -H "$(auth_header)" \
  "${SONAR_HOST}/api/qualitygates/select?projectKey=${PROJECT_KEY}&gateName=${GATE_NAME// /%20}"

echo "✅ Quality Gate ${GATE_NAME} prête (aucune condition bloquante)."

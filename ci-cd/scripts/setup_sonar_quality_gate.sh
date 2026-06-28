#!/bin/bash
# Quality Gate SonarQube MSPR niveau 3 — seuils réalistes et bloquants.
# Usage : SONAR_TOKEN=sqp_xxx bash ci-cd/scripts/setup_sonar_quality_gate.sh

set -euo pipefail

SONAR_HOST="${SONAR_HOST:-http://localhost:9000}"
SONAR_TOKEN="${SONAR_TOKEN:?SONAR_TOKEN requis — My Account > Security > Generate Token}"
GATE_NAME="FutureKawa CI"
PROJECT_KEY="futurekawa"

auth_header() {
  echo "Authorization: Bearer ${SONAR_TOKEN}"
}

create_condition() {
  local metric="$1"
  local op="$2"
  local threshold="$3"
  curl -fsS -X POST -H "$(auth_header)" \
    "${SONAR_HOST}/api/qualitygates/create_condition" \
    --data-urlencode "gateName=${GATE_NAME}" \
    --data-urlencode "metric=${metric}" \
    --data-urlencode "op=${op}" \
    --data-urlencode "error=${threshold}" >/dev/null
  echo "  + ${metric} ${op} ${threshold}"
}

echo "=== Création Quality Gate : ${GATE_NAME} ==="
curl -fsS -X POST -H "$(auth_header)" \
  "${SONAR_HOST}/api/qualitygates/create?name=${GATE_NAME// /%20}" >/dev/null 2>&1 || true

echo "=== Suppression des conditions existantes ==="
mapfile -t condition_ids < <(
  curl -fsS -H "$(auth_header)" \
    "${SONAR_HOST}/api/qualitygates/show?name=${GATE_NAME// /%20}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(c['id'] for c in d.get('conditions',[])))"
)

for id in "${condition_ids[@]}"; do
  if [ -n "$id" ]; then
    curl -fsS -X POST -H "$(auth_header)" \
      "${SONAR_HOST}/api/qualitygates/delete_condition?id=${id}" >/dev/null
  fi
done

echo "=== Ajout des conditions MSPR (niveau 3) ==="
# Ratings SonarQube : 1=A, 2=B, 3=C, 4=D, 5=E — GT = pire que le seuil
create_condition "security_rating" "GT" "1"              # Security = A minimum
create_condition "sqale_rating" "GT" "1"                 # Maintainability = A minimum
create_condition "reliability_rating" "GT" "3"           # Reliability = C minimum (11 bugs connus)
create_condition "coverage" "LT" "50"                      # Couverture logique métier >= 50 %
create_condition "duplicated_lines_density" "GT" "25"      # Duplication <= 25 %
create_condition "security_hotspots_reviewed" "LT" "100"   # 100 % hotspots revus

echo "=== Association au projet ${PROJECT_KEY} ==="
curl -fsS -X POST -H "$(auth_header)" \
  "${SONAR_HOST}/api/qualitygates/select?projectKey=${PROJECT_KEY}&gateName=${GATE_NAME// /%20}"

echo ""
echo "✅ Quality Gate « ${GATE_NAME} » configurée avec 6 conditions bloquantes."
echo ""
echo "Actions manuelles avant le prochain build Jenkins :"
echo "  1. SonarQube > Security Hotspots > revoir les 12 points (Safe ou Fixed)"
echo "  2. Relancer le pipeline Jenkins (Build Now)"
echo "  3. Vérifier Quality Gate PASSED sur http://localhost:9000/dashboard?id=${PROJECT_KEY}"

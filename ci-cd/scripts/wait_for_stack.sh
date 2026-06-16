#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p tests/reports

# Détection de l'environnement
if [ -n "${RENDER:-}" ]; then
  # Production sur Render - utiliser les URLs publiques
  BASE_URL="${BASE_URL:-https://futurekawa.onrender.com}"
  API_BRESIL="${API_BRESIL_URL:-https://api-bresil.onrender.com}"
  API_EQUATEUR="${API_EQUATEUR_URL:-https://api-equateur.onrender.com}"
  API_COLOMBIE="${API_COLOMBIE_URL:-https://api-colombie.onrender.com}"
  CHECK_FRONTEND=true
elif [ -n "${CI:-}" ] || docker info >/dev/null 2>&1; then
  # CI/CD ou environnement Docker - utiliser host.docker.internal
  BASE_URL="http://host.docker.internal"
  API_BRESIL="http://host.docker.internal:8001"
  API_EQUATEUR="http://host.docker.internal:8002"
  API_COLOMBIE="http://host.docker.internal:8003"
  CHECK_FRONTEND=false
else
  # Développement local - utiliser localhost
  BASE_URL="http://127.0.0.1"
  API_BRESIL="http://127.0.0.1:8001"
  API_EQUATEUR="http://127.0.0.1:8002"
  API_COLOMBIE="http://127.0.0.1:8003"
  CHECK_FRONTEND=true
fi

wait_for_url() {
  local url="$1"
  local label="$2"
  local retries="${3:-120}"

  echo "Attente $label ($url)..."
  for i in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "OK: $label"
      return 0
    fi
    sleep 5
  done

  echo "ERREUR: $label indisponible après $((retries * 5))s"
  return 1
}

wait_for_url "${API_BRESIL}/health" "API Brésil"
wait_for_url "${API_EQUATEUR}/health" "API Équateur"
wait_for_url "${API_COLOMBIE}/health" "API Colombie"
wait_for_url "${BASE_URL}/api/health" "API Siège"

if [ "$CHECK_FRONTEND" = true ]; then
  wait_for_url "${BASE_URL}/" "Frontend Siège"
else
  echo "OK: Frontend Siège (skip en mode dev Docker)"
fi

echo "Stack FutureKawa prête pour les tests d'intégration."

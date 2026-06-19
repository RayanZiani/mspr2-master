#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p tests/reports

# Détection de l'environnement
if [ -n "${RENDER:-}" ]; then
  # Production sur Render - utiliser les URLs publiques réelles
  API_SIEGE="${API_SIEGE_URL:-https://mspr2-master.onrender.com}"
  FRONTEND="${FRONTEND_URL:-https://mspr2-master-front.onrender.com}"
  CHECK_FRONTEND=true
  # Sur Render, seul le backend centralisé est déployé (pas les APIs pays séparées)
  SKIP_COUNTRY_APIS=true
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

# Vérifier les APIs pays seulement si déployées séparément (Docker local)
if [ "${SKIP_COUNTRY_APIS:-false}" != "true" ]; then
  wait_for_url "${API_BRESIL}/health" "API Brésil"
  wait_for_url "${API_EQUATEUR}/health" "API Équateur"
  wait_for_url "${API_COLOMBIE}/health" "API Colombie"
fi

# Vérifier l'API Siège (backend principal)
if [ -n "${RENDER:-}" ]; then
  # Sur Render, vérifier directement l'API Siège et un endpoint avec auth
  wait_for_url "${API_SIEGE}/health" "API Siège (Health)"
  
  # Vérifier aussi que l'API docs est accessible (endpoint public)
  wait_for_url "${API_SIEGE}/docs" "API Siège (Docs)"
  
  # Vérifier le frontend
  if [ "$CHECK_FRONTEND" = true ]; then
    wait_for_url "${FRONTEND}/" "Frontend Siège"
  fi
else
  # En local Docker, utiliser BASE_URL/api
  wait_for_url "${BASE_URL}/api/health" "API Siège"
  
  if [ "$CHECK_FRONTEND" = true ]; then
    wait_for_url "${BASE_URL}/" "Frontend Siège"
  else
    echo "OK: Frontend Siège (skip en mode dev Docker)"
  fi
fi

echo "✅ Stack FutureKawa prête pour les tests d'intégration."

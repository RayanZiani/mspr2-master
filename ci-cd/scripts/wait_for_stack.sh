#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p tests/reports

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

wait_for_url "http://127.0.0.1:8001/health" "API Brésil"
wait_for_url "http://127.0.0.1:8002/health" "API Équateur"
wait_for_url "http://127.0.0.1:8003/health" "API Colombie"
wait_for_url "http://127.0.0.1/api/health" "API Siège"
wait_for_url "http://127.0.0.1/" "Frontend Siège"

echo "Stack FutureKawa prête pour les tests d'intégration."

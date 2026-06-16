#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
REGISTRY="${DOCKER_REGISTRY:-}"
PAYS=(bresil equateur colombie)

login_if_needed() {
  if [ -n "${DOCKER_HUB_CREDENTIALS:-}" ]; then
    echo "$DOCKER_HUB_CREDENTIALS" | docker login -u "${DOCKER_HUB_USER:-}" --password-stdin
  fi
}

build_and_push() {
  local image_name="$1"
  local context="$2"

  local tag="${image_name}:${IMAGE_TAG}"
  if [ -n "$REGISTRY" ]; then
    tag="${REGISTRY}/${tag}"
  fi

  echo "Build image $tag"
  docker build -t "$tag" "$context"
  docker push "$tag"
}

login_if_needed

for pays in "${PAYS[@]}"; do
  build_and_push "futurekawa-${pays}" "pays/${pays}/api"
done

build_and_push "futurekawa-siege-api" "siege/api"
build_and_push "futurekawa-siege-front" "siege/frontend"

echo "Images Docker publiées avec le tag ${IMAGE_TAG}"

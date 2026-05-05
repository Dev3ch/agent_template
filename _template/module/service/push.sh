#!/usr/bin/env bash
# Push de la imagen al registry.
set -euo pipefail

MODULE="{{MODULE_NAME}}"
TAG="${TAG:-latest}"
REGISTRY_PREFIX="${REGISTRY_PREFIX:-docker.io/dev3ch}"
IMAGE="${REGISTRY_PREFIX}/${MODULE}-service:${TAG}"

if [ -f .env ]; then
    set -a; source .env; set +a
fi

# Login a Docker Hub si hay creds
if [ -n "${DOCKERHUB_USERNAME:-}" ] && [ -n "${DOCKERHUB_TOKEN:-}" ]; then
    echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
fi

echo "→ Pushing $IMAGE"
docker push "$IMAGE"
echo "✔ Imagen pusheada: $IMAGE"

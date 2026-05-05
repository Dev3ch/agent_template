#!/usr/bin/env bash
# Build de la imagen del módulo {{MODULE_NAME}}.
# Corre desde la raíz del monorepo.
set -euo pipefail

MODULE="{{MODULE_NAME}}"
TAG="${TAG:-latest}"
REGISTRY_PREFIX="${REGISTRY_PREFIX:-docker.io/dev3ch}"
IMAGE="${REGISTRY_PREFIX}/${MODULE}-service:${TAG}"

# Cargar .env raíz si existe
if [ -f .env ]; then
    set -a; source .env; set +a
fi

echo "→ Building $IMAGE"
docker build -f "${MODULE}/service/Dockerfile" -t "$IMAGE" .
echo "✔ Imagen lista: $IMAGE"

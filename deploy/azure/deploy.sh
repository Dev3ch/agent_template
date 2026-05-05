#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Deploy de un módulo a Azure Container Apps.
#
# Uso:
#   ./deploy/azure/deploy.sh <modulo>            # tag :latest
#   ./deploy/azure/deploy.sh <modulo> v0.2.0     # tag específico
#
# Requiere:
#   - Imagen ya pushada al registry: ./<modulo>/service/push.sh
#   - az login hecho previamente
#   - .env raíz + <modulo>/service/.env con variables.
# ─────────────────────────────────────────────
set -euo pipefail

MODULE="${1:?Uso: $0 <modulo> [tag]}"
TAG="${2:-latest}"

if [ ! -d "$MODULE/service" ]; then
  echo "✗ El módulo '$MODULE' no tiene service/. Es un módulo de agentes solo n8n?"
  exit 1
fi

# Cargar .env raíz + .env del módulo (override).
[ -f .env ] && { set -a; source .env; set +a; }
[ -f "$MODULE/service/.env" ] && { set -a; source "$MODULE/service/.env"; set +a; }

REGISTRY_PREFIX="${REGISTRY_PREFIX:-docker.io/dev3ch}"
APP_NAME="${MODULE}-service"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:?AZURE_RESOURCE_GROUP requerido}"
LOCATION="${AZURE_LOCATION:-southcentralus}"
ENVIRONMENT="${AZURE_CONTAINERAPPS_ENV:-agents-env}"
IMAGE="${REGISTRY_PREFIX}/${MODULE}-service:${TAG}"
PORT="${SERVICE_PORT:-8000}"

# Convertir el .env del módulo + algunas vars raíz en --env-vars KEY=VALUE
ENV_ARGS=()
collect_env() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    [[ -z "$value" ]] && continue
    ENV_ARGS+=("${key}=${value}")
  done < <(grep -v '^\s*#' "$file" | grep -v '^\s*$')
}
collect_env .env
collect_env "$MODULE/service/.env"

# Forzar modelo de prod
ENV_ARGS+=("CLAUDE_MODEL=${CLAUDE_MODEL_PROD:-claude-sonnet-4-6}")

echo "▸ Deploy ${APP_NAME} (imagen: ${IMAGE})"

if az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  echo "  → Container app existe, update..."
  az containerapp update \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$IMAGE" \
    --set-env-vars "${ENV_ARGS[@]}"
else
  echo "  → Container app no existe, creando..."
  az containerapp create \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$ENVIRONMENT" \
    --image "$IMAGE" \
    --target-port "$PORT" \
    --ingress external \
    --min-replicas 0 \
    --max-replicas 1 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars "${ENV_ARGS[@]}"
fi

URL=$(az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query 'properties.configuration.ingress.fqdn' -o tsv)

echo ""
echo "✓ Módulo $MODULE desplegado"
echo "  URL:    https://${URL}"
echo "  Health: https://${URL}/health"
echo "  Agentes: https://${URL}/agents"

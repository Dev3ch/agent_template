#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Deploy de un módulo a Google Cloud Run.
#
# Uso:
#   ./deploy/gcp/deploy.sh <modulo>            # tag :latest
#   ./deploy/gcp/deploy.sh <modulo> v0.2.0
# ─────────────────────────────────────────────
set -euo pipefail

MODULE="${1:?Uso: $0 <modulo> [tag]}"
TAG="${2:-latest}"

if [ ! -d "$MODULE/service" ]; then
  echo "✗ El módulo '$MODULE' no tiene service/."
  exit 1
fi

[ -f .env ] && { set -a; source .env; set +a; }
[ -f "$MODULE/service/.env" ] && { set -a; source "$MODULE/service/.env"; set +a; }

APP_NAME="${MODULE}-service"
GCP_PROJECT="${GCP_PROJECT:?GCP_PROJECT requerido}"
GCP_REGION="${GCP_REGION:-us-central1}"
GAR_REGION="${GAR_REGION:-$GCP_REGION}"
GAR_REPOSITORY="${GAR_REPOSITORY:-agents}"
PORT="${SERVICE_PORT:-8000}"
IMAGE_URI="${GAR_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPOSITORY}/${APP_NAME}:${TAG}"

# ENV_VARS para Cloud Run
ENV_VARS=""
SEP=""
collect_env() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    [[ -z "$value" ]] && continue
    ENV_VARS+="${SEP}${key}=${value}"
    SEP=","
  done < <(grep -v '^\s*#' "$file" | grep -v '^\s*$')
}
collect_env .env
collect_env "$MODULE/service/.env"
ENV_VARS+="${SEP}CLAUDE_MODEL=${CLAUDE_MODEL_PROD:-claude-sonnet-4-6}"

echo "▸ Deploy ${APP_NAME} a Cloud Run (imagen: ${IMAGE_URI})"

gcloud run deploy "$APP_NAME" \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --image "$IMAGE_URI" \
  --port "$PORT" \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --cpu 1 \
  --memory 1Gi \
  --set-env-vars "$ENV_VARS"

URL=$(gcloud run services describe "$APP_NAME" \
  --project "$GCP_PROJECT" \
  --region "$GCP_REGION" \
  --format='value(status.url)')

echo ""
echo "✓ Módulo $MODULE desplegado"
echo "  URL:    ${URL}"
echo "  Health: ${URL}/health"

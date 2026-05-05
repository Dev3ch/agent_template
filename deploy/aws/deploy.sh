#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Deploy de un módulo a AWS App Runner.
#
# Uso:
#   ./deploy/aws/deploy.sh <modulo>            # tag :latest
#   ./deploy/aws/deploy.sh <modulo> v0.2.0
#
# Requiere:
#   - aws cli configurado.
#   - Imagen pushada a ECR.
#   - .env raíz + <modulo>/service/.env.
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
AWS_REGION="${AWS_REGION:?AWS_REGION requerido}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID requerido}"
ECR_REPOSITORY="${ECR_REPOSITORY:-$APP_NAME}"
PORT="${SERVICE_PORT:-8000}"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${TAG}"

# Construir ENV_JSON desde .env raíz + .env del módulo
ENV_JSON="{"
FIRST=1
collect_env() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    [[ -z "$value" ]] && continue
    [[ $FIRST -eq 0 ]] && ENV_JSON+=","
    ENV_JSON+="\"${key}\":\"${value}\""
    FIRST=0
  done < <(grep -v '^\s*#' "$file" | grep -v '^\s*$')
}
collect_env .env
collect_env "$MODULE/service/.env"
[[ $FIRST -eq 0 ]] && ENV_JSON+=","
ENV_JSON+="\"CLAUDE_MODEL\":\"${CLAUDE_MODEL_PROD:-claude-sonnet-4-6}\"}"

echo "▸ Deploy ${APP_NAME} a App Runner (imagen: ${IMAGE_URI})"

SERVICE_ARN=$(aws apprunner list-services --region "$AWS_REGION" \
  --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceArn" \
  --output text)

if [ -n "$SERVICE_ARN" ]; then
  echo "  → Service existe, update..."
  aws apprunner update-service \
    --region "$AWS_REGION" \
    --service-arn "$SERVICE_ARN" \
    --source-configuration "ImageRepository={ImageIdentifier=${IMAGE_URI},ImageRepositoryType=ECR,ImageConfiguration={Port=${PORT},RuntimeEnvironmentVariables=${ENV_JSON}}}"
else
  echo "  → Service no existe, creando..."
  aws apprunner create-service \
    --region "$AWS_REGION" \
    --service-name "$APP_NAME" \
    --source-configuration "ImageRepository={ImageIdentifier=${IMAGE_URI},ImageRepositoryType=ECR,ImageConfiguration={Port=${PORT},RuntimeEnvironmentVariables=${ENV_JSON}}}" \
    --instance-configuration "Cpu=0.5 vCPU,Memory=1 GB"
fi

URL=$(aws apprunner list-services --region "$AWS_REGION" \
  --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceUrl" \
  --output text)

echo ""
echo "✓ Módulo $MODULE desplegado"
echo "  URL:    https://${URL}"
echo "  Health: https://${URL}/health"

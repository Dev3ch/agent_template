# {{MODULE_NAME}}/service

FastAPI compartido por todos los agentes tipo B/C del módulo.

## Levantar local

```bash
cd {{MODULE_NAME}}/service/
cp .env.example .env
uv sync
uv run uvicorn main:app --reload --port 8000
```

Probar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/agents
```

## Build & push

```bash
# Desde la raíz del monorepo
./{{MODULE_NAME}}/service/build.sh
./{{MODULE_NAME}}/service/push.sh
```

## Deploy

```bash
# Desde la raíz
./deploy/azure/deploy.sh {{MODULE_NAME}}
# o ./deploy/aws/deploy.sh {{MODULE_NAME}}
# o ./deploy/gcp/deploy.sh {{MODULE_NAME}}
```

El script de deploy lee `REGISTRY_PREFIX`, configura el container app y sobrescribe
`CLAUDE_MODEL=claude-sonnet-4-6` en producción.

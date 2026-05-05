# deploy/

Scripts de deploy por cloud. **Borrá las carpetas que no uses.**

Cada script recibe el **módulo** como primer argumento — así un solo monorepo
puede tener múltiples módulos desplegados como container apps independientes.

## Uso

```bash
./deploy/azure/deploy.sh marketing            # deploy marketing/service a Azure
./deploy/azure/deploy.sh sales v0.2.0         # con tag específico
./deploy/aws/deploy.sh finance
./deploy/gcp/deploy.sh customer-success
```

## Pre-requisitos

1. CLI del cloud autenticada (`az login`, `aws configure`, `gcloud auth login`).
2. Imagen pushada al registry: `./<modulo>/service/build.sh && ./<modulo>/service/push.sh`.
3. `.env` raíz + `<modulo>/service/.env` completos (con cuentas / region / project).

## Convenciones

- **App name**: `<modulo>-service` (ej: `marketing-service`, `sales-service`).
- **Modelo Claude**: el script sobrescribe a `claude-sonnet-4-6` en prod (usar
  `CLAUDE_MODEL_PROD` si querés cambiarlo).
- **Healthcheck**: el script verifica `/health` después del deploy.

## Cuándo NO necesitás deploy

Si **todos** los agentes del módulo son **tipo A (n8n-only)**, el módulo no tiene
`service/` y no hay nada que desplegar como container. Subí los workflows JSON a
n8n y listo.

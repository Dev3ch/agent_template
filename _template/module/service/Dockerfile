# Multi-stage build para service del módulo {{MODULE_NAME}}
# Build context: la RAÍZ del monorepo (no el directorio service/).
# Razón: necesitamos copiar `shared/` y `{{MODULE_NAME}}/` juntos.
#
# Build:  docker build -f {{MODULE_NAME}}/service/Dockerfile -t {{MODULE_NAME}}-service:latest .
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# uv para instalación rápida
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copiar shared y el módulo
COPY shared/ ./shared/
COPY {{MODULE_NAME}}/ ./{{MODULE_NAME}}/

# Instalar deps del service
WORKDIR /app/{{MODULE_NAME}}/service
RUN uv pip install --system -r pyproject.toml

# Healthcheck para Azure Container Apps / AWS / GCP
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

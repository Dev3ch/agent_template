"""Service FastAPI del módulo {{MODULE_NAME}}.

Expone:
  GET  /health                    — healthcheck (Azure / AWS / GCP)
  GET  /agents                    — lista agentes registrados
  POST /agents/{name}/run         — ejecuta el agente

Para registrar un agente: importar su módulo y llamar registry.register(...).
`make new-agent` agrega automáticamente el import + register cuando creás
agentes tipo B o C.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Permitir imports de `shared` y de los agentes del módulo cuando se corre local.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()  # carga {modulo}/service/.env
load_dotenv(ROOT / ".env")  # fallback al .env raíz

from shared.http_helpers import (
    AgentRegistry,
    health_router,
    register_agent_routes,
    setup_logging,
)

setup_logging(os.getenv("LOG_LEVEL", "INFO"))

# ── Registro de agentes ──────────────────────
# Importá acá los agentes tipo B/C de este módulo y registrálos.
#
# Ejemplo (descomenta cuando agregues agentes):
#
#     from {{MODULE_NAME}}.agents.example_agent import core as example_agent
#     registry.register("example-agent", example_agent.run)

registry = AgentRegistry()

# ── App ──────────────────────────────────────
app = FastAPI(
    title="{{MODULE_NAME}}-service",
    description="Service de agentes del módulo {{MODULE_NAME}}.",
    version="0.1.0",
)
app.include_router(health_router)
register_agent_routes(app, registry)

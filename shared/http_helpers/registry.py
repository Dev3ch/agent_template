"""Registry uniforme de agentes para el service de un módulo.

Uso en `{modulo}/service/main.py`:

    from shared.http_helpers import AgentRegistry, register_agent_routes, health_router, setup_logging
    from fastapi import FastAPI

    from marketing.agents.google_ads import core as google_ads
    from marketing.agents.meta_ads import core as meta_ads

    setup_logging()
    registry = AgentRegistry()
    registry.register("google-ads", google_ads.run)
    registry.register("meta-ads", meta_ads.run)

    app = FastAPI(title="marketing-service")
    app.include_router(health_router)
    register_agent_routes(app, registry)
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

AgentRunFn = Callable[[dict], dict]


class RunRequest(BaseModel):
    input: dict[str, Any]
    # _env permite a workflows comunes (send-email, send-whatsapp) redirigir
    # destinos a dev cuando _env="dev". Convención del workspace.
    env: str | None = None


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentRunFn] = {}

    def register(self, name: str, run_fn: AgentRunFn) -> None:
        if name in self._agents:
            raise ValueError(f"Agente '{name}' ya registrado")
        self._agents[name] = run_fn

    def get(self, name: str) -> AgentRunFn:
        if name not in self._agents:
            raise KeyError(name)
        return self._agents[name]

    def names(self) -> list[str]:
        return sorted(self._agents.keys())


def register_agent_routes(app: FastAPI, registry: AgentRegistry) -> None:
    @app.get("/agents")
    def list_agents() -> dict:
        return {"agents": registry.names()}

    @app.post("/agents/{agent_name}/run")
    def run_agent(agent_name: str, request: RunRequest) -> dict:
        try:
            run_fn = registry.get(agent_name)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Agente '{agent_name}' no encontrado")

        payload = dict(request.input)
        if request.env:
            payload["_env"] = request.env

        logger.info("agent.run.start", extra={"agent": agent_name, "env": request.env})
        result = run_fn(payload)
        logger.info("agent.run.done", extra={"agent": agent_name})
        return {"agent": agent_name, "result": result}

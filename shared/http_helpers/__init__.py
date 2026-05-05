"""http_helpers — utilidades para los services FastAPI de cada módulo.

- `setup_logging()`: configuración de logging estructurada (JSON-friendly).
- `health_router`: router con `GET /health` listo para Azure / AWS / GCP.
- `register_agent_routes`: monta `POST /agents/{nombre}/run` para todos los agentes
  registrados en el módulo.
"""
from .health import health_router
from .logging_config import setup_logging
from .registry import AgentRegistry, register_agent_routes

__all__ = ["health_router", "setup_logging", "AgentRegistry", "register_agent_routes"]

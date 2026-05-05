"""Tools del agente {{AGENT_NAME}}.

Convención:
- TOOL_DEFS: lista de definiciones (name, description, input_schema) para Anthropic.
- TOOL_HANDLERS: dict {name: callable} con la implementación.

Agregá más tools creando archivos hermanos (`mi_tool.py`) y registrándolos abajo.
"""
from .example_tool import EXAMPLE_TOOL_DEF, example_tool

TOOL_DEFS = [EXAMPLE_TOOL_DEF]

TOOL_HANDLERS = {
    "example_tool": example_tool,
}

__all__ = ["TOOL_DEFS", "TOOL_HANDLERS"]

"""Tool de ejemplo. Reemplazar con la lógica real.

Cada tool tiene:
- Una definición JSONSchema (`<NAME>_TOOL_DEF`).
- Una función handler que recibe los kwargs validados por Anthropic.
"""
from __future__ import annotations

EXAMPLE_TOOL_DEF = {
    "name": "example_tool",
    "description": (
        "Tool de ejemplo. Reemplazá la descripción con qué hace la tool y "
        "cuándo el modelo debería usarla."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto que la tool va a procesar.",
            },
        },
        "required": ["query"],
    },
}


def example_tool(query: str) -> dict:
    """Implementación. Reemplazar con la lógica real (consulta DB, API, etc.)."""
    return {"echo": query, "length": len(query)}

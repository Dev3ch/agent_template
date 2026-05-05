"""Agente {{AGENT_NAME}} (tipo B — híbrido n8n + Python).

Punto de entrada: `run(input_data)` devuelve dict serializable a JSON.
"""
from __future__ import annotations

import logging
from pathlib import Path

from shared.claude_advisor import ClaudeAdvisor

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")


def run(input_data: dict) -> dict:
    """Punto de entrada del agente.

    Args:
        input_data: payload del request. Convencionalmente puede traer `_env`
            ("dev"|"prod") para distinguir entornos en workflows compartidos.

    Returns:
        dict con la decisión / resultado del agente.
    """
    logger.info("{{AGENT_NAME}}.run", extra={"keys": list(input_data.keys())})

    # 1) Reglas determinísticas — filtrar/clasificar antes de llamar a Claude.
    #    (Acá iría tu lógica de pandas, SDK propietario, etc.)

    # 2) Solo si queda algo ambiguo, consultar a Claude.
    advisor = ClaudeAdvisor()
    response = advisor.ask(
        system=SYSTEM_PROMPT,
        user=str(input_data),
        max_tokens=512,
    )

    return {
        "status": "ok",
        "decision": response.text,
        "tokens": response.total_tokens,
        "_meta": {"latency_ms": response.latency_ms},
    }

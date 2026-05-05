"""Agente {{AGENT_NAME}} (tipo C — AgentLoop con tools).

El loop sigue el patrón estándar de Anthropic: Claude propone usar una tool,
nosotros la ejecutamos, devolvemos el resultado, repetimos.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import anthropic

from .tools import TOOL_DEFS, TOOL_HANDLERS

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")

MAX_ITERATIONS = 10
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")


def run(input_data: dict) -> dict:
    """Ejecuta el AgentLoop hasta que Claude termina o se agota el budget.

    Returns:
        dict con la respuesta final + metadata (iteraciones, tokens, tools usadas).
    """
    client = anthropic.Anthropic()
    messages: list[dict] = [
        {"role": "user", "content": _format_input(input_data)},
    ]

    tools_used: list[str] = []
    total_input_tokens = 0
    total_output_tokens = 0

    for iteration in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=2048,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            tools=TOOL_DEFS,
            messages=messages,
        )
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        if response.stop_reason == "end_turn":
            return {
                "status": "ok",
                "answer": _extract_text(response),
                "_meta": {
                    "iterations": iteration + 1,
                    "tools_used": tools_used,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                },
            }

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tools_used.append(tool_name)
                    handler = TOOL_HANDLERS.get(tool_name)
                    if handler is None:
                        result = {"error": f"tool '{tool_name}' no implementada"}
                    else:
                        try:
                            result = handler(**tool_input)
                        except Exception as exc:
                            logger.exception("tool.error", extra={"tool": tool_name})
                            result = {"error": str(exc)}
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        return {"status": "error", "reason": f"stop_reason inesperado: {response.stop_reason}"}

    return {
        "status": "error",
        "reason": f"agente excedió MAX_ITERATIONS={MAX_ITERATIONS}",
        "_meta": {"tools_used": tools_used},
    }


def _format_input(input_data: dict) -> str:
    import json
    return json.dumps(input_data, ensure_ascii=False)


def _extract_text(response) -> str:
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts)

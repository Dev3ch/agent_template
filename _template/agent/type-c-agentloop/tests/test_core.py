"""Tests del agente {{AGENT_NAME}} (tipo C)."""
from __future__ import annotations

import pytest


def test_tools_module_loads():
    """Sanity: el registro de tools tiene la forma esperada."""
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}}.tools import TOOL_DEFS, TOOL_HANDLERS

    assert isinstance(TOOL_DEFS, list)
    assert isinstance(TOOL_HANDLERS, dict)
    for tool_def in TOOL_DEFS:
        assert tool_def["name"] in TOOL_HANDLERS, (
            f"tool '{tool_def['name']}' definida pero sin handler"
        )


def test_example_tool_runs():
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}}.tools.example_tool import example_tool

    result = example_tool(query="hola")
    assert result["echo"] == "hola"
    assert result["length"] == 4


@pytest.mark.integration
def test_run_against_real_claude():
    """Llamada real al AgentLoop. Requiere ANTHROPIC_API_KEY."""
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}} import core

    result = core.run({"ping": "pong"})
    assert "status" in result

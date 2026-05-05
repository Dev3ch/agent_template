"""Tests del agente {{AGENT_NAME}}.

Convención: nada de mocks de Claude. Para tests rápidos sin gastar tokens,
parchear `ClaudeAdvisor.ask` con un fake. Para integration tests reales,
marcar con @pytest.mark.integration.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest


def test_run_happy_path():
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}} import core

    fake = type("FakeResp", (), {
        "text": '{"status": "ok", "decision": "test"}',
        "total_tokens": 10,
        "latency_ms": 50,
    })()

    with patch.object(core, "ClaudeAdvisor") as MockAdvisor:
        MockAdvisor.return_value.ask.return_value = fake
        result = core.run({"hola": "mundo"})

    assert result["status"] == "ok"
    assert "decision" in result
    assert result["tokens"] == 10


def test_run_returns_dict():
    """Contrato uniforme: el agente siempre devuelve un dict serializable."""
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}} import core

    fake = type("FakeResp", (), {"text": "x", "total_tokens": 1, "latency_ms": 1})()
    with patch.object(core, "ClaudeAdvisor") as MockAdvisor:
        MockAdvisor.return_value.ask.return_value = fake
        result = core.run({})

    assert isinstance(result, dict)


@pytest.mark.integration
def test_run_against_real_claude():
    """Llamada real a Anthropic. Requiere ANTHROPIC_API_KEY."""
    from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}} import core

    result = core.run({"ping": "pong"})
    assert result["status"] in {"ok", "unavailable"}

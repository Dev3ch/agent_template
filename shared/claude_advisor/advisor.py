"""Wrapper estándar del SDK de Anthropic con logging, retries y prompt caching."""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import anthropic

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")
DEFAULT_MAX_TOKENS = 1024
DEFAULT_RETRIES = 3


@dataclass
class ClaudeResponse:
    text: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    latency_ms: int
    raw: Any

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class ClaudeAdvisor:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_retries: int = DEFAULT_RETRIES,
    ):
        self.model = model or DEFAULT_MODEL
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            max_retries=max_retries,
        )

    def ask(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        tools: list[dict] | None = None,
        cache_system: bool = True,
    ) -> ClaudeResponse:
        """Llamada simple. Usar para razonamientos puntuales (1 ida y vuelta).

        Para AgentLoop iterativo, usar `loop()`.
        """
        system_blocks = self._build_system(system, cache_system)
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_blocks,
            "messages": [{"role": "user", "content": user}],
        }
        if tools:
            kwargs["tools"] = tools

        start = time.monotonic()
        response = self.client.messages.create(**kwargs)
        latency_ms = int((time.monotonic() - start) * 1000)

        text = self._extract_text(response)
        usage = response.usage

        result = ClaudeResponse(
            text=text,
            stop_reason=response.stop_reason or "",
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            cache_creation_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
            latency_ms=latency_ms,
            raw=response,
        )
        logger.info(
            "claude.ask",
            extra={
                "model": self.model,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "cache_read": result.cache_read_tokens,
                "latency_ms": latency_ms,
            },
        )
        return result

    @staticmethod
    def _build_system(system: str, cache: bool) -> list[dict]:
        block: dict[str, Any] = {"type": "text", "text": system}
        if cache:
            block["cache_control"] = {"type": "ephemeral"}
        return [block]

    @staticmethod
    def _extract_text(response: Any) -> str:
        parts = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts)

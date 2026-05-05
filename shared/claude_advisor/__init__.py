"""claude_advisor — wrapper estándar del Anthropic SDK.

Razones de existencia:
- Modelo por env (haiku local / sonnet prod) sin tocar código.
- Logging estructurado de cada llamada (tokens, latencia, costo aprox).
- Retries con backoff exponencial.
- Prompt caching activado por default (reduce costo en runs repetidos).
"""
from .advisor import ClaudeAdvisor, ClaudeResponse

__all__ = ["ClaudeAdvisor", "ClaudeResponse"]

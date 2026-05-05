# shared/

Librerías reutilizables entre módulos del monorepo.

## Regla de oro

| Va acá | Va en `{modulo}/lib/` |
|---|---|
| Lo usan 2+ módulos | Lo usa solo agentes de un módulo |
| Genérico (LLM, HTTP, persistencia, reglas) | Específico del dominio |
| Estable | Puede romper sin afectar otros módulos |

Si dudás, empezá en `{modulo}/lib/`. Promové a `shared/` cuando un segundo módulo lo necesite.

## Contenido

| Paquete | Qué hace |
|---|---|
| [claude_advisor](claude_advisor/) | Wrapper de Anthropic SDK. Maneja modelo por env (haiku local / sonnet prod), retries, prompt caching. |
| [notion_client](notion_client/) | CRUD contra Notion. Útil cuando Notion es la memoria compartida del agente. |
| [http_helpers](http_helpers/) | Logging estructurado, healthchecks FastAPI, retries httpx. |
| [rule_engine](rule_engine/) | Motor de reglas/umbrales declarativo. Filtra ítems antes de mandar a Claude. |

## Uso desde un módulo

```python
# marketing/agents/google-ads/core.py
from shared.claude_advisor import ClaudeAdvisor
from shared.rule_engine import RuleEngine

advisor = ClaudeAdvisor()
result = advisor.ask(system="...", user="...", max_tokens=500)
```

Para que el import funcione en el `service/` de cada módulo, su `pyproject.toml`
declara `shared` como dependencia editable del workspace (lo agrega `make new-module`).

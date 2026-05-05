# {{AGENT_NAME}} — agente tipo B (híbrido n8n + Python)

n8n orquesta. Python expone un endpoint específico cuando la lógica requiere
un SDK que no está en JS, o cálculo >50 líneas.

## Por qué tipo B

- Necesitás `pandas`, `playwright`, `google-ads-api`, `facebook-business`, etc.
- O la lógica de negocio es lo suficientemente compleja como para tener tests.
- Pero **no** es un AgentLoop iterativo (eso es tipo C).

## Estructura

```
{{MODULE_NAME}}/
├── agents/{{AGENT_SNAKE}}/   ← este agente (Python, snake_case para imports)
│   ├── README.md
│   ├── __init__.py
│   ├── core.py               ← run(input) -> dict
│   ├── prompts/system.md
│   └── tests/test_core.py
└── workflows/{{AGENT_NAME}}.json  ← workflow n8n (kebab-case)
```

## Registro en el service del módulo

Agregar a mano en `{{MODULE_NAME}}/service/main.py`:

```python
from {{MODULE_SNAKE}}.agents.{{AGENT_SNAKE}} import core as {{AGENT_SNAKE}}_agent
registry.register("{{AGENT_NAME}}", {{AGENT_SNAKE}}_agent.run)
```

## Probar

```bash
# 1) Levantar el service
cd {{MODULE_NAME}}/service && uv run uvicorn main:app --reload --port 8000

# 2) Llamar al agente
curl -X POST http://localhost:8000/agents/{{AGENT_NAME}}/run \
  -H 'Content-Type: application/json' \
  -d '{"input": {"ejemplo": "data"}}'

# 3) Tests
uv run pytest {{MODULE_NAME}}/agents/{{AGENT_SNAKE}}/tests/
```

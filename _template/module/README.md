# {{MODULE_NAME}}/

Módulo de agentes del dominio **{{MODULE_NAME}}**.

## Agentes

(Lista cada agente con `/new-agent` o `make new-agent module={{MODULE_NAME}} name=<agente> type=<a|b|c>`.)

| Agente | Tipo | Qué hace |
|---|---|---|
| _(vacío)_ | | |

## Tipos de agente

- **A — n8n-only**: solo workflow n8n. Sin código Python. No aparece en `service/`.
- **B — híbrido**: workflow n8n + endpoint en `service/main.py` para lógica que requiere Python.
- **C — AgentLoop**: el service ejecuta un loop iterativo con tools. n8n solo dispara.

Ver [`.claude/rules/agent-design.md`](../.claude/rules/agent-design.md) para criterios.

## Estructura

```
{{MODULE_NAME}}/
├── README.md
├── CLAUDE.md            ← contexto específico del módulo
├── agents/              ← un directorio por agente
├── workflows/           ← n8n JSONs (uno por agente, active: false)
├── service/             ← FastAPI compartido por agentes tipo B/C
└── lib/                 ← código compartido SOLO entre agentes de este módulo
```

## Levantar local

Si el módulo tiene `service/`:

```bash
cd {{MODULE_NAME}}/service/
cp .env.example .env
uv sync
uv run uvicorn main:app --reload --port 8000
```

Probar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/agents/<agente>/run \
  -H 'Content-Type: application/json' \
  -d '{"input": {}}'
```

# {{AGENT_NAME}} — agente tipo A (n8n-only)

Este agente vive **solo en n8n**. No hay código Python.

## Por qué tipo A

Porque su lógica entra en las dos primeras capas de la regla 1 de [agent-design.md](../../../.claude/rules/agent-design.md):

- Filtros, transformaciones, llamadas HTTP → nodos nativos.
- Razonamiento puntual con prompt corto → nodo Anthropic nativo.

No requiere SDK propietario ni AgentLoop iterativo.

## Estructura

```
{{AGENT_NAME}}/
├── README.md
├── prompts/
│   └── system.md       ← prompt del nodo Anthropic (versionado en git, no embebido en JSON)
└── workflow.json       ← copia del JSON exportado de n8n (active: false)
```

## Triggers obligatorios

- Webhook (siempre).
- Schedule (si la lógica es periódica).
- Error trigger + alerta (siempre).

## Cómo desplegarlo

1. Importar `workflow.json` a n8n (UI → Import from file).
2. Configurar credenciales (Anthropic, etc.) en la instancia n8n.
3. **Activar manualmente** desde la UI.

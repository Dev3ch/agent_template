# {{AGENT_NAME}} — agente tipo C (AgentLoop con tools)

Loop iterativo donde Claude usa tools y mantiene contexto entre pasos.
n8n solo dispara y recibe el resultado final.

## Por qué tipo C

- Múltiples tools que se llaman en orden no determinístico.
- El resultado depende del contexto acumulado entre llamadas.
- Pasos como: "buscar en CRM → analizar → decidir acción → ejecutar".

Si tu agente solo llama 1 tool, probablemente es tipo B, no C.

## Estructura

```
{{AGENT_NAME}}/
├── README.md
├── core.py               ← run(input) -> dict   (orquesta el loop)
├── tools/
│   ├── __init__.py       ← TOOL_DEFS + TOOL_HANDLERS
│   └── example_tool.py
├── prompts/
│   └── system.md
├── tests/
│   └── test_core.py
└── workflow.json
```

## Cómo funciona

`core.run()`:
1. Construye el primer mensaje con el input.
2. Llama a Claude con `tools=TOOL_DEFS`.
3. Si Claude pide usar una tool, ejecuta `TOOL_HANDLERS[tool_name](**args)`.
4. Devuelve el resultado a Claude.
5. Repite hasta que Claude da una respuesta final (`stop_reason="end_turn"`).
6. Devuelve resultado al caller.

Hay un límite duro de iteraciones (`MAX_ITERATIONS = 10`) para evitar loops infinitos.

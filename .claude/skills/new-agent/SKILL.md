---
name: new-agent
description: Crear un nuevo agente dentro de un módulo existente. Elige tipo A (n8n-only), B (híbrido) o C (AgentLoop) según las 4 preguntas de agent-design.md.
---

# /new-agent

Crea un agente nuevo dentro de un módulo. **El paso previo obligatorio es decidir el tipo.**

## Cuándo usar

- El usuario dice "creá un agente de google-ads", "agregá un agente de cobranza", etc.
- El módulo padre **ya existe** (sino, primero `/new-module`).

## Antes de ejecutar — recomendación obligatoria

Aplicar **Regla 5** de [agent-design.md](../../rules/agent-design.md): listar pasos,
estimar tokens, proponer particionamiento. Recién después construir.

Y aplicar las **4 preguntas** de Regla 2 para elegir tipo:

```
1. ¿La lógica es <50 líneas que un Code Node JS resuelve?
   SÍ → tipo A (n8n-only). FIN.
2. ¿Solo necesito un razonamiento puntual con prompt corto?
   SÍ → tipo A (con nodo Anthropic nativo). FIN.
3. ¿Necesito un SDK que NO existe en JS, o pandas/playwright?
   SÍ → tipo B.
4. ¿Necesito AgentLoop iterativo con múltiples tools?
   SÍ → tipo C.
   NO → volver al 1, no era tan complejo.
```

Mostrar al usuario qué tipo recomendás y pedir confirmación si es B o C
(por implicancia de costos).

## Pasos

1. **Validar inputs**: `module`, `name` (kebab-case), `type` ∈ {a, b, c}.
2. **Validar que `<module>/` existe**.
3. **Ejecutar**:
   ```bash
   make new-agent module=<module> name=<name> type=<a|b|c>
   ```
   Esto copia `_template/agent/type-{a|b|c}-*/` a `<module>/agents/<name>/`.
4. **Si tipo B o C**: registrar el agente en `<module>/service/main.py`.
   Importante: kebab-case en URLs / nombres de tools, snake_case en imports Python.

   Agregar (con `<module_snake>` y `<name_snake>` = nombres con `-` reemplazados por `_`):
   ```python
   from <module_snake>.agents.<name_snake> import core as <name_snake>_agent
   registry.register("<name>", <name_snake>_agent.run)  # kebab-case en el registry
   ```
5. **Layout resultante**:
   - Código Python: `<module>/agents/<name_snake>/`
   - Workflow n8n: `<module>/workflows/<name>.json`
6. **Recordar al usuario**:
   - Editar `prompts/system.md` con el prompt real.
   - Editar `core.py` con la lógica.
   - Editar el workflow JSON con los nodos n8n.
   - Correr tests: `uv run pytest <module>/agents/<name_snake>/tests/`.

## NO hacer

- No crear el agente sin elegir tipo: forzar la pregunta evita el error de meter
  todo en un servicio Python por default (Regla 1).
- No activar workflows directamente — siempre `active: false` (Regla 6).

---
name: new-module
description: Crear un nuevo módulo de agentes en el monorepo. Un módulo agrupa agentes del mismo dominio (marketing, sales, finance, etc.) y comparte un FastAPI service.
---

# /new-module

Crea un módulo nuevo bajo la raíz del monorepo. Un módulo es la unidad de
**agrupamiento de agentes** del mismo dominio.

## Cuándo usar

- El usuario dice "creá un módulo de cobranza", "necesito agrupar agentes de marketing", etc.
- Antes de `/new-agent`: el agente vive **dentro** de un módulo, no suelto en raíz.

## Pasos

1. **Validar nombre**:
   - kebab-case (`cobranza`, `customer-success`).
   - Único: `[ -d "$name" ]` debe ser falso.

2. **Ejecutar el scaffold** (atajo Makefile):
   ```bash
   make new-module name=<nombre>
   ```
   Esto:
   - Copia `_template/module/` a `<nombre>/`.
   - Reemplaza `{{MODULE_NAME}}` en todos los archivos.
   - Crea `<nombre>/{agents,workflows,service,lib}/`.

3. **Registrar en el workspace**: agregar `"<nombre>/service"` a `tool.uv.workspace.members`
   en el `pyproject.toml` raíz.

4. **Confirmar al usuario** qué se creó y proponer crear el primer agente con
   `/new-agent module=<nombre> name=<agente> type=<a|b|c>`.

## Estructura resultante

```
<nombre>/
├── README.md
├── CLAUDE.md
├── agents/        ← se llenará con /new-agent
├── workflows/     ← un JSON por agente
├── service/       ← FastAPI compartido
└── lib/           ← código compartido entre agentes del módulo
```

## NO hacer

- No crear módulos sin el comando: el `sed` para reemplazar `{{MODULE_NAME}}` es esencial.
- No crear el primer agente automáticamente — esperá a que el usuario decida tipo A/B/C.

# Estructura de módulos

Reglas operativas para organizar agentes en este monorepo. **Aplicá esto antes
de crear cualquier agente.**

---

## El modelo: monorepo modular

Un solo repo agrupa **N módulos × N agentes**. No tenemos "un repo por agente".

```
mi-repo/                       ← UN repo, generado a partir de agent_template
├── marketing/                 ← MÓDULO (dominio)
│   ├── agents/
│   │   ├── google-ads/        ← AGENTE
│   │   ├── meta-ads/
│   │   └── seo-optimizer/
│   ├── workflows/             ← n8n por agente
│   ├── service/               ← UN FastAPI por módulo (compartido)
│   └── lib/                   ← código compartido entre agentes del módulo
├── sales/
├── finance/
└── ...
```

---

## Por qué esto y no "un repo por agente"

| Monorepo modular (lo que hacemos) | Repo por agente (NO) |
|---|---|
| `shared/` cross-módulo sin paquete pip privado | Hay que publicar libs como paquete |
| 1 CI / 1 tooling | N pipelines |
| 1 service por módulo (3 agentes = 1 container) | 3 containers |
| Refactor cross-agente en 1 PR | N PRs sincronizados |
| Onboarding: clonás 1 repo | Clonás N repos |

Es el patrón que usan Microsoft, Google, Meta, Stripe.

---

## Reglas operativas

### R1 — Un módulo por dominio funcional

Buenos nombres: `marketing`, `sales`, `finance`, `customer-success`, `ops`,
`hr`, `intelligence`, `security`. Malos: `utils`, `tools`, `helpers` (eso va
en `shared/` o en `{modulo}/lib/`).

### R2 — Un service por módulo, no por agente

Si `marketing/` tiene 3 agentes tipo B/C, hay **un solo container** con rutas:

- `POST /agents/google-ads/run`
- `POST /agents/meta-ads/run`
- `POST /agents/seo-optimizer/run`

Comparten dependencias, lib del módulo, cold start, cuesta menos. n8n llama a
`https://marketing-service.<cloud>.app/agents/<nombre>/run`.

### R3 — `shared/` vs. `{modulo}/lib/`

| Va en `shared/` (raíz) | Va en `{modulo}/lib/` |
|---|---|
| Lo usan 2+ módulos | Lo usa solo agentes del módulo |
| Genérico (LLM, HTTP, Notion, reglas) | Específico del dominio |
| Estable | Puede romper sin afectar otros módulos |

Si dudás, empezá en `{modulo}/lib/`. Promové a `shared/` cuando aparezca el segundo módulo que lo necesite.

### R4 — Tipos de agente A / B / C

Cada agente nace eligiendo tipo (`/new-agent ... type=a|b|c`):

| Tipo | Vive en | Cuándo |
|---|---|---|
| **A — n8n-only** | Solo `{modulo}/workflows/{nombre}.json` (+ `prompts/system.md`). Sin código Python. | Lógica entra en nodos nativos + nodo Anthropic. **El 70% de los casos.** |
| **B — híbrido** | `{modulo}/agents/{nombre}/` con `core.run()` + se registra en `{modulo}/service/main.py`. | Necesitás SDK no-JS, pandas, playwright, o lógica con tests. |
| **C — AgentLoop** | `{modulo}/agents/{nombre}/` con `core.py` + `tools/`. | Loop iterativo con múltiples tools que mantienen contexto. |

Las **4 preguntas** y la lógica completa: [agent-design.md](agent-design.md).

### R5 — Naming

- Módulos: kebab-case (`customer-success`).
- Agentes: kebab-case (`google-ads`, `lead-finder`).
- Python imports: `marketing.agents.google_ads` (kebab → snake automático).
- Workflows: `{modulo}-{agente}` (ej `marketing-google-ads`).
- Container apps: `{modulo}-service`.

### R6 — Cada agente expone la misma interfaz

```python
# {modulo}/agents/{agente}/core.py
def run(input_data: dict) -> dict: ...
```

El service del módulo lo registra y lo expone uniformemente:

```python
registry.register("google-ads", google_ads.run)
# → POST /agents/google-ads/run
```

### R7 — Workflows siempre `active: false`

Igual que la Regla 6 de [agent-design.md](agent-design.md). El dev activa
manualmente en la UI de n8n.

### R8 — Tests obligatorios para tipo B y C

Cada agente tipo B/C nace con `tests/test_core.py`:

- Happy path con `ClaudeAdvisor` parcheado (rápido, sin tokens).
- Test de contrato: `run()` siempre devuelve `dict`.
- Test integration con Claude real, marcado `@pytest.mark.integration` (no corre en CI default).

### R9 — Convención `_env` en el body

Workflows compartidos (`send-email`, `send-whatsapp`) leen `_env` del payload:

- `_env: "dev"` → destinos del dev.
- `_env: "prod"` → destinos reales.

El service inyecta `_env` automáticamente al payload del agente. Reemplaza tener
workflows duplicados `-staging` / `-prod`.

---

## Flujo típico para crear un agente nuevo

```
1. /new-module name=cobranza         (si no existe el módulo)
2. /new-agent module=cobranza name=recordatorios type=a
3. Editar cobranza/agents/recordatorios/prompts/system.md
4. Editar cobranza/workflows/recordatorios.json (los nodos)
5. Si tipo B/C: editar core.py + tests/, correr pytest
6. /test → /build → /review → /deploy (si aplica)
```

---

## Anti-patrones

- ❌ Crear `agents/` o `services/` planos en raíz (eso era el template viejo).
- ❌ Un service por agente (forza N containers donde alcanza con 1).
- ❌ Duplicar `claude_advisor` en cada módulo (eso va en `shared/`).
- ❌ Mezclar dominios en un mismo módulo (`marketing/` con agente de cobranza).
- ❌ Servicio Python para lógica que un Code Node JS resuelve (Regla 1 de agent-design).

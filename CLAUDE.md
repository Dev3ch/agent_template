# CLAUDE.md

Guía para Claude Code en este repositorio.

## Qué es agent_template

Plantilla oficial del workspace **dev3ch** para crear **monorepos modulares de
agentes de IA**. Un repo generado a partir de este template agrupa N módulos × N
agentes, con FastAPI + Docker + Anthropic Claude, orquestado desde n8n y
desplegable en Azure / AWS / GCP.

**Repo:** `dev3ch/agent_template`
**Stack:** Python 3.12 + FastAPI + uv + Docker + Anthropic Claude
**Modelo:** monorepo modular (1 repo = N módulos = N×M agentes)

## Mental model

```
mi-repo/
├── shared/                   # libs compartidas entre módulos
├── workflows/shared/         # workflows n8n reusados
├── _template/                # scaffolds de módulo y agente (no se edita)
├── deploy/                   # un script por cloud
│
├── marketing/                # MÓDULO
│   ├── agents/google-ads/    # AGENTE (tipo A/B/C)
│   ├── agents/meta-ads/
│   ├── workflows/            # n8n por agente
│   ├── service/              # FastAPI compartido por agentes B/C
│   └── lib/                  # código compartido del módulo
│
├── sales/                    # MÓDULO
└── finance/                  # MÓDULO
```

Detalle completo: [.claude/rules/module-structure.md](.claude/rules/module-structure.md).

## Filosofía de agentes

**El orquestador (n8n) es el protagonista. Claude entra solo cuando hay
razonamiento real. El servicio Python en container existe únicamente cuando la
lógica es genuinamente compleja.**

Los **3 tipos** de agente:

| Tipo | Vive en | Cuándo |
|---|---|---|
| **A — n8n-only** | Solo `workflows/`. Sin Python. | Lógica entra en nodos nativos + nodo Anthropic. **70% de los casos.** |
| **B — híbrido** | `agents/{nombre}/core.py` registrado en `service/main.py` | SDK no-JS, pandas, playwright, lógica con tests. |
| **C — AgentLoop** | `agents/{nombre}/core.py` + `tools/` | Loop iterativo con múltiples tools que mantienen contexto. |

Las 4 preguntas para elegir tipo y las 6 reglas operativas:
[.claude/rules/agent-design.md](.claude/rules/agent-design.md).

## Comandos clave

| Comando | Qué hace |
|---|---|
| `/init` | Arranca sesión: rama, issues, contexto. |
| `/new-module` | Crea un módulo nuevo (`make new-module name=<nombre>`). |
| `/new-agent` | Crea un agente dentro de un módulo (`make new-agent module=<m> name=<a> type=<a\|b\|c>`). |
| `/plan` → `/apply` → `/test` → `/build` → `/review` | Flujo de desarrollo. |
| `/secure` → `/deploy` | Pre-deploy + deploy a cloud. |
| `/debug`, `/audit`, `/pentest`, `/sync`, `/rollback` | Soporte. |

## Stack y dependencias

**Raíz** ([pyproject.toml](pyproject.toml)): solo tooling (ruff, pytest, mypy).
Sin deps de runtime — esas viven en cada `{modulo}/service/pyproject.toml`.

**Por módulo** (`{modulo}/service/pyproject.toml`): deps específicas del módulo.
Se registran en el workspace uv:

```toml
# pyproject.toml raíz
[tool.uv.workspace]
members = ["marketing/service", "sales/service"]
```

**Levantar un módulo local:**

```bash
cd marketing/service/
cp .env.example .env
uv sync
uv run uvicorn main:app --reload --port 8000
```

## Convenciones

### Commits

Conventional commits con referencia a issue:

```
feat(marketing/google-ads): webhook handler #42 — feature #12
fix(shared): null en notion_client #58 — fix #18
chore(deps): bump fastapi #60 — chore #20
```

Detalle: [.claude/rules/commits.md](.claude/rules/commits.md).

### Branching

3 branches protegidas: `main` (prod) / `staging` (QA) / `dev` (integración).
Branches efímeras: `feature/*`, `refactor/*`, `fix/*`, `chore/*`, `hotfix/*`.

Detalle: [.claude/rules/branching.md](.claude/rules/branching.md).

### Tests

- Cada agente tipo B/C requiere: happy path + contrato + integration (opt-in).
- `pytest -m "not integration"` corre en CI; integration tests son manuales.
- No mocks para servicios reales (Notion, APIs) — usar `_env: "dev"` para
  redirigir destinos.

Detalle: [.claude/rules/tests.md](.claude/rules/tests.md).

## Reglas específicas del template

1. **Cloud opcional, no obligatorio.** Borrá las carpetas `deploy/{azure,aws,gcp}/` que no uses.
2. **Registry parametrizado** vía `REGISTRY_PREFIX` en `.env` raíz.
3. **El agente vive en `{modulo}/agents/{nombre}/`**, NO en raíz.
4. **Modelo Claude por entorno**: local `claude-haiku-4-5`, prod `claude-sonnet-4-6` (override automático en `deploy.sh`).
5. **No commitear `.env`.** Solo `.env.example` (raíz + por módulo).
6. **Workflows siempre `active: false`.** El dev activa manualmente en n8n.

## Context policy

| Contexto | Dónde |
|---|---|
| Estado de una feature | Issue de GitHub |
| Plan de un epic | Issue padre + sub-issues |
| Convenciones | `CLAUDE.md` + `.claude/rules/` |
| Preferencias personales | `CLAUDE.local.md` (no commitear) |

## Reglas operativas para Claude

1. Al arrancar sesión: `/init`.
2. Antes de crear un agente: aplicar las **4 preguntas** de [agent-design.md](.claude/rules/agent-design.md). Recomendación obligatoria al usuario antes de construir.
3. Antes de cada deploy: `/secure`.
4. Si el plan en GitHub no refleja el código: `/sync`.
5. Aprendizajes que persisten: commitear al `CLAUDE.md`.

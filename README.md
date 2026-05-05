# agent_template

Plantilla oficial del workspace **dev3ch** para crear **monorepos modulares de
agentes de IA**.

Stack: **Python 3.12 + FastAPI + uv + Docker + Anthropic Claude**, orquestado
desde **n8n** y desplegable en **Azure / AWS / GCP** (elegís uno y borrás el
resto).

---

## Modelo: monorepo modular

Un solo repo, varios módulos, varios agentes por módulo. Igual que Microsoft,
Google, Meta o Stripe organizan sus stacks de servicios.

```
mi-repo-de-agentes/
├── shared/                   # libs compartidas entre módulos
├── workflows/shared/         # workflows n8n reusados
├── deploy/{azure,aws,gcp}/   # un script por cloud
│
├── marketing/                # MÓDULO (dominio)
│   ├── agents/
│   │   ├── google-ads/       # AGENTE (tipo A, B o C)
│   │   ├── meta-ads/
│   │   └── seo-optimizer/
│   ├── workflows/            # un n8n JSON por agente
│   ├── service/              # FastAPI compartido por agentes B/C del módulo
│   └── lib/                  # código compartido entre los agentes del módulo
│
├── sales/                    # MÓDULO
│   └── ...
└── finance/                  # MÓDULO
```

---

## Quickstart

```bash
# 1) "Use this template" en GitHub → dev3ch/agent_template
# 2) Clonar el repo nuevo
git clone https://github.com/<vos>/mi-agentes.git
cd mi-agentes

# 3) Crear el primer módulo
make new-module name=marketing

# 4) Crear el primer agente del módulo (tipo A: n8n-only)
make new-agent module=marketing name=google-ads type=a

# 5) (Opcional) Crear un agente tipo B (necesita Python)
make new-agent module=marketing name=seo-optimizer type=b

# 6) Levantar el service del módulo (si tiene agentes B o C)
cd marketing/service/
cp .env.example .env
uv sync
uv run uvicorn main:app --reload --port 8000
```

Probar:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/agents
curl -X POST http://localhost:8000/agents/seo-optimizer/run \
  -H 'Content-Type: application/json' \
  -d '{"input": {"url": "https://example.com"}}'
```

---

## Los 3 tipos de agente

Antes de crear un agente, elegís tipo. **El default es A**: la mayoría de los
agentes no necesitan Python.

| Tipo | Vive en | Cuándo usarlo | Costo runtime |
|---|---|---|---|
| **A — n8n-only** | `{modulo}/workflows/{nombre}.json` (+ `prompts/system.md`) | Lógica entra en nodos n8n nativos + nodo Anthropic. | Solo n8n + tokens del nodo Anthropic. |
| **B — híbrido** | `{modulo}/agents/{nombre}/core.py` registrado en `service/main.py` | Necesitás SDK que no existe en JS, pandas, playwright, o lógica testeable. | n8n + container app. |
| **C — AgentLoop** | `{modulo}/agents/{nombre}/core.py` + `tools/` | Loop iterativo con múltiples tools que mantienen contexto. | n8n + container app + más tokens. |

Decisión completa: [.claude/rules/agent-design.md](.claude/rules/agent-design.md)
y [.claude/rules/module-structure.md](.claude/rules/module-structure.md).

---

## Estructura del template

```
agent_template/
├── README.md                 # este archivo
├── CLAUDE.md                 # contexto para Claude Code
├── pyproject.toml            # tooling raíz (ruff, pytest)
├── Makefile                  # atajos: make new-module, new-agent, test, lint
├── .env.example              # vars compartidas (ANTHROPIC_API_KEY, etc.)
│
├── .claude/
│   ├── rules/                # agent-design, module-structure, branching, commits, tests, python
│   ├── skills/               # /init, /plan, /apply, /new-module, /new-agent, /deploy, ...
│   └── scripts/
│
├── shared/                   # libs reusables entre módulos
│   ├── claude_advisor/       # wrapper Anthropic con caching, retries, logging
│   ├── notion_client/        # CRUD ligero contra Notion
│   ├── http_helpers/         # logging, healthcheck, AgentRegistry
│   └── rule_engine/          # reglas/umbrales declarativos
│
├── workflows/shared/         # workflows n8n compartidos (send-email, send-whatsapp)
│
├── _template/                # scaffolds (copiados por make new-module / new-agent)
│   ├── module/               # plantilla de módulo
│   └── agent/
│       ├── type-a-n8n-only/  # solo workflow + prompt
│       ├── type-b-hybrid/    # core.py + workflow + tests
│       └── type-c-agentloop/ # core.py + tools/ + workflow + tests
│
├── deploy/                   # un script por cloud (borrar los que no uses)
│   ├── azure/deploy.sh       # ./deploy/azure/deploy.sh <modulo>
│   ├── aws/deploy.sh
│   └── gcp/deploy.sh
│
└── .github/
    └── workflows/
        ├── ci.yml            # lint + tests + docker build (matrix por módulo)
        └── deploy.yml        # workflow_dispatch para deploy manual
```

---

## Decisiones de stack

**Fijas** (parte del template):

- Python 3.12+ (workspace uv).
- FastAPI por módulo (`POST /agents/{nombre}/run`, `GET /health`, `GET /agents`).
- Docker (multi-stage) — un container por módulo, no por agente.
- Anthropic Claude.
- ruff + pytest.

**Opcionales** (elegís al usar):

| Decisión | Opciones | Cómo elegir |
|---|---|---|
| Cloud | Azure / AWS / GCP | Borrar carpetas no usadas en `deploy/` |
| Container registry | Docker Hub / ACR / ECR / GAR | `REGISTRY_PREFIX` en `.env` raíz |
| Orquestador | n8n / nada | Workflows en `{modulo}/workflows/` opcionales |
| Modelo Claude | Haiku / Sonnet / Opus | `CLAUDE_MODEL` en `.env` (default: Haiku local, Sonnet prod) |

---

## Flujo típico

```
/init                                              # arrancar sesión
/new-module name=marketing                         # crear módulo
/new-agent module=marketing name=google-ads type=b # crear agente
/plan → /apply → /test                             # implementar + testear
/build → /review                                   # commit + PR
/secure → /deploy                                  # pre-deploy + cloud
```

---

## Mantenimiento del template

```bash
make sync            # actualizar deps del workspace
make lint            # ruff check
make fmt             # ruff format
make test            # pytest (no integration)
```

Para regenerar el template completo: ver `.claude/skills/setup/`.

# Diseño de agentes

Reglas operativas para diseñar y mantener agentes basados en este template. **Aplica a agentes nuevos y a refactor de los existentes.**

> **Premisa:** n8n (u otro orquestador) es el protagonista. Claude entra solo cuando hay razonamiento real. El servicio Python en un container existe únicamente cuando la lógica es genuinamente compleja.
>
> No al revés.

---

## Por qué existen estas reglas

Es muy fácil caer en sobrecargar el prompt de Claude con tareas que un nodo nativo del orquestador (HTTP, Notion, SendGrid, IF, Code JS, Webhook, Schedule) o un Code Node resuelven gratis. El resultado es decenas de miles de tokens por corrida, costo creciente y lógica difícil de testear.

Estas reglas evitan ese patrón.

---

## Regla 1 — Tres formas de ejecutar lógica, en orden de preferencia

| Prioridad | Forma | Cuándo usarla |
|---|---|---|
| **1ra** | **Nodo nativo del orquestador** (HTTP, Notion, SendGrid, IF, Code JS, Webhook, Schedule, Aggregate) | Filtros, transformaciones, escrituras simples, reglas de umbrales, formateo, llamadas HTTP a APIs ya soportadas. |
| **2da** | **Nodo Anthropic nativo del orquestador** | Razonamiento puntual con prompt corto y respuesta acotada (texto o JSON). Sin tools, sin loops, sin contexto entre llamadas. |
| **3ra** | **Servicio Python en container** (FastAPI / este template) | Solo cuando la lógica es genuinamente compleja: AgentLoop con tools, SDKs oficiales no disponibles en JS, multi-step business logic con tests, pandas/numpy. |

**El default es el orquestador. Subir de nivel solo si el anterior no alcanza.**

Ningún agente arranca como "servicio Python" por defecto. Eso se gana demostrando que las dos primeras opciones no resuelven el problema.

---

## Regla 2 — Cuándo NO crear servicio Python

Antes de proponer un servicio Python, contestá las **4 preguntas** en orden:

```
┌──────────────────────────────────────────────────────────────┐
│ 1. ¿La lógica es < ~50 líneas que un Code Node JS puede     │
│    hacer (filtrar, mapear, agregar, formatear)?             │
│       SÍ → orquestador puro. Fin.                            │
│       NO → siguiente pregunta.                               │
├──────────────────────────────────────────────────────────────┤
│ 2. ¿Solo necesito que Claude razone con un prompt corto y    │
│    devuelva texto o JSON?                                    │
│       SÍ → nodo Anthropic del orquestador. Fin.              │
│       NO → siguiente pregunta.                               │
├──────────────────────────────────────────────────────────────┤
│ 3. ¿Necesito un SDK oficial que NO existe en JS              │
│    (ej: google-ads-api, facebook-business, GA4 admin)?       │
│       SÍ → servicio Python justificado.                      │
│       NO → siguiente pregunta.                               │
├──────────────────────────────────────────────────────────────┤
│ 4. ¿Necesito AgentLoop iterativo con múltiples tools que     │
│    mantengan contexto entre llamadas?                        │
│       SÍ → servicio Python justificado.                      │
│       NO → volver al paso 1, no era tan complejo.            │
└──────────────────────────────────────────────────────────────┘
```

**Solo si las preguntas 3 o 4 son sí, se crea servicio Python.** En cualquier otro caso, queda en el orquestador.

---

## Regla 3 — Particionar agentes, no monolitos

> **Ningún agente debe tener más de 1 razonamiento principal.** Si lo tiene, particionar en mini-agentes coordinados por el orquestador.

### Mal diseño (monolito)

```
Cron → POST /agente/check
        ↓
Servicio Python (FastAPI):
  - Lee API externa
  - Pasa TODA la data cruda a Claude
  - Claude ejecuta AgentLoop con 5 tools
  - Claude filtra, agrega, decide, formatea, escribe destino, notifica
        ↓
~30k tokens input + iteraciones + output
~$0.10–0.30 por corrida
```

Claude termina haciendo trabajo de IF, filter y formateo que no requieren razonamiento.

### Buen diseño (particionado)

```
Cron del orquestador
  ↓
Nodo HTTP: GET API externa
  ↓
Nodo Code (JS): aplica reglas de umbrales
  - métrica > X → marca "acción A"
  - métrica > Y → marca "acción B"
  → arma lista: casos automáticos + casos a decidir
  ↓
IF: ¿hay casos a decidir?
  ↓ sí
  Nodo Anthropic: SOLO los casos ambiguos (5-10 items)
    prompt corto: "decidí solo entre estos casos: [datos mínimos]"
    respuesta corta: { "acciones": [...] }
  ↓
Nodo de destino (Notion, DB, webhook): escribe propuestas
  ↓
Nodo HTTP → notifier
```

```
~1-3k tokens (solo casos ambiguos llegan a Claude)
~$0.01 por corrida
Reducción real: 10-30x
```

Cada pieza es **testeable y reemplazable** por separado.

---

## Regla 4 — Triggers obligatorios en workflows del orquestador

Todo workflow que se diseñe **debe tener**:

| Trigger | ¿Cuándo? | Por qué |
|---|---|---|
| **Webhook (POST)** | **Siempre.** | Permite invocación on-demand desde otros workflows, testing, orquestación. Sin webhook un workflow no se puede testear. |
| **Schedule (cron)** | Solo si el dev pide explícitamente cron. | Evita programaciones accidentales. |
| **Error trigger + alerta** | **Siempre.** | Email o mensaje al responsable. Un workflow sin error handler falla en silencio. |

### Reglas de interpretación

| El dev dice... | Triggers que se crean |
|---|---|
| "Hazme un workflow programado X" | Schedule + Webhook + Error |
| "Hazme un workflow de X" | Webhook + Error |
| "Hazme un endpoint API X" | Webhook + Error |
| (sin especificar trigger) | Webhook + Error |

**Nunca un workflow sin webhook.** El webhook es la puerta de testing y de orquestación cross-workflow.

---

## Regla 5 — Recomendación obligatoria al diseñar agentes nuevos

Cuando un usuario pida "hazme un agente que haga X, Y, Z", la respuesta **no es construir el agente**. La respuesta es seguir este proceso de 5 pasos:

```
1. Listar lo pedido en formato de pasos discretos.
2. Por cada paso, marcar dónde corre:
     [Orquestador nativo]  [Mini-Claude orquestador]  [Servicio Python]
3. Estimar tokens para los pasos que van a Claude.
4. Proponer particionamiento si hay más de 1 razonamiento principal.
5. Recién entonces, después de aprobado el plan, construir.
```

### Plantilla de respuesta

```
Lo que pediste se descompone en N pasos:

Paso 1: <descripción>             [Orquestador nativo]
Paso 2: <descripción>             [Mini-Claude]    ~500 tokens
Paso 3: <descripción>             [Orquestador nativo]
Paso 4: <descripción>             [Servicio Python]    justifica por SDK X
Paso 5: <descripción>             [Orquestador nativo]

Razonamientos principales: 2 (Paso 2 y Paso 4).
Recomiendo particionar en 2 mini-agentes:
  • Agente A: Pasos 1-3 (todo en orquestador, sin servicio).
  • Agente B: Paso 4 (servicio Python por SDK propietario).

Costo estimado por corrida: ~$0.0X
¿Confirmás este diseño antes de construir?
```

Así el usuario ve el costo y la complejidad **antes** de que se construya nada.

---

## Regla 6 — Workflows del orquestador siempre se crean inactivos

Cuando Claude genera o sube un workflow (vía MCP, API o subiendo JSON), **debe crearlo con `active: false`**.

```json
{
  "name": "...",
  "active": false,    // ← obligatorio
  ...
}
```

### Por qué

- Evita ejecuciones accidentales mientras se valida.
- En algunas plataformas (n8n por ejemplo), si el workflow se sube ya activo desde fuera de la UI, después puede quedar en estado inconsistente al despublicar/republicar desde la UI.

### Flujo correcto

1. Diseñar el JSON local en `workflows/`.
2. Validar con la herramienta correspondiente (ej. `n8n-mcp validate_workflow`).
3. Subir al orquestador **inactivo** (`active: false`).
4. Probar via webhook desde local con curl o un cliente HTTP.
5. **El dev activa manualmente en la UI** cuando esté listo.

Claude **nunca activa workflows directamente.**

---

## Tabla de oro: Claude SÍ hace / Claude NO hace

| ✅ Claude SÍ hace (irreemplazable) | ❌ Claude NO hace (sangría de tokens) |
|---|---|
| Razonar sobre data ambigua | Llamar APIs (eso lo hace nodo HTTP) |
| Decidir bajo incertidumbre | Filtrar listas (`filter` JS de 1 línea) |
| Generar texto creativo (copy, propuestas) | Aplicar reglas de umbrales (IF) |
| Interpretar resultados ambiguos | Formatear output (HTML, Markdown, JSON) |
| Priorizar entre opciones | Escribir en destino (nodo nativo Notion/DB) |
| Resumir grandes volúmenes de texto | Loops sobre arrays |
| Clasificar intención del usuario | Validar campos requeridos |
| Sugerir keywords / opciones nuevas | Sumar, contar, agregar métricas |

**Regla clara:** si lo puede hacer un IF, un `filter`, o un nodo nativo del orquestador → no se lo das a Claude.

---

## Convención de testing

> **Nada de mocks. Todo testing es real, contra servicios reales.**

- **Local**: el agente Python o el workflow corre con `.env` apuntando a servicios reales (Notion real, APIs reales).
- **Para evitar enviar mensajes reales a clientes en testing**, los workflows comunes (`send-email`, `send-whatsapp-*`) reciben un campo `_env` en el payload:
  - `_env: "dev"` → el primer nodo IF redirige los destinos al dev (su email, su WhatsApp).
  - `_env: "prod"` → destinos reales del cliente.
- El cliente HTTP del servicio agrega `_env` automáticamente al payload leyendo su variable de entorno. El dev no se acuerda de eso.

Esto reemplaza la convención de workflows duplicados (`-staging`): **un solo workflow, comportamiento distinto según `_env`**.

---

## Mapa mental rápido

```
                ┌─────────────────────┐
                │  Cron / Webhook     │  ← Orquestador
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │  Nodo HTTP / nativo │  ← lee fuentes (APIs, DB)
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │  Nodo Code (JS)     │  ← filtra, agrega, marca
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │  IF: ¿hay ambiguos? │
                └────┬────────────┬───┘
                     ↓ no         ↓ sí
                ┌─────────┐  ┌──────────────────┐
                │  Skip   │  │ Anthropic node   │  ← razona casos ambiguos
                │  Claude │  │  (prompt corto)  │
                └────┬────┘  └────────┬─────────┘
                     └──────┬─────────┘
                            ↓
                ┌─────────────────────┐
                │  Servicio Python    │  ← SOLO si SDK propietario
                │  (este template)    │     o AgentLoop con tools
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │ Nodo destino        │  ← escribe + notifica
                │ (Notion/DB/email)   │
                └─────────────────────┘
```

---

## Referencias rápidas

- Antes de crear un workflow nuevo: validar con la herramienta del orquestador.
- Modelo Claude por defecto: `claude-sonnet-4-6`. No usar Opus salvo pedido explícito.
- Cualquier duda: este archivo es la fuente de verdad. Si choca con algo en un agente concreto, **gana este archivo** y se abre un work-item de refactor.

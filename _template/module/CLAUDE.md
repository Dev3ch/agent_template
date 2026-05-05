# CLAUDE.md — módulo {{MODULE_NAME}}

Contexto específico del módulo. Lo que NO está acá, mirá el `CLAUDE.md` raíz.

## Qué hace este módulo

(Describir el dominio: qué problema resuelve, qué stakeholders sirve.)

## Agentes activos

| Agente | Tipo | Trigger | Notas |
|---|---|---|---|
| _(vacío)_ | | | |

## Convenciones del módulo

- Modelo Claude default: el del `.env` raíz (override en `service/.env` si hace falta).
- HITL: definir umbrales y a quién notifica cada agente.
- Memoria compartida: (Notion DB, Postgres, etc. — declarar acá si aplica).

## Variables de entorno propias

Listar acá las vars que SOLO usa este módulo y van en `service/.env`.

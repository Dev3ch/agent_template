# workflows/

Workflows n8n del repo.

## Estructura

```
workflows/
└── shared/                ← workflows reusados por múltiples módulos
    ├── send-email.json
    └── send-whatsapp.json
```

Los workflows **específicos de cada agente** viven en `{modulo}/workflows/`,
no acá.

## Convención _env

Los workflows compartidos (`send-email`, `send-whatsapp`) reciben en su payload
un campo `_env`:

- `_env: "dev"` → primer nodo IF redirige a destinos del dev (su email, su WhatsApp).
- `_env: "prod"` → destinos reales del cliente.

Esto reemplaza tener `-staging` y `-prod` duplicados.

## Cómo subir un workflow a n8n

1. Importarlo desde la UI (`Import from file`).
2. Configurar credenciales requeridas.
3. **Activar manualmente** (los JSONs vienen con `active: false` por seguridad — Regla 6).

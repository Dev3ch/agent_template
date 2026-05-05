"""notion_client — CRUD ligero contra la API de Notion.

Útil cuando Notion es la memoria compartida del monorepo (learnings, actions, proposals).

Si tu agente NO usa Notion, ignorá este paquete. No es obligatorio.
"""
from .client import NotionClient

__all__ = ["NotionClient"]

"""Cliente ligero contra la API de Notion. Solo lo esencial.

Si necesitás algo más sofisticado (filtros complejos, paginación grande), usar
el SDK oficial `notion-client` directamente.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


class NotionClient:
    def __init__(self, token: str | None = None, timeout: float = 30.0):
        self.token = token or os.getenv("NOTION_TOKEN")
        if not self.token:
            raise RuntimeError("NOTION_TOKEN no seteado")
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def query_database(self, database_id: str, filter: dict | None = None) -> list[dict]:
        body: dict[str, Any] = {}
        if filter:
            body["filter"] = filter
        r = self._client.post(f"/databases/{database_id}/query", json=body)
        r.raise_for_status()
        return r.json().get("results", [])

    def create_page(self, parent_database_id: str, properties: dict) -> dict:
        body = {"parent": {"database_id": parent_database_id}, "properties": properties}
        r = self._client.post("/pages", json=body)
        r.raise_for_status()
        return r.json()

    def update_page(self, page_id: str, properties: dict) -> dict:
        r = self._client.patch(f"/pages/{page_id}", json={"properties": properties})
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> NotionClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

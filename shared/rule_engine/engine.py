"""Motor declarativo de reglas. Sin dependencias externas."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Predicate = Callable[[dict[str, Any]], bool]


@dataclass
class Rule:
    name: str
    when: Predicate
    then: str  # bucket / acción
    stop_on_match: bool = False  # si True, no se evalúan reglas siguientes


@dataclass
class RuleEngine:
    rules: list[Rule] = field(default_factory=list)

    def classify(self, items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Clasifica items en buckets. Items sin match van a `_unmatched`."""
        buckets: dict[str, list[dict[str, Any]]] = {"_unmatched": []}
        for item in items:
            matched = False
            for rule in self.rules:
                if rule.when(item):
                    buckets.setdefault(rule.then, []).append(item)
                    matched = True
                    if rule.stop_on_match:
                        break
            if not matched:
                buckets["_unmatched"].append(item)
        return buckets

    def filter(self, items: list[dict[str, Any]], bucket: str) -> list[dict[str, Any]]:
        """Atajo: devuelve solo los items que caen en `bucket`."""
        return self.classify(items).get(bucket, [])

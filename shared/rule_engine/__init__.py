"""rule_engine — motor declarativo de reglas/umbrales.

Idea: filtrar y clasificar items en JS-puro/Python-puro ANTES de mandar a Claude.
Cumple la Regla 3 de agent-design: Claude solo ve los casos ambiguos.

Ejemplo:
    from shared.rule_engine import RuleEngine, Rule

    engine = RuleEngine([
        Rule(name="alta_inversion", when=lambda x: x["spend"] > 1000, then="review"),
        Rule(name="bajo_ctr", when=lambda x: x["ctr"] < 0.01, then="pause"),
    ])
    classified = engine.classify(items)
    # classified = {"review": [...], "pause": [...], "_unmatched": [...]}
"""
from .engine import Rule, RuleEngine

__all__ = ["RuleEngine", "Rule"]

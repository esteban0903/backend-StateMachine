from __future__ import annotations

from collections.abc import Iterable

from app.rules.models.rule import Rule
from app.rules.models.sample_rules import build_sample_rules
from app.rules.repositories.rule_repository import RuleRepository


class InMemoryRuleRepository(RuleRepository):
    def __init__(self, initial_rules: Iterable[Rule] | None = None) -> None:
        rules = list(initial_rules) if initial_rules is not None else build_sample_rules()
        self._rules: dict[str, Rule] = {rule.id: rule for rule in rules}

    def get_all_enabled(self) -> list[Rule]:
        return [rule for rule in self._rules.values() if rule.enabled]

    def save(self, rule: Rule) -> Rule:
        self._rules[rule.id] = rule
        return rule

    def get_by_id(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

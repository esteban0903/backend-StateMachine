from __future__ import annotations

from app.rules.engine.rule_engine import RuleEngine
from app.rules.models.context import RuleEvaluationContext
from app.rules.models.evaluation_result import RuleEvaluationResult
from app.rules.repositories.rule_repository import RuleRepository


class RuleService:
    def __init__(self, rule_repository: RuleRepository, rule_engine: RuleEngine | None = None) -> None:
        self._rule_repository = rule_repository
        self._rule_engine = rule_engine or RuleEngine()

    def evaluate(self, context: RuleEvaluationContext) -> RuleEvaluationResult:
        enabled_rules = self._rule_repository.get_all_enabled()
        return self._rule_engine.evaluate(enabled_rules, context)

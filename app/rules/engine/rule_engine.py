from __future__ import annotations

from app.rules.engine.action_executor import ActionExecutor
from app.rules.engine.condition_evaluator import ConditionEvaluator
from app.rules.models.context import RuleEvaluationContext
from app.rules.models.evaluation_result import RuleActionResult, RuleEvaluationResult
from app.rules.models.rule import Rule


class RuleEngine:
    def __init__(
        self,
        condition_evaluator: ConditionEvaluator | None = None,
        action_executor: ActionExecutor | None = None,
    ) -> None:
        self._condition_evaluator = condition_evaluator or ConditionEvaluator()
        self._action_executor = action_executor or ActionExecutor()

    def evaluate(self, rules: list[Rule], context: RuleEvaluationContext) -> RuleEvaluationResult:
        matched_rule_ids: list[str] = []
        action_results: list[RuleActionResult] = []
        surcharge_value = 0.0

        for rule in sorted(rules, key=lambda item: item.priority, reverse=True):
            if not rule.enabled:
                continue

            if not self._condition_evaluator.evaluate(rule.condition, context):
                continue

            matched_rule_ids.append(rule.id)

            for action in rule.actions:
                action_result, surcharge_delta = self._action_executor.execute(action)
                action_results.append(action_result)
                surcharge_value += surcharge_delta

        return RuleEvaluationResult(
            matched_rule_ids=matched_rule_ids,
            action_results=action_results,
            surcharge_value=surcharge_value if surcharge_value > 0 else None,
        )

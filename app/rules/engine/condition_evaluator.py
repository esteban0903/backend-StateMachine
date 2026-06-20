from __future__ import annotations

from functools import singledispatchmethod

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState
from app.rules.models.condition import (
    AmountComparator,
    AmountCondition,
    ConditionGroup,
    ConditionGroupOperator,
    EventTypeCondition,
    OrderStateCondition,
    RuleCondition,
)
from app.rules.models.context import RuleEvaluationContext


class ConditionEvaluator:
    def evaluate(self, condition: RuleCondition, context: RuleEvaluationContext) -> bool:
        return self._evaluate(condition, context)

    @singledispatchmethod
    def _evaluate(self, condition: RuleCondition, context: RuleEvaluationContext) -> bool:
        raise TypeError(f"Unsupported condition type: {type(condition).__name__}")

    @_evaluate.register
    def _(self, condition: AmountCondition, context: RuleEvaluationContext) -> bool:
        if condition.comparator is AmountComparator.GT:
            return context.amount > condition.value
        if condition.comparator is AmountComparator.GTE:
            return context.amount >= condition.value
        if condition.comparator is AmountComparator.LT:
            return context.amount < condition.value
        if condition.comparator is AmountComparator.LTE:
            return context.amount <= condition.value
        if condition.comparator is AmountComparator.EQ:
            return context.amount == condition.value
        if condition.comparator is AmountComparator.NE:
            return context.amount != condition.value
        raise ValueError(f"Unsupported amount comparator: {condition.comparator}")

    @_evaluate.register
    def _(self, condition: OrderStateCondition, context: RuleEvaluationContext) -> bool:
        return context.state in condition.states

    @_evaluate.register
    def _(self, condition: EventTypeCondition, context: RuleEvaluationContext) -> bool:
        return context.event_type in condition.events

    @_evaluate.register
    def _(self, condition: ConditionGroup, context: RuleEvaluationContext) -> bool:
        if condition.operator is ConditionGroupOperator.AND:
            return all(self.evaluate(child, context) for child in condition.conditions)
        if condition.operator is ConditionGroupOperator.OR:
            return any(self.evaluate(child, context) for child in condition.conditions)
        raise ValueError(f"Unsupported condition group operator: {condition.operator}")

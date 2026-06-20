from __future__ import annotations

from functools import singledispatchmethod

from app.rules.models.action import (
    AddSurchargeAction,
    CancelOrderAction,
    CreateSupportTicketAction,
    RuleAction,
)
from app.rules.models.evaluation_result import RuleActionResult


class ActionExecutor:
    def execute(self, action: RuleAction) -> tuple[RuleActionResult, float]:
        return self._execute(action)

    @singledispatchmethod
    def _execute(self, action: RuleAction) -> tuple[RuleActionResult, float]:
        raise TypeError(f"Unsupported action type: {type(action).__name__}")

    @_execute.register
    def _(self, action: CreateSupportTicketAction) -> tuple[RuleActionResult, float]:
        return (
            RuleActionResult(kind=action.kind, payload={"reason": action.reason, "metadata": action.metadata}),
            0.0,
        )

    @_execute.register
    def _(self, action: CancelOrderAction) -> tuple[RuleActionResult, float]:
        return RuleActionResult(kind=action.kind, payload={"reason": action.reason}), 0.0

    @_execute.register
    def _(self, action: AddSurchargeAction) -> tuple[RuleActionResult, float]:
        return RuleActionResult(kind=action.kind, payload={"amount": action.amount}), action.amount

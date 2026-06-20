from __future__ import annotations

from typing import Any

from app.domain.models.order import Order
from app.rules.models.evaluation_result import RuleActionResult
from app.rules.runtime.action_handler import ActionDispatchOutcome


class AddSurchargeHandler:
    action_kind = "add_surcharge"

    def handle(
        self,
        order: Order,
        action_result: RuleActionResult,
        metadata: dict[str, Any] | None = None,
    ) -> ActionDispatchOutcome:
        order.amount += float(action_result.payload.get("amount", 0.0))
        return ActionDispatchOutcome()

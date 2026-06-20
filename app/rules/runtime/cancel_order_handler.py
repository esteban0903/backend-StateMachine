from __future__ import annotations

from typing import Any

from app.domain.enums.order_state import OrderState
from app.domain.models.order import Order
from app.rules.models.evaluation_result import RuleActionResult
from app.rules.runtime.action_handler import ActionDispatchOutcome


class CancelOrderHandler:
    action_kind = "cancel_order"

    def handle(
        self,
        order: Order,
        action_result: RuleActionResult,
        metadata: dict[str, Any] | None = None,
    ) -> ActionDispatchOutcome:
        return ActionDispatchOutcome(next_state=OrderState.CANCELLED)

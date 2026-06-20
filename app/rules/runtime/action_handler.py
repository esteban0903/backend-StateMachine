from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.domain.models.order import Order
from app.domain.enums.order_state import OrderState
from app.rules.models.evaluation_result import RuleActionResult


@dataclass(frozen=True)
class ActionDispatchOutcome:
    next_state: OrderState | None = None


class ActionHandler(Protocol):
    action_kind: str

    def handle(
        self,
        order: Order,
        action_result: RuleActionResult,
        metadata: dict[str, Any] | None = None,
    ) -> ActionDispatchOutcome:
        """Apply a single action result to the order and return the resulting dispatch outcome."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.domain.enums.order_state import OrderState
from app.domain.models.order import Order
from app.rules.models.evaluation_result import RuleEvaluationResult
from app.rules.runtime.action_handler import ActionDispatchOutcome, ActionHandler
from app.rules.runtime.add_surcharge_handler import AddSurchargeHandler
from app.rules.runtime.cancel_order_handler import CancelOrderHandler
from app.rules.runtime.create_support_ticket_handler import CreateSupportTicketHandler
from app.services.ticket_service import TicketService


class ActionDispatcher:
    def __init__(
        self,
        ticket_service: TicketService,
        handlers: Iterable[ActionHandler] | None = None,
    ) -> None:
        self._handlers = self._build_handlers(ticket_service, handlers)

    def _build_handlers(
        self,
        ticket_service: TicketService,
        handlers: Iterable[ActionHandler] | None,
    ) -> dict[str, ActionHandler]:
        if handlers is None:
            active_handlers = (
                CreateSupportTicketHandler(ticket_service),
                CancelOrderHandler(),
                AddSurchargeHandler(),
            )
        else:
            active_handlers = handlers

        return {handler.action_kind: handler for handler in active_handlers}

    def dispatch(
        self,
        order: Order,
        results: RuleEvaluationResult,
        metadata: dict[str, Any] | None = None,
    ) -> ActionDispatchOutcome:
        next_state: OrderState | None = None

        for action_result in results.action_results:
            handler = self._handlers.get(action_result.kind)
            if handler is None:
                raise ValueError(f"Unsupported action kind: {action_result.kind}")

            outcome = handler.handle(order=order, action_result=action_result, metadata=metadata)
            if outcome.next_state is not None:
                next_state = outcome.next_state

        return ActionDispatchOutcome(next_state=next_state)

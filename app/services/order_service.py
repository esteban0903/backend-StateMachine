from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState
from app.domain.exceptions.domain_exceptions import InvalidTransitionError, OrderNotFoundError
from app.domain.models.order import Order
from app.domain.models.order_history_entry import OrderHistoryEntry
from app.domain.state_machine import TransitionTableStateMachine as StateMachine
from app.repositories.order_repository import OrderRepository
from app.rules.models.context import RuleEvaluationContext
from app.rules.runtime.action_dispatcher import ActionDispatcher
from app.rules.services.rule_service import RuleService
from app.services.observability import increment_metric, logger, order_logging_context, tracer


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        state_machine: StateMachine,
        rule_service: RuleService,
        action_dispatcher: ActionDispatcher,
    ) -> None:
        self._order_repository = order_repository
        self._state_machine = state_machine
        self._rule_service = rule_service
        self._action_dispatcher = action_dispatcher

    @tracer.capture_method
    def create_order(self, product_ids: list[str], amount: float) -> Order:
        order = Order(
            id=uuid4().hex,
            product_ids=list(product_ids),
            amount=amount,
            state=OrderState.PENDING,
        )
        saved_order = self._order_repository.save(order)

        # structured logging removed for successful creation to reduce noise

        increment_metric("OrdersCreated")
        return saved_order

    def get_order(self, order_id: str) -> Order:
        order = self._order_repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        return order

    def get_order_history(self, order_id: str) -> list[OrderHistoryEntry]:
        return self.get_order(order_id).history

    def _resolve_next_state(self, order: Order, event_type: OrderEvent) -> OrderState:
        current_state = order.state
        try:
            return self._state_machine.get_next_state(current_state, event_type)
        except InvalidTransitionError:
            increment_metric("InvalidTransitions")

            with order_logging_context(
                order_id=order.id,
                event_type=event_type.value,
                current_state=current_state.value,
                next_state=None,
            ):
                logger.warning("Invalid transition rejected")

            raise

    def _build_rule_context(
        self,
        order: Order,
        event_type: OrderEvent,
        metadata: dict[str, Any] | None,
    ) -> RuleEvaluationContext:
        return RuleEvaluationContext(
            order_id=order.id,
            amount=order.amount,
            state=order.state,
            event_type=event_type,
            metadata=dict(metadata or {}),
        )

    def _record_transition(
        self, order: Order, event_type: OrderEvent, previous_state: OrderState, next_state: OrderState
    ) -> None:
        order.history.append(
            OrderHistoryEntry(
                event_type=event_type.value,
                previous_state=previous_state.value,
                new_state=next_state.value,
                timestamp=datetime.now(UTC).replace(microsecond=0).isoformat().replace(
                    "+00:00",
                    "Z",
                ),
            )
        )
        order.state = next_state

    @tracer.capture_method
    def process_event(
        self,
        order_id: str,
        event_type: OrderEvent,
        metadata: dict[str, Any] | None = None,
    ) -> Order:
        order = self.get_order(order_id)
        previous_state = order.state

        rule_context = self._build_rule_context(order, event_type, metadata)
        rule_results = self._rule_service.evaluate(rule_context)

        # Resolve next state (handles invalid transitions and logs warning)
        next_state = self._resolve_next_state(order, event_type)

        # Apply dynamic business rules before persisting the transition
        dispatch_outcome = self._action_dispatcher.dispatch(order=order, results=rule_results, metadata=metadata)
        if dispatch_outcome.next_state is not None:
            next_state = dispatch_outcome.next_state

        self._record_transition(order, event_type, previous_state, next_state)
        saved_order = self._order_repository.save(order)

        # Final metrics
        increment_metric("EventsProcessed")
        return saved_order

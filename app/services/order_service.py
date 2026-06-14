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
from app.services.observability import increment_metric, logger, order_logging_context, tracer
from app.services.ticket_service import TicketService


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        state_machine: StateMachine,
        ticket_service: TicketService,
    ) -> None:
        self._order_repository = order_repository
        self._state_machine = state_machine
        self._ticket_service = ticket_service

    @tracer.capture_method
    def create_order(self, product_ids: list[str], amount: float) -> Order:
        order = Order(
            id=uuid4().hex,
            product_ids=list(product_ids),
            amount=amount,
            state=OrderState.PENDING,
        )
        saved_order = self._order_repository.save(order)

        with order_logging_context(
            order_id=saved_order.id,
            event_type=None,
            current_state=saved_order.state.value,
            next_state=saved_order.state.value,
        ):
            logger.info("Order created")

        increment_metric("OrdersCreated")
        return saved_order

    def get_order(self, order_id: str) -> Order:
        order = self._order_repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        return order

    def get_order_history(self, order_id: str) -> list[OrderHistoryEntry]:
        return self.get_order(order_id).history

    @tracer.capture_method
    def process_event(
        self,
        order_id: str,
        event_type: OrderEvent,
        metadata: dict[str, Any] | None = None,
    ) -> Order:
        order = self.get_order(order_id)
        current_state = order.state

        with order_logging_context(
            order_id=order.id,
            event_type=event_type.value,
            current_state=current_state.value,
            next_state=None,
        ):
            logger.info("Processing order event")

        try:
            next_state = self._state_machine.get_next_state(current_state, event_type)
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

        if event_type is OrderEvent.PAYMENT_FAILED and order.amount > 1000:
            self._ticket_service.create_support_review_ticket(
                order_id=order.id,
                amount=order.amount,
                metadata=metadata,
            )
            increment_metric("SupportReviewTicketsCreated")

        order.history.append(
            OrderHistoryEntry(
                event_type=event_type.value,
                previous_state=current_state.value,
                new_state=next_state.value,
                timestamp=datetime.now(UTC).replace(microsecond=0).isoformat().replace(
                    "+00:00",
                    "Z",
                ),
            )
        )
        order.state = next_state
        saved_order = self._order_repository.save(order)

        with order_logging_context(
            order_id=saved_order.id,
            event_type=event_type.value,
            current_state=current_state.value,
            next_state=next_state.value,
        ):
            logger.info("Order event processed")

        increment_metric("EventsProcessed")
        return saved_order

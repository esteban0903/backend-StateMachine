from __future__ import annotations

import pytest

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState
from app.domain.exceptions.domain_exceptions import OrderNotFoundError
from app.repositories.in_memory_order_repository import InMemoryOrderRepository
from app.services.order_service import OrderService
from app.domain.state_machine import TransitionTableStateMachine


class RecordingTicketService:
    def __init__(self) -> None:
        self.created_tickets: list[dict[str, object]] = []

    def create_support_review_ticket(
        self,
        order_id: str,
        amount: float,
        metadata: dict[str, object] | None = None,
    ) -> str:
        ticket = {
            "order_id": order_id,
            "amount": amount,
            "metadata": dict(metadata or {}),
        }
        self.created_tickets.append(ticket)
        return f"ticket-{len(self.created_tickets)}"


def test_create_order_persists_order_in_pending_state(order_service: OrderService) -> None:
    # Arrange
    product_ids = ["P1", "P2"]
    amount = 1200

    # Act
    order = order_service.create_order(product_ids, amount)

    # Assert
    assert order.id
    assert order.product_ids == product_ids
    assert order.amount == amount
    assert order.state is OrderState.PENDING
    assert order_service.get_order(order.id) == order


def test_get_order_returns_existing_order(order_service: OrderService) -> None:
    # Arrange
    created_order = order_service.create_order(["P1"], 100)

    # Act
    found_order = order_service.get_order(created_order.id)

    # Assert
    assert found_order == created_order


def test_get_order_raises_when_order_is_missing(order_service: OrderService) -> None:
    # Act / Assert
    with pytest.raises(OrderNotFoundError):
        order_service.get_order("missing-order-id")


def test_process_event_updates_state(order_service: OrderService) -> None:
    # Arrange
    order = order_service.create_order(["P1"], 100)

    # Act
    updated_order = order_service.process_event(
        order.id,
        OrderEvent.NO_VERIFICATION_NEEDED,
        {},
    )

    # Assert
    assert updated_order.state is OrderState.PENDING_PAYMENT
    assert order_service.get_order(order.id).state is OrderState.PENDING_PAYMENT
    assert len(updated_order.history) == 1
    assert updated_order.history[0].event_type == "noVerificationNeeded"
    assert updated_order.history[0].previous_state == "Pending"
    assert updated_order.history[0].new_state == "PendingPayment"
    assert updated_order.history[0].timestamp.endswith("Z")


def test_get_order_history_returns_recorded_history(order_service: OrderService) -> None:
    # Arrange
    order = order_service.create_order(["P1"], 100)
    order_service.process_event(order.id, OrderEvent.NO_VERIFICATION_NEEDED)
    order_service.process_event(order.id, OrderEvent.PAYMENT_SUCCESSFUL)

    # Act
    history = order_service.get_order_history(order.id)

    # Assert
    assert [entry.event_type for entry in history] == [
        "noVerificationNeeded",
        "paymentSuccessful",
    ]
    assert [entry.previous_state for entry in history] == ["Pending", "PendingPayment"]
    assert [entry.new_state for entry in history] == ["PendingPayment", "Confirmed"]
    assert all(entry.timestamp.endswith("Z") for entry in history)


def test_payment_failed_creates_ticket_when_amount_above_threshold() -> None:
    # Arrange
    repository = InMemoryOrderRepository()
    state_machine = TransitionTableStateMachine()
    ticket_service = RecordingTicketService()
    order_service = OrderService(repository, state_machine, ticket_service)
    order = order_service.create_order(["P1"], 1201)

    # Act
    updated_order = order_service.process_event(order.id, OrderEvent.PAYMENT_FAILED)

    # Assert
    assert updated_order.state is OrderState.CANCELLED
    assert len(ticket_service.created_tickets) == 1


def test_payment_failed_does_not_create_ticket_when_amount_is_at_or_below_threshold() -> None:
    # Arrange
    repository = InMemoryOrderRepository()
    state_machine = TransitionTableStateMachine()
    ticket_service = RecordingTicketService()
    order_service = OrderService(repository, state_machine, ticket_service)
    order = order_service.create_order(["P1"], 1000)

    # Act
    updated_order = order_service.process_event(order.id, OrderEvent.PAYMENT_FAILED)

    # Assert
    assert updated_order.state is OrderState.CANCELLED
    assert ticket_service.created_tickets == []

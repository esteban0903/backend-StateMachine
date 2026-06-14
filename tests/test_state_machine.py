from __future__ import annotations

import pytest

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState
from app.domain.exceptions.domain_exceptions import InvalidTransitionError
from app.domain.state_machine import TransitionTableStateMachine


def test_get_next_state_valid_transition_from_pending_to_on_hold() -> None:
    # Arrange
    state_machine = TransitionTableStateMachine()

    # Act
    next_state = state_machine.get_next_state(
        OrderState.PENDING,
        OrderEvent.PENDING_BIOMETRICAL_VERIFICATION,
    )

    # Assert
    assert next_state is OrderState.ON_HOLD


@pytest.mark.parametrize(
    ("current_state", "event_type", "expected_state"),
    [
        (OrderState.PENDING, OrderEvent.PENDING_BIOMETRICAL_VERIFICATION, OrderState.ON_HOLD),
        (OrderState.PENDING, OrderEvent.NO_VERIFICATION_NEEDED, OrderState.PENDING_PAYMENT),
        (OrderState.PENDING, OrderEvent.PAYMENT_FAILED, OrderState.CANCELLED),
        (OrderState.PENDING, OrderEvent.ORDER_CANCELLED, OrderState.CANCELLED),
        (OrderState.PENDING, OrderEvent.ORDER_CANCELLED_BY_USER, OrderState.CANCELLED),
        (
            OrderState.ON_HOLD,
            OrderEvent.BIOMETRICAL_VERIFICATION_SUCCESSFUL,
            OrderState.PENDING_PAYMENT,
        ),
        (OrderState.ON_HOLD, OrderEvent.VERIFICATION_FAILED, OrderState.CANCELLED),
        (
            OrderState.ON_HOLD,
            OrderEvent.ORDER_CANCELLED_BY_USER,
            OrderState.CANCELLED,
        ),
        (OrderState.PENDING_PAYMENT, OrderEvent.PAYMENT_SUCCESSFUL, OrderState.CONFIRMED),
        (OrderState.PENDING_PAYMENT, OrderEvent.ORDER_CANCELLED_BY_USER, OrderState.CANCELLED),
        (OrderState.CONFIRMED, OrderEvent.PREPARING_SHIPMENT, OrderState.PROCESSING),
        (OrderState.CONFIRMED, OrderEvent.ORDER_CANCELLED_BY_USER, OrderState.CANCELLED),
        (OrderState.PROCESSING, OrderEvent.ITEM_DISPATCHED, OrderState.SHIPPED),
        (OrderState.PROCESSING, OrderEvent.ORDER_CANCELLED_BY_USER, OrderState.CANCELLED),
        (OrderState.SHIPPED, OrderEvent.ITEM_RECEIVED_BY_CUSTOMER, OrderState.DELIVERED),
        (OrderState.SHIPPED, OrderEvent.DELIVERY_ISSUE, OrderState.ON_HOLD),
        (OrderState.SHIPPED, OrderEvent.ORDER_CANCELLED_BY_USER, OrderState.CANCELLED),
    ],
)
def test_get_next_state_valid_transitions(
    current_state: OrderState,
    event_type: OrderEvent,
    expected_state: OrderState,
) -> None:
    # Arrange
    state_machine = TransitionTableStateMachine()

    # Act
    next_state = state_machine.get_next_state(current_state, event_type)

    # Assert
    assert next_state is expected_state


def test_get_next_state_invalid_transition_raises_error() -> None:
    # Arrange
    state_machine = TransitionTableStateMachine()

    # Act / Assert
    with pytest.raises(InvalidTransitionError):
        state_machine.get_next_state(OrderState.PENDING, OrderEvent.ITEM_DISPATCHED)


def test_order_cancelled_by_user_from_active_state_moves_to_cancelled() -> None:
    # Arrange
    state_machine = TransitionTableStateMachine()

    # Act
    next_state = state_machine.get_next_state(
        OrderState.CONFIRMED,
        OrderEvent.ORDER_CANCELLED_BY_USER,
    )

    # Assert
    assert next_state is OrderState.CANCELLED


@pytest.mark.parametrize("terminal_state", [OrderState.DELIVERED, OrderState.CANCELLED])
def test_order_cancelled_by_user_is_invalid_for_terminal_states(
    terminal_state: OrderState,
) -> None:
    # Arrange
    state_machine = TransitionTableStateMachine()

    # Act / Assert
    with pytest.raises(InvalidTransitionError):
        state_machine.get_next_state(terminal_state, OrderEvent.ORDER_CANCELLED_BY_USER)

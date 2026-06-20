from __future__ import annotations

from typing import Mapping

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState
from app.domain.exceptions.domain_exceptions import InvalidTransitionError


StateTransitionTable = Mapping[OrderState, Mapping[OrderEvent, OrderState]]

TERMINAL_STATES = {
    OrderState.DELIVERED,
    OrderState.CANCELLED,
}

TRANSITIONS: dict[OrderState, dict[OrderEvent, OrderState]] = {
    OrderState.PENDING: {
        OrderEvent.PENDING_BIOMETRICAL_VERIFICATION: OrderState.ON_HOLD,
        OrderEvent.NO_VERIFICATION_NEEDED: OrderState.PENDING_PAYMENT,
        OrderEvent.PAYMENT_FAILED: OrderState.CANCELLED,
        OrderEvent.ORDER_CANCELLED: OrderState.CANCELLED,
    },
    OrderState.ON_HOLD: {
        OrderEvent.BIOMETRICAL_VERIFICATION_SUCCESSFUL: OrderState.PENDING_PAYMENT,
        OrderEvent.VERIFICATION_FAILED: OrderState.CANCELLED,
    },
    OrderState.PENDING_PAYMENT: {
        OrderEvent.PAYMENT_SUCCESSFUL: OrderState.CONFIRMED,
    },
    OrderState.CONFIRMED: {
        OrderEvent.PREPARING_SHIPMENT: OrderState.PROCESSING,
    },
    OrderState.PROCESSING: {
        OrderEvent.ITEM_DISPATCHED: OrderState.SHIPPED,
    },
    OrderState.SHIPPED: {
        OrderEvent.ITEM_RECEIVED_BY_CUSTOMER: OrderState.DELIVERED,
        OrderEvent.DELIVERY_ISSUE: OrderState.ON_HOLD,
    },
    OrderState.CANCELLED: {},
}




class TransitionTableStateMachine:
    def __init__(self, transitions: StateTransitionTable | None = None) -> None:
        base = transitions or TRANSITIONS
        # Create a shallow copy of the outer mapping and copy each inner mapping
        # so we can augment safely without mutating module-level constants.
        self._transitions: dict[OrderState, dict[OrderEvent, OrderState]] = {
            state: dict(mapping) for state, mapping in base.items()
        }

        # Make the global "cancel by user" rule declarative: for every non-terminal
        # state that doesn't already define ORDER_CANCELLED_BY_USER, map it to CANCELLED.
        for state, mapping in list(self._transitions.items()):
            if state in TERMINAL_STATES:
                continue
            if OrderEvent.ORDER_CANCELLED_BY_USER not in mapping:
                mapping[OrderEvent.ORDER_CANCELLED_BY_USER] = OrderState.CANCELLED

    def get_next_state(self, current_state: OrderState, event_type: OrderEvent) -> OrderState:
        state_transitions = self._transitions.get(current_state, {})
        next_state = state_transitions.get(event_type)

        if next_state is None:
            raise InvalidTransitionError(current_state, event_type)

        return next_state

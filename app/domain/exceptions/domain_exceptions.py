from __future__ import annotations

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState


class DomainError(Exception):
    """Base class for domain-level errors."""


class OrderNotFoundError(DomainError, LookupError):
    def __init__(self, order_id: str) -> None:
        super().__init__(f"Order '{order_id}' was not found.")
        self.order_id = order_id


class InvalidTransitionError(DomainError, ValueError):
    def __init__(self, current_state: OrderState, event_type: OrderEvent) -> None:
        message = (
            f"Invalid transition from '{current_state.value}' "
            f"using event '{event_type.value}'."
        )
        super().__init__(message)
        self.current_state = current_state
        self.event_type = event_type


class InvalidEventError(DomainError, ValueError):
    def __init__(self, event_type: str) -> None:
        super().__init__(f"Invalid event '{event_type}'.")
        self.event_type = event_type

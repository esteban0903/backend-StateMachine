from __future__ import annotations

from typing import Protocol

from app.domain.models.order import Order


class OrderRepository(Protocol):
    def get_by_id(self, order_id: str) -> Order | None:
        """Return the order for the given identifier, or None if it does not exist."""

    def save(self, order: Order) -> Order:
        """Persist the order and return the saved instance."""

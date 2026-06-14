from __future__ import annotations

from collections.abc import Iterable

from app.domain.models.order import Order
from app.repositories.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, initial_orders: Iterable[Order] | None = None) -> None:
        self._orders: dict[str, Order] = {
            order.id: order for order in (initial_orders or ())
        }

    def get_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

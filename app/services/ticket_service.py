from __future__ import annotations

from typing import Any, Protocol
from uuid import uuid4


class TicketService(Protocol):
    def create_support_review_ticket(
        self,
        order_id: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a support review ticket and return its identifier."""


class InMemoryTicketService:
    def __init__(self) -> None:
        self._tickets: dict[str, dict[str, Any]] = {}

    def create_support_review_ticket(
        self,
        order_id: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        ticket_id = uuid4().hex
        self._tickets[ticket_id] = {
            "id": ticket_id,
            "order_id": order_id,
            "amount": amount,
            "metadata": dict(metadata or {}),
        }
        return ticket_id

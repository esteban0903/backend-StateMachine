from __future__ import annotations

from typing import Any

from app.domain.models.order import Order
from app.rules.models.evaluation_result import RuleActionResult
from app.rules.runtime.action_handler import ActionDispatchOutcome
from app.services.observability import increment_metric
from app.services.ticket_service import TicketService


class CreateSupportTicketHandler:
    action_kind = "create_support_ticket"

    def __init__(self, ticket_service: TicketService) -> None:
        self._ticket_service = ticket_service

    def handle(
        self,
        order: Order,
        action_result: RuleActionResult,
        metadata: dict[str, Any] | None = None,
    ) -> ActionDispatchOutcome:
        ticket_metadata = dict(metadata or {})
        ticket_metadata.update(action_result.payload.get("metadata", {}))
        self._ticket_service.create_support_review_ticket(
            order_id=order.id,
            amount=order.amount,
            metadata=ticket_metadata,
        )
        increment_metric("SupportReviewTicketsCreated")
        return ActionDispatchOutcome()

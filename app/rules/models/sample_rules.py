from __future__ import annotations

from app.domain.enums.order_event import OrderEvent
from app.rules.models.action import AddSurchargeAction, CancelOrderAction, CreateSupportTicketAction
from app.rules.models.condition import (
    AmountComparator,
    AmountCondition,
    ConditionGroup,
    ConditionGroupOperator,
    EventTypeCondition,
)
from app.rules.models.rule import Rule


def build_sample_rules() -> list[Rule]:
    return [
        Rule(
            id="high_amount_payment_failure",
            name="High amount payment failure",
            priority=100,
            condition=ConditionGroup(
                operator=ConditionGroupOperator.AND,
                conditions=[
                    EventTypeCondition(events=[OrderEvent.PAYMENT_FAILED]),
                    AmountCondition(comparator=AmountComparator.GT, value=1000),
                ],
            ),
            actions=[CreateSupportTicketAction()],
            description="Create a support ticket when a large payment fails.",
        ),
        Rule(
            id="large_international_order_surcharge",
            name="Large international order surcharge",
            priority=90,
            condition=AmountCondition(comparator=AmountComparator.GT, value=5000),
            actions=[AddSurchargeAction(amount=250.0)],
            description="Apply a surcharge for very large orders.",
        ),
        Rule(
            id="manual_cancellation",
            name="Manual cancellation",
            priority=80,
            condition=EventTypeCondition(events=[OrderEvent.ORDER_CANCELLED_BY_USER]),
            actions=[CancelOrderAction()],
            description="Cancel the order when the customer cancels manually.",
        ),
    ]

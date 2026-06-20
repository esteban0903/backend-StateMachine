from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState


class ConditionGroupOperator(str, Enum):
    AND = "AND"
    OR = "OR"


class AmountComparator(str, Enum):
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    NE = "ne"


class RuleCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str


class AmountCondition(RuleCondition):
    kind: Literal["amount"] = "amount"
    comparator: AmountComparator
    value: float


class OrderStateCondition(RuleCondition):
    kind: Literal["order_state"] = "order_state"
    states: list[OrderState] = Field(default_factory=list)


class EventTypeCondition(RuleCondition):
    kind: Literal["event_type"] = "event_type"
    events: list[OrderEvent] = Field(default_factory=list)


class ConditionGroup(RuleCondition):
    kind: Literal["group"] = "group"
    operator: ConditionGroupOperator
    conditions: list[RuleCondition] = Field(default_factory=list)

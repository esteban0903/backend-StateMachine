from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.order_event import OrderEvent
from app.domain.enums.order_state import OrderState


class RuleEvaluationContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str | None = None
    amount: float
    state: OrderState
    event_type: OrderEvent
    metadata: dict[str, Any] = Field(default_factory=dict)

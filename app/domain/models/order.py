from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.order_state import OrderState
from app.domain.models.order_history_entry import OrderHistoryEntry


class Order(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    product_ids: list[str] = Field(default_factory=list)
    amount: float = Field(ge=0)
    state: OrderState = OrderState.PENDING
    history: list[OrderHistoryEntry] = Field(default_factory=list)

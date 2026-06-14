from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    product_ids: list[str] = Field(alias="productIds")
    amount: float

class CreateOrderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    order_id: str = Field(alias="orderId")
    state: str
    
class ProcessEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    event_type: str = Field(alias="eventType")
    metadata: dict[str, Any] = Field(default_factory=dict)

class ProcessEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    state: str


class OrderHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    event_type: str = Field(alias="eventType")
    previous_state: str = Field(alias="previousState")
    new_state: str = Field(alias="newState")
    timestamp: str
    
class OrderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    product_ids: list[str] = Field(alias="productIds")
    amount: float
    state: str



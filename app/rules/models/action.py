from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RuleActionType(str, Enum):
    CREATE_SUPPORT_TICKET = "create_support_ticket"
    CANCEL_ORDER = "cancel_order"
    ADD_SURCHARGE = "add_surcharge"


class RuleAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str


class CreateSupportTicketAction(RuleAction):
    kind: Literal["create_support_ticket"] = "create_support_ticket"
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CancelOrderAction(RuleAction):
    kind: Literal["cancel_order"] = "cancel_order"
    reason: str | None = None


class AddSurchargeAction(RuleAction):
    kind: Literal["add_surcharge"] = "add_surcharge"
    amount: float
